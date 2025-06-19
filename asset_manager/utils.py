from datetime import datetime

def fix_date_format(date_str):
    try:
        date_str = date_str.strip().replace(".", "-").replace("/", "-")
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except:
        return None

def format_currency(amount):
    return f"{amount:,}"

def calculate_d_day(date_str):
    try:
        today = datetime.today().date()
        expire = datetime.strptime(date_str, "%Y-%m-%d").date()
        diff = (expire - today).days
        if diff > 0:
            return f"D-{diff}"
        elif diff == 0:
            return "D-Day"
        else:
            return f"D+{-diff}"
    except:
        return ""
