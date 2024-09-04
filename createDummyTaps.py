import json
import random
import datetime


users = [
    {"user_permission_id": "msii001", "days": [random.randint(0, 1) for _ in range(7)]},
    {"user_permission_id": "msii002", "days": [random.randint(0, 1) for _ in range(7)]},
    {"user_permission_id": "msii003", "days": [random.randint(0, 1) for _ in range(7)]},
    {"user_permission_id": "msii004", "days": [random.randint(0, 1) for _ in range(7)]},
    {"user_permission_id": "msii005", "days": [random.randint(0, 1) for _ in range(7)]},
    {"user_permission_id": "msii006", "days": [random.randint(0, 1) for _ in range(7)]},
    {"user_permission_id": "msii007", "days": [random.randint(0, 1) for _ in range(7)]},
    {"user_permission_id": "msii008", "days": [random.randint(0, 1) for _ in range(7)]},
]
taps = []


def generate_start_time(weekday):
    # Get today's date and find the next occurrence of the given weekday
    today = datetime.date.today()
    days_ahead = (weekday - today.weekday() + 7) % 7
    target_date = today - datetime.timedelta(days=days_ahead)
    
    # Create the base datetime object for 10pm on the target date
    base_time = datetime.datetime(target_date.year, target_date.month, target_date.day, 22, 0, 0)
    
    # Generate a random number of seconds within one hour (0 to 3600 seconds)
    random_seconds = random.randint(0, 3600)
    
    # Add the random seconds to the base time
    random_timestamp = base_time + datetime.timedelta(seconds=random_seconds)
    
    return random_timestamp


def generate_timestamps(start_time, num_timestamps, min_interval, max_interval):
    timestamps = [start_time]
    current_time = start_time

    for _ in range(num_timestamps - 1):
        interval = random.randint(min_interval, max_interval)
        current_time += datetime.timedelta(seconds=interval)
        timestamps.append(current_time)
    
    return timestamps


for user in users:
    for day, switch in enumerate(user["days"]):
        if switch:
            num_timestamps = 0
            start_time = generate_start_time(day)

            while num_timestamps < 30:
                num_timestamps = random.randint(10, 100)
                timestamps = generate_timestamps(start_time, num_timestamps, 3, 5)
                taps.extend({"user_permission_id": user["user_permission_id"], "time": t.isoformat()} for t in timestamps)
                start_time = start_time + datetime.timedelta(minutes=random.randint(20, 60))

with open("dummyData.json", "w") as f:
    json.dump(taps, f, indent=4)
