import requests
import json

# Replace with your GitHub token and organization
GITHUB_TOKEN = 'your_github_token'
ORG_NAME = 'your_org_name'
API_URL = 'https://api.github.com'
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_org_members(org_name):
    """Fetch all members of the organization."""
    members = []
    url = f"{API_URL}/orgs/{org_name}/members"
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        members.extend(response.json())
        url = response.links.get('next', {}).get('url')
    return members

def get_user_name(login):
    """Retrieve the 'name' attribute of a user."""
    url = f"{API_URL}/users/{login}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    user_data = response.json()
    return user_data.get('name', '')

def split_name(name):
    """Split the name by spaces, preserving hyphens within words."""
    return name.lower().split()

def main():
    members = get_org_members(ORG_NAME)
    for member in members:
        login = member['login']
        name = get_user_name(login)
        if name:
            name_parts = split_name(name)
            print(f"User: {login}, Name Parts: {name_parts}")

if __name__ == "__main__":
    main()
