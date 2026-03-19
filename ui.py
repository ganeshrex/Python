# app/ui_streamlit.py
import streamlit as st
import pandas as pd
from pathlib import Path

from .config_loader import load_clusters_from_excel, load_client_properties
from .topic_search import search_topic_pattern


def load_initial_config():
    base_dir = Path(__file__).resolve().parents[1]
    excel_path = base_dir / "config" / "clusters.xlsx"
    props_path = base_dir / "config" / "client.properties"

    clusters = load_clusters_from_excel(str(excel_path))
    base_props = load_client_properties(str(props_path))
    return clusters, base_props


def main():
    st.title("Kafka Topic Explorer (Multi-Cluster)")

    # Load config once and cache it
    @st.cache_resource
    def get_config():
        return load_initial_config()

    clusters, base_props = get_config()

    pattern = st.text_input("Topic name or pattern", placeholder="e.g. payments, .*_events")
    use_regex = st.checkbox("Use regex match", value=False)

    if st.button("Search") and pattern:
        if use_regex:
            import re

            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                st.error(f"Invalid regex: {e}")
                return

            def matcher(name: str) -> bool:
                return bool(regex.search(name))

        else:
            p = pattern.lower()

            def matcher(name: str) -> bool:
                return p in name.lower()

        from .topic_search import TopicMatch
        from .kafka_client import list_topics_for_cluster

        results = []
        errors = []

        progress = st.progress(0.0, text="Searching clusters...")

        for idx, cluster in enumerate(clusters):
            try:
                topics = list_topics_for_cluster(cluster, base_props)
                for t in topics:
                    if matcher(t):
                        results.append(
                            TopicMatch(
                                cluster_name=cluster.name,
                                bootstrap_servers=cluster.bootstrap_servers,
                                topic_name=t,
                            )
                        )
            except Exception as exc:
                errors.append(f"{cluster.name}: {exc}")

            progress.progress((idx + 1) / len(clusters))

        if results:
            df = pd.DataFrame(
                [
                    {
                        "cluster": r.cluster_name,
                        "bootstrap_servers": r.bootstrap_servers,
                        "topic": r.topic_name,
                    }
                    for r in results
                ]
            )
            st.subheader("Matches")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No topics matched the pattern.")

        if errors:
            with st.expander("Errors while querying some clusters"):
                for line in errors:
                    st.warning(line)
    else:
        st.write("Enter a pattern and click Search to begin.")


if __name__ == "__main__":
    main()
