from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas import AnalyzeRequest, AnalyzeResponse


app = FastAPI(
    title="Bayan AI API",
    description="Backend API for Bayan AI",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "Bayan AI API",
        "status": "running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/api/options")
def get_options():
    return {
        "target_markets": [
            {
                "id": "uae",
                "name": "United Arab Emirates"
            },
            {
                "id": "eu",
                "name": "European Union"
            },
            {
                "id": "us",
                "name": "United States of America"
            }
        ],
        "product_types": [
            {
                "id": "skin",
                "name": "Skin Care"
            },
            {
                "id": "hair",
                "name": "Hair Care"
            },
            {
                "id": "color",
                "name": "Color cosmetics"
            }
        ]
    }


@app.post(
    "/api/analyze",
    response_model=AnalyzeResponse
)
def analyze_product(request: AnalyzeRequest):

    # TEMPORARY MOCK RESPONSE
    # Потом добавлю раг и квен

    return {
        "overall_status": "NEEDS_REVIEW",
        "summary": "AI analysis will be connected in the next backend version.",
        "metrics": {
            "banned": 0,
            "restricted": 0,
            "safe": 0,
            "unknown": 0
        },
        "banned": [],
        "restricted": [],
        "safe": [],
        "unknown": []
    }