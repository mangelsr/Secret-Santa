# Secret Santa Backend 🐍⚙️

Serverless Backend written in **FastAPI** and packaged for **AWS Lambda** using **Mangum** and **Serverless Framework v3**.

---

## 🛠️ Tech Stack & Libraries

* **FastAPI:** Asynchronous web framework for building the RESTful API.
* **Mangum:** ASGI adapter to run FastAPI inside AWS Lambda.
* **Boto3:** AWS SDK for **DynamoDB** operations and transactional emails via **AWS SES**.
* **Pydantic:** Data validation and settings management using Python type annotations.
* **Serverless Framework v3:** Infrastructure as Code definition (`serverless.yml`).

---

## 🎲 Secret Santa Draw Engine (`app/core/santa_draw.py`)

The draw engine solves historical exclusion constraints using a **Randomized Backtracking Algorithm over a Directed Graph**:
1. For each participant $u$, get their set of exclusions $E(u)$ (family members they gifted to in previous years).
2. Filter invalid targets: $v \neq u$ and $v \notin E(u)$.
3. Recursively explore assignments where every participant gives exactly 1 gift and receives 1 gift.
4. If constraints form an impossible graph, it returns a user-friendly HTTP 400 error suggesting to revise exclusion rules.

---

## 📡 REST API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/groups` | Create a new Christmas group with an admin passcode |
| `GET` | `/api/v1/groups/{group_id}` | Get group details and public list of participants |
| `POST` | `/api/v1/groups/{group_id}/participants` | Register a participant specifying historical exclusions |
| `DELETE` | `/api/v1/groups/{group_id}/participants/{participant_id}` | Remove a participant (Requires `X-Admin-Passcode` header) |
| `POST` | `/api/v1/groups/{group_id}/draw` | Execute secret draw and dispatch emails via AWS SES |
| `GET` | `/api/v1/health` | Lambda service healthcheck |

---

## 💻 Local Development & Testing

```bash
# 1. Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Run local FastAPI dev server
uvicorn app.main:app --reload --port 8000

# 3. Run draw algorithm unit tests
PYTHONPATH=. python3 tests/test_santa_draw.py
```

---

## 🚀 AWS Deployment

```bash
npm install
npx serverless deploy --stage dev
```
