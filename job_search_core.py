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
    # New optional fields for job description preview and full description:
    description_preview: Optional[str]
    full_description: Optional[str]

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
    Adds a 'description_preview' field and a 'full_description' field to each job for further processing.
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
    jobs: List[JobListing] = list(jobs_data)
    
    from job_analysis import fetch_full_job_description
    
    # For each job, add description preview and full description if not present
    for job in jobs:
        # Check if 'full_description' exists; if not, use an empty string
        full_desc = job.get("full_description", "") or (fetch_full_job_description(job["jobUrl"]) or "")
        # Optionally, if you have a method to fetch full description separately, call it here.
        # For now, we assume the scraper either returns it or it remains empty.
        job["full_description"] = full_desc or "Full description not available."

        # Create a preview from the full description (e.g., first 200 characters)
        if full_desc:
            job["description_preview"] = f"{full_desc[:200]}..."
        else:
            job["description_preview"] = "No preview available."

    return jobs
