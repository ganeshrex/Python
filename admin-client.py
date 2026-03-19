# app/kafka_client.py
from typing import Dict, List
from confluent_kafka.admin import AdminClient

from .config_loader import ClusterConfig


def build_admin_client(cluster: ClusterConfig, base_props: Dict[str, str]) -> AdminClient:
    conf = dict(base_props)
    conf["bootstrap.servers"] = cluster.bootstrap_servers
    return AdminClient(conf)


def list_topics_for_cluster(
    cluster: ClusterConfig,
    base_props: Dict[str, str],
    timeout: float = 5.0,
) -> List[str]:
    admin = build_admin_client(cluster, base_props)
    md = admin.list_topics(timeout=timeout)  # synchronous metadata call [web:7][web:19]
    return list(md.topics.keys())  # topic names
