import json
import os
import requests

# Environment variable for organization name and token
ORG_NAME = os.getenv("ORG_NAME", "unknown")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", None)
IGNORE_FILE_PATH = os.getenv("IGNORE_FILE_PATH", None)

CSPELL_FILE = "cspell.json"

def fetch_members():
    """
    Fetches organization members from the GitHub API and returns them as a list of usernames.
    """
    if not AUTH_TOKEN:
        print("AUTH_TOKEN is not set. Skipping member fetching and processing.")
        return []

    url = f"https://api.github.com/orgs/{ORG_NAME}/members"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Failed to fetch members. HTTP Status: {response.status_code}")
        return []

    return [member.get("login", "") for member in response.json()]

def get_user_name(username):
    """
    Retrieves the full name of the user via the GitHub API.
    """
    if not AUTH_TOKEN:
        return None

    url = f"https://api.github.com/users/{username}"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Failed to fetch user data for {username}. HTTP Status: {response.status_code}")
        return None

    user_data = response.json()
    return user_data.get("name")

def extract_words(members):
    """
    Extracts names from the organization members and returns a set of unique words.
    """
    words = set()
    for member in members:
        username = member
        full_name = get_user_name(username)
        if full_name:
            words.update(full_name.split())
    return words

def get_existing_ignore_words():
    """
    Reads the existing ignoreWords from the main cspell.json file.
    """
    if not os.path.exists(CSPELL_FILE):
        return set()

    with open(CSPELL_FILE, "r") as file:
        try:
            data = json.load(file)
            return set(data.get("ignoreWords", []))
        except json.JSONDecodeError:
            print("Error parsing cspell.json. Proceeding with empty ignoreWords.")
            return set()

def write_ignore_config(words):
    """
    Writes the combined ignore words to a temporary cspell config file.
    """
    if not IGNORE_FILE_PATH:
        print("IGNORE_FILE_PATH is not set. Exiting.")
        return

    existing_words = get_existing_ignore_words()
    combined_words = sorted(existing_words.union(words))

    config = {
        "version": "0.2",
        "language": "en",
        "ignorePaths": [".devcontainer/**", ".vscode/**", ".github/**"],
        "ignoreWords": combined_words
    }

    with open(IGNORE_FILE_PATH, "w") as file:
        json.dump(config, file, indent=2)
    print(f"Ignore config written to {IGNORE_FILE_PATH}")

def main():
    if not AUTH_TOKEN:
        print("AUTH_TOKEN is not set. Skipping member fetching and processing.")
        return

    members = fetch_members()
    if not members:
        print("No members fetched.")
        return

    words = extract_words(members)
    write_ignore_config(words)

if __name__ == "__main__":
    main()
