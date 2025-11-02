import os
import openai
import pdfplumber
import docx
import json
import shutil
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
from tqdm import tqdm



# 1. Read file content
def extract_text_from_file(file_path: str) -> str:
    if file_path.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            return '\n'.join(page.extract_text() or '' for page in pdf.pages)
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    return ""

# 2. Generate embedding for text
def get_embedding(text: str) -> List[float]:
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8192]  # truncate long text
    )
    return response.data[0].embedding

# 3. Organize by clustering embeddings
def group_files_by_content(folder_path: str, n_clusters: int = 5):
    file_paths = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(('.pdf', '.docx', '.txt'))
    ]

    contents = []
    embeddings = []
    valid_files = []

    for path in tqdm(file_paths, desc="Extracting and embedding"):
        text = extract_text_from_file(path)
        if text.strip():
            try:
                embedding = get_embedding(text)
                contents.append(text)
                embeddings.append(embedding)
                valid_files.append(path)
            except Exception as e:
                print(f"Embedding failed for {path}: {e}")

    if len(embeddings) < 2:
        print("Not enough valid files to cluster.")
        return

    # Cluster with KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)

    # Organize files by cluster
    for label, file_path in zip(labels, valid_files):
        cluster_folder = os.path.join(folder_path, f"cluster_{label}")
        os.makedirs(cluster_folder, exist_ok=True)
        shutil.move(file_path, os.path.join(cluster_folder, os.path.basename(file_path)))

    print(f"Grouped {len(valid_files)} files into {n_clusters} folders.")