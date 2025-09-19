from core.schemas import artifacts

def test_plan_schema_roundtrip():
    payload = artifacts.PlanArtifact(
        goals=["Improve webhook retries"],
        milestones=["Design", "Implement"],
        acceptance_criteria=["Retries are idempotent"],
        risks=["Duplicate execution"],
        dri="Payments Team",
        timeline="2 sprints",
        confidence=0.8,
    )
    assert payload.confidence == 0.8
