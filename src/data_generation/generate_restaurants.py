"""Generate a synthetic dataset of 100 restaurants."""

import os
import random

import pandas as pd

random.seed(42)

NUM_RESTAURANTS = 100

CUISINES = [
    "Japanese",
    "Korean",
    "Chinese",
    "Western",
    "Thai",
    "Indian",
    "Italian",
    "Mexican",
    "Malaysian",
    "Vegetarian",
]

# Approximate city centres. Coordinates are jittered later so restaurants
# are nearby but not stacked on the same point.
CITIES = {
    "Kuala Lumpur": (3.1390, 101.6869),
    "Petaling Jaya": (3.1073, 101.6067),
    "Shah Alam": (3.0733, 101.5185),
    "Johor Bahru": (1.4927, 103.7414),
    "Penang": (5.4141, 100.3288),
}

PRICE_RANGES = ["$", "$$", "$$$", "$$$$"]

# Cuisine-specific names, categories, and description templates.
CUISINE_DETAILS = {
    "Japanese": {
        "name_prefixes": [
            "Sakura", "Tokyo", "Nami", "Koi", "Hana", "Zen", "Umami", "Raku",
        ],
        "name_suffixes": [
            "Sushi", "Ramen", "Izakaya", "Kitchen", "House", "Bar",
        ],
        "categories": [
            "sushi", "ramen", "izakaya", "tempura", "donburi", "casual dining",
        ],
        "descriptions": [
            "A {price} Japanese spot in {city} known for {cat} and a {rating}-star crowd.",
            "Serves classic {cat} with a modern twist, popular among {city} diners.",
            "Casual Japanese kitchen offering {cat} in a relaxed {city} setting.",
        ],
    },
    "Korean": {
        "name_prefixes": [
            "Seoul", "Han", "Kimchi", "Dae", "Nara", "Gogi", "Banchan", "K-Town",
        ],
        "name_suffixes": [
            "BBQ", "Kitchen", "House", "Grill", "Chicken", "Eatery",
        ],
        "categories": [
            "korean bbq", "fried chicken", "bibimbap", "soju bar", "street food",
        ],
        "descriptions": [
            "A {price} Korean restaurant in {city} famous for {cat}.",
            "Warm Korean cooking with a focus on {cat}, well-liked in {city}.",
            "Family-friendly Korean eatery serving {cat} and classic sides.",
        ],
    },
    "Chinese": {
        "name_prefixes": [
            "Dragon", "Jade", "Lucky", "Golden", "Lotus", "Pearl", "Imperial", "Red",
        ],
        "name_suffixes": [
            "Palace", "Garden", "Kitchen", "House", "Wok", "Dim Sum",
        ],
        "categories": [
            "dim sum", "roasted meats", "noodle soup", "stir-fry", "family restaurant",
        ],
        "descriptions": [
            "A {price} Chinese restaurant in {city} serving {cat} and comfort classics.",
            "Busy neighbourhood kitchen known for {cat} and generous portions.",
            "Traditional Chinese flavours with a focus on {cat} in {city}.",
        ],
    },
    "Western": {
        "name_prefixes": [
            "The Oak", "Harbor", "Maple", "Brook", "Forge", "Copper", "Willow", "Stone",
        ],
        "name_suffixes": [
            "Grill", "Bistro", "Cafe", "Kitchen", "Diner", "Steakhouse",
        ],
        "categories": [
            "steak", "burgers", "brunch", "pasta", "casual dining", "comfort food",
        ],
        "descriptions": [
            "A {price} Western {cat} restaurant in {city} with a {rating}-star following.",
            "Relaxed Western dining in {city}, known for {cat} and hearty mains.",
            "All-day Western menu featuring {cat} in a neighbourhood setting.",
        ],
    },
    "Thai": {
        "name_prefixes": [
            "Bangkok", "Siam", "Basil", "Lotus", "Chiang", "Lemongrass", "Thai", "Orchid",
        ],
        "name_suffixes": [
            "Kitchen", "House", "Cafe", "Garden", "Street", "Bistro",
        ],
        "categories": [
            "tom yum", "pad thai", "green curry", "street food", "spicy",
        ],
        "descriptions": [
            "A {price} Thai eatery in {city} known for {cat} and bold flavours.",
            "Home-style Thai cooking with a focus on {cat}, popular in {city}.",
            "Fragrant Thai kitchen serving {cat} in a casual setting.",
        ],
    },
    "Indian": {
        "name_prefixes": [
            "Spice", "Mumbai", "Tandoor", "Masala", "Royal", "Naan", "Curry", "Saffron",
        ],
        "name_suffixes": [
            "House", "Kitchen", "Palace", "Grill", "Dhaba", "Bistro",
        ],
        "categories": [
            "tandoori", "biryani", "north indian", "south indian", "vegetarian-friendly",
        ],
        "descriptions": [
            "A {price} Indian restaurant in {city} specialising in {cat}.",
            "Aromatic Indian cooking with {cat} as the house favourite.",
            "Comforting Indian flavours and {cat}, well known around {city}.",
        ],
    },
    "Italian": {
        "name_prefixes": [
            "Nonna", "Roma", "Bella", "Luca", "Vino", "Trattoria", "Casa", "Olive",
        ],
        "name_suffixes": [
            "Trattoria", "Pizzeria", "Kitchen", "Osteria", "Pasta", "Bistro",
        ],
        "categories": [
            "pizza", "pasta", "wine bar", "risotto", "fine casual",
        ],
        "descriptions": [
            "A {price} Italian spot in {city} known for {cat} and a {rating}-star crowd.",
            "Handmade Italian cooking with a focus on {cat}.",
            "Cosy trattoria serving {cat} in the heart of {city}.",
        ],
    },
    "Mexican": {
        "name_prefixes": [
            "Casa", "El Sol", "Fiesta", "Cactus", "Maya", "Taco", "Luna", "Azul",
        ],
        "name_suffixes": [
            "Cantina", "Kitchen", "Grill", "Tacos", "Bar", "House",
        ],
        "categories": [
            "tacos", "burritos", "guacamole", "quesadillas", "casual dining",
        ],
        "descriptions": [
            "A {price} Mexican kitchen in {city} famous for {cat}.",
            "Bright, casual Mexican cooking centred on {cat}.",
            "Street-style Mexican flavours with {cat} as a signature dish.",
        ],
    },
    "Malaysian": {
        "name_prefixes": [
            "Kampung", "Nasi", "Warung", "Penang", "Nyonya", "Satay", "Mamak", "Heritage",
        ],
        "name_suffixes": [
            "Kitchen", "House", "Stall", "Cafe", "Corner", "Eatery",
        ],
        "categories": [
            "nasi lemak", "laksa", "satay", "roti canai", "mamak", "nyonya",
        ],
        "descriptions": [
            "A {price} Malaysian favourite in {city} known for {cat}.",
            "Local comfort food with a focus on {cat} and everyday flavours.",
            "Neighbourhood Malaysian eatery serving {cat} in {city}.",
        ],
    },
    "Vegetarian": {
        "name_prefixes": [
            "Green", "Garden", "Leaf", "Harmony", "Pure", "Lotus", "Earth", "Bloom",
        ],
        "name_suffixes": [
            "Kitchen", "Cafe", "Table", "Bowl", "House", "Garden",
        ],
        "categories": [
            "plant-based", "vegan-friendly", "salads", "healthy", "meat-free",
        ],
        "descriptions": [
            "A {price} vegetarian restaurant in {city} focused on {cat} dishes.",
            "Meat-free cooking with {cat} options and a {rating}-star following.",
            "Bright vegetarian cafe in {city} known for {cat}.",
        ],
    },
}

# Cheaper cuisines are more likely to be $ / $$; others lean a bit higher.
CUISINE_PRICE_WEIGHTS = {
    "Japanese": [0.10, 0.35, 0.40, 0.15],
    "Korean": [0.20, 0.45, 0.28, 0.07],
    "Chinese": [0.25, 0.45, 0.25, 0.05],
    "Western": [0.15, 0.40, 0.35, 0.10],
    "Thai": [0.30, 0.45, 0.20, 0.05],
    "Indian": [0.25, 0.45, 0.25, 0.05],
    "Italian": [0.10, 0.35, 0.40, 0.15],
    "Mexican": [0.30, 0.50, 0.18, 0.02],
    "Malaysian": [0.40, 0.45, 0.13, 0.02],
    "Vegetarian": [0.20, 0.50, 0.25, 0.05],
}


def pick_categories(cuisine):
    """Pick 2-3 categories that match the cuisine."""
    options = CUISINE_DETAILS[cuisine]["categories"]
    n = random.randint(2, 3)
    chosen = random.sample(options, n)
    return ", ".join(chosen)


def make_name(cuisine, used_names):
    """Build a unique restaurant name from cuisine-specific words."""
    details = CUISINE_DETAILS[cuisine]
    for _ in range(50):
        prefix = random.choice(details["name_prefixes"])
        suffix = random.choice(details["name_suffixes"])
        name = f"{prefix} {suffix}"
        if name not in used_names:
            used_names.add(name)
            return name

    # Fallback if the name lists collide.
    extra = 1
    while True:
        name = f"{prefix} {suffix} {extra}"
        if name not in used_names:
            used_names.add(name)
            return name
        extra += 1


def make_rating():
    """Ratings are slightly skewed toward 3.8-4.6, still within 3.0-5.0."""
    rating = random.gauss(4.2, 0.45)
    rating = max(3.0, min(5.0, rating))
    return round(rating, 1)


def make_review_count(rating, price_range):
    """Higher ratings and mid-range prices tend to attract more reviews."""
    base = 40 + int((rating - 3.0) * 220)
    if price_range == "$":
        base += random.randint(0, 80)
    elif price_range == "$$":
        base += random.randint(40, 180)
    elif price_range == "$$$":
        base += random.randint(10, 120)
    else:
        base += random.randint(-20, 60)

    noise = random.randint(-50, 80)
    return max(12, base + noise)


def make_description(cuisine, city, price_range, rating, categories):
    template = random.choice(CUISINE_DETAILS[cuisine]["descriptions"])
    first_category = categories.split(",")[0].strip()
    return template.format(
        price=price_range,
        city=city,
        cat=first_category,
        rating=rating,
    )


def make_coordinates(city):
    lat, lon = CITIES[city]
    return (
        round(lat + random.uniform(-0.04, 0.04), 6),
        round(lon + random.uniform(-0.04, 0.04), 6),
    )


def generate_restaurants():
    rows = []
    used_names = set()
    city_names = list(CITIES.keys())

    for i in range(1, NUM_RESTAURANTS + 1):
        cuisine = random.choice(CUISINES)
        city = random.choice(city_names)
        price_range = random.choices(
            PRICE_RANGES,
            weights=CUISINE_PRICE_WEIGHTS[cuisine],
            k=1,
        )[0]
        rating = make_rating()
        review_count = make_review_count(rating, price_range)
        categories = pick_categories(cuisine)
        latitude, longitude = make_coordinates(city)

        rows.append(
            {
                "restaurant_id": f"R{i:03d}",
                "name": make_name(cuisine, used_names),
                "cuisine": cuisine,
                "categories": categories,
                "description": make_description(
                    cuisine, city, price_range, rating, categories
                ),
                "price_range": price_range,
                "rating": rating,
                "review_count": review_count,
                "city": city,
                "latitude": latitude,
                "longitude": longitude,
            }
        )

    return pd.DataFrame(rows)


def main():
    df = generate_restaurants()

    # data/ sits at the project root, two folders above this script.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    output_path = os.path.join(data_dir, "restaurants.csv")
    df.to_csv(output_path, index=False)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.width", 200)
    print(df.head().to_string(index=False))
    print(f"\nDataset shape: {df.shape}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
