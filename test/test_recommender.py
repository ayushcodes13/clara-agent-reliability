from src.retriever import load_products, retrieve_products
from src.recommender import build_recommendation

products = load_products()

query = "I am pregnant and facing hair fall"

results = retrieve_products(query, products)

for product in results:
    rec = build_recommendation(product, query)
    print(rec)
    print("---")