from openai import AzureOpenAI
from httpx import Client
from string import Template
from pathlib import Path
import argparse
import os
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--src_dir", type=str, help="Directory containing markdown source files"
)
parser.add_argument(
    "--dst_file", type=str, help="A json filepath where to write the result"
)
parser.add_argument(
    "--count", type=int, help="Number of questions in the document.", default=10
)


prompt = Template(
    """TITLE: $TITLE
CONTENT: $CONTENT
NUM_DIFFERENT_QUESTIONS: $N_QUESTION
---
"""
)

response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "QAList",
        "schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "answer": {"type": "string"},
                            "title": {"type": "string"},
                        },
                        "required": ["question", "answer", "title"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["items"],
            "additionalProperties": False,
        },
    },
}


def main(src_dir: str, dst_file: str, count: int):
    azure_openai = AzureOpenAI(
        azure_endpoint=os.getenv(
            "AZURE_OPENAI_ENDPOINT", "https://indus.api.michelin.com/aicp-openai-gpt"
        ),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        http_client=Client(verify=False),
    )
    model_name = os.getenv("AZURE_OPENAI_MODELNAME", "gpt-4o-mini")
    questions = []
    for filename in Path(src_dir).rglob("*.md"):
        with open(filename, "r") as f:
            content = f.read()
            title = filename.stem
            prompt_str = prompt.substitute(
                TITLE=title, CONTENT=content, N_QUESTION=count
            )
            messages = [
                {
                    "role": "assistant",
                    "content": """You generate a set of question and answers based on the user query.
                    - You respect the number of questions/answers required by the user.
                    - You fill the title of the document
                    - Question are technical questions about the content of the document, and not the document itself.
                    - Questions and Answers are written in english

                    For example : 
                    TITLE: How to change a tire
                    CONTENT: <Content of the document>
                    NUM_DIFFERENT_QUESTIONS: 3
                    ---

                    """,
                },
                {"role": "user", "content": prompt_str},
            ]
            # We query openai API
            response = azure_openai.chat.completions.create(
                model=model_name,
                messages=messages,
                response_format=response_format,
            )
            json_dict = json.loads(response.choices[0].message.content)
            questions.extend(json_dict["items"])

            logger.info(f"Generated questions for {filename}")

        with open(dst_file, "w", encoding="utf-8") as f:
            json.dump(questions, f, indent=4)
            logger.info(f"Questions written to {dst_file}")


if __name__ == "__main__":
    args = vars(parser.parse_args())
    [print(f"{k}:{v}") for k, v in args.items()]
    main(**args)
