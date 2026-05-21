import csv
from pathlib import Path
from datetime import datetime


FEEDBACK_LOG_PATH = Path("data/feedback_log.csv")


def log_feedback(query, product_id, feedback, reason=None):
    FEEDBACK_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    file_exists = FEEDBACK_LOG_PATH.exists()

    with open(FEEDBACK_LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "query",
                "product_id",
                "feedback",
                "reason",
            ],
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "product_id": product_id,
            "feedback": feedback,
            "reason": reason or "",
        })