<div align="center">

# Clara Agent Reliability

**A local CLI demo of safety gates for medical-adjacent product recommendations**

Routes a query, searches a small product catalogue, checks product claims and risks, and holds recommendations for doctor review when the query or product requires it.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github)](https://github.com/ayushcodes13/clara-agent-reliability)
[![Demo video](https://img.shields.io/badge/Watch-Demo%20video-4285F4?style=flat-square&logo=youtube)](https://youtu.be/K3pfU-BcIXI)

![Python 3.9 tested](https://img.shields.io/badge/Python-3.9%20tested-blue)
![Project status](https://img.shields.io/badge/Status-Local%20demo-orange)
![Safety gate](https://img.shields.io/badge/Review-Doctor%20gate-red)

</div>

---

## Why this project exists

A product can match a user's search terms and still be inappropriate for their context. For example, a pregnancy-related hair-loss query should not receive an ordinary product recommendation when the catalogue includes a pregnancy contraindication.

Clara demonstrates a rule-based control layer that routes queries, retrieves catalogue entries, exposes only catalogue claims, checks risk rules, and builds a review-gated response. It is a demonstration of those mechanisms, not a healthcare service.

## Architecture

![Clara pipeline architecture](assets/architecture.png)

The source illustration is also available as [`architecture.html`](architecture.html).

## Run the demo

The project has no browser UI or API. Its end-to-end flow runs locally in the terminal and uses the checked-in JSON catalogue.

```bash
git clone https://github.com/ayushcodes13/clara-agent-reliability.git
cd clara-agent-reliability
python3 demo.py
```

The CLI was run successfully with Python 3.9.6. The demo prints two ordinary skincare queries and a pregnancy-related query that requires doctor review. It also appends a sample feedback row to `data/feedback_log.csv` each time it runs.

Watch the [recorded demo](https://youtu.be/K3pfU-BcIXI). The architecture diagram and recording are the visual project artifacts; there are no screenshots of a live app because this repository does not include one.

## Run the focused regression checks

```bash
python3 -m unittest test.test_safety_gate
```

These checks cover the request-level doctor-review gate for allergy and child queries, and confirm that an ordinary sunscreen query remains ungated. Older files in `test/` are print-based examples, not an asserted full test suite.

## What the demo demonstrates

- **Routing:** flags selected high-risk terms before retrieval.
- **Catalogue retrieval:** ranks products from a small local JSON file using keyword rules.
- **Grounded claims:** returns claims stored with each catalogue product.
- **Risk checks:** surfaces product risk factors and contraindications.
- **Review gate:** holds all returned recommendations when the query routes to doctor review, or when a product-specific rule requires it.
- **Trace:** returns route, retrieved product IDs, decisions, and pipeline steps with each result.
- **Feedback log:** appends a sample review row to a local CSV file.

## Limits and deployment

- This is a deterministic rules demo; it does not call a language model or use semantic retrieval.
- The catalogue is small, local, and manually maintained.
- Routing and risk checks rely on simple keyword rules and are not a substitute for clinical review.
- There is no clinician integration, live product database, browser interface, or API.
- It is **not for real medical use**.
- The core workflow is not deployed on Vercel: the repository provides a local command-line program and file-based data, not a web application or hosted API.

## Possible next steps

- Build an evaluation set for routing and review decisions.
- Expand the catalogue and review product data sources.
- Add a review dashboard or API only with a clearly scoped, tested use case.

<div align="center">
  <sub>A small project for exploring reliability, traceability, and safety gates in recommendation workflows.</sub>
</div>
