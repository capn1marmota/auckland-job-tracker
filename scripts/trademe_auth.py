from requests_oauthlib import OAuth1Session
import os
from dotenv import load_dotenv

load_dotenv()

KEY    = os.getenv("TRADEME_CONSUMER_KEY")
SECRET = os.getenv("TRADEME_CONSUMER_SECRET")

# Trade Me sandbox endpoints (use these first to test)
REQUEST_TOKEN_URL = "https://secure.tmsandbox.co.nz/Oauth/RequestToken"
AUTHORIZE_URL     = "https://secure.tmsandbox.co.nz/Oauth/Authorize"
ACCESS_TOKEN_URL  = "https://secure.tmsandbox.co.nz/Oauth/AccessToken"

oauth = OAuth1Session(KEY, client_secret=SECRET, callback_uri="oob")

# Step 1 — get request token
fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
resource_owner_key    = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")

# Step 2 — authorize in browser
auth_url = oauth.authorization_url(AUTHORIZE_URL)
print(f"\nOpen this URL in your browser and authorize:\n{auth_url}\n")
verifier = input("Paste the verifier code here: ")

# Step 3 — exchange for access token
oauth = OAuth1Session(
    KEY, client_secret=SECRET,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=verifier,
)
tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)

print("\n── ADD THESE TO YOUR .env ──")
print(f"TRADEME_OAUTH_TOKEN={tokens['oauth_token']}")
print(f"TRADEME_OAUTH_SECRET={tokens['oauth_token_secret']}")
