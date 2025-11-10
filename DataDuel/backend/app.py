from flask import Flask, redirect, request, jsonify
import requests
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@app.route("/")
def home():
    return "🏃 Flask Strava API Backend Running!"

# STEP 1: Redirect to Strava
@app.route("/auth/strava")
def auth_strava():
    auth_url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&approval_prompt=auto"
        f"&scope=read,activity:read_all"
    )
    return redirect(auth_url)

# STEP 2: Handle callback and exchange code for access token
@app.route("/auth/strava/callback")
def auth_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=payload)
    data = response.json()

    if "access_token" not in data:
        return jsonify({"error": "Failed to get access token", "details": data}), 400

    athlete = data.get("athlete", {})

    # Store tokens_ securely (example: in JSON)
    with open("tokens_.json", "w") as f:
        json.dump({
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": data["expires_at"],
        }, f)

    return jsonify({
        "message": "Strava authentication successful!",
        "athlete": athlete,
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_at": data["expires_at"],
    })

def get_valid_token():
    """Load and refresh the access token if expired."""
    FILE_NAME = "tokens.json"
    # Ensure the file exists
    if not os.path.exists(FILE_NAME):
        raise FileNotFoundError("tokens_.json not found. Please authenticate first.")
    # Load saved tokens_
    with open(FILE_NAME, "r") as f:
        tokens_ = json.load(f)

    # Check if expired
    if time.time() > tokens_.get("expires_at", 0):
        print("Access token expired — refreshing...")

        refresh_payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": tokens_["refresh_token"],
        }

        response = requests.post("https://www.strava.com/oauth/token", data=refresh_payload)
        new_data = response.json()

        # Update stored tokens_
        tokens_.update({
            "access_token": new_data["access_token"],
            "refresh_token": new_data["refresh_token"],
            "expires_at": new_data["expires_at"],
        })

        with open(FILE_NAME, "w") as f:
            json.dump(tokens_, f)

        print("New access token saved.")

    return tokens_["access_token"]


@app.route("/strava/activities")
def get_activities():
    """Fetch recent Strava activities using a valid access token."""
    try:
        access_token = get_valid_token()
    except Exception as e:
        return jsonify({"error": f"Could not load or refresh token: {str(e)}"}), 500

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch activities", "details": response.json()}), response.status_code

    return jsonify(response.json())

if __name__ == "__main__":
    app.run(debug=True)
