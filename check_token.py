import json

with open("token.json", "r") as file:
    token_data = json.load(file)

print("Access token:", bool(token_data.get("token")))
print("Refresh token:", bool(token_data.get("refresh_token")))