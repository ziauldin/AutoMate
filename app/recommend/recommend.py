import os
import logging
import traceback
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Configuration & Logging ----------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/recommend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Path to your CSV file (adjust if needed)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "pakwheels_products.csv")

# --- Module Cache ---------------------------------------------------------

_data_cache = {
    "df": None,
    "vectorizer": None,
    "matrix": None
}

# --- Indexing -------------------------------------------------------------

def _load_and_index_from_csv():
    """
    Load the pakwheels_products.csv into a DataFrame, clean & combine the text,
    and build a TF-IDF matrix.
    """
    global _data_cache
    try:
        logger.info("Loading products from CSV: %s", CSV_PATH)
        df = pd.read_csv(CSV_PATH)

        # Expecting columns: id, title, details, manufacturer, price, url
        # Clean text columns
        for col in ("title", "details", "manufacturer"):
            if col in df.columns:
                df[col] = (
                    df[col]
                    .fillna("")
                    .astype(str)
                    .str.replace(r"[^\w\s]", "", regex=True)
                )
            else:
                df[col] = ""

        # Convert price column if present
        if "price" in df.columns:
            df["price"] = (
                df["price"]
                .astype(str)
                .str.replace(r"[^\d\.]", "", regex=True)
                .replace("", "0")
                .astype(float)
            )
        else:
            df["price"] = 0.0

        # Combine all text for TF-IDF
        df["combined_text"] = (
            df["title"] + " " + df["details"] + " " + df["manufacturer"]
        ).str.lower()

        logger.info("Building TF-IDF index")
        vect = TfidfVectorizer(
            min_df=1,
            max_df=0.95,
            stop_words="english",
            ngram_range=(1, 3),
            max_features=10000,
            analyzer="word"
        )
        mat = vect.fit_transform(df["combined_text"])

        _data_cache["df"] = df
        _data_cache["vectorizer"] = vect
        _data_cache["matrix"] = mat

        logger.info("Indexed %d products, %d features.", mat.shape[0], mat.shape[1])

    except Exception:
        logger.error("Error indexing CSV:\n%s", traceback.format_exc())
        _data_cache = {"df": pd.DataFrame(), "vectorizer": None, "matrix": None}

# --- Keyword Extraction ---------------------------------------------------

def _extract_keywords(text: str) -> str:
    """
    Pull out automotive terms and fault codes to boost relevance.
    """
    text_lower = text.lower()

    # common parts & symptoms
    parts = [
        "headlight", "brake pads", "battery", "spark plugs",
        "oil filter", "tire", "coolant", "alternator", "belt",
        "sensor", "pump", "brake rotor", "fuse", "radiator"
    ]
    keywords = [p for p in parts if p in text_lower]

    # OBD codes like P0420
    codes = re.findall(r"\b[pP]\d{4}\b", text)
    keywords.extend(codes)

    return " ".join(keywords)

# --- Public API -----------------------------------------------------------

def recommend_products(query: str, top_k: int = 5) -> list[dict]:
    """
    Return up to `top_k` product dicts most similar to `query`.
    """
    logger.info("Recommending for query: %s", query[:60])
    if _data_cache["df"] is None:
        _load_and_index_from_csv()

    df = _data_cache["df"]
    vect = _data_cache["vectorizer"]
    mat = _data_cache["matrix"]

    if df.empty or vect is None or mat is None:
        logger.warning("No product data available for recommendations.")
        return []

    try:
        # boost with extracted keywords
        processed = (_extract_keywords(query) + " " + query).lower()
        qv = vect.transform([processed])
        sims = cosine_similarity(qv, mat).flatten()

        best_idxs = sims.argsort()[:-top_k - 1:-1]
        results = []
        for idx in best_idxs:
            row = df.iloc[idx]
            results.append({
                "id": int(row.get("id", idx)),
                "title": row.get("title", ""),
                "manufacturer": row.get("manufacturer", ""),
                "price": float(row.get("price", 0)),
                "url": row.get("url", "")
            })

        logger.info("Returning %d recommendations.", len(results))
        return results

    except Exception:
        logger.error("Error during recommendation:\n%s", traceback.format_exc())
        return []
