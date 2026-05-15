import jwt
import sys

SECRET = "your-strong-secret-here-change-me"

def generate_token(tenant: str):
    payload = {"tenant": tenant}
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    print(token)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_jwt.py <tenant>")
        sys.exit(1)
    generate_token(sys.argv[1])
