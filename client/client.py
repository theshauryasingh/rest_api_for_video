import requests
import json

# Base URL of the API
BASE_URL = "http://127.0.0.1:5000"

# Helper function to print response
def print_response(response):
    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Error:", response.status_code, response.text)

print("\n--- Testing /signup ---")
SIGNUP_URL = f"{BASE_URL}/signup"
signup_payload = {
    "username": "test_user",
    "password": "securepassword",
    "email": "test_user@example.com"
}
response = requests.post(SIGNUP_URL, json=signup_payload)
print_response(response)

# 2. Test the /signin endpoint
print("\n--- Testing /signin ---")
SIGNIN_URL = f"{BASE_URL}/signin"
signin_payload = {
    "username": "test_user",
    "password": "securepassword"
}
response = requests.post(SIGNIN_URL, json=signin_payload)
print_response(response)

token = response.json().get("token")
if not token:
    print("Failed to retrieve token. Exiting tests.")
    exit()

# Set headers with the token for authenticated requests
headers = {
    "Authorization": f"Bearer {token}"
}

# 3. Test the /upload endpoint
print("\n--- Testing /upload ---")
UPLOAD_URL = f"{BASE_URL}/upload"
with open("test_video.mp4", "rb") as video_file:  # Replace 'test_video.mp4' with your test file
    files = {"video": video_file}
    response = requests.post(UPLOAD_URL, files=files, headers=headers)
    print_response(response)

# Extract filename from the response for further tests
uploaded_video = response.json().get("filename")
if not uploaded_video:
    print("Failed to upload video. Exiting tests.")
    exit()

# 4. Test the /trim endpoint
print("\n--- Testing /trim ---")
TRIM_URL = f"{BASE_URL}/trim"
trim_payload = {
    "video_name": uploaded_video,
    "start_time": 5,  # Start time in seconds
    "end_time": 10,   # End time in seconds
}
response = requests.post(TRIM_URL, json=trim_payload, headers=headers)
print_response(response)

# 5. Test the /merge endpoint
print("\n--- Testing /merge ---")
MERGE_URL = f"{BASE_URL}/merge"
merge_payload = {
    "video_names": [uploaded_video, uploaded_video]  # Use the same video twice for merging
}
response = requests.post(MERGE_URL, json=merge_payload, headers=headers)
print_response(response)
