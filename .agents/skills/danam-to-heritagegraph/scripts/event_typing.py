"""Event typing rules: which ontology class(es) an event row gets.

DANAM's event tables have no event class, so every event is typed from its name and description by the keyword rules
below (RULES). Matching is case-insensitive and each keyword matches at the start of a word ('collaps' matches
'collapsed'). The rules are tried in order; the first that matches decides. "name" rules read the event name only;
"text" rules read the name and the description together. A rule with two patterns needs both in the name; the event
then gets both classes (one row reports two happenings, e.g. 'Collapse and reconstruction').

Keyword groups:
  DONATION         donation…, donated, 'offering of'
  GUTHI_FORMATION  formation…, establish…, founded, formed … followed later by guṭhī / guṭhi / guthi
  REPAIR           renovat…, restor…, rebuil…, reconstruct…, repair…, refurbish…, renew…, retrofit…
  DAMAGE           destr…, dismantl…, collaps…, burn…, demolish…, damage…, devastat…, 'washed away', earthquake, flood,
                   fire, blaze
  TRANSFER         endow…, guṭhi, guthi, handed, transfer, custody, allocated, grant… (not granth…: granthakūṭa is a
                   temple style). Donations are not transfers of custody (they are acquisitions, crm:E8).
  CONSTRUCTION     built, build…, construct…, erect…

  1. Modification + Acquisition   name: REPAIR and DONATION ('Renovation and donation') -> crm:E11 + crm:E8
  2. Acquisition                  name: DONATION ('Donation of a bell', 'Offering of a patāḥ') -> crm:E8_Acquisition.
                                  Comes before consecration and enshrinement, which also read the description.
  3. Consecration                 text: prāṇapratiṣṭhā, consecrat…
  4. Enshrinement                 text: enshrin…, 'install … image', 'installed in … sanctum'
  5. Destruction + Modification   name: DAMAGE and REPAIR ('Collapse and reconstruction') -> crm:E6 + crm:E11
  6. Destruction                  name: DAMAGE -> crm:E6_Destruction. A damage word only in the description is
                                  background ('Rebuilding of the temple … following the 1934 earthquake'), not the event.
  7. Modification + Formation     name: REPAIR and GUTHI_FORMATION ('Minor renovation and formation of a guṭhī')
                                  -> crm:E11 + crm:E66
  8. Modification + Transfer      name: REPAIR and TRANSFER ('Renovation and land endowment') -> crm:E11 + crm:E10
  9. Modification                 name: REPAIR -> crm:E11_Modification
 10. Production + Formation       name: CONSTRUCTION and GUTHI_FORMATION ('Initial Construction of the Temple and
                                  Establishment of a Guṭhī') -> crm:E12 + crm:E66
 11. Formation                    name: GUTHI_FORMATION ('Formation of a guṭhī') -> crm:E66_Formation
 12. Transfer of custody          name: TRANSFER. Comes before rule 13 so that 'Endowment of lands for daily worship'
                                  stays a transfer.
 13. Ritual event                 name: ritual…, worship…, pūjā, puja
 14. Transfer of custody          text: TRANSFER
 15. Ritual event                 text: puja, pūjā, jātrā, jatra, festival, bhajan, procession, purification, omen, blood
 16. Production                   text: built, construct…, rebuil…, renovat…, repair…, restor…, erect…, found…,
                                  'install … roof/toraṇa/door', 'offer … pinnacle/gilded' -> crm:E12_Production
 17. Condition assessment         text: assess…, survey…, document… -> crm:E14_Condition_Assessment
 18. Historical event             anything else

Rules 3, 4 and 14-18 are the builder's earlier rules, unchanged: a repair word only in the description still gives
production (rule 16), as before. The other rules come from fix round 1 (F2, F9, F10 in docs/sync/SYNC_LOG.md); they
replace the earlier destruction rule, which read the description too and typed renovations as destruction.
"""
import re

DONATION = r"donation|donated|offering of"
GUTHI_FORMATION = r"(formation|establish|founded|formed)\w*\b.*\bgu(ṭ|ṭ?)h(i|ī|ī)"  # composed or decomposed ṭ / ī
REPAIR = r"renovat|restor|rebuil|reconstruct|repair|refurbish|renew|retrofit"
DAMAGE = r"destr|dismantl|collaps|burnt|burn|demolish|damage|devastat|washed away|earthquake|flood|fire|blaze"
TRANSFER = r"endow|guṭhi|guthi|handed|transfer|custody|allocated|grant(?!h)"
CONSTRUCTION = r"built|build|construct|erect"

RULES = [  # (class name(s), pattern or (pattern, pattern) = both, what is searched: "name" or "text" = name + description)
    (("Modification", "Acquisition"), (REPAIR, DONATION), "name"),
    (("Acquisition",), DONATION, "name"),
    (("Consecration",), r"prāṇapratiṣṭhā|pranapratistha|consecrat", "text"),
    (("Enshrinement",), r"enshrin|install.*image|installed in.*sanctum", "text"),
    (("DestructionEvent", "Modification"), (DAMAGE, REPAIR), "name"),
    (("DestructionEvent",), DAMAGE, "name"),
    (("Modification", "Formation"), (REPAIR, GUTHI_FORMATION), "name"),
    (("Modification", "TransferOfCustody"), (REPAIR, TRANSFER), "name"),
    (("Modification",), REPAIR, "name"),
    (("Production", "Formation"), (CONSTRUCTION, GUTHI_FORMATION), "name"),
    (("Formation",), GUTHI_FORMATION, "name"),
    (("TransferOfCustody",), TRANSFER, "name"),
    (("RitualEvent",), r"ritual|worship|pūjā|puja", "name"),
    (("TransferOfCustody",), TRANSFER, "text"),
    (("RitualEvent",), r"puja|pūjā|jātrā|jatra|festival|bhajan|procession|purification|omen|blood", "text"),
    (("Production",), r"built|construct|rebuil|renovat|install.*roof|install.*toraṇa|install.*door|repair|erect|found|"
                      r"offer.*pinnacle|offer.*gilded|restor", "text"),
    (("ConditionAssessment",), r"assess|survey|document", "text"),
]


def _has(pattern: str, text: str) -> bool:
    return re.search(rf"\b({pattern})", text) is not None


def classify_event_rule(name: str, desc: str) -> tuple[tuple[str, ...], int]:
    """(class names, number of the rule that matched, 1-18)."""
    n, t = name.lower(), f"{name} {desc}".lower()
    for i, (classes, pattern, where) in enumerate(RULES, 1):
        text = n if where == "name" else t
        patterns = pattern if isinstance(pattern, tuple) else (pattern,)
        if all(_has(p, text) for p in patterns):
            return classes, i
    return ("HistoricalEvent",), len(RULES) + 1


def classify_event(name: str, desc: str) -> tuple[str, ...]:
    """Ontology class name(s) of an event (see the module docstring)."""
    return classify_event_rule(name, desc)[0]
