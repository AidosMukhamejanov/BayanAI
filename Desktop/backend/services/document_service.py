from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENTS_FOLDER = BASE_DIR / "documents"


def load_market_documents(
    target_market: str
) -> str:

    market = target_market.lower().strip()

    market_folder = DOCUMENTS_FOLDER / market

    if not market_folder.exists():
        raise ValueError(
            f"No regulatory documents found for market: {target_market}"
        )

    documents = []

    for file_path in market_folder.glob("*.txt"):

        text = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not text:
            continue

        documents.append(
            f"""
SOURCE FILE: {file_path.name}

{text}
"""
        )

    if not documents:
        raise ValueError(
            f"No regulatory text available for market: {target_market}"
        )

    return "\n\n".join(documents)