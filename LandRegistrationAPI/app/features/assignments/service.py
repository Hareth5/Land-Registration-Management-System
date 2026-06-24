from fastapi import HTTPException
from datetime import datetime, timezone
from uuid import uuid4
from app.database.mongo import db
from app.shared import crud
from app.features.assignments.schemas import SurveyMilestoneRequest, SurveyReportRequest, RegistrarReviewRequest

land_applications = db["land_applications"]
staff_members = db["staff_members"]
survey_tasks = db["survey_tasks"]
performance_logs = db["performance_logs"]
survey_reports = db["survey_reports"]

def get_all_staff():
    found = crud.get_many(staff_members)
    return found

def auto_assign_surveyor(application_id: str):  
    application = crud.get_one(land_applications, {"application_id": application_id})
    if not application:
        raise HTTPException(status_code = 404, detail = "Application not found")
    
    if application["status"] != "survey_required":
        raise HTTPException(status_code = 400, detail = "Application is not in survey_required stage")
    
    zone = application["parcel_ref"]["zone_id"]
    if not zone:
        raise HTTPException(status_code = 400, detail = "Application parcel zone is missing")
    
    staffs = get_all_staff()
    best_staff = None
    min_tasks = 1e9
    for staff in staffs:
        if staff["role"] != "surveyor": continue
        if staff["active"] != True: continue
        if zone not in staff["coverage"]["zone_ids"]: continue
        if staff["workload"]["active_tasks"] >= staff["workload"]["max_tasks"] : continue
        if staff["workload"]["active_tasks"] >= min_tasks: continue

        best_staff = staff
        min_tasks = staff["workload"]["active_tasks"]

    if best_staff == None:
        raise HTTPException(status_code = 404, detail = "No available surveyor found for this zone")

    task_id = f"SURV-2026-{uuid4().hex[:8].upper()}"
    document = {
        "task_id" : task_id,
        "application_id" : application_id,
        "parcel_id" : application["parcel_ref"]["parcel_id"],
        "assigned_surveyor_id" : best_staff["_id"],
        "status" : "assigned",
        "milestones": [
            {
                "type": "assigned",
                "at": datetime.now(timezone.utc),
                "by": "system",
                "meta": {
                    "reason": "zone and workload match"
                }
            }
        ],
        "field_notes" : [],
        "report_uploaded" : False,
        "created_at" : datetime.now(timezone.utc)
        }

    inserted_id = crud.create(survey_tasks, document)

    staff_members.update_one(
    {"_id" : best_staff["_id"]},
    {"$inc" : {"workload.active_tasks": 1}}
    )

    updated_application = crud.update_one(
     land_applications, {"application_id": application_id}, {
        "assignment.assigned_surveyor_id": best_staff["_id"],
        "assignment.assignment_policy": "zone+availability+workload"
     }
    )

    if not updated_application:
        raise HTTPException (status_code = 404, detail = "Application not found while updating assignment")
    
    log_document = {
    "application_id": application_id,
    "event_stream": [
        {
            "type": "survey_assigned",
            "by": {
                "actor_type": "system",
                "actor_id": "assignment_engine"
            },
            "at": datetime.now(timezone.utc),
            "meta": {
                "assigned_surveyor": best_staff["staff_code"]
                }
            }
        ]
    }

    crud.create(performance_logs, log_document)

    return {
        "message": "Survey task created successfully",
        "survey_task_id": str(inserted_id),
        "task_id": task_id,
        "application_id": application_id,
        "assigned_surveyor_id": str(best_staff["_id"]),
        "assigned_surveyor_name": best_staff["name"],
        "zone_id": zone
    }

def add_survey_milestone(application_id: str, milestone: SurveyMilestoneRequest):
    application = crud.get_one(land_applications, {"application_id": application_id})
    if not application:
        raise HTTPException(status_code = 404, detail = "Application not found")
    
    survey = crud.get_one(survey_tasks, {"application_id": application_id})
    if not survey:
        raise HTTPException(status_code = 404, detail = "Survey task not found for this application")
    
    current_status = survey["status"]
    new_milestone = milestone.milestone_type.value

    if current_status == "assigned":
        expected_milestone = "visit_scheduled"

    elif current_status == "visit_scheduled":
        expected_milestone = "arrived_on_site"

    elif current_status == "arrived_on_site":
        expected_milestone = "survey_started"

    elif current_status == "survey_started":
        expected_milestone = "survey_completed"

    elif current_status == "registrar_reviewed":
        raise HTTPException(status_code = 400, detail = "Survey task already reached final milestone")

    else:
        raise HTTPException(status_code = 400, detail = "Invalid current survey task status")

    if new_milestone != expected_milestone:
        raise HTTPException(status_code = 400, detail = "Invalid milestone transition")
    
    result = survey_tasks.update_one(
        {"_id": survey["_id"]},
        {
            "$push": {
                "milestones": {
                    "type": new_milestone,
                    "at": datetime.now(timezone.utc),
                    "by": milestone.by.value,
                    "meta": milestone.meta
                }
            },
            "$set": {
                "status": new_milestone
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code = 404, detail = "Survey task not found while updating milestone")
    
    if milestone.by.value == "surveyor":
        actor_id = str(survey["assigned_surveyor_id"])
    else:
        actor_id = "system"

    log_document = {
    "application_id": application_id,
    "event_stream": [
        {
            "type": "survey_milestone_added",
            "by": {
                "actor_type": milestone.by.value,
                "actor_id": actor_id
            },
            "at": datetime.now(timezone.utc),
            "meta": {
                "task_id": survey["task_id"],
                "previous_status": current_status,
                "new_status": new_milestone,
                "milestone_type": new_milestone,
                "milestone_meta": milestone.meta
                }
            }
        ]
    }

    crud.create(performance_logs, log_document)

    return {
    "message": "Survey milestone added successfully",
    "application_id": application_id,
    "survey_task_id": str(survey["_id"]),
    "task_id": survey["task_id"],
    "previous_status": current_status,
    "new_status": new_milestone,
    "milestone_by": milestone.by.value
}

def add_survey_report(application_id: str, report: SurveyReportRequest):
    application = crud.get_one(land_applications, {"application_id": application_id})
    if not application:
        raise HTTPException(status_code = 404, detail = "Application not found")
    
    survey = crud.get_one(survey_tasks, {"application_id": application_id})
    if not survey:
        raise HTTPException(status_code = 404, detail = "Survey task not found for this application")
    
    if survey["status"] != "survey_completed":
        raise HTTPException(status_code = 400, detail = "Survey task is not completed yet")
    
    report_id = f"REP-2026-{uuid4().hex[:8].upper()}"
    document = {
        "report_id": report_id,
        "application_id": application_id,
        "task_id": survey["task_id"],
        "uploaded_by": report.uploaded_by,
        "report_title": report.report_title,
        "summary": report.summary,
        "file_name": report.file_name,
        "file_path": report.file_path,
        "created_at": datetime.now(timezone.utc)
    }

    inserted_id = crud.create(survey_reports, document)

    result = survey_tasks.update_one(
        {"_id": survey["_id"]},
        {
            "$push": {
                "milestones": {
                    "type": "report_uploaded",
                    "at": datetime.now(timezone.utc),
                    "by": "surveyor",
                    "meta": {
                        "report_id": report_id,
                        "file_name": report.file_name
                    }
                }
            },
            "$set": {
                "status": "report_uploaded",
                "report_uploaded": True
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code = 404, detail = "Survey task not found while uploading report")

    log_document = {
    "application_id": application_id,
    "event_stream": [
        {
            "type": "survey_report_uploaded",
            "by": {
                "actor_type": "surveyor",
                "actor_id": report.uploaded_by
            },
            "at": datetime.now(timezone.utc),
            "meta": {
                "task_id": survey["task_id"],
                "report_id": report_id,
                "file_name": report.file_name
                }
            }
        ]
    }

    crud.create(performance_logs, log_document)

    return {
        "message": "Survey report uploaded successfully",
        "application_id": application_id,
        "survey_task_id": str(survey["_id"]),
        "task_id": survey["task_id"],
        "report_mongo_id": str(inserted_id),
        "report_id": report_id,
        "status": "report_uploaded"
    }

def registrar_review(application_id: str, review: RegistrarReviewRequest):
    application = crud.get_one(land_applications, {"application_id": application_id})
    if not application:
        raise HTTPException(status_code = 404, detail = "Application not found")
    
    survey = crud.get_one(survey_tasks, {"application_id": application_id})
    if not survey:
        raise HTTPException(status_code = 404, detail = "Survey task not found for this application")
    
    report = crud.get_one(survey_reports, {"application_id": application_id})
    if not report:
        raise HTTPException(status_code = 404, detail = "Survey report not found for this application")
    
    if survey["status"] == "registrar_reviewed":
        raise HTTPException(status_code = 400, detail = "Survey task already reviewed by registrar")
    
    if survey["status"] != "report_uploaded":
        raise HTTPException(status_code = 400, detail = "Survey report must be uploaded before registrar review")
    
    decision = review.decision.value
    if decision == "approved":
        status = "approved"
    elif decision == "rejected":
        status = "rejected"
    else:
        status = "on_hold"

    application_data = {
    "status": status,
    "registrar_review.reviewed_by": review.reviewed_by,
    "registrar_review.decision": decision,
    "registrar_review.notes": review.notes,
    "registrar_review.reviewed_at": datetime.now(timezone.utc),
    "timestamps.legal_review_at": datetime.now(timezone.utc),
    "timestamps.updated_at": datetime.now(timezone.utc)
    }

    updated_application = crud.update_one(land_applications, {"application_id": application_id}, application_data)

    if not updated_application:
        raise HTTPException(status_code = 404, detail = "Application not found while updating registrar review")

    result = survey_tasks.update_one(
        {"_id": survey["_id"]},
        {
            "$push": {
                "milestones": {
                    "type": "registrar_reviewed",
                    "at": datetime.now(timezone.utc),
                    "by": "registrar",
                    "meta": {
                        "decision": decision,
                        "notes": review.notes,
                        "reviewed_by": review.reviewed_by
                    }
                }
            },
            "$set": {
                "status": "registrar_reviewed"
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code = 404, detail = "Survey task not found while updating registrar review")
    
    staff_members.update_one(
    {"_id" : survey["assigned_surveyor_id"]},
    {"$inc" : {"workload.active_tasks": -1}}
    )

    log_document = {
    "application_id": application_id,
    "event_stream": [
        {
            "type": "registrar_reviewed",
            "by": {
                "actor_type": "registrar",
                "actor_id": review.reviewed_by
            },
            "at": datetime.now(timezone.utc),
            "meta": {
                "task_id": survey["task_id"],
                "report_id": report["report_id"],
                "decision": decision,
                "status": status,
                "notes": review.notes
                }
            }
        ]
    }

    crud.create(performance_logs, log_document)

    return {
        "message": "Registrar review completed successfully",
        "application_id": application_id,
        "survey_task_id": str(survey["_id"]),
        "task_id": survey["task_id"],
        "report_id": report["report_id"],
        "decision": decision,
        "status": status,
        "survey_status": "registrar_reviewed"
    }