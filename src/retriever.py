import json


def load_products(path="data/products.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


HAIR_TERMS = ["hair", "hairfall", "hair fall", "scalp", "thinning"]

SKIN_TERMS = [
    "skin",
    "acne",
    "pimple",
    "pigmentation",
    "hyperpigmentation",
    "marks",
    "dark spots",
    "redness",
    "sunscreen",
    "cleanser",
    "moisturizer",
    "dry",
    "sensitive",
    "oily",
]


INTENT_PRODUCT_TYPES = {
    "sunscreen": ["sunscreen"],
    "sun protection": ["sunscreen"],
    "spf": ["sunscreen"],

    "cleanser": ["cleanser"],
    "face wash": ["cleanser"],
    "wash": ["cleanser"],
    "cleansing": ["cleanser"],

    "moisturizer": ["moisturizer"],
    "moisturiser": ["moisturizer"],
    "hydration": ["moisturizer", "serum"],
    "dry": ["cleanser", "moisturizer"],
    "sensitive": ["cleanser", "moisturizer"],

    "hair fall": ["hair_serum"],
    "hairfall": ["hair_serum"],
    "hair thinning": ["hair_serum"],
    "scalp": ["hair_serum"],

    "acne": ["serum", "moisturizer"],
    "pimple": ["serum", "moisturizer"],
    "clogged pores": ["serum", "moisturizer"],
    "oil control": ["serum", "moisturizer", "sunscreen"],
    "oily": ["serum", "moisturizer", "sunscreen"],

    "marks": ["serum", "cream"],
    "dark spots": ["serum", "cream"],
    "pigmentation": ["serum", "cream"],
    "hyperpigmentation": ["serum", "cream"],
    "brightening": ["serum", "cream"],
}


def detect_category(query):
    q = query.lower()

    if any(term in q for term in HAIR_TERMS):
        return "hair_care"

    if any(term in q for term in SKIN_TERMS):
        return "skin_care"

    return None


def infer_allowed_product_types(query):
    q = query.lower()
    allowed = set()

    for term, product_types in INTENT_PRODUCT_TYPES.items():
        if term in q:
            allowed.update(product_types)

    return allowed


def score_product(query, product):
    q = query.lower()
    score = 0

    searchable_text = " ".join([
        product.get("name", ""),
        product.get("category", ""),
        product.get("product_type", ""),
        product.get("description", ""),
        " ".join(product.get("use_cases", [])),
        " ".join(product.get("claims", [])),
        " ".join(product.get("ingredients", [])),
    ]).lower()

    for term in q.split():
        if term in searchable_text:
            score += 1

    for use_case in product.get("use_cases", []):
        if use_case.lower() in q:
            score += 5

    if product.get("product_type", "").lower() in q:
        score += 3

    return score


def retrieve_products(query, products, top_k=3, min_score=1):
    detected_category = detect_category(query)
    allowed_product_types = infer_allowed_product_types(query)

    filtered_products = products

    if detected_category:
        filtered_products = [
            p for p in filtered_products
            if p.get("category") == detected_category
        ]

    if allowed_product_types:
        filtered_products = [
            p for p in filtered_products
            if p.get("product_type") in allowed_product_types
        ]

    scored_products = []

    for product in filtered_products:
        score = score_product(query, product)

        if score >= min_score:
            scored_products.append((score, product))

    scored_products.sort(key=lambda x: x[0], reverse=True)

    return [product for score, product in scored_products[:top_k]]