#!/usr/bin/env bash
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Запусти: sudo $0"; exit 1; }
REAL_USER="${SUDO_USER:-$USER}"
UH="$(getent passwd "$REAL_USER" | cut -d: -f6)"
sedif(){ [ -f "$1" ] || return 0; sed -i "$2" "$1"; }

# 1) GDM: профиль dconf + логотип гретера
install -d /etc/dconf/db/gdm.d
cat > /etc/dconf/profile/gdm <<'EOF'
user-db:user
system-db:gdm
file-db:/usr/share/gdm/greeter-dconf-defaults
EOF
cat > /etc/dconf/db/gdm.d/01-pixium-logo <<'EOF'
[org/gnome/login-screen]
logo='/usr/local/share/pixiumos-logo.png'
EOF
dconf update

# 2) логотип в gnome-control-center
sedif /var/lib/gnome-control-center/vendor.conf 's|pulseos-logo\.png|pixiumos-logo.png|g'

# 3) os-release / lsb-release / dpkg origins
sedif /usr/lib/os-release 's|LOGO=pulseos-logo|LOGO=pixiumos-logo|; s|PulseOS|PixiumOS|g; s|ID=pulseos|ID=pixiumos|'
sedif /etc/lsb-release 's|PulseOS|PixiumOS|g'
sedif /etc/dpkg/origins/ubuntu 's|PulseOS|PixiumOS|g'

# 4) fastfetch юзера
sedif "$UH/.config/fastfetch/config.jsonc" 's|pulseos-logo|pixiumos-logo|g; s|PulseOS|PixiumOS|g'
sedif "$UH/.config/fastfetch/config.json"  's|pulseos-logo|pixiumos-logo|g; s|PulseOS|PixiumOS|g'

# 5) кэши
gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database /usr/share/applications 2>/dev/null || true
echo "OK: PixiumOS branding applied"
