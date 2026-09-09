# Course Content Simplification Agent

**AICTE 2026 Internship · Problem Statement #24**

An AI-powered web application that simplifies academic course content into clear,
digestible explanations tailored to a student's knowledge level — powered by
**IBM Granite** via **IBM watsonx.ai**.

---

## What it does

Paste any academic text (a textbook paragraph, lecture notes, a concept definition),
choose a learner level, and the app returns:

- A **simplified explanation** written for that level
- A list of **Key Concepts**
- A list of **Key Points to Remember**
- A short **Summary**

Three learner levels are supported:

| Level | Who it's for |
|---|---|
| **Beginner** | No prior knowledge; plain language, no jargon |
| **Intermediate** | Some background; technical terms briefly explained |
| **Advanced** | Strong subject knowledge; precise, in-depth language |

---

## IBM Cloud services used

| Service | Purpose |
|---|---|
| **IBM watsonx.ai Runtime** (us-south, Dallas) | Hosts the IBM Granite model and exposes the REST API |
| **IBM Granite** (`ibm/granite-4-h-small`) | Foundation model that generates the simplified explanations |

Both services are available on the **IBM Cloud Lite (free) plan**.

---

## Prerequisites

- Python 3.10 or later — [python.org/downloads](https://www.python.org/downloads/)
- An IBM Cloud account with a watsonx.ai project set up
- Your IBM Cloud API key and watsonx.ai Project ID

---

## Setup — step by step

### 1. Clone or download the project

```
git clone <your-repo-url>
cd Course_Content_Simplifier
```

Or simply open the project folder in your editor.

### 2. Create a Python virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> If `python` is not found, use the full path, for example:
> `C:\Users\YourName\AppData\Local\Programs\Python\Python310\python.exe -m venv .venv`

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

This installs Flask, the IBM watsonx.ai SDK, and python-dotenv.

### 4. Create your `.env` file

Copy the example template:

```
cp .env.example .env        # macOS / Linux
copy .env.example .env      # Windows Command Prompt
Copy-Item .env.example .env # Windows PowerShell
```

Open `.env` and fill in your two secret values:

```
WATSONX_API_KEY=<your IBM Cloud API key>
WATSONX_PROJECT_ID=<your watsonx.ai Project ID>
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-4-h-small
```

Where to find each value:

| Variable | Location |
|---|---|
| `WATSONX_API_KEY` | IBM Cloud → Manage → Access (IAM) → API keys |
| `WATSONX_PROJECT_ID` | watsonx.ai → Your project → Manage tab → General → Project ID |
| `WATSONX_URL` | Fixed for Dallas region — do not change |
| `WATSONX_MODEL_ID` | Fixed — do not change |

> **Security note:** The `.env` file is listed in `.gitignore` and will never be
> committed to Git. Never share or upload this file.

### 5. Run the application

```
python app.py
```

Open your browser and go to: **http://127.0.0.1:5000**

---

## Project structure

```
Course_Content_Simplifier/
│
├── app.py              # Flask backend — all server logic (~200 lines, heavily commented)
├── requirements.txt    # Pinned Python dependencies
├── .env                # Your credentials (never committed to Git)
├── .env.example        # Credential template (safe to share)
├── .gitignore          # Excludes .env, __pycache__, .venv
├── plan.md             # Implementation plan
│
├── templates/
│   └── index.html      # Single-page UI (Jinja2 template)
│
└── static/
    └── style.css       # Stylesheet (no external CDN dependencies)
```

---

## How the application works

```
Browser (HTML form)
      |  HTTP POST /simplify
      v
Flask app.py
      |  ibm-watsonx-ai SDK
      v
IBM watsonx.ai Runtime  →  IBM Granite (ibm/granite-4-h-small)
      |  Simplified text response
      v
Flask renders result back into index.html
```

1. The student pastes content and selects a level, then submits the form.
2. Flask reads the form values and builds a structured prompt tailored to the chosen level.
3. The prompt is sent to IBM Granite via the `ibm-watsonx-ai` Python SDK.
4. Granite returns a response with four labelled sections.
5. Flask parses the sections and passes them to the HTML template.
6. The page re-renders with the simplified explanation, key concepts, key points, and summary.

---

## Demonstrating Problem Statement #24 compliance

| Requirement | How it is met |
|---|---|
| AI-powered simplification agent | IBM Granite (`ibm/granite-4-h-small`) generates all explanations |
| IBM Cloud Lite / IBM Granite | watsonx.ai Runtime on Lite plan; Granite model confirmed in Prompt Lab |
| Different learner levels | Beginner / Intermediate / Advanced — prompt changes vocabulary and depth |
| Clear digestible explanations | Structured output: Simplified Explanation + Key Concepts + Key Points + Summary |
| Simple student-facing UI | Single page — paste, select level, click Simplify, read result |

To demonstrate to evaluators:
1. Paste a paragraph from a university textbook.
2. Run it at **Beginner** level — show the simple vocabulary output.
3. Run the same paragraph at **Advanced** level — show the depth difference.
4. Show the IBM Cloud dashboard with the watsonx.ai Runtime service active.
5. Show `app.py` line 41 where the model ID `ibm/granite-4-h-small` is loaded from `.env`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `MISSING .env variables` on startup | Open `.env` and make sure `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are filled in |
| `Provided API key could not be found` | Re-generate your API key in IBM Cloud IAM — keys can only be viewed once at creation |
| Page shows error after submit | Check the error message on screen; it shows the exact SDK error |
| `python` not found on Windows | Use the full path to your Python install, or add it to your PATH |
| Blank result (no sections shown) | The model may have returned unstructured text; the raw output is shown as the explanation |

---

## Running again after closing the terminal

```powershell
# Windows PowerShell — from the project folder
.\.venv\Scripts\Activate.ps1
python app.py
```

---

*Built for AICTE 2026 · Problem Statement #24 · Course Content Simplification Agent*
