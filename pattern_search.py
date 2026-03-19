# app/topic_search.py
from dataclasses import dataclass
from typing import Dict, List

from .config_loader import ClusterConfig
from .kafka_client import list_topics_for_cluster


@dataclass
class TopicMatch:
    cluster_name: str
    bootstrap_servers: str
    topic_name: str


def search_topic_pattern(
    clusters: List[ClusterConfig],
    base_props: Dict[str, str],
    pattern: str,
    timeout: float = 5.0,
) -> List[TopicMatch]:
    pattern_lower = pattern.lower()
    results: List[TopicMatch] = []

    for cluster in clusters:
        try:
            topics = list_topics_for_cluster(cluster, base_props, timeout=timeout)
        except Exception as exc:
            # For UI: you might collect errors separately
            print(f"Error listing topics for {cluster.name}: {exc}")
            continue

        for t in topics:
            if pattern_lower in t.lower():
                results.append(
                    TopicMatch(
                        cluster_name=cluster.name,
                        bootstrap_servers=cluster.bootstrap_servers,
                        topic_name=t,
                    )
                )
    return results
