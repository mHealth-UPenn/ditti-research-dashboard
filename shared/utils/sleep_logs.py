from datetime import datetime, timedelta
import random
import uuid


def generate_random_time_between(start_hour, end_hour):
    """Generates a random time between the specified hours of the day."""
    hour = random.randint(start_hour, end_hour - 1)
    minute = random.randint(0, 59)
    return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)


def get_random_level_stages(previous_level):
    """Returns a random sleep level stage, avoiding the previous level."""
    levels_stages = ["deep", "light", "rem", "wake"]
    levels_stages.remove(previous_level)
    return random.choice(levels_stages)


def get_random_level_classic(previous_level):
    """Returns a random sleep level classic, avoiding the previous level."""
    levels_classic = ["asleep", "awake", "restless"]
    levels_classic.remove(previous_level)
    return random.choice(levels_classic)


def generate_sleep_logs():
    sleep_logs = []
    levels_stages = ["deep", "light", "rem", "wake"]
    levels_classic = ["asleep", "awake", "restless"]
    classic_day = random.randint(1, 7)

    for i in range(7, 0, -1):
        date_of_sleep = datetime.now() - timedelta(days=i)
        start_time = generate_random_time_between(22, 24).replace(day=date_of_sleep.day)

        sleep_log = {
            "sleep_log": {
                "logId": str(uuid.uuid4()),
                "dateOfSleep": date_of_sleep.isoformat(),
                "startTime": start_time.isoformat(),
                "duration": "",
                "efficiency": "",
                "endTime": datetime.now().isoformat(),
                "infoCode": "",
                "isMainSleep": "",
                "minutesAfterWakeup": "",
                "minutesAsleep": "",
                "minutesAwake": "",
                "minutesToFallAsleep": "",
                "logType": "",
                "timeInBed": "",
                "totalMinutesAsleep": "",
                "sleepEfficiencyPercentage": "",
                "type": "classic" if i == classic_day else "stages",
                "levels": {"data": [], "summary": []},
            },
        }

        previous_level = None
        total_duration_minutes = 0
        max_duration_minutes = 360 + random.random() * 120

        while total_duration_minutes < max_duration_minutes:
            seconds = random.randint(5 * 60, 30 * 60)
            date_time = (
                previous_level["dateTime"] + timedelta(seconds=previous_level["seconds"])
                if previous_level
                else start_time
            )

            if i == classic_day:
                level = {
                    "dateTime": date_time.isoformat(),
                    "seconds": seconds,
                    "isShort": None,
                    "level": (
                        get_random_level_classic(previous_level["level"])
                        if previous_level
                        else random.choice(levels_classic)
                    ),
                }
            else:
                level = {
                    "dateTime": date_time,
                    "seconds": seconds,
                    "isShort": None,
                    "level": (
                        get_random_level_stages(previous_level["level"])
                        if previous_level
                        else random.choice(levels_stages)
                    ),
                }

            sleep_log["levels"]["data"].append(level)
            previous_level = level
            total_duration_minutes += seconds / 60

        sleep_logs.append(sleep_log)

    return sleep_logs
