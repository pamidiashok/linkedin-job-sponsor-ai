import os
import time
import random
import requests
from bs4 import BeautifulSoup
from typing import TypedDict, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from job_search_core import JobListing

# Initialize OpenAI LLM with your API key
llm = ChatOpenAI(
    model="gpt-3.5-turbo", temperature=0, api_key=os.getenv("OPENAI_API_KEY")
)

prompt = PromptTemplate(
    input_variables=["description"],
    template=(
        "Carefully read the following job description. Only respond 'yes' if the company explicitly states "
        "they offer visa sponsorship. If sponsorship is not explicitly mentioned or explicitly denied, respond 'no'.\n\n"
        "Job Description:\n{description}\n\n"
        "Visa Sponsorship available? (yes or no):"
    ),
)

ats_prompt = PromptTemplate(
    input_variables=["description"],
    template=(
        "Analyze the following job description and extract the top 10 keywords or phrases that an Applicant Tracking System (ATS) might prioritize.\n\n"
        "Focus on technical skills, certifications, tools, and job-relevant terminology.\n\n"
        "Job Description:\n{description}\n\n"
        "Top 10 ATS Keywords:"
    )
)

# Define the structure for the agent state
class JobState(TypedDict):
    description: str
    sponsorship_available: str  # explicitly "yes" or "no"


def fetch_full_job_description(job_url: str) -> Optional[str]:
    """
    Fetch the complete job description from LinkedIn using their guest-access API endpoint.
    Includes debug statements for clear visibility into fetched descriptions.
    """
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.linkedin.com/jobs",
    }

    # Extract the job ID explicitly from URL
    try:
        job_id = job_url.split("/")[-1].split("?")[0].split("-")[-1]
        detail_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    except Exception as e:
        print(f"[Debug] Invalid URL format for {job_url}: {e}")
        return None

    try:
        response = requests.get(detail_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        description_section = soup.find("div", class_="show-more-less-html__markup")

        if description_section:
            description_text = description_section.get_text(separator="\n").strip()

            # Debug output explicitly showing fetched description snippet
            print(
                f"[Debug] Successfully fetched description for URL ({detail_url}):\n"
                f"{'-'*60}\n"
                f"{description_text[:500]}...\n"  # Display first 500 chars explicitly
                f"{'-'*60}\n"
            )

            return description_text
        else:
            print(f"[Debug] No description found at {detail_url}")
            return None
    except Exception as e:
        print(f"[Debug] Error fetching description from {detail_url}: {e}")
        return None
    finally:
        # Polite and clearly random delay to avoid blocking
        time.sleep(random.uniform(3, 5))


def sponsorship_detection_node(state: JobState):
    """
    LangChain node clearly analyzing if visa sponsorship is explicitly offered or not.
    """

    message = HumanMessage(content=prompt.format(description=state["description"]))
    response = llm.invoke([message]).content.strip().lower()

    print(
        "AI Prompt:\n", prompt.format(description=state["description"])[:500], "..."
    )  # Debug
    print("AI Response:", response)  # Debug

    # Clearly ensure the response is strictly 'yes' or 'no'
    sponsorship_available = "yes" if "yes" in response else "no"
    return {"sponsorship_available": sponsorship_available}


def analyze_job_for_sponsorship_and_keywords(job: JobListing) -> dict:
    """
    Runs both visa sponsorship detection and ATS keyword extraction on a job description.
    Returns a dictionary with 'sponsorship_available' and 'ats_keywords'.
    """
    description = fetch_full_job_description(job['jobUrl'])
    if not description:
        return {"sponsorship_available": "no", "ats_keywords": []}

    # --- Run visa sponsorship check ---
    sponsor_msg = HumanMessage(content=prompt.format(description=description))
    sponsorship_response = llm.invoke([sponsor_msg]).content.strip().lower()
    sponsorship_status = "yes" if "yes" in sponsorship_response else "no"

    # --- Run ATS keyword extraction ---
    ats_msg = HumanMessage(content=ats_prompt.format(description=description))
    ats_response = llm.invoke([ats_msg]).content.strip()
    ats_keywords = [kw.strip("-• ").strip() for kw in ats_response.split("\n") if kw.strip()]

    return {
        "sponsorship_available": sponsorship_status,
        "ats_keywords": ats_keywords
    }

