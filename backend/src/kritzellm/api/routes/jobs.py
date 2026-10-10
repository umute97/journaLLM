from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from ..errors import not_implemented, problem_responses
from ..schemas.jobs import Job, JobKind, JobList, JobStatus
from .params import BINARY, JOB_LOCATION, CursorQuery, JobIdPath, Limit

router = APIRouter()


@router.get(
    "/jobs",
    summary="List jobs",
    tags=["jobs"],
    responses=problem_responses(400, 401, 422),
)
async def list_jobs(
    job_status: Annotated[
        JobStatus | None, Query(alias="status", description="Only jobs in this status.")
    ] = None,
    kind: Annotated[JobKind | None, Query(description="Only jobs of this kind.")] = None,
    limit: Limit = 25,
    cursor: CursorQuery = None,
) -> JobList:
    """Lists background jobs, newest first."""
    not_implemented()


@router.get(
    "/jobs/{jobId}",
    summary="Get a job",
    tags=["jobs"],
    responses=problem_responses(400, 401, 404, 422),
)
async def get_job(job_id: JobIdPath) -> Job:
    """Returns a job's status and progress. Poll this after a `202 Accepted`."""
    not_implemented()


@router.get(
    "/jobs/{jobId}/result",
    response_class=Response,
    summary="Download a job's result",
    tags=["jobs"],
    responses={
        200: {
            "description": "The result file, with a `Content-Disposition` filename.",
            "content": {"application/zip": BINARY},
        },
        **problem_responses(400, 401, 404, 409, 422),
    },
)
async def get_job_result(job_id: JobIdPath) -> Response:
    """Downloads the file a finished job produced (currently only exports).

    Returns `409` while the job hasn't succeeded.
    """
    not_implemented()


@router.post(
    "/admin/reindex",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Re-index everything",
    tags=["admin"],
    responses={202: {"headers": JOB_LOCATION}, **problem_responses(400, 401, 409)},
)
async def reindex_all() -> Job:
    """Rebuilds the search index for all pages, e.g. after switching the embedding model.

    Transcriptions are kept.
    """
    not_implemented()
