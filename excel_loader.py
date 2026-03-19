# app/config_loader.py
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

import pandas as pd


@dataclass
class ClusterConfig:
    name: str
    bootstrap_servers: str
    extra: Dict[str, str]


def load_clusters_from_excel(xlsx_path: str) -> List[ClusterConfig]:
    df = pd.read_excel(xlsx_path)  # columns: cluster_name, hostname, port
    clusters: List[ClusterConfig] = []

    for _, row in df.iterrows():
        cluster_name = str(row["cluster_name"])
        hostname = str(row["hostname"])
        port = str(row["port"])
        bootstrap = f"{hostname}:{port}"
        clusters.append(
            ClusterConfig(
                name=cluster_name,
                bootstrap_servers=bootstrap,
                extra={},
            )
        )
    return clusters


def load_client_properties(props_path: str) -> Dict[str, str]:
    props: Dict[str, str] = {}
    path = Path(props_path)
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        props[key.strip()] = value.strip()
    return props
