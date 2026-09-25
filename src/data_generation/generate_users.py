"""Generate a synthetic dataset of 100 restaurant-app users."""

import os
import random

import pandas as pd

random.seed(42)

NUM_USERS = 100

CITIES = [
    "Kuala Lumpur",
    "Petaling Jaya",
    "Shah Alam",
    "Johor Bahru",
    "Penang",
]

# Larger cities get more users.
CITY_WEIGHTS = [0.38, 0.22, 0.14, 0.13, 0.13]

PRICE_RANGES = ["$", "$$", "$$$", "$$$$"]


def make_age():
    """Most users are young adults or working-age adults."""
    group = random.choices(
        ["young", "adult", "mid", "older"],
        weights=[0.28, 0.42, 0.22, 0.08],
        k=1,
    )[0]

    if group == "young":
        return random.randint(18, 25)
    if group == "adult":
        return random.randint(26, 35)
    if group == "mid":
        return random.randint(36, 50)
    return random.randint(51, 65)


def make_price_range(age):
    """Younger users lean cheaper; older users lean mid-to-high."""
    if age <= 25:
        weights = [0.45, 0.40, 0.13, 0.02]
    elif age <= 35:
        weights = [0.20, 0.50, 0.25, 0.05]
    elif age <= 50:
        weights = [0.10, 0.40, 0.38, 0.12]
    else:
        weights = [0.08, 0.35, 0.40, 0.17]

    return random.choices(PRICE_RANGES, weights=weights, k=1)[0]


def generate_users():
    rows = []

    for i in range(1, NUM_USERS + 1):
        age = make_age()
        city = random.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]
        price_range = make_price_range(age)

        rows.append(
            {
                "user_id": f"U{i:03d}",
                "age": age,
                "city": city,
                "preferred_price_range": price_range,
            }
        )

    return pd.DataFrame(rows)


def main():
    df = generate_users()

    # data/ sits at the project root, two folders above this script.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    output_path = os.path.join(data_dir, "users.csv")
    df.to_csv(output_path, index=False)

    print(df.head().to_string(index=False))
    print(f"\nDataset shape: {df.shape}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
