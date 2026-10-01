"""Food photo URLs for restaurant cards (demo / synthetic data)."""

import json
import os
import urllib.request

import pandas as pd

PHOTOS_PER_RESTAURANT = 4

# Cuisine-themed Unsplash photos (verified to load).
CUISINE_UNSPLASH = {
    "Japanese": [
        "https://images.unsplash.com/photo-1553621042-f6e147245754?w=800&q=80",
        "https://images.unsplash.com/photo-1574484284002-952d92456975?w=800&q=80",
        "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&q=80",
        "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&q=80",
        "https://images.unsplash.com/photo-1526318896980-cf78c088247c?w=800&q=80",
        "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&q=80",
        "https://images.unsplash.com/photo-1590301157890-4810ed352733?w=800&q=80",
        "https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800&q=80",
    ],
    "Korean": [
        "https://images.unsplash.com/photo-1590301157890-4810ed352733?w=800&q=80",
        "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&q=80",
        "https://images.unsplash.com/photo-1553621042-f6e147245754?w=800&q=80",
        "https://images.unsplash.com/photo-1574484284002-952d92456975?w=800&q=80",
    ],
    "Chinese": [
        "https://images.unsplash.com/photo-1526318896980-cf78c088247c?w=800&q=80",
        "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&q=80",
        "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&q=80",
        "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&q=80",
    ],
    "Western": [
        "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&q=80",
        "https://images.unsplash.com/photo-1600891964092-4316c288032e?w=800&q=80",
        "https://images.unsplash.com/photo-1432139555190-58524dae6a55?w=800&q=80",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
    ],
    "Thai": [
        "https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800&q=80",
        "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=800&q=80",
        "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&q=80",
        "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80",
    ],
    "Indian": [
        "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&q=80",
        "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=800&q=80",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
    ],
    "Italian": [
        "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&q=80",
        "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&q=80",
        "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80",
    ],
    "Mexican": [
        "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800&q=80",
        "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=800&q=80",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
        "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80",
    ],
    "Malaysian": [
        "https://images.unsplash.com/photo-1569058242253-92a9c755a0ec?w=800&q=80",
        "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=800&q=80",
        "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&q=80",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80",
    ],
    "Vegetarian": [
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80",
        "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&q=80",
        "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800&q=80",
        "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80",
    ],
}

# Extra Foodish photos to enlarge each cuisine pool (unique dishes).
CUISINE_FOODISH = {
    "Japanese": None,
    "Korean": "burger",
    "Chinese": "samosa",
    "Western": "burger",
    "Thai": "samosa",
    "Indian": "biryani",
    "Italian": "pizza",
    "Mexican": "burger",
    "Malaysian": "biryani",
    "Vegetarian": "dosa",
}

TYPE_MAX_IMAGE = {
    "pizza": 90,
    "burger": 90,
    "biryani": 90,
    "samosa": 22,
    "dosa": 90,
    "idly": 90,
    "butter-chicken": 90,
}

_CUISINE_POOL_CACHE = {}

DEFAULT_UNSPLASH = [
    "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80",
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
    "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800&q=80",
    "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&q=80",
]


def _project_data_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    return os.path.join(project_root, "data")


def _restaurant_number(restaurant_id):
    text = str(restaurant_id).strip()
    if text.startswith("R") and text[1:].isdigit():
        return int(text[1:])
    return sum(ord(char) for char in text)


def _foodish_url(food_type, image_number):
    return (
        f"https://foodish-api.com/images/"
        f"{food_type}/{food_type}{image_number}.jpg"
    )


def _url_exists(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as response:
            return response.status < 400
    except Exception:
        return False


def cuisine_image_pool(cuisine):
    """Build a large cuisine-themed pool (Unsplash + Foodish)."""
    if cuisine in _CUISINE_POOL_CACHE:
        return _CUISINE_POOL_CACHE[cuisine]

    pool = list(CUISINE_UNSPLASH.get(cuisine, DEFAULT_UNSPLASH))
    seen = set(pool)

    food_type = CUISINE_FOODISH.get(cuisine)
    if food_type:
        max_number = TYPE_MAX_IMAGE.get(food_type, 90)
        for image_number in range(1, max_number + 1):
            url = _foodish_url(food_type, image_number)
            if url in seen:
                continue
            if not _url_exists(url):
                continue
            pool.append(url)
            seen.add(url)
            if len(pool) >= 40:
                break

    if len(pool) < PHOTOS_PER_RESTAURANT:
        for url in DEFAULT_UNSPLASH:
            if url not in seen:
                pool.append(url)
                seen.add(url)

    _CUISINE_POOL_CACHE[cuisine] = pool
    return pool


def pick_restaurant_image_urls(cuisine, restaurant_id, count=PHOTOS_PER_RESTAURANT):
    """Pick `count` unique cuisine-themed photos for one restaurant."""
    pool = cuisine_image_pool(cuisine)
    if len(pool) < count:
        raise ValueError(f"Not enough images for cuisine {cuisine}")

    restaurant_number = _restaurant_number(restaurant_id)
    start = ((restaurant_number - 1) * count) % len(pool)
    picks = []

    for offset in range(len(pool)):
        if len(picks) >= count:
            break
        url = pool[(start + offset) % len(pool)]
        if url not in picks:
            picks.append(url)

    return picks


def _parse_image_urls_from_csv(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text == "nan":
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list) and len(parsed) > 0:
            return parsed
    except json.JSONDecodeError:
        pass
    return None


def image_urls_for_restaurant(restaurant, *, ignore_csv=False):
    if not ignore_csv and "image_urls" in restaurant.index:
        parsed = _parse_image_urls_from_csv(restaurant["image_urls"])
        if parsed:
            return parsed[:PHOTOS_PER_RESTAURANT]

    cuisine = restaurant.get("cuisine", "")
    restaurant_id = restaurant.get("restaurant_id", "R000")
    return pick_restaurant_image_urls(cuisine, restaurant_id)


def image_url_for_restaurant(restaurant, *, ignore_csv=False):
    urls = image_urls_for_restaurant(restaurant, ignore_csv=ignore_csv)
    return urls[0]


def refresh_restaurant_image_urls(csv_path):
    df = pd.read_csv(csv_path)
    image_urls_col = []
    image_url_col = []

    for _, row in df.iterrows():
        urls = pick_restaurant_image_urls(
            row["cuisine"],
            row["restaurant_id"],
        )
        image_urls_col.append(json.dumps(urls))
        image_url_col.append(urls[0])

    df["image_urls"] = image_urls_col
    df["image_url"] = image_url_col
    df.to_csv(csv_path, index=False)
    return df
