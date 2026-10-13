# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Firestore tools for Hyderabad Food Trail Guide."""

from typing import Any, Dict, List, Optional
import uuid
from google.cloud import firestore, storage
from google import genai
from google.genai import types
from google.adk.tools.tool_context import ToolContext

# Hardcode project ID explicitly as required for Agent Platform deployment
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-e226274537b5"
COLLECTION_SPOTS = "hyderabad_food_spots"
COLLECTION_FAVORITES = "user_favorites"

_db: Optional[firestore.Client] = None


def get_db() -> firestore.Client:
    """Returns a singleton Firestore client pinned to the explicit project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    return _db


def search_food_spots(
    area: Optional[str] = None,
    dietary: Optional[str] = None,
    query: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search for famous Hyderabad food spots in Firestore.

    Args:
        area: Optional neighborhood filter (e.g., 'Old City', 'Banjara Hills', 'Gachibowli', 'Ameerpet').
        dietary: Optional dietary filter ('veg' or 'non-veg').
        query: Optional keyword to match against name, signature dish, or description (e.g. 'biryani', 'chai', 'dosa').

    Returns:
        A list of matching food spot dictionaries.
    """
    db = get_db()
    spots_ref = db.collection(COLLECTION_SPOTS)
    docs = spots_ref.stream()

    results = []
    area_clean = area.strip().lower() if area else None
    dietary_clean = dietary.strip().lower() if dietary else None
    query_clean = query.strip().lower() if query else None

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        # Area filter
        if area_clean and area_clean not in data.get("area", "").lower():
            continue

        # Dietary filter
        if dietary_clean and dietary_clean != data.get("dietary", "").lower():
            continue

        # Keyword query filter
        if query_clean:
            searchable_text = f"{data.get('name', '')} {data.get('signature_dish', '')} {data.get('description', '')}".lower()
            if query_clean not in searchable_text:
                continue

        results.append(data)

    return results


def save_favorite_spot(
    spot_id: str,
    notes: Optional[str] = None,
) -> str:
    """Save a food spot to user favorites in Firestore.

    Args:
        spot_id: Unique identifier or name of the spot (e.g., 'hotel-shadab', 'cafe-niloufer').
        notes: Optional user note or reason for favoriting (e.g., 'Must try late night with friends').

    Returns:
        Status message confirming the spot was saved.
    """
    db = get_db()
    # Check if spot exists in catalog
    spot_doc = db.collection(COLLECTION_SPOTS).document(spot_id).get()
    spot_name = spot_doc.to_dict().get("name", spot_id) if spot_doc.exists else spot_id

    fav_ref = db.collection(COLLECTION_FAVORITES).document(spot_id)
    fav_data = {
        "spot_id": spot_id,
        "name": spot_name,
        "notes": notes or "",
        "saved_at": firestore.SERVER_TIMESTAMP,
    }
    fav_ref.set(fav_data, merge=True)
    return f"Saved '{spot_name}' to your favorites successfully!"


def list_favorite_spots() -> List[Dict[str, Any]]:
    """Retrieve all saved favorite food spots from Firestore.

    Returns:
        List of saved favorite spots with details and notes.
    """
    db = get_db()
    docs = db.collection(COLLECTION_FAVORITES).stream()
    favorites = []
    for doc in docs:
        data = doc.to_dict()
        # Drop non-serializable timestamp if present
        if "saved_at" in data:
            data["saved_at"] = str(data["saved_at"])
        favorites.append(data)
    return favorites


STORAGE_BUCKET_NAME = "hyderabad-food-trail-274537b5"
_storage_client: Optional[storage.Client] = None
_genai_client: Optional[genai.Client] = None


def get_storage_client() -> storage.Client:
    """Returns a singleton Cloud Storage client."""
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    return _storage_client


def get_genai_client() -> genai.Client:
    """Returns a singleton GenAI client configured for Vertex AI in global region."""
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            vertexai=True,
            project=FIRESTORE_PROJECT_ID,
            location="global",
        )
    return _genai_client


async def generate_dish_image(
    dish_name: str,
    tool_context: ToolContext,
) -> str:
    """Generates an image of a famous Hyderabad dish, saves it as an artifact, and uploads to Cloud Storage.

    Args:
        dish_name: Name of the dish to generate (e.g., 'Hyderabadi Mutton Dum Biryani', 'Irani Chai with Osmania Biscuits', 'Mutton Haleem').
        tool_context: Injected tool context for saving session artifacts in Playground.

    Returns:
        The public HTTPS URL of the uploaded image in Cloud Storage.
    """
    client = get_genai_client()
    prompt = (
        f"A mouth-watering, highly detailed, gourmet photograph of authentic Hyderabadi {dish_name}. "
        "Professional food photography, steaming hot, rich appetizing colors, garnished beautifully in authentic Indian tableware, shallow depth of field."
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
    )

    # Extract image bytes
    image_bytes: Optional[bytes] = None
    mime_type = "image/jpeg"

    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            image_bytes = part.inline_data.data
            if part.inline_data.mime_type:
                mime_type = part.inline_data.mime_type
            break

    if not image_bytes:
        raise ValueError(f"No image was generated for '{dish_name}'.")

    # 1. Save artifact to ToolContext for Playground Artifacts panel
    slug = "".join(c if c.isalnum() else "_" for c in dish_name.lower()).strip("_")
    filename = f"{slug}_{uuid.uuid4().hex[:6]}.jpg"

    artifact_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type,
    )
    await tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
    )

    # 2. Upload bytes to public Cloud Storage bucket
    storage_client = get_storage_client()
    bucket = storage_client.bucket(STORAGE_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(
        data=image_bytes,
        content_type=mime_type,
    )

    # Return public HTTPS URL
    public_url = f"https://storage.googleapis.com/{STORAGE_BUCKET_NAME}/{filename}"
    return public_url
