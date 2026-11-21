#!/bin/bash
# pixiumos-logo-guard — восстанавливает логотип PixiumOS в GNOME после обновлений пакетов
set -u

LOGO_PNG="/usr/local/share/pixiumos-logo.png"
LOGO_SVG="/usr/local/share/pixiumos-logo.svg"
PIXMAPS="/usr/share/pixmaps"
BACKUP_DIR="$PIXMAPS/ubuntu-logos-original"

[ -f "$LOGO_PNG" ] || exit 0

mkdir -p "$BACKUP_DIR"

PNG_NAMES="ubuntu-logo.png ubuntu-logo-text.png ubuntu-logo-text-dark.png"
SVG_NAMES="ubuntu-logo.svg ubuntu-logo-text.svg ubuntu-logo-text-dark.svg"

changed=0

for name in $PNG_NAMES; do
    target="$PIXMAPS/$name"
    backup="$BACKUP_DIR/$name"

    if [ ! -f "$backup" ] && [ -f "$target" ] && ! cmp -s "$target" "$LOGO_PNG"; then
        cp -f "$target" "$backup" 2>/dev/null || true
    fi

    if [ ! -f "$target" ] || ! cmp -s "$target" "$LOGO_PNG"; then
        cp -f "$LOGO_PNG" "$target"
        changed=1
    fi
done

if [ -f "$LOGO_SVG" ]; then
    for name in $SVG_NAMES; do
        target="$PIXMAPS/$name"
        backup="$BACKUP_DIR/$name"

        if [ ! -f "$backup" ] && [ -f "$target" ] && ! cmp -s "$target" "$LOGO_SVG"; then
            cp -f "$target" "$backup" 2>/dev/null || true
        fi

        if [ ! -f "$target" ] || ! cmp -s "$target" "$LOGO_SVG"; then
            cp -f "$LOGO_SVG" "$target"
            changed=1
        fi
    done
fi

if [ "$changed" = "1" ]; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor >/dev/null 2>&1 || true
    pkill -f gnome-control-center 2>/dev/null || true
fi

exit 0
