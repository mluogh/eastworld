import asyncio
import uuid
from configparser import ConfigParser
from typing import Awaitable, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from game.agent import GenAgent
from game.memory import GenAgentMemory
from game.session import Session
from game.ti_retriever import TIRetriever
from llm.base import LLMBase
from schema import (
    AgentDef,
    Conversation,
    GameDef,
    Knowledge,
    Lore,
    MemoryConfig,
    Message,
)
from server.context import (
    SessionsType,
    get_config_parser,
    get_llm,
    get_redis,
    get_sessions,
)
from server.router.game_def_handlers import get_game_def
from server.schema.debug import (
    ActionCompletionWithDebug,
    InteractWithDebug,
    MessageWithDebug,
)
from server.security.auth import authenticate
from server.typecheck_fighter import RedisType
from server.util.rate_limit import rate_limiter

router = APIRouter(prefix="/session", tags=["Game Sessions"])


def get_gen_agent(agent: str, session: Session):
    gen_agent = next(
        (gen_agent for gen_agent in session.agents if str(gen_agent.uuid) == agent),
        None,
    )
    if not gen_agent:
        gen_agent = next(
            (gen_agent for gen_agent in session.agents if gen_agent.name == agent),
            None,
        )
        if not gen_agent:
            raise HTTPException(status_code=404, detail="Agent not found")

    return gen_agent


def get_agent_def(agent: str, session: Session) -> AgentDef:
    agent_def = next(
        (
            gen_agent
            for gen_agent in session.game_def.agents
            if str(gen_agent.uuid) == agent
        ),
        None,
    )
    if not agent_def:
        agent_def = next(
            (
                gen_agent
                for gen_agent in session.game_def.agents
                if gen_agent.name == agent
            ),
            None,
        )
        if not agent_def:
            raise HTTPException(status_code=404, detail="Agent not found")

    return agent_def


@router.post(
    "/create",
    operation_id="create_session",
    response_model=str,
    dependencies=[Depends(authenticate)],
)
async def create_session(
    game_uuid: str,
    sessions: SessionsType = Depends(get_sessions),
    config_parser: ConfigParser = Depends(get_config_parser),
    redis: RedisType = Depends(get_redis),
    llm: LLMBase = Depends(get_llm),
):
    """Given a Game, creates a game session and populates the Agents
    with their lore and knowledge.

    <h3>Args:</h3>

    - **game_uuid** (uuid4 as str): The uuid of the GameDef that this session will
    populate from.

    <h3>Returns:</h3>
    - **session_uuid** (uuid4 as str): the uuid of the session created
    """
    game_def = await get_game_def(game_uuid, redis)

    memory_config = MemoryConfig(
        max_memories=config_parser.getint(
            "memory_config", "max_memories", fallback=1024
        ),
        memories_returned=config_parser.getint(
            "memory_config", "default_memories_returned", fallback=5
        ),
        embedding_dims=llm.embedding_size,
    )

    # TODO: embed personal lore at the same time as this
    async def lore_task(lore: Lore):
        lore.memory.embedding = await llm.embed(lore.memory.description)

    set_lore_coroutines: List[Awaitable[None]] = []
    for shared_lore in game_def.shared_lore:
        set_lore_coroutines.append(lore_task(shared_lore))

    await asyncio.gather(*set_lore_coroutines)

    awaitable_agents: List[Awaitable[GenAgent]] = []
    for agent_def in game_def.agents:
        knowledge = Knowledge(
            game_description=game_def.description,
            agent_def=agent_def,
            shared_lore=game_def.shared_lore,
        )

        memory = GenAgentMemory(
            llm,
            memory_config.memories_returned,
            TIRetriever(memory_config),
        )

        awaitable_agents.append(GenAgent.create(knowledge, llm, memory))

    agents = await asyncio.gather(*awaitable_agents)
    session = Session(uuid=uuid.uuid4(), game_def=game_def, agents=agents)
    sessions[session.uuid] = session

    return str(session.uuid)


@router.get("/list", operation_id="list_sessions", response_model=List[str])
def get_sessions_list(
    game_uuid: str,
    sessions: SessionsType = Depends(get_sessions),
):
    """Lists all active sessions for a given Game.

    <h3>Args:</h3>

    - **game_uuid** (uuid4 as str): The uuid of the GameDef

    <h3>Returns:</h3>
    - **session_uuids** (List[uuid4] as List[str]): the uuids of the sessions
    """
    return [
        session.uuid
        for session in sessions.values()
        if str(session.game_def.uuid) == game_uuid
    ]


@router.get(
    "/{session_uuid}/active", operation_id="is_session_active", response_model=bool
)
def is_session_active(
    session_uuid: str,
    sessions: SessionsType = Depends(get_sessions),
):
    return uuid.UUID(session_uuid, version=4) in sessions.keys()


@router.post(
    "/{session_uuid}/start_chat",
    operation_id="start_chat",
    dependencies=[Depends(authenticate)],
)
async def start_conversation(
    session_uuid: str,
    agent: str,
    history: Optional[List[Message]] = None,
    correspondent: Optional[str] = None,
    conversation: Optional[Conversation] = None,
    sessions: SessionsType = Depends(get_sessions),
):
    """Starts a chat with the given agent. Clears previous conversation
    history.

    <h3>Args:</h3>

    - **session_uuid** (str): the uuid of the session
    - **agent** (str): either the uuid or the name of the agent.
    - **correspondent** (str): the character with whom the agent is speaking to.
    - **conversation** (Conversation): conversation context. See definition.
    - **history** List[Message]: pre-populate the conversation so you start
    as though you were mid-conversation

    <h3>Returns:</h3>
    - none
    """
    session = sessions[UUID4(session_uuid)]
    gen_agent = get_gen_agent(agent, session)
    if not conversation:
        conversation = Conversation()

    if correspondent:
        conversation = Conversation(correspondent=get_agent_def(correspondent, session))

    return gen_agent.startConversation(conversation, history or [])


@router.post(
    "/{session_uuid}/chat",
    operation_id="chat",
    response_model=MessageWithDebug,
    dependencies=[Depends(authenticate), Depends(rate_limiter)],
)
async def chat(
    session_uuid: str,
    agent: str,
    message: str,
    send_debug: bool = False,
    sessions: SessionsType = Depends(get_sessions),
) -> MessageWithDebug:
    """Sends `message` to the given agent. They will respond with text.

    <h3>Args:</h3>

    - **session_uuid** (str): the uuid of the session
    - **agent** (str): either the uuid or the name of the agent.
    - **message** (str): what you're saying to the agent
    - **send_debug** (bool): sends optional debugging information

    <h3>Returns:</h3>
    - **message_with_debug** (MessageWithDebug): returned completion is in
    message_with_debug.message.content. Optional debug information in
    message_with_debug.debug.
    """
    session = sessions[UUID4(session_uuid)]
    gen_agent = get_gen_agent(agent, session)

    response, debug = await gen_agent.chat(message)

    msg_with_debug = MessageWithDebug(message=response)
    if send_debug:
        msg_with_debug.debug = debug

    return msg_with_debug


@router.post(
    "/{session_uuid}/interact",
    operation_id="interact",
    response_model=InteractWithDebug,
    dependencies=[Depends(authenticate), Depends(rate_limiter)],
)
async def interact(
    session_uuid: str,
    agent: str,
    message: str,
    send_debug: bool = False,
    sessions: SessionsType = Depends(get_sessions),
):
    """Sends message to the given agent. They will respond with
    an Action or text.

    <h3>Args:</h3>

    - **session_uuid** (str): the uuid of the session
    - **agent** (str): either the uuid or the name of the agent.
    - **message** (str): what you're saying to the agent
    - **send_debug** (bool): sends optional debugging information

    <h3>Returns:</h3>
    - **response_with_debug** (ResponseWithDebug): returned completion
    response_with_debug.response can either be a Message or an
    ActionCompletion
    Optional debug information in message_with_debug.debug.
    """
    session = sessions[UUID4(session_uuid)]
    gen_agent = get_gen_agent(agent, session)

    response, debug = await gen_agent.interact(message)

    response_with_debug = InteractWithDebug(response=response)

    if send_debug:
        response_with_debug.debug = debug

    return response_with_debug


@router.post(
    "/{session_uuid}/act",
    operation_id="action",
    response_model=Optional[ActionCompletionWithDebug],
    dependencies=[Depends(authenticate), Depends(rate_limiter)],
)
async def act(
    session_uuid: str,
    agent: str,
    message: Optional[str],
    send_debug: bool = False,
    sessions: SessionsType = Depends(get_sessions),
):
    """Asks the given agent to perform an action. Optionally
    after sending a message.

    <h3>Args:</h3>

    - **session_uuid** (str): the uuid of the session
    - **agent** (str): either the uuid or the name of the agent.
    - **message** (Optional[str]): what you're saying to the agent
    - **send_debug** (bool): sends optional debugging information

    <h3>Returns:</h3>
    - **action_with_debug** (ActionCompletionWithDebug): returned completion
    in response_with_debug.action.
    Optional debug information in message_with_debug.debug.
    """
    session = sessions[UUID4(session_uuid)]
    gen_agent = get_gen_agent(agent, session)

    action, debug = await gen_agent.act(message)
    action_with_debug = ActionCompletionWithDebug(action=action)

    if send_debug:
        action_with_debug.debug = debug

    return action_with_debug


@router.post(
    "/{session_uuid}/guardrail",
    operation_id="guardrail",
    response_model=int,
    dependencies=[Depends(authenticate)],
)
async def guardrail(
    session_uuid: str,
    agent: str,
    message: str,
    sessions: SessionsType = Depends(get_sessions),
):
    """Asks whether or not what the player is saying is appropriate given
    the time period, tone, and intent of the game.

    <h3>Args:</h3>

    - **session_uuid** (str): the uuid of the session
    - **agent** (str): either the uuid or the name of the agent.
    - **message** (Optional[str]): what the player is trying to say to the agent

    <h3>Returns:</h3>
    - **appropriateness** (int): number from 1-5. 1 = very inappropriate,
    5 = very appropriate. Return -1 on LLM error
    """
    session = sessions[UUID4(session_uuid)]
    gen_agent = get_gen_agent(agent, session)

    return await gen_agent.guardrail(message)


@router.post(
    "/{session_uuid}/query",
    operation_id="query",
    response_model=List[int],
    dependencies=[Depends(authenticate)],
)
async def query(
    session_uuid: str,
    agent: str,
    queries: List[str],
    sessions: SessionsType = Depends(get_sessions),
):
    """Responds to queries into how the Agent is feeling during conversation
    with the player. Write in second person. You can use {player} to refer
    to the player character (since there can be several).

    e.g.
    - How suspicious are you that {player} is onto him?
    - How happy are you?
    - How angry are you with {player}?

    Phrase queries in a way such that responses like "not at all" or "extremely"
    make sense.

    <h3>Args:</h3>

    - **session_uuid** (str): the uuid of the session
    - **agent** (str): either the uuid or the name of the agent.
    - **queries** (List[str]): list of queries you want to know about agent

    <h3>Returns:</h3>
    - **appropriateness** (List[int]): number from 1-5. 1 = not at all,
    5 = extremely. Returns -1 on LLM error
    """
    session = sessions[UUID4(session_uuid)]
    gen_agent = get_gen_agent(agent, session)

    return await gen_agent.query(queries)


@router.put(
    "/sync",
    operation_id="sync_sessions_to_game_defs",
    dependencies=[Depends(authenticate)],
)
async def updateSessions(
    game_uuid: str,
    sessions: SessionsType = Depends(get_sessions),
    redis: RedisType = Depends(get_redis),
):
    jsoned = await redis.get(game_uuid)
    if not jsoned:
        raise HTTPException(status_code=404, detail="Game not found")

    updated_game = GameDef.parse_raw(jsoned)

    matching_sessions = [
        session
        for session in sessions.values()
        if str(session.game_def.uuid) == game_uuid
    ]

    for session in matching_sessions:
        session.game_def = updated_game
        for gen_agent in session.agents:
            matching_agent_def = next(
                (
                    agent_def
                    for agent_def in updated_game.agents
                    if agent_def.uuid == gen_agent.uuid
                ),
                None,
            )
            if matching_agent_def:
                knowledge = Knowledge(
                    game_description=updated_game.description,
                    agent_def=matching_agent_def,
                    shared_lore=updated_game.shared_lore,
                )
                gen_agent.updateKnowledge(knowledge)
