#!/usr/bin/env python3
"""Build Knowledge Graph (KG) RDFs for Linked Open Data (LOD) and SPARQL querying.

Transforms staging / export CSVs (monuments.csv, events.csv, objects.csv) into
standards-compliant RDF Knowledge Graphs serialized in Turtle (.ttl), N-Triples (.nt),
and JSON-LD (.jsonld), aligned with:
- CAIR-Nepal CulturalHeritageOntology (heritageGraph, v0.1.0-alpha.2)
- CIDOC-CRM (v7.1.2)
- W3C PROV-O (Provenance Ontology)
- Getty Art & Architecture Thesaurus (AAT)
- GeoSPARQL & WGS84 Geo
- W3C VoID & DCAT (Linked Open Data dataset description)

Usage:
    uv run --with rdflib python .agents/skills/danam-to-heritagegraph/scripts/build_kg.py
    python build_kg.py --help
"""

import argparse
import csv
import os
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime

# Reconfigure Windows console to handle UTF-8 / IAST diacritics
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import rdflib
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, OWL, RDF, RDFS, VOID, XSD

csv.field_size_limit(10**9)

# ── Namespaces ────────────────────────────────────────────────────────────────
HG = Namespace("https://cair-nepal.org/heritagegraph/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
PROV = Namespace("http://www.w3.org/ns/prov#")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
GEOSPARQL = Namespace("http://www.opengis.net/ont/geosparql#")
AAT = Namespace("http://vocab.getty.edu/aat/")
SCHEMA = Namespace("https://schema.org/")
RES = Namespace("https://data.cairnepal.org/heritage/resource/")
# Extension vocabulary (vocab/hgn.ttl) for terms the HeritageGraph ontology does not declare. Temporary base IRI.
HGN_BASE = "https://w3id.org/heritagegraph-nepal/vocab#"
HGN = Namespace(HGN_BASE)

AAT_STYLE_TO_HG = {
    "300004829": "Pagoda",
    "300446671": "Shikhara",
    "300001285": "Dome",
    "300007562": "Chaitya",
    "300007576": "Stupa",
}

# hg: classes that the ontology publishes under a CIDOC-CRM IRI (LinkML class_uri). The CRM IRI is written instead,
# because the ontology does not declare the hg: IRI.
CRM_CLASS_FOR = {
    "HumanMadeObject": CRM["E22_Human-Made_Object"],
    "Production": CRM["E12_Production"],
    "ConditionAssessment": CRM["E14_Condition_Assessment"],
    "Place": CRM["E53_Place"],
    "DestructionEvent": CRM["E6_Destruction"],
    "TransferOfCustody": CRM["E10_Transfer_of_Custody"],
}


def hg_class(name: str) -> URIRef:
    """IRI of an ontology class given by its local name (e.g. from an ontology_class cell)."""
    return CRM_CLASS_FOR.get(name, HG[name])


# ── Classification Helpers ───────────────────────────────────────────────────
def slugify(text: str) -> str:
    """Create a URL-safe IRI slug."""
    if not text:
        return "unknown"
    normalized = unicodedata.normalize("NFKD", text)
    cleaned = "".join(c for c in normalized if not unicodedata.combining(c))
    slug = re.sub(r"[^a-zA-Z0-9_\-]+", "_", cleaned).strip("_").lower()
    return slug or "unknown"


def classify_event(name: str, desc: str) -> str:
    """Map event description and name to CulturalHeritageOntology class."""
    combined = f"{name} {desc}".lower()
    if re.search(r"\b(prāṇapratiṣṭhā|pranapratistha|consecrat)", combined):
        return "Consecration"
    if re.search(r"\b(enshrin|install.*image|installed in.*sanctum|enshrined)", combined):
        return "Enshrinement"
    if re.search(r"\b(dismantl|collaps|burnt|burn|demolish|destroy|earthquake|flood|fire|damage)", combined):
        return "DestructionEvent"
    if re.search(r"\b(endow|guṭhi|guthi|handed|transfer|custody|allocated|grant)", combined):
        return "TransferOfCustody"
    if re.search(r"\b(puja|pūjā|jātrā|jatra|festival|bhajan|procession|purification|omen|blood)", combined):
        return "RitualEvent"
    if re.search(r"\b(built|construct|rebuil|renovat|install.*roof|install.*toraṇa|install.*door|repair|erect|found|offer.*pinnacle|offer.*gilded|restor)", combined):
        return "Production"
    if re.search(r"\b(assess|survey|document)", combined):
        return "ConditionAssessment"
    return "HistoricalEvent"


def classify_object(name: str, otype: str) -> str:
    """Map object name and type to CulturalHeritageOntology class."""
    combined = f"{name} {otype}".lower()
    if re.search(r"\b(murti|statue|deity|viṣṇu|visnu|shiva|śiva|buddha|ganesh|gaṇeśa|bhairava|devi|tārā|tara|image of)", combined):
        return "Murti"
    if re.search(r"\b(paubhā|paubha|thangka|painting|mural|fresco)", combined):
        return "Paubha"
    if re.search(r"\b(toraṇa|torana|gajūra|gajura|pinnacle|finial|door|window|strut|pillar|stele|roof|plinth|lintel|bracket)", combined):
        return "ArchitecturalElement"
    if re.search(r"\b(lion|dhvaja|lamp|bell|caitya|chaitya|vessel|urn|movable|sacred|trident)", combined):
        return "IconographicObject"
    return "HumanMadeObject"


def clean_clean_aat(style_str: str) -> list[str]:
    """Extract valid AAT IDs from string like 'aat:300004829|aat:300446671'."""
    if not style_str:
        return []
    matches = re.findall(r"aat:(\d+)", style_str)
    return matches


def extract_year(date_str: str) -> int | None:
    """Extract numerical year from strings like '1689 CE', '1300 BCE', etc."""
    if not date_str:
        return None
    m = re.search(r"\b(\d{1,4})\s*(CE|AD)?\b", date_str)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


# ── KG Builder ────────────────────────────────────────────────────────────────
def build_knowledge_graph(
    monuments_path: str,
    events_path: str,
    objects_path: str,
    limit: int | None = None,
) -> tuple[Graph, dict]:
    """Construct the RDF Knowledge Graph from input staging / export CSV files."""
    g = Graph()

    # Bind namespaces
    g.bind("hg", HG)
    g.bind("crm", CRM)
    g.bind("prov", PROV)
    g.bind("geo", GEO)
    g.bind("geosparql", GEOSPARQL)
    g.bind("aat", AAT)
    g.bind("schema", SCHEMA)
    g.bind("void", VOID)
    g.bind("dcat", DCAT)
    g.bind("dcterms", DCTERMS)
    g.bind("res", RES)

    # ── 1. VoID Dataset & LOD Description ─────────────────────────────────────
    dataset_uri = RES["dataset"]
    g.add((dataset_uri, RDF.type, VOID.Dataset))
    g.add((dataset_uri, RDF.type, DCAT.Dataset))
    g.add((dataset_uri, DCTERMS.title, Literal("CAIR-Nepal HeritageGraph Linked Open Dataset", lang="en")))
    g.add((
        dataset_uri,
        DCTERMS.description,
        Literal(
            "Event-centric cultural heritage knowledge graph of Nepal derived from DANAM "
            "(Digital Archive of Nepalese Arts and Monuments) and aligned with the "
            "CAIR-Nepal CulturalHeritageOntology, CIDOC-CRM, PROV-O, and Getty AAT.",
            lang="en",
        ),
    ))
    g.add((dataset_uri, DCTERMS.publisher, URIRef("https://cairnepal.org")))
    g.add((dataset_uri, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by-sa/4.0/")))
    g.add((dataset_uri, DCTERMS.source, URIRef("https://danam.cats.uni-heidelberg.de")))
    g.add((dataset_uri, DCTERMS.issued, Literal(datetime.now().strftime("%Y-%m-%d"), datatype=XSD.date)))
    g.add((dataset_uri, VOID.sparqlEndpoint, URIRef("https://data.cairnepal.org/sparql")))
    g.add((dataset_uri, VOID.vocabulary, URIRef(str(HG))))
    g.add((dataset_uri, VOID.vocabulary, URIRef(str(CRM))))
    g.add((dataset_uri, VOID.vocabulary, URIRef(str(PROV))))
    g.add((dataset_uri, VOID.vocabulary, URIRef(str(AAT))))

    # ── 1.1 PROV-O Agents & Activity ──────────────────────────────────────────
    agent_antigravity = RES["agent/antigravity_agent"]
    g.add((agent_antigravity, RDF.type, PROV.SoftwareAgent))
    g.add((agent_antigravity, RDF.type, PROV.Agent))
    g.add((agent_antigravity, RDFS.label, Literal("Antigravity AI Agent (DeepMind)", lang="en")))
    g.add((agent_antigravity, HG.skill, Literal("danam-to-heritagegraph", lang="en")))
    g.add((agent_antigravity, SCHEMA.softwareRequirements, Literal("danam-to-heritagegraph skill (CAIR-Nepal)", lang="en")))

    agent_cair = RES["agent/cair_nepal"]
    g.add((agent_cair, RDF.type, PROV.Organization))
    g.add((agent_cair, RDF.type, PROV.Agent))
    g.add((agent_cair, RDFS.label, Literal("CAIR-Nepal (Center for Artificial Intelligence Research Nepal)", lang="en")))
    g.add((agent_cair, SCHEMA.url, URIRef("https://cairnepal.org")))
    g.add((agent_antigravity, PROV.actedOnBehalfOf, agent_cair))

    agent_danam = RES["agent/danam_heidelberg"]
    g.add((agent_danam, RDF.type, PROV.Organization))
    g.add((agent_danam, RDF.type, PROV.Agent))
    g.add((agent_danam, RDFS.label, Literal("Digital Archive of Nepalese Arts and Monuments (DANAM), Heidelberg University", lang="en")))
    g.add((agent_danam, SCHEMA.url, URIRef("https://danam.cats.uni-heidelberg.de")))

    activity_kg = RES["activity/heritagegraph_kg_construction"]
    g.add((activity_kg, RDF.type, PROV.Activity))
    g.add((activity_kg, RDFS.label, Literal("HeritageGraph Knowledge Graph Construction & LOD Export Activity", lang="en")))
    g.add((activity_kg, PROV.wasAssociatedWith, agent_antigravity))
    g.add((activity_kg, PROV.used, URIRef("https://danam.cats.uni-heidelberg.de")))
    g.add((URIRef("https://danam.cats.uni-heidelberg.de"), RDF.type, PROV.Entity))

    g.add((dataset_uri, PROV.wasAttributedTo, agent_antigravity))
    g.add((dataset_uri, PROV.wasAttributedTo, agent_cair))
    g.add((dataset_uri, PROV.wasGeneratedBy, activity_kg))

    # ── 2. Monuments ───────────────────────────────────────────────────────────
    print(f"[*] Reading monuments from {monuments_path}...")
    monuments = {}
    with open(monuments_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            monuments[r["resource_id"]] = r

    mon_count = 0
    active_mon_ids = set()
    places_cache = {}
    deities_cache = {}

    for res_id, m in monuments.items():
        if limit and mon_count >= limit:
            break
        mon_count += 1
        active_mon_ids.add(res_id)

        m_uri = RES[f"monument/{res_id}"]
        g.add((m_uri, RDF.type, CRM["E22_Human-Made_Object"]))
        g.add((m_uri, RDF.type, HG.ArchitecturalStructure))

        # Assign specific ontology class
        ont_cls_str = m.get("ontology_class", "").strip()
        classes_to_add = set()
        if ont_cls_str:
            for cls_name in ont_cls_str.split("|"):
                cls_clean = cls_name.strip()
                if cls_clean:
                    classes_to_add.add(cls_clean)
        else:
            mtype = (m.get("monument_type") or "").lower()
            if "temple" in mtype or "mandir" in mtype:
                classes_to_add.add("Temple")
            elif "caitya" in mtype or "chaitya" in mtype:
                classes_to_add.add("Chaitya")
            elif "stupa" in mtype:
                classes_to_add.add("Stupa")
            elif "water architecture" in mtype or "hiti" in mtype or "dhārā" in mtype:
                classes_to_add.add("DhungeDhara")
            elif "pokhari" in mtype:
                classes_to_add.add("Pokhari")
            elif "pati" in mtype or "phalcā" in mtype:
                classes_to_add.add("Pati")
            elif "sattal" in mtype:
                classes_to_add.add("Sattal")

        for c_name in classes_to_add:
            g.add((m_uri, RDF.type, HG[c_name]))
            if c_name in ["Temple", "Chaitya", "Stupa", "KumariHouse"]:
                g.add((m_uri, RDF.type, HG.ReligiousStructure))
            elif c_name in ["Pati", "Sattal", "Dharmashala"]:
                g.add((m_uri, RDF.type, HG.RestHouse))
            elif c_name in ["DhungeDhara", "Pokhari"]:
                g.add((m_uri, RDF.type, HG.WaterStructure))

        # Names & Identifiers
        m_name = m.get("monument_name", "").strip()
        if m_name:
            g.add((m_uri, RDFS.label, Literal(m_name, lang="en")))
            g.add((m_uri, DCTERMS.title, Literal(m_name, lang="en")))

        anglicized = m.get("anglicized_name", "").strip()
        if anglicized and anglicized != m_name:
            g.add((m_uri, SCHEMA.alternateName, Literal(anglicized, lang="en")))

        name_ne = m.get("name_ne", "").strip() or m.get("name_devanagari", "").strip()
        if name_ne:
            g.add((m_uri, SCHEMA.name, Literal(name_ne, lang="ne")))

        g.add((m_uri, DCTERMS.identifier, Literal(res_id)))

        danam_code = m.get("danam_code", "").strip()
        if danam_code:
            g.add((m_uri, HG.danamCode, Literal(danam_code)))
            code_uri = RES[f"monument/{danam_code}"]
            g.add((m_uri, OWL.sameAs, code_uri))
            g.add((code_uri, OWL.sameAs, m_uri))

        # Architectural styles: every AAT concept DANAM lists on crm:P2_has_type; one ontology style value (the ontology
        # allows one) on hg:hasArchitecturalStyle, the first DANAM lists. Further styles are recorded in a note.
        aat_styles = clean_clean_aat(m.get("aat_style", ""))
        for aat_id in aat_styles:
            g.add((m_uri, CRM["P2_has_type"], AAT[aat_id]))
        hg_styles = [AAT_STYLE_TO_HG[a] for a in aat_styles if a in AAT_STYLE_TO_HG]
        if hg_styles:
            g.add((m_uri, HG.hasArchitecturalStyle, HG[f"ArchitecturalStyle#{hg_styles[0]}"]))
        if len(hg_styles) > 1:
            g.add((m_uri, CRM["P3_has_note"], Literal(
                f"DANAM also lists the architectural style {', '.join(hg_styles[1:])}; "
                f"the ontology allows one style per structure, so the first listed ({hg_styles[0]}) is used.")))

        # Religion & Main Deity
        religion = m.get("religion", "").strip()
        if religion:
            g.add((m_uri, HG.hasReligiousTradition, Literal(religion, lang="en")))

        main_deity = m.get("main_deity", "").strip()
        if main_deity:
            d_slug = slugify(main_deity)
            d_uri = RES[f"deity/{d_slug}"]
            g.add((m_uri, HG.hasMainDeity, d_uri))
            if d_slug not in deities_cache:
                deities_cache[d_slug] = True
                g.add((d_uri, RDF.type, HG.Deity))
                g.add((d_uri, RDFS.label, Literal(main_deity, lang="en")))
                if religion:
                    g.add((d_uri, HG.hasReligiousTradition, Literal(religion, lang="en")))

        # Geographic Location & Place
        district = m.get("district", "").strip()
        municipality = m.get("municipality", "").strip()
        tola = m.get("tola", "").strip()
        province = m.get("province", "").strip()

        if district or municipality or tola:
            place_slug = slugify(f"{district}_{municipality}_{tola}")
            p_uri = RES[f"place/{place_slug}"]
            g.add((m_uri, CRM["P55_has_current_location"], p_uri))
            g.add((m_uri, CRM["P53_has_former_or_current_location"], p_uri))
            if place_slug not in places_cache:
                places_cache[place_slug] = True
                g.add((p_uri, RDF.type, hg_class("Place")))
                g.add((p_uri, RDF.type, SCHEMA.Place))
                label_parts = [p for p in [tola, municipality, district] if p]
                if label_parts:
                    g.add((p_uri, RDFS.label, Literal(", ".join(label_parts), lang="en")))
                if district:
                    g.add((p_uri, HG.district, Literal(district, lang="en")))
                if municipality:
                    g.add((p_uri, HG.municipality, Literal(municipality, lang="en")))
                if tola:
                    g.add((p_uri, HG.tola, Literal(tola, lang="en")))
                if province:
                    g.add((p_uri, HG.province, Literal(province)))

        # GeoSPARQL & WGS84 Coordinates
        lat_str = m.get("coordinates_lat", "").strip()
        lon_str = m.get("coordinates_lon", "").strip()
        if lat_str and lon_str:
            try:
                lat = float(lat_str)
                lon = float(lon_str)
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    g.add((m_uri, GEO.lat, Literal(lat, datatype=XSD.decimal)))
                    g.add((m_uri, GEO.long, Literal(lon, datatype=XSD.decimal)))

                    geom_uri = RES[f"geometry/{res_id}"]
                    g.add((m_uri, GEOSPARQL.hasGeometry, geom_uri))
                    g.add((geom_uri, RDF.type, GEOSPARQL.Geometry))
                    wkt_literal = Literal(f"POINT({lon} {lat})", datatype=GEOSPARQL.wktLiteral)
                    g.add((geom_uri, GEOSPARQL.asWKT, wkt_literal))
            except ValueError:
                pass

        # Physical Architecture Attributes
        storeys = m.get("num_storeys", "").strip()
        if storeys and storeys.isdigit():
            g.add((m_uri, HG.numStoreys, Literal(int(storeys), datatype=XSD.integer)))

        roofs = m.get("num_roofs", "").strip()
        if roofs and roofs.isdigit():
            g.add((m_uri, HG.numRoofs, Literal(int(roofs), datatype=XSD.integer)))

        roof_type = m.get("roof_type", "").strip()
        if roof_type:
            g.add((m_uri, HG.roofType, Literal(roof_type, lang="en")))

        shape = m.get("monument_shape", "").strip()
        if shape:
            g.add((m_uri, HG.monumentShape, Literal(shape, lang="en")))

        brick = m.get("brick_type", "").strip()
        if brick:
            g.add((m_uri, HG.brickType, Literal(brick, lang="en")))

        # Condition Assessment & Threats
        assess = m.get("monument_assessment", "").strip()
        threats = m.get("identified_threats", "").strip()
        cond_types = m.get("condition_types", "").strip()

        if assess or threats or cond_types:
            assess_uri = RES[f"assessment/{res_id}"]
            state_uri = RES[f"condition_state/{res_id}"]
            g.add((m_uri, CRM["P44_has_condition"], assess_uri))
            g.add((m_uri, CRM["P34i_was_assessed_by"], assess_uri))
            g.add((assess_uri, RDF.type, CRM["E14_Condition_Assessment"]))
            g.add((assess_uri, CRM["P34_concerned"], m_uri))
            g.add((assess_uri, CRM["P35_has_identified"], state_uri))
            g.add((state_uri, RDF.type, CRM["E3_Condition_State"]))
            g.add((assess_uri, RDFS.label, Literal(f"Condition assessment of {m_name}", lang="en")))
            if assess:
                g.add((assess_uri, RDFS.comment, Literal(assess, lang="en")))
                g.add((assess_uri, CRM["P3_has_note"], Literal(assess, lang="en")))
            if cond_types:
                for c_type in cond_types.split("|"):
                    c_clean = c_type.strip()
                    if c_clean:
                        g.add((m_uri, HG.conditionStatus, Literal(c_clean, lang="en")))
                        if c_clean in ["Good", "Damaged", "Ruined", "Restored"]:
                            g.add((state_uri, HG.hasConditionType, HG[f"ConditionType#{c_clean}"]))
                            if c_clean == "Ruined":
                                g.add((m_uri, HG.existenceStatus, HG["ExistenceStatus#Ruined"]))
                            elif c_clean == "Damaged":
                                g.add((m_uri, HG.existenceStatus, HG["ExistenceStatus#PartiallyExtant"]))
                            else:
                                g.add((m_uri, HG.existenceStatus, HG["ExistenceStatus#Extant"]))
            if threats:
                g.add((assess_uri, HG.identifiedThreats, Literal(threats, lang="en")))

        # Provenance: Link to original DANAM source report URL
        danam_url = m.get("url", "").strip()
        if danam_url and danam_url.startswith("http"):
            g.add((m_uri, PROV.wasDerivedFrom, URIRef(danam_url)))
            g.add((URIRef(danam_url), RDF.type, PROV.Entity))
            g.add((m_uri, SCHEMA.url, URIRef(danam_url)))

        scraped_at = m.get("scraped_at", "").strip()
        if scraped_at:
            try:
                g.add((m_uri, PROV.generatedAtTime, Literal(scraped_at, datatype=XSD.dateTime)))
            except Exception:
                pass

        refs = m.get("references", "").strip()
        if refs:
            g.add((m_uri, DCTERMS.references, Literal(refs, lang="en")))

    print(f"[+] Loaded {mon_count} monuments into graph.")

    # ── 3. Events ─────────────────────────────────────────────────────────────
    print(f"[*] Reading events from {events_path}...")
    ev_count = 0
    with open(events_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            res_id = r["resource_id"]
            if res_id not in active_mon_ids:
                continue

            idx = r.get("event_index", str(ev_count))
            ev_uri = RES[f"event/{res_id}_{idx}"]
            m_uri = RES[f"monument/{res_id}"]

            ev_name = r.get("event_name", "").strip() or "Historical event"
            ev_desc = r.get("event_description", "").strip()

            # Classify event
            ev_class_name = r.get("ontology_class", "").strip() or classify_event(ev_name, ev_desc)
            g.add((ev_uri, RDF.type, hg_class(ev_class_name)))
            g.add((ev_uri, RDF.type, CRM["E5_Event"]))
            if ev_class_name == "Production":
                g.add((ev_uri, RDF.type, CRM["E12_Production"]))
            elif ev_class_name == "DestructionEvent":
                g.add((ev_uri, RDF.type, CRM["E6_Destruction"]))
            elif ev_class_name == "TransferOfCustody":
                g.add((ev_uri, RDF.type, CRM["E10_Transfer_of_Custody"]))
            elif ev_class_name == "ConditionAssessment":
                g.add((ev_uri, RDF.type, CRM["E14_Condition_Assessment"]))
            elif ev_class_name in ["RitualEvent", "Consecration", "Enshrinement"]:
                g.add((ev_uri, RDF.type, HG.RitualEvent))

            g.add((ev_uri, RDFS.label, Literal(ev_name, lang="en")))
            if ev_desc:
                g.add((ev_uri, DCTERMS.description, Literal(ev_desc, lang="en")))
                g.add((ev_uri, RDFS.comment, Literal(ev_desc, lang="en")))

            # Link Event <-> Monument
            g.add((ev_uri, CRM["P12_occurred_in_the_presence_of"], m_uri))
            g.add((m_uri, CRM["P12i_was_present_at"], ev_uri))

            try:
                g.add((ev_uri, HG.eventIndex, Literal(int(idx), datatype=XSD.integer)))
            except ValueError:
                pass

            # Dates and Timelines
            date_ce = r.get("date_bce_ce", "").strip()
            if date_ce:
                g.add((ev_uri, HG.dateBCE_CE, Literal(date_ce)))
                cal_year = extract_year(date_ce)
                if cal_year:
                    g.add((ev_uri, HG.calendarYear, Literal(cal_year, datatype=XSD.integer)))

            period = r.get("period", "").strip()
            if period:
                g.add((ev_uri, HG.historicalPeriod, Literal(period, lang="en")))

            era_year = r.get("year_ss_ns_vs", "").strip()
            if era_year:
                g.add((ev_uri, HG.inscriptionalDateEra, Literal(era_year)))

            nep_month = r.get("nepali_month", "").strip()
            if nep_month:
                g.add((ev_uri, HG.nepaliMonth, Literal(nep_month, lang="en")))

            paksha = r.get("paksha", "").strip()
            if paksha:
                g.add((ev_uri, HG.paksha, Literal(paksha, lang="en")))

            tithi = r.get("tithi", "").strip()
            if tithi and tithi.isdigit():
                g.add((ev_uri, HG.tithi, Literal(int(tithi), datatype=XSD.integer)))

            # Provenance
            sources = r.get("sources", "").strip()
            if sources:
                g.add((ev_uri, DCTERMS.source, Literal(sources)))
                g.add((ev_uri, PROV.hadPrimarySource, Literal(sources)))

            evidence = r.get("evidence_text", "").strip()
            if evidence:
                g.add((ev_uri, HG.evidenceText, Literal(evidence, lang="en")))

            extraction_method = r.get("extraction_method", "").strip() or "source_table"
            g.add((ev_uri, HG.extractionMethod, Literal(extraction_method)))
            g.add((ev_uri, PROV.wasAttributedTo, agent_antigravity))
            g.add((ev_uri, PROV.wasGeneratedBy, activity_kg))

            ev_count += 1

    print(f"[+] Loaded {ev_count} events into graph.")

    # ── 4. Objects ────────────────────────────────────────────────────────────
    print(f"[*] Reading objects from {objects_path}...")
    obj_count = 0
    with open(objects_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            res_id = r["resource_id"]
            if res_id not in active_mon_ids:
                continue

            obj_id = r.get("object_id", "").strip() or f"{res_id}-obj-{obj_count}"
            obj_slug = slugify(obj_id)
            obj_uri = RES[f"object/{obj_slug}"]
            m_uri = RES[f"monument/{res_id}"]

            obj_name = r.get("object_name", "").strip() or "Sacred Object"
            obj_type = r.get("object_type", "").strip()

            # Classify object
            obj_class_name = r.get("ontology_class", "").strip() or classify_object(obj_name, obj_type)
            g.add((obj_uri, RDF.type, hg_class(obj_class_name)))
            g.add((obj_uri, RDF.type, CRM["E22_Human-Made_Object"]))
            if obj_class_name in ["Murti", "Paubha"]:
                g.add((obj_uri, RDF.type, HG.IconographicObject))
            elif obj_class_name == "ArchitecturalElement":
                g.add((obj_uri, RDF.type, PROV.Entity))

            g.add((obj_uri, RDFS.label, Literal(obj_name, lang="en")))
            g.add((obj_uri, DCTERMS.identifier, Literal(obj_id)))

            if obj_type:
                g.add((obj_uri, HG.objectType, Literal(obj_type, lang="en")))

            material = r.get("object_material", "").strip()
            if material:
                g.add((obj_uri, HG.material, Literal(material, lang="en")))
                g.add((obj_uri, CRM["P45_consists_of"], Literal(material, lang="en")))

            location = r.get("object_location", "").strip()
            if location:
                g.add((obj_uri, HG.locationWithinMonument, Literal(location, lang="en")))

            date_ce = r.get("date_bce_ce", "").strip()
            if date_ce:
                g.add((obj_uri, HG.dateBCE_CE, Literal(date_ce)))

            date_vs_ns = r.get("date_vs_ns", "").strip()
            if date_vs_ns:
                g.add((obj_uri, HG.inscriptionalDateEra, Literal(date_vs_ns)))

            # Link Object <-> Monument: P46 (composition) only for architectural parts, as the ontology's shapes require;
            # other objects are housed in the monument (extension property).
            if obj_class_name == "ArchitecturalElement":
                g.add((obj_uri, CRM["P46i_forms_part_of"], m_uri))
                g.add((m_uri, CRM["P46_is_composed_of"], obj_uri))
            else:
                g.add((obj_uri, HGN.isObjectOf, m_uri))
                g.add((m_uri, HGN.containsObject, obj_uri))

            # Provenance
            g.add((obj_uri, PROV.wasAttributedTo, agent_antigravity))
            g.add((obj_uri, PROV.wasGeneratedBy, activity_kg))

            obj_count += 1

    print(f"[+] Loaded {obj_count} objects into graph.")

    # ── Summary & Metadata Update ─────────────────────────────────────────────
    triple_count = len(g)
    g.add((dataset_uri, VOID.triples, Literal(triple_count, datatype=XSD.integer)))
    g.add((dataset_uri, VOID.entities, Literal(mon_count + ev_count + obj_count, datatype=XSD.integer)))

    stats = {
        "monuments": mon_count,
        "events": ev_count,
        "objects": obj_count,
        "places": len(places_cache),
        "deities": len(deities_cache),
        "triples": triple_count,
    }
    return g, stats


# ── Serializers & Main Runner ─────────────────────────────────────────────────
def export_kg(
    graph: Graph,
    outdir: str,
    formats: list[str] = ["turtle", "nt"],
) -> dict[str, str]:
    """Serialize the graph to specified formats in outdir."""
    os.makedirs(outdir, exist_ok=True)
    exported_files = {}

    format_mapping = {
        "turtle": ("heritage_graph.ttl", "turtle"),
        "ttl": ("heritage_graph.ttl", "turtle"),
        "nt": ("heritage_graph.nt", "nt"),
        "ntriples": ("heritage_graph.nt", "nt"),
        "jsonld": ("heritage_graph.jsonld", "json-ld"),
        "json-ld": ("heritage_graph.jsonld", "json-ld"),
        "xml": ("heritage_graph.rdf", "xml"),
    }

    for fmt in formats:
        fmt_key = fmt.lower().strip()
        if fmt_key not in format_mapping:
            print(f"[!] Warning: format '{fmt}' not recognized, skipping.")
            continue

        filename, rdflib_fmt = format_mapping[fmt_key]
        dest_path = os.path.join(outdir, filename)
        print(f"[*] Serializing graph to {dest_path} (format: {rdflib_fmt})...")
        graph.serialize(destination=dest_path, format=rdflib_fmt, encoding="utf-8")
        size_bytes = os.path.getsize(dest_path)
        print(f"[+] Wrote {dest_path} ({size_bytes / (1024 * 1024):.2f} MB)")
        exported_files[rdflib_fmt] = dest_path

    return exported_files


def main():
    parser = argparse.ArgumentParser(
        description="Build CAIR-Nepal HeritageGraph RDF & LOD Export",
        epilog="Examples:\n"
               "  python build_kg.py --dir staging --outdir lod_export\n"
               "  python build_kg.py --monuments staging/monuments.csv --events staging/events.csv --objects staging/objects.csv\n"
               "  python build_kg.py --sample 50 --formats turtle,nt,json-ld\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dir", "--staging-dir", dest="input_dir", default=None,
                        help="Convenience parameter: base directory containing monuments.csv, events.csv, and objects.csv")
    parser.add_argument("--monuments", default=None, help="Path to monuments.csv")
    parser.add_argument("--events", default=None, help="Path to events.csv")
    parser.add_argument("--objects", default=None, help="Path to objects.csv")
    parser.add_argument("--outdir", default="lod_export", help="Output directory for RDF/LOD exports (default: 'lod_export')")
    parser.add_argument("--formats", default="turtle,nt", help="Comma-separated RDF formats: turtle, nt, json-ld (default: 'turtle,nt')")
    parser.add_argument("--sample", type=int, default=None, help="Process only first N monuments for testing/debugging")
    parser.add_argument("--release", default=None, help="Publish versioned release layout (e.g. v1.0.0, v1.1.0) and update latest/")
    parser.add_argument("--no-latest", action="store_true", help="When using --release, do not update latest/")
    args = parser.parse_args()

    # Intelligent path resolution
    base_dir = args.input_dir

    def resolve_path(cli_val, filename, default_candidates):
        if cli_val:
            return cli_val
        if base_dir:
            cand = os.path.join(base_dir, filename)
            if os.path.exists(cand):
                return cand
        for candidate in default_candidates:
            if os.path.exists(candidate):
                return candidate
        return default_candidates[0]

    monuments_path = resolve_path(args.monuments, "monuments.csv", [
        "staging/monuments.csv",
        "data_collection/data/exports/monuments.csv"
    ])
    events_path = resolve_path(args.events, "events.csv", [
        "staging/events.csv",
        "data_collection/data/exports/events.csv"
    ])
    objects_path = resolve_path(args.objects, "objects.csv", [
        "staging/objects.csv",
        "data_collection/data/exports/objects.csv"
    ])

    # Validation
    missing = []
    for label, path in [("Monuments CSV", monuments_path), ("Events CSV", events_path), ("Objects CSV", objects_path)]:
        if not os.path.exists(path):
            missing.append(f"  - {label}: '{path}'")

    if missing:
        print("[!] Error: Required input files not found:", file=sys.stderr)
        for m in missing:
            print(m, file=sys.stderr)
        print("    Please verify paths or specify --dir <directory> / --monuments / --events / --objects", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Ingesting datasets:")
    print(f"    - Monuments: {monuments_path}")
    print(f"    - Events:    {events_path}")
    print(f"    - Objects:   {objects_path}")

    start_time = datetime.now()
    graph, stats = build_knowledge_graph(
        monuments_path=monuments_path,
        events_path=events_path,
        objects_path=objects_path,
        limit=args.sample,
    )

    fmt_list = [f.strip() for f in args.formats.split(",") if f.strip()]
    exported = export_kg(graph, args.outdir, fmt_list)

    if args.release:
        try:
            import publish_release
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import publish_release
        publish_release.create_release(
            version=args.release,
            graph=graph,
            update_latest=not args.no_latest,
        )

    elapsed = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print(" CAIR-Nepal HeritageGraph RDF Knowledge Graph Generated")
    print("=" * 60)
    print(f" Monuments Ingested:    {stats['monuments']:,}")
    print(f" Historical Events:     {stats['events']:,}")
    print(f" Sacred Objects:        {stats['objects']:,}")
    print(f" Geographic Places:     {stats['places']:,}")
    print(f" Unique Deities:        {stats['deities']:,}")
    print(f" Total RDF Triples:     {stats['triples']:,}")
    print(f" Elapsed Time:          {elapsed:.2f} seconds")
    print(" Files Created:")
    for fmt_name, path in exported.items():
        print(f"   - [{fmt_name.upper()}] {path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
