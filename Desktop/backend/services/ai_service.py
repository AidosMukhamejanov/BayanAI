import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from services.document_service import load_market_documents


# Загружаем .env
load_dotenv(
    ".env",
    override=True
)


API_KEY = os.getenv(
    "GROQ_API_KEY"
)

BASE_URL = os.getenv(
    "GROQ_BASE_URL",
    "https://api.groq.com/openai/v1"
)

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing"
    )


print(
    "AI MODEL:",
    MODEL
)


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)


def clean_json_response(
    content: str
) -> str:

    content = content.strip()

    if content.startswith(
        "```json"
    ):
        content = content[7:]

    elif content.startswith(
        "```"
    ):
        content = content[3:]

    if content.endswith(
        "```"
    ):
        content = content[:-3]

    return content.strip()


def validate_ai_result(
    result: dict
) -> dict:

    required_fields = [
        "overall_status",
        "summary",
        "metrics",
        "banned",
        "restricted",
        "safe",
        "unknown"
    ]

    for field in required_fields:

        if field not in result:
            raise ValueError(
                f"AI response missing field: {field}"
            )

    if not isinstance(
        result["banned"],
        list
    ):
        raise ValueError(
            "banned must be a list"
        )

    if not isinstance(
        result["restricted"],
        list
    ):
        raise ValueError(
            "restricted must be a list"
        )

    if not isinstance(
        result["safe"],
        list
    ):
        raise ValueError(
            "safe must be a list"
        )

    if not isinstance(
        result["unknown"],
        list
    ):
        raise ValueError(
            "unknown must be a list"
        )

    result["metrics"] = {
        "banned": len(
            result["banned"]
        ),

        "restricted": len(
            result["restricted"]
        ),

        "safe": len(
            result["safe"]
        ),

        "unknown": len(
            result["unknown"]
        )
    }

    if len(
        result["banned"]
    ) > 0:

        result[
            "overall_status"
        ] = "NOT_COMPLIANT"

    elif (
        len(
            result["restricted"]
        ) > 0
        or
        len(
            result["unknown"]
        ) > 0
    ):

        result[
            "overall_status"
        ] = "NEEDS_REVIEW"

    else:

        result[
            "overall_status"
        ] = "COMPLIANT"

    return result


def analyze_with_ai(
    target_market: str,
    product_type: str,
    ingredients: str
) -> dict:

    regulatory_context = (
        load_market_documents(
            target_market
        )
    )

    system_prompt = """
You are BayanAI.

You are a cosmetic regulatory compliance assistant.

You must analyze ingredients using ONLY
the regulatory documents provided in the
user message.

IMPORTANT RULES:

1. Do not use general knowledge as regulatory evidence.

2. Do not invent laws.

3. Do not invent article numbers.

4. Do not invent concentration limits.

5. Classify an ingredient as BANNED only if
the provided regulatory documents clearly
state that it is prohibited.

6. Classify an ingredient as RESTRICTED only
if the provided regulatory documents clearly
state that it has restrictions, concentration
limits, usage limits or conditions.

7. Classify an ingredient as SAFE only if the
provided regulatory documents clearly provide
enough evidence that it is permitted.

8. If there is not enough evidence, classify
the ingredient as UNKNOWN.

9. Every ingredient supplied by the user must
appear exactly once in one category:
banned, restricted, safe or unknown.

10. Do not claim that the product is medically
safe.

11. This is regulatory compliance analysis.

12. Return ONLY valid JSON.
"""

    user_prompt = f"""
TARGET MARKET:

{target_market}


PRODUCT TYPE:

{product_type}


INGREDIENTS:

{ingredients}


REGULATORY DOCUMENTS:

{regulatory_context}


Analyze every ingredient.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "overall_status": "COMPLIANT | NOT_COMPLIANT | NEEDS_REVIEW",

  "summary": "short overall conclusion",

  "metrics": {{
    "banned": 0,
    "restricted": 0,
    "safe": 0,
    "unknown": 0
  }},

  "banned": [
    {{
      "name": "ingredient name",
      "short_reason": "short explanation",
      "full_reason": "detailed explanation based only on provided documents"
    }}
  ],

  "restricted": [
    {{
      "name": "ingredient name",
      "short_reason": "short explanation",
      "full_reason": "detailed explanation based only on provided documents"
    }}
  ],

  "safe": [
    "ingredient name"
  ],

  "unknown": [
    "ingredient name"
  ]
}}

STATUS RULES:

If there is at least one banned ingredient:
overall_status = NOT_COMPLIANT

If there are no banned ingredients but
there are restricted or unknown ingredients:
overall_status = NEEDS_REVIEW

Only if there are no banned, restricted
or unknown ingredients:
overall_status = COMPLIANT
"""

    response = (
        client
        .chat
        .completions
        .create(
            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },

                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=0
        )
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    if not content:
        raise ValueError(
            "AI returned an empty response"
        )

    content = clean_json_response(
        content
    )

    try:

        result = json.loads(
            content
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            f"AI returned invalid JSON: {content}"
        ) from error

    result = validate_ai_result(
        result
    )

    return result