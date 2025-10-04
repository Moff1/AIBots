# app/main.py
from fastapi import FastAPI
from notion_client import Client
import os

app = FastAPI()

NOTION_SECRET = os.getenv("NOTION_SECRET")
PAGE_ID = os.getenv("NOTION_PAGE_ID")

notion = Client(auth=NOTION_SECRET)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/page")
def get_page():
    page = notion.pages.retrieve(PAGE_ID)
    return page
