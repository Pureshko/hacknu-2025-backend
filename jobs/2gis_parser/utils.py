import json 
import os

def save_json(data, filename):
    os.makedirs('data', exist_ok=True)
    path = os.path.join('data', filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved: {path}")

def read_json(filename):
    path = os.path.join("data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)