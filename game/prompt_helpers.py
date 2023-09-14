from typing import Dict, List, Optional

from schema import Action, ActionCompletion, Conversation, Knowledge, Message, Parameter


def get_knowledge_fragment(
    knowledge: Knowledge, conversation: Conversation, facts: List[str]
) -> str:
    fragment = [
        """You are roleplaying as a character named {knowledge.agent_def.name}.
Description of {knowledge.agent_def.name}: 
{knowledge.agent_def.description} 
\n Description of the world you live in: {knowledge.game_description}.
 """
    ]

    if knowledge.agent_def.core_facts.strip():
        fragment.append(
            """{knowledge.agent_def.name} knows the following: 
{knowledge.agent_def.core_facts}"""
        )

    if knowledge.agent_def.example_speech.strip():
        fragment.append(
            """Example of {knowledge.agent_def.name}'s manner of speech: 
{knowledge.agent_def.example_speech}"""
        )

    if facts:
        fragment.append(
            "{knowledge.agent_def.name} has the following memories: \n{facts}"
        )

    if conversation.correspondent:
        fragment.append(
            """As {knowledge.agent_def.name}, you are currently speaking to \
{conversation.correspondent.name}. 
\nDescription of {conversation.correspondent.name}: 
{conversation.correspondent.description}
"""
        )

    if conversation.scene_description:
        fragment.append(
            """\nThe conversation is occuring in the following scene:
{conversation.scene_description}"""
        )

    return "\n\n".join(
        [
            piece.format(
                knowledge=knowledge, conversation=conversation, facts="\n".join(facts)
            )
            for piece in fragment
        ]
    )


def get_system_prompt(
    knowledge: Knowledge, conversation: Conversation, facts: List[str]
) -> Message:
    system_prompt = get_knowledge_fragment(knowledge, conversation, facts)

    instructions: List[str] = []
    instructions.append(
        """\nYou MUST obey the following instructions:
Keep responses concise.
Do not offer information that is irrelevant to the current conversation.
"""
    )
    instructions.append(knowledge.agent_def.instructions or "")
    instructions.append(conversation.instructions or "")
    instructions.append(
        """NEVER mention you are an AI language model. You MUST stay in character and \
respond ONLY as {knowledge.agent_def.name}."""
    )
    system_prompt += "\n".join(instructions)

    return Message(
        role="system",
        content=system_prompt.format(
            knowledge=knowledge, conversation=conversation, facts=facts
        ),
    )


_CHARACTER_DIALOG_PREPEND = "{character} says: {message}"
_CHARACTER_INTERACT_PREPEND = "{character} says:"


def get_chat_messages(
    knowledge: Knowledge,
    conversation: Conversation,
    facts: List[str],
    history: List[Message],
) -> List[Message]:
    return (
        [get_system_prompt(knowledge, conversation, facts)]
        + _format_history(knowledge, conversation, history)
        + [
            Message(
                role="assistant",
                content=_CHARACTER_DIALOG_PREPEND.format(
                    character=knowledge.agent_def.name, message=""
                ),
            )
        ]
    )


def get_interact_messages(
    knowledge: Knowledge,
    conversation: Conversation,
    facts: List[str],
    history: List[Message],
) -> List[Message]:
    return (
        [get_system_prompt(knowledge, conversation, facts)]
        + _format_history(knowledge, conversation, history)
        + [
            Message(
                role="assistant",
                content=_CHARACTER_INTERACT_PREPEND.format(
                    character=knowledge.agent_def.name
                ),
            )
        ]
    )


def get_action_messages(
    knowledge: Knowledge,
    conversation: Conversation,
    facts: List[str],
    history: List[Message],
) -> List[Message]:
    return (
        [get_system_prompt(knowledge, conversation, facts)]
        + _format_history(knowledge, conversation, history)
        + [Message(role="system", content="You must return a function call.")]
    )


def _format_history(
    knowledge: Knowledge, conversation: Conversation, history: List[Message]
) -> List[Message]:
    def format_message(message: Message) -> Message:
        if message.role == "user":
            character = (
                conversation.correspondent.name
                if conversation.correspondent
                else "Player"
            )
        else:
            character = knowledge.agent_def.name

        new_message = message.copy()
        new_message.content = _CHARACTER_DIALOG_PREPEND.format(
            character=character, message=message.content
        )
        return new_message

    return [format_message(message) for message in history]


def clean_response(agent_name: str, message: Message) -> Message:
    dialog_prepend = _CHARACTER_DIALOG_PREPEND.format(
        character=agent_name, message=""
    ).strip()
    if message.content.startswith(dialog_prepend):
        message.content = message.content[len(dialog_prepend) :]
    interact_prepend = _CHARACTER_INTERACT_PREPEND.format(character=agent_name).strip()
    if message.content.startswith(interact_prepend):
        message.content = message.content[len(interact_prepend) :]
    return message


def get_query_messages(
    knowledge: Knowledge,
    conversation: Conversation,
    facts: List[List[str]],
    history: List[Message],
    queries: List[str],
) -> List[List[Message]]:
    query_base = """Pretend you are {knowledge.agent_def.name}'s inner \
thoughts. Despite what {knowledge.agent_def.name} may be saying, {query}?
{{your answer here}}. Please respond with the provided Rate() function."""

    formatted_queries: List[List[Message]] = []
    for index in range(len(queries)):
        query = queries[index]
        base_message = Message(
            role="system",
            content=get_knowledge_fragment(knowledge, conversation, facts[index]),
        )

        name = (
            conversation.correspondent.name if conversation.correspondent else "player"
        )
        user_formatted_query = query.format(
            agent=knowledge.agent_def.name, player=name, player_character=name
        )
        formatted_query = query_base.format(
            knowledge=knowledge, query=user_formatted_query
        )

        query_as_message = Message(role="system", content=formatted_query)
        formatted_queries.append([base_message] + history + [query_as_message])

    return formatted_queries


def get_guardrail_query(
    knowledge: Knowledge,
    user_message: str,
) -> str:
    query_fragments: List[str] = []

    if knowledge.agent_def.instructions:
        instructions = """With {knowledge.agent_def.name} obeying the following 
        instructions: {knowledge.agent_def.instructions}, """

        query_fragments.append(instructions.format(knowledge=knowledge))

    query = """Based on the instructions, the tone and the time period of the game, 
    and current conversation, how appropriate would it be for you as 
    {knowledge.agent_def.name} to say "{user_message}"?
    """
    query_fragments.append(query.format(knowledge=knowledge, user_message=user_message))

    return "\n".join(query_fragments)


def generate_functions_from_actions(actions: List[Action]) -> List[Dict[str, str]]:
    # Format taken from https://platform.openai.com/docs/guides/gpt/function-calling
    functions = [action.dict() for action in actions]

    for func in functions:
        properties = {}
        for p in func["parameters"]:
            properties[p["name"]] = p
        func["parameters"] = {
            "type": "object",
            "properties": properties,
            "required": [p["name"] for p in func["parameters"]],
        }

    return functions


_RATING_ENUM_MAP: Dict[str, int] = {
    "Not at all.": 1,
    "Not very.": 2,
    "Moderately.": 3,
    "Fairly.": 4,
    "Very.": 5,
}


def get_rate_function() -> Dict[str, str]:
    act = Action(
        name="Rate",
        description="Answers the question with a rating",
        parameters=[
            Parameter(
                name="rating",
                description="The rating you want to give in response to the question.",
                type="string",
                enum=list(_RATING_ENUM_MAP.keys()),
            ),
        ],
    )

    return generate_functions_from_actions([act])[0]


def rating_to_int(completion: Optional[ActionCompletion]) -> int:
    if (
        completion is None
        or "rating" not in completion.args
        or completion.args["rating"] not in _RATING_ENUM_MAP.keys()
    ):
        return -1

    return _RATING_ENUM_MAP[completion.args["rating"]]
