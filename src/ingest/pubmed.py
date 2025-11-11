"""PubMed ingestion (MVP)
- E-utilities: esearch -> efetch for abstracts (XML -> text).
- Stores minimal fields for RAG context + citation.
"""
import os
from typing import List, Dict, Any
from xml.etree import ElementTree as ET
from src.common.utils import S, save_records, dump_json, RAW_DIR, rate_limit_sleep

PM_MAX = int(os.getenv("PUBMED_MAX_PMIDS", 200))

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def esearch(query: str, retmax: int = PM_MAX) -> List[str]:
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": retmax}
    r = S.get(ESEARCH, params=params, timeout=60)
    r.raise_for_status()
    return r.json()["esearchresult"].get("idlist", [])


def efetch(pmids: List[str]) -> List[Dict[str, Any]]:
    if not pmids:
        return []
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
    r = S.get(EFETCH, params=params, timeout=120)
    r.raise_for_status()
    xml = ET.fromstring(r.text)
    out: List[Dict[str, Any]] = []
    for art in xml.findall('.//PubmedArticle'):
        title = art.findtext('.//ArticleTitle') or ''
        abstract = ' '.join([a.text or '' for a in art.findall('.//Abstract/AbstractText')]).strip()
        journal = art.findtext('.//Journal/Title') or ''
        year = art.findtext('.//PubDate/Year') or ''
        pmid = art.findtext('.//PMID') or ''
        out.append({
            "source": "pubmed",
            "pmid": pmid,
            "title": title,
            "text": abstract or title,
            "date": year,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "journal": journal,
        })
    return out


def run(query: str = "multiple sclerosis BTK inhibitor") -> str:
    ids = esearch(query)
    rate_limit_sleep(0.4)
    records = efetch(ids)
    dump_json(os.path.join(RAW_DIR, "pubmed_ids.json"), {"pmids": ids})
    return save_records("pubmed", records)

if __name__ == "__main__":
    print(run())
