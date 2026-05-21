# test/test_feedback.py

from src.feedback import log_feedback


log_feedback(
    query="I am pregnant and facing hair fall",
    product_id="prod_004",
    feedback="unsafe",
    reason="Pregnancy context should require doctor review",
)

print("Feedback logged successfully.")