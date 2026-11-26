# Secret Santa Family App 🎅🎁

A serverless web application to organize **Secret Santa** gift exchanges for Christmas. It allows family members to register, specify **family members they have already gifted to in previous years** to avoid repeats, and securely dispatch secret assignments to each person via email using **AWS SES**.

---

## 🏗️ Overall System Architecture

```
                        [ Client / Web Browser ]
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
     [ AWS CloudFront (HTTPS / OAC) ]      [ AWS API Gateway ]
                    │                               │
                    ▼                               ▼
     [ AWS S3 Bucket (Private SPA) ]    [ AWS Lambda (FastAPI) ]
                                                    │
                                    ┌───────────────┴───────────────┐
                                    ▼                               ▼
                          [ AWS DynamoDB Table ]      [ SMTP / AWS SES Email ]
```

### Tech Stack

* **Frontend:** React, Vite, `pnpm`, CSS3 with Glassmorphic aesthetic and responsive layout.
* **Backend:** FastAPI, Mangum (ASGI adapter), Python 3.14, Pydantic, Boto3.
* **Infrastructure as Code (IaC):** Open Serverless (`osls` v4, `serverless.yml`).
* **AWS Services:** AWS Lambda, AWS API Gateway, AWS DynamoDB, AWS S3 (private + OAC), AWS CloudFront, AWS SSM Parameter Store, AWS SES.
* **CDN & Routing:** AWS CloudFront CDN with HTTPS redirect and SPA fallback routing (`403`/`404` -> `/index.html`).

---

## 📁 Repository Structure

```
secret-santa/
├── backend/            # FastAPI, DynamoDB, SES & Open Serverless (osls v4)
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

## 🚀 Quick Start & Deployment

### Prerequisites

* Node.js v20.19+ (or v22.13+ / v24+) and `pnpm` installed (`npm i -g pnpm`).
* Python 3.14+ and `uv` package manager installed.
* AWS CLI configured (`aws configure`).

### Automated Deployment (Recommended)

Run the root deployment script to automatically check prerequisites, build the React frontend, run Python unit tests, and deploy to AWS:

```bash
# Basic deployment (defaults to dev stage, us-east-1)
./deploy.sh

# Deployment with custom stage, region, and verified SES sender email
./deploy.sh --stage prod --region us-east-1 --sender-email "notifications@yourdomain.com"
```

### Manual Step-by-Step Deployment

#### 1. Build Frontend

```bash
cd frontend
pnpm install
pnpm run build
```

#### 2. Test and Deploy Stack

```bash
cd ../backend
uv sync
pnpm install
uv run pytest

# Deploy full stack to AWS
pnpm exec osls deploy --stage dev --param="sender-email=notifications@yourdomain.com"

# Sync built frontend to S3
aws s3 sync ../frontend/dist s3://santa-secreto-frontend-dev --delete --region us-east-1
```
