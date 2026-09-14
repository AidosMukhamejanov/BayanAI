from typing import List

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    target_market: str
    product_type: str
    ingredients: str = Field(
        min_length=1,
        max_length=3000
    )


class IngredientIssue(BaseModel):
    name: str
    short_reason: str
    full_reason: str


class Metrics(BaseModel):
    banned: int
    restricted: int
    safe: int
    unknown: int


class AnalyzeResponse(BaseModel):
    overall_status: str
    summary: str

    metrics: Metrics

    banned: List[IngredientIssue]
    restricted: List[IngredientIssue]

    safe: List[str]
    unknown: List[str]