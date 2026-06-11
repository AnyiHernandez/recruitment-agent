from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from parser import ParsedDocument


@dataclass
class JobRequirement:
    role_id: str
    title: str
    location: str | None
    required_years_min: float | None
    required_years_max: float | None
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    functional_knowledge: list[str] = field(default_factory=list)
    technical_knowledge: list[str] = field(default_factory=list)
    industry_requirements: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    raw_text: str = ""


@dataclass
class CandidateProfile:
    candidate_id: str
    source_file: str
    name: str
    title: str | None
    years_of_experience: float | None
    oracle_ebs_experience: str
    technical_skills: list[str] = field(default_factory=list)
    functional_skills: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    industry_experience: list[str] = field(default_factory=list)
    salary_expectation: str | None = None
    location: str | None = None
    raw_text: str = ""


TECHNICAL_TERMS = [
    "Oracle Integration Cloud", "OIC", "SOA", "WebLogic", "BPEL", "OSB",
    "PL/SQL", "SQL", "Java", "JSON", "Python", "Unix", "Shell", "JDeveloper",
    "GitHub", "Git", "REST", "SOAP", "API", "Mulesoft", "Dell Boomi",
    "Oracle Database", "Oracle Forms", "Oracle Reports", "XML", "WebSphere MQ",
    "IBM Integration Bus", "Matillion", "Snowflake", "ODI", "Oracle Data Integrator",
]

FUNCTIONAL_TERMS = [
    "Order-to-Cash", "O2C", "Procure-to-Pay", "P2P", "Financials", "GL", "AP",
    "AR", "Accounts Payable", "Accounts Receivable", "Purchasing", "Inventory",
    "Oracle Inventory", "WIP", "BOM", "CST", "SCM", "Oracle SCM", "Accounting",
    "Payroll", "Treasury", "Supply Chain", "Foreign Trade", "ERP",
]

BUSINESS_ANALYSIS_TERMS = [
    "Business Analysis", "Business Analyst", "requirements", "solution design",
    "testing", "implementation", "stakeholder", "front-line support", "support",
    "documentation", "JIRA", "Confluence", "Project Management",
]

INDUSTRY_TERMS = [
    "LATAM", "Brazil", "BR", "tax", "federal regulations", "eCommerce",
    "Supply Chain", "PIM", "PLM", "retail", "finance", "financial", "healthcare",
    "pharmaceutical", "medical devices", "regulated", "logistics", "public sector",
]

LANGUAGE_TERMS = ["Spanish", "English", "Portuguese", "Ingles", "Inglés"]


def _contains(text: str, term: str) -> bool:
    escaped = re.escape(term)
    if re.fullmatch(r"[A-Za-z0-9/+-]{1,4}", term):
        return re.search(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", text, flags=re.IGNORECASE) is not None
    return term.lower() in text.lower()


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _find_terms(text: str, terms: list[str]) -> list[str]:
    return _unique([term for term in terms if _contains(text, term)])


def extract_location(text: str) -> str | None:
    match = re.search(r"Location:\s*([^\n]+)", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    for location in ["Montevideo, Uruguay", "Salto, Uruguay", "Punta del Este, Uruguay", "Uruguay"]:
        if location.lower() in text.lower():
            return location
    return None


def extract_languages(text: str) -> list[str]:
    languages = _find_terms(text, LANGUAGE_TERMS)
    normalized = []
    for language in languages:
        if language.lower() in {"ingles", "inglés"}:
            normalized.append("English")
        else:
            normalized.append(language)
    return _unique(normalized)


def estimate_years_experience(text: str) -> float | None:
    explicit = re.search(r"(\d+)\+?\s+years", text, flags=re.IGNORECASE)
    if explicit:
        return float(explicit.group(1))

    more_than = re.search(r"more than\s+(\w+|\d+)\s+years", text, flags=re.IGNORECASE)
    if more_than:
        token = more_than.group(1).lower()
        word_numbers = {
            "five": 5, "ten": 10, "fourteen": 14, "eighteen": 18, "twenty": 20
        }
        return float(word_numbers.get(token, token)) if str(word_numbers.get(token, token)).isdigit() else None

    years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", text)]
    years = [year for year in years if 1990 <= year <= 2026]
    if len(years) >= 2:
        return float(max(years) - min(years))
    return None


def extract_education(text: str) -> list[str]:
    if "EDUCATION" not in text:
        return []
    section = text.split("EDUCATION", 1)[1].split("SKILLS", 1)[0]
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    return lines[:6]


def extract_name_and_title(text: str) -> tuple[str, str | None]:
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if not first_line:
        return "Unknown Candidate", None

    split_markers = [" Montevideo,", " Uruguay", " Salto,", " Punta del Este,"]
    candidate_line = first_line
    for marker in split_markers:
        if marker in candidate_line:
            candidate_line = candidate_line.split(marker, 1)[0]
            break

    words = candidate_line.split()
    if len(words) <= 4:
        return candidate_line.strip(" ·"), None

    stop_words = {
        "at", "en", "Oracle", "Project", "Director", "Founder", "Integration",
        "Developer", "Engineer", "Consultant", "Senior", "Functional", "Leader",
        "Accounting", "Manager", "ERP", "Business", "Analyst", "Oracle", "Techno",
    }
    split_index = len(words)
    for idx, word in enumerate(words):
        if idx >= 2 and word.strip("·") in stop_words:
            split_index = idx
            break
    name = " ".join(words[:split_index]).strip(" ·")
    title = " ".join(words[split_index:]).strip(" ·") or None
    return name, title


def assess_oracle_ebs_experience(text: str) -> str:
    lower = text.lower()
    ebs_mentions = lower.count("oracle e-business suite") + lower.count("oracle ebs") + lower.count("oracle e-business")
    if ebs_mentions >= 3 or "oracle ebs r12" in lower or "20+ years as oracle ebs" in lower:
        return "strong"
    if ebs_mentions >= 1:
        return "moderate"
    if "oracle applications" in lower or "oracle financials" in lower or "oracle scm" in lower:
        return "moderate"
    if "oracle database" in lower or "oracle" in lower:
        return "low"
    return "none"


def extract_job_requirements(document: ParsedDocument) -> JobRequirement:
    text = document.raw_text
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), document.path.stem)
    role_id = Path(document.file_name).stem
    if "integration developer" in text.lower():
        role_id = "position_a"
    elif "business systems analyst" in text.lower():
        role_id = "position_b"

    years_match = re.search(r"(\d+)\s*-\s*(\d+)\s+years|(\d+)\+?\s+years", text, flags=re.IGNORECASE)
    min_years = max_years = None
    if years_match:
        if years_match.group(1) and years_match.group(2):
            min_years = float(years_match.group(1))
            max_years = float(years_match.group(2))
        elif years_match.group(3):
            min_years = float(years_match.group(3))

    return JobRequirement(
        role_id=role_id,
        title=first_line,
        location=extract_location(text),
        required_years_min=min_years,
        required_years_max=max_years,
        required_skills=_find_terms(text, TECHNICAL_TERMS + FUNCTIONAL_TERMS + BUSINESS_ANALYSIS_TERMS),
        preferred_skills=_find_terms(text, ["Matillion", "Snowflake", "Brazil", "Salesforce", "SAP Hybris", "Concur", "Inspyrus"]),
        languages=extract_languages(text),
        functional_knowledge=_find_terms(text, FUNCTIONAL_TERMS),
        technical_knowledge=_find_terms(text, TECHNICAL_TERMS),
        industry_requirements=_find_terms(text, INDUSTRY_TERMS),
        responsibilities=[line.strip() for line in text.splitlines() if line.strip().endswith(".")][:12],
        raw_text=text,
    )


def extract_candidate_profile(document: ParsedDocument) -> CandidateProfile:
    text = document.raw_text
    name, title = extract_name_and_title(text)
    return CandidateProfile(
        candidate_id=Path(document.file_name).stem,
        source_file=document.file_name,
        name=name,
        title=title,
        years_of_experience=estimate_years_experience(text),
        oracle_ebs_experience=assess_oracle_ebs_experience(text),
        technical_skills=_find_terms(text, TECHNICAL_TERMS),
        functional_skills=_find_terms(text, FUNCTIONAL_TERMS + BUSINESS_ANALYSIS_TERMS),
        languages=extract_languages(text),
        education=extract_education(text),
        industry_experience=_find_terms(text, INDUSTRY_TERMS),
        salary_expectation=None,
        location=extract_location(text),
        raw_text=text,
    )
