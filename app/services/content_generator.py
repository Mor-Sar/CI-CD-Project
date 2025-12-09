# app/services/content_generator.py

from ..config import OPENAI_API_KEY, OPENAI_MODEL, AI_ENABLED

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# initialize client only if allowed and available
client = None
if AI_ENABLED and OpenAI is not None:
    client = OpenAI(api_key=OPENAI_API_KEY)


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
    Try generating real content using OpenAI API.
    If the API is unavailable or errors occur, fallback to dummy content.
    """
    if client is None:
        return generate_dummy_content(topic, card_type)

    system_prompt = (
        "You generate concise and structured study materials: flashcards, "
        "summaries, quizzes, tasks, usecases and mindmaps."
    )

    user_prompt = f"""
Create a {card_type} for the topic: "{topic}".

Required format:
- flashcard: "Q: ... / A: ..."
- summary: 3–6 bullet points
- quiz: question + 4 options + mark correct answer
- task: small hands-on exercise
- usecase: 1–2 paragraphs
- mindmap: text outline like:
  Topic
  - Subtopic A
    - Detail 1
  - Subtopic B
"""

    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )

        content = completion.choices[0].message.content
        return content.strip()

    except Exception as e:
        # fallback: avoid crashing the app
        return generate_dummy_content(topic, card_type)


def generate_content(topic: str, card_type: str, mode="dummy"):
    if mode == "ai":
        return generate_ai_content(topic, card_type)
    return generate_dummy_content(topic, card_type)
