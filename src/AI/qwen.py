"""Qwen restaurant preference extraction."""

import json
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


def extract_preferences(user_request):
    response = client.chat.completions.create(
        model="qwen3.7-flash",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract restaurant preferences from the user. "
                    "Return ONLY valid JSON with these fields: "
                    "cuisine, city, price_range, minimum_rating. "
                    "Use null when a value is not specified. "
                    "price_range must be one of: $, $$, $$$, $$$$."
                ),
            },
            {
                "role": "user",
                "content": user_request,
            },
        ],
        response_format={
            "type": "json_object"
        },
    )

    content = response.choices[0].message.content

    return json.loads(content)


def main():
    user_request = (
        "I want a cheap Japanese restaurant in Kuala Lumpur "
        "with good ratings."
    )

    preferences = extract_preferences(user_request)

    print(preferences)


if __name__ == "__main__":
    main()