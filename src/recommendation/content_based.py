"""Content-based restaurant recommendations with TF-IDF.

What TF-IDF does
----------------
Restaurants are turned into text by joining cuisine, categories, and
description. TF-IDF then turns that text into numbers.

- TF (term frequency): a word that appears often in this restaurant's
  text gets a higher score for this restaurant.
- IDF (inverse document frequency): a word that appears in almost every
  restaurant (like "in" or "city") is down-weighted, because it does not
  help us tell restaurants apart.

The result is a vector for each restaurant. Nearby numbers mean similar
wording / cuisine / dishes.

What cosine similarity does
---------------------------
Cosine similarity compares two vectors by the angle between them, not
by how long they are. Score 1 means "same direction" (very similar
content). Score 0 means "no overlap in important words". We rank
restaurants by this score.

How the user profile is constructed
-----------------------------------
We do not store a separate profile file. For a user, we take every
restaurant they already interacted with, look up those restaurants'
TF-IDF vectors, and average them. That average vector is the user
profile: a summary of "what this person has already shown interest in".

How recommendations are generated
---------------------------------
1. Similar restaurants: cosine similarity of one restaurant vs all
   others, drop itself, return the top K.
2. For a user: cosine similarity of the user profile vs all restaurants,
   drop places they already interacted with, return the top K.
"""

import os

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def project_paths():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    return os.path.join(project_root, "data")


def prepare():
    """Load CSVs and build the TF-IDF matrix used by both recommenders."""
    data_dir = project_paths()
    restaurants = pd.read_csv(os.path.join(data_dir, "restaurants.csv"))
    interactions = pd.read_csv(os.path.join(data_dir, "interactions.csv"))

    restaurants["content_text"] = (
        restaurants["cuisine"].fillna("")
        + " "
        + restaurants["categories"].fillna("")
        + " "
        + restaurants["description"].fillna("")
    )

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(restaurants["content_text"])

    id_to_index = {
        restaurant_id: i
        for i, restaurant_id in enumerate(restaurants["restaurant_id"])
    }

    return restaurants, interactions, tfidf_matrix, id_to_index


def get_similar_restaurants(restaurant_id, top_k=10):
    """Return the restaurants with the most similar content."""
    restaurants, _, tfidf_matrix, id_to_index = prepare()

    if restaurant_id not in id_to_index:
        raise ValueError(f"Unknown restaurant_id: {restaurant_id}")

    index = id_to_index[restaurant_id]
    scores = cosine_similarity(tfidf_matrix[index], tfidf_matrix).flatten()

    similar = restaurants.copy()
    similar["similarity"] = scores
    similar = similar[similar["restaurant_id"] != restaurant_id]
    similar = similar.sort_values("similarity", ascending=False)
    return similar.head(top_k).reset_index(drop=True)


def recommend_for_user(user_id, top_k=10):
    """Recommend new restaurants from the user's interaction history."""
    restaurants, interactions, tfidf_matrix, id_to_index = prepare()

    seen_ids = interactions.loc[
        interactions["user_id"] == user_id, "restaurant_id"
    ].unique()

    if len(seen_ids) == 0:
        raise ValueError(f"No interactions found for user_id: {user_id}")

    seen_indexes = [id_to_index[rid] for rid in seen_ids if rid in id_to_index]
    if len(seen_indexes) == 0:
        raise ValueError(f"No matching restaurants found for user_id: {user_id}")

    # Average TF-IDF vectors of restaurants this user already touched.
    user_profile = np.asarray(tfidf_matrix[seen_indexes].mean(axis=0))
    scores = cosine_similarity(user_profile, tfidf_matrix).flatten()

    ranked = restaurants.copy()
    ranked["similarity"] = scores
    ranked = ranked[~ranked["restaurant_id"].isin(seen_ids)]
    ranked = ranked.sort_values("similarity", ascending=False)
    return ranked.head(top_k).reset_index(drop=True)


def main():
    columns = ["restaurant_id", "name", "cuisine", "rating", "similarity"]

    print("Restaurants similar to R001:")
    print(get_similar_restaurants("R001", top_k=10)[columns].to_string(index=False))

    print("\nRecommendations for user U001:")
    print(recommend_for_user("U001", top_k=10)[columns].to_string(index=False))


if __name__ == "__main__":
    main()
