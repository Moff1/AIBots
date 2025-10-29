from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from typing import List

app = FastAPI()

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

class Phrase(BaseModel):
    normalphrase: str
    slangphrase: str
    accent: str

@app.post("/add-phrase")
def add_phrase(item: Phrase):
    notion_payload = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "normalphrase": { "title": [{ "text": { "content": item.normalphrase } }] },
            "slangphrase": { "rich_text": [{ "text": { "content": item.slangphrase } }] },
            "accent": { "select": { "name": item.accent} }
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
            title_list = page["properties"]["mormalphrase"]["title"]
            meaning_list = page["properties"]["slangphrase"]["rich_text"]
            region_obj = page["properties"]["accent"]["select"]

            normalphrase = title_list[0]["text"]["content"] if title_list else ""
            slangphrase = meaning_list[0]["text"]["content"] if meaning_list else ""
            accent = region_obj["name"] if region_obj else ""

            # Skip empty entries (optional)
            if normalphrase and slangphrase and accent:
                results.append(Phrase(normalphrase=normalphrase, slangphrase=slangphrase, accent=accent))
        except Exception as e:
            # Log or handle specific error instead of silently skipping
            print(f"Error parsing page: {e}")
            continue

    return results
