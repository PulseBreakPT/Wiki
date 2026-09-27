from typing import Literal
from pydantic import BaseModel, Field, HttpUrl, EmailStr, ConfigDict


class PublicModel(BaseModel):
    model_config = ConfigDict(extra='ignore')


class Source(PublicModel):
    id: str
    title: str
    url: str
    publisher: str
    accessed_at: str
    published_at: str | None = None
    rights: str


class ClaimInput(BaseModel):
    property: str = Field(min_length=2, max_length=100)
    value: str = Field(min_length=1, max_length=1200)
    source_id: str
    excerpt: str = Field(min_length=3, max_length=1500)
    locator: str = Field(min_length=2, max_length=200)
    origin: Literal['oficial', 'observacao_no_jogo', 'datamining', 'imprensa', 'comunidade'] = 'oficial'
    nature: Literal['observacao', 'declaracao', 'interpretacao', 'rumor'] = 'declaracao'
    verification: Literal['pendente', 'reproduzida', 'contestada', 'refutada'] = 'pendente'
    applicability: str = Field(default='Material promocional; versão jogável não indicada.', max_length=300)
    method: str = Field(default='Consulta da fonte primária e transcrição do excerto.', min_length=3, max_length=500)
    related_entity_id: str | None = None
    spoiler: bool = False


class Assertion(ClaimInput, PublicModel):
    id: str
    entity_id: str
    reviewed_by: str
    recorded_at: str
    source: Source | None = None


class Entity(PublicModel):
    id: str
    slug: str
    name: str
    type: str
    summary: str
    aliases: list[str]
    image: str
    image_position: str = 'center'
    version: int
    updated_at: str
    assertion_count: int
    label: str = 'Official'


class EntityDetail(Entity):
    assertions: list[Assertion]
    related: list[Entity]


class SearchResult(PublicModel):
    items: list[Entity]
    total: int
    next_cursor: str | None
    suggestion: str | None = None


class Snapshot(BaseModel):
    slug: str = Field(pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$', max_length=100)
    name: str = Field(min_length=2, max_length=100)
    type: Literal['personagem', 'local', 'organizacao', 'veiculo', 'arma', 'sistema']
    summary: str = Field(min_length=15, max_length=1000)
    aliases: list[str] = Field(default_factory=list, max_length=15)
    image: str = Field(default='', max_length=2000)
    image_position: str = 'center'
    label: str = 'Official'


class DraftInput(BaseModel):
    entity_id: str | None = None
    base_version: int = 0
    snapshot: Snapshot
    assertions: list[ClaimInput] = Field(min_length=1, max_length=40)
    reason: str = Field(min_length=5, max_length=500)


class Draft(PublicModel):
    id: str
    entity_id: str
    base_version: int
    snapshot: Snapshot
    assertions: list[ClaimInput]
    reason: str
    status: str
    author_id: str
    author_name: str
    created_at: str
    updated_at: str
    revision: int
    reviewer_id: str | None = None
    reviewer_name: str | None = None


class User(PublicModel):
    id: str
    name: str
    email: str
    role: str


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class SourceInput(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    url: HttpUrl
    publisher: str = Field(min_length=2, max_length=100)
    rights: str = Field(min_length=5, max_length=500)


class PublicationHistory(PublicModel):
    id: str
    entity_id: str
    version: int
    created_at: str
    reason: str
    author_name: str
    reviewer_name: str
    snapshot: Snapshot
    assertion_ids: list[str]


class TimelineEntry(PublicModel):
    id: str
    date: str
    title: str
    summary: str
    source_url: str
    type: str


class Change(PublicModel):
    field: str
    before: str | None
    after: str | None


class PublicationDiff(PublicModel):
    entity_id: str
    from_version: int
    to_version: int
    changes: list[Change]