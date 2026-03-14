import google.generativeai as genai
import json
import re
import os

from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a Smart Reasoning Assistant. When given any problem or question, you MUST always respond in the following strict JSON format and nothing else:

{
  "problem_breakdown": [
    "Sub-problem 1",
    "Sub-problem 2",
    "Sub-problem 3"
  ],
  "reasoning_steps": [
    {
      "step": 1,
      "title": "Short title for this step",
      "thinking": "Detailed explanation of what you are doing in this step and why",
      "result": "What you concluded from this step"
    }
  ],
  "final_answer": "Your clear, complete final answer here",
  "confidence": "high | medium | low",
  "why_it_makes_sense": "A plain-English explanation of why your answer is correct and logical"
}

Rules:
- Always break the problem into 2-5 sub-problems
- Always show at least 3 reasoning steps
- Be thorough in your thinking field — show your actual reasoning process
- The final_answer must directly answer the original question
- Respond ONLY with valid JSON. No text before or after."""


def query_gemini(user_message: str) -> dict:
    """Send a message to Gemini and return structured reasoning response."""

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

    response = model.generate_content(user_message)
    raw_text = response.text.strip()

    # Strip markdown code fences if present
    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {
            "problem_breakdown": ["Could not parse structured response"],
            "reasoning_steps": [
                {
                    "step": 1,
                    "title": "Raw response",
                    "thinking": raw_text,
                    "result": "See thinking above"
                }
            ],
            "final_answer": raw_text,
            "confidence": "low",
            "why_it_makes_sense": "Response could not be parsed into structured format."
        }

    return result


def format_confidence_emoji(confidence: str) -> str:
    mapping = {
        "high":   "🟢 High",
        "medium": "🟡 Medium",
        "low":    "🔴 Low"
    }
    return mapping.get(confidence.lower(), "⚪ Unknown")
