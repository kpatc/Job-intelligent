#!/usr/bin/env python3
import requests
import logging
import pandas as pd
import os

logging.basicConfig(filename="remoteok_full_ingest.log", level=logging.INFO)

API_URL = "https://remoteok.com/api"

def run():
    r = requests.get(API_URL, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    data = r.json()

    jobs = []
    for item in data:
        if not isinstance(item, dict):
            continue
        jobs.append({
            "title": item.get("position"),
            "company": item.get("company"),
            "location": item.get("location"),
            "url": item.get("url"),
            "description": item.get("description"),
            "skills": ", ".join(item.get("tags", [])),
        })

    df = pd.DataFrame(jobs)
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    # Sauvegarder dans le dossier data
    df.to_csv("data/remoteok_jobs.csv", index=False)
    logging.info(f"RemoteOK ingestion finished! {len(df)} jobs saved to data/remoteok_jobs.csv")

if __name__ == "__main__":
    run()
