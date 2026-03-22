from __future__ import annotations

import asyncio
from collections import defaultdict

from .models import ProjectProgressEvent


class ProgressBroker:
    def __init__(self, history_limit: int = 128) -> None:
        self.history_limit = history_limit
        self._history: dict[str, list[ProjectProgressEvent]] = defaultdict(list)
        self._subscribers: dict[str, set[asyncio.Queue[ProjectProgressEvent]]] = defaultdict(set)

    def publish(self, event: ProjectProgressEvent) -> None:
        history = self._history[event.project_id]
        history.append(event)
        if len(history) > self.history_limit:
            del history[:-self.history_limit]

        for queue in list(self._subscribers[event.project_id]):
            queue.put_nowait(event)

    def publish_threadsafe(
        self,
        loop: asyncio.AbstractEventLoop,
        event: ProjectProgressEvent,
    ) -> None:
        loop.call_soon_threadsafe(self.publish, event)

    def register(self, project_id: str) -> asyncio.Queue[ProjectProgressEvent]:
        queue: asyncio.Queue[ProjectProgressEvent] = asyncio.Queue()
        for event in self._history.get(project_id, []):
            queue.put_nowait(event)
        self._subscribers[project_id].add(queue)
        return queue

    def unregister(
        self,
        project_id: str,
        queue: asyncio.Queue[ProjectProgressEvent],
    ) -> None:
        subscribers = self._subscribers.get(project_id)
        if subscribers is None:
            return
        subscribers.discard(queue)
        if not subscribers:
            self._subscribers.pop(project_id, None)
