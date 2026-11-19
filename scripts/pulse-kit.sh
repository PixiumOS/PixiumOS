#!/usr/bin/env bash
# PulseOS Kit - simple terminal installer menu

ITEMS=("pulseos-gaming" "pulseos-dev" "pulseos-office" "pulseos-creative" "exit")
DESCS=("(Steam, Lutris, Wine, Winetricks)" "(VS Code, Docker)" "(LibreOffice or OnlyOffice)" "(Blender, OBS)" "")
CHECKED=(0 0 0 0 0)
SELECTED=0

cleanup() {
    tput cnorm 2>/dev/null
    echo
}
trap cleanup EXIT
trap 'exit 130' INT TERM

read_key() {
    local k rest
    IFS= read -rsn1 k
    if [[ $k == $'\x1b' ]]; then
        IFS= read -rsn2 -t 0.1 rest
        k+="$rest"
    fi
    KEY="$k"
}

pause() {
    echo
    read -rp "Press Enter to return to the menu..." _
}

ensure_flatpak() {
    if ! command -v flatpak >/dev/null 2>&1; then
        sudo apt install -y flatpak || return 1
    fi
    sudo flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
}

draw_menu() {
    clear
    echo "PulseOS Kit"
    echo "─────────────"
    local i prefix box
    for i in "${!ITEMS[@]}"; do
        prefix=" "
        [[ $i -eq $SELECTED ]] && prefix=">"
        if [[ ${ITEMS[$i]} == "exit" ]]; then
            echo "$prefix [ ] exit" | sed 's/\[ \] //'
            continue
        fi
        box="[ ]"
        [[ ${CHECKED[$i]} -eq 1 ]] && box="[x]"
        printf "%s %s %-18s %s\n" "$prefix" "$box" "${ITEMS[$i]}" "${DESCS[$i]}"
    done
    echo
    echo "Use Up/Down arrows to move, Enter to select."
}

# ---------- install actions ----------

install_gaming() {
    sudo apt update \
        && ensure_flatpak \
        && flatpak install -y flathub com.valvesoftware.Steam net.lutris.Lutris \
        && sudo apt install -y winetricks wine
}

install_dev() {
    sudo /usr/bin/apt-get update \
        && ensure_flatpak \
        && flatpak install -y flathub com.visualstudio.code \
        && sudo /usr/bin/apt-get install -y docker.io docker-compose-v2
}

install_creative() {
    sudo apt update && sudo apt install -y blender obs-studio
}

install_office() {
    local sel=0
    local opts=("LibreOffice" "OnlyOffice" "Back")
    while true; do
        clear
        echo "Choose your office suite"
        echo "────────────────────────"
        echo
        echo "Quick comparison:"
        echo
        echo "  LibreOffice"
        echo "    - Installed via APT (system package)"
        echo "    - Most complete feature set (Writer, Calc, Impress, Draw, Base)"
        echo "    - Best support for open formats (ODF)"
        echo "    - Classic desktop-style interface"
        echo
        echo "  OnlyOffice"
        echo "    - Installed via Flatpak (sandboxed)"
        echo "    - Modern ribbon interface, similar to Microsoft Office"
        echo "    - Better .docx / .xlsx / .pptx compatibility"
        echo "    - Fewer features than LibreOffice"
        echo
        local i prefix
        for i in "${!opts[@]}"; do
            prefix=" "
            [[ $i -eq $sel ]] && prefix=">"
            echo "$prefix ${opts[$i]}"
        done
        read_key
        case "$KEY" in
            $'\x1b[A'|k) ((sel--)); [[ $sel -lt 0 ]] && sel=$((${#opts[@]} - 1)) ;;
            $'\x1b[B'|j) ((sel++)); [[ $sel -ge ${#opts[@]} ]] && sel=0 ;;
            "")
                case $sel in
                    0) clear; tput cnorm
                       sudo apt update && sudo apt install -y libreoffice
                       return $? ;;
                    1) clear; tput cnorm
                       ensure_flatpak && sudo apt update \
                         && flatpak install -y flathub org.onlyoffice.desktopeditors
                       return $? ;;
                    2) return 2 ;;
                esac
                ;;
        esac
    done
}

run_item() {
    local idx=$1 status=0
    case ${ITEMS[$idx]} in
        pulseos-gaming)   clear; tput cnorm; install_gaming;   status=$? ;;
        pulseos-dev)      clear; tput cnorm; install_dev;      status=$? ;;
        pulseos-office)   install_office;                      status=$? ;;
        pulseos-creative) clear; tput cnorm; install_creative; status=$? ;;
    esac

    if [[ $status -eq 2 ]]; then      # user pressed "Back" in office menu
        return
    fi
    if [[ $status -eq 0 ]]; then
        CHECKED[$idx]=1
        echo; echo "Done: ${ITEMS[$idx]} installed."
    else
        echo; echo "Something went wrong while installing ${ITEMS[$idx]}."
    fi
    pause
}

# ---------- main loop ----------

tput civis
while true; do
    draw_menu
    read_key
    case "$KEY" in
        $'\x1b[A'|k)
            ((SELECTED--))
            [[ $SELECTED -lt 0 ]] && SELECTED=$((${#ITEMS[@]} - 1)) ;;
        $'\x1b[B'|j)
            ((SELECTED++))
            [[ $SELECTED -ge ${#ITEMS[@]} ]] && SELECTED=0 ;;
        "")
            if [[ ${ITEMS[$SELECTED]} == "exit" ]]; then
                clear
                exit 0
            fi
            run_item "$SELECTED"
            tput civis
            ;;
        q) clear; exit 0 ;;
    esac
done
