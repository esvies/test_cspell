import json
import os
import re
import requests

# Environment variable for organization name and token
ORG_NAME = os.getenv("ORG_NAME", "unknown")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", None)  # Check for AUTH_TOKEN

CSPELL_FILE = "cspell.json"

def fetch_members():
    """
    Fetches organization members from the GitHub API and returns them as a list of dictionaries.
    """
    if not AUTH_TOKEN:
        print("AUTH_TOKEN is not set. Skipping member fetching and processing.")
        return []

    url = f"https://api.github.com/orgs/{ORG_NAME}/members"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    print(f"Fetching members from organization: {ORG_NAME}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Failed to fetch members. HTTP Status: {response.status_code}")
        return []

    members = response.json()
    print(f"Fetched {len(members)} members.")
    return members

def process_login(username):
    """
    Splits the username by dashes, removes any suffix starting with an underscore,
    and returns the resulting words.
    """
    username = re.sub(r"_.*$", "", username)  # Remove any suffix starting with an underscore
    split_names = username.split("-")  # Split the username by dashes
    return [name for name in split_names if name]

def extract_words(members):
    """
    Extracts words from the 'login' field of each member, processes them, and returns a set of unique words.
    """
    words = set()
    for member in members:
        username = member.get("login", "")
        processed_words = process_login(username)
        print(f"Processed username '{username}' into words: {processed_words}")
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
    if not AUTH_TOKEN:
        print("AUTH_TOKEN is not set. Skipping member fetching and processing.")
        return

    # Fetch members from the GitHub API
    members = fetch_members()
    if not members:
        print("No members fetched. Exiting.")
        return

    # Process members and update cspell.json
    words = extract_words(members)
    update_cspell(words)

if __name__ == "__main__":
    main()
