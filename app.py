import streamlit as st
from job_search_core import perform_search
from job_analysis import analyze_job_for_sponsorship

st.set_page_config(page_title="LinkedIn Job Sponsor AI", layout="wide")
st.title("🔍 LinkedIn Job Sponsor AI")

# --- User Inputs ---
keyword = st.text_input("Job Title or Skills", placeholder="e.g., Software Engineer")
location = st.text_input("Location", "United States")

col1, col2 = st.columns(2)

with col1:
    date_posted = st.selectbox(
        "Date Posted",
        ["", "24hr", "past week", "past month"],
        help="Filter jobs posted within the selected timeframe.",
    )
    job_type = st.selectbox(
        "Job Type",
        [
            "",
            "full time",
            "part time",
            "contract",
            "temporary",
            "internship",
            "volunteer",
        ],
    )
    remote_filter = st.selectbox("Remote Option", ["", "on-site", "remote", "hybrid"])
    experience_level = st.selectbox(
        "Experience Level",
        [
            "",
            "internship",
            "entry level",
            "associate",
            "senior",
            "director",
            "executive",
        ],
    )

with col2:
    minimum_salary = st.selectbox(
        "Minimum Salary",
        ["", "40000", "60000", "80000", "100000", "120000"],
        help="Minimum expected salary in USD.",
    )
    limit_results = st.slider(
        "Limit Number of Results",
        min_value=5,
        max_value=50,
        value=10,
        help="Number of jobs to display. Recommended: 10–20 for faster performance.",
    )
    page_number = st.number_input(
        "Page Number to Start From",
        min_value=0,
        value=0,
        help="Pagination: 0 = first page, 1 = second page, etc.",
    )
    sort_by = st.selectbox(
        "Sort By",
        ["relevant", "recent"],
        help="Sort job listings by relevance or most recent first.",
    )

need_sponsorship = st.radio(
    "Do you require visa sponsorship?", ("Yes", "No"), horizontal=True
)

# --- Submit Button ---
if st.button("🚀 Search Jobs"):
    if not location:
        st.warning("Please enter at least a Location.")
    else:
        with st.spinner("Fetching jobs from LinkedIn..."):
            jobs = perform_search(
                keyword=keyword,
                location=location,
                date_posted=date_posted,
                job_type=job_type,
                remote=remote_filter,
                experience=experience_level,
                salary=minimum_salary,
                limit=limit_results,
                page=page_number,
                sort_by=sort_by,
            )

            filtered_jobs = []
            total_jobs = len(jobs)

            # Progress bar + status message container
            progress_bar = st.progress(0)
            status_text = st.empty()
            response_container = st.container()
            responses_so_far = []  # List of markdown-formatted strings

            for index, job in enumerate(jobs):
                status_text.text(f"🔎 Analyzing job {index + 1} of {total_jobs}...")

                if need_sponsorship == "Yes":
                    try:
                        sponsorship_status = analyze_job_for_sponsorship(job)

                        if sponsorship_status == "yes":
                            job["visa_sponsorship"] = "✅ Yes"
                            filtered_jobs.append(job)

                        # Append result for just this job
                        with response_container:
                            color = "green" if sponsorship_status == "yes" else "red"
                            st.markdown(
                                f"AI Response for Job {index + 1}: "
                                f'<span style="color:{color}; font-weight:bold;">{sponsorship_status.upper()}</span><br>'
                                f'<a href="{job["jobUrl"]}" target="_blank">🔗 LinkedIn Link</a><hr>',
                                unsafe_allow_html=True,
                            )

                    except Exception as e:
                        st.error(f"Error during analysis: {e}")
                        break
                else:
                    job["visa_sponsorship"] = "Not required"
                    filtered_jobs.append(job)

                progress_bar.progress((index + 1) / total_jobs)

            # Final status
            progress_bar.empty()
            status_text.text("✅ Finished analyzing jobs.")

        # --- Display Results ---
        if filtered_jobs:
            st.success(f"Found {len(filtered_jobs)} job(s):")
            for job in filtered_jobs:
                with st.expander(f"{job['position']} @ {job['company']}"):
                    st.markdown(f"**Location:** {job['location']}")
                    st.markdown(f"**Posted:** {job['agoTime']}")
                    st.markdown(f"**Salary:** {job['salary']}")
                    st.markdown(f"[🌐 View Job on LinkedIn]({job['jobUrl']})")
                    if need_sponsorship == "Yes":
                        st.markdown(
                            f"**Visa Sponsorship Available?** {job['visa_sponsorship']}"
                        )
        else:
            st.warning(
                "No jobs found matching your criteria or sponsorship requirement."
            )
