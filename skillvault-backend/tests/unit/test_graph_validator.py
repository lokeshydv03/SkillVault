import pytest
from app.skills.graph_validator import GraphValidator


def test_graph_validator_valid_dag():
    validator = GraphValidator(max_depth=20, max_steps=30)
    steps = [
        {"step_number": 1, "skill_id": "skill_1", "input_mapping": {}},
        {"step_number": 2, "skill_id": "skill_2", "input_mapping": {"data": "steps.1.output"}},
    ]
    res = validator.validate_graph(steps, {"skill_1", "skill_2"})
    assert res.valid is True
    assert len(res.errors) == 0


def test_graph_validator_nonexistent_skill():
    validator = GraphValidator()
    steps = [{"step_number": 1, "skill_id": "missing_skill"}]
    res = validator.validate_graph(steps, {"skill_1"})
    assert res.valid is False
    assert any("references non-existent Skill ID" in e for e in res.errors)


def test_graph_validator_cycle_detection():
    validator = GraphValidator()
    steps = [
        {"step_number": 1, "skill_id": "skill_1", "input_mapping": {"input": "steps.2.output"}},
        {"step_number": 2, "skill_id": "skill_2", "input_mapping": {"input": "steps.1.output"}},
    ]
    res = validator.validate_graph(steps, {"skill_1", "skill_2"})
    assert res.valid is False
    assert any("Cyclic dependency detected" in e for e in res.errors)


def test_graph_validator_max_steps_exceeded():
    validator = GraphValidator(max_steps=2)
    steps = [
        {"step_number": 1, "skill_id": "skill_1"},
        {"step_number": 2, "skill_id": "skill_2"},
        {"step_number": 3, "skill_id": "skill_3"},
    ]
    res = validator.validate_graph(steps, {"skill_1", "skill_2", "skill_3"})
    assert res.valid is False
    assert any("exceeds maximum allowed steps limit" in e for e in res.errors)
