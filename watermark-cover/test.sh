#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  test.sh  –  render a 20-second cover test
#
#  Usage:
#    chmod +x test.sh
#    ./test.sh 00:12:30        # start at that timecode
#    ./test.sh                 # uses fallback TC below
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SOURCE="/Users/mittelmax/Desktop/andre-capcut.Utopia-CapcutMaster-H264.mov"

# ── Edit these as needed ──────────────────────────────────────────────────────
START="${1:-TIMECODE_PLACEHOLDER}"   # ← replace or pass as arg
DURATION=20
# ─────────────────────────────────────────────────────────────────────────────

OVERLAY="$HERE/overlay_test.mov"
OUT="$HERE/test_output.mp4"

echo "════════════════════════════════════════"
echo " Step 1 – Render overlay (${DURATION}s)"
echo "════════════════════════════════════════"
python3 "$HERE/render.py" "$DURATION" "$OVERLAY"

echo ""
echo "════════════════════════════════════════"
echo " Step 2 – Composite onto source"
echo "════════════════════════════════════════"
ffmpeg -y -hide_banner \
  -ss "$START" -t "$DURATION" \
  -i "$SOURCE" \
  -i "$OVERLAY" \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p" \
  -c:v libx264 -crf 18 -preset fast \
  -c:a copy \
  "$OUT"

echo ""
echo "════════════════════════════════════════"
echo " Done → $OUT"
echo "════════════════════════════════════════"
open "$OUT"
