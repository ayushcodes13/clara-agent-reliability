def route_query(query):
    q = query.lower()

    high_risk_terms = [
        "pregnant", "pregnancy", "breastfeeding", "nursing",
        "infection", "bleeding", "severe", "pain", "allergy",
        "child", "baby"
    ]

    if any(term in q for term in high_risk_terms):
        return {
            "route": "doctor_review",
            "reason": "Query contains high-risk medical context"
        }

    if any(term in q for term in ["hair", "hair fall", "hairfall", "scalp", "thinning"]):
        return {
            "route": "hair_care",
            "reason": "Query is related to hair care"
        }

    if any(term in q for term in ["skin", "acne", "marks", "pigmentation", "sunscreen", "cleanser", "moisturizer"]):
        return {
            "route": "skin_care",
            "reason": "Query is related to skin care"
        }

    return {
        "route": "general",
        "reason": "No specific route detected"
    }