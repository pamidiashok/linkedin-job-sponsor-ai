# linkedin-job-sponsor-ai

[![Creator](https://img.shields.io/badge/made%20by-pamidiashok-blue)](https://github.com/pamidiashok)
[![GitHub Repo stars](https://img.shields.io/github/stars/pamidiashok/linkedin-job-sponsor-ai)](https://github.com/pamidiashok/linkedin-job-sponsor-ai/stargazers)
[![Code size](https://img.shields.io/github/languages/code-size/pamidiashok/linkedin-job-sponsor-ai)](https://github.com/pamidiashok/linkedin-job-sponsor-ai)
[![Issues](https://img.shields.io/github/issues/pamidiashok/linkedin-job-sponsor-ai)](https://github.com/pamidiashok/linkedin-job-sponsor-ai/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent LinkedIn job search and analysis tool built with Python, Streamlit, and GPT (via LangChain), designed to help users filter job listings based on visa sponsorship availability. The app provides a simple UI to search jobs and uses AI to read job descriptions and detect whether the job offers sponsorship — going far beyond basic keyword matching.

---

## 🚀 What This Project Does

- Searches LinkedIn for job listings based on filters like title, location, posting date, remote options, salary, etc.
- Retrieves full job descriptions using LinkedIn’s guest-access job API.
- Uses an AI agent (powered by OpenAI GPT via LangChain) to analyze the **full job description**, and intelligently decide whether visa sponsorship is available.
- Visually shows job-by-job sponsorship responses in real-time with colored feedback (`YES` = green, `NO` = red).
- Offers both **CLI** and **Streamlit web UI** options to use the tool.

---

## 🧠 How the AI Agent Works

This project integrates **LangChain** and **OpenAI GPT** (GPT-4 or GPT-3.5) to build a modular and intelligent reasoning pipeline:

- Full job descriptions are passed through a **LangChain PromptTemplate** that asks the model to infer visa sponsorship availability.
- The AI agent doesn't just look for keywords — it understands nuance. For example:
  - `"Visa sponsorship is not available"` → ❌ `no`
  - `"Sponsorship may be available"` or `"We offer sponsorship"` → ✅ `yes`
- This logic is built in a reusable agent function that can be extended to include more capabilities (e.g., job classification or summarization).

---

## 💡 Why LangChain?

We use [LangChain](https://www.langchain.com/) to:

- Create structured agent flows (state management, prompt templates).
- Modularize LLM interactions for clarity and extensibility.
- Provide cleaner integration with OpenAI’s GPT models via `langchain-openai`.

LangChain lets us build a more explainable and maintainable AI logic pipeline — rather than using raw prompts directly.

---

## 🧠 How LangChain Is Used

This project uses **LangChain** to create a structured, intelligent, and maintainable AI reasoning pipeline.

### 🔹 What LangChain brings to the table:

- **Prompt templating:** We use `PromptTemplate` to define a consistent, reusable question to the language model asking it to determine visa sponsorship availability.
- **State handling:** LangChain’s structure helps us build typed and clean data flows (`TypedDict` state).
- **Model invocation:** We use LangChain’s `ChatOpenAI` interface to cleanly communicate with GPT (gpt-4 or gpt-3.5), while keeping the code modular and production-ready.
- **Extensibility:** With LangChain, it’s easy to later add more "nodes" like:
  - Classify jobs by industry
  - Extract named entities (company, technologies)
  - Summarize job descriptions

### 📦 Code Example:

```python
prompt = PromptTemplate(
    input_variables=["description"],
    template=(
        "Carefully read the following job description. Only respond 'yes' if the company explicitly states "
        "they offer visa sponsorship. If not mentioned or denied, respond 'no'.\n\n"
        "Job Description:\n{description}\n\nVisa Sponsorship available? (yes or no):"
    )
)

message = HumanMessage(content=prompt.format(description=state["description"]))
sponsorship = llm.invoke([message]).content.strip().lower()
```

---

## 📂 Project Structure

| File                  | Purpose                                                                                   |
| --------------------- | ----------------------------------------------------------------------------------------- |
| `linkedin_scraper.py` | Fetches job listings from LinkedIn using the filters provided.                            |
| `job_search_core.py`  | Coordinates the job search process and pagination.                                        |
| `job_analysis.py`     | Uses LangChain + GPT to analyze job descriptions and determine if sponsorship is offered. |
| `main.py`             | Command-line interface to enter search filters and display results.                       |
| `app.py`              | Interactive Streamlit UI for job search with real-time AI responses and visual feedback.  |
| `requirements.txt`    | All Python dependencies, including LangChain, OpenAI, Streamlit, BeautifulSoup, etc.      |

---

## 🧭 Architecture Diagram

This diagram illustrates the flow of the AI-powered job search application, from user input to job result analysis using GPT and LangChain.

![AI Job Search Architecture](screenshots/linkedin-job-sponsor-ai.png)

---

## 🌐 Run the Interactive Web App (Recommended)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set OpenAI API Key

```bash
export OPENAI_API_KEY='your-api-key'
```

> Or set it in your .env file or directly in job_analysis.py.

### Step 3: Launch the App

```bash
streamlit run app.py
```

Then open your browser at:
📍 http://localhost:8501

## 🙌 Credits

Thanks to the following open-source tools and libraries that made this project possible:

| Tool                                                            | Description                                                                                            |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| [OpenAI](https://platform.openai.com/)                          | Powers the AI model (GPT-4 / GPT-3.5) that analyzes job descriptions for visa sponsorship intent.      |
| [LangChain](https://www.langchain.com/)                         | Provides prompt templating, state management, and integration with OpenAI to build intelligent agents. |
| [Streamlit](https://streamlit.io/)                              | Used to create the modern, interactive web UI with real-time feedback and controls.                    |
| [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) | Parses HTML content to extract job descriptions from LinkedIn's job posting pages.                     |
| [Requests](https://docs.python-requests.org/)                   | Handles HTTP requests to fetch job data and descriptions from LinkedIn's guest-access job API.         |
| ❤️ **You**                                                      | For using, testing, and improving this project — and giving feedback to make it better!                |

## Contributing

Feel free to contribute!

1. Fork the repository
2. Make changes
3. Submit a pull request
