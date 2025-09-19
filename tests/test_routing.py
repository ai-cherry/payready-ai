from tekton.swarm import describe

def test_workflow_has_threat_stage():
    stages = describe()["stages"]
    assert stages == [
        "plan",
        "research",
        "plan_update",
        "code",
        "review",
        "threat",
        "integrate",
        "test_debug",
        "release",
    ]
