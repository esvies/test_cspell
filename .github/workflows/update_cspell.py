import json
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Environment variables
ORG_NAME = os.getenv("ORG_NAME", "unknown")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", None)
IGNORE_FILE_PATH = os.getenv("IGNORE_FILE_PATH", None)

CSPELL_FILE = "cspell.json"

def fetch_members():
    """
    Fetches organization members from the GitHub API and returns them as a list of usernames.
    """
    if not AUTH_TOKEN:
        logger.warning("AUTH_TOKEN is not set. Skipping member fetching and processing.")
        return []

    url = f"https://api.github.com/orgs/{ORG_NAME}/members"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    logger.info(f"Fetching members from organization: {ORG_NAME}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to fetch members. HTTP Status: {response.status_code}")
        return []

    logger.info(f"Successfully fetched {len(response.json())} members.")
    return [member.get("login", "") for member in response.json()]

def get_user_name(username):
    """
    Retrieves the full name of the user via the GitHub API.
    """
    if not AUTH_TOKEN:
        logger.warning("AUTH_TOKEN is not set. Skipping user name fetching.")
        return None

    url = f"https://api.github.com/users/{username}"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    logger.info(f"Fetching full name for user: {username}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to fetch user data for {username}. HTTP Status: {response.status_code}")
        return None

    user_data = response.json()
    full_name = user_data.get("name")
    if full_name:
        logger.info(f"Full name for user {username}: {full_name}")
    else:
        logger.warning(f"No full name found for user {username}.")
    return full_name

def extract_words(members):
    """
    Extracts names from the organization members and returns a set of unique words.
    """
    logger.info("Extracting words from member names.")
    words = set()
    for member in members:
        username = member
        full_name = get_user_name(username)
        if full_name:
            words.update(full_name.split())
    logger.info(f"Extracted {len(words)} unique words from member names.")
    return words

def get_existing_ignore_words():
    """
    Reads the existing ignoreWords from the main cspell.json file.
    """
    if not os.path.exists(CSPELL_FILE):
        logger.warning(f"{CSPELL_FILE} does not exist. Proceeding with an empty ignoreWords list.")
        return set()

    logger.info(f"Reading existing ignoreWords from {CSPELL_FILE}.")
    with open(CSPELL_FILE, "r") as file:
        try:
            data = json.load(file)
            ignore_words = set(data.get("ignoreWords", []))
            logger.info(f"Found {len(ignore_words)} existing ignoreWords.")
            return ignore_words
        except json.JSONDecodeError:
            logger.error(f"Error parsing {CSPELL_FILE}. Proceeding with an empty ignoreWords list.")
            return set()

def write_ignore_config(words):
    """
    Writes the combined ignore words to a temporary cspell.json config file.
    """
    if not IGNORE_FILE_PATH:
        logger.error("IGNORE_FILE_PATH is not set. Exiting.")
        return

    existing_words = get_existing_ignore_words()
    combined_words = sorted(existing_words.union(words))

    config = {
        "version": "0.2",
        "language": "en",
        "ignorePaths": [".devcontainer/**", ".vscode/**", ".github/**"],
        "ignoreWords": combined_words
    }

    logger.info(f"Writing ignore config to {IGNORE_FILE_PATH}.")
    with open(IGNORE_FILE_PATH, "w") as file:
        json.dump(config, file, indent=2)

    logger.info(f"Ignore config successfully written to {IGNORE_FILE_PATH}.")

def main():
    if not AUTH_TOKEN:
        logger.error("AUTH_TOKEN is not set. Skipping member fetching and processing.")
        return

    logger.info("Starting the process to generate cspell ignore config.")
    members = fetch_members()
    if not members:
        logger.warning("No members fetched. Exiting.")
        return

    words = extract_words(members)
    if words:
        write_ignore_config(words)
    else:
        logger.warning("No words to write to ignore config.")

    logger.info("Process completed successfully.")

if __name__ == "__main__":
    main()
