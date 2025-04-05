import requests
import random
import time
from bs4 import BeautifulSoup
from typing import List, Optional


class LinkedInJobScraper:
    """Scraper for LinkedIn job listings using LinkedIn's unofficial jobs API."""

    # Base URL for LinkedIn Jobs search (guest access)
    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    BATCH_SIZE = 25  # LinkedIn returns 25 jobs per page by default

    # Define mapping for filter values to LinkedIn query parameters
    DATE_FILTERS = {
        "past month": "r2592000",  # posted in last 30 days
        "past week": "r604800",  # posted in last 7 days
        "24hr": "r86400",  # posted in last 24 hours
    }
    EXPERIENCE_FILTERS = {
        "internship": "1",
        "entry level": "2",
        "associate": "3",
        "senior": "4",
        "director": "5",
        "executive": "6",
    }
    JOB_TYPE_FILTERS = {
        "full time": "F",
        "full-time": "F",
        "part time": "P",
        "part-time": "P",
        "contract": "C",
        "temporary": "T",
        "volunteer": "V",
        "internship": "I",
    }
    REMOTE_FILTERS = {"on site": "1", "on-site": "1", "remote": "2", "hybrid": "3"}
    SALARY_FILTERS = {
        "40000": "1",
        "60000": "2",
        "80000": "3",
        "100000": "4",
        "120000": "5",
    }

    # Some User-Agent strings to rotate for polite scraping
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    ]

    def __init__(
        self,
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
    ):
        """
        Initialize the scraper with search filters.
        - keyword: Job title or keywords to search for.
        - location: Location name (city, state, country, etc.).
        - date_posted: Date filter ('past month', 'past week', '24hr').
        - job_type: Job type filter ('full time', 'part time', 'contract', etc.).
        - remote: Remote filter ('on-site', 'remote', 'hybrid').
        - salary: Minimum salary filter (e.g., '100000' for $100k+).
        - experience: Experience level filter ('internship', 'entry level', etc.).
        - sort_by: 'recent' or 'relevant' for sorting.
        - page: Results page number to start from (0-indexed).
        - limit: Total number of results to retrieve (0 for no specific limit).
        """
        self.keyword = keyword.strip()
        self.location = location.strip()
        self.date_posted = date_posted.strip().lower()
        self.job_type = job_type.strip().lower()
        self.remote = remote.strip().lower()
        self.salary = salary.strip()
        self.experience = experience.strip().lower()
        self.sort_by = sort_by.strip().lower()
        self.page = page if page is not None else 0
        self.limit = limit if limit is not None else 0

    def _build_search_url(self, start: int) -> str:
        """
        Construct the LinkedIn jobs search URL with query parameters for a given start offset.
        The 'start' parameter is the index of the first job to fetch (multiples of 25).
        """
        params = {}
        if self.keyword:
            # Replace spaces with '+' for the keywords (URL encoding will handle others)
            params["keywords"] = self.keyword.replace(" ", "+")
        if self.location:
            params["location"] = self.location.replace(" ", "+")
        if self.date_posted:
            # Map human-readable date filter to LinkedIn code (f_TPR)
            code = self.DATE_FILTERS.get(self.date_posted, "")
            if code:
                params["f_TPR"] = code
        if self.salary:
            # Map salary to LinkedIn salary bucket code (f_SB2)
            code = self.SALARY_FILTERS.get(self.salary, "")
            if code:
                params["f_SB2"] = code
        if self.experience:
            # Map experience level to code (f_E)
            code = self.EXPERIENCE_FILTERS.get(self.experience, "")
            if code:
                params["f_E"] = code
        if self.remote:
            # Map remote filter to code (f_WT)
            code = self.REMOTE_FILTERS.get(self.remote, "")
            if code:
                params["f_WT"] = code
        if self.job_type:
            # Map job type to code (f_JT)
            code = self.JOB_TYPE_FILTERS.get(self.job_type, "")
            if code:
                params["f_JT"] = code
        # Sorting: 'recent' -> DD (date descending), 'relevant' -> R (relevance)
        if self.sort_by:
            if self.sort_by == "recent":
                params["sortBy"] = "DD"
            elif self.sort_by == "relevant":
                params["sortBy"] = "R"
        # Set the start offset combining page offset and batch offset
        params["start"] = start + (self.page * self.BATCH_SIZE)
        # Build full URL with encoded query string
        query_string = "&".join(
            f"{key}={requests.utils.requote_uri(str(value))}"
            for key, value in params.items()
        )
        return f"{self.BASE_URL}?{query_string}"

    def _parse_jobs_from_html(self, html: str) -> List[dict]:
        """
        Parse the HTML fragment returned by LinkedIn and extract job listing data.
        Returns a list of job dictionaries.
        """
        soup = BeautifulSoup(html, "html.parser")
        job_elements = soup.find_all("li")  # Each job posting is in an <li> element
        jobs = []
        for li in job_elements:
            try:
                title_elem = li.find("h3", class_="base-search-card__title")
                company_elem = li.find("h4", class_="base-search-card__subtitle")
                location_elem = li.find("span", class_="job-search-card__location")
                date_elem = li.find("time", class_="job-search-card__listdate")
                salary_elem = li.find("span", class_="job-search-card__salary-info")
                link_elem = li.find("a", class_="base-card__full-link")
                logo_elem = li.find("img", class_="artdeco-entity-image")

                position = title_elem.get_text(strip=True) if title_elem else None
                company = company_elem.get_text(strip=True) if company_elem else None
                location = location_elem.get_text(strip=True) if location_elem else None
                date = (
                    date_elem["datetime"] if date_elem else None
                )  # ISO date from datetime attribute
                ago_time = (
                    date_elem.get_text(strip=True) if date_elem else None
                )  # e.g., "3 weeks ago"
                salary = None
                if salary_elem:
                    salary_text = salary_elem.get_text(
                        " ", strip=True
                    )  # get salary with spaces normalized
                    salary = salary_text if salary_text else None
                job_url = link_elem["href"] if link_elem else None
                # LinkedIn may provide a company logo image URL (often in data-delayed-url attribute)
                company_logo = None
                if logo_elem:
                    # data-delayed-url holds the actual image src if lazy-loaded
                    company_logo = logo_elem.get("data-delayed-url") or logo_elem.get(
                        "src"
                    )

                # Only include the job if it has at least title and company
                if position and company:
                    jobs.append(
                        {
                            "position": position,
                            "company": company,
                            "location": location or "",
                            "date": date or "",
                            "agoTime": ago_time or "",
                            "salary": salary or "Not specified",
                            "jobUrl": job_url or "",
                            "companyLogo": company_logo or "",
                        }
                    )
            except Exception as e:
                # If a parsing error occurs for a job element, skip it
                continue
        return jobs

    def search_jobs(self) -> List[dict]:
        """
        Execute the job search with the given filters. It fetches multiple pages (batches of 25 jobs)
        until the specified limit is reached or no more jobs are found.
        Returns a list of job listings (each as a dict).
        """
        results: List[dict] = []
        start_offset = 0
        consecutive_errors = 0
        max_errors = (
            3  # stop if 3 consecutive errors (to avoid infinite loop in case of issues)
        )

        while True:
            # Build URL for current batch
            url = self._build_search_url(start_offset)
            # Prepare headers (random User-Agent for each batch request)
            headers = {
                "User-Agent": random.choice(self.USER_AGENTS),
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.linkedin.com/jobs",  # Referer set to jobs page
                "X-Requested-With": "XMLHttpRequest",  # Indicate AJAX request
            }
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                # LinkedIn returns HTTP 200 with an HTML snippet for valid queries.
                # If status is not 200, or content is empty, we consider it an error.
                if resp.status_code != 200 or not resp.text:
                    # If we hit a rate limit (429) or any error status, handle accordingly
                    if resp.status_code == 429:
                        raise Exception("Rate limit reached (HTTP 429)")
                    raise Exception(f"Request failed with status {resp.status_code}")
                # Parse jobs from the returned HTML content
                batch_jobs = self._parse_jobs_from_html(resp.text)
                if not batch_jobs:
                    # No jobs returned – end of results
                    break
                results.extend(batch_jobs)
                # If a limit is set and we've reached or exceeded it, truncate and stop
                if self.limit and len(results) >= self.limit:
                    results = results[: self.limit]
                    break
                # Prepare for next batch
                start_offset += self.BATCH_SIZE
                consecutive_errors = 0  # reset error counter on success
                # Pause between requests to avoid overwhelming the server (politeness delay)
                time.sleep(2 + random.random())  # 2 to 3 seconds delay
            except Exception as err:
                consecutive_errors += 1
                print(f"Error fetching jobs at offset {start_offset}: {err}")
                if consecutive_errors >= max_errors:
                    print(
                        "Maximum consecutive errors reached. Stopping further requests."
                    )
                    break
                # Exponential backoff before retrying the batch that failed
                time.sleep((2**consecutive_errors) * 1)  # 2s, 4s, 8s...
                # (Loop will retry the same offset without incrementing it)
        return results
