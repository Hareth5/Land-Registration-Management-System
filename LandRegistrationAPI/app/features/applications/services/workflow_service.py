from ..enums import ApplicationStatus

ALLOWED_TRANSITIONS = {
    ApplicationStatus.SUBMITTED: [ApplicationStatus.PRE_CHECKED],
    ApplicationStatus.PRE_CHECKED: [
        ApplicationStatus.SURVEY_REQUIRED,
        ApplicationStatus.LEGAL_REVIEW,
    ],
    ApplicationStatus.SURVEY_REQUIRED: [ApplicationStatus.SURVEYED],
    ApplicationStatus.SURVEYED: [ApplicationStatus.LEGAL_REVIEW],
    ApplicationStatus.LEGAL_REVIEW: [
        ApplicationStatus.APPROVED,
        ApplicationStatus.REJECTED,
    ],
    ApplicationStatus.APPROVED: [ApplicationStatus.CERTIFICATE_ISSUED],
    ApplicationStatus.CERTIFICATE_ISSUED: [ApplicationStatus.CLOSED],
}


def is_transition_allowed(current_status, new_status):

    allowed_statuses = ALLOWED_TRANSITIONS.get(current_status, [])

    return new_status in allowed_statuses


def validate_transition(
    application,
    new_status,
):

    current_status = application["status"]

    if not is_transition_allowed(
        current_status,
        new_status,
    ):

        raise Exception(
            f"Invalid transition from " f"{current_status} " f"to " f"{new_status}"
        )

    if new_status == ApplicationStatus.PRE_CHECKED:

        if not application.get("applicant_ref"):

            raise Exception("Applicant information is required")

        if not application.get("parcel_ref"):

            raise Exception("Parcel information is required")

    return True
