#!/usr/bin/env python3
"""Seed Firestore with iconic Hyderabad food spots."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-e226274537b5"
COLLECTION_NAME = "hyderabad_food_spots"

SPOTS = [
    {
        "id": "hotel-shadab",
        "name": "Hotel Shadab",
        "area": "Old City",
        "signature_dish": "Hyderabadi Mutton Dum Biryani",
        "price_range": "₹₹",
        "dietary": "non-veg",
        "timings": "5:30 AM - 12:30 AM",
        "description": "Legendary restaurant near Charminar famous for authentic slow-cooked dum biryani, paya with roti, and festive haleem.",
    },
    {
        "id": "cafe-niloufer",
        "name": "Cafe Niloufer",
        "area": "Banjara Hills",
        "signature_dish": "Irani Chai & Osmania Biscuits",
        "price_range": "₹",
        "dietary": "veg",
        "timings": "6:00 AM - 11:30 PM",
        "description": "Iconic tea destination established in 1978, serving creamy malai Irani chai, fresh Osmania biscuits, and bun maska.",
    },
    {
        "id": "pista-house",
        "name": "Pista House",
        "area": "Old City",
        "signature_dish": "Mutton Haleem",
        "price_range": "₹₹",
        "dietary": "non-veg",
        "timings": "11:00 AM - 11:30 PM",
        "description": "GI-tagged world-famous rich mutton haleem garnished with fried onions, ghee, cashews, and fresh lemon.",
    },
    {
        "id": "bawarchi",
        "name": "Bawarchi Restaurant",
        "area": "Ameerpet",
        "signature_dish": "Special Chicken Biryani",
        "price_range": "₹₹",
        "dietary": "non-veg",
        "timings": "11:30 AM - 11:00 PM",
        "description": "The quintessential Hyderabad biryani haven at RTC X Roads, renowned for generous portions and fragrant mirchi ka salan.",
    },
    {
        "id": "govind-dosa",
        "name": "Govind Ki Bandi",
        "area": "Old City",
        "signature_dish": "Butter Tawa Idli & Cheese Tawa Dosa",
        "price_range": "₹",
        "dietary": "veg",
        "timings": "6:30 AM - 1:30 PM",
        "description": "Famous street cart near Charminar legendary for melt-in-the-mouth idlis roasted in generous butter and spicy podi.",
    },
    {
        "id": "chutneys",
        "name": "Chutneys",
        "area": "Banjara Hills",
        "signature_dish": "Steam Dosa with Six Chutneys",
        "price_range": "₹₹",
        "dietary": "veg",
        "timings": "7:00 AM - 11:00 PM",
        "description": "Premium South Indian vegetarian dining famous for fluffy oil-free steam dosas served with six signature chutneys.",
    },
    {
        "id": "shah-ghouse",
        "name": "Shah Ghouse Cafe & Restaurant",
        "area": "Gachibowli",
        "signature_dish": "Special Mutton Biryani & Tangdi Kabab",
        "price_range": "₹₹",
        "dietary": "non-veg",
        "timings": "11:00 AM - 1:00 AM",
        "description": "Bustling outlet beloved by IT corridor locals for flavorful, spicy biryani, succulent kababs, and midnight chai.",
    },
    {
        "id": "subhan-bakery",
        "name": "Subhan Bakery",
        "area": "Old City",
        "signature_dish": "Dum Ke Roat & Osmania Biscuits",
        "price_range": "₹",
        "dietary": "veg",
        "timings": "8:00 AM - 10:30 PM",
        "description": "Heritage bakery crafting classic Hyderabadi baked delicacies including authentic baked roat and butter cookies since 1880.",
    },
    {
        "id": "famous-ice-cream",
        "name": "Famous Ice Cream",
        "area": "Old City",
        "signature_dish": "Handmade Mango & Sapota Seasonal Pot Ice Cream",
        "price_range": "₹",
        "dietary": "veg",
        "timings": "9:00 AM - 12:00 AM",
        "description": "Historic ice cream shop in Mozamjahi Market serving traditional handmade seasonal fruit ice creams in terracotta pots.",
    },
    {
        "id": "varalakshmi-tiffins",
        "name": "Varalakshmi Tiffins",
        "area": "Gachibowli",
        "signature_dish": "Ghee Karam Dosa & Filter Coffee",
        "price_range": "₹",
        "dietary": "veg",
        "timings": "6:00 AM - 11:30 PM",
        "description": "Popular tech-corridor tiffin spot known for crisp ghee-laden dosas, spicy gun powder idlis, and piping hot filter coffee.",
    },
]


def seed():
    print(f"Connecting to Firestore for project '{PROJECT_ID}'...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    batch = db.batch()
    for spot in SPOTS:
        doc_ref = collection.document(spot["id"])
        batch.set(doc_ref, spot)

    batch.commit()
    print(f"Successfully seeded {len(SPOTS)} spots into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed()
