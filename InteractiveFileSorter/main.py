from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from api.file_grouping_by_content import group_files_by_content

app = FastAPI(
    title="File Organizer API",
    description="Organize and group local files by type, date, or content",
    version="0.1.0"
)

# CORS setup (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # use specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "File Organizer API is running."}

@app.post("/organize-by-content")
def organize_by_content_api(
    path: str = Query(..., description="Absolute path to folder with files"),
    clusters: int = Query(5, description="Number of semantic clusters to create")
):
    """
    Organize files by semantic content similarity using OpenAI embeddings.
    Moves files into folders named cluster_0, cluster_1, etc.
    """
    group_files_by_content(path, n_clusters=clusters)
    return {"message": f"Organized files in '{path}' into {clusters} content clusters."}
