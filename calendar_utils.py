
from calendar_auth import get_calendar_service
import datetime

def find_free_slot(events, duration_hours, date):
    work_start = datetime.datetime.combine(date, datetime.time(10, 0))
    work_end = datetime.datetime.combine(date, datetime.time(20, 0))
    busy_times = []

    for event in events:
        start = event['start'].get('dateTime')
        end = event['end'].get('dateTime')
        if start and end:
            busy_times.append((datetime.datetime.fromisoformat(start), datetime.datetime.fromisoformat(end)))

    busy_times.sort()
    cursor = work_start
    needed = datetime.timedelta(hours=duration_hours)

    for start, end in busy_times:
        if start - cursor >= needed:
            return cursor, cursor + needed
        cursor = max(cursor, end)

    if work_end - cursor >= needed:
        return cursor, cursor + needed

    return None, None

def add_task(summary, duration_hours, date):
    service = get_calendar_service()

    start_day = datetime.datetime.combine(date, datetime.time.min).isoformat() + 'Z'
    end_day = datetime.datetime.combine(date, datetime.time.max).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary', timeMin=start_day, timeMax=end_day,
        singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    start, end = find_free_slot(events, duration_hours, date)
    if not start:
        return None

    event = {
        'summary': summary,
        'start': {'dateTime': start.isoformat(), 'timeZone': 'Europe/Istanbul'},
        'end': {'dateTime': end.isoformat(), 'timeZone': 'Europe/Istanbul'}
    }
    created = service.events().insert(calendarId='primary', body=event).execute()
    return created
