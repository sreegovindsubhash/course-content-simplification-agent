# =============================================================================
# Course Content Simplification Agent
# AICTE 2026 — Problem Statement #24
#
# This file is the entire backend.  It:
#   1. Loads your IBM Cloud credentials from the .env file.
#   2. Serves the HTML page at http://127.0.0.1:5000
#   3. Receives the form submission (course text + learner level).
#   4. Builds a structured prompt and calls IBM Granite via watsonx.ai.
#   5. Parses the response and sends it back to the page.
# =============================================================================

# ── Standard library ──────────────────────────────────────────────────────────
import os

# ── Third-party: web framework ────────────────────────────────────────────────
from flask import Flask, render_template, request

# ── Third-party: load variables from the .env file ────────────────────────────
from dotenv import load_dotenv

# ── Third-party: IBM watsonx.ai SDK ───────────────────────────────────────────
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as Params

# =============================================================================
# 1. Load credentials
#    python-dotenv reads the .env file and makes its values available via
#    os.environ, exactly as if you had set them as system environment variables.
# =============================================================================
load_dotenv()

WATSONX_API_KEY   = os.environ.get("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.environ.get("WATSONX_PROJECT_ID")
WATSONX_URL       = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_MODEL_ID  = os.environ.get("WATSONX_MODEL_ID", "ibm/granite-4-h-small")

# =============================================================================
# 2. Create the Flask application
# =============================================================================
app = Flask(__name__)

# =============================================================================
# 3. Helper — build the prompt
#    The prompt tells Granite exactly what we want and in what format.
#    A structured prompt with clear section headers makes the response
#    easy to split into separate parts later.
# =============================================================================
def build_prompt(content: str, level: str) -> str:
    level_guidance = {
        "Beginner": (
            "Use very simple words and short sentences. "
            "Avoid jargon. Explain every term as if the reader has never seen it before."
        ),
        "Intermediate": (
            "Use clear language suitable for a student who knows the basics. "
            "You may use subject-specific terms but briefly explain any complex ones."
        ),
        "Advanced": (
            "Use precise technical language. Assume the reader has solid subject knowledge. "
            "Focus on depth, nuance, and connections to broader concepts."
        ),
    }
    guidance = level_guidance.get(level, level_guidance["Intermediate"])

    return f"""You are an expert educational assistant helping students understand difficult material.

Simplify the following course content for a {level} learner. {guidance}

Respond using EXACTLY this format with these four section headers (keep the headers in CAPITALS):

SIMPLIFIED EXPLANATION:
<write the simplified explanation here>

KEY CONCEPTS:
- <concept 1>
- <concept 2>

KEY POINTS:
- <key point 1>
- <key point 2>

SUMMARY:
<one or two sentences>

Course content to simplify:
{content}"""


# =============================================================================
# 4. Helper — parse the model's response into its four sections
#    If a section header is missing, we fall back gracefully.
# =============================================================================
def parse_response(text: str) -> dict:
    sections = {
        "result":     "",   # SIMPLIFIED EXPLANATION
        "concepts":   [],   # KEY CONCEPTS  (list)
        "key_points": [],   # KEY POINTS    (list)
        "summary":    "",   # SUMMARY
    }

    # Split on the known headers (case-insensitive, strip extra whitespace)
    import re
    parts = re.split(
        r"(?i)(SIMPLIFIED EXPLANATION:|KEY CONCEPTS:|KEY POINTS:|SUMMARY:)",
        text
    )

    # parts will look like:
    # ['', 'SIMPLIFIED EXPLANATION:', ' ...text... ', 'KEY CONCEPTS:', ' ...', ...]
    current = None
    for chunk in parts:
        header = chunk.strip().upper().rstrip(":")
        if header == "SIMPLIFIED EXPLANATION":
            current = "result"
        elif header == "KEY CONCEPTS":
            current = "concepts"
        elif header == "KEY POINTS":
            current = "key_points"
        elif header == "SUMMARY":
            current = "summary"
        elif current == "result":
            sections["result"] = chunk.strip()
        elif current in ("concepts", "key_points"):
            # Each line that starts with a bullet or dash is one item
            items = [
                line.lstrip("-•* ").strip()
                for line in chunk.splitlines()
                if line.strip().lstrip("-•* ").strip()
            ]
            sections[current] = items
        elif current == "summary":
            sections["summary"] = chunk.strip()

    # If the model returned nothing structured, show the raw text as the result
    if not sections["result"]:
        sections["result"] = text.strip()

    return sections


# =============================================================================
# 5. Routes
# =============================================================================

# ── GET /  →  show the empty form ────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── POST /simplify  →  call Granite, return result ───────────────────────────
@app.route("/simplify", methods=["POST"])
def simplify():
    # Read what the student submitted
    content = request.form.get("content", "").strip()
    level   = request.form.get("level", "Beginner")

    # Guard: if the textarea was empty, return a friendly message
    if not content:
        return render_template(
            "index.html",
            error="Please paste some course content before clicking Simplify.",
            selected_level=level,
        )

    try:
        # -- Set up the IBM watsonx.ai client ---------------------------------
        credentials = Credentials(
            url=WATSONX_URL,
            api_key=WATSONX_API_KEY,
        )

        model = ModelInference(
            model_id=WATSONX_MODEL_ID,
            credentials=credentials,
            project_id=WATSONX_PROJECT_ID,
            params={
                Params.MAX_NEW_TOKENS: 800,   # enough for a full explanation
                Params.TEMPERATURE:    0.3,   # low = factual, consistent output
                Params.DECODING_METHOD: "greedy",
            },
        )

        # -- Build the prompt and call Granite --------------------------------
        prompt   = build_prompt(content, level)
        raw_text = model.generate_text(prompt=prompt)

        # -- Parse the response into sections ---------------------------------
        parsed = parse_response(raw_text)

        return render_template(
            "index.html",
            result=parsed["result"],
            concepts=parsed["concepts"],
            key_points=parsed["key_points"],
            summary=parsed["summary"],
            original_content=content,
            selected_level=level,
        )

    except Exception as exc:
        # Show a readable error on the page instead of crashing
        return render_template(
            "index.html",
            error=str(exc),
            original_content=content,
            selected_level=level,
        )


# =============================================================================
# 6. Entry point
#    Run with:  python app.py
#    Then open: http://127.0.0.1:5000
# =============================================================================
if __name__ == "__main__":
    # debug=True gives helpful error messages during development.
    # Set debug=False before any public deployment.
    app.run(debug=True)
