import json
import os

MEMBERS_FILE = "members.json"
CSPELL_FILE = "cspell.json"

def load_json(file_path):
    """Load JSON data from a file."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            print(f"Loaded data from {file_path}: {data}")
            print(f"Data type: {type(data)}")
            return data
    except json.JSONDecodeError:
        print(f"Error: Failed to parse {file_path}. Ensure it is valid JSON.")
        return []

def extract_first_names(members):
    """Extract first names from GitHub usernames."""
    first_names = set()

    # Validate that members is a list
    if not isinstance(members, list):
        print(f"Unexpected data type for members: {type(members)}. Expected a list.")
        return first_names

    for member in members:
        # Ensure each member is a dictionary
        if not isinstance(member, dict):
            print(f"Unexpected member format: {member}")
            continue

        # Extract the username
        username = member.get("login", "")
        if not username:
            print(f"Member has no 'login' field: {member}")
            continue

        # Extract potential first names
        split_names = username.replace("-", " ").replace("_", " ").split()
        if split_names:
            print(f"Extracted names from username '{username}': {split_names}")
            first_names.add(split_names[0])

    print(f"Extracted first names: {first_names}")
    return first_names

def update_cspell(first_names):
    """Update cspell.json with new words."""
    # Initialize the cspell structure if file does not exist
    if not os.path.exists(CSPELL_FILE):
        print(f"{CSPELL_FILE} not found. Initializing new structure.")
        cspell_data = {
            "version": "0.2",
            "language": "en",
            "ignorePaths": [".devcontainer/**", ".vscode/**", ".github/**"],
            "ignoreWords": []
        }
    else:
        try:
            with open(CSPELL_FILE, "r") as file:
                cspell_data = json.load(file)
        except json.JSONDecodeError:
            print(f"Error: Failed to parse {CSPELL_FILE}. Resetting to new structure.")
            cspell_data = {
                "version": "0.2",
                "language": "en",
                "ignorePaths": [".devcontainer/**", ".vscode/**", ".github/**"],
                "ignoreWords": []
            }

    # Ensure 'ignoreWords' exists and is a list
    if "ignoreWords" not in cspell_data or not isinstance(cspell_data["ignoreWords"], list):
        print(f"'ignoreWords' field missing or invalid in {CSPELL_FILE}. Resetting to an empty list.")
        cspell_data["ignoreWords"] = []

    # Calculate new words to add
    existing_words = set(cspell_data["ignoreWords"])
    new_words = first_names - existing_words

    if new_words:
        print(f"Adding {len(new_words)} new words to cspell.json: {new_words}")
        cspell_data["ignoreWords"].extend(sorted(new_words))

        # Write updated cspell.json
        with open(CSPELL_FILE, "w") as file:
            json.dump(cspell_data, file, indent=2)
        print("cspell.json updated successfully.")
    else:
        print("No new words to add.")

def main():
    """Main function to execute the update process."""
    print("Starting the cspell update process...")
    members = load_json(MEMBERS_FILE)

    if not members:
        print(f"No valid members data found in {MEMBERS_FILE}. Exiting.")
        return

    first_names = extract_first_names(members)
    update_cspell(first_names)

if __name__ == "__main__":
    main()
