import requests

student_id = "23A91A05D9"
github_repo_url = "https://github.com/Mythili369/my-project"

api_url = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

# 1. Read public key directly from PEM file
with open("student_public.pem", "r") as f:
    public_key_str = f.read()

# 2. Prepare payload
payload = {
    "student_id": student_id,
    "github_repo_url": github_repo_url,
    "public_key": public_key_str
}

# 3. Send request
response = requests.post(api_url, json=payload)

# 4. Handle response
if response.status_code == 200:
    data = response.json()
    if data.get("status") == "success":
        encrypted_seed = data["encrypted_seed"]
        with open("encrypted_seed.txt", "w") as f:
            f.write(encrypted_seed)
        print("Encrypted seed received and saved to encrypted_seed.txt")
    else:
        print("Error from API:", data)
else:
    print("HTTP error:", response.status_code)
    print("Response:", response.text)
