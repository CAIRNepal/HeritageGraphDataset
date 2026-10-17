"""Date helpers for DANAM / Nepali heritage text.

Finds era dates (NS, VS, ŚS, MS) and CE/BCE years in free text, pairs them,
parses month / paksha / tithi, converts eras to CE, and flags disagreements
between the CE year written in the source and the CE year implied by the era.
Nothing here invents data: conversions are returned as *derived* values.
"""
import os
import re
import sys
import unicodedata

# Reconfigure Windows console to handle UTF-8 / IAST diacritics
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


MONTHS = {
    "caitra": "Caitra", "chaitra": "Caitra",
    "vaisakha": "Vaiśākha", "baisakh": "Vaiśākha", "baisakha": "Vaiśākha",
    "jyestha": "Jyeṣṭha", "jestha": "Jyeṣṭha",
    "asadha": "Āṣāḍha", "asar": "Āṣāḍha", "ashad": "Āṣāḍha",
    "sravana": "Śrāvaṇa", "shrawan": "Śrāvaṇa",
    "bhadra": "Bhādra", "bhadau": "Bhādra",
    "asvina": "Āśvina", "aswin": "Āśvina", "ashwin": "Āśvina",
    "kartika": "Kārtika", "kartik": "Kārtika",
    "margasirsa": "Mārgaśīrṣa", "mangsir": "Mārgaśīrṣa",
    "pausa": "Pauṣa", "paush": "Pauṣa", "pus": "Pauṣa",
    "magha": "Māgha", "magh": "Māgha",
    "phalguna": "Phālguna", "falgun": "Phālguna", "phalgun": "Phālguna",
}
MONTH_ALT = "|".join(sorted(MONTHS, key=len, reverse=True))

NS_LATE = {"Kārtika", "Mārgaśīrṣa", "Pauṣa"}       # NS year already rolled over, CE = NS+879
VS_EARLY = {"Māgha", "Phālguna", "Caitra"}          # Jan-Apr, CE = VS-56 (else VS-57)

ERA_RE = re.compile(r"(?<![A-Za-z])(NS|VS|BS|ŚS|SS|MS|Mānadeva Era)\s*(\d{1,4})\b")
CE_RE = re.compile(r"(?<![\d-])(\d{1,4})\s*(CE|BCE|AD|BC)\b")
KALI_RE = re.compile(r"Kaligata Era\s*(\d+)", re.I)
TITHI_RE = re.compile(
    r"(\d{1,2})(?:st|nd|rd|th)\s+of\s+the\s+(bright|dark)\s+fortnight(?:\s+of\s+(\w+))?", re.I)
MONTH_RE = re.compile(r"\b(" + MONTH_ALT + r")\b", re.I)


def canon_month(word):
    return MONTHS.get(fold(word)) if word else None


def era_to_ce(era, year, month=None):
    """Return (ce_year, approximate_flag)."""
    era = {"BS": "VS", "SS": "ŚS", "Mānadeva Era": "MS"}.get(era, era)
    if era == "NS":
        return year + (879 if month in NS_LATE else 880), month is None
    if era == "VS":
        return year - (56 if month in VS_EARLY else 57), month is None
    if era == "ŚS":
        return year + 78, month is None
    if era == "MS":   # Mānadeva era
        return year + 576, True
    return None, True


def period_for(ce):
    if ce is None:
        return ""
    if ce < 879:
        return "Licchavi" if ce >= 300 else "Pre-Licchavi"
    if ce < 1200: return "Early medieval (Transitional)"
    if ce < 1769: return "Malla"
    if ce < 1846: return "Śāha"
    if ce < 1951: return "Rāṇā"
    return "Post-Rāṇā / Modern"


def _signed(m):
    bce = m.group(2).upper() in ("BCE", "BC")
    return -int(m.group(1)) if bce else int(m.group(1))


def find_dates(text):
    """Return a list of date mentions found in `text` (document order)."""
    ces = [(m.start(), m.end(), _signed(m), m.group(0)) for m in CE_RE.finditer(text)]
    eras = [(m.start(), m.end(), m.group(1), int(m.group(2)), m.group(0)) for m in ERA_RE.finditer(text)]
    used_ce, out = set(), []
    for s, e, era, yr, raw in eras:
        pair = None
        for i, (cs, ce_, cyear, craw) in enumerate(ces):
            if i in used_ce:
                continue
            gap = cs - e if cs >= e else (s - ce_ if ce_ <= s else 999)
            if gap <= 14:
                pair = i
                break
        out.append(_mention(text, s, e, era, yr, raw, ces[pair] if pair is not None else None))
        if pair is not None:
            used_ce.add(pair)
    for i, (cs, ce_, cyear, craw) in enumerate(ces):
        if i not in used_ce:
            out.append(_mention(text, cs, ce_, None, None, craw, (cs, ce_, cyear, craw)))
    for m in KALI_RE.finditer(text):
        out.append({"raw": m.group(0), "start": m.start(), "ce": None, "era": f"Kaligata {m.group(1)}",
                    "month": None, "paksha": None, "tithi": None, "ce_derived": False,
                    "flags": ["traditional_chronology_not_converted"]})
    return sorted(out, key=lambda d: d["start"])


def _mention(text, s, e, era, yr, raw, cepair):
    pre = text[max(0, s - 110):s]
    month = paksha = tithi = None
    last = None
    for m in TITHI_RE.finditer(pre):
        if len(pre) - m.end() <= 24:
            last = m
    if last:
        tithi = int(last.group(1))
        paksha = "Śukla" if last.group(2).lower() == "bright" else "Kṛṣṇa"
        month = canon_month(last.group(3))
    if not month:
        for m in MONTH_RE.finditer(pre):
            if len(pre) - m.end() <= 24:
                month = canon_month(m.group(1))
    era = {"BS": "VS", "SS": "ŚS", "Mānadeva Era": "MS"}.get(era, era)
    flags, start, end = [], s, e
    ce_text = None
    if cepair:
        start, end = min(s, cepair[0]), max(e, cepair[1])
        ce_text = cepair[2]
    ce, ce_derived = ce_text, False
    if era:
        derived, approx = era_to_ce(era, yr, month)
        if ce_text is None:
            ce, ce_derived = derived, True
            if approx:
                flags.append("ce_year_may_be_off_by_one")
        elif derived is not None and abs(derived - ce_text) > 1:
            flags.append(f"era_ce_mismatch(text_ce={ce_text}, era_implies={derived})")
    if text[end:end + 1] == ")" and text[start:end].count("(") > text[start:end].count(")"):
        end += 1
    return {"raw": text[start:end], "start": start, "ce": ce, "era": f"{era} {yr}" if era else None,
            "month": month, "paksha": paksha, "tithi": tithi, "ce_derived": ce_derived, "flags": flags}


def fmt_ce(ce):
    if ce is None:
        return ""
    return f"{abs(ce)} BCE" if ce < 0 else f"{ce} CE"


def run_selftest() -> bool:
    """Run built-in test suite for date parsing and conversions."""
    test_cases = [
        (
            "On the 13th of the bright fortnight of Phālguna in 1689 CE (NS 809)",
            0,
            {"era": "NS 809", "ce": 1689, "month": "Phālguna", "paksha": "Śukla", "tithi": 13},
        ),
        (
            "An inscription dated ŚS 1422 (i.e., 500 CE)",
            0,
            {"era": "ŚS 1422", "ce": 500},
        ),
        (
            "Founded in 1300 BC (Kaligata Era 1801)",
            1,
            {"era": "Kaligata 1801", "ce": None},
        ),
    ]
    all_passed = True
    print("[*] Running heritage_dates self-test...")
    for idx, (sample_text, match_idx, expected) in enumerate(test_cases, 1):
        found = find_dates(sample_text)
        if not found or len(found) <= match_idx:
            print(f"[-] Case {idx} FAILED: mention index {match_idx} not found in '{sample_text}'")
            all_passed = False
            continue
        target = found[match_idx]
        passed = True
        for key, val in expected.items():
            if target.get(key) != val:
                print(f"[-] Case {idx} MISMATCH on '{key}': expected {val}, got {target.get(key)}")
                passed = False
        if passed:
            print(f"[+] Case {idx} PASSED: {target['era'] or ''} -> {target['ce']} (raw: '{target['raw']}')")
        else:
            all_passed = False
    return all_passed


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="DANAM & Nepali Heritage Date / Era Parsing Utility",
        epilog="Examples:\n"
               "  python heritage_dates.py \"Renovated in 1689 CE (NS 809)\"\n"
               "  python heritage_dates.py --test\n"
               "  python heritage_dates.py --file description.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("text", nargs="?", default=None, help="Text string to extract dates from")
    parser.add_argument("--file", "-f", help="Read text from file instead of command line argument")
    parser.add_argument("--test", action="store_true", help="Run internal validation test suite")
    parser.add_argument("--compact", action="store_true", help="Output compact JSON instead of formatted")

    args = parser.parse_args()

    if args.test:
        success = run_selftest()
        sys.exit(0 if success else 1)

    input_text = None
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        with open(args.file, encoding="utf-8") as f:
            input_text = f.read()
    elif args.text:
        input_text = args.text
    else:
        parser.print_help()
        sys.exit(0)

    results = find_dates(input_text)
    indent = None if args.compact else 2
    print(json.dumps(results, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    import os
    import sys
    main()
