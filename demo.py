from src.agent import run_agent
from src.feedback import log_feedback


queries = [
    "I have oily skin and acne marks",
    "I need sunscreen for daily use",
    "I am pregnant and facing hair fall",
]


def print_result(query, result):
    print("\n" + "=" * 72)
    print(f"USER QUERY: {query}")
    print("=" * 72)

    route = result["trace"]["route"]
    print(f"\nROUTE: {route['route']}")
    print(f"Reason: {route['reason']}")

    print("\nUSER RESPONSE:")

    for idx, item in enumerate(result["user_response"], start=1):
        print(f"\n{idx}. {item['product_name']}")
        print(f"   Message: {item['message']}")
        print(f"   Doctor Review Required: {item['doctor_review']['requires_doctor_review']}")

        if item["doctor_review"]["reasons"]:
            print("   Review Reasons:")
            for reason in item["doctor_review"]["reasons"]:
                print(f"   - {reason}")

        print("   Grounded Claims:")
        for claim in item["grounded_claims"]:
            print(f"   - {claim}")

        print("   Risk Flags:")
        for risk in item["risk_flags"]:
            print(f"   - {risk}")

        print(f"   Source: {item['source']}")

    print("\nTRACE STEPS:")
    for step in result["trace"]["pipeline_steps"]:
        print(f"- {step}")


for query in queries:
    result = run_agent(query)
    print_result(query, result)


log_feedback(
    query="I am pregnant and facing hair fall",
    product_id="prod_004",
    feedback="unsafe",
    reason="Pregnancy context should require doctor review",
)

print("\nFeedback logged to data/feedback_log.csv")