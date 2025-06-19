import json
import os
from tkinter import filedialog, messagebox
import csv

DATA_FILE = "assets.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_csv(data, columns):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV 파일", "*.csv"), ("모든 파일", "*.*")])
    if not file_path:
        return
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for item in data:
            alert_str = "True" if item[4] else "False"
            row = [item[0], item[1], item[2], item[3], alert_str, item[5]]
            writer.writerow(row)

def import_csv(columns):
    file_path = filedialog.askopenfilename(filetypes=[("CSV 파일", "*.csv"), ("모든 파일", "*.*")])
    if not file_path:
        return None
    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        if header != columns:
            messagebox.showerror("오류", "CSV 헤더가 올바르지 않습니다.")
            return None
        data = []
        for row in reader:
            if len(row) != len(columns):
                continue
            kind, name, amount_str, expire, alert_str, note = row
            if not amount_str.isdigit():
                continue
            alert = alert_str.lower() in ["true", "1", "yes"]
            data.append([kind, name, int(amount_str), expire, alert, note])
        return data
