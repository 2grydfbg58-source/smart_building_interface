import re

import chromadb
import pandas as pd
import requests

from utils.helper import format_document, get_dataset_path, load_dataset_as_documents


client = chromadb.PersistentClient(path=".chroma")

collection = client.get_or_create_collection(
    name="building_data",
    metadata={"hnsw:space": "cosine"}
)


def embed_with_ollama(texts, model="nomic-embed-text"):
    url = "http://localhost:11434/api/embed"
    payload = {
        "model": model,
        "input": texts
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()

    if "embeddings" in data:
        embeddings = data["embeddings"]
    elif "embedding" in data:
        embeddings = [data["embedding"]]
    else:
        raise KeyError("Response missing 'embeddings' or 'embedding'")

    if isinstance(texts, str):
        return embeddings[0]
    return embeddings


def infer_hour(query):
    query_lower = query.lower()
    matches = []
    patterns = [
        re.compile(r"(?<!\d)(\d{1,2})(?::(\d{2}))?\s*(?:am|a\.m\.|in the morning|morning)\b", re.IGNORECASE),
        re.compile(r"(?<!\d)(\d{1,2})(?::(\d{2}))?\s*(?:pm|p\.m\.|in the afternoon|afternoon|evening|night)\b", re.IGNORECASE),
    ]
    for pattern in patterns:
        match = pattern.search(query_lower)
        if match:
            hour = int(match.group(1))
            if "pm" in match.group(0) or "afternoon" in match.group(0) or "evening" in match.group(0) or "night" in match.group(0):
                if hour < 12:
                    hour += 12
            elif "morning" in match.group(0) and hour == 12:
                hour = 0
            matches.append(hour)
    if matches:
        return matches[0]
    return None


def find_exact_matches(query, df, k=5):
    hour = infer_hour(query)
    if hour is None:
        return []

    timestamp_series = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H-%M-%S", errors="coerce")
    zone_names = df["zone_name"].drop_duplicates().tolist()
    zone = None
    query_lower = query.lower()
    for candidate in zone_names:
        if candidate in query_lower:
            zone = candidate
            break

    match_mask = timestamp_series.dt.hour == hour
    if zone:
        match_mask &= df["zone_name"] == zone

    matches = df.loc[match_mask].head(k)
    return [format_document(row) for _, row in matches.iterrows()]


def index_documents(docs):
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    embeddings = embed_with_ollama(docs)
    ids = [f"doc_{i}" for i in range(len(docs))]
    collection.add(
        documents=docs,
        embeddings=embeddings,
        ids=ids
    )


def retrieve(query, k=5):
    docs, df = load_dataset_as_documents(get_dataset_path())
    exact_documents = find_exact_matches(query, df, k=k)
    if exact_documents:
        return exact_documents

    query_emb = embed_with_ollama([query])[0]
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=k
    )
    return results["documents"][0]
