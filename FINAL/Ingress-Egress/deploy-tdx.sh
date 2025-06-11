#!/usr/bin/env bash
set -euo pipefail

TDX_DEPLOY_YAML="ingress-tfs.yaml"   
CONTROLLER_YAML="controller.yaml"          
LOG_CONTAINER="trustee_as_1"               
LOG_TIMEOUT=30                            

PATTERNS=(
  "Quote DCAP check succeeded"
  "MRCONFIGID check succeeded"
  "CCEL integrity check succeeded"
  "Tdx Verifier/endorsement check passed"
)


GREEN='\033[0;32m'
NC='\033[0m'      # reset colour

echo "------------- DEPLOYING NODES -------------"
echo "kubectl apply -f ${TDX_DEPLOY_YAML}"
kubectl apply -f "${TDX_DEPLOY_YAML}"

echo -n "Waiting for attestation container '${LOG_CONTAINER}' … "
until docker ps --format '{{.Names}}' | grep -q "^${LOG_CONTAINER}$"; do
  sleep 1
done
echo "ready"

start=$(date +%s)
remaining=${#PATTERNS[@]}
declare -A seen                                 

pipe=$(mktemp -u)
mkfifo "$pipe"
docker logs "${LOG_CONTAINER}" --follow --tail 0 >"$pipe" 2>&1 &
log_pid=$!

cleanup() { kill "$log_pid" 2>/dev/null || true; rm -f "$pipe"; }
trap cleanup EXIT

regex=$(IFS='|'; echo "${PATTERNS[*]}")

while IFS= read -r line; do
  # Global timeout
  if (( $(date +%s) - start >= LOG_TIMEOUT )); then
    echo "❌  Attestation did not show all evidences within ${LOG_TIMEOUT}s." >&2
    exit 1
  fi

  [[ $line =~ $regex ]] || continue           

  printf "${GREEN}%s${NC}\n" "$line"
  for p in "${PATTERNS[@]}"; do
    if [[ -z ${seen[$p]+_} && "$line" == *"$p"* ]]; then
      seen[$p]=1
      ((remaining--))
    fi
  done

  # All evidences found?
  if (( remaining == 0 )); then
    echo "------------- ATTESTATION SUCCESSFUL -------------"
    cleanup

    echo "------------- MONITORING PODS -------------"
    timeout 25s kubectl get pods -n scenario -w || true
    echo "------------- DEPLOYMENT COMPLETE -------------"
    exit 0
  fi
done <"$pipe"
