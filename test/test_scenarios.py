from src.agent import run_agent

queries = [
    "I have oily skin and acne marks",
    "I need sunscreen for daily use",
    "My skin is very dry and sensitive",
    "I am pregnant and facing hair fall",
    "I have active acne and clogged pores",
    "I have dark spots and hyperpigmentation",
]

for query in queries:
    result = run_agent(query)

    print("\nQUERY:", query)
    print("PRODUCTS:", result["trace"]["retrieved_product_ids"])

    for response in result["user_response"]:
        print(response["product_name"])
        print(response["message"])
        print("Doctor review:", response["doctor_review"]["requires_doctor_review"])
        print("Reasons:", response["doctor_review"]["reasons"])
        print("---")