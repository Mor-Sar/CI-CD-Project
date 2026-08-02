# app/services/content_generator.py

from ..config import AI_ENABLED, AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL

try:
    import google as genai
except ImportError:
    genai = None

print("AI_ENABLED:", AI_ENABLED)
print("AI_PROVIDER:", AI_PROVIDER)
print("GEMINI_API_KEY loaded:", bool(GEMINI_API_KEY))

# initialize gemini only if allowed and available
gemini_model = None
if AI_ENABLED and AI_PROVIDER == "gemini" and genai is not None and GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def generate_dummy_content(topic: str, card_type: str) -> str:
    if card_type == "flashcard":
        return f"Q: What is {topic}?\nA: This is a simple explanation of {topic}."
    elif card_type == "summary":
        return f"Summary for {topic}: this is a short high-level summary."
    elif card_type == "quiz":
        return f"Quiz question about {topic}: write one key concept related to it."
    elif card_type == "task":
        return f"Task for {topic}: perform a small exercise using this topic."
    elif card_type == "usecase":
        return f"Use case for {topic}: describe when and why you would use it."
    elif card_type == "mindmap":
        return f"Mindmap for {topic}: main -> A -> B -> C."
    else:
        return f"Generic content for {topic}."


def generate_ai_content(topic: str, card_type: str) -> str:
    """
    Generate content using Gemini.
    If unavailable or errors occur, fallback to dummy content.
    """
    if (
        not AI_ENABLED
        or AI_PROVIDER != "gemini"
        or genai is None
        or not GEMINI_API_KEY
        or gemini_client is None
    ):
        return generate_dummy_content(topic, card_type)

    system_prompt = (
        "You generate concise and structured study materials: flashcards, "
        "summaries, quizzes, tasks, usecases and mindmaps. Follow the user's requested output format exactly"
    )
    format_rules = {
        "flashcard": 'Return ONLY exactly two lines:\nQ: ...\nA: ...',
        "summary": "Return ONLY 3–6 bullet points. Each line must start with '- '.",
        "quiz": "Return ONLY:\nQuestion: ...\nA) ...\nB) ...\nC) ...\nD) ...\nCorrect: <A|B|C|D>",
        "task": "Return ONLY a small hands-on exercise as 3–6 numbered steps.",
        "usecase": "Return ONLY 1–2 paragraphs. No lists unless needed.",
        "mindmap": "Return ONLY a text outline:\nTopic\n- Subtopic A\n  - Detail 1\n- Subtopic B",
    }

    user_prompt = f"""
Generate ONLY a {card_type} for the topic: "{topic}".

STRICT RULES:
- Output must contain ONLY the {card_type} content.
- Do NOT include sections for other card types (no Flashcard/Summary/Quiz headers).
- No intro text like "Okay, here's...".
- Follow the format exactly.

FORMAT:
{format_rules.get(card_type, "Return ONLY relevant content.")}
"""


    try:
        response = gemini_client.models.generate_content(
    model=GEMINI_MODEL,
    contents=f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_prompt}",
    )
        content = getattr(response, "text", "") or ""
        return content.strip() or generate_dummy_content(topic, card_type)

    except Exception as e:
        print("GEMINI ERROR:", repr(e), flush=True)
        return generate_dummy_content(topic, card_type)


def generate_content(topic: str, card_type: str, mode="dummy"):
    if mode == "ai":
        return generate_ai_content(topic, card_type)
    return generate_dummy_content(topic, card_type)
