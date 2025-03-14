import base64
import requests

APP_KEY = input("Input APP_KEY: ")
APP_SECRET = input("Input APP_SECRET: ")

BASIC_AUTH = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode('utf-8')).decode('utf-8')

print("Go to the following url and get your ACCESS CODE")
print(f"https://www.dropbox.com/oauth2/authorize?client_id={APP_KEY}&token_access_type=offline&response_type=code")

input("Retur here, When you have the ACCESS_CODE and press ENTER to continue...")

ACCESS_CODE_GENERATED = input("Input ACCESS_CODE: ")

url = 'https://api.dropboxapi.com/oauth2/token'
headers = {
    'Authorization': f'Basic {BASIC_AUTH}',
    'Content-Type': 'application/x-www-form-urlencoded'
}
data = {
    'code': ACCESS_CODE_GENERATED,
    'grant_type': 'authorization_code'
}

response = requests.post(url, headers=headers, data=data)

if response.status_code == 200:
    print("Success!")
    print(response.json()) 
else:
    print(f"Error!: {response.status_code}")
    print(response.text)
