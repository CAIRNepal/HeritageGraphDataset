"""Event typing rules: which ontology class(es) an event row gets.

DANAM's event tables have no event class, so every event is typed from its name and description by the keyword rules
below (RULES). Matching is case-insensitive and each keyword matches at the start of a word ('collaps' matches
'collapsed'). The rules are tried in order; the first that matches decides. "name" rules read the event name only;
"text" rules read the name and the description together.

  1. Consecration          text: prāṇapratiṣṭhā, consecrat…
  2. Enshrinement          text: enshrin…, 'install … image', 'installed in … sanctum'
  3. Destruction + Modification
                           name: a DAMAGE word and a REPAIR word ('Collapse and reconstruction'). One row reports two
                           happenings, so the event gets both crm:E6_Destruction and crm:E11_Modification.
  4. Destruction           name: DAMAGE (destr…, dismantl…, collaps…, burn…, demolish…, damage…, devastat…, 'washed away',
                           earthquake, flood, fire, blaze) -> crm:E6_Destruction. A damage word only in the description is
                           background (e.g. 'Rebuilding of the temple … following the 1934 earthquake'), not the event.
  5. Modification + Transfer of custody
                           name: a REPAIR word and a TRANSFER word or donat… ('Renovation and land endowment') -> both
                           crm:E11_Modification and crm:E10_Transfer_of_Custody.
  6. Modification          name: REPAIR (renovat…, restor…, rebuil…, reconstruct…, repair…, refurbish…, renew…, retrofit…)
                           -> crm:E11_Modification
  7. Transfer of custody   name: TRANSFER (endow…, guṭhi, guthi, handed, transfer, custody, allocated, grant…). Comes before
                           rule 8 so that 'Endowment of lands for daily worship' stays a transfer.
  8. Ritual event          name: ritual…, worship…, pūjā, puja
  9. Transfer of custody   text: TRANSFER
 10. Ritual event          text: puja, pūjā, jātrā, jatra, festival, bhajan, procession, purification, omen, blood
 11. Production            text: built, construct…, rebuil…, renovat…, repair…, restor…, erect…, found…,
                           'install … roof/toraṇa/door', 'offer … pinnacle/gilded' -> crm:E12_Production
 12. Condition assessment  text: assess…, survey…, document… -> crm:E14_Condition_Assessment
 13. Historical event      anything else

Rules 1, 2 and 9-13 are the builder's earlier rules, unchanged: a repair word only in the description still gives
production (rule 11), as before. Rules 3-8 are fix F2 (docs/sync/SYNC_LOG.md); they replace the earlier destruction rule,
which read the description too and typed renovations as destruction.

Known limitation (listed, not changed): 'grant' also matches 'granthakūṭa' (a temple style), which makes
'Installing door to build new temple' a transfer of custody.
"""
import re

DAMAGE = (r"destr|dismantl|collaps|burnt|burn|demolish|damage|devastat|washed away|earthquake|flood|fire|blaze")
REPAIR = r"renovat|restor|rebuil|reconstruct|repair|refurbish|renew|retrofit"
TRANSFER = r"endow|guṭhi|guthi|handed|transfer|custody|allocated|grant"

RULES = [  # (class name(s), regex, what is searched: "name" or "text" = name + description)
    (("Consecration",), r"prāṇapratiṣṭhā|pranapratistha|consecrat", "text"),
    (("Enshrinement",), r"enshrin|install.*image|installed in.*sanctum", "text"),
    (("DestructionEvent", "Modification"), None, "name"),  # rule 3: both DAMAGE and REPAIR in the name
    (("DestructionEvent",), DAMAGE, "name"),
    (("Modification", "TransferOfCustody"), None, "name"),  # rule 6: both REPAIR and TRANSFER (or donat…) in the name
    (("Modification",), REPAIR, "name"),
    (("TransferOfCustody",), TRANSFER, "name"),  # keeps 'Endowment of lands for daily worship' a transfer
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
    """(class names, number of the rule that matched, 1-13)."""
    n, t = name.lower(), f"{name} {desc}".lower()
    for i, (classes, pattern, where) in enumerate(RULES, 1):
        if pattern is None:
            second = DAMAGE if classes[0] == "DestructionEvent" else TRANSFER + "|donat"
            if _has(second, n) and _has(REPAIR, n):
                return classes, i
        elif _has(pattern, n if where == "name" else t):
            return classes, i
    return ("HistoricalEvent",), len(RULES) + 1


def classify_event(name: str, desc: str) -> tuple[str, ...]:
    """Ontology class name(s) of an event (see the module docstring)."""
    return classify_event_rule(name, desc)[0]
