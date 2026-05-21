def ground_claims(product):
    return {
        "product_id": product.get("id"),
        "product_name": product.get("name"),
        "grounded_claims": product.get("claims", []),
        "source": product.get("source", "unknown"),
        "evidence_level": product.get("evidence_level", "unknown")
    }