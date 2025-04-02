from job_search_core import perform_search, JobListing
from job_analysis import analyze_job_for_sponsorship


def prompt_user_for_filters() -> dict:
    print("** LinkedIn Job Search **")
    keyword = input("Keyword(s) (e.g., job title or skills): ").strip()
    location = input("Location (e.g., city, state, or country): ").strip()
    date_posted = input(
        "Date posted filter [24hr / past week / past month] (leave blank for none): "
    ).strip()
    job_type = input(
        "Job type [full time / part time / contract / etc.] (leave blank for none): "
    ).strip()
    remote = input(
        "Remote filter [on-site / remote / hybrid] (leave blank for none): "
    ).strip()
    experience = input(
        "Experience level [internship / entry level / associate / senior / director / executive] (leave blank for none): "
    ).strip()
    salary = input(
        "Minimum salary (e.g., 40000 for $40k+, leave blank for none): "
    ).strip()
    limit = input(
        "Limit number of results (e.g., 10, or leave blank for no limit): "
    ).strip()
    page = input("Page number to start from (0 for first page): ").strip()
    sort_by = input(
        "Sort by [recent / relevant] (leave blank for default relevance): "
    ).strip()
    need_sponsorship = (
        input("Do you require visa sponsorship? (yes/no): ").strip().lower()
    )

    limit_num = int(limit) if limit else 0
    page_num = int(page) if page else 0

    return {
        "keyword": keyword,
        "location": location,
        "date_posted": date_posted,
        "job_type": job_type,
        "remote": remote,
        "experience": experience,
        "salary": salary,
        "limit": limit_num,
        "page": page_num,
        "sort_by": sort_by,
        "need_sponsorship": need_sponsorship == "yes",
    }


def main():
    filters = prompt_user_for_filters()
    print("\nSearching LinkedIn for jobs...\n")

    jobs = perform_search(
        keyword=filters["keyword"],
        location=filters["location"],
        date_posted=filters["date_posted"],
        job_type=filters["job_type"],
        remote=filters["remote"],
        experience=filters["experience"],
        salary=filters["salary"],
        limit=filters["limit"],
        page=filters["page"],
        sort_by=filters["sort_by"],
    )

    if not jobs:
        print("No jobs found for the given criteria.")
        return

    filtered_jobs = []

    for job in jobs:
        if filters["need_sponsorship"]:
            sponsorship_available = analyze_job_for_sponsorship(job)
            if sponsorship_available == "yes":
                job["visa_sponsorship"] = "Yes"
                filtered_jobs.append(job)
        else:
            # No visa analysis required
            job["visa_sponsorship"] = "N/A"
            filtered_jobs.append(job)

    if not filtered_jobs:
        print("No jobs found that offer visa sponsorship based on your criteria.")
        return

    print(f"\nFound {len(filtered_jobs)} job(s).")
    print("Results:\n" + "-" * 60)

    for job in filtered_jobs:
        print(f"Title: {job['position']}")
        print(f"Company: {job['company']}  |  Location: {job['location']}")
        print(f"Posted: {job['agoTime']}  |  URL: {job['jobUrl']}")

        if filters["need_sponsorship"]:
            print(f"Visa Sponsorship Available?: {job['visa_sponsorship']}")

        print("-" * 60)


if __name__ == "__main__":
    main()
