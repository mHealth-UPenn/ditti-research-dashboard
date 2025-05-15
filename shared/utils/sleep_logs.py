# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import random
from collections import defaultdict
from datetime import date, datetime, timedelta


def generate_random_time_between(start_hour, end_hour):
    """Generate a random time between the specified hours of the day."""
    hour = random.randint(start_hour, end_hour - 1)  # noqa: S311
    minute = random.randint(0, 59)  # noqa: S311
    return datetime.now().replace(hour=hour, minute=minute)


def get_random_level_stages(previous_level):
    """Return a random sleep level stage, avoiding the previous level."""
    levels_stages = ["deep", "light", "rem", "wake"]
    levels_stages.remove(previous_level)
    return random.choice(levels_stages)  # noqa: S311


def get_random_level_classic(previous_level):
    """Return a random sleep level classic, avoiding the previous level."""
    levels_classic = ["asleep", "awake", "restless"]
    levels_classic.remove(previous_level)
    return random.choice(levels_classic)  # noqa: S311


def generate_sleep_logs():
    """
    Generate random sleep log data for testing.

    Creates a set of synthetic sleep logs with realistic patterns
    for testing data visualization and analysis features.

    Returns
    -------
    list
        List of dictionaries containing sleep log data
    """
    sleep_logs = []
    levels_stages = ["deep", "light", "rem", "wake"]
    levels_classic = ["asleep", "awake", "restless"]
    classic_day = random.randint(1, 7)  # noqa: S311

    for i in range(7, 0, -1):
        date_of_sleep = date.today() - timedelta(days=i)
        start_time = generate_random_time_between(22, 24).replace(
            day=date_of_sleep.day
        )

        sleep_log = {
            "logId": random.randint(0, int(1e9)),  # noqa: S311
            "dateOfSleep": date_of_sleep.isoformat(),
            "startTime": start_time.isoformat(),
            "duration": 1,
            "efficiency": 1,
            "endTime": datetime.now().isoformat(),
            "infoCode": 1,
            "isMainSleep": True,
            "minutesAfterWakeup": 1,
            "minutesAsleep": 1,
            "minutesAwake": 1,
            "minutesToFallAsleep": 1,
            "logType": "auto_detected",
            "timeInBed": 1,
            "type": "classic" if i == classic_day else "stages",
            "levels": {"data": [], "shortData": [], "summary": {}},
        }

        if i == classic_day:
            sleep_log["levels"]["summary"] = {
                level: defaultdict(int) for level in levels_classic
            }
        else:
            sleep_log["levels"]["summary"] = {
                level: defaultdict(int) for level in levels_stages
            }

        previous_level = None
        total_duration_minutes = 0
        max_duration_minutes = 360 + random.random() * 120  # noqa: S311

        while total_duration_minutes < max_duration_minutes:
            if random.randint(0, 1):  # noqa: S311
                seconds = random.randint(210, 30 * 60)  # noqa: S311
            else:
                seconds = random.randint(60, 210)  # noqa: S311
            seconds = seconds - seconds % 30
            date_time = (
                datetime.strptime(
                    previous_level["dateTime"], "%Y-%m-%dT%H:%M:%S.%f"
                )
                + timedelta(seconds=previous_level["seconds"])
                if previous_level
                else start_time
            )

            if i == classic_day:
                if previous_level:
                    level = get_random_level_classic(previous_level["level"])
                else:
                    level = random.choice(levels_classic)  # noqa: S311
            else:
                if previous_level:
                    level = get_random_level_stages(previous_level["level"])
                else:
                    level = random.choice(levels_stages)  # noqa: S311

            level_data = {
                "dateTime": date_time.isoformat(),
                "seconds": seconds,
                "level": level,
            }

            sleep_log["levels"]["data"].append(level_data)
            sleep_log["levels"]["summary"][level]["count"] += 1
            sleep_log["levels"]["summary"][level]["minutes"] += seconds // 60
            sleep_log["levels"]["summary"][level]["thirtyDayAverageMinutes"] += (
                seconds // 60
            )

            if seconds < 210:
                sleep_log["levels"]["shortData"].append(level_data)

            previous_level = level_data
            total_duration_minutes += seconds // 60

        sleep_logs.append(sleep_log)

    return {"sleep": sleep_logs}
