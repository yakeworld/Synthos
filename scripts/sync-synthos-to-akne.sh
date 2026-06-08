#!/usr/bin/env bash
# AKNE-Synthos 同步守护脚本
# 定期将 Synthos 论文和技能的变更同步到 AKNE 知识图谱
#
# 用法:
#   ./scripts/sync-synthos-to-akne.sh    # 一次性同步
#   ./scripts/sync-synthos-to-akne.sh --daemon  # 守护进程模式
#
# 环境变量:
#   SYNTHOS_ROOT  - Synthos 仓库路径（默认: /media/yakeworld/sda2/Synthos）
#   AKNE_ROOT     - AKNE 仓库路径（默认: /media/yakeworld/sda2/academic_writer/yakeworld）
#   SYNC_INTERVAL - 守护进程间隔秒数（默认: 3600）

set -euo pipefail

SYNTHOS_ROOT="${SYNTHOS_ROOT:-/media/yakeworld/sda2/Synthos}"
AKNE_ROOT="${AKNE_ROOT:-/media/yakeworld/sda2/academic_writer/yakeworld}"
SYNC_INTERVAL="${SYNC_INTERVAL:-3600}"
BRIDGE_SCRIPT="${AKNE_ROOT}/scripts/synthos-akne-bridge.py"
SYNC_LOG="${SYNTHOS_ROOT}/outputs/sync.log"

mkdir -p "${SYNTHOS_ROOT}/outputs"

log() {
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $*" >> "$SYNC_LOG"
    echo "$*"
}

sync_once() {
    log "=== Synthos-AKNE Sync Start ==="

    if [ ! -f "$BRIDGE_SCRIPT" ]; then
        log "ERROR: Bridge script not found: $BRIDGE_SCRIPT"
        return 1
    fi

    python3 "$BRIDGE_SCRIPT" sync 2>&1 | tee -a "$SYNC_LOG"
    local exit_code=${PIPESTATUS[0]}

    if [ $exit_code -eq 0 ]; then
        log "Sync completed successfully"
    else
        log "ERROR: Sync failed with exit code $exit_code"
        return $exit_code
    fi

    log "=== Synthos-AKNE Sync End ==="
}

daemon_mode() {
    log "Starting daemon mode (interval: ${SYNC_INTERVAL}s)"

    while true; do
        sync_once
        sleep "$SYNC_INTERVAL"
    done
}

# Main
case "${1:-sync}" in
    sync)
        sync_once
        ;;
    daemon)
        daemon_mode
        ;;
    report)
        python3 "${AKNE_ROOT}/scripts/synthos-akne-bridge.py" report
        ;;
    *)
        echo "Usage: $0 {sync|daemon|report}"
        exit 1
        ;;
esac
