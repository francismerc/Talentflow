"""Read-focused Supabase query modules."""

from app.database.queries.applicants import ApplicantQueries
from app.database.queries.jobs import JobQueries

__all__ = ["ApplicantQueries", "JobQueries"]
