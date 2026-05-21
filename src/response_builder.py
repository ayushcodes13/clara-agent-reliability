def build_user_response(recommendations):
    responses = []

    for rec in recommendations:
        doctor_review = rec.get("doctor_review", {})
        requires_review = doctor_review.get("requires_doctor_review", False)

        if requires_review:
            message = (
                f"{rec['product_name']} may match your concern, "
                "but doctor review is required before use."
            )
        else:
            message = rec["recommendation"]

        responses.append({
            "product_id": rec["product_id"],
            "product_name": rec["product_name"],
            "message": message,
            "grounded_claims": rec.get("grounded_claims", []),
            "risk_flags": rec.get("risk_flags", []),
            "doctor_review": doctor_review,
            "source": rec.get("source")
        })

    return responses