from __future__ import annotations

from dataclasses import dataclass

from extractor import CandidateProfile
from scorer import ScoreBreakdown


@dataclass
class CandidateEvaluation:
    candidate: CandidateProfile
    score_a: ScoreBreakdown
    score_b: ScoreBreakdown
    match_category: str
    best_score: float
    confidence: str
    recommendation: str
    justification: list[str]
    risks: list[str]


def classify_candidate(score_a: float, score_b: float) -> str:
    if score_a >= 80 and score_b < 80:
        return "Position A"
    if score_b >= 80 and score_a < 80:
        return "Position B"
    if score_a >= 80 and score_b >= 80:
        return "Both"
    return "No Match"


def confidence_level(best_score: float, score_gap: float) -> str:
    if best_score >= 85 and score_gap >= 8:
        return "High"
    if best_score >= 80:
        return "High"
    if best_score >= 70:
        return "Medium"
    return "Low"


def recommendation_for(category: str, best_score: float) -> str:
    if category in {"Position A", "Position B", "Both"}:
        return "Contact Immediately"
    if best_score >= 70:
        return "Review Manually / Keep Warm"
    if best_score >= 60:
        return "Backup Candidate"
    return "Do Not Prioritize"


def build_justification(candidate: CandidateProfile, score_a: ScoreBreakdown, score_b: ScoreBreakdown) -> list[str]:
    justifications: list[str] = []
    if candidate.oracle_ebs_experience in {"strong", "moderate"}:
        justifications.append(f"Oracle EBS exposure assessed as {candidate.oracle_ebs_experience}.")
    if candidate.technical_skills:
        justifications.append("Technical evidence: " + ", ".join(candidate.technical_skills[:6]) + ".")
    if candidate.functional_skills:
        justifications.append("Functional/BA evidence: " + ", ".join(candidate.functional_skills[:6]) + ".")
    if candidate.languages:
        justifications.append("Languages: " + ", ".join(candidate.languages) + ".")
    justifications.append(f"Position A score: {score_a.total}; Position B score: {score_b.total}.")
    return justifications


def build_risks(candidate: CandidateProfile, score_a: ScoreBreakdown, score_b: ScoreBreakdown) -> list[str]:
    risks: list[str] = []
    if candidate.oracle_ebs_experience in {"none", "low"}:
        risks.append("Limited explicit Oracle EBS evidence.")
    if not candidate.years_of_experience:
        risks.append("Years of experience could not be estimated confidently from the resume.")
    if "English" not in candidate.languages:
        risks.append("English proficiency is not clearly stated.")
    if score_a.total < 80 and score_b.total < 80:
        risks.append("Does not reach the threshold for either open role.")
    return risks or ["No major risk detected from available resume text."]


def evaluate_candidate(candidate: CandidateProfile, score_a: ScoreBreakdown, score_b: ScoreBreakdown) -> CandidateEvaluation:
    category = classify_candidate(score_a.total, score_b.total)
    best_score = max(score_a.total, score_b.total)
    gap = abs(score_a.total - score_b.total)
    return CandidateEvaluation(
        candidate=candidate,
        score_a=score_a,
        score_b=score_b,
        match_category=category,
        best_score=best_score,
        confidence=confidence_level(best_score, gap),
        recommendation=recommendation_for(category, best_score),
        justification=build_justification(candidate, score_a, score_b),
        risks=build_risks(candidate, score_a, score_b),
    )
