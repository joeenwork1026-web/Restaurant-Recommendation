"""Evaluation metrics and evaluation pipeline."""

import os
import pandas as pd

from src.recommendation.popularity import get_popular_restaurants
from src.recommendation.content_based import (
    recommend_for_user as content_recommend,
)
from src.recommendation.collaborative import (
    recommend_for_user as collaborative_recommend,
)
from src.recommendation.hybrid import (
    recommend_for_user as hybrid_recommend,
)


POSITIVE_EVENTS = {
    "like",
    "save",
    "visit",
    "rating",
}


def project_paths():
    """Return the path to the project's data directory."""

    script_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    project_root = os.path.abspath(
        os.path.join(
            script_dir,
            "..",
            "..",
        )
    )

    return os.path.join(
        project_root,
        "data",
    )


def split_interactions(
    interactions,
    test_ratio=0.2,
):
    """Split each user's interactions chronologically."""

    train_parts = []
    test_parts = []

    for user_id, user_data in interactions.groupby(
        "user_id"
    ):

        user_data = user_data.sort_values(
            "timestamp"
        )

        split_index = int(
            len(user_data)
            * (1 - test_ratio)
        )

        split_index = max(
            1,
            min(
                split_index,
                len(user_data) - 1,
            ),
        )

        train_parts.append(
            user_data.iloc[:split_index]
        )

        test_parts.append(
            user_data.iloc[split_index:]
        )

    train = pd.concat(
        train_parts
    ).reset_index(drop=True)

    test = pd.concat(
        test_parts
    ).reset_index(drop=True)

    return train, test


def recall_at_k(
    recommended_ids,
    relevant_ids,
    k=10,
):
    """Calculate Recall@K."""

    recommended_ids = recommended_ids[:k]
    relevant_ids = set(relevant_ids)

    if not relevant_ids:
        return 0.0

    hits = sum(
        1
        for restaurant_id in recommended_ids
        if restaurant_id in relevant_ids
    )

    return hits / len(relevant_ids)


def precision_at_k(
    recommended_ids,
    relevant_ids,
    k=10,
):
    """Calculate Precision@K."""

    recommended_ids = recommended_ids[:k]
    relevant_ids = set(relevant_ids)

    if not recommended_ids:
        return 0.0

    hits = sum(
        1
        for restaurant_id in recommended_ids
        if restaurant_id in relevant_ids
    )

    return hits / len(recommended_ids)


def ndcg_at_k(
    recommended_ids,
    relevant_ids,
    k=10,
):
    """Calculate binary NDCG@K."""

    import math

    recommended_ids = recommended_ids[:k]
    relevant_ids = set(relevant_ids)

    if not relevant_ids:
        return 0.0

    dcg = 0.0

    for position, restaurant_id in enumerate(
        recommended_ids,
        start=1,
    ):

        if restaurant_id in relevant_ids:

            dcg += (
                1
                / math.log2(position + 1)
            )

    ideal_hits = min(
        len(relevant_ids),
        k,
    )

    idcg = sum(
        1
        / math.log2(position + 1)
        for position in range(
            1,
            ideal_hits + 1,
        )
    )

    if idcg == 0:
        return 0.0

    return dcg / idcg


def get_test_relevant_items(
    test_interactions,
    user_id,
):
    """
    Get positive interactions from the test set.

    These events are considered meaningful:
        like
        save
        visit
        rating
    """

    user_test = test_interactions[
        (
            test_interactions["user_id"]
            == user_id
        )
        & (
            test_interactions["event_type"]
            .isin(POSITIVE_EVENTS)
        )
    ]

    return user_test[
        "restaurant_id"
    ].tolist()


def get_recommendation_ids(
    user_id,
    model,
    train_interactions,
    top_k=10,
):
    """Generate recommendation IDs."""

    if model == "popularity":

        recommendations = (
            get_popular_restaurants(
                top_k=top_k,
                interactions=train_interactions,
            )
        )

        return recommendations[
            "restaurant_id"
        ].tolist()

    if model == "content":

        recommendations = content_recommend(
            user_id,
            top_k=top_k,
            interactions=train_interactions,
        )

        return recommendations[
            "restaurant_id"
        ].tolist()

    if model == "collaborative":

        recommendations = (
            collaborative_recommend(
                user_id,
                top_k=top_k,
                interactions=train_interactions,
            )
        )

        return recommendations[
            "restaurant_id"
        ].tolist()

    if model == "hybrid":

        recommendations = hybrid_recommend(
            user_id,
            top_k=top_k,
            interactions=train_interactions,
        )

        return recommendations[
            "restaurant_id"
        ].tolist()

    raise ValueError(
        f"Unknown model: {model}"
    )


def evaluate_model(
    model,
    train_interactions,
    test_interactions,
    k=10,
):
    """Evaluate one recommendation model."""

    users = test_interactions[
        "user_id"
    ].unique()

    recall_scores = []
    precision_scores = []
    ndcg_scores = []

    users_with_positive_items = 0
    users_with_recommendations = 0

    total_positive_items = 0
    total_hits = 0

    for user_id in users:

        recommended_ids = (
            get_recommendation_ids(
                user_id,
                model,
                train_interactions,
                top_k=k,
            )
        )

        relevant_ids = (
            get_test_relevant_items(
                test_interactions,
                user_id,
            )
        )

        # Skip users who don't have a
        # positive interaction in the test set.
        if not relevant_ids:
            continue

        users_with_positive_items += 1

        total_positive_items += len(
            set(relevant_ids)
        )

        if recommended_ids:
            users_with_recommendations += 1

        recommended_set = set(
            recommended_ids[:k]
        )

        relevant_set = set(
            relevant_ids
        )

        hits = len(
            recommended_set
            & relevant_set
        )

        total_hits += hits

        recall_scores.append(
            recall_at_k(
                recommended_ids,
                relevant_ids,
                k=k,
            )
        )

        precision_scores.append(
            precision_at_k(
                recommended_ids,
                relevant_ids,
                k=k,
            )
        )

        ndcg_scores.append(
            ndcg_at_k(
                recommended_ids,
                relevant_ids,
                k=k,
            )
        )

    if not recall_scores:

        return {
            f"recall@{k}": 0.0,
            f"precision@{k}": 0.0,
            f"ndcg@{k}": 0.0,
        }

    return {
        f"recall@{k}": (
            sum(recall_scores)
            / len(recall_scores)
        ),

        f"precision@{k}": (
            sum(precision_scores)
            / len(precision_scores)
        ),

        f"ndcg@{k}": (
            sum(ndcg_scores)
            / len(ndcg_scores)
        ),

        "_users_evaluated": (
            users_with_positive_items
        ),

        "_users_with_recommendations": (
            users_with_recommendations
        ),

        "_positive_items": (
            total_positive_items
        ),

        "_hits": total_hits,
    }


def print_collaborative_diagnostics(
    train_interactions,
    test_interactions,
):
    """
    Print diagnostics specifically for
    collaborative filtering.
    """

    users = test_interactions[
        "user_id"
    ].unique()

    users_with_positive_items = 0
    users_with_recommendations = 0

    total_positive_items = 0
    total_recommendation_items = 0
    total_hits = 0

    for user_id in users:

        relevant_ids = (
            get_test_relevant_items(
                test_interactions,
                user_id,
            )
        )

        if not relevant_ids:
            continue

        users_with_positive_items += 1

        relevant_set = set(
            relevant_ids
        )

        total_positive_items += len(
            relevant_set
        )

        recommended_ids = (
            get_recommendation_ids(
                user_id,
                "collaborative",
                train_interactions,
                top_k=10,
            )
        )

        if recommended_ids:
            users_with_recommendations += 1

        total_recommendation_items += len(
            recommended_ids
        )

        hits = len(
            set(recommended_ids)
            & relevant_set
        )

        total_hits += hits

    print()
    print(
        "Collaborative Filtering Diagnostics"
    )
    print("=" * 50)

    print(
        f"Users with positive test items: "
        f"{users_with_positive_items}"
    )

    print(
        f"Users with recommendations: "
        f"{users_with_recommendations}"
    )

    print(
        f"Total positive test items: "
        f"{total_positive_items}"
    )

    print(
        f"Total recommendation items: "
        f"{total_recommendation_items}"
    )

    print(
        f"Total recommendation hits: "
        f"{total_hits}"
    )

    if total_positive_items > 0:

        coverage = (
            total_hits
            / total_positive_items
        )

        print(
            f"Positive-item hit coverage: "
            f"{coverage:.4f}"
        )


def evaluate_all_models(
    interactions,
    test_ratio=0.2,
    k=10,
):
    """Evaluate all recommendation models."""

    train, test = split_interactions(
        interactions,
        test_ratio=test_ratio,
    )

    models = [
        "popularity",
        "content",
        "collaborative",
        "hybrid",
    ]

    results = []

    for model in models:

        metrics = evaluate_model(
            model,
            train,
            test,
            k=k,
        )

        row = {
            "model": model,
            f"recall@{k}": metrics[
                f"recall@{k}"
            ],
            f"precision@{k}": metrics[
                f"precision@{k}"
            ],
            f"ndcg@{k}": metrics[
                f"ndcg@{k}"
            ],
        }

        results.append(row)

    return (
        pd.DataFrame(results),
        train,
        test,
    )


def main():
    """Run the complete evaluation."""

    data_dir = project_paths()

    interactions = pd.read_csv(
        os.path.join(
            data_dir,
            "interactions.csv",
        )
    )

    (
        results,
        train,
        test,
    ) = evaluate_all_models(
        interactions,
        test_ratio=0.2,
        k=10,
    )

    print()

    print(
        "Recommendation Model Evaluation"
    )

    print("=" * 50)

    print(
        results.to_string(
            index=False
        )
    )

    print_collaborative_diagnostics(
        train,
        test,
    )


if __name__ == "__main__":
    main()