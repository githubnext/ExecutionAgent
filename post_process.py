import os
import json
import sys
import argparse

import warnings
warnings.filterwarnings("ignore")

import openai

def ask_chatgpt(query, system_message, model="gpt-4"):
    # Read the OpenAI API token from a file
    with open("openai_token.txt") as opt:
        token = opt.read().strip()

    # Set up the OpenAI API key
    openai.api_key = token

    # Construct the messages for the Chat Completion API
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query}
    ]

    # Call the OpenAI API for chat completion
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )

    # Extract and return the content of the assistant's response
    return response["choices"][0]["message"]["content"]

def main():
    if len(sys.argv) != 2:
        print("Usage: python post_process.py <project_name>")
        sys.exit(1)

    project_name = sys.argv[1]

    # Read the last line of experiments_list.txt
    experiments_file = "experimental_setups/experiments_list.txt"
    if not os.path.exists(experiments_file):
        print(f"Error: {experiments_file} does not exist.")
        sys.exit(1)

    with open(experiments_file, 'r') as f:
        lines = f.readlines()
        if not lines:
            print(f"Error: {experiments_file} is empty.")
            sys.exit(1)
        last_line = lines[-1].strip()

    # Build paths
    success_file = f"experimental_setups/{last_line}/saved_contexts/{project_name}/SUCCESS"

    if os.path.exists(success_file):
        print("SUCCESS")
        return

    # Find the cycle_XX file with the highest XX
    contexts_dir = f"experimental_setups/{last_line}/saved_contexts/{project_name}"
    if not os.path.exists(contexts_dir):
        print(f"Error: {contexts_dir} does not exist.")
        sys.exit(1)

    cycle_files = [f for f in os.listdir(contexts_dir) if f.startswith("cycle_") and f[6:].isdigit()]
    if not cycle_files:
        print(f"Error: No cycle files found in {contexts_dir}.")
        sys.exit(1)

    latest_cycle_file = max(cycle_files, key=lambda x: int(x[6:]))
    latest_cycle_path = os.path.join(contexts_dir, latest_cycle_file)

    # Read the JSON content of the latest cycle file
    with open(latest_cycle_path, 'r') as f:
        try:
            file_content = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {latest_cycle_path}.")
            sys.exit(1)

    # Extract the desired content
    try:
        extracted_content = file_content["steps_object"]["1"]["result_of_step"]
    except KeyError as e:
        print(f"Error: Missing key in JSON structure: {e}")
        sys.exit(1)

    # Prepare the query for ask_chatgpt
    query = (
        f"the following would represent the sequence of commands and reasoning made by an LLM trying to install \"{project_name}\" project from source code and execute test cases. "
        "I want you to summarize the encountered problems and give advice for next attempt. Be precise and concise. Address the most important and critical issues (ignore non critical warnings and so). Your response should have one header: ### Feedback from previous installation attempts\n"
        f"+ {extracted_content}"
    )
    
    system_message = (
        "You are a helpful software engineering assistant with capabilities of installing, building, configuring, and testing software projects."
    )

    # Call ask_chatgpt
    response = ask_chatgpt(query, system_message)

    # Save the response to problems_memory/{project_name}
    problems_memory = f"problems_memory/{project_name}"
    with open(problems_memory, 'w') as f:
        f.write(response)

    # Print FAILURE
    print("FAILURE")

if __name__ == "__main__":
    main()
