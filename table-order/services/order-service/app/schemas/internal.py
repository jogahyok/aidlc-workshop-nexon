from pydantic import BaseModel


class ArchiveRequest(BaseModel):
    session_id: int
    store_id: int


class ArchiveResponse(BaseModel):
    archived_count: int
    session_id: int
