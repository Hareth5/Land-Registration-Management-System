export const APPLICATION_TYPES = [
  "first_registration",
  "ownership_transfer",
  "parcel_subdivision",
  "parcel_merge",
  "boundary_correction",
  "certificate_request",
];

export const APPLICATION_STATUSES = [
  "submitted",
  "pre_checked",
  "survey_required",
  "surveyed",
  "legal_review",
  "approved",
  "certificate_issued",
  "closed",
  "rejected",
  "on_hold",
  "missing_documents",
  "under_objection",
];

export const ALLOWED_TRANSITIONS = {
  submitted: ["pre_checked"],
  pre_checked: ["survey_required", "legal_review"],
  survey_required: ["surveyed"],
  surveyed: ["legal_review"],
  legal_review: ["approved", "rejected"],
  approved: ["certificate_issued"],
  certificate_issued: ["closed"],
};

export const APPLICANT_TYPES = [
  "citizen",
  "lawyer",
  "company",
  "surveyor",
  "authorized_representative",
];

export const SURVEY_MILESTONES = [
  "visit_scheduled",
  "arrived_on_site",
  "survey_started",
  "survey_completed",
];

export const MILESTONE_ACTORS = ["system", "surveyor", "registrar"];
export const REGISTRAR_DECISIONS = ["approved", "rejected", "needs_correction"];
