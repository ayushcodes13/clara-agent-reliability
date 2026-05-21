from src.agent import run_agent

query = "I am pregnant and facing hair fall"

result = run_agent(query)

print("QUERY:", result["user_query"])
print()

print("USER RESPONSE:")
for response in result["user_response"]:
    print(response)
    print("---")

print()
print("RECOMMENDATIONS:")
for rec in result["recommendations"]:
    print(rec)
    print("---")

print()
print("TRACE:")
print(result["trace"])