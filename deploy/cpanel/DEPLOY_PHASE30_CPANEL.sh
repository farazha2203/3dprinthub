#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="${PROJECT_DIR:-/home/sfkilvrs/3dprinthub}"
VENV_DIR="${VENV_DIR:-/home/sfkilvrs/virtualenv/3dprinthub/3.12}"
BRANCH="${BRANCH:-feature/phase30-online-payment-gateway}"
PYTHON_BIN="${PYTHON_BIN:-$VENV_DIR/bin/python}"
PIP_BIN="${PIP_BIN:-$VENV_DIR/bin/pip}"

log() { printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }
fail() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

[[ -d "$PROJECT_DIR/.git" ]] || fail "Git repository not found: $PROJECT_DIR"
[[ -x "$PYTHON_BIN" ]] || fail "Python virtualenv not found: $PYTHON_BIN"
[[ -f "$PROJECT_DIR/.env" ]] || fail ".env not found in $PROJECT_DIR"

cd "$PROJECT_DIR"

log "Preflight: refusing deployment over local tracked changes"
tracked_changes="$(git status --porcelain --untracked-files=no)"
[[ -z "$tracked_changes" ]] || fail "Tracked changes exist on the server. Commit/stash them first:\n$tracked_changes"

log "Recording rollback point"
mkdir -p "$HOME/3dprinthub-deploy-backups"
backup_dir="$HOME/3dprinthub-deploy-backups/$(date '+%Y%m%d-%H%M%S')"
mkdir -p "$backup_dir"
git rev-parse HEAD > "$backup_dir/before_commit.txt"
cp -p .env "$backup_dir/.env"
if [[ -f db.sqlite3 ]]; then
    cp -p db.sqlite3 "$backup_dir/db.sqlite3"
fi

log "Fetching and switching to $BRANCH"
git fetch origin --prune
git show-ref --verify --quiet "refs/remotes/origin/$BRANCH" || fail "Remote branch origin/$BRANCH does not exist"
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    git switch "$BRANCH"
else
    git switch --track -c "$BRANCH" "origin/$BRANCH"
fi
git pull --ff-only origin "$BRANCH"

log "Installing locked Python dependencies"
"$PIP_BIN" install -r requirements.txt

log "Validating source before database changes"
"$PYTHON_BIN" scripts/verify_phase30.py
"$PYTHON_BIN" manage.py makemigrations --check --dry-run
"$PYTHON_BIN" manage.py check

log "Applying database migrations"
"$PYTHON_BIN" manage.py migrate --noinput

log "Collecting static assets"
"$PYTHON_BIN" manage.py collectstatic --noinput

log "Running production-safe audits"
"$PYTHON_BIN" manage.py phase29_pricing_seo_audit
"$PYTHON_BIN" manage.py phase30_payment_audit
"$PYTHON_BIN" manage.py deployment_readiness_check || true

log "Restarting Passenger"
mkdir -p tmp
touch tmp/restart.txt

log "Deployment completed"
printf 'Branch: %s\nCommit: %s\nBackup metadata: %s\n' "$BRANCH" "$(git rev-parse HEAD)" "$backup_dir"
printf 'Keep PAYMENT_GATEWAY_ENABLED=0 until the public callback URL is tested in Sandbox.\n'
