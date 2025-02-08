import os
import argparse
import requests
import json
from dotenv import load_dotenv, find_dotenv


def load_env():
    _ = load_dotenv(find_dotenv())


def make_request(url, data, headers, verbose=False):
    if verbose:
        print(f"Request URL: {url}")
        print(f"Request Data: {json.dumps(data, indent=4)}")

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if verbose:
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {response.text}")

    return response


def print_result(message, response):
    if response.status_code == 200:
        print(f"✅ {message}")
    else:
        print(f"❌ {message} (Status code: {response.status_code})")


def run_test(api_base, api_version, api_key, model, verbose):

    print(f"Running test for model: {model}")
    # print(f"API base: {api_base}")
    # print(f"API version: {api_version}")

    # 0. common
    url = f"{api_base}/openai/deployments/{model}/chat/completions?api-version={api_version}"
    headers = {"Content-Type": "application/json", "api-key": api_key}

    common_data = {
        "temperature": 0.7,
        "top_p": 0.95,
        # "max_tokens": 800
    }

    # print(f"URL: {url}")

    # 1. chat request: should always work !
    data = {
        **common_data,
        "messages": [
            {"role": "system", "content": "You are an helpful assistant."},
            {"role": "user", "content": "Good day, who am I talking to?"},
        ],
    }
    response = make_request(url, data, headers, verbose)
    print_result("Chat Request", response)

    # 2. structured output request: should work if the model is recent enough
    data = {
        **common_data,
        "messages": [{"role": "user", "content": "solve 8x + 31 = 2"}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "math_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "explanation": {"type": "string"},
                                    "output": {"type": "string"},
                                },
                                "required": ["explanation", "output"],
                                "additionalProperties": False,
                            },
                        },
                        "final_answer": {"type": "string"},
                    },
                    "required": ["steps", "final_answer"],
                    "additionalProperties": False,
                },
            },
        },
    }
    response = make_request(url, data, headers, verbose)
    print_result("Structured Output Request", response)

    # 3. tool calling request: should always work
    data = {
        **common_data,
        "messages": [{"role": "user", "content": "What is the weather in Paris?"}],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and country, e.g., Paris, France",
                            },
                            "format": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                            },
                        },
                        "required": ["location", "format"],
                    },
                },
            }
        ],
        "tool_choice": "auto",
    }
    response = make_request(url, data, headers, verbose)
    print_result("Tool Calling Request", response)


if __name__ == "__main__":

    load_env()
    api_base = os.getenv("AZURE_ENDPOINT")
    api_version = os.getenv("AZURE_API_VERSION")
    api_key = os.getenv("AZURE_API_KEY")

    assert api_base, "Error: AZURE_ENDPOINT must be set in environment variables."
    assert api_version, "Error: AZURE_API_VERSION must be set in environment variables."
    assert api_key, "Error: AZURE_API_KEY must be set in environment variables."

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.model == "all":
        models = [
            "Dalle3",
            "GPT-4-Turbo",
            "Text-Embedding-Ada-002",
            "gpt-4o",
            "gpt-4o-mini",
            "o1",
            "o1-mini",
            "text-embedding-3-large",
            "whisper",
            "Meta Llama3 8b",
            "Meta Llama3 90b",
            "Mistral 7b",
        ]
        for model in models:
            run_test(api_base, api_version, api_key, model, args.verbose)
    else:
        run_test(api_base, api_version, api_key, args.model, args.verbose)
