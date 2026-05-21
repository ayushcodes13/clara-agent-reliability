from src.retriever import load_products, retrieve_products

products = load_products()

query = "I have oily skin and acne marks"

results = retrieve_products(query, products)

for p in results:
    print(p["id"], p["name"], p["use_cases"])