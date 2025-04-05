import streamlit as st
from job_search_core import perform_search
from job_analysis import analyze_job_for_sponsorship_and_keywords

# Initialize session state keys
if "filtered_jobs" not in st.session_state:
    st.session_state["filtered_jobs"] = []
if "ai_results" not in st.session_state:
    st.session_state["ai_results"] = []

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
        ["", "full time", "part time", "contract", "temporary", "internship", "volunteer"],
    )
    remote_filter = st.selectbox("Remote Option", ["", "on-site", "remote", "hybrid"])
    experience_level = st.selectbox(
        "Experience Level",
        ["", "internship", "entry level", "associate", "senior", "director", "executive"],
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

# --- Search Button ---
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
            progress_bar = st.progress(0)
            status_text = st.empty()
            response_container = st.container()
            ai_results = []  # Local variable to store AI analysis for skipped jobs

            for index, job in enumerate(jobs):
                percent_complete = int((index + 1) / total_jobs * 100)
                status_text.text(f"🔎 Analyzing job {index + 1} of {total_jobs} ({percent_complete}% complete)...")
                try:
                    if need_sponsorship == "Yes":
                        # Run AI analysis
                        analysis = analyze_job_for_sponsorship_and_keywords(job)
                        sponsorship_status = analysis["sponsorship_available"]
                        keywords = analysis["ats_keywords"]

                        # If sponsorship is not available, store AI analysis and skip this job
                        if sponsorship_status != "yes":
                            ai_results.append({
                                "index": index + 1,
                                "jobUrl": job["jobUrl"],
                                "sponsorship": sponsorship_status,
                                "ats_keywords": keywords
                            })
                            progress_bar.progress((index + 1) / total_jobs)
                            continue

                        # Add job to filtered list if it meets criteria
                        job["visa_sponsorship"] = "✅ Yes"
                        job["ats_keywords"] = keywords
                        filtered_jobs.append(job)

                    else:
                        # When sponsorship is not required, skip AI analysis
                        job["visa_sponsorship"] = "Not required"
                        filtered_jobs.append(job)

                    progress_bar.progress((index + 1) / total_jobs)
                except Exception as e:
                    st.error(f"Error during analysis: {e}")
                    break

            progress_bar.empty()
            status_text.text("✅ Finished analyzing jobs.")

            # Store filtered jobs and AI results in session state for persistence
            st.session_state["filtered_jobs"] = filtered_jobs
            st.session_state["ai_results"] = ai_results

# ---- Display Results from Session State ----
if st.session_state["filtered_jobs"]:
    st.success(f"Found {len(st.session_state['filtered_jobs'])} job(s):")
    for index, job in enumerate(st.session_state["filtered_jobs"]):
        job_title = job.get("position", f"Job {index + 1}")
        container_key = f"container_{index}_{job['jobUrl']}"
        with st.container(key=container_key):
            with st.expander(f"{index + 1}. {job_title} @ {job['company']}"):
                st.markdown(f"**Location:** {job['location']}")
                st.markdown(f"**Posted:** {job['agoTime']}")
                st.markdown(f"**Visa Sponsorship Available?** {job['visa_sponsorship']}")
                st.markdown(f"[🔗 View Job on LinkedIn]({job['jobUrl']})")
                if job.get("ats_keywords"):
                    st.markdown("**Top ATS Keywords:**")
                    st.write("• " + "\n• ".join(job["ats_keywords"]))
                preview = job.get("description_preview", "No preview available.")
                st.markdown("**Job Preview:**")
                st.markdown(preview)
                
                # Use a session state flag to control full description display
                flag_key = f"show_full_flag_{index}"
                if st.button("Show Full Job Details", key=f"show_full_btn_{index}"):
                    st.session_state[flag_key] = True

                if st.session_state.get(flag_key, False):
                    full_description = job.get("full_description", "Full description not available.")
                    st.markdown("**Full Job Description:**")
                    st.markdown(full_description)

else:
    st.warning("No jobs found matching your criteria or sponsorship requirement.")
    if need_sponsorship == "Yes" and st.session_state.get("ai_results"):
        with st.expander("🧠 See AI Analysis for Skipped Jobs"):
            for res in st.session_state["ai_results"]:
                color = "green" if res["sponsorship"] == "yes" else "red"
                st.markdown(
                    f'AI Response for Job {res["index"]}: '
                    f'<span style="color:{color}; font-weight:bold;">{res["sponsorship"].upper()}</span><br>'
                    f'<a href="{res["jobUrl"]}" target="_blank">🔗 LinkedIn Link</a>',
                    unsafe_allow_html=True
                )
                if res["ats_keywords"]:
                    st.markdown("**Top ATS Keywords:**")
                    st.write("• " + "\n• ".join(res["ats_keywords"]))
                st.markdown("---")
