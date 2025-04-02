from typing import TypedDict, List, Any, Optional
from linkedin_scraper import LinkedInJobScraper


# Define a TypedDict for the job listing structure
class JobListing(TypedDict):
    position: str
    company: str
    location: str
    date: str  # ISO date string when the job was posted
    agoTime: str  # Human-readable relative time (e.g., "3 weeks ago")
    salary: str
    jobUrl: str
    companyLogo: str


def perform_search(
    keyword: str = "",
    location: str = "",
    date_posted: str = "",
    job_type: str = "",
    remote: str = "",
    salary: str = "",
    experience: str = "",
    sort_by: str = "",
    page: int = 0,
    limit: int = 0,
) -> List[JobListing]:
    """
    Perform a LinkedIn job search with the given filters and return a list of JobListing objects.
    """
    # Initialize the scraper with provided filters
    scraper = LinkedInJobScraper(
        keyword=keyword,
        location=location,
        date_posted=date_posted,
        job_type=job_type,
        remote=remote,
        salary=salary,
        experience=experience,
        sort_by=sort_by,
        page=page,
        limit=limit,
    )
    # Fetch job listings
    jobs_data = scraper.search_jobs()
    # The scraper returns a list of dict; we ensure each is typed as JobListing for clarity
    jobs: List[JobListing] = [job for job in jobs_data]  # type: ignore
    return jobs
