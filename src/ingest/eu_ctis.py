"""EU CTIS ingestion (stub for MVP)
CTIS provides a public search portal. Official programmatic API access is limited.
For MVP we provide a placeholder that lets you manually append curated records
(or implement HTML scraping responsibly later).
"""
from src.common.utils import save_records

SAMPLE = [
    {
        "source": "eu_ctis",
        "ctis_id": "CT-EXAMPLE-0001",
        "title": "Example EU CTIS oncology trial",
        "condition": ["Oncology"],
        "phase": "Phase II",
        "status": "Ongoing",
        "sponsor": "Example Sponsor",
        "start_date": "2024-05-10",
        "completion_date": "",
        "last_update": "2025-08-15",
        "url": "https://euclinicaltrials.eu/ctis-public-web/",
    }
]

def run() -> str:
    return save_records("eu_ctis", SAMPLE)

if __name__ == "__main__":
    print(run())
