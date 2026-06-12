from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analytics.signals import MarketSignalAnalyzer
from src.config.loader import ConfigLoader
from src.config.settings import get_settings
from src.storage.database import Database
from src.storage.repositories import OpportunityRepository


def _repository() -> tuple[OpportunityRepository, ConfigLoader]:
    settings = get_settings()
    database = Database(settings.database_url)
    database.init_schema()
    return OpportunityRepository(database), ConfigLoader(settings.organizations_path, settings.profile_path)


def run() -> None:
    st.set_page_config(page_title="Opportunity Intelligence Platform", layout="wide")
    st.title("Opportunity Intelligence Platform")
    repository, loader = _repository()
    opportunities = repository.list_opportunities()
    ranked = repository.ranked_opportunities(limit=500)

    tabs = st.tabs(["Opportunity Feed", "Intelligence Rankings", "Market Signals", "Engagement Pipeline", "Metrics"])

    with tabs[0]:
        st.subheader("Aggregated opportunities")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "organization": item.organization,
                        "title": item.title,
                        "location": item.location,
                        "remote": item.remote,
                        "source": item.source,
                        "url": str(item.url) if item.url else "",
                    }
                    for item in opportunities
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )

    with tabs[1]:
        st.subheader("Top aligned opportunities")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "score": score.alignment_score,
                        "tier": score.tier,
                        "organization": opportunity.organization,
                        "title": opportunity.title,
                        "priority": score.engagement_priority,
                        "strengths": ", ".join(score.strengths[:5]),
                        "gaps": ", ".join(score.gaps[:5]),
                    }
                    for opportunity, score in ranked
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )

    with tabs[2]:
        st.subheader("Market signals")
        profile = loader.load_profile()
        signals = MarketSignalAnalyzer().analyze(opportunities, profile)
        technology_counts = dict(signals["trending_technologies"])
        domain_counts = dict(signals["trending_domains"])
        col1, col2 = st.columns(2)
        col1.bar_chart(pd.Series(technology_counts, dtype="int64"))
        col2.bar_chart(pd.Series(domain_counts, dtype="int64"))

    with tabs[3]:
        st.subheader("Engagement pipeline")
        st.json(repository.engagement_summary())

    with tabs[4]:
        st.subheader("Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Opportunities", len(opportunities))
        col2.metric("Ranked", len(ranked))
        col3.metric("Tier A/B", sum(1 for _, score in ranked if score.alignment_score >= 75))


if __name__ == "__main__":
    run()
