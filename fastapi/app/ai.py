from openai import OpenAI

from envs import OPENAI_API_KEY

openai_client = OpenAI(api_key=OPENAI_API_KEY)


def get_harvest(image_url: str) -> bool:
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a crop expert. Answer whether the crop in the image is ready for harvest with just 'yes' or 'no'.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Is this crop ready to harvest? Answer only 'yes' or 'no'.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    },
                ],
            },
        ],
        max_tokens=1,
    )

    answer = response.choices[0].message.content.strip().lower()
    return answer.startswith("y")
