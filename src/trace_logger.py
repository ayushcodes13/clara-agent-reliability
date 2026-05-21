from datetime import datetime


def create_trace(user_query, retrieved_product_ids, recommendations, extra=None):
    trace = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_query": user_query,
        "retrieved_product_ids": retrieved_product_ids,
        "recommendations": recommendations,
        "pipeline_steps": [
            "user_query_received",
            "products_retrieved",
            "claims_grounded",
            "risks_flagged",
            "doctor_review_decision_created"
        ]
    }
    
    if extra:
        trace.update(extra)
        
    return trace