from src.ingest.clinicaltrials import run as ctg_run  # needs update to new CTIS source
from src.ingest.opentargets import run as ot_run
from src.ingest.pubmed import run as pm_run
from src.ingest.eu_ctis import run as eu_run
from src.index.build_index import build


if __name__ == "__main__":
    print("[1/5] ClinicalTrials.gov...")
    print("Skipping ClinicalTrials.gov ingestion step. Needs Update to new CTIS source.")
    #ctg_run("multiple sclerosis")         # needs update to new CTIS source
    print("[2/5] OpenTargets...")
    ot_run("EFO_0000685") # MS
    print("[3/5] PubMed...")
    pm_run("multiple sclerosis BTK inhibitor")
    print("[4/5] EU CTIS (stub)...")
    eu_run()
    print("[5/5] Build FAISS index...")
    build()
    print("Done.")