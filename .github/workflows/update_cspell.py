import json
import os
import re  # Import the regex module

# Environment variable for organization name
ORG_NAME = os.getenv("ORG_NAME", "unknown")

MEMBERS_FILE = ".github/workflows/members.json"
CSPELL_FILE = "cspell.json"

def load_json(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            print(f"Loaded data from {file_path}: {data}")
            return data
    except json.JSONDecodeError:
        print(f"Error: Failed to parse {file_path}. Ensure it is valid JSON.")
        return []

def process_login(username):
    """
    Splits the username by dashes, removes any suffix starting with an underscore,
    and returns the resulting words.
    """
    # Remove any suffix starting with an underscore
    username = re.sub(r"_.*$", "", username)
    # Split the username by dashes
    split_names = username.split("-")
    return [name for name in split_names if name]

def extract_words(members):
    """
    Extracts words from the 'login' field of each member, processes them, and returns a set of unique words.
    """
    words = set()

    if not isinstance(members, list):
        print(f"Unexpected data type for members: {type(members)}. Expected a list.")
        return words

    for member in members:
        if not isinstance(member, dict):
            print(f"Unexpected member format: {member}")
            continue

        username = member.get("login", "")
        processed_words = process_login(username)
        words.update(processed_words)

    return words

def update_cspell(words):
    """
    Updates the cspell.json file by adding new words to the 'ignoreWords' list.
    """
    if not os.path.exists(CSPELL_FILE):
        cspell_data = {
            "version": "0.2",
            "language": "en",
            "ignorePaths": [".devcontainer/**", ".vscode/**", ".github/**"],
            "ignoreWords": []
        }
    else:
        with open(CSPELL_FILE, "r") as file:
            cspell_data = json.load(file)

    existing_words = set(cspell_data.get("ignoreWords", []))
    new_words = words - existing_words

    if new_words:
        print(f"Adding {len(new_words)} new words to cspell.json: {new_words}")
        cspell_data["ignoreWords"].extend(sorted(new_words))

        with open(CSPELL_FILE, "w") as file:
            json.dump(cspell_data, file, indent=2)
        print("cspell.json updated successfully.")
    else:
        print("No new words to add.")

def main():
    members = load_json(MEMBERS_FILE)
    words = extract_words(members)
    update_cspell(words)

if __name__ == "__main__":
    main()
