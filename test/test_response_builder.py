from src.agent import run_agent
from src.response_builder import build_user_response

query = "I am pregnant and facing hair fall"

result = run_agent(query)
safe_response = build_user_response(result["recommendations"])

for item in safe_response:
    print(item)
    print("---")