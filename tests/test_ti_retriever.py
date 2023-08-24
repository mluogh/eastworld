import unittest

from game.ti_retriever import TIRetriever
from schema import GameStage, Memory, MemoryConfig


def test_simple_add():
    ret = TIRetriever(MemoryConfig(embedding_dims=10))

    simple_memory = Memory(
        importance=10,
        description="test",
        embedding=[1.0] * 10,
        timestamp=GameStage(stage=1, major=2, minor=3),
    )

    ret.add_memory(simple_memory)


def test_multiple_add():
    ret = TIRetriever(MemoryConfig(embedding_dims=10))

    for _ in range(1000):
        simple_memory = Memory(
            importance=10,
            description="test",
            embedding=[1.0] * 10,
            timestamp=GameStage(stage=1, major=2, minor=3),
        )

        ret.add_memory(simple_memory)


def test_importance_retrieval():
    ret = TIRetriever(MemoryConfig(embedding_dims=10))

    for _ in range(10):
        simple_memory = Memory(
            importance=1,
            description="test",
            embedding=[0.1] * 10,
            timestamp=GameStage(stage=1, major=2, minor=3),
        )
        ret.add_memory(simple_memory)

    king_memory = Memory(
        importance=10,
        description="king importance",
        embedding=[0.1] * 10,
        timestamp=GameStage(stage=1, major=2, minor=3),
    )
    ret.add_memory(king_memory)

    bigly_memory = Memory(
        importance=1,
        description="bigly embedding",
        embedding=[1.0] * 10,
        timestamp=GameStage(stage=1, major=2, minor=3),
    )
    ret.add_memory(bigly_memory)

    query_memory = Memory(
        importance=1,
        description="gron",
        embedding=[1.0] * 10,
        timestamp=GameStage(stage=1, major=2, minor=3),
    )

    mems_and_scores = ret.get_relevant_memories(query_memory, 2)
    memories = [m for m, _ in mems_and_scores]
    scores = [s for _, s in mems_and_scores]

    unittest.TestCase().assertCountEqual(memories, [king_memory, bigly_memory])

    # First score is bigly_memory: embedding (10) + time weight (1) + importance (1/10)
    # First score is king_memory: embedding (1) + time weight (1) + importance (10/10)
    unittest.TestCase().assertCountEqual(scores, [11.1, 3.0])


def test_many_memory_importance_retrieval():
    ret = TIRetriever(MemoryConfig(embedding_dims=10))

    for _ in range(100):
        simple_memory = Memory(
            importance=1,
            description="test",
            embedding=[0.1] * 10,
            timestamp=GameStage(stage=1, major=2, minor=3),
        )
        ret.add_memory(simple_memory)

    king_memory1 = Memory(
        importance=10,
        description="king importance",
        embedding=[0.1] * 10,
        timestamp=GameStage(stage=1, major=2, minor=3),
    )
    ret.add_memory(king_memory1)

    for _ in range(200):
        simple_memory = Memory(
            importance=1,
            description="test",
            embedding=[0.1] * 10,
            timestamp=GameStage(stage=1, major=2, minor=3),
        )
        ret.add_memory(simple_memory)

    king_memory2 = Memory(
        importance=10,
        description="king shit",
        embedding=[0.1] * 10,
        timestamp=GameStage(stage=1, major=2, minor=3),
    )
    ret.add_memory(king_memory2)

    for _ in range(400):
        simple_memory = Memory(
            importance=1,
            description="test",
            embedding=[0.1] * 10,
            timestamp=GameStage(stage=1, major=2, minor=3),
        )
        ret.add_memory(simple_memory)

    king_memory3 = Memory(
        importance=10,
        description="kinging",
        embedding=[0.1] * 10,
        timestamp=GameStage(stage=1, major=2, minor=3),
    )
    ret.add_memory(king_memory3)

    query_memory = Memory(
        importance=1,
        description="gron",
        embedding=[1.0] * 10,
        timestamp=GameStage(stage=1, major=2, minor=3),
    )

    mems_and_scores = ret.get_relevant_memories(query_memory, 3)
    memories = [m for m, _ in mems_and_scores]
    scores = [s for _, s in mems_and_scores]

    unittest.TestCase().assertCountEqual(
        memories, [king_memory1, king_memory2, king_memory3]
    )
    unittest.TestCase().assertCountEqual(scores, [3.0, 3.0, 3.0])
