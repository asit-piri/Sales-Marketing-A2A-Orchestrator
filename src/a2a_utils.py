from __future__ import annotations

from typing import Any
from uuid import uuid4

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    DataPart,
    Message,
    Role,
    TextPart,
    TransportProtocol,
)


def create_agent_card(
    *,
    name: str,
    description: str,
    skill_id: str,
    skill_name: str,
    skill_description: str,
    version: str = "1.0.0",
    url: str | None = None,
) -> AgentCard:
    """Build a minimal A2A agent card for local orchestration."""
    endpoint = url or f"local://{name.lower().replace(' ', '-') }"
    return AgentCard(
        name=name,
        description=description,
        version=version,
        url=endpoint,
        preferred_transport=TransportProtocol.jsonrpc.value,
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain", "application/json"],
        capabilities=AgentCapabilities(streaming=False, push_notifications=False),
        skills=[
            AgentSkill(
                id=skill_id,
                name=skill_name,
                description=skill_description,
                tags=["sales", "marketing", "analytics"],
            )
        ],
        supports_authenticated_extended_card=False,
    )


def create_text_message(content: str, role: Role = Role.user) -> Message:
    """Create an A2A text message."""
    return Message(message_id=str(uuid4()), role=role, parts=[TextPart(text=content)])


def create_agent_message(*, text: str, data: dict[str, Any] | None = None) -> Message:
    """Create a combined agent response with optional structured data."""
    parts: list[TextPart | DataPart] = []
    if text:
        parts.append(TextPart(text=text))
    if data is not None:
        parts.append(DataPart(data=data))
    return Message(message_id=str(uuid4()), role=Role.agent, parts=parts)


def extract_text_from_message(message: Message) -> str:
    """Extract the concatenated text parts from a message."""
    return "\n".join(part.text for part in message.parts if isinstance(part, TextPart))


def get_data_part(message: Message) -> dict[str, Any] | None:
    """Return the first structured data part if present."""
    for part in message.parts:
        if isinstance(part, DataPart):
            return part.data
    return None
