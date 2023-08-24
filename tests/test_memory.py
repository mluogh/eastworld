import unittest
from typing import Any, List
from unittest.mock import AsyncMock, Mock

from game.memory import GenAgentMemory
from schema import GameStage, Memory


async def test_add_uses_llm():
    retriever: Any = Mock()
    llm: Any = AsyncMock()

    gen_agent_memory = GenAgentMemory(llm, 5, retriever)

    simple_memory = Memory(
        importance=0,
        description="I was coronated as King!",
        timestamp=GameStage(stage=1, major=2, minor=3),
        embedding=[],
    )

    fake_embed = [1.0, 2.0]
    llm.digit_completions.return_value = [8]
    llm.embed.return_value = fake_embed

    await gen_agent_memory.add_memory(simple_memory)

    rated_memory = simple_memory.copy()
    rated_memory.importance = 9
    rated_memory.embedding = fake_embed

    retriever.add_memory.assert_called_once_with(rated_memory)


async def test_add_doesnt_overwrite():
    retriever: Any = Mock()
    llm: Any = AsyncMock()

    gen_agent_memory = GenAgentMemory(llm, 5, retriever)

    simple_memory = Memory(
        importance=5,
        description="I was coronated as King!",
        timestamp=GameStage(stage=1, major=2, minor=3),
        embedding=[1.2, 3.4],
    )

    # Shouldn't be used.
    fake_embed = [1.0, 2.0]
    llm.digit_completions.return_value = [8]
    llm.embed.return_value = fake_embed

    await gen_agent_memory.add_memory(simple_memory)
    retriever.add_memory.assert_called_once_with(simple_memory)


async def test_retrieve():
    retriever: Any = Mock()
    llm: Any = AsyncMock()

    gen_agent_memory = GenAgentMemory(llm, 5, retriever)

    query_memory = Memory(
        importance=0,
        description="I was coronated as King!",
        timestamp=GameStage(stage=1, major=2, minor=3),
        embedding=[],
    )

    fake_embed = [1.0, 2.0]
    llm.embed.return_value = fake_embed

    retriever.get_relevant_memories.return_value = [(query_memory, 0.04)]

    await gen_agent_memory.retrieve_relevant_memories([query_memory.copy()], 5)

    llm.embed.assert_called_once_with(query_memory.description)
    embedded_query_memory = query_memory.copy()
    embedded_query_memory.embedding = fake_embed
    retriever.get_relevant_memories.assert_called_once_with(embedded_query_memory, 5)

    # Should not call LLM when query memory is embedded.
    await gen_agent_memory.retrieve_relevant_memories([embedded_query_memory], 5)
    assert llm.embed.call_count == 1
    assert retriever.get_relevant_memories.call_count == 2


async def test_multi_query_retrieve():
    TOP_K = 3
    # Test that it blends in the queries and gets max of each
    retriever: Any = Mock()
    llm: Any = AsyncMock()

    gen_agent_memory = GenAgentMemory(llm, 5, retriever)

    memories: List[Memory] = []

    query_memory1 = Memory(
        importance=0,
        description="I was coronated as King!",
        timestamp=GameStage(stage=1, major=2, minor=3),
        embedding=[],
    )

    for i in range(5):
        memories.append(query_memory1.copy())
        memories[i].description = str(i)

    query_memory2 = query_memory1.copy()
    query_memory2.description = "blah"

    fake_embed = [1.0, 2.0]
    llm.embed.return_value = fake_embed

    def side_effect(*args):  # type: ignore
        # memories 0, 2, 4 should be returned since they have val 3
        if args == (query_memory1, TOP_K):
            return [(memories[0], 1), (memories[1], 2), (memories[2], 3)]
        return [(memories[0], 3), (memories[3], 2), (memories[4], 3)]

    retriever.get_relevant_memories = side_effect

    relevant_memories = await gen_agent_memory.retrieve_relevant_memories(
        [query_memory1, query_memory2], TOP_K
    )
    unittest.TestCase().assertCountEqual(
        relevant_memories, [memories[0], memories[2], memories[4]]
    )
