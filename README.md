# Secret Santa Family App 🎅🎁

A serverless web application to organize **Secret Santa** gift exchanges for Christmas. It allows family members to register, specify **family members they have already gifted to in previous years** to avoid repeats, and securely dispatch secret assignments to each person via email using **AWS SES**.

---

## 🏗️ Overall System Architecture

```
                        [ Client / Web Browser ]
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
     [ Cloudflare CDN / SSL ]              [ AWS API Gateway ]
                    │                               │
                    ▼                               ▼
    [ AWS S3 Bucket (React SPA) ]       [ AWS Lambda (FastAPI) ]
                                                    │
                                    ┌───────────────┴───────────────┐
                                    ▼                               ▼
                          [ AWS DynamoDB Table ]         [ AWS SES Email ]
```

### Tech Stack

* **Frontend:** React, Vite, `pnpm`, CSS3 with Glassmorphic aesthetic and responsive layout.
* **Backend:** FastAPI, Mangum (ASGI adapter), Python 3.11, Pydantic, Boto3.
* **Infrastructure as Code (IaC):** Serverless Framework v3 (`serverless.yml`).
* **AWS Services:** AWS Lambda, AWS API Gateway, AWS DynamoDB, AWS S3, AWS SES.
* **CDN & DNS:** Cloudflare CDN with HTTPS proxy and SPA fallback routing.

---

## 📁 Repository Structure

```
secret-santa/
├── backend/            # FastAPI, DynamoDB, SES & Serverless Framework v3
│   ├── app/            # Source code for API and draw engine
│   ├── tests/          # Unit tests for exclusion constraints
│   ├── serverless.yml  # AWS Infrastructure orchestration
│   └── README.md       # Backend documentation
│
├── frontend/           # React + Vite (pnpm) SPA
│   ├── src/            # Components, views, and API client
│   ├── pnpm-lock.yaml
│   └── README.md       # Frontend documentation
│
└── README.md           # Main project documentation
```

---

## 🚀 Quick Start

### Prerequisites

* Node.js v18+ and `pnpm` installed (`npm i -g pnpm`).
* Python 3.11+ and `uv` package manager installed.
* AWS CLI configured (`aws configure`).

### 1. Build Frontend

```bash
cd frontend
pnpm install
pnpm run build
```

### 2. Test and Deploy Backend

```bash
cd ../backend
uv sync
npm install
uv run python tests/test_santa_draw.py

# Deploy full stack to AWS
npx serverless deploy --stage dev --sender-email "notifications@yourdomain.com"
```
