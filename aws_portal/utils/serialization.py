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
