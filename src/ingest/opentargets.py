"""OpenTargets ingestion (MVP)
- Queries associations for a disease to pull targets and basic info.
- For a production build, prefer GraphQL w/ pagination; here we keep it simple.
"""
import os
from typing import List, Dict, Any
from urllib.parse import urlencode
from src.common.utils import S, save_records, dump_json, RAW_DIR

OT_MAX = int(os.getenv("OPENTARGETS_MAX", 200))

BASE = "https://api.opentargets.io/v3/platform/public/association/filter"

# Example disease: EFO_0000685 (multiple sclerosis). You can pass another efo_id in run().

def fetch_associations(efo_id: str = "EFO_0000685", size: int = OT_MAX) -> List[Dict[str, Any]]:
    params = {
        "disease": efo_id,
        "size": size,
    }
    url = f"{BASE}?{urlencode(params)}"
    r = S.get(url, timeout=60)
    r.raise_for_status()
    data = r.json()
    dump_json(os.path.join(RAW_DIR, "opentargets_raw.json"), data)

    norm: List[Dict[str, Any]] = []
    for hit in data.get("data", []):
        target = hit.get("target", {})
        disease = hit.get("disease", {})
        evidences = hit.get("evidence_count", {})
        norm.append({
            "source": "opentargets",
            "target_id": target.get("id"),
            "target_symbol": target.get("symbol"),
            "target_name": target.get("approved_symbol") or target.get("symbol"),
            "disease_id": disease.get("id"),
            "disease_name": disease.get("name"),
            "evidence_count": evidences,
            "url": f"https://platform.opentargets.org/target/{target.get('id')}",
        })
    return norm


def run(efo_id: str = "EFO_0000685") -> str:
    records = fetch_associations(efo_id=efo_id)
    return save_records("opentargets", records)

if __name__ == "__main__":
    print(run())
