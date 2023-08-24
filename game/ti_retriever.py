from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from schema import GameStage, Memory, MemoryConfig


# My constraints:
# Memories of importance < 7 are lost when game stages are returned
# Major memories are used to weight importance
# Minor memories are more used to represent the passing of time
def time_weighted_importance(
    current_time: Optional[GameStage], memory: Memory
) -> float:
    if not current_time or not memory.timestamp:
        return 0
    importance = 0.5 ** (current_time.stage - memory.timestamp.stage + 1)
    importance += 0.4 * 0.8 ** (current_time.major - memory.timestamp.major)
    importance += 0.1 * 0.9 ** (current_time.minor - memory.timestamp.minor)
    return importance


# TODO: support non-normalized embeddings
class TIRetriever:
    """A retriever that weights by time and importance"""

    def __init__(self, memory_config: MemoryConfig):
        self._memory_config = memory_config
        self._memories: List[Memory] = []
        self._memory_embeddings: NDArray[np.float64] = np.zeros(
            (10, memory_config.embedding_dims)
        )
        self._memory_importances: NDArray[np.float64] = np.zeros(10)

    def get_relevant_memories(
        self, query: Memory, top_k: int
    ) -> List[Tuple[Memory, float]]:
        top_k = min(len(self._memories), top_k)
        relevance = self._memory_embeddings @ np.array(query.embedding).T
        relevance += self._memory_importances / 10
        for i, memory in enumerate(self._memories):
            relevance[i] += time_weighted_importance(query.timestamp, memory)
        return [
            (self._memories[i], float(relevance[i]))
            for i in np.argpartition(relevance, -top_k)[-top_k:]
            if i < len(self._memories)
        ]

    def add_memory(self, memory: Memory) -> None:
        self._memories.append(memory)

        # TODO: delete memories when it goes over max_memories
        # Doubling size keeps add_memory linear time
        if len(self._memories) > len(self._memory_embeddings):
            self._memory_embeddings = np.concatenate(
                (
                    self._memory_embeddings,
                    np.zeros((len(self._memories), len(self._memory_embeddings[0]))),
                ),
                axis=0,
            )

            self._memory_importances = np.concatenate(
                (self._memory_importances, np.zeros(len(self._memories)))
            )

        self._memory_embeddings[len(self._memories) - 1] = memory.embedding
        self._memory_importances[len(self._memories) - 1] = memory.importance
