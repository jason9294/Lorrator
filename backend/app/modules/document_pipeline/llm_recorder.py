import asyncio
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable
from uuid import UUID

from app.models import DocumentProcessingLlmCallModel
from app.repositories.document_processing_llm_call_repo import (
    DocumentProcessingLlmCallRepository,
)
from app.shared.utils import uuid7


@runtime_checkable
class LlmCallRecorder(Protocol):
    async def record(
        self,
        *,
        step_id: str,
        call_key: str,
        label: str,
        model: str,
        request: list[dict[str, Any]],
        response: dict[str, Any] | str,
    ) -> UUID: ...

    async def flush(self) -> None: ...


class PipelineLlmCallRecorder:
    def __init__(
        self,
        *,
        repo: DocumentProcessingLlmCallRepository,
        run_id: UUID,
    ) -> None:
        self._repo = repo
        self._run_id = run_id
        self._sequence = 0
        self._lock = asyncio.Lock()
        self._pending: list[DocumentProcessingLlmCallModel] = []

    async def record(
        self,
        *,
        step_id: str,
        call_key: str,
        label: str,
        model: str,
        request: list[dict[str, Any]],
        response: dict[str, Any] | str,
    ) -> UUID:
        async with self._lock:
            self._sequence += 1
            call = DocumentProcessingLlmCallModel(
                run_id=self._run_id,
                step_id=step_id,
                call_key=call_key,
                label=label,
                model=model,
                request=request,
                response=response,
                sequence=self._sequence,
            )
            self._pending.append(call)
            return call.id

    async def flush(self) -> None:
        async with self._lock:
            pending = self._pending
            self._pending = []

        if pending:
            await self._repo.create_many(pending)


@dataclass
class RecordedLlmCall:
    id: UUID
    step_id: str
    call_key: str
    label: str
    model: str
    request: list[dict[str, Any]]
    response: dict[str, Any] | str
    sequence: int


class InMemoryLlmCallRecorder:
    def __init__(self) -> None:
        self.calls: list[RecordedLlmCall] = []
        self._sequence = 0

    async def record(
        self,
        *,
        step_id: str,
        call_key: str,
        label: str,
        model: str,
        request: list[dict[str, Any]],
        response: dict[str, Any] | str,
    ) -> UUID:
        self._sequence += 1
        call_id = uuid7()
        self.calls.append(
            RecordedLlmCall(
                id=call_id,
                step_id=step_id,
                call_key=call_key,
                label=label,
                model=model,
                request=request,
                response=response,
                sequence=self._sequence,
            )
        )
        return call_id

    async def flush(self) -> None:
        return None
