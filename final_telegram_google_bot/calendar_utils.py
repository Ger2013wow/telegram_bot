from datetime import datetime, timedelta
from calendar_auth import get_calendar_service

def add_task(summary, duration_minutes, date_str):
    service = get_calendar_service()
    events_result = service.events().list(
        calendarId='primary',
        timeMin=f"{date_str}T10:00:00Z",
        timeMax=f"{date_str}T20:00:00Z",
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    start_time = datetime.fromisoformat(f"{date_str}T10:00:00")
    for event in events:
        end = datetime.fromisoformat(event['start']['dateTime'])
        if (end - start_time).total_seconds() >= duration_minutes * 60:
            break
        start_time = datetime.fromisoformat(event['end']['dateTime'])

    end_time = start_time + timedelta(minutes=duration_minutes)
    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event

def get_daily_summary():
    service = get_calendar_service()
    now = datetime.utcnow()
    start = datetime(now.year, now.month, now.day, 0, 0, 0)
    end = start + timedelta(days=1)
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    if not events:
        return "📭 На сегодня нет встреч."
    summary = "📅 Встречи на сегодня:
"
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        summary += f"— {event['summary']} в {start_time}
"
    return summary