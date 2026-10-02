"""Build deterministic restaurant_id -> cuisine food image map for the React app."""

import json
import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH = os.path.join(ROOT, "data", "restaurants.csv")
OUTPUT_PATH = os.path.join(
    ROOT,
    "frontend-react",
    "src",
    "restaurantImageMap.json",
)

GENERIC = (
    "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80"
)


def unsplash(photo_id):
    return f"https://images.unsplash.com/photo-{photo_id}?w=800&q=80"


def foodish(food_type, number):
    return (
        f"https://foodish-api.com/images/{food_type}/"
        f"{food_type}{number}.jpg"
    )


# Verified / cuisine-themed image pools (each list is used in order per restaurant).
CUISINE_IMAGE_POOLS = {
    "Japanese": [
        unsplash("1553621042-f6e147245754"),
        unsplash("1574484284002-952d92456975"),
        unsplash("1559339352-11d035aa65de"),
        unsplash("1544025162-d76694265947"),
        unsplash("1490806849937-45d4a36d4a21"),
        unsplash("1564489568502-aa3e998e037a"),
        unsplash("1557872943-16a5ac26436e"),
        unsplash("1617196034797-47a7e5e5640f"),
    ],
    "Korean": [
        unsplash("1590301157890-4810ed352733"),
        unsplash("1626804475297-41608ea09e59"),
        unsplash("1544025162-d76694265947"),
        unsplash("1559339352-11d035aa65de"),
        unsplash("1574484284002-952d92456975"),
        unsplash("1553621042-f6e147245754"),
        unsplash("1490806849937-45d4a36d4a21"),
        unsplash("1564489568502-aa3e998e037a"),
        unsplash("1557872943-16a5ac26436e"),
        unsplash("1617196034797-47a7e5e5640f"),
        unsplash("1526318896980-cf78c088247c"),
        unsplash("1563379091339-03b21ab4a4f8"),
        unsplash("1559314809-0d155014e29e"),
        unsplash("1455619452474-d2be8b1e70cd"),
    ],
    "Chinese": [
        unsplash("1526318896980-cf78c088247c"),
        unsplash("1563379091339-03b21ab4a4f8"),
        foodish("samosa", 1),
        foodish("samosa", 2),
        foodish("samosa", 3),
        foodish("samosa", 4),
        foodish("samosa", 5),
        foodish("samosa", 6),
        foodish("samosa", 7),
    ],
    "Western": [foodish("burger", n) for n in range(1, 14)],
    "Thai": [
        unsplash("1559314809-0d155014e29e"),
        unsplash("1455619452474-d2be8b1e70cd"),
        unsplash("1476224203421-9ac39bcb3327"),
        unsplash("1504674900247-0877df9cc836"),
        unsplash("1544025162-d76694265947"),
        unsplash("1559339352-11d035aa65de"),
        unsplash("1574484284002-952d92456975"),
        unsplash("1553621042-f6e147245754"),
        unsplash("1526318896980-cf78c088247c"),
        unsplash("1563379091339-03b21ab4a4f8"),
        unsplash("1569058242253-92a9c755a0ec"),
        unsplash("1512058564366-18510be2db19"),
        unsplash("1585937421612-70a008356fbe"),
        unsplash("1565557623262-b51c2513a641"),
        unsplash("1565299624946-b28f40a0ae38"),
        unsplash("1513104890138-7c749659a591"),
    ],
    "Indian": [foodish("biryani", n) for n in range(1, 14)],
    "Italian": [foodish("pizza", n) for n in range(1, 8)],
    "Mexican": [
        unsplash("1565299585323-38d6b0865b47"),
        unsplash("1551504734-5ee1c4a1479b"),
        foodish("burger", 40),
        foodish("burger", 41),
        foodish("burger", 42),
        foodish("burger", 43),
        foodish("burger", 45),
    ],
    "Malaysian": [
        unsplash("1569058242253-92a9c755a0ec"),
        unsplash("1512058564366-18510be2db19"),
        foodish("biryani", 20),
        foodish("biryani", 21),
        foodish("biryani", 22),
        foodish("biryani", 23),
        foodish("biryani", 24),
        foodish("biryani", 25),
        foodish("biryani", 26),
        foodish("biryani", 27),
    ],
    "Vegetarian": [
        unsplash("1512621776951-a57141f2eefd"),
        unsplash("1540420773420-3366772f4999"),
        unsplash("1490645935967-10de6ba17061"),
        foodish("dosa", 1),
        foodish("dosa", 2),
        foodish("dosa", 3),
    ],
}


def main():
    df = pd.read_csv(CSV_PATH)
    image_map = {}
    cuisine_counters = {}

    for _, row in df.sort_values("restaurant_id").iterrows():
        restaurant_id = row["restaurant_id"]
        cuisine = row["cuisine"]
        pool = CUISINE_IMAGE_POOLS.get(cuisine, [GENERIC])

        counter = cuisine_counters.get(cuisine, 0)
        image_map[restaurant_id] = pool[counter % len(pool)]
        cuisine_counters[cuisine] = counter + 1

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(image_map, file, indent=2)

    print(f"Wrote {len(image_map)} entries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
