"""Pilot districts: OSM boundary relation (admin_level 6) and Wikidata item. The relation IDs are Wikidata's
'OSM relation ID' (P402) of each district item, and each Overpass response repeats the relation's own tags."""
import os

PILOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docs", "pilot")

DISTRICTS = {
    "lalitpur": {"label": "Lalitpur", "rel": 4583253, "qid": "Q1108338", "province": "Bagmati"},
    "chitwan": {"label": "Chitwan", "rel": 4589410, "qid": "Q28583", "province": "Bagmati"},
    "kanchanpur": {"label": "Kanchanpur", "rel": 4586286, "qid": "Q28981", "province": "Sudurpashchim"},
}
