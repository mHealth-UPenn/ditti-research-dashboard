def serialize_participant(study_subject):
    """
    Transforms a StudySubject object into a JSON-serializable dictionary containing only the required fields.

    Args:
        study_subject (StudySubject): The StudySubject instance to serialize.

    Returns:
        dict: A dictionary containing the serialized participant data.
    """
    participant_data = {
        "email": study_subject.email,
        "user_id": study_subject.id,
        # "name": study_subject.name,  # TODO: Add this later
        "apis": [],
        "studies": []
    }

    # Serialize APIs
    for api_entry in study_subject.apis:
        api_data = {
            "api_name": api_entry.api.name,
            "scope": api_entry.scope,
            "expires_at": api_entry.meta.get('expires_at', None)
        }
        participant_data["apis"].append(api_data)

    # Serialize Studies
    for study_entry in study_subject.studies:
        study_data = {
            "study_name": study_entry.study.name,
            "study_id": study_entry.study.id,
            # "study_start_date": study_entry.study.created_on.isoformat(),
            "study_start_date": study_subject.created_on.isoformat(),  # TODO: Replace later
            "study_end_date": study_entry.expires_on.isoformat(),
            # "why_collecting_data": study_entry.study.consent_information  # TODO: Add this later
        }
        participant_data["studies"].append(study_data)

    return participant_data
