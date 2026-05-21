def flag_risks(product):
    risks = []
    risks.extend(product.get("risk_factors", []))
    risks.extend(product.get("contraindications", []))
    return risks


def doctor_review_decision(product, user_query):
    query = user_query.lower()
    reasons = []

    high_risk_terms = [
        "pregnant", "nursing", "breastfeeding",
        "infected", "raw skin", "broken skin",
        "severe acne", "eczema", "burning",
        "swelling", "bleeding"
    ]

    if product.get("requires_doctor_review"):
        reasons.append("Product is marked as requiring doctor review")

    for term in high_risk_terms:
        if term in query:
            reasons.append(f"User query contains high-risk term: {term}")

    for contraindication in product.get("contraindications", []):
        c = contraindication.lower()
        if ("pregnancy" in c or "pregnant" in c or "nursing" in c) and (
            "pregnant" in query or "nursing" in query or "breastfeeding" in query
        ):
            reasons.append("Product contraindication matches user's pregnancy/nursing context")

    return {
        "requires_doctor_review": len(reasons) > 0,
        "reasons": reasons
    }