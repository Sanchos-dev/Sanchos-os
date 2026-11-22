
set -u

SAVE_DIR="${SCREENSHOT_DIR:-$HOME/Pictures}"
FORMAT="png"
mkdir -p "$SAVE_DIR"

MODE="${1:-full}"
FILE="$SAVE_DIR/screenshot_$(date +%Y%m%d_%H%M%S).$FORMAT"

notify() {
    notify-send -u low -i camera-photo "Screenshot" "$1" 2>/dev/null || true
}

case "$MODE" in
    full)
        grim -t "$FORMAT" "$FILE" || { notify "Failed to capture screen"; exit 1; }
        wl-copy -t "image/$FORMAT" < "$FILE"
        notify "Saved to $FILE (copied to clipboard)"
        ;;
    area)
        GEO=$(slurp -b "#00000080" -c "#888888ff" -w 1) || exit 0
        [ -z "$GEO" ] && exit 0
        grim -g "$GEO" -t "$FORMAT" "$FILE" || { notify "Failed to capture region"; exit 1; }
        wl-copy -t "image/$FORMAT" < "$FILE"
        notify "Saved to $FILE (copied to clipboard)"
        ;;
    *)
        echo "Usage: $0 [full|area]" >&2
        exit 2
        ;;
esac
