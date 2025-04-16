import json
import numpy as np
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)  # reuse your existing embedding logic
from dotenv import load_dotenv
import os
import torch
import json
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel
from transformers import CLIPTokenizerFast
from transformers import pipeline
import unicodedata
import os
import requests
from io import BytesIO
from app.models import load_fashionclip
from more_itertools import chunked

COLLECTION_A = "company_a_index"
COLLECTION_B = "company_b_index"
VECTOR_SIZE = 512

# --- LOAD PRODUCTS ---
with open("consolidated_products_normalized.json", "r", encoding="utf-8") as f:
    products = json.load(f)

# --- SPLIT BY CUSTOMER (ODD vs EVEN product_id) ---
company_a_products = [p for p in products if int(p["product_id"]) % 2 == 1]
company_b_products = [p for p in products if int(p["product_id"]) % 2 == 0]


def clean_text(text):
    """Remove non-printable characters and normalize text encoding."""

    # Remove b'...' or b"..." prefixes if they exist
    if text.startswith("b'") and text.endswith("'"):
        return text[2:-1]
    if text.startswith('b"') and text.endswith('"'):
        return text[2:-1]
    # Normalize Unicode (NFKC to combine similar characters)
    text = unicodedata.normalize("NFKC", text)

    # Remove replacement character (�) if it appears
    text = text.replace("�", "")

    # If text is still empty, assign a default description
    if len(text.strip()) == 0:
        return "generic fashion item"

    return text


def get_text_embedding(text):
    max_tokens = 75  # CLIP's token limit
    text = clean_text(text)  # Ensure valid, encoded text

    if not text or len(text.strip()) == 0:  # Handle empty strings
        text = "generic fashion item"  # Provide a default text

    # Use the Hugging Face tokenizer with truncation to ensure the tokenized output fits within max_tokens
    tokenized = hf_tokenizer(
        text, truncation=True, max_length=max_tokens, return_tensors="pt"
    )

    # Move the tokens to the appropriate device
    input_ids = tokenized["input_ids"].to(device)

    with torch.no_grad():
        text_embedding = model.get_text_features(input_ids)
    return text_embedding.cpu().numpy()


def get_combined_text(product):
    """
    Combine the product name and summary description into one string.
    If summary_description is missing or empty, use only the product name.
    """
    product_name = product.get("name", "").strip()
    summary = product.get("description", "").strip()  # Using the English version
    if summary:
        combined_text = f"{product_name}. {summary}"
    else:
        combined_text = product_name
    return combined_text


def get_product_embedding(product):
    """
    Generate an embedding for the product by combining product name and summary description.
    """
    combined_text = get_combined_text(product)
    return get_text_embedding(combined_text)


# Function to get image embeddings
def get_image_embedding(image_path_or_url):
    # Check if image_path is valid (not None or empty)
    if not image_path_or_url:
        # print("⚠️ No image path provided; returning zero vector.")
        return np.zeros((1, 512))
    try:
        # Determine if the path is a URL by checking if it starts with "http"
        if image_path_or_url.startswith("http"):
            # Download the image data from the URL
            response = requests.get(image_path_or_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
        else:
            # For local files, open directly
            img = Image.open(image_path_or_url)

        # Determine the file extension (if available)
        ext = (
            os.path.splitext(image_path_or_url)[1].lower()
            if not image_path_or_url.startswith("http")
            else os.path.splitext(image_path_or_url)[1].lower()
        )

        # If the image is a GIF, extract the first frame
        if ext == ".gif":
            with Image.open(img.fp if hasattr(img, "fp") else img) as gif:
                gif.seek(0)
                img = gif.convert("RGB")
        else:
            img = img.convert("RGB")

        # for image_path
        # image = processor(images=Image.open(image_path), return_tensors="pt").to(device)
        # for gif path
        image = processor(images=img, return_tensors="pt").to(device)
        with torch.no_grad():
            image_embedding = model.get_image_features(**image)
        return image_embedding.cpu().numpy()
    except Exception as e:
        print(f"⚠️ Error processing image {image_path_or_url}: {e}")
        return np.zeros((1, 512))  # Return a zero vector if image fails


def get_fused_embedding(product):
    # Compute text embedding (shape: (1, 512))
    text_emb = get_product_embedding(product)

    # Compute image embedding if available; if not, use a zero vector
    if "list_image" in product and product["image_path"]:
        image_emb = get_image_embedding(product["image_path"])
    else:
        image_emb = np.zeros((1, 512))

    # Average the embeddings
    fused_emb = (text_emb + image_emb) / 2
    return fused_emb


def create_collection_if_needed(collection_name):
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


# --- CREATE BOTH COLLECTIONS ---
create_collection_if_needed(COLLECTION_A)
create_collection_if_needed(COLLECTION_B)


def batchify(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i : i + batch_size]


def upload_embeddings(collection_name, products, batch_size=50):
    for batch in batchify(products, batch_size):
        points = []
        for product in batch:
            embedding = get_fused_embedding(product).flatten().tolist()
            points.append(
                PointStruct(
                    id=int(product["product_id"]),
                    vector=embedding,
                    payload={
                        "name": product.get("name", ""),
                        "description": product.get("description", ""),
                        "category": product.get("category", ""),
                        "brand": product.get("brand", ""),
                        "gender": product.get("gender", ""),
                        "image_path": product.get("image_path", ""),
                    },
                )
            )
        print(f"Uploading batch of {len(points)} to {collection_name}")
        client.upsert(collection_name=collection_name, points=points)


# --- UPLOAD TO BOTH COLLECTIONS ---
"""
upload_embeddings(
    collection_name="company_a_index",
    products=company_a_products,
    batch_size=50,
)
"""
