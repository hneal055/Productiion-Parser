"""
ScreenFlow AURA — Sample screenplay API tester.

Reads .fountain, .fdx, and .txt production draft files and runs them
through all three AURA endpoints: /api/parse, /api/analyze, /api/validate.

Usage:
    python test_api.py

    # Override defaults:
    AURA_API_KEY=your-key AURA_URL=http://localhost:8083 python test_api.py

Requires: pip install requests
"""

import json
import os
import sys
import xml.etree.ElementTree as ET

try:
    import requests
except ImportError:
    print("requests not installed. Run: pip install requests")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

BASE_URL = os.environ.get("AURA_URL", "http://localhost:8083")
API_KEY  = os.environ.get("AURA_API_KEY", "")

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SAMPLES = {
    "fountain": os.path.join(SCRIPT_DIR, "the_golden_hour.fountain"),
    "fdx":      os.path.join(SCRIPT_DIR, "the_golden_hour.fdx"),
    "txt":      os.path.join(SCRIPT_DIR, "the_golden_hour_production_draft.txt"),
}

# ── File readers ──────────────────────────────────────────────────────────────

def read_fountain(path: str) -> str:
    """Fountain is plain UTF-8 text — read directly."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_fdx(path: str) -> str:
    """
    Extract screenplay text from Final Draft XML (.fdx).
    Reconstructs the script as plain text suitable for analysis.
    """
    tree = ET.parse(path)
    root = tree.getroot()

    lines = []
    for para in root.iter("Paragraph"):
        ptype = para.get("Type", "")
        text  = "".join(t.text or "" for t in para.iter("Text")).strip()
        if not text:
            continue

        if ptype == "Scene Heading":
            lines.append(f"\n{text}\n")
        elif ptype == "Action":
            lines.append(f"{text}\n")
        elif ptype == "Character":
            lines.append(f"\n                    {text}")
        elif ptype == "Parenthetical":
            lines.append(f"                  {text}")
        elif ptype == "Dialogue":
            lines.append(f"          {text}\n")
        elif ptype == "Transition":
            lines.append(f"\n                                        {text}\n")
        else:
            lines.append(text)

    return "\n".join(lines)


def read_txt(path: str) -> str:
    """Production draft .txt — read directly."""
    with open(path, encoding="utf-8") as f:
        return f.read()


READERS = {
    "fountain": read_fountain,
    "fdx":      read_fdx,
    "txt":      read_txt,
}

# ── API helpers ───────────────────────────────────────────────────────────────

def check_health() -> bool:
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        data = r.json()
        print(f"  Health: {data.get('status')} | analyses so far: {data.get('total_analyses', 0)}")
        return r.status_code == 200
    except Exception as e:
        print(f"  Health check failed: {e}")
        return False


def run_endpoint(endpoint: str, payload: dict, label: str) -> dict | None:
    url = f"{BASE_URL}{endpoint}"
    try:
        r = requests.post(url, headers=HEADERS, json=payload, timeout=120)
    except Exception as e:
        print(f"    Request error: {e}")
        return None

    if r.status_code == 200:
        return r.json()
    else:
        print(f"    HTTP {r.status_code}: {r.text[:200]}")
        return None


def summarise_parse(data: dict) -> None:
    a = data.get("analysis", {})
    dm = a.get("document_metrics", {})
    qa = a.get("quality_assessment", {})
    ai = a.get("ai_insights", {})
    print(f"    Words: {dm.get('word_count')} | Pages: {dm.get('estimated_pages')}"
          f" | Genre: {dm.get('primary_genre')}")
    print(f"    Quality score: {qa.get('overall_score')} | Commercial: {qa.get('commercial_potential')}")
    themes = ai.get("theme_detection", [])
    print(f"    Themes: {', '.join(themes) if themes else 'n/a'}")
    recs = a.get("recommendations", [])
    for rec in recs[:3]:
        print(f"      • {rec}")


def summarise_analyze(data: dict) -> None:
    a = data.get("analysis", {})
    ins = a.get("insights", {})
    ca  = ins.get("character_analysis", {})
    cv  = ins.get("commercial_viability", {})
    ra  = a.get("risk_assessment", {})
    print(f"    Characters: {ca.get('main_characters')} | Depth: {ca.get('character_depth')}")
    print(f"    Market potential: {cv.get('market_potential')} | Audience: {cv.get('target_audience')}")
    print(f"    Risk: {ra.get('overall_risk')} | Market fit: {ra.get('market_fit')}")
    comps = cv.get("comparable_titles", [])
    if comps:
        print(f"    Comparable titles: {', '.join(comps)}")


def summarise_validate(data: dict) -> None:
    v = data.get("validation", {})
    cr = v.get("compliance_report", {})
    standards = cr.get("industry_standards", {})
    print(f"    Hollywood format: {standards.get('hollywood_format')}"
          f" | Fountain compat: {standards.get('fountain_compatibility')}")
    print(f"    Overall score: {v.get('overall_score')} | Status: {v.get('certification_status')}")
    issues = v.get("issues", [])
    for issue in issues[:3]:
        print(f"      [{issue.get('severity','?').upper()}] {issue.get('description')}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not API_KEY:
        print("ERROR: AURA_API_KEY not set.")
        print("  Run:  AURA_API_KEY=your-key python test_api.py")
        sys.exit(1)

    print("=" * 70)
    print("  ScreenFlow AURA — Sample Screenplay Evaluation")
    print(f"  Server: {BASE_URL}")
    print("=" * 70)

    print("\n[1/4] Health check")
    if not check_health():
        print("Server not reachable. Is it running?")
        sys.exit(1)

    results_dir = os.path.join(SCRIPT_DIR, "results")
    os.makedirs(results_dir, exist_ok=True)

    for fmt, path in SAMPLES.items():
        if not os.path.exists(path):
            print(f"\nSkipping {fmt} — file not found: {path}")
            continue

        print(f"\n{'─' * 70}")
        print(f"  File format : {fmt.upper()}")
        print(f"  Source      : {os.path.basename(path)}")
        print(f"{'─' * 70}")

        text = READERS[fmt](path)
        word_count = len(text.split())
        print(f"  Extracted   : {word_count} words\n")

        # ── Parse ──────────────────────────────────────────────────────────
        print("  [parse] Full screenplay analysis...")
        parse_data = run_endpoint("/api/parse", {"screenplay": text}, fmt)
        if parse_data:
            summarise_parse(parse_data)
            with open(os.path.join(results_dir, f"{fmt}_parse.json"), "w") as f:
                json.dump(parse_data, f, indent=2)

        # ── Analyze ────────────────────────────────────────────────────────
        print("\n  [analyze] Deep narrative analysis...")
        analyze_data = run_endpoint(
            "/api/analyze",
            {"screenplay": text, "analysis_type": "comprehensive"},
            fmt,
        )
        if analyze_data:
            summarise_analyze(analyze_data)
            with open(os.path.join(results_dir, f"{fmt}_analyze.json"), "w") as f:
                json.dump(analyze_data, f, indent=2)

        # ── Validate ───────────────────────────────────────────────────────
        print("\n  [validate] Format compliance check...")
        validate_data = run_endpoint("/api/validate", {"screenplay": text}, fmt)
        if validate_data:
            summarise_validate(validate_data)
            with open(os.path.join(results_dir, f"{fmt}_validate.json"), "w") as f:
                json.dump(validate_data, f, indent=2)

    # ── Batch test ─────────────────────────────────────────────────────────
    print(f"\n{'─' * 70}")
    print("  Batch parse — all three formats as one request")
    print(f"{'─' * 70}")

    batch_items = []
    for fmt, path in SAMPLES.items():
        if os.path.exists(path):
            text = READERS[fmt](path)
            batch_items.append({"filename": os.path.basename(path), "content": text})

    if len(batch_items) >= 2:
        batch_data = run_endpoint("/api/batch/parse", {"screenplays": batch_items}, "batch")
        if batch_data:
            b = batch_data.get("batch", {})
            print(f"  Items processed: {b.get('total_items')} | Successful: {b.get('successful')}"
                  f" | Failed: {b.get('failed')}")
            results = batch_data.get("results", [])
            for item in results:
                qv = item.get("quick_verdict", {})
                print(f"    {item.get('item_id')}: score={qv.get('overall_score')}"
                      f" | {qv.get('commercial_potential')} | {qv.get('recommendation','')[:60]}")
            with open(os.path.join(results_dir, "batch_parse.json"), "w") as f:
                json.dump(batch_data, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  Results saved to: {results_dir}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
