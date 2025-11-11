"""ClinicalTrials.gov ingestion (MVP)
- Uses Study Fields API for a focused slice.
- Stores normalized JSONL with key metadata and a displayable source URL.
"""
import os
from typing import List, Dict, Any
from urllib.parse import urlencode
from src.common.utils import S, save_records, dump_json, RAW_DIR

CTG_MAX = int(os.getenv("CTG_MAX_STUDIES", 200))

FIELDS = [
    "NCTId", "Condition", "BriefTitle", "OverallStatus", "Phase",
    "LeadSponsorName", "StartDate", "CompletionDate", "LastUpdatePostDate",
]

BASE = "https://clinicaltrials.gov/api/query/study_fields"


def fetch_trials(expr: str = "cancer", max_studies: int = CTG_MAX) -> List[Dict[str, Any]]:
    params = {
        "expr": expr,
        "fields": ",".join(FIELDS),
        "min_rnk": 1,
        "max_rnk": max_studies,
        "fmt": "json",
    }
    url = f"{BASE}?{urlencode(params)}"
    res = S.get(url, timeout=60)
    res.raise_for_status()
    data = res.json()
    studies = data["StudyFieldsResponse"]["StudyFields"]
    # Raw dump for reference
    dump_json(os.path.join(RAW_DIR, "clinicaltrials_raw.json"), data)
    norm: List[Dict[str, Any]] = []
    for s in studies:
        norm.append({
            "source": "clinicaltrials.gov",
            "nct_id": s.get("NCTId", [None])[0],
            "title": s.get("BriefTitle", [""])[0],
            "condition": s.get("Condition", []),
            "phase": s.get("Phase", [""])[0],
            "status": s.get("OverallStatus", [""])[0],
            "sponsor": s.get("LeadSponsorName", [""])[0],
            "start_date": s.get("StartDate", [""])[0],
            "completion_date": s.get("CompletionDate", [""])[0],
            "last_update": s.get("LastUpdatePostDate", [""])[0],
            "url": f"https://clinicaltrials.gov/study/{s.get('NCTId', [''])[0]}",
        })
    return norm


def run(expr: str = "multiple sclerosis") -> str:
    records = fetch_trials(expr=expr)
    return save_records("clinicaltrials", records)

if __name__ == "__main__":
    print(run())
