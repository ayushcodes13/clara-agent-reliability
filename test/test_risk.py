from src.retriever import load_products, retrieve_products
from src.risk_rules import flag_risks, doctor_review_decision

products = load_products()

query = "I am pregnant and facing hair fall"

results = retrieve_products(query, products)

for product in results:
    print("Product:", product["name"])
    print("Risks:", flag_risks(product))
    print("Doctor Review:", doctor_review_decision(product, query))
    print("---")