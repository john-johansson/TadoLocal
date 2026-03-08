#!/bin/sh
set -e

STATE_DB="/data/tado-local.db"

if [ -z "$TADO_BRIDGE" ] && [ -z "$TADO_BRIDGE_IP" ] && [ ! -f "$STATE_DB" ]; then
    echo "No TADO_BRIDGE (or legacy TADO_BRIDGE_IP) set and no existing pairing DB found at $STATE_DB."
    echo "Set TADO_BRIDGE=ip:pin (e.g. 192.168.1.1:111-11-111) then restart."
    echo "Sleeping to keep container alive for debugging..."
    exec sleep infinity
fi

ARGS="--state $STATE_DB --port ${TADO_PORT:-4407}"

# New combined format: TADO_BRIDGE=ip[:pin],ip[:pin],...
if [ -n "$TADO_BRIDGE" ]; then
    IFS=','
    for entry in $TADO_BRIDGE; do
        ARGS="$ARGS --bridge $entry"
    done
    unset IFS
elif [ -n "$TADO_BRIDGE_IP" ]; then
    # Legacy: TADO_BRIDGE_IP / TADO_BRIDGE_PIN (single bridge)
    ARGS="$ARGS --bridge-ip $TADO_BRIDGE_IP"
    [ -n "$TADO_BRIDGE_PIN" ] && ARGS="$ARGS --pin $TADO_BRIDGE_PIN"
fi

# New combined format: TADO_ACCESSORY=ip[:pin],ip[:pin],...
if [ -n "$TADO_ACCESSORY" ]; then
    IFS=','
    for entry in $TADO_ACCESSORY; do
        ARGS="$ARGS --accessory $entry"
    done
    unset IFS
elif [ -n "$TADO_ACCESSORY_IP" ]; then
    # Legacy: comma-separated TADO_ACCESSORY_IP / TADO_ACCESSORY_PIN (positional)
    IFS=','
    set -- $TADO_ACCESSORY_IP
    idx=0
    for ip in "$@"; do
        pin=$(echo "$TADO_ACCESSORY_PIN" | cut -d',' -f$((idx + 1)))
        ARGS="$ARGS --accessory-ip $ip"
        [ -n "$pin" ] && ARGS="$ARGS --accessory-pin $pin"
        idx=$((idx + 1))
    done
    unset IFS
fi

exec tado-local $ARGS
