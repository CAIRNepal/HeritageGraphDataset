"""Shared fixtures. The graph is built once per test session from the same inputs as release v1.0.0:
staging/monuments.csv plus DANAM's export tables for events and objects (staging has none yet)."""
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import build_kg  # noqa: E402

MONUMENTS = os.path.join(REPO, "staging", "monuments.csv")
EVENTS = os.path.join(REPO, "data_collection", "data", "exports", "events.csv")
OBJECTS = os.path.join(REPO, "data_collection", "data", "exports", "objects.csv")


@pytest.fixture(scope="session")
def built():
    """(graph, stats) of a full build."""
    return build_kg.build_knowledge_graph(MONUMENTS, EVENTS, OBJECTS)


@pytest.fixture(scope="session")
def graph(built):
    return built[0]
