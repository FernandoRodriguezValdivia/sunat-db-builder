import os
import requests

DB_PATH = "output/sunat.sqlite"

HOST = os.environ["TURSO_HOST"]
TOKEN = os.environ["TURSO_DATABASE_TOKEN"]

URL = f"https://{HOST}/v1/upload"

size = os.path.getsize(DB_PATH)

print(f"Tamaño SQLite: {size:,} bytes")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Length": str(size),
}

def file_iterator(path, chunk_size=1024 * 1024):
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


response = requests.post(
    URL,
    headers=headers,
    data=file_iterator(DB_PATH),
    timeout=None
)

print("Status:", response.status_code)

if response.text:
    print(response.text)

response.raise_for_status()

print("SQLite subida correctamente.")