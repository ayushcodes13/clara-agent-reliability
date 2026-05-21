from src.risk_rules import flag_risks, doctor_review_decision


def build_recommendation(product, user_query):
    risks = flag_risks(product)
    doctor_review = doctor_review_decision(product, user_query)

    return {
        "product_id": product["id"],
        "product_name": product["name"],
        "recommendation": (
            f"{product['name']} may be relevant because it matches: "
            f"{', '.join(product.get('use_cases', []))}."
        ),
        "grounded_claims": product.get("claims", []),
        "risk_flags": risks,
        "doctor_review": doctor_review,
        "source": product.get("source", "unknown")
    }