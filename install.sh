#!/bin/bash
# ╔══════════════════════════════════════════════════════════╗
# ║            CAMERA HUB - INSTALLER                        ║
# ║     GTK Control Panel for OBSBOT & USB Webcams           ║
# ╚══════════════════════════════════════════════════════════╝
set -e

# ── Colors ─────────────────────────────────────────────────
R='\033[1;31m'
G='\033[1;32m'
Y='\033[1;33m'
B='\033[1;34m'
M='\033[1;35m'
C='\033[1;36m'
W='\033[1;37m'
NC='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'

# ── Progress bar ───────────────────────────────────────────
progressbar() {
    local current=$1 total=$2 width=30
    local pct=$(( current * 100 / total ))
    local filled=$(( current * width / total ))
    local empty=$(( width - filled ))
    printf "\r  ${C}[${G}"
    printf '█%.0s' $(seq 1 $filled 2>/dev/null) || true
    printf "${DIM}"
    printf '░%.0s' $(seq 1 $empty 2>/dev/null) || true
    printf "${NC}${C}] ${W}%3d%%${NC}" "$pct"
}

spin() {
    local chars='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0
    while kill -0 "$1" 2>/dev/null; do
        printf "\r  ${C}${chars:i++%${#chars}:1}${NC} %s" "$2"
        sleep 0.1
    done
    printf "\r  ${G}✔${NC} %s\n" "$2"
}

# ── Banner ─────────────────────────────────────────────────
clear
echo -e "${M}  ╔═══════════════════════════════════════════╗${NC}"
echo -e "${M}  ║        ${W}★ Stephen's Studio${M} ★               ║${NC}"
echo -e "${M}  ╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${B}"
cat << 'EOF'
    ██████╗ ██████╗ ██████╗ ██████╗ ███████╗ ██████╗████████╗
   ██╔════╝██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝╚══██╔══╝
   ██║     ██║   ██║██████╔╝██████╔╝█████╗  ██║        ██║
   ██║     ██║   ██║██╔═══╝ ██╔═══╝ ██╔══╝  ██║        ██║
   ╚██████╗╚██████╔╝██║     ██║     ███████╗╚██████╗   ██║
    ╚═════╝ ╚═════╝ ╚═╝     ╚═╝     ╚══════╝ ╚═════╝   ╚═╝
EOF
echo -e "${NC}"
echo -e "${W}  ── OBSBOT PTZ & USB Webcam Control Panel ──${NC}"
echo ""

# ── Menu ───────────────────────────────────────────────────
echo -e "${B}[MENU]${NC} Choose an option:"
echo -e "  ${G}1)${NC} Full Install (recommended)"
echo -e "  ${Y}2)${NC} Install System Packages Only"
echo -e "  ${Y}3)${NC} Add User to 'video' Group Only"
echo -e "  ${R}4)${NC} Uninstall"
echo ""
read -p "$(echo -e ${B}'Select [1-4]: '${NC})" CHOICE

case $CHOICE in
    4)
        echo -e "\n${R}╔═══════════════════════════════════════╗${NC}"
        echo -e "${R}║       UNINSTALL CAMERA HUB            ║${NC}"
        echo -e "${R}╚═══════════════════════════════════════╝${NC}"
        echo -e "${G}Done. System packages were not removed.${NC}"
        exit 0
        ;;
    2)
        INSTALL_SYSTEM=1; INSTALL_GROUP=0
        ;;
    3)
        INSTALL_SYSTEM=0; INSTALL_GROUP=1
        ;;
    *)
        INSTALL_SYSTEM=1; INSTALL_GROUP=1
        ;;
esac

# ── Helper functions ───────────────────────────────────────
step() { echo -e "\n${G}[$1/$TOTAL]${NC} ${W}$2${NC}"; }
ok()   { echo -e "  ${G}✔${NC} $1"; }
warn() { echo -e "  ${Y}⚠${NC} $1"; }

TOTAL=2
STEP=0

# ── Step 1: System packages ────────────────────────────────
if [[ $INSTALL_SYSTEM -eq 1 ]]; then
    STEP=$((STEP+1))
    step $STEP "Installing system packages..."
    sudo apt-get update -qq 2>/dev/null
    for i in $(seq 1 10); do progressbar $i 10; sleep 0.1; done; echo ""
    sudo apt-get install -y -qq \
        python3 python3-gi python3-cairo python3-numpy \
        gir1.2-gtk-3.0 gir1.2-gdkpixbuf-2.0 gir1.2-pango-1.0 \
        gstreamer1.0-tools gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly \
        v4l-utils 2>/dev/null || true
    for i in $(seq 1 10); do progressbar $((10+i)) 20; sleep 0.05; done; echo ""
    ok "System packages installed"
fi

# ── Step 2: Video group ────────────────────────────────────
if [[ $INSTALL_GROUP -eq 1 ]]; then
    STEP=$((STEP+1))
    step $STEP "Adding user to 'video' group..."
    for i in $(seq 1 3); do progressbar $i 3; sleep 0.15; done; echo ""
    if groups "$USER" | grep -q video; then
        ok "Already in video group"
    else
        sudo usermod -aG video "$USER"
        ok "Added to video group (log out and back in for effect)"
    fi
fi

# ── Done ───────────────────────────────────────────────────
echo ""
echo -e "${G}╔═══════════════════════════════════════╗${NC}"
echo -e "${G}║       INSTALLATION COMPLETE!          ║${NC}"
echo -e "${G}╚═══════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${W}Start Camera Hub:${NC}"
echo -e "    ${C}python3 media_control.py${NC}"
echo ""
echo -e "  ${W}CLI camera control:${NC}"
echo -e "    ${C}python3 obsbot_control.py${NC}"
echo ""
echo -e "  ${Y}⚠ Log out and back in for video group to take effect${NC}"
echo ""
echo -e "  ${M}★ Stephen's Studio ★${NC}"
echo ""
