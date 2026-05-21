from src.retriever import load_products, retrieve_products
from src.recommender import build_recommendation
from src.trace_logger import create_trace
from src.response_builder import build_user_response
from src.router import route_query
from src.grounding import ground_claims


def run_agent(query, top_k=3):
    products = load_products()

    route = route_query(query)

    retrieved_products = retrieve_products(
        query=query,
        products=products,
        top_k=top_k
    )

    recommendations = [
        build_recommendation(product=p, user_query=query)
        for p in retrieved_products
    ]

    grounded_recommendations = []

    for recommendation in recommendations:
        matching_product = next(
            (
                product for product in retrieved_products
                if product.get("id") == recommendation.get("product_id")
            ),
            None
        )

        grounding = ground_claims(matching_product) if matching_product else {}

        recommendation["grounding"] = grounding
        grounded_recommendations.append(recommendation)

    user_response = build_user_response(grounded_recommendations)

    trace = create_trace(
        user_query=query,
        retrieved_product_ids=[
            product.get("id") for product in retrieved_products
        ],
        recommendations=grounded_recommendations,
        extra={
            "route": route,
            "pipeline_steps": [
                "user_query_received",
                "query_routed",
                "products_retrieved",
                "claims_grounded",
                "risks_flagged",
                "doctor_review_decision_created",
                "response_built",
                "trace_created"
            ]
        }
    )

    return {
        "user_query": query,
        "route": route,
        "user_response": user_response,
        "recommendations": grounded_recommendations,
        "trace": trace
    }