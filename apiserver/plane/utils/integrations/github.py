import os
import jwt
import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend


def get_jwt_token():
    app_id = os.environ.get("GITHUB_APP_ID", "")
    secret = bytes(os.environ.get("GITHUB_APP_PRIVATE_KEY", ""), encoding="utf8")
    current_timestamp = int(datetime.now().timestamp())
    due_date = datetime.now() + timedelta(minutes=10)
    expiry = int(due_date.timestamp())
    payload = {
        "iss": app_id,
        "sub": app_id,
        "exp": expiry,
        "iat": current_timestamp,
        "aud": "https://github.com/login/oauth/access_token",
    }

    priv_rsakey = load_pem_private_key(secret, None, default_backend())
    return jwt.encode(payload, priv_rsakey, algorithm="RS256")


def get_github_metadata(installation_id):
    token = get_jwt_token()

    url = f"https://api.github.com/app/installations/{installation_id}"
    headers = {
        "Authorization": f"Bearer {str(token)}",
        "Accept": "application/vnd.github+json",
    }
    return requests.get(url, headers=headers).json()


def get_github_repos(access_tokens_url, repositories_url):
    token = get_jwt_token()

    headers = {
        "Authorization": f"Bearer {str(token)}",
        "Accept": "application/vnd.github+json",
    }

    oauth_response = requests.post(
        access_tokens_url,
        headers=headers,
    ).json()

    oauth_token = oauth_response.get("token", "")
    headers = {
        "Authorization": f"Bearer {str(oauth_token)}",
        "Accept": "application/vnd.github+json",
    }
    return requests.get(
        repositories_url,
        headers=headers,
    ).json()


def delete_github_installation(installation_id):
    token = get_jwt_token()

    url = f"https://api.github.com/app/installations/{installation_id}"
    headers = {
        "Authorization": f"Bearer {str(token)}",
        "Accept": "application/vnd.github+json",
    }
    return requests.delete(url, headers=headers)


def get_github_repo_details(access_tokens_url, owner, repo):
    token = get_jwt_token()

    headers = {
        "Authorization": f"Bearer {str(token)}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    oauth_response = requests.post(
        access_tokens_url,
        headers=headers,
    ).json()

    oauth_token = oauth_response.get("token")
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Accept": "application/vnd.github+json",
    }
    open_issues = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}",
        headers=headers,
    ).json()["open_issues_count"]

    total_labels = 0

    labels_response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/labels?per_page=100&page=1",
        headers=headers,
    )

    # Check if there are more pages
    if len(labels_response.links.keys()):
        # get the query parameter of last
        last_url = labels_response.links.get("last").get("url")
        parsed_url = urlparse(last_url)
        last_page_value = parse_qs(parsed_url.query)["page"][0]
        total_labels += 100 * (last_page_value - 1)

        # Get labels in last page
        last_page_labels = requests.get(last_url, headers=headers).json()
        total_labels += len(last_page_labels)
    else:
        total_labels = len(labels_response.json())

    # Currently only supporting upto 100 collaborators
    # TODO: Update this function to fetch all collaborators
    collaborators = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/collaborators?per_page=100&page=1",
        headers=headers,
    ).json()

    return open_issues, total_labels, collaborators
