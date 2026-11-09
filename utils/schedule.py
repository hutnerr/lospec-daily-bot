import datetime

# 08:00 AM daily, in the host machine's local timezone
POST_HOUR = 8
POST_MINUTE = 0
POST_TIME_TEXT = "8:00 AM Eastern"

# if the daily fails to fetch (or lospec hasn't updated yet), keep retrying
# this often, and give up on the day this long after the post time
RETRY_INTERVAL = datetime.timedelta(minutes=10)
GIVE_UP_AFTER = datetime.timedelta(hours=6)

def now() -> datetime.datetime:
    return datetime.datetime.now().astimezone()

def postTimeOn(day: datetime.datetime) -> datetime.datetime:
    return day.replace(hour=POST_HOUR, minute=POST_MINUTE, second=0, microsecond=0)
