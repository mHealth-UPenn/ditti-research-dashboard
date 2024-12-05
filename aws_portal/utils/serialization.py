from typing import List, Dict
from collections import defaultdict


def serialize_participant(study_subject):
    """
    Transforms a StudySubject object into a JSON-serializable dictionary containing only the required fields.

    Args:
        study_subject (StudySubject): The StudySubject instance to serialize.

    Returns:
        dict: A dictionary containing the serialized participant data.
    """
    participant_data = {
        "dittiId": study_subject.meta.dittiId,
        "userId": study_subject.meta.id,
        "apis": [],
        "studies": []
    }

    # Serialize APIs
    for api_entry in study_subject.meta.apis:
        api_data = {
            "apiName": api_entry.meta.api.meta.name,
            "scope": api_entry.meta.scope
        }
        participant_data["apis"].append(api_data)

    # Serialize Studies
    for study_entry in study_subject.studies:
        study_data = {
            "studyName": study_entry.meta.study.meta.name,
            "studyId": study_entry.meta.study.meta.id,
            "createdOn": study_entry.meta.createdOn,
            "expiresOn": study_entry.meta.expiresOn,
            "dataSummary": study_entry.meta.study.meta.dataSummary
        }
        participant_data["studies"].append(study_data)

    return participant_data


def serialize_fitbit_data(results: List) -> List[Dict]:
    """
    Serializes Fitbit data from query results into a structured format.

    Parameters:
        results (List): List of rows returned from the joined SleepLog and SleepLevel query.

    Returns:
        List[Dict]: A list of serialized sleep log data dictionaries.
    """
    sleep_logs_dict = defaultdict(lambda: {
        "id": None,
        "logId": None,
        "dateOfSleep": None,
        "duration": None,
        "efficiency": None,
        "endTime": None,
        "infoCode": None,
        "isMainSleep": None,
        "minutesAfterWakeup": None,
        "minutesAsleep": None,
        "minutesAwake": None,
        "minutesToFallAsleep": None,
        "logType": None,
        "startTime": None,
        "timeInBed": None,
        "type": None,
        "levels": []
    })

    for row in results:
        log_id = row.sleep_log_id
        sleep_log = sleep_logs_dict[log_id]

        if sleep_log["id"] is None:
            sleep_log.update({
                "id": row.sleep_log_id,
                "logId": row.log_id,
                "dateOfSleep": row.date_of_sleep.isoformat(),
                "duration": row.duration,
                "efficiency": row.efficiency,
                "endTime": row.end_time.isoformat() if row.end_time else None,
                "infoCode": row.info_code,
                "isMainSleep": row.is_main_sleep,
                "minutesAfterWakeup": row.minutes_after_wakeup,
                "minutesAsleep": row.minutes_asleep,
                "minutesAwake": row.minutes_awake,
                "minutesToFallAsleep": row.minutes_to_fall_asleep,
                "logType": row.log_type.value if row.log_type else None,
                "startTime": row.start_time.isoformat() if row.start_time else None,
                "timeInBed": row.time_in_bed,
                "type": row.type.value if row.type else None,
                "levels": []
            })

        sleep_log["levels"].append({
            "dateTime": row.level_date_time.isoformat(),
            "level": row.level_level.value if row.level_level else None,
            "seconds": row.level_seconds
        })

    serialized_data = list(sleep_logs_dict.values())

    return serialized_data
