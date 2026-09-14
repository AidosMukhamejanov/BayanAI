from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import AnalyzeRequest, AnalyzeResponse
from services.ai_service import analyze_with_ai


app = FastAPI(
    title="BayanAI API",
    description="AI cosmetic regulatory compliance backend",
    version="0.2.0"
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
        "service": "BayanAI API",
        "status": "running",
        "version": "0.2.0"
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
def analyze_product(
    request: AnalyzeRequest
):
    try:
        result = analyze_with_ai(
            target_market=request.target_market,
            product_type=request.product_type,
            ingredients=request.ingredients
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print(
            "AI ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="AI compliance analysis failed"
        )