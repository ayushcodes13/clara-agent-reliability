from src.retriever import load_products, retrieve_products
from src.recommender import build_recommendation
from src.trace_logger import create_trace

products = load_products()

query = "I am pregnant and facing hair fall"

retrieved = retrieve_products(query, products)
recommendations = [build_recommendation(p, query) for p in retrieved]

trace = create_trace(query, retrieved, recommendations)

print(trace)