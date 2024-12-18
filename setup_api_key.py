import os


def replace_placeholder(file_path, placeholder, new_value):
    """
    Replace all occurrences of a placeholder in a file with a new value.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        updated_content = content.replace(placeholder, new_value)

        with open(file_path, 'w') as file:
            file.write(updated_content)

        print(f"Updated {placeholder} in {file_path}")
    except Exception as e:
        print(f"Failed to update {file_path}: {e}")


def main():
    files_and_placeholders = [
        ("autogpt/.env", "GLOBAL-API-KEY-PLACEHOLDER"),
        ("run.sh", "GLOBAL-API-KEY-PLACEHOLDER"),
    ]
    if os.path.exists("openai_token.txt"):
        with open("openai_token.txt") as ott:
            replacement_value = ott.read()
        if replacement_value.startswith("sk-"):
            # Replace placeholders in files
            for file_path, placeholder in files_and_placeholders:
                replace_placeholder(file_path, placeholder, replacement_value)
            return
        print("OpenAI token value in `openai_token.txt` is invalid: does not start with 'sk-'.")

    else:
        print("OpenAI API-KEY not found: `openai_token.txt` not found.")
    print("Please provide your OpenAI API-KEY. (It will be saved to 'openai_token.txt')")
    replacement_value = input("OpenAI API-KEY: ").strip()
    if not replacement_value.startswith("sk-"):
        raise ValueError("Invalid OpenAI API-KEY: must start with 'sk-'")
    # Save the replacement value to token.txt
    with open("openai_token.txt", "w") as token_file:
        token_file.write(replacement_value)
    for file_path, placeholder in files_and_placeholders:
        replace_placeholder(file_path, placeholder, replacement_value)


if __name__ == "__main__":
    main()
