"""Pydantic schemas for Diamond v5 artifacts."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, conlist, confloat

Confidence = confloat(ge=0.0, le=1.0)


class PlanArtifact(BaseModel):
    goals: conlist(str, min_items=1)
    milestones: List[str]
    acceptance_criteria: List[str]
    risks: List[str]
    slos: List[str] = Field(default_factory=list)
    dri: str
    timeline: str
    confidence: Confidence


class ResearchOption(BaseModel):
    name: str
    pros: List[str]
    cons: List[str]
    links: List[str]


class ResearchArtifact(BaseModel):
    options: conlist(ResearchOption, min_items=1)
    decision_matrix: List[dict]
    chosen: str
    citations: List[str]
    freshness_window_days: int = 120
    confidence: Confidence


class BacklogItem(BaseModel):
    item_id: str
    task: str
    rationale: str
    dependencies: List[str] = Field(default_factory=list)
    owner: Optional[str]


class BacklogArtifact(BaseModel):
    items: conlist(BacklogItem, min_items=1)
    plan_version: str
    confidence: Confidence


class ThreatArtifact(BaseModel):
    dfd: str
    risks: List[str]
    mitigations: List[str]
    controls: List[str]
    rollback_plan: str
    compliance: dict
    confidence: Confidence


class IntegrationArtifact(BaseModel):
    flags: List[str]
    migrations: List[str]
    config_map: dict
    rollback: str
    confidence: Confidence


class TestReport(BaseModel):
    ship: bool
    junit_path: Optional[str]
    coverage: dict
    flakes: List[str]
    confidence: Confidence
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ReleaseReport(BaseModel):
    environment: str
    version: str
    canary_metrics: dict
    health: List[str]
    rollback_cmds: List[str]
    links: List[str]
    confidence: Confidence


__all__ = [
    "PlanArtifact",
    "ResearchArtifact",
    "BacklogArtifact",
    "ThreatArtifact",
    "IntegrationArtifact",
    "TestReport",
    "ReleaseReport",
]
