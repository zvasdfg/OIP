from __future__ import annotations

from src.models.evaluation import OpportunityScore
from src.models.opportunity import Opportunity
from src.storage.database import Database
from src.storage.repositories import OpportunityRepository


def test_repository_persists_opportunities_and_scores(tmp_path, opportunity: Opportunity) -> None:
    database = Database(f"sqlite:///{tmp_path / 'oip.sqlite3'}")
    database.init_schema()
    repository = OpportunityRepository(database)

    assert repository.save_opportunities([opportunity]) == 1
    stored = repository.list_opportunities()
    assert stored[0].title == opportunity.title

    score = OpportunityScore(
        opportunity_id=opportunity.opportunity_id,
        alignment_score=90,
        tier="A",
        strategic_fit="high",
        engagement_priority="recommended",
        criterion_scores={},
        analysis="Strong fit.",
    )
    assert repository.save_scores([score]) == 1
    ranked = repository.ranked_opportunities()
    assert ranked[0][1].alignment_score == 90


def test_repository_updates_organizations_and_opportunities(tmp_path, opportunity: Opportunity, organization) -> None:
    database = Database(f"sqlite:///{tmp_path / 'oip.sqlite3'}")
    database.init_schema()
    repository = OpportunityRepository(database)

    assert repository.save_organizations([organization]) == 1
    updated_org = organization.model_copy(update={"priority": "medium"})
    assert repository.save_organizations([updated_org]) == 1

    repository.save_opportunities([opportunity])
    changed = opportunity.model_copy(update={"description": opportunity.description + " Updated."})
    repository.save_opportunities([changed])

    stored = repository.list_opportunities(limit=1)
    assert stored[0].description.endswith("Updated.")
    assert repository.latest_scores(limit=1) == {}
    repository.save_analytics("test", {"value": 1}, value=1.0)
    assert repository.engagement_summary() == {}
