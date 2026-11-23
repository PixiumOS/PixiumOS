#!/usr/bin/env bash
set -euo pipefail

sync
echo 3 > /proc/sys/vm/drop_caches

MEM_KB="$(awk '/^MemAvailable:/ {print $2; exit}' /proc/meminfo)"
MEM_GIB="$(awk -v kb="$MEM_KB" 'BEGIN {printf "%.1f", kb / 1048576}')"
MSG="Доступно памяти: ${MEM_GIB} ГиБ"

GRAPHICAL_USER=""
while read -r SID _; do
    [[ -n "$SID" ]] || continue

    SEAT="$(loginctl show-session "$SID" -p Seat --value 2>/dev/null || true)"
    ACTIVE="$(loginctl show-session "$SID" -p Active --value 2>/dev/null || true)"
    REMOTE="$(loginctl show-session "$SID" -p Remote --value 2>/dev/null || true)"
    CLASS="$(loginctl show-session "$SID" -p Class --value 2>/dev/null || true)"
    TYPE="$(loginctl show-session "$SID" -p Type --value 2>/dev/null || true)"

    if [[ "$SEAT" == "seat0" && "$ACTIVE" == "yes" &&
          "$REMOTE" == "no" && "$CLASS" == "user" &&
          ( "$TYPE" == "x11" || "$TYPE" == "wayland" ) ]]; then
        GRAPHICAL_USER="$(loginctl show-session "$SID" -p Name --value 2>/dev/null || true)"
        break
    fi
done < <(loginctl list-sessions --no-legend --no-pager 2>/dev/null || true)

if [[ -z "$GRAPHICAL_USER" ]]; then
    echo "cacheclean: активная графическая сессия не найдена; уведомление пропущено" >&2
    exit 0
fi

UID_NUM="$(id -u "$GRAPHICAL_USER")"
BUS="/run/user/$UID_NUM/bus"

if [[ ! -S "$BUS" ]]; then
    echo "cacheclean: D-Bus-шина не найдена для $GRAPHICAL_USER" >&2
    exit 0
fi

if ! runuser -u "$GRAPHICAL_USER" -- env \
    XDG_RUNTIME_DIR="/run/user/$UID_NUM" \
    DBUS_SESSION_BUS_ADDRESS="unix:path=$BUS" \
    /usr/bin/notify-send \
        --app-name="Cache Cleaner" \
        --icon=/usr/share/icons/cacheclean.png \
        --urgency=normal \
        "cacheclean" "$MSG"; then
    echo "cacheclean: notify-send не смог отправить уведомление" >&2
fi
