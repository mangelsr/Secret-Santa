#!/usr/bin/env bash
# ==============================================================================
# Secret Santa Application Deployment Script 🎅🎁
# ==============================================================================
# Executes all required steps to build the React frontend SPA, test the Python
# FastAPI backend, and deploy the entire serverless stack to AWS using the
# Serverless Framework.
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status

# Increase Node heap memory to prevent OOM during packaging
export NODE_OPTIONS="--max-old-space-size=4096"
# Ensure Docker build produces AWS Lambda compatible image manifests (Docker V2 Schema 2 without OCI attestations)
export BUILDX_NO_DEFAULT_ATTESTATIONS=1
export DOCKER_DEFAULT_PLATFORM="linux/amd64"

# Color codes for formatted terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Helper logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${BOLD}${CYAN}========== $1 ==========${NC}\n"
}

# Resolve root directory of the repository
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$SCRIPT_DIR"

# Default configuration values
STAGE="dev"
REGION="us-east-1"
SKIP_TESTS=false
SENDER_EMAIL=""

# Attempt to load default SENDER_EMAIL from backend/.env if present
if [ -f "$ROOT_DIR/backend/.env" ]; then
    ENV_EMAIL=$(grep -E '^SES_SENDER_EMAIL=' "$ROOT_DIR/backend/.env" | cut -d '=' -f2 | tr -d '"' | tr -d "'")
    if [ -n "$ENV_EMAIL" ]; then
        SENDER_EMAIL="$ENV_EMAIL"
    fi
fi

# Fallback default if not specified in .env
if [ -z "$SENDER_EMAIL" ]; then
    SENDER_EMAIL="notificaciones@tudominio.com"
fi

# Display Help / Usage
show_help() {
    cat << EOF
Secret Santa App Deployment Script 🎅🎁

Usage: ./deploy.sh [OPTIONS]

Options:
  -s, --stage STAGE          Deployment stage (default: "dev")
  -r, --region REGION        AWS region (default: "us-east-1")
  -e, --sender-email EMAIL   AWS SES verified sender email (default: "$SENDER_EMAIL")
  --skip-tests               Skip backend unit tests execution before deployment
  -h, --help                 Display this help message and exit

Examples:
  ./deploy.sh
  ./deploy.sh --stage prod --region us-west-2
  ./deploy.sh --sender-email admin@mydomain.com --skip-tests
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--stage)
            STAGE="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -e|--sender-email)
            SENDER_EMAIL="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

log_step "1. Checking Deployment Prerequisites"

# Check Node.js
if command -v node >/dev/null 2>&1; then
    log_info "Node.js detected: $(node --version)"
else
    log_error "Node.js is not installed. Please install Node.js (v18+) to continue."
    exit 1
fi

# Determine package manager for frontend (pnpm preferred, npm fallback)
PKG_MANAGER=""
if command -v pnpm >/dev/null 2>&1; then
    PKG_MANAGER="pnpm"
    log_info "Package Manager detected: pnpm ($(pnpm --version))"
elif command -v npm >/dev/null 2>&1; then
    PKG_MANAGER="npm"
    log_info "Package Manager detected: npm ($(npm --version))"
else
    log_error "Neither pnpm nor npm found. Please install a package manager."
    exit 1
fi

# Check AWS CLI
if command -v aws >/dev/null 2>&1; then
    log_info "AWS CLI detected: $(aws --version | head -n1)"
    if aws sts get-caller-identity >/dev/null 2>&1; then
        AWS_ACCOUNT=$(aws sts get-caller-identity --query "Account" --output text 2>/dev/null || echo "Unknown")
        log_info "AWS Credentials verified (Account: ${AWS_ACCOUNT})"
    else
        log_warning "AWS CLI is installed, but valid credentials were not found. Ensure 'aws configure' or AWS env variables are set."
    fi
else
    log_warning "AWS CLI is not installed. Ensure credentials are available to Serverless Framework via environment variables."
fi

# Check Docker
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    log_info "Docker Engine detected: $(docker --version)"
else
    log_error "Docker daemon is not running or accessible. Please ensure Docker is running."
    exit 1
fi

log_info "Deployment Stage: ${BOLD}${STAGE}${NC}"
log_info "AWS Region: ${BOLD}${REGION}${NC}"
log_info "SES Sender Email: ${BOLD}${SENDER_EMAIL}${NC}"

log_step "2. Building Frontend Application"
cd "$ROOT_DIR/frontend"

log_info "Installing frontend dependencies..."
$PKG_MANAGER install

log_info "Building production SPA bundle with Vite..."
if [ "$PKG_MANAGER" = "pnpm" ]; then
    pnpm run build
else
    npm run build
fi

if [ -d "$ROOT_DIR/frontend/dist" ]; then
    log_success "Frontend static bundle built successfully at frontend/dist"
else
    log_error "Frontend build failed: frontend/dist directory missing!"
    exit 1
fi

log_step "3. Preparing & Testing Backend"
cd "$ROOT_DIR/backend"

log_info "Checking Python environment..."
if command -v uv >/dev/null 2>&1; then
    log_info "Using uv package manager..."
    uv sync
    uv export --no-dev --no-hashes -o requirements.txt
    PYTHON_CMD="uv run"
else
    log_info "Using standard python3..."
    PYTHON_CMD="python3"
fi

if [ "$SKIP_TESTS" = false ]; then
    log_info "Running backend unit tests..."
    if command -v uv >/dev/null 2>&1; then
        uv run pytest
    else
        PYTHONPATH=. python3 -m pytest
    fi
    log_success "All backend unit tests passed!"
else
    log_warning "Skipping backend unit tests (--skip-tests specified)."
fi

log_info "Installing Serverless Framework plugins in backend..."
pnpm install

log_step "4. Deploying Infrastructure to AWS via Serverless Framework"
cd "$ROOT_DIR/backend"

log_info "Cleaning up stale build artifacts (.serverless & python-requirements cache)..."
rm -rf "$ROOT_DIR/backend/.serverless"
rm -rf ~/.cache/serverless-python-requirements

log_info "Executing 'npx serverless deploy --stage $STAGE --region $REGION --param=\"sender-email=$SENDER_EMAIL\"'..."
npx serverless deploy \
    --stage "$STAGE" \
    --region "$REGION" \
    --param="sender-email=$SENDER_EMAIL"

log_step "5. Deployment Complete! 🎄✨"
log_success "Successfully deployed Secret Santa application!"
log_info "Stage: $STAGE"
log_info "Region: $REGION"
log_info "SES Sender Email: $SENDER_EMAIL"
echo -e "${CYAN}Note:${NC} The frontend static files (dist/) were automatically synchronized to the S3 web bucket via serverless-s3-sync."
