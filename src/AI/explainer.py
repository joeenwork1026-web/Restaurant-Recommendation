"""Generate natural-language explanations for recommendations."""

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


api_key = os.getenv("DASHSCOPE_API_KEY")

if not api_key:
    raise ValueError(
        "DASHSCOPE_API_KEY was not found."
    )


client = OpenAI(
    api_key=api_key,
    base_url="https://maas.qwencloudapi.com/compatible-mode/v1",
)


def explain_recommendation(
    user_request,
    restaurant,
):
    prompt = f"""
The user asked:

"{user_request}"

We recommended this restaurant:

Name: {restaurant["name"]}
Cuisine: {restaurant["cuisine"]}
City: {restaurant["city"]}
Price range: {restaurant["price_range"]}
Rating: {restaurant["rating"]}
Review count: {restaurant["review_count"]}

Explain in 1-2 short sentences why this restaurant
matches the user's request.

Only mention facts provided above.
Do not invent information.
"""

    response = client.chat.completions.create(
        model="qwen3.7-flash",
        messages=[
            {
                "role": "system",
                "content": (
                    "You explain restaurant recommendations "
                    "clearly and concisely."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.choices[0].message.content


def main():
    user_request = (
        "I want a cheap Japanese restaurant "
        "in Kuala Lumpur with good ratings."
    )

    restaurant = {
        "name": "Hana Kitchen",
        "cuisine": "Japanese",
        "city": "Kuala Lumpur",
        "price_range": "$",
        "rating": 4.1,
        "review_count": 307,
    }

    explanation = explain_recommendation(
        user_request,
        restaurant,
    )

    print(explanation)


if __name__ == "__main__":
    main()