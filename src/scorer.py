from __future__ import annotations

from dataclasses import dataclass, field

from extractor import CandidateProfile, JobRequirement


@dataclass
class ScoreBreakdown:
    role_id: str
    title: str
    total: float
    components: dict[str, float] = field(default_factory=dict)
    evidence: dict[str, list[str]] = field(default_factory=dict)


POSITION_A_WEIGHTS = {
    "technical_match": 0.40,
    "oracle_ebs_match": 0.25,
    "experience_match": 0.15,
    "language_match": 0.10,
    "industry_match": 0.10,
}

POSITION_B_WEIGHTS = {
    "functional_match": 0.35,
    "business_analysis_match": 0.25,
    "oracle_ebs_match": 0.20,
    "leadership_match": 0.10,
    "language_match": 0.10,
}

TECHNICAL_HIGH_VALUE = {
    "PL/SQL", "SQL", "Java", "Oracle Integration Cloud", "OIC", "SOA", "WebLogic",
    "BPEL", "OSB", "Python", "Unix", "Shell", "REST", "SOAP", "API",
    "Oracle Forms", "Oracle Reports", "XML", "Oracle Data Integrator",
}

FUNCTIONAL_HIGH_VALUE = {
    "Financials", "GL", "AP", "AR", "Accounts Payable", "Purchasing", "Inventory",
    "Oracle Inventory", "WIP", "BOM", "SCM", "Oracle SCM", "Accounting",
    "Supply Chain", "Procure-to-Pay", "Order-to-Cash", "P2P", "O2C",
    "ERP", "Business Analysis", "Business Analyst", "implementation", "support",
}

BUSINESS_ANALYSIS_HIGH_VALUE = {
    "Business Analysis", "Business Analyst", "requirements", "solution design",
    "testing", "implementation", "stakeholder", "support", "JIRA", "Confluence",
    "Project Management",
}

LEADERSHIP_TERMS = {
    "leader", "leadership", "manager", "director", "project manager", "cto",
    "chief", "head", "team leader", "leading", "managed",
}


def _term_matches(candidate_terms: list[str], desired_terms: set[str]) -> list[str]:
    result = []
    for term in candidate_terms:
        for desired in desired_terms:
            if term.lower() == desired.lower() or desired.lower() in term.lower():
                result.append(term)
    return sorted(set(result))


def _coverage_score(matches: list[str], target_count: int, cap: float = 100.0) -> float:
    if target_count <= 0:
        return 0.0
    return min(cap, (len(set(matches)) / target_count) * 100)


def score_oracle_ebs(candidate: CandidateProfile) -> float:
    mapping = {"strong": 95.0, "moderate": 75.0, "low": 35.0, "none": 0.0}
    return mapping.get(candidate.oracle_ebs_experience, 0.0)


def score_experience(candidate: CandidateProfile, job: JobRequirement) -> float:
    if job.required_years_min is None:
        return 70.0
    if candidate.years_of_experience is None:
        return 45.0
    ratio = candidate.years_of_experience / job.required_years_min
    if ratio >= 1.4:
        return 100.0
    if ratio >= 1.0:
        return 90.0
    if ratio >= 0.75:
        return 70.0
    if ratio >= 0.5:
        return 50.0
    return 25.0


def score_language(candidate: CandidateProfile, job: JobRequirement) -> float:
    languages = {language.lower() for language in candidate.languages}
    has_english = "english" in languages
    has_spanish = "spanish" in languages
    has_portuguese = "portuguese" in languages
    if has_english and (has_spanish or has_portuguese):
        return 100.0
    if has_english:
        return 85.0
    if has_spanish or has_portuguese:
        return 55.0
    return 0.0


def score_industry(candidate: CandidateProfile) -> float:
    if not candidate.industry_experience:
        return 20.0 if candidate.oracle_ebs_experience in {"strong", "moderate"} else 0.0
    return min(100.0, 35.0 + len(candidate.industry_experience) * 18.0)


def score_technical(candidate: CandidateProfile) -> tuple[float, list[str]]:
    matches = _term_matches(candidate.technical_skills, TECHNICAL_HIGH_VALUE)
    base = _coverage_score(matches, 5)
    if candidate.oracle_ebs_experience == "strong":
        base += 10
    elif candidate.oracle_ebs_experience == "moderate":
        base += 5
    return min(100.0, base), matches


def score_functional(candidate: CandidateProfile) -> tuple[float, list[str]]:
    matches = _term_matches(candidate.functional_skills, FUNCTIONAL_HIGH_VALUE)
    base = _coverage_score(matches, 4)
    if candidate.oracle_ebs_experience == "strong":
        base += 15
    elif candidate.oracle_ebs_experience == "moderate":
        base += 8
    lower = candidate.raw_text.lower()
    if "oracle ebs financials" in lower or "oracle e-business suite financials" in lower:
        base += 20
    if "oracle ebs r12 implementation" in lower or "oracle e-business suite 12" in lower:
        base += 15
    return min(100.0, base), matches


def score_business_analysis(candidate: CandidateProfile) -> tuple[float, list[str]]:
    text = candidate.raw_text.lower()
    matches = [term for term in BUSINESS_ANALYSIS_HIGH_VALUE if term.lower() in text]
    base = _coverage_score(matches, 5)
    if "business analyst" in text:
        base += 20
    return min(100.0, base), sorted(set(matches))


def score_leadership(candidate: CandidateProfile) -> tuple[float, list[str]]:
    text = candidate.raw_text.lower()
    matches = [term for term in LEADERSHIP_TERMS if term in text]
    if len(matches) >= 3:
        return 100.0, sorted(set(matches))
    if len(matches) == 2:
        return 80.0, sorted(set(matches))
    if len(matches) == 1:
        return 55.0, sorted(set(matches))
    return 0.0, []


def score_candidate_for_position(candidate: CandidateProfile, job: JobRequirement) -> ScoreBreakdown:
    if job.role_id == "position_a":
        technical, technical_evidence = score_technical(candidate)
        components = {
            "technical_match": technical,
            "oracle_ebs_match": score_oracle_ebs(candidate),
            "experience_match": score_experience(candidate, job),
            "language_match": score_language(candidate, job),
            "industry_match": score_industry(candidate),
        }
        evidence = {
            "technical_match": technical_evidence,
            "oracle_ebs_match": [candidate.oracle_ebs_experience],
            "industry_match": candidate.industry_experience,
        }
        weights = POSITION_A_WEIGHTS
    elif job.role_id == "position_b":
        functional, functional_evidence = score_functional(candidate)
        business, business_evidence = score_business_analysis(candidate)
        leadership, leadership_evidence = score_leadership(candidate)
        components = {
            "functional_match": functional,
            "business_analysis_match": business,
            "oracle_ebs_match": score_oracle_ebs(candidate),
            "leadership_match": leadership,
            "language_match": score_language(candidate, job),
        }
        evidence = {
            "functional_match": functional_evidence,
            "business_analysis_match": business_evidence,
            "oracle_ebs_match": [candidate.oracle_ebs_experience],
            "leadership_match": leadership_evidence,
        }
        weights = POSITION_B_WEIGHTS
    else:
        raise ValueError(f"Unsupported role_id for configured scoring: {job.role_id}")

    total = sum(components[key] * weight for key, weight in weights.items())
    return ScoreBreakdown(role_id=job.role_id, title=job.title, total=round(total, 2), components=components, evidence=evidence)
