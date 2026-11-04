"""Nepal's seven provinces: OSM boundary relation (admin_level 4; Wikidata P402) and Wikidata item."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "data_collection", "collected")

PROVINCES = {
    "koshi": {"label": "Koshi", "rel": 10489132, "qid": "Q25104008"},
    "madhesh": {"label": "Madhesh", "rel": 10489318, "qid": "Q25104009"},
    "bagmati": {"label": "Bagmati", "rel": 10489317, "qid": "Q25104015"},
    "gandaki": {"label": "Gandaki", "rel": 10489605, "qid": "Q25104016"},
    "lumbini": {"label": "Lumbini", "rel": 10493722, "qid": "Q25104014"},
    "karnali": {"label": "Karnali", "rel": 10493723, "qid": "Q25104017"},
    "sudurpashchim": {"label": "Sudurpashchim", "rel": 10488187, "qid": "Q25104019"},
}
