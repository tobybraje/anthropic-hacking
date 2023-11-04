from typing import List

from pydantic import BaseModel, Field


class ChatPrompt(BaseModel):
    messages: List[dict] = Field(title="GPT chat prompt")
