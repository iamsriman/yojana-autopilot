"""API request and response schemas."""

from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class APIError(BaseModel):
    detail: str


class EligibilityProfile(BaseModel):
    district: str | None = Field(default=None, examples=["Visakhapatnam"])
    income: float | None = Field(default=None, ge=0, description="Monthly income unless explicitly annual_income is supplied.")
    annual_income: float | None = Field(default=None, ge=0)
    location: Literal["rural", "urban"] | None = None
    has_rice_card: bool | None = None
    has_ration_card: bool | None = None
    farmer: bool | None = None
    disabled: bool | None = None
    widow: bool | None = None
    student: bool | None = None
    electricity_units: float | None = Field(default=None, ge=0)
    land: float | None = Field(default=None, ge=0, description="Acres of land, when relevant.")
    four_wheeler: bool | None = None
    answers: dict[str, Any] = Field(default_factory=dict, description="Additional rule flags or facts.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "district": "Visakhapatnam",
                    "income": 9000,
                    "location": "rural",
                    "has_rice_card": True,
                    "farmer": True,
                    "student": True,
                    "electricity_units": 120,
                    "land": 2,
                    "four_wheeler": False,
                    "answers": {
                        "is_ap_resident": True,
                        "has_digitized_land_records": True,
                        "ekyc_done": True,
                    },
                }
            ]
        }
    }


class SchemeDecision(BaseModel):
    scheme_id: str
    scheme_name: str
    category: str | None = None
    status: Literal["eligible", "need_more_information", "not_eligible"]
    eligible: bool
    reasons: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    missing_questions: list[str] = Field(default_factory=list)
    next_questions: list[str] = Field(default_factory=list)
    missing_documents: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    application_links: list[str] = Field(default_factory=list)
    processing_time: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class EligibilityResponse(BaseModel):
    eligible: list[SchemeDecision]
    need_more_information: list[SchemeDecision]
    not_eligible: list[SchemeDecision]


class SearchRequest(BaseModel):
    query: str | None = Field(default=None, min_length=1)
    keywords: list[str] = Field(default_factory=list)
    category: str | None = None
    documents: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    top_k: int = Field(default=10, ge=1, le=50)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"query": "income cert", "keywords": ["aadaya"], "category": "certificates", "top_k": 5}
            ]
        }
    }


class ServiceSearchResult(BaseModel):
    id: str
    name: str
    category: str | None = None
    description: str | None = None
    documents: list[str] = Field(default_factory=list)
    portal: str | None = None
    offices: list[str] = Field(default_factory=list)
    processing_time: str | None = None
    score: float


class SchemeSearchResult(BaseModel):
    id: str
    name: str
    category: str | None = None
    benefit: str | None = None
    documents: list[str] = Field(default_factory=list)
    portal: str | None = None
    processing_time: str | None = None
    score: float


class DocumentChecklistResponse(BaseModel):
    scheme_id: str
    scheme_name: str
    required_documents: list[str]
    optional_documents: list[str] = Field(default_factory=list)
    fees: dict[str, Any] | str | None = None
    timeline: str | None = None
    application_mode: list[str]


class Office(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None
    office_hours: str | None = Field(default=None, alias="hours")
    latitude: float | None = None
    longitude: float | None = None
    office_type: str
    rating: float | None = None
    notes: str | None = None

    model_config = {"populate_by_name": True}


class OfficesResponse(BaseModel):
    district: str
    offices: list[Office]
    available_office_types: list[str]


class PortalResponse(BaseModel):
    portal_id: str
    name: str
    portal_url: HttpUrl | str | None = None
    status_url: HttpUrl | str | None = None
    helpline: str | None = None
    description: str | None = None
    owner: str | None = None
    verify_before_use: bool = False


class RetrievedSource(BaseModel):
    source_type: Literal["JSON", "Web"]
    title: str
    content: str
    score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    url: str | None = None


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3)
    district: str | None = None
    top_k: int | None = Field(default=None, ge=1, le=10)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question cannot be blank")
        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"question": "How do I apply for an income certificate in Guntur?", "district": "Guntur", "top_k": 5}
            ]
        }
    }


class ChatResponse(BaseModel):
    answer: str
    confidence: float
    sources: list[RetrievedSource]
    used_web_search: bool


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app_name: str
    version: str
    data_files_loaded: dict[str, int]
    vector_store_ready: bool
