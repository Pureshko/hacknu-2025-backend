import csv
import json
import os

def save_json(data, filename):
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[+] Saved JSON: {path}")
    except Exception as e:
        print(f"[!] Ошибка при сохранении JSON {filename}: {e}")

def read_json(filename):
    path = os.path.join("data", filename)
    if not os.path.exists(path):
        print(f"[!] Файл {filename} не найден")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"[!] Файл {filename} повреждён, возвращаю пустой словарь")
        return {}
    except Exception as e:
        print(f"[!] Ошибка при чтении JSON {filename}: {e}")
        return {}

def save_to_csv(data, filename):
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", filename)
    if not data:
        print("[!] Нет данных для сохранения")
        return
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"[+] Saved CSV: {path}")
    except Exception as e:
        print(f"[!] Ошибка при сохранении CSV {filename}: {e}")

def append_to_csv(data, filename):
    """Добавляет строки в CSV, создавая файл при первом вызове"""
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", filename)
    if not data:
        return
    try:
        file_exists = os.path.isfile(path)
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"[!] Ошибка при добавлении данных в CSV {filename}: {e}")

def load_seen_ids(path="data/seen_ids.json"):
    """Загружает множество уже сохранённых ID (если файл повреждён — возвращает пустое)"""
    if not os.path.exists(path):
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return set(data)
            elif isinstance(data, set):
                return data
            elif isinstance(data, dict):
                # если файл случайно сохранился как dict
                return set(data.keys())
    except json.JSONDecodeError:
        print(f"[!] Файл seen_ids.json повреждён, создаю новый")
    except Exception as e:
        print(f"[!] Ошибка при загрузке seen_ids.json: {e}")
    return set()

def save_seen_ids(seen_ids, path="data/seen_ids.json"):
    """Безопасное сохранение ID — даже если файл временно заблокирован"""
    os.makedirs("data", exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(list(seen_ids), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[!] Ошибка при сохранении seen_ids.json: {e}")



# import csv
# import json 
# import os

# def save_json(data, filename):
#     os.makedirs('data', exist_ok=True)
#     path = os.path.join('data', filename)
#     with open(path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)
#     print(f"[+] Saved: {path}")

# def read_json(filename):
#     path = os.path.join("data", filename)
#     with open(path, "r", encoding="utf-8") as f:
#         return json.load(f)
    

# def save_to_csv(data, filename):
#     os.makedirs("data", exist_ok=True)
#     path = os.path.join("data", filename)
#     if not data:
#         print("[!] Нет данных для сохранения")
#         return

#     with open(path, "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=data[0].keys())
#         writer.writeheader()
#         writer.writerows(data)

#     print(f"[+] Saved CSV: {path}")


# def append_to_csv(data, filename):
#     """Добавляет список словарей в CSV, создавая файл при первом вызове"""
#     os.makedirs("data", exist_ok=True)
#     path = os.path.join("data", filename)
#     if not data:
#         return
#     file_exists = os.path.isfile(path)
#     with open(path, "a", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=data[0].keys())
#         if not file_exists:
#             writer.writeheader()
#         writer.writerows(data)


# def load_seen_ids(path="data/seen_ids.json"):
#     if os.path.exists(path):
#         with open(path, "r", encoding="utf-8") as f:
#             return set(json.load(f))
#     return set()

# def save_seen_ids(seen_ids, path="data/seen_ids.json"):
#     os.makedirs("data", exist_ok=True)
#     with open(path, "w", encoding="utf-8") as f:
#         json.dump(list(seen_ids), f, ensure_ascii=False, indent=2)