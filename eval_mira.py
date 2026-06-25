import pytest
from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric
)
from deepeval.test_case import LLMTestCase

# ── Test Data ─────────────────────────────────────────────
# These are the actual outputs from Mira's baseline tests

# T1 — Project Plan
tc_planner = LLMTestCase(
    input="Generate a project plan for the AI Adoption Project at ABCDE Ltd.",
    actual_output="""Phase 1 - Project Initiation (Week 1-2): Define project scope, 
    form cross-functional team, initial stakeholder meeting. 
    Phase 2 - Current State Analysis (Week 3-4): Assess existing processes and systems.
    Phase 3 - Use Case Selection (Week 5-6): Shortlist priority AI use cases.
    Phase 4 - Pilot Design (Week 7-10): Data collection and model design.
    Phase 5 - Pilot Implementation (Week 11-14): Deploy AI models in test environments.
    Phase 6 - Evaluation (Week 15-16): Evaluate pilot outcomes.
    Phase 7 - Full Deployment (Week 17-22): Scale AI models across departments.
    Phase 8 - Monitoring (Week 23-24): Continuous performance monitoring.""",
    retrieval_context=[
        "ABCDE Ltd. is a logistics company adopting AI for demand forecasting, route optimization, inventory management.",
        "Project timeline spans 24 weeks across 8 phases.",
        "Goals: reduce delivery delays by 15%, lower costs by 10%."
    ]
)

# T3 — Risk Assessment
tc_risk = LLMTestCase(
    input="Generate a risk assessment for the AI Adoption Project at ABCDE Ltd.",
    actual_output="""Top risks identified:
    R01 - Data Quality: Incomplete data leading to poor model performance. Mitigation: Early data audits.
    R02 - Integration Issues: Difficulty integrating AI with legacy systems. Mitigation: Use APIs/middleware.
    R03 - Talent Gap: Lack of internal AI expertise. Mitigation: Staff training and hiring.
    R04 - Change Resistance: Employees resist AI workflows. Mitigation: Change management program.
    R05 - Security Vulnerabilities: AI models targeted by adversarial attacks. Mitigation: Penetration testing.""",
    retrieval_context=[
        "Risk data includes 10 risks across categories: Data Quality, Integration, Talent, Change, Ethics, Cost, Expectations, Drift, Security, Vendor.",
        "Each risk has impact and mitigation strategy defined."
    ]
)

# T10 — Status Report
tc_status = LLMTestCase(
    input="Summarize current project status: tasks done, in progress, to do, blocked?",
    actual_output="""Weekly Status Report - ABCDE Ltd. AI Adoption Project
    Tasks Done: 5 - T001, T002, T003, T004, T005
    Tasks In Progress: 3 - T006, T007, T025
    Tasks Blocked: 1 - T024 Security review of AI infrastructure - BLOCKED: waiting for security team availability
    Tasks To Do: 16
    Total Tasks: 25
    Overall Health: At Risk - one blocker impacting security review.""",
    retrieval_context=[
        "Task board has 25 tasks total.",
        "5 tasks are Done, 3 In Progress, 1 Blocked (T024), 16 To Do.",
        "T024 is blocked waiting for security team availability."
    ]
)

# ── Metrics ───────────────────────────────────────────────
answer_relevancy = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
faithfulness = FaithfulnessMetric(threshold=0.7, model="gpt-4o-mini")

# ── Test Functions ────────────────────────────────────────
def test_planner_relevancy():
    answer_relevancy.measure(tc_planner)
    print(f"\nPlanner Relevancy Score: {answer_relevancy.score}")
    assert answer_relevancy.score >= 0.7

def test_risk_relevancy():
    answer_relevancy.measure(tc_risk)
    print(f"\nRisk Relevancy Score: {answer_relevancy.score}")
    assert answer_relevancy.score >= 0.7

def test_status_faithfulness():
    faithfulness.measure(tc_status)
    print(f"\nStatus Faithfulness Score: {faithfulness.score}")
    assert faithfulness.score >= 0.7

if __name__ == "__main__":
    evaluate(
        test_cases=[tc_planner, tc_risk, tc_status],
        metrics=[answer_relevancy, faithfulness]
    )