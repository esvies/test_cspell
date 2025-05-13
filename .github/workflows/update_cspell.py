import json
import os
import requests

# Environment variable for organization name and token
ORG_NAME = os.getenv("ORG_NAME", "unknown")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", None)

CSPELL_FILE = "cspell.json"

def ensure_cspell_exists():
    """
    Ensures that the cspell.json file exists. If not, it creates it with default content.
    """
    if not os.path.exists(CSPELL_FILE):
        print("cspell.json not found. Creating default cspell.json...")
        cspell_data = {
            "version": "0.2",
            "language": "en",
            "ignorePaths": [".devcontainer/**", ".vscode/**", ".github/**"],
            "ignoreWords": []
        }
        with open(CSPELL_FILE, "w") as file:
            json.dump(cspell_data, file, indent=2)
        print("Default cspell.json created.")
    else:
        print("cspell.json already exists.")

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

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Failed to fetch members. HTTP Status: {response.status_code}")
        return []

    return response.json()

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

def extract_words(members, existing_words):
    """
    Extracts names from the organization members and returns a set of unique words.
    Splits full names into individual words and ensures they are not already present in cspell.json.
    """
    words = set()
    for member in members:
        username = member.get("login", "")
        full_name = get_user_name(username)
        if full_name:
            # Split full name into individual words
            name_parts = full_name.split()
            for part in name_parts:
                if part not in existing_words:
                    print(f"Adding {part} to ignore words")
                    words.add(part)
    return words

def update_cspell(words):
    """
    Updates the cspell.json file by adding new words to the 'ignoreWords' list.
    """
    with open(CSPELL_FILE, "r") as file:
        cspell_data = json.load(file)

    existing_words = set(cspell_data.get("ignoreWords", []))
    new_words = words - existing_words

    if new_words:
        print(f"Adding {len(new_words)} new words to cspell.json: {new_words}")
        # Update the ignoreWords list
        updated_words = sorted(existing_words.union(new_words))
        cspell_data["ignoreWords"] = updated_words

        with open(CSPELL_FILE, "w") as file:
            json.dump(cspell_data, file, indent=2)
        print("cspell.json updated successfully.")
    else:
        print("No new words to add or no new members found.")

def main():
    if not AUTH_TOKEN:
        print("AUTH_TOKEN is not set. Skipping member fetching and processing.")
        return

    # Ensure cspell.json exists
    ensure_cspell_exists()

    # Load existing words
    with open(CSPELL_FILE, "r") as file:
        cspell_data = json.load(file)
        existing_words = set(cspell_data.get("ignoreWords", []))

    # Fetch organization members
    members = fetch_members()
    if not members:
        print("No members fetched. Exiting.")
        return

    # Extract words and update cspell.json
    words = extract_words(members, existing_words)
    if not words:
        print("No new members found or no new words to add to cspell.json.")
        return

    update_cspell(words)

if __name__ == "__main__":
    main()
