
from datetime import datetime, timedelta, timezone

def add_task(summary, duration_minutes, date_str):
    now = datetime.now(timezone.utc)
    date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    start_time = datetime.combine(date.date(), datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=10)
    end_time = start_time + timedelta(minutes=duration_minutes)

    if (end_time - start_time).total_seconds() < duration_minutes * 60:
        raise Exception("❌ Недостаточно времени для задачи")

    return {
        "summary": f"{summary} ({duration_minutes} мин) на {date_str}"
    }

def get_daily_summary():
    return "🗓 Сегодня: задач пока нет."
