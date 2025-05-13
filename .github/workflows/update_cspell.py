import json
import os
import requests

# Environment variable for organization name and token
ORG_NAME = os.getenv("ORG_NAME", "unknown")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", None)
IGNORE_FILE_PATH = os.getenv("IGNORE_FILE_PATH", None)

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
    Splits full names into individual words.
    """
    words = set()
    for member in members:
        username = member
        full_name = get_user_name(username)
        if full_name:
            # Split full name into individual words
            name_parts = full_name.split()
            words.update(name_parts)
    return words

def write_ignore_file(words):
    """
    Writes the ignore words to the temporary ignore file.
    """
    if not IGNORE_FILE_PATH:
        print("IGNORE_FILE_PATH is not set. Exiting.")
        return

    with open(IGNORE_FILE_PATH, "w") as file:
        file.write("\n".join(sorted(words)))
    print(f"Ignore words written to {IGNORE_FILE_PATH}")

def main():
    if not AUTH_TOKEN:
        print("AUTH_TOKEN is not set. Skipping member fetching and processing.")
        return

    # Fetch organization members
    members = fetch_members()
    if not members:
        print("No members fetched.")
        return

    # Extract words and write to ignore file
    words = extract_words(members)
    if words:
        write_ignore_file(words)
    else:
        print("No words to write to ignore file.")

if __name__ == "__main__":
    main()
