import os
import time
import json
from typing import Any, Dict
import requests
from requests.adapters import HTTPAdapter, Retry

RAW_DIR = os.getenv("RAW_DIR", "./data/raw")
CLEAN_DIR = os.getenv("CLEAN_DIR", "./data/clean")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)


def session_with_retries(total=5, backoff=0.5):
    s = requests.Session()
    retries = Retry(total=total, backoff_factor=backoff, status_forcelist=[429, 500, 502, 503, 504])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.mount('https://', HTTPAdapter(max_retries=retries))
    return s


S = session_with_retries()


def dump_json(path: str, obj: Any):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_json(path: str) -> Any:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_records(name: str, records: list[Dict[str, Any]]):
    p = os.path.join(CLEAN_DIR, f"{name}.jsonl")
    with open(p, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return p


def rate_limit_sleep(seconds: float):
    time.sleep(seconds)
