# Multi-source pilot (DANAM, OpenStreetMap, Wikidata)

Three districts, each with the same queries and matching rules; nothing is merged into the dataset.

- `COMPARISON.md`: one table for all districts (`tools/pilot/compare.py`).
- `<district>/REPORT.md`, `<district>/candidates_*.csv`, `<district>/summary.json`: per district (`tools/pilot/match.py <district>`).
- `<district>/raw/`: the Overpass and Wikidata queries, raw responses and retrieval times (`tools/pilot/fetch.py <district>`;
  Lalitpur was fetched by hand with the same queries, see `lalitpur/raw/README.md`).

Districts and their OSM boundary relations are in `tools/pilot/districts.py`.

Licences: OpenStreetMap data © OpenStreetMap contributors, ODbL 1.0 (<https://www.openstreetmap.org/copyright>);
Wikidata CC0 1.0; DANAM not yet settled. Requests identified themselves with the User-Agent
`HeritageGraphDataset-pilot/0.1 (CAIR-Nepal research; https://github.com/CAIRNepal/HeritageGraphDataset)`; one Overpass
data request per district for Chitwan and Kanchanpur, each sent only when the server reported a free slot.
