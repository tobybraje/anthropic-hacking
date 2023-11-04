from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from settings import settings


def generate_response(messages):
    anthropic = Anthropic(api_key=settings.CLAUDE_API_KEY)
    prompt = ""
    for message in messages:
        if message["role"] == "assistant":
            prompt += f"{AI_PROMPT}{message['content']}"
        else:
            prompt += f"{HUMAN_PROMPT}{message['content']}"

    prompt += "\n\nAssistant:"
    completion = anthropic.completions.create(
        model="claude-2",
        max_tokens_to_sample=300,
        prompt=prompt,
    )
    return completion.completion
