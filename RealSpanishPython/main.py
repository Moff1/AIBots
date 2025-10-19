from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from typing import List

app = FastAPI()

NOTION_TOKEN = os.environ["ntn_X3620961771at2knhAAXOx8kGlOiIQ9GKV0P9x69MT90xm"]
DATABASE_ID = os.environ["28e0d7d37deb8063813ac7a5b0adf02a"]

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

class Phrase(BaseModel):
    phrase: str
    meaning: str
    region: str

@app.post("/add-phrase")
def add_phrase(item: Phrase):
    notion_payload = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "Phrase": { "title": [{ "text": { "content": item.phrase } }] },
            "Meaning": { "rich_text": [{ "text": { "content": item.meaning } }] },
            "Region": { "select": { "name": item.region } }
        }
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=notion_payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return { "status": "Phrase added", "data": item }

@app.get("/phrases", response_model=List[Phrase])
def get_phrases():
    response = requests.post(
        f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
        headers=HEADERS
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    pages = response.json().get("results", [])
    results = []

    for page in pages:
        try:
            phrase = page["properties"]["Spanish Phrase"]["title"][0]["text"]["content"]
            meaning = page["properties"]["Slang Phrase"]["rich_text"][0]["text"]["content"]
            region = page["properties"]["Accent"]["select"]["name"]
            results.append(Phrase(phrase=phrase, meaning=meaning, region=region))
        except Exception as e:
            continue

    return results
