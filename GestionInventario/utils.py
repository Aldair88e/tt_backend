from datetime import datetime, timedelta

def add_months(date, months):
    month = date.month - 1 + months
    year = date.year + month // 12
    month = month % 12 + 1
    day = min(date.day, (date.replace(month=month, year=year) - timedelta(days=1)).day)
    return date.replace(year=year, month=month, day=day)