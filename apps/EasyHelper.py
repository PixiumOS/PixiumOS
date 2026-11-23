#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EasyHelper — помощник новичка в PixiumOS."""
import ast
import gettext
import glob
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path
 
import gi
 
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Adw, Gdk, GdkPixbuf, GLib, Gtk, Pango, Vte  # noqa: E402
 
APP_ID = "org.easyhelper.App"
APP_DIR = Path(GLib.get_user_data_dir()) / "easyhelper"
CONTAINER = "easyhelper-sandbox"
LOGO_PATH = "/usr/share/ksnip_20261111-174102-removebg-preview.png"
SETTINGS_FILE = APP_DIR / "settings.json"
 
 
def register_local_fonts():
    """Подключает .ttf/.otf из папок fonts/ (рядом с программой и в ~/.local/share/easyhelper/fonts)."""
    try:
        import ctypes
        import ctypes.util
        lib = ctypes.util.find_library("fontconfig")
        if not lib:
            return
        fc = ctypes.CDLL(lib)
        fc.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        fc.FcConfigAppFontAddFile.restype = ctypes.c_int
        for d in (APP_DIR / "fonts", Path(__file__).resolve().parent / "fonts"):
            if d.is_dir():
                for p in sorted(list(d.glob("*.ttf")) + list(d.glob("*.otf"))):
                    fc.FcConfigAppFontAddFile(None, str(p).encode())
    except Exception as e:  # noqa
        print("font register error:", e)
 
 
register_local_fonts()
 
# ════════════════════════════════════════════════════════════════════
#  ЯЗЫКИ  (все переводы встроены в программу — интернет НЕ нужен)
#  (код, название на своём языке, название по-английски, служебное поле)
#  ru / en / zh_CN — ручные переводы прямо в коде (функция L и словари TR/DESC_TR).
#  uk, fr, es, pt, de, fi, id, hi, ko, tr, ja — офлайн-таблицы в конце файла.
# ════════════════════════════════════════════════════════════════════
LANGUAGES = [
    ("ru", "Русский", "Russian", "ru"),
    ("uk", "Українська", "Ukrainian", "uk"),
    ("en", "English", "English", "en"),
    ("fr", "Français", "French", "fr"),
    ("es", "Español", "Spanish", "es"),
    ("pt", "Português", "Portuguese", "pt"),
    ("de", "Deutsch", "German", "de"),
    ("fi", "Suomi", "Finnish", "fi"),
    ("id", "Bahasa Indonesia", "Indonesian", "id"),
    ("zh_CN", "简体中文", "Chinese (Mandarin)", "zh-CN"),
    ("hi", "हिन्दी", "Hindi", "hi"),
    ("ko", "한국어", "Korean", "ko"),
    ("tr", "Türkçe", "Turkish", "tr"),
    ("ja", "日本語", "Japanese", "ja"),
]
LANG_INDEX = {l[0]: l for l in LANGUAGES}
BUILTIN = {"ru": "ru", "en": "en", "zh_CN": "zh"}
RTL_LANGS = set()
DEFAULT_LANG = "ru"
 
CUR = DEFAULT_LANG      # выбранный язык (код из LANGUAGES)
UI_LANG = "ru"          # ru / en / zh — переводы в коде; auto — офлайн-таблицы
 
_TRANS = {}             # кэш системных gettext-переводов
HAS_LETTER = re.compile(r"[^\W\d_]")
 
# Порядок языков в офлайн-таблицах (после английского оригинала)
LANG_ORDER = ("uk", "fr", "es", "pt", "de", "fi", "id", "hi", "ko", "tr", "ja")
OFFLINE = {c: {} for c in LANG_ORDER}     # язык -> {английский текст: перевод}
DESC_OFF = {}                             # команда -> {язык: описание}
 
 
def reg_rows(rows):
    """Строка: (english, uk, fr, es, pt, de, fi, id, hi, ko, tr, ja)."""
    for r in rows:
        if len(r) != 1 + len(LANG_ORDER):
            print("offline row skipped:", r[0])
            continue
        for code, tr in zip(LANG_ORDER, r[1:]):
            OFFLINE[code][r[0]] = tr
 
 
def reg_desc(rows):
    """Строка: (команда, uk, fr, es, pt, de, fi, id, hi, ko, tr, ja)."""
    for r in rows:
        if len(r) != 1 + len(LANG_ORDER):
            print("offline desc skipped:", r[0])
            continue
        DESC_OFF[r[0]] = dict(zip(LANG_ORDER, r[1:]))
 
 
def load_lang():
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            code = json.load(f).get("lang")
        if code in LANG_INDEX:
            return code
    except Exception:
        pass
    return DEFAULT_LANG
 
 
def save_lang(code):
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({"lang": code}, f)
    except Exception as e:  # noqa
        print("settings error:", e)
 
 
def set_lang(code):
    global CUR, UI_LANG
    if code not in LANG_INDEX:
        code = DEFAULT_LANG
    CUR = code
    UI_LANG = BUILTIN.get(code, "auto")
    _TRANS.clear()
 
 
def apply_direction():
    rtl = CUR.split("_")[0] in RTL_LANGS
    Gtk.Widget.set_default_direction(Gtk.TextDirection.RTL if rtl else Gtk.TextDirection.LTR)
 
 
def mt(text):
    """Офлайн-перевод английского текста на выбранный язык (из встроенных таблиц)."""
    if not text or not HAS_LETTER.search(text):
        return text
    core = text.strip()
    tr = OFFLINE.get(CUR, {}).get(core)
    if tr is None:
        return text
    lead = text[:len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()):]
    return lead + tr + trail
 
 
def L(ru, en, zh):
    """Выбрать строку под выбранный язык."""
    if UI_LANG == "ru":
        return ru
    if UI_LANG == "zh":
        return zh
    if UI_LANG == "en":
        return en
    return mt(en)
 
 
set_lang(load_lang())
 
 
TR = {
    # категории команд
    "Обновление системы (APT)": ("System updates (APT)", "系统更新 (APT)"),
    "Snap / Flatpak / dpkg": ("Snap / Flatpak / dpkg", "Snap / Flatpak / dpkg"),
    "Файлы и папки": ("Files and folders", "文件和文件夹"),
    "Информация о системе": ("System information", "系统信息"),
    "Процессы и службы": ("Processes and services", "进程和服务"),
    "CacheClean (вкл/выкл)": ("CacheClean (on/off)", "CacheClean（开/关）"),
    "Полезное": ("Useful tips", "实用技巧"),
    # названия разделов горячих клавиш
    "🪟 Окна и рабочие столы": ("🪟 Windows and workspaces", "🪟 窗口和工作区"),
    "🐚 GNOME Shell": ("🐚 GNOME Shell", "🐚 GNOME Shell"),
    "🧱 Mutter: мозаика и мониторы": ("🧱 Mutter: tiling and monitors", "🧱 Mutter：平铺与显示器"),
    "🌊 Wayland": ("🌊 Wayland", "🌊 Wayland"),
    "🎛 Система и мультимедиа": ("🎛 System and multimedia", "🎛 系统和多媒体"),
    "⚓ Док": ("⚓ Dock", "⚓ 程序坞"),
    "⭐ Ваши собственные сочетания": ("⭐ Your custom shortcuts", "⭐ 你的自定义快捷键"),
    "💻 Терминал и командная строка": ("💻 Terminal and command line", "💻 终端和命令行"),
    "📝 Общие для программ": ("📝 Common to all apps", "📝 通用应用快捷键"),
    "Без названия": ("Untitled", "未命名"),
    # клавиши дока и шаблоны
    "Показать док (фокус на док)": ("Show the dock (focus the dock)", "显示程序坞（聚焦程序坞）"),
    "Запустить приложение из дока по номеру (Super+1 … Super+9)":
        ("Launch app from the dock by number (Super+1 … Super+9)", "按序号启动程序坞中的应用 (Super+1 … Super+9)"),
    "Перейти на рабочий стол {}": ("Go to workspace {}", "切换到工作区 {}"),
    "Переместить окно на рабочий стол {}": ("Move window to workspace {}", "将窗口移到工作区 {}"),
    "Открыть приложение №{} из дока": ("Open app #{} from the dock", "打开程序坞中的第 {} 个应用"),
    "(отпустить)": ("(release)", "(松开)"),
    "` (над Tab)": ("` (above Tab)", "` (Tab 上方)"),
    # терминал
    "Скопировать в терминале": ("Copy in terminal", "在终端中复制"),
    "Вставить в терминале": ("Paste in terminal", "在终端中粘贴"),
    "Новая вкладка терминала": ("New terminal tab", "新建终端标签页"),
    "Новое окно терминала": ("New terminal window", "新建终端窗口"),
    "Прервать запущенную команду": ("Interrupt the running command", "中断正在运行的命令"),
    "Конец ввода / выйти из терминала": ("End of input / exit the terminal", "输入结束 / 退出终端"),
    "Очистить экран": ("Clear the screen", "清屏"),
    "Поиск по истории команд": ("Search command history", "搜索命令历史"),
    "В начало строки": ("Jump to start of line", "跳到行首"),
    "В конец строки": ("Jump to end of line", "跳到行尾"),
    "Удалить всё слева от курсора": ("Delete everything left of the cursor", "删除光标左侧所有内容"),
    "Удалить всё справа от курсора": ("Delete everything right of the cursor", "删除光标右侧所有内容"),
    "Удалить слово слева": ("Delete the word on the left", "删除左侧的一个单词"),
    "Автодополнение имён и команд": ("Autocomplete names and commands", "自动补全名称和命令"),
    "Приостановить программу (вернуть: fg)": ("Suspend the program (resume with: fg)", "暂停程序（用 fg 恢复）"),
    "Последний аргумент предыдущей команды": ("Last argument of the previous command", "上一条命令的最后一个参数"),
    # общие
    "Копировать": ("Copy", "复制"),
    "Вставить": ("Paste", "粘贴"),
    "Вырезать": ("Cut", "剪切"),
    "Отменить действие": ("Undo", "撤销"),
    "Выделить всё": ("Select all", "全选"),
    "Поиск на странице / в файле": ("Find on page / in file", "在页面/文件中查找"),
    "Сохранить": ("Save", "保存"),
    "Новая вкладка в браузере": ("New browser tab", "新建浏览器标签页"),
    "Закрыть вкладку": ("Close tab", "关闭标签页"),
}
 
 
def T(s):
    """Перевод строки-ключа (русский оригинал) на выбранный язык."""
    if UI_LANG == "ru":
        return s
    e = TR.get(s)
    if not e:
        return s
    if UI_LANG == "en":
        return e[0]
    if UI_LANG == "zh":
        return e[1]
    if e[0] == s:
        return s
    return mt(e[0])
 
 
# Переводы «плейсхолдеров» в командах: <пакет> → <package> / <软件包>
PH = {
    "пакет": ("package", "软件包"), "слово": ("word", "关键词"), "файл.deb": ("file.deb", "文件.deb"),
    "имя": ("name", "名称"), "папка": ("folder", "文件夹"), "откуда": ("from", "源"),
    "куда": ("to", "目标"), "файл": ("file", "文件"), "текст": ("text", "文本"),
    "архив.tar.gz": ("archive.tar.gz", "压缩包.tar.gz"), "цель": ("target", "目标"),
    "ссылка": ("link", "链接"), "PID": ("PID", "PID"), "сервис": ("service", "服务"),
    "команда": ("command", "命令"),
}
 
 
def tr_cmd(cmd):
    if UI_LANG == "ru":
        return cmd
 
    def rep(m):
        name = m.group(1)
        v = PH.get(name)
        if not v:
            return "<" + name + ">"
        if UI_LANG == "en":
            w = v[0]
        elif UI_LANG == "zh":
            w = v[1]
        else:
            w = v[0]
            if "." not in w and w != "PID":
                w = mt(w)
            w = w.replace("<", "").replace(">", "").strip() or v[0]
        return "<" + w + ">"
 
    return re.sub(r"<([^<>]+)>", rep, cmd)
 
 
# Описания команд: ключ — команда (русский оригинал), значение — (en, zh)
DESC_TR = {
    "sudo apt update": (
        "Refreshes the LIST of available packages from the repositories. It doesn't change any programs — it just checks what's new.",
        "从软件源刷新可用软件包的列表。不会改动任何程序——只是“看看有什么新东西”。"),
    "sudo apt upgrade": (
        "Installs newer versions of already installed programs. Doesn't remove or add anything — a safe update.",
        "安装已安装程序的新版本。不会删除或新增任何软件包——安全的更新方式。"),
    "sudo apt full-upgrade": (
        "Full upgrade: may remove old and install new packages when needed to update (for example, a new kernel).",
        "完整升级：为完成升级，必要时会删除旧软件包并安装新软件包（例如新内核）。"),
    "sudo apt dist-upgrade": (
        "Old name of full-upgrade. Smartly resolves dependencies, upgrading the whole system.",
        "full-upgrade 的旧名称。智能处理依赖关系，升级整个系统。"),
    "sudo apt install <пакет>": (
        "Installs a program by package name. For example: sudo apt install vlc",
        "按软件包名称安装程序。例如：sudo apt install vlc"),
    "sudo apt remove <пакет>": (
        "Removes a program but keeps its configuration files.", "卸载程序，但保留其配置文件。"),
    "sudo apt purge <пакет>": (
        "Removes a program TOGETHER with its settings.", "卸载程序并同时删除其配置。"),
    "sudo apt autoremove": (
        "Removes “orphaned” packages that were installed as dependencies and are no longer needed.",
        "删除作为依赖安装、现已不再需要的“孤立”软件包。"),
    "sudo apt autoclean": (
        "Cleans the cache of downloaded .deb files that are now outdated.", "清理已过时的已下载 .deb 文件缓存。"),
    "sudo apt clean": (
        "Completely clears the downloaded package cache — frees disk space.", "彻底清空已下载软件包的缓存——释放磁盘空间。"),
    "apt search <слово>": (
        "Searches packages by a word in the name and description.", "按名称和描述中的关键词搜索软件包。"),
    "apt show <пакет>": (
        "Shows detailed package information: version, size, description.", "显示软件包详细信息：版本、大小、描述。"),
    "apt list --installed": ("List of all installed packages.", "所有已安装软件包的列表。"),
    "apt list --upgradable": (
        "Which packages can be upgraded (after apt update).", "哪些软件包可以升级（需先执行 apt update）。"),
    "sudo apt --fix-broken install": (
        "Tries to fix broken dependencies after a failed installation.", "尝试修复安装失败后损坏的依赖关系。"),
    "snap list": ("List of programs installed via Snap.", "通过 Snap 安装的程序列表。"),
    "sudo snap install <пакет>": ("Install a program from the Snap Store.", "从 Snap Store 安装程序。"),
    "sudo snap refresh": ("Update all snap programs.", "更新所有 snap 程序。"),
    "flatpak list": ("List of Flatpak programs.", "Flatpak 程序列表。"),
    "flatpak update": ("Update all Flatpak programs.", "更新所有 Flatpak 程序。"),
    "sudo dpkg -i <файл.deb>": ("Install a downloaded .deb file manually.", "手动安装已下载的 .deb 文件。"),
    "dpkg -l | grep <имя>": (
        "Check whether a package with this name is installed.", "检查是否已安装该名称的软件包。"),
    "pwd": ("Show which folder you are currently in.", "显示当前所在的文件夹。"),
    "ls -la": (
        "List files (including hidden) with permissions, size and date.", "列出文件（包括隐藏文件）及其权限、大小和日期。"),
    "cd <папка>": (
        "Go to a folder. “cd ..” goes up one level, “cd ~” goes home.", "进入文件夹。“cd ..”返回上一级，“cd ~”回到主目录。"),
    "mkdir -p <папка>": (
        "Create a folder (and all parent folders if they don't exist).", "创建文件夹（若父文件夹不存在则一并创建）。"),
    "touch <файл>": ("Create an empty file or update the modification time.", "创建空文件或更新修改时间。"),
    "cp -r <откуда> <куда>": ("Copy a file or folder (-r means recursive).", "复制文件或文件夹（-r 表示递归）。"),
    "mv <откуда> <куда>": ("Move or rename a file/folder.", "移动或重命名文件/文件夹。"),
    "rm <файл>": (
        "Delete a file. It does NOT go to the trash — it is gone forever!", "删除文件。不会进入回收站——将永久删除！"),
    "rm -r <папка>": (
        "Delete a folder with all its contents. Forever! Double-check the path.", "删除文件夹及其全部内容。永久删除！请务必再三确认路径。"),
    "cat <файл>": ("Print the file contents to the terminal.", "在终端中输出文件内容。"),
    "less <файл>": ("Read a file page by page (q — quit, / — search).", "分页阅读文件（q 退出，/ 搜索）。"),
    "tail -f <файл>": (
        "Follow the end of a file in real time (handy for logs).", "实时跟踪文件末尾（查看日志很方便）。"),
    "nano <файл>": (
        "A simple text editor in the terminal (Ctrl+O — save, Ctrl+X — exit).",
        "终端中的简易文本编辑器（Ctrl+O 保存，Ctrl+X 退出）。"),
    'find ~ -name "<имя>"': ("Find a file by name in the home folder.", "在主目录中按名称查找文件。"),
    'grep -rn "<текст>" .': ("Find text inside files of the current folder.", "在当前文件夹的文件内容中查找文本。"),
    "du -sh *": (
        "Size of each file and folder in the current directory.", "当前目录中每个文件和文件夹的大小。"),
    "chmod +x <файл>": ("Allow the file to be run as a program.", "允许将文件作为程序运行。"),
    "sudo chown $USER:$USER <файл>": ("Make yourself the owner of the file.", "将你自己设为该文件的所有者。"),
    "tar -czf <архив.tar.gz> <папка>": ("Pack a folder into a tar.gz archive.", "将文件夹打包为 tar.gz 压缩包。"),
    "tar -xzf <архив.tar.gz>": ("Unpack a tar.gz archive.", "解压 tar.gz 压缩包。"),
    "ln -s <цель> <ссылка>": ("Create a symbolic link (like a shortcut).", "创建符号链接（类似快捷方式）。"),
    "uname -a": ("Kernel version and architecture.", "内核版本和架构。"),
    "lsb_release -a": ("Which system version is installed.", "已安装的系统版本。"),
    "hostnamectl": ("Computer name, OS, kernel, virtualization.", "计算机名称、操作系统、内核、虚拟化信息。"),
    "uptime": (
        "How long the system has been running and the load average.", "系统已运行多长时间及平均负载。"),
    "whoami": ("Which user you are working as.", "你当前使用的用户名。"),
    "df -h": ("Free and used space on disks.", "磁盘的可用和已用空间。"),
    "free -h": ("RAM and swap usage.", "内存和交换空间使用情况。"),
    "lscpu": ("Processor information.", "处理器信息。"),
    "lsblk": ("Tree of disks and partitions.", "磁盘和分区树。"),
    "lspci": (
        "List of PCI devices (graphics card, network, etc.).", "PCI 设备列表（显卡、网卡等）。"),
    "lsusb": ("List of connected USB devices.", "已连接的 USB 设备列表。"),
    "ip a": ("Network interfaces and IP addresses.", "网络接口和 IP 地址。"),
    "ping -c 4 8.8.8.8": ("Check the internet connection (4 packets).", "检查网络连接（发送 4 个数据包）。"),
    "ss -tulpn": (
        "Which programs listen on which network ports.", "哪些程序在监听哪些网络端口。"),
    "top": ("Process monitor (q — quit).", "进程监视器（q 退出）。"),
    "htop": (
        "A friendlier process monitor (sudo apt install htop).", "更友好的进程监视器（sudo apt install htop）。"),
    "ps aux | grep <имя>": ("Find a running process by name.", "按名称查找正在运行的进程。"),
    "kill <PID>": (
        "End a process by its number. kill -9 — forcibly.", "按编号结束进程。kill -9 为强制结束。"),
    "killall <имя>": ("End all processes with this name.", "结束所有同名进程。"),
    "systemctl status <сервис>": (
        "Service status (for example: ssh, NetworkManager).", "服务状态（例如：ssh、NetworkManager）。"),
    "sudo systemctl restart <сервис>": ("Restart a service.", "重启服务。"),
    "systemctl --failed": ("Show services that failed to start.", "显示启动失败的服务。"),
    "journalctl -xe": (
        "Latest system messages with explanations (for finding errors).", "最新的系统消息及说明（用于排查错误）。"),
    "journalctl -b -p err": ("Only errors since the last boot.", "仅显示自上次启动以来的错误。"),
    "dmesg | tail": (
        "Latest kernel messages (drivers, USB, disks).", "最新的内核消息（驱动、USB、磁盘）。"),
    "sudo reboot": ("Reboot the computer.", "重启计算机。"),
    "sudo shutdown now": ("Shut down the computer immediately.", "立即关闭计算机。"),
    "sudo chmod -x /usr/share/cacheclean/cacheclean.sh": (
        "DISABLES the cache cleaning script: the file's execute permission is removed. The file itself stays in "
        "place and is not deleted, so you can enable it again with the command below.",
        "禁用缓存清理脚本：移除该文件的执行权限。文件本身保留在原处，不会被删除，因此可以用下面的命令重新启用。"),
    "sudo chmod +x /usr/share/cacheclean/cacheclean.sh": (
        "ENABLES the cache cleaning script again: restores the execute permission. This is the pair of the "
        "command above.",
        "重新启用缓存清理脚本：恢复执行权限。这是上一条命令的配套命令。"),
    "history": ("History of your commands. Ctrl+R — search it.", "你的命令历史。Ctrl+R 可搜索。"),
    "man <команда>": ("Manual for a command (q — quit).", "命令的手册（q 退出）。"),
    "<команда> --help": ("A short hint for a command.", "命令的简短帮助。"),
    "sudo !!": ("Repeat the previous command with sudo.", "用 sudo 重新执行上一条命令。"),
    "which <команда>": ("Where a program is located.", "程序所在的位置。"),
    "echo $PATH": (
        "List of folders where the system looks for programs.", "系统查找程序的文件夹列表。"),
    "clear": ("Clear the terminal screen (Ctrl+L).", "清除终端屏幕（Ctrl+L）。"),
    "sudo ufw status": ("Firewall status.", "防火墙状态。"),
    "sudo ufw enable": ("Enable the firewall.", "启用防火墙。"),
    "gsettings list-recursively org.gnome.desktop.wm.keybindings": (
        "Show all GNOME window-management keyboard shortcuts.", "显示 GNOME 所有窗口管理键盘快捷键。"),
}
 
 
def tr_desc(cmd, desc):
    if UI_LANG == "ru":
        return desc
    e = DESC_TR.get(cmd)
    if not e:
        return desc
    if UI_LANG == "en":
        return e[0]
    if UI_LANG == "zh":
        return e[1]
    return DESC_OFF.get(cmd, {}).get(CUR) or e[0]
 
 
def apply_env_messages():
    """Сообщения приветствия песочницы (читаются из окружения в .zshrc)."""
    def esc(s):
        return s.replace("%", "%%")
 
    os.environ["EH_MSG1A"] = esc(L("🧪 Песочница EasyHelper", "🧪 EasyHelper sandbox", "🧪 EasyHelper 沙盒"))
    os.environ["EH_MSG1B"] = esc(L(" — это не ваша система, ломайте что хотите.",
                                   " — this is not your system, break whatever you like.",
                                   " —— 这不是你的系统，随便折腾。"))
    os.environ["EH_MSG2"] = esc(L("→ принимает подсказку, ↑/↓ — история, Tab — дополнение",
                                  "→ accepts the suggestion, ↑/↓ — history, Tab — completion",
                                  "→ 接受建议，↑/↓ — 历史记录，Tab — 补全"))
    os.environ["EH_MSG3"] = L(
        "[песочница] симуляция: настоящая система не меняется",
        "[sandbox] simulated — your real system is not changed",
        "[沙盒] 模拟执行——真实系统不会被更改")
 
 
# ════════════════════════════════════════════════════════════════════
#  СТИЛИ
#  Окно прозрачное "в целом", но все части интерфейса, кроме терминала,
#  закрашены непрозрачным цветом (.opaque-bg). Поэтому прозрачным
#  остаётся только терминал.
#  Два набора: тёмный и светлый — выбирается по теме системы.
# ════════════════════════════════════════════════════════════════════
from string import Template  # noqa: E402
 
# Пиксельные шрифты: интерфейс — Pixelify Sans, моноширинный/запасной — GNU Unifont
PIXEL_UI_FONT = "Pixelify Sans"
PIXEL_MONO_FONT = "Unifont"
 
_CSS_TPL = Template("""
* { font-family: 'Pixelify Sans', 'Silkscreen', 'Press Start 2P', 'Unifont', 'Unifont Upper', sans-serif; }
window, window.csd, window.csd > decoration, window.background { border-radius:0; }
window.background { background-color: transparent; color:$fg; }
window.background.opaque-bg { background-color:$bg; }
.opaque-bg { background-color:$bg; }
.pad-bar { padding:8px 14px; }
 
headerbar { background:$bar; box-shadow:none; border-radius:0; border-bottom:2px solid $edge; color:$fg; }
headerbar button { border-radius:0; border:2px solid $edge; background:$card; background-image:none;
  color:$fg; box-shadow:2px 2px 0 $shadow; padding:4px 10px; }
headerbar button:hover { background:$hover; }
headerbar button:active { box-shadow:none; }
stackswitcher button {
  background:transparent; background-image:none; border:2px solid $edge; border-radius:0;
  padding:6px 18px; margin:0 4px; color:$fg; box-shadow:2px 2px 0 $shadow; }
stackswitcher button:hover { background:$hover; }
stackswitcher button:checked { background:$checked; border-color:$accent; box-shadow:none; }
 
.app-title { font-size:26px; font-weight:800; }
.app-sub   { color:$sub; }
.section-title { font-weight:700; font-size:15px; color:$title; margin-top:6px; }
.dim { color:$dim; font-size:12px; }
 
list.card-list { background:$card; border-radius:0; border:2px solid $edge; box-shadow:4px 4px 0 $shadow; }
list.card-list > row { background:transparent; border-radius:0; padding:10px 14px; border-bottom:2px solid $rowline; }
list.card-list > row:last-child { border-bottom:none; }
 
.keycap { background:$keycap; border-radius:0; padding:2px 9px; font-family:'Unifont','Pixelify Sans',monospace;
          font-weight:600; border:2px solid $keycap_edge; border-bottom-width:4px; color:$keycap_fg; }
.cmd { font-family:'Unifont','Pixelify Sans',monospace; font-size:13px; color:$cmd; font-weight:600; }
 
button.accent-btn { background:$accent; background-image:none; color:#fff; font-weight:600;
          border-radius:0; padding:6px 14px; border:2px solid $accent_edge; box-shadow:3px 3px 0 $shadow; }
button.accent-btn:hover { background:#b66cfa; }
button.accent-btn:active { box-shadow:none; }
button.ghost-btn { background:transparent; background-image:none; border:2px solid $edge;
          border-radius:0; padding:6px 14px; color:$fg; box-shadow:3px 3px 0 $shadow; }
button.ghost-btn:hover { background:$ghost_hover; }
button.ghost-btn:active { box-shadow:none; }
button.danger-btn { background:#dc2626; background-image:none; color:#fff; border:2px solid #7f1d1d;
          border-radius:0; padding:6px 14px; box-shadow:3px 3px 0 $shadow; }
button.danger-btn:hover { background:#ef4444; }
button.danger-btn:active { box-shadow:none; }
 
entry, searchentry { background:$card; color:$fg; border:2px solid $edge;
          border-radius:0; box-shadow:none; }
entry:focus-within, searchentry:focus-within { border-color:$accent; box-shadow:2px 2px 0 $accent; }
entry.cmd-entry { font-family:'Unifont','Pixelify Sans',monospace; font-size:14px; }
 
popover > contents { background:$card; color:$fg; border:2px solid $edge; border-radius:0; box-shadow:4px 4px 0 $shadow; }
popover > arrow { background:transparent; border:none; box-shadow:none; }
popover list, popover row { background:transparent; border-radius:0; }
popover row:hover { background:$hover; }
tooltip, tooltip.background { background:$card; color:$fg; border:2px solid $edge; border-radius:0; box-shadow:3px 3px 0 $shadow; }
tooltip > box { background:transparent; }
toast { background:$card; color:$fg; border:2px solid $edge; border-radius:0; box-shadow:3px 3px 0 $shadow; }
 
scrollbar trough { background:$card; border-radius:0; }
scrollbar slider { background:$accent; border:2px solid $accent_edge; border-radius:0; min-width:10px; min-height:10px; }
 
.warn { color:$warn; }
.ok   { color:$ok; }
.terminal-frame { border-top:2px solid $edge; border-bottom:2px solid $edge; border-radius:0; }
scrolledwindow, viewport { background:transparent; }
""")
 
_PAL_DARK = dict(
    bg="#181326", fg="#e8e3f3", bar="#1e182f", edge="#4a3d6e", shadow="#0d0916", accent="#a855f7",
    accent_edge="#6b21a8", sub="#a29bb8", title="#d8b4fe", dim="#8f88a6", card="#2a2142", rowline="#3a3058",
    keycap="#3f3162", keycap_edge="#1b1430", keycap_fg="#f3e8ff", cmd="#e9d5ff", ghost_hover="#34285a",
    hover="#34285a", checked="#3b2d63", warn="#fca5a5", ok="#86efac")
_PAL_LIGHT = dict(
    bg="#f6f3fb", fg="#241c3a", bar="#ece7f6", edge="#b5a6d6", shadow="#d6cde8", accent="#a855f7",
    accent_edge="#7e22ce", sub="#5f5778", title="#7e22ce", dim="#6b6482", card="#ffffff", rowline="#e3dcf0",
    keycap="#ece4fa", keycap_edge="#c9bde3", keycap_fg="#3b1f6b", cmd="#581c87", ghost_hover="#ece4fa",
    hover="#ece4fa", checked="#e3d6fb", warn="#b91c1c", ok="#15803d")
 
CSS_DARK = _CSS_TPL.substitute(_PAL_DARK)
CSS_LIGHT = _CSS_TPL.substitute(_PAL_LIGHT)
 
# ════════════════════════════════════════════════════════════════════
#  КОМАНДЫ  (категория, команда, описание, опасная?)
#  <в угловых скобках> — место, куда надо подставить своё значение
# ════════════════════════════════════════════════════════════════════
COMMANDS = [
    # ── APT
    ("Обновление системы (APT)", "sudo apt update",
     "Обновляет СПИСОК доступных пакетов из репозиториев. Сами программы не меняет — это «посмотреть, что нового есть».", False),
    ("Обновление системы (APT)", "sudo apt upgrade",
     "Ставит новые версии уже установленных программ. Ничего не удаляет и не добавляет — безопасное обновление.", False),
    ("Обновление системы (APT)", "sudo apt full-upgrade",
     "Полное обновление: может удалять старые и ставить новые пакеты, если это нужно для обновления (например, новое ядро).", False),
    ("Обновление системы (APT)", "sudo apt dist-upgrade",
     "Старое название full-upgrade. Умно разрешает зависимости, обновляя систему целиком.", False),
    ("Обновление системы (APT)", "sudo apt install <пакет>",
     "Устанавливает программу по имени пакета. Например: sudo apt install vlc", False),
    ("Обновление системы (APT)", "sudo apt remove <пакет>",
     "Удаляет программу, но оставляет её файлы настроек.", False),
    ("Обновление системы (APT)", "sudo apt purge <пакет>",
     "Удаляет программу ВМЕСТЕ с настройками.", False),
    ("Обновление системы (APT)", "sudo apt autoremove",
     "Удаляет «осиротевшие» пакеты, которые ставились как зависимости и больше не нужны.", False),
    ("Обновление системы (APT)", "sudo apt autoclean",
     "Чистит кэш скачанных .deb-файлов, которые уже устарели.", False),
    ("Обновление системы (APT)", "sudo apt clean",
     "Полностью очищает кэш скачанных пакетов — освобождает место на диске.", False),
    ("Обновление системы (APT)", "apt search <слово>",
     "Ищет пакеты по слову в названии и описании.", False),
    ("Обновление системы (APT)", "apt show <пакет>",
     "Показывает подробную информацию о пакете: версию, размер, описание.", False),
    ("Обновление системы (APT)", "apt list --installed",
     "Список всех установленных пакетов.", False),
    ("Обновление системы (APT)", "apt list --upgradable",
     "Какие пакеты можно обновить (после apt update).", False),
    ("Обновление системы (APT)", "sudo apt --fix-broken install",
     "Пытается починить сломанные зависимости после неудачной установки.", False),
    # ── Пакеты
    ("Snap / Flatpak / dpkg", "snap list", "Список программ, установленных через Snap.", False),
    ("Snap / Flatpak / dpkg", "sudo snap install <пакет>", "Установить программу из Snap Store.", False),
    ("Snap / Flatpak / dpkg", "sudo snap refresh", "Обновить все snap-программы.", False),
    ("Snap / Flatpak / dpkg", "flatpak list", "Список Flatpak-программ.", False),
    ("Snap / Flatpak / dpkg", "flatpak update", "Обновить все Flatpak-программы.", False),
    ("Snap / Flatpak / dpkg", "sudo dpkg -i <файл.deb>", "Установить скачанный .deb-файл вручную.", False),
    ("Snap / Flatpak / dpkg", "dpkg -l | grep <имя>", "Проверить, установлен ли пакет с таким именем.", False),
    # ── Файлы
    ("Файлы и папки", "pwd", "Показать, в какой папке вы сейчас находитесь.", False),
    ("Файлы и папки", "ls -la", "Список файлов (включая скрытые) с правами, размером и датой.", False),
    ("Файлы и папки", "cd <папка>", "Перейти в папку. «cd ..» — на уровень вверх, «cd ~» — домой.", False),
    ("Файлы и папки", "mkdir -p <папка>", "Создать папку (и все родительские, если их нет).", False),
    ("Файлы и папки", "touch <файл>", "Создать пустой файл или обновить время изменения.", False),
    ("Файлы и папки", "cp -r <откуда> <куда>", "Копировать файл или папку (-r — рекурсивно).", False),
    ("Файлы и папки", "mv <откуда> <куда>", "Переместить или переименовать файл/папку.", False),
    ("Файлы и папки", "rm <файл>", "Удалить файл. В корзину НЕ попадает — удаляется навсегда!", True),
    ("Файлы и папки", "rm -r <папка>", "Удалить папку со всем содержимым. Навсегда! Проверяйте путь дважды.", True),
    ("Файлы и папки", "cat <файл>", "Вывести содержимое файла в терминал.", False),
    ("Файлы и папки", "less <файл>", "Постранично читать файл (q — выход, / — поиск).", False),
    ("Файлы и папки", "tail -f <файл>", "Следить за концом файла в реальном времени (удобно для логов).", False),
    ("Файлы и папки", "nano <файл>", "Простой текстовый редактор в терминале (Ctrl+O — сохранить, Ctrl+X — выход).", False),
    ("Файлы и папки", 'find ~ -name "<имя>"', "Найти файл по имени в домашней папке.", False),
    ("Файлы и папки", 'grep -rn "<текст>" .', "Найти текст внутри файлов текущей папки.", False),
    ("Файлы и папки", "du -sh *", "Размер каждого файла и папки в текущей директории.", False),
    ("Файлы и папки", "chmod +x <файл>", "Разрешить запуск файла как программы.", False),
    ("Файлы и папки", "sudo chown $USER:$USER <файл>", "Сделать себя владельцем файла.", False),
    ("Файлы и папки", "tar -czf <архив.tar.gz> <папка>", "Упаковать папку в архив tar.gz.", False),
    ("Файлы и папки", "tar -xzf <архив.tar.gz>", "Распаковать архив tar.gz.", False),
    ("Файлы и папки", "ln -s <цель> <ссылка>", "Создать символическую ссылку (как ярлык).", False),
    # ── Система
    ("Информация о системе", "uname -a", "Версия ядра и архитектура.", False),
    ("Информация о системе", "lsb_release -a", "Какая версия системы установлена.", False),
    ("Информация о системе", "hostnamectl", "Имя компьютера, ОС, ядро, виртуализация.", False),
    ("Информация о системе", "uptime", "Сколько времени система работает и средняя нагрузка.", False),
    ("Информация о системе", "whoami", "Под каким пользователем вы работаете.", False),
    ("Информация о системе", "df -h", "Свободное и занятое место на дисках.", False),
    ("Информация о системе", "free -h", "Использование оперативной памяти и swap.", False),
    ("Информация о системе", "lscpu", "Информация о процессоре.", False),
    ("Информация о системе", "lsblk", "Дерево дисков и разделов.", False),
    ("Информация о системе", "lspci", "Список PCI-устройств (видеокарта, сеть и т.д.).", False),
    ("Информация о системе", "lsusb", "Список подключённых USB-устройств.", False),
    ("Информация о системе", "ip a", "Сетевые интерфейсы и IP-адреса.", False),
    ("Информация о системе", "ping -c 4 8.8.8.8", "Проверить связь с интернетом (4 пакета).", False),
    ("Информация о системе", "ss -tulpn", "Какие программы слушают какие сетевые порты.", False),
    # ── Процессы и службы
    ("Процессы и службы", "top", "Монитор процессов (q — выход).", False),
    ("Процессы и службы", "htop", "Удобный монитор процессов (sudo apt install htop).", False),
    ("Процессы и службы", "ps aux | grep <имя>", "Найти запущенный процесс по имени.", False),
    ("Процессы и службы", "kill <PID>", "Завершить процесс по номеру. kill -9 — принудительно.", False),
    ("Процессы и службы", "killall <имя>", "Завершить все процессы с таким именем.", False),
    ("Процессы и службы", "systemctl status <сервис>", "Статус службы (например: ssh, NetworkManager).", False),
    ("Процессы и службы", "sudo systemctl restart <сервис>", "Перезапустить службу.", False),
    ("Процессы и службы", "systemctl --failed", "Показать службы, которые не смогли запуститься.", False),
    ("Процессы и службы", "journalctl -xe", "Последние системные сообщения с пояснениями (для поиска ошибок).", False),
    ("Процессы и службы", "journalctl -b -p err", "Только ошибки с момента последней загрузки.", False),
    ("Процессы и службы", "dmesg | tail", "Последние сообщения ядра (драйверы, USB, диски).", False),
    ("Процессы и службы", "sudo reboot", "Перезагрузить компьютер.", True),
    ("Процессы и службы", "sudo shutdown now", "Выключить компьютер немедленно.", True),
    # ── Прочее
    ("CacheClean (вкл/выкл)", "sudo chmod -x /usr/share/cacheclean/cacheclean.sh",
     "ОТКЛЮЧАЕТ скрипт очистки кэша: у файла снимается право на запуск. Сам файл остаётся на месте и не удаляется, "
     "так что его можно включить обратно командой ниже.", False),
    ("CacheClean (вкл/выкл)", "sudo chmod +x /usr/share/cacheclean/cacheclean.sh",
     "ВКЛЮЧАЕТ скрипт очистки кэша обратно: возвращает право на запуск. Это пара к команде выше.", False),
    ("Полезное", "history", "История ваших команд. Ctrl+R — поиск по ней.", False),
    ("Полезное", "man <команда>", "Справка по команде (q — выход).", False),
    ("Полезное", "<команда> --help", "Краткая подсказка по команде.", False),
    ("Полезное", "sudo !!", "Повторить предыдущую команду с sudo.", False),
    ("Полезное", "which <команда>", "Где лежит программа.", False),
    ("Полезное", "echo $PATH", "Список папок, где система ищет программы.", False),
    ("Полезное", "clear", "Очистить экран терминала (Ctrl+L).", False),
    ("Полезное", "sudo ufw status", "Состояние брандмауэра.", False),
    ("Полезное", "sudo ufw enable", "Включить брандмауэр.", False),
    ("Полезное", "gsettings list-recursively org.gnome.desktop.wm.keybindings",
     "Показать все клавиатурные сочетания управления окнами GNOME.", False),
]
 
# ════════════════════════════════════════════════════════════════════
#  ГОРЯЧИЕ КЛАВИШИ: что анализируем
# ════════════════════════════════════════════════════════════════════
DOCK_KEYS = {"shortcut", "app-hotkey-1"}
SCHEMAS = [
    ("org.gnome.desktop.wm.keybindings", "🪟 Окна и рабочие столы", None),
    ("org.gnome.shell.keybindings", "🐚 GNOME Shell", None),
    ("org.gnome.mutter.keybindings", "🧱 Mutter: мозаика и мониторы", None),
    ("org.gnome.mutter.wayland.keybindings", "🌊 Wayland", None),
    ("org.gnome.settings-daemon.plugins.media-keys", "🎛 Система и мультимедиа", None),
    ("org.gnome.shell.extensions.dash-to-dock", "⚓ Док", DOCK_KEYS),
]
CUSTOM_SCHEMA = "org.gnome.settings-daemon.plugins.media-keys"
 
KEY_RU = {
    # окна
    "close": "Закрыть окно", "minimize": "Свернуть окно", "maximize": "Развернуть окно",
    "unmaximize": "Восстановить размер окна", "toggle-maximized": "Развернуть / восстановить окно",
    "toggle-fullscreen": "Полноэкранный режим", "show-desktop": "Показать рабочий стол",
    "switch-windows": "Переключение между окнами", "switch-windows-backward": "Переключение между окнами (назад)",
    "switch-applications": "Переключение между приложениями",
    "switch-applications-backward": "Переключение между приложениями (назад)",
    "switch-group": "Переключение между окнами одного приложения",
    "switch-group-backward": "Окна одного приложения (назад)",
    "cycle-windows": "Циклический перебор окон", "cycle-windows-backward": "Перебор окон (назад)",
    "cycle-group": "Перебор окон группы", "cycle-group-backward": "Перебор окон группы (назад)",
    "switch-to-workspace-left": "Рабочий стол слева", "switch-to-workspace-right": "Рабочий стол справа",
    "switch-to-workspace-up": "Рабочий стол выше", "switch-to-workspace-down": "Рабочий стол ниже",
    "switch-to-workspace-last": "Последний рабочий стол",
    "move-to-workspace-left": "Переместить окно на рабочий стол слева",
    "move-to-workspace-right": "Переместить окно на рабочий стол справа",
    "move-to-workspace-up": "Переместить окно на рабочий стол выше",
    "move-to-workspace-down": "Переместить окно на рабочий стол ниже",
    "move-to-workspace-last": "Переместить окно на последний рабочий стол",
    "move-to-monitor-left": "Окно на монитор слева", "move-to-monitor-right": "Окно на монитор справа",
    "move-to-monitor-up": "Окно на монитор выше", "move-to-monitor-down": "Окно на монитор ниже",
    "toggle-on-all-workspaces": "Окно на всех рабочих столах",
    "activate-window-menu": "Меню окна", "begin-move": "Переместить окно с клавиатуры",
    "begin-resize": "Изменить размер окна с клавиатуры", "lower": "Опустить окно под остальные",
    "raise": "Поднять окно над остальными", "raise-or-lower": "Поднять / опустить окно",
    "panel-run-dialog": "Окно «Выполнить команду»", "panel-main-menu": "Главное меню",
    "switch-input-source": "Следующая раскладка клавиатуры",
    "switch-input-source-backward": "Предыдущая раскладка клавиатуры",
    # shell
    "toggle-overview": "Обзор окон (Activities)", "toggle-application-view": "Все приложения",
    "toggle-message-tray": "Календарь и уведомления", "focus-active-notification": "Фокус на уведомлении",
    "screenshot": "Снимок всего экрана", "screenshot-window": "Снимок окна",
    "show-screenshot-ui": "Скриншот / запись экрана (интерфейс)",
    "show-screen-recording-ui": "Запись экрана", "toggle-quick-settings": "Быстрые настройки",
    "open-application-menu": "Меню приложения", "shift-overview-up": "Обзор: сдвиг вверх",
    "shift-overview-down": "Обзор: сдвиг вниз", "toggle-tiled-left": "Прижать окно к левой половине",
    "toggle-tiled-right": "Прижать окно к правой половине", "switch-monitor": "Режим мониторов (дублировать/расширить)",
    "rotate-monitor": "Повернуть экран", "cancel-input-capture": "Отменить захват ввода",
    # media-keys
    "terminal": "Открыть терминал", "home": "Домашняя папка", "www": "Открыть браузер",
    "email": "Почта", "calculator": "Калькулятор", "search": "Поиск", "help": "Справка",
    "screensaver": "Заблокировать экран", "logout": "Меню выключения / выхода",
    "volume-up": "Громкость +", "volume-down": "Громкость −", "volume-mute": "Выключить звук",
    "mic-mute": "Выключить микрофон", "play": "Воспроизведение", "pause": "Пауза",
    "stop": "Стоп", "next": "Следующий трек", "previous": "Предыдущий трек", "eject": "Извлечь диск",
    "screenreader": "Экранный диктор", "magnifier": "Лупа (экранная)",
    "magnifier-zoom-in": "Лупа: приблизить", "magnifier-zoom-out": "Лупа: отдалить",
    "on-screen-keyboard": "Экранная клавиатура", "increase-text-size": "Увеличить текст",
    "decrease-text-size": "Уменьшить текст", "toggle-contrast": "Высокий контраст",
    "control-center": "Параметры системы", "touchpad-toggle": "Вкл/выкл тачпад",
    "touchpad-on": "Включить тачпад", "touchpad-off": "Выключить тачпад",
    "screen-brightness-up": "Яркость экрана +", "screen-brightness-down": "Яркость экрана −",
    "keyboard-brightness-up": "Подсветка клавиатуры +", "keyboard-brightness-down": "Подсветка клавиатуры −",
    "keyboard-brightness-toggle": "Подсветка клавиатуры вкл/выкл", "power": "Кнопка питания",
    "suspend": "Ждущий режим", "hibernate": "Гибернация", "rfkill": "Режим «в самолёте»",
    "rotate-video-lock": "Блокировка поворота экрана", "playback-rewind": "Перемотка назад",
    "playback-forward": "Перемотка вперёд", "playback-repeat": "Повтор", "playback-random": "Случайный порядок",
    "media": "Медиаплеер", "battery": "Показать заряд батареи", "shortcut": "Показать док (фокус на док)",
    "app-hotkey-1": "Запустить приложение из дока по номеру (Super+1 … Super+9)",
}
KEY_PATTERNS = [
    (r"switch-to-workspace-(\d+)", "Перейти на рабочий стол {}"),
    (r"move-to-workspace-(\d+)", "Переместить окно на рабочий стол {}"),
    (r"switch-to-application-(\d+)", "Открыть приложение №{} из дока"),
]
 
MODS = {"Primary": "Ctrl", "Control": "Ctrl", "Ctrl": "Ctrl", "Shift": "Shift", "Alt": "Alt",
        "Mod1": "Alt", "Super": "Super", "Mod4": "Super", "Meta": "Meta", "Hyper": "Hyper",
        "Release": "(отпустить)"}
KEYS = {"Return": "Enter", "Page_Up": "PgUp", "Page_Down": "PgDn", "Prior": "PgUp", "Next": "PgDn",
        "Print": "PrtSc", "Escape": "Esc", "space": "Space", "minus": "−", "plus": "+",
        "Above_Tab": "` (над Tab)", "grave": "`", "Left": "←", "Right": "→", "Up": "↑", "Down": "↓",
        "BackSpace": "⌫", "Delete": "Del", "comma": ",", "period": ".", "slash": "/",
        "bracketleft": "[", "bracketright": "]", "Super_L": "Super", "Super_R": "Super",
        "XF86AudioRaiseVolume": "Vol+", "XF86AudioLowerVolume": "Vol−", "XF86AudioMute": "Mute",
        "XF86AudioPlay": "Play", "XF86AudioPause": "Pause", "XF86AudioStop": "Stop",
        "XF86AudioNext": "Next", "XF86AudioPrev": "Prev", "XF86MonBrightnessUp": "Bright+",
        "XF86MonBrightnessDown": "Bright−", "XF86AudioMicMute": "MicMute", "XF86Calculator": "Calc",
        "XF86WWW": "WWW", "XF86Mail": "Mail", "XF86HomePage": "Home", "XF86Search": "Search"}
 
TERMINAL_SHORTCUTS = [
    ("Скопировать в терминале", "", ["<Primary><Shift>c"]),
    ("Вставить в терминале", "", ["<Primary><Shift>v"]),
    ("Новая вкладка терминала", "", ["<Primary><Shift>t"]),
    ("Новое окно терминала", "", ["<Primary><Shift>n"]),
    ("Прервать запущенную команду", "SIGINT", ["<Primary>c"]),
    ("Конец ввода / выйти из терминала", "EOF", ["<Primary>d"]),
    ("Очистить экран", "clear", ["<Primary>l"]),
    ("Поиск по истории команд", "reverse-search", ["<Primary>r"]),
    ("В начало строки", "", ["<Primary>a"]),
    ("В конец строки", "", ["<Primary>e"]),
    ("Удалить всё слева от курсора", "", ["<Primary>u"]),
    ("Удалить всё справа от курсора", "", ["<Primary>k"]),
    ("Удалить слово слева", "", ["<Primary>w"]),
    ("Автодополнение имён и команд", "", ["Tab"]),
    ("Приостановить программу (вернуть: fg)", "SIGTSTP", ["<Primary>z"]),
    ("Последний аргумент предыдущей команды", "", ["<Alt>period"]),
]
GENERAL_SHORTCUTS = [
    ("Копировать", "", ["<Primary>c"]), ("Вставить", "", ["<Primary>v"]),
    ("Вырезать", "", ["<Primary>x"]), ("Отменить действие", "", ["<Primary>z"]),
    ("Выделить всё", "", ["<Primary>a"]), ("Поиск на странице / в файле", "", ["<Primary>f"]),
    ("Сохранить", "", ["<Primary>s"]), ("Новая вкладка в браузере", "", ["<Primary>t"]),
    ("Закрыть вкладку", "", ["<Primary>w"]),
]
 
 
def tr_items(lst):
    return [(T(d), s, a) for d, s, a in lst]
 
 
def terminal_sections():
    return [(T("💻 Терминал и командная строка"), tr_items(TERMINAL_SHORTCUTS)),
            (T("📝 Общие для программ"), tr_items(GENERAL_SHORTCUTS))]
 
 
def looks_accel(a: str) -> bool:
    if not a or a == "disabled" or a.startswith("/"):
        return False
    if "<" in a:
        return True
    return bool(re.fullmatch(r"(XF86\w+|F\d{1,2}|Print|Pause|Home|Escape|Cancel|Super_[LR]|Num_Lock|Scroll_Lock)", a))
 
 
def parse_accels(val: str):
    v = val.strip()
    if v.startswith("@as"):
        v = v[3:].strip()
    try:
        x = ast.literal_eval(v)
    except Exception:
        return []
    if isinstance(x, str):
        x = [x]
    if not isinstance(x, (list, tuple)):
        return []
    return [a for a in x if isinstance(a, str) and looks_accel(a)]
 
 
def pretty_accel(accel: str):
    mods = re.findall(r"<(\w+)>", accel)
    key = re.sub(r"<\w+>", "", accel)
    parts = [T(MODS.get(m, m)) for m in mods]
    if key:
        if key in KEYS:
            k = T(KEYS[key])
        elif key.startswith("XF86"):
            k = key[4:]
        elif len(key) == 1:
            k = key.upper()
        else:
            k = key
        parts.append(k)
    return parts
 
 
# ── системные переводы (gettext) — названия клавиш на выбранном языке
GCC_DOMAINS = ("gnome-control-center-2.0", "gnome-control-center", "gnome-settings-daemon", "mutter", "gnome-shell")
LOCALE_DIRS = ("/usr/share/locale-langpack", "/usr/share/locale")
 
 
def gettext_langs():
    if CUR == "en":
        return []
    langs = [CUR]
    base = CUR.split("_")[0]
    if base != CUR:
        langs.append(base)
    return langs
 
 
def _get_trans(domain):
    t = _TRANS.get(domain)
    if t is None:
        t = gettext.NullTranslations()
        langs = gettext_langs()
        if langs:
            for d in LOCALE_DIRS:
                try:
                    t = gettext.translation(domain, d, languages=langs)
                    break
                except Exception:
                    continue
        _TRANS[domain] = t
    return t
 
 
def _gt(domain, msg, ctx=None):
    if not domain or CUR == "en":
        return msg
    t = _get_trans(domain)
    try:
        if ctx:
            m = ctx + "\x04" + msg
            r = t.gettext(m)
            return msg if r == m else r
        return t.gettext(msg)
    except Exception:
        return msg
 
 
def sys_tr(domains, msg, ctx=None):
    for d in domains:
        if not d:
            continue
        r = _gt(d, msg, ctx)
        if r != msg:
            return r
    # системного перевода нет: пробуем встроенную офлайн-таблицу (если есть), иначе оригинал
    return mt(msg) if UI_LANG == "auto" else msg
 
 
def describe_key(schema, key, gcc, summaries):
    if UI_LANG == "ru":
        if key in KEY_RU:
            return KEY_RU[key]
        for pat, tpl in KEY_PATTERNS:
            m = re.fullmatch(pat, key)
            if m:
                return tpl.format(m.group(1))
        return gcc.get((schema, key)) or summaries.get((schema, key)) or key
    # другие языки: сначала системные (переведённые) описания GNOME
    if schema.endswith("dash-to-dock") and key in DOCK_KEYS:
        return T(KEY_RU[key])
    v = gcc.get((schema, key)) or summaries.get((schema, key))
    if v:
        return v
    for pat, tpl in KEY_PATTERNS:
        m = re.fullmatch(pat, key)
        if m:
            return T(tpl).format(m.group(1))
    return key
 
 
def run_out(cmd, timeout=6):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
 
 
def load_summaries(ids):
    res = {}
    for p in glob.glob("/usr/share/glib-2.0/schemas/*.gschema.xml"):
        try:
            txt = open(p, encoding="utf-8").read()
            if not any(f'"{i}"' in txt for i in ids):
                continue
            root = ET.fromstring(txt)
        except Exception:
            continue
        for sc in root.iter("schema"):
            sid = sc.get("id")
            if sid not in ids:
                continue
            dom = sc.get("gettext-domain") or root.get("gettext-domain")
            for k in sc.findall("key"):
                s = k.find("summary")
                if s is not None and s.text:
                    text = s.text.strip()
                    res[(sid, k.get("name"))] = sys_tr((dom,) + GCC_DOMAINS, text, s.get("context"))
    return res
 
 
def load_gcc_descriptions():
    res = {}
    for p in glob.glob("/usr/share/gnome-control-center/keybindings/*.xml"):
        try:
            root = ET.parse(p).getroot()
        except Exception:
            continue
        for ents in root.iter("KeyListEntries"):
            schema = ents.get("schema")
            domains = (ents.get("package"),) + GCC_DOMAINS
            for e in ents.findall("KeyListEntry"):
                if schema and e.get("name") and e.get("description"):
                    res[(schema, e.get("name"))] = sys_tr(domains, e.get("description"))
    return res
 
 
def analyze_shortcuts():
    """Читает реальные комбинации системы. Возвращает (секции, статистика)."""
    stats = {"schemas": 0, "count": 0, "gsettings": True}
    sections = []
    try:
        have = set(run_out(["gsettings", "list-schemas"]).split())
    except Exception:
        have = set()
        stats["gsettings"] = False
    summaries = load_summaries({s[0] for s in SCHEMAS})
    gcc = load_gcc_descriptions()
 
    for schema, title, allow in SCHEMAS:
        if schema not in have:
            continue
        try:
            out = run_out(["gsettings", "list-recursively", schema])
        except Exception:
            continue
        items = []
        for line in out.splitlines():
            parts = line.split(" ", 2)
            if len(parts) < 3:
                continue
            _, key, val = parts
            if allow and key not in allow:
                continue
            accels = parse_accels(val)
            if accels:
                items.append((describe_key(schema, key, gcc, summaries), schema.split(".")[-1] + " · " + key, accels))
        if items:
            items.sort(key=lambda i: i[0].lower())
            sections.append((T(title), items))
            stats["schemas"] += 1
            stats["count"] += len(items)
 
    # пользовательские
    try:
        raw = run_out(["gsettings", "get", CUSTOM_SCHEMA, "custom-keybindings"]).strip()
        if raw.startswith("@as"):
            raw = raw[3:].strip()
        paths = ast.literal_eval(raw) if raw else []
        items = []
        for path in paths:
            sch = f"{CUSTOM_SCHEMA}.custom-keybinding:{path}"
            g = lambda k: ast.literal_eval(run_out(["gsettings", "get", sch, k]).strip() or "''")
            name, cmd, bind = g("name"), g("command"), g("binding")
            if looks_accel(bind):
                items.append((name or T("Без названия"),
                              L("команда: {cmd}", "command: {cmd}", "命令：{cmd}").format(cmd=cmd), [bind]))
        if items:
            sections.append((T("⭐ Ваши собственные сочетания"), items))
            stats["count"] += len(items)
    except Exception:
        pass
 
    sections.extend(terminal_sections())
    return sections, stats
 
 
# ════════════════════════════════════════════════════════════════════
#  ПЕСОЧНИЦА: файлы, движок, запуск
# ════════════════════════════════════════════════════════════════════
ZSHRC = r'''# EasyHelper sandbox zsh
export LANG=C.UTF-8
export TERM=${TERM:-xterm-256color}
HISTFILE=~/.zsh_history
HISTSIZE=50000
SAVEHIST=50000
if [ -r /opt/easyhelper/seed_history ] && [ ! -s "$HISTFILE" ]; then
  cp /opt/easyhelper/seed_history "$HISTFILE" 2>/dev/null
fi
setopt APPEND_HISTORY SHARE_HISTORY INC_APPEND_HISTORY HIST_IGNORE_DUPS HIST_REDUCE_BLANKS
setopt AUTO_CD INTERACTIVE_COMMENTS PROMPT_SUBST
autoload -Uz compinit && compinit -u -d ~/.zcompdump
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'
zstyle ':completion:*' list-colors ''
autoload -Uz colors && colors
bindkey -e
bindkey '^[[A' history-beginning-search-backward
bindkey '^[OA' history-beginning-search-backward
bindkey '^[[B' history-beginning-search-forward
bindkey '^[OB' history-beginning-search-forward
bindkey '^[[3~' delete-char
bindkey '^[[H' beginning-of-line
bindkey '^[[F' end-of-line
PROMPT='%F{141}sandbox%f%F{245}@%f%F{51}easyhelper%f %F{221}%~%f %F{141}❯%f '
alias ls='ls --color=auto' ll='ls -alF --color=auto' la='ls -A --color=auto' grep='grep --color=auto'
precmd() { print -Pn "\e]0;sandbox:%~\a" }
ZSH_AUTOSUGGEST_STRATEGY=(history completion)
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=244'
for f in /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh \
         /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh; do
  [ -r "$f" ] && source "$f" && break
done
# подсветка синтаксиса — строго последней
for f in /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh \
         /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh; do
  [ -r "$f" ] && source "$f" && break
done
print -P "%F{141}${EH_MSG1A:-EasyHelper sandbox}%f${EH_MSG1B}"
print -P "%F{245}${EH_MSG2}%f\n"
'''
 
DOCKERFILE = '''FROM docker.io/library/ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8
RUN apt-get update && apt-get install -y --no-install-recommends \\
    zsh zsh-autosuggestions zsh-syntax-highlighting sudo ca-certificates locales \\
    nano vim-tiny curl wget git htop tree less man-db manpages procps psmisc \\
    iputils-ping iproute2 net-tools dnsutils file zip unzip lsb-release \\
    bash-completion pciutils usbutils bsdmainutils unminimize \\
    && (yes | unminimize || true)
RUN useradd -m -s /usr/bin/zsh -G sudo user \\
    && echo 'user ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/user && chmod 0440 /etc/sudoers.d/user
COPY --chown=user:user zshrc /home/user/.zshrc
COPY seed_history /opt/easyhelper/seed_history
USER user
WORKDIR /home/user
CMD ["zsh"]
'''
 
# аргументы: $1 движок, $2 образ, $3 папка, $4 имя, $5/$6/$7 — сообщения
BOOT_SCRIPT = r'''
engine="$1"; img="$2"; dir="$3"; name="$4"
"$engine" rm -f "$name" >/dev/null 2>&1
if ! "$engine" image inspect "$img" >/dev/null 2>&1; then
  echo "$5"
  "$engine" build -t "$img" "$dir" || { echo "$6"; read -rsn1 -p "$7"; exit 1; }
fi
exec "$engine" run --rm -it --name "$name" --hostname easyhelper --memory 1g --pids-limit 512 --security-opt no-new-privileges=false \
  -e TERM=xterm-256color -e COLORTERM=truecolor -e EH_MSG1A -e EH_MSG1B -e EH_MSG2 "$img"
'''
 
 
# ── обёртки для режима bubblewrap (там sudo не работает: ядро запрещает повышение привилегий)
SHIM_SUDO = r'''#!/bin/bash
# EasyHelper sandbox: эмуляция sudo (повышать права не нужно и нельзя)
while [ $# -gt 0 ]; do
  case "$1" in
    -u|-g|-h|-p|-C|-D|-R|-T|-U) shift 2 ;;
    --) shift; break ;;
    -*) shift ;;
    *) break ;;
  esac
done
if [ $# -eq 0 ]; then
  exec "${SHELL:-/bin/bash}"
fi
exec "$@"
'''

SHIM_APT = r'''#!/bin/bash
# EasyHelper sandbox: безопасная имитация apt (настоящая система не меняется)
me="${0##*/}"
sub=""
pk=()
for a in "$@"; do
  case "$a" in
    -*) ;;
    *) if [ -z "$sub" ]; then sub="$a"; else pk+=("$a"); fi ;;
  esac
done
note() { printf '\033[2m%s\033[0m\n' "${EH_MSG3:-[sandbox] simulated}"; }
lists() {
  echo "Reading package lists... Done"
  echo "Building dependency tree... Done"
  echo "Reading state information... Done"
}
case "$sub" in
  update)
    sleep 0.4
    echo "Hit:1 http://archive.ubuntu.com/ubuntu noble InRelease"
    echo "Hit:2 http://archive.ubuntu.com/ubuntu noble-updates InRelease"
    echo "Hit:3 http://archive.ubuntu.com/ubuntu noble-backports InRelease"
    echo "Hit:4 http://security.ubuntu.com/ubuntu noble-security InRelease"
    lists
    echo "All packages are up to date."
    note ;;
  upgrade|full-upgrade|dist-upgrade)
    sleep 0.3
    lists
    echo "Calculating upgrade... Done"
    echo "0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded."
    note ;;
  autoremove|autopurge)
    lists
    echo "0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded."
    note ;;
  autoclean|auto-clean)
    lists
    note ;;
  clean)
    note ;;
  install|reinstall)
    lists
    if [ ${#pk[@]} -gt 0 ]; then
      echo "The following NEW packages will be installed:"
      echo "  ${pk[*]}"
    fi
    echo "0 upgraded, ${#pk[@]} newly installed, 0 to remove and 0 not upgraded."
    for p in "${pk[@]}"; do echo "Setting up $p ..."; done
    note ;;
  remove|purge)
    lists
    if [ ${#pk[@]} -gt 0 ]; then
      echo "The following packages will be REMOVED:"
      echo "  ${pk[*]}"
    fi
    echo "0 upgraded, 0 newly installed, ${#pk[@]} to remove and 0 not upgraded."
    for p in "${pk[@]}"; do echo "Removing $p ..."; done
    note ;;
  *)
    exec "/usr/bin/$me" "$@" ;;
esac
'''


def write_shims():
    d = APP_DIR / "bwrap-bin"
    d.mkdir(parents=True, exist_ok=True)
    for name, body in (("sudo", SHIM_SUDO), ("apt", SHIM_APT), ("apt-get", SHIM_APT)):
        p = d / name
        p.write_text(body, encoding="utf-8")
        p.chmod(0o755)
    return d


def prepare_files():
    ctx = APP_DIR / "build"
    ctx.mkdir(parents=True, exist_ok=True)
    seen, hist = set(), []
    for _, cmd, _, danger in COMMANDS:
        if "<" in cmd or danger or cmd in seen:
            continue
        seen.add(cmd)
        hist.append(cmd)
    seed = "\n".join(hist) + "\n"
    (ctx / "Dockerfile").write_text(DOCKERFILE, encoding="utf-8")
    (ctx / "zshrc").write_text(ZSHRC, encoding="utf-8")
    (ctx / "seed_history").write_text(seed, encoding="utf-8")
    (APP_DIR / "passwd").write_text(
        "root:x:0:0:root:/root:/bin/sh\nuser:x:1000:1000:user:/home/user:/usr/bin/zsh\n"
        "nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\n", encoding="utf-8")
    (APP_DIR / "group").write_text("root:x:0:\nuser:x:1000:\nnogroup:x:65534:\n", encoding="utf-8")
    write_shims()
    h = hashlib.sha1((DOCKERFILE + ZSHRC + seed).encode()).hexdigest()[:8]
    return ctx, f"easyhelper-sandbox:{h}"
 
 
def detect_engine():
    for e in ("podman", "docker"):
        if shutil.which(e):
            try:
                if subprocess.run([e, "info"], capture_output=True, timeout=20).returncode == 0:
                    return e
            except Exception:
                pass
    return "bwrap" if shutil.which("bwrap") else None
 
 
def bwrap_argv():
    zsh = shutil.which("zsh")
    zsh = os.path.realpath(zsh) if zsh else None
    use_zsh = bool(zsh and zsh.startswith("/usr/"))
    shell = [zsh] if use_zsh else ["/usr/bin/bash", "--noprofile", "--norc", "-i"]
    ctx = APP_DIR / "build"
    a = ["bwrap", "--unshare-all", "--share-net", "--die-with-parent", "--uid", "1000", "--gid", "1000",
         "--ro-bind", "/usr", "/usr", "--symlink", "usr/bin", "/bin", "--symlink", "usr/sbin", "/sbin",
         "--symlink", "usr/lib", "/lib", "--symlink", "usr/lib64", "/lib64",
         "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--tmpfs", "/run", "--tmpfs", "/home/user",
         "--ro-bind-try", "/etc/alternatives", "/etc/alternatives",
         "--ro-bind-try", "/etc/ld.so.cache", "/etc/ld.so.cache",
         "--ro-bind-try", "/etc/ssl", "/etc/ssl",
         "--ro-bind-try", "/etc/resolv.conf", "/etc/resolv.conf",
         "--ro-bind-try", "/run/systemd/resolve", "/run/systemd/resolve",
         "--ro-bind-try", "/etc/hosts", "/etc/hosts",
         "--ro-bind", str(APP_DIR / "passwd"), "/etc/passwd", "--ro-bind", str(APP_DIR / "group"), "/etc/group",
         "--ro-bind", str(ctx / "zshrc"), "/home/user/.zshrc",
         "--ro-bind", str(ctx / "seed_history"), "/opt/easyhelper/seed_history",
         "--ro-bind", str(APP_DIR / "bwrap-bin"), "/opt/easyhelper/bin",
         "--ro-bind-try", "/etc/apt", "/etc/apt",
         "--ro-bind-try", "/var/lib/dpkg", "/var/lib/dpkg",
         "--ro-bind-try", "/var/lib/apt/lists", "/var/lib/apt/lists",
         "--ro-bind-try", "/var/cache/apt", "/var/cache/apt",
         "--setenv", "HOME", "/home/user", "--setenv", "USER", "user", "--setenv", "LANG", "C.UTF-8",
         "--setenv", "TERM", "xterm-256color", "--setenv", "COLORTERM", "truecolor",
         "--setenv", "PATH", "/opt/easyhelper/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
         "--setenv", "EH_MSG1A", os.environ.get("EH_MSG1A", ""),
         "--setenv", "EH_MSG1B", os.environ.get("EH_MSG1B", ""),
         "--setenv", "EH_MSG2", os.environ.get("EH_MSG2", ""),
         "--setenv", "EH_MSG3", os.environ.get("EH_MSG3", ""),
         "--setenv", "PS1", r"\[\e[35m\]sandbox\[\e[0m\]@easyhelper \w $ ",
         "--setenv", "PROMPT_COMMAND", r'printf "\033]0;sandbox:%s\007" "$PWD"',
         "--chdir", "/home/user"]
    return a + shell, use_zsh
 
 
# ════════════════════════════════════════════════════════════════════
#  ВСПОМОГАТЕЛЬНОЕ ДЛЯ VTE
# ════════════════════════════════════════════════════════════════════
def rgba(r, g, b, a=1.0):
    c = Gdk.RGBA()
    c.red, c.green, c.blue, c.alpha = r, g, b, a
    return c
 
 
def style_terminal(t):
    t.set_font(Pango.FontDescription("Unifont,VT323,Monospace 12"))
    try:
        t.set_cursor_shape(Vte.CursorShape.BLOCK)
    except Exception:
        pass
    t.set_color_foreground(rgba(0.90, 0.88, 0.94))
    t.set_color_background(rgba(0, 0, 0, 0.62))          # чёрный полупрозрачный
    t.set_color_cursor(rgba(0.66, 0.33, 0.97))
    t.set_scrollback_lines(20000)
    t.set_scroll_on_keystroke(True)
    t.set_audible_bell(False)
    t.set_allow_hyperlink(True)
    t.set_hexpand(True)
    t.set_vexpand(True)
    kc = Gtk.EventControllerKey()
    kc.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
 
    def pressed(_c, keyval, _code, state):
        m = state & Gtk.accelerator_get_default_mod_mask()
        if m == (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK):
            if keyval in (Gdk.KEY_C, Gdk.KEY_c):
                t.copy_clipboard_format(Vte.Format.TEXT)
                return True
            if keyval in (Gdk.KEY_V, Gdk.KEY_v):
                t.paste_clipboard()
                return True
        return False
 
    kc.connect("key-pressed", pressed)
    t.add_controller(kc)
 
 
def spawn(term, argv, on_pid=None, cwd=None):
    def cb(_t, pid, err, *_a):
        if err:
            print("spawn error:", err)
        elif on_pid:
            on_pid(pid)
 
    args = (Vte.PtyFlags.DEFAULT, cwd, argv, None, GLib.SpawnFlags.DEFAULT, None, None, -1, None, cb)
    try:
        term.spawn_async(*args)
    except TypeError:
        term.spawn_async(*args, None)
 
 
def term_feed_text(term, text):
    data = text.replace("\n", "\r\n").encode()
    try:
        term.feed(data)
    except TypeError:
        term.feed(data.decode(), -1)
 
 
def term_feed_child(term, data: bytes):
    try:
        term.feed_child(data)
    except TypeError:
        term.feed_child(data.decode(), -1)
 
 
# ════════════════════════════════════════════════════════════════════
#  ЛОГОТИП
# ════════════════════════════════════════════════════════════════════
def load_logo(height=64):
    """Картинка-логотип. Если файла нет или он битый — возвращает None."""
    try:
        if not os.path.isfile(LOGO_PATH):
            return None
        pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(LOGO_PATH, -1, height, True)
        pic = Gtk.Picture.new_for_paintable(Gdk.Texture.new_for_pixbuf(pb))
        pic.set_can_shrink(False)
        pic.set_halign(Gtk.Align.START)
        pic.set_valign(Gtk.Align.CENTER)
        return pic
    except Exception as e:  # noqa
        print("logo error:", e)
        return None
 
 
# ════════════════════════════════════════════════════════════════════
#  UI-КОМПОНЕНТЫ
# ════════════════════════════════════════════════════════════════════
def make_card():
    lb = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
    lb.add_css_class("card-list")
    return lb
 
 
def make_section(title):
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    box.append(Gtk.Label(label=title, xalign=0, css_classes=["section-title"]))
    lb = make_card()
    box.append(lb)
    return box, lb
 
 
def keycaps_box(accel):
    box = Gtk.Box(spacing=4, halign=Gtk.Align.END)
    parts = pretty_accel(accel)
    for i, p in enumerate(parts):
        if i:
            box.append(Gtk.Label(label="+", css_classes=["dim"]))
        box.append(Gtk.Label(label=p, css_classes=["keycap"]))
    return box
 
 
def page_scaffold(search_placeholder):
    """Вертикальный контейнер: поиск сверху + прокручиваемый список по центру."""
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    search = Gtk.SearchEntry(placeholder_text=search_placeholder)
    status = Gtk.Label(xalign=0, wrap=True, css_classes=["dim"])
    top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin_start=12, margin_end=12, margin_top=6)
    top.append(search)
    top.append(status)
    outer.append(Adw.Clamp(maximum_size=760, child=top))
    content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16, margin_start=12, margin_end=12,
                      margin_top=6, margin_bottom=20)
    scroll = Gtk.ScrolledWindow(vexpand=True, hscrollbar_policy=Gtk.PolicyType.NEVER)
    scroll.set_child(Adw.Clamp(maximum_size=760, child=content))
    outer.append(scroll)
    return outer, search, status, content
 
 
def make_lang_button(on_pick):
    """Кнопка выбора языка со списком и поиском."""
    cur = LANG_INDEX[CUR]
    btn = Gtk.MenuButton()
    btn.set_label("🌐 " + cur[1])
    btn.set_tooltip_text(L("Язык интерфейса", "Interface language", "界面语言"))
 
    pop = Gtk.Popover()
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin_top=8, margin_bottom=8,
                  margin_start=8, margin_end=8)
    search = Gtk.SearchEntry(placeholder_text=L("Поиск языка…", "Search language…", "搜索语言…"))
    lb = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
    for code, native, eng, _g in LANGUAGES:
        row = Gtk.ListBoxRow()
        h = Gtk.Box(spacing=10, margin_top=4, margin_bottom=4, margin_start=6, margin_end=6)
        h.append(Gtk.Label(label=native, xalign=0, hexpand=True))
        if eng != native:
            h.append(Gtk.Label(label=eng, css_classes=["dim"]))
        h.append(Gtk.Label(label="✓" if code == CUR else "  "))
        row.set_child(h)
        lb.append(row)
 
    def flt(row):
        q = search.get_text().strip().lower()
        if not q:
            return True
        code, native, eng, _g = LANGUAGES[row.get_index()]
        return q in (native + " " + eng + " " + code).lower()
 
    lb.set_filter_func(flt)
    search.connect("search-changed", lambda *_: lb.invalidate_filter())
 
    def activated(_lb, row):
        code = LANGUAGES[row.get_index()][0]
        pop.popdown()
        GLib.idle_add(lambda: (on_pick(code), False)[1])
 
    lb.connect("row-activated", activated)
    lb.set_activate_on_single_click(True)
 
    sw = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, min_content_height=360, min_content_width=320)
    sw.set_child(lb)
    box.append(search)
    box.append(sw)
    pop.set_child(box)
    btn.set_popover(pop)
    return btn, "🌐 " + cur[1]
 
 
class ShortcutsPage(Gtk.Box):
    def __init__(self, on_done=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.on_done = on_done
        self.add_css_class("opaque-bg")
        outer, self.search, self.status, self.content = page_scaffold(
            L("Поиск: действие или клавиша…", "Search: action or key…", "搜索：操作或按键…"))
        outer.set_vexpand(True)
        self.append(outer)
        self.sections = []
        self.search.connect("search-changed", self.on_search)
        self.status.set_text(L("🔍 Анализирую настройки GNOME…", "🔍 Analyzing GNOME settings…",
                               "🔍 正在分析 GNOME 设置…"))
        threading.Thread(target=self._work, daemon=True).start()
 
    def _work(self):
        try:
            res = analyze_shortcuts()
        except Exception as e:  # noqa
            res = (terminal_sections()[:1], {"schemas": 0, "count": 0, "gsettings": False})
            print("analyze error:", e)
        GLib.idle_add(self._render, *res)
 
    def _render(self, sections, stats):
        if stats["gsettings"] and stats["count"]:
            self.status.set_text(L(
                "✔ Найдено комбинаций: {count} · схем GNOME: {schemas}. "
                "Источники: dconf/gsettings, /usr/share/glib-2.0/schemas, gnome-control-center.",
                "✔ Shortcuts found: {count} · GNOME schemas: {schemas}. "
                "Sources: dconf/gsettings, /usr/share/glib-2.0/schemas, gnome-control-center.",
                "✔ 共找到 {count} 个快捷键 · GNOME 方案：{schemas} 个。"
                "来源：dconf/gsettings、/usr/share/glib-2.0/schemas、gnome-control-center。"
            ).format(count=stats["count"], schemas=stats["schemas"]))
            self.status.add_css_class("ok")
        else:
            self.status.set_text(L(
                "⚠ GNOME/gsettings не найден — показаны только универсальные комбинации.",
                "⚠ GNOME/gsettings not found — only universal shortcuts are shown.",
                "⚠ 未找到 GNOME/gsettings —— 仅显示通用快捷键。"))
            self.status.add_css_class("warn")
        for title, items in sections:
            box, lb = make_section(title)
            rows = []
            for desc, sub, accels in items:
                row = Gtk.ListBoxRow(activatable=False)
                h = Gtk.Box(spacing=12)
                left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, hexpand=True, valign=Gtk.Align.CENTER)
                left.append(Gtk.Label(label=desc, xalign=0, wrap=True))
                if sub:
                    left.append(Gtk.Label(label=sub, xalign=0, wrap=True, css_classes=["dim"]))
                right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, valign=Gtk.Align.CENTER,
                                halign=Gtk.Align.END)
                for a in accels:
                    right.append(keycaps_box(a))
                h.append(left)
                h.append(right)
                row.set_child(h)
                lb.append(row)
                text = (desc + " " + sub + " " + " ".join(" ".join(pretty_accel(a)) for a in accels)).lower()
                rows.append((row, text))
            self.content.append(box)
            self.sections.append((box, rows))
        if self.on_done:
            try:
                self.on_done()
            except Exception as e:  # noqa
                print("on_done error:", e)
        return False
 
    def on_search(self, entry):
        q = entry.get_text().strip().lower()
        for box, rows in self.sections:
            any_vis = False
            for row, text in rows:
                vis = q in text
                row.set_visible(vis)
                any_vis |= vis
            box.set_visible(any_vis)
 
 
class CommandsPage(Gtk.Box):
    def __init__(self, on_run):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.add_css_class("opaque-bg")
        outer, self.search, status, self.content = page_scaffold(
            L("Поиск команды или описания…", "Search command or description…", "搜索命令或描述…"))
        status.set_text(L(
            "Нажмите «Выполнить» — вы сможете отредактировать команду и выбрать: система или песочница.",
            "Press “Run” — you can edit the command and choose: system or sandbox.",
            "点击“执行”——你可以先编辑命令，再选择在系统还是沙盒中运行。"))
        outer.set_vexpand(True)
        self.append(outer)
        self.sections = []
        cats = {}
        for cat, cmd, desc, danger in COMMANDS:
            cats.setdefault(cat, []).append((cmd, desc, danger))
        for cat, items in cats.items():
            box, lb = make_section(T(cat))
            rows = []
            for cmd, desc, danger in items:
                tcmd = tr_cmd(cmd)
                tdesc = tr_desc(cmd, desc)
                row = Gtk.ListBoxRow(activatable=False)
                h = Gtk.Box(spacing=12)
                left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3, hexpand=True)
                left.append(Gtk.Label(label=tcmd, xalign=0, wrap=True, selectable=True, css_classes=["cmd"]))
                left.append(Gtk.Label(label=tdesc, xalign=0, wrap=True, css_classes=["dim"]))
                btn = Gtk.Button(label=L("▶ Выполнить", "▶ Run", "▶ 执行"), valign=Gtk.Align.CENTER,
                                 css_classes=["accent-btn"])
                btn.connect("clicked", lambda _b, c=tcmd, d=tdesc, dg=danger: on_run(c, d, dg))
                h.append(left)
                h.append(btn)
                row.set_child(h)
                lb.append(row)
                rows.append((row, (tcmd + " " + tdesc).lower()))
            self.content.append(box)
            self.sections.append((box, rows))
        self.search.connect("search-changed", self.on_search)
 
    def on_search(self, entry):
        q = entry.get_text().strip().lower()
        for box, rows in self.sections:
            any_vis = False
            for row, text in rows:
                vis = q in text
                row.set_visible(vis)
                any_vis |= vis
            box.set_visible(any_vis)
 
 
class JournalPage(Gtk.Box):
    def __init__(self, entries):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin_start=0, margin_end=0, margin_top=0)
        self.add_css_class("opaque-bg")
        self.entries = entries          # общий список: (время, "sandbox"/"system", команда)
        self.empty = Gtk.Label(
            label=L("Пока пусто. Запущенные команды появятся здесь.",
                    "Nothing here yet. Commands you run will appear here.",
                    "暂无内容。运行过的命令会显示在这里。"),
            css_classes=["dim"], vexpand=True)
        self.lb = make_card()
        self.lb.set_visible(False)
        scroll = Gtk.ScrolledWindow(vexpand=True, hscrollbar_policy=Gtk.PolicyType.NEVER)
        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin_bottom=16,
                        margin_start=12, margin_end=12)
        inner.append(self.lb)
        scroll.set_child(Adw.Clamp(maximum_size=760, child=inner))
        clear = Gtk.Button(label=L("Очистить журнал", "Clear journal", "清空日志"),
                           css_classes=["ghost-btn"], halign=Gtk.Align.END,
                           margin_start=12, margin_end=12, margin_top=6)
        clear.connect("clicked", self.clear)
        self.append(Adw.Clamp(maximum_size=760, child=clear))
        self.append(self.empty)
        self.append(scroll)
        for e in self.entries:
            self._add_row(*e)
 
    def _add_row(self, ts, kind, cmd):
        self.empty.set_visible(False)
        self.lb.set_visible(True)
        where = (L("песочница", "sandbox", "沙盒") if kind == "sandbox"
                 else L("система", "system", "系统"))
        row = Gtk.ListBoxRow(activatable=False)
        h = Gtk.Box(spacing=10)
        h.append(Gtk.Label(label=ts, css_classes=["dim"]))
        h.append(Gtk.Label(label=where, css_classes=["keycap"]))
        h.append(Gtk.Label(label=cmd, xalign=0, hexpand=True, wrap=True, selectable=True, css_classes=["cmd"]))
        row.set_child(h)
        self.lb.prepend(row)
 
    def add(self, kind, cmd):
        ts = time.strftime("%H:%M:%S")
        self.entries.append((ts, kind, cmd))
        self._add_row(ts, kind, cmd)
 
    def clear(self, *_):
        self.entries.clear()
        while (r := self.lb.get_first_child()):
            self.lb.remove(r)
        self.lb.set_visible(False)
        self.empty.set_visible(True)
 
 
class SandboxPage(Gtk.Box):
    """Страница НЕ закрашена: сквозь терминал виден рабочий стол.
    Полоса статуса сверху и подсказка снизу закрашены непрозрачно."""
 
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.engine = None
        self.started = False
        self.ready = False
        self.alive = False
        self.suppress_exit = False
        self.pending = []
        self.pid = None
 
        bar = Gtk.Box(spacing=8, css_classes=["opaque-bg", "pad-bar"])
        self.status = Gtk.Label(xalign=0, hexpand=True, wrap=True, css_classes=["dim"],
                                label=L("Песочница запустится при открытии вкладки.",
                                        "The sandbox will start when you open this tab.",
                                        "打开此标签页时将启动沙盒。"))
        restart = Gtk.Button(label=L("↻ Новая сессия", "↻ New session", "↻ 新会话"), css_classes=["ghost-btn"])
        restart.connect("clicked", lambda *_: self.restart())
        bar.append(self.status)
        bar.append(restart)
        self.append(bar)
 
        self.term = Vte.Terminal()
        style_terminal(self.term)
        self.term.connect("window-title-changed", self.on_title)
        self.term.connect("child-exited", self.on_exit)
        frame = Gtk.ScrolledWindow(vexpand=True, css_classes=["terminal-frame"])
        frame.set_child(self.term)
        self.append(frame)
 
        self.append(Gtk.Label(
            xalign=0, wrap=True, css_classes=["dim", "opaque-bg", "pad-bar"],
            label=L("Копировать/вставить: Ctrl+Shift+C / Ctrl+Shift+V. Это изолированная среда — "
                    "системные службы (systemctl, ufw) и реальные диски здесь не работают.",
                    "Copy/paste: Ctrl+Shift+C / Ctrl+Shift+V. This is an isolated environment — "
                    "system services (systemctl, ufw) and real disks do not work here.",
                    "复制/粘贴：Ctrl+Shift+C / Ctrl+Shift+V。这是隔离环境——"
                    "系统服务（systemctl、ufw）和真实磁盘在这里无法使用。")))
 
    # --- запуск
    def start(self):
        if self.started:
            return
        self.started = True
        self.ready = False
        self.status.set_text(L("⏳ Подготавливаю песочницу…", "⏳ Preparing the sandbox…", "⏳ 正在准备沙盒…"))
        threading.Thread(target=self._detect, daemon=True).start()
 
    def _detect(self):
        try:
            ctx, image = prepare_files()
            eng = detect_engine()
        except Exception as e:  # noqa
            ctx, image, eng = None, None, None
            print(e)
        GLib.idle_add(self._spawn, eng, ctx, image)
 
    def _spawn(self, eng, ctx, image):
        self.engine = eng
        apply_env_messages()
        if eng is None:
            self.status.set_text(L("❌ Нет podman / docker / bubblewrap.",
                                   "❌ No podman / docker / bubblewrap found.",
                                   "❌ 未找到 podman / docker / bubblewrap。"))
            cmds = ("\n\n  sudo apt install podman            "
                    + L("(лучший вариант, полноценный Ubuntu)", "(best option, a full Ubuntu)",
                        "（最佳选择，完整的 Ubuntu）")
                    + "\n  sudo apt install bubblewrap zsh zsh-autosuggestions zsh-syntax-highlighting\n\n")
            term_feed_text(self.term,
                           L("Для песочницы установите один из движков:",
                             "To use the sandbox, install one of the engines:",
                             "要使用沙盒，请安装以下任一引擎：")
                           + cmds
                           + L("и нажмите «Новая сессия».", "and press “New session”.", "然后点击“新会话”。")
                           + "\n")
            return False
        if eng == "bwrap":
            argv, use_zsh = bwrap_argv()
            self.status.set_text(
                L("🧪 Режим bubblewrap (лёгкая изоляция, без apt install)",
                  "🧪 bubblewrap mode (light isolation, no apt install)",
                  "🧪 bubblewrap 模式（轻量隔离，无需 apt install）")
                + ("" if use_zsh else L(" · zsh не найден, используется bash",
                                        " · zsh not found, using bash",
                                        " · 未找到 zsh，使用 bash")))
        else:
            msg1 = L("⏳ Первый запуск: собираю образ песочницы (нужен интернет, 2–6 минут)…",
                     "⏳ First run: building the sandbox image (internet required, 2–6 minutes)…",
                     "⏳ 首次运行：正在构建沙盒镜像（需要联网，约 2–6 分钟）…")
            msg2 = L("❌ Не удалось собрать образ.", "❌ Failed to build the image.", "❌ 镜像构建失败。")
            msg3 = L("Нажмите любую клавишу…", "Press any key…", "按任意键继续…")
            argv = ["bash", "-c", BOOT_SCRIPT, "easyhelper", eng, image, str(ctx), CONTAINER, msg1, msg2, msg3]
            self.status.set_text(L(
                "🧪 Контейнер Ubuntu 24.04 через {eng} · изменения исчезают после сессии",
                "🧪 Ubuntu 24.04 container via {eng} · changes disappear after the session",
                "🧪 通过 {eng} 运行的 Ubuntu 24.04 容器 · 会话结束后更改将消失").format(eng=eng))
        self.alive = True
        spawn(self.term, argv, on_pid=lambda p: setattr(self, "pid", p))
        return False
 
    def restart(self):
        if self.alive and self.pid:
            self.suppress_exit = True
            try:
                os.kill(self.pid, signal.SIGHUP)
            except Exception:
                self.suppress_exit = False
        self.term.reset(True, True)
        self.started = False
        self.pending.clear()
        self.start()
 
    def shutdown(self):
        if self.engine in ("podman", "docker"):
            subprocess.Popen([self.engine, "rm", "-f", CONTAINER], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
 
    # --- события
    def on_title(self, term):
        title = term.get_window_title() or ""
        if title.startswith("sandbox") and not self.ready:
            self.ready = True
            self.status.set_text(self.status.get_text().replace("⏳", "✔"))
            data, self.pending = self.pending, []
            for d in data:
                GLib.timeout_add(300, lambda d=d: (term_feed_child(self.term, d), False)[1])
 
    def on_exit(self, *_):
        self.alive = False
        if self.suppress_exit:
            self.suppress_exit = False
            return
        self.ready = False
        self.started = False
        term_feed_text(self.term, L("\n[Сессия завершена — нажмите «↻ Новая сессия»]\n",
                                    "\n[Session ended — press “↻ New session”]\n",
                                    "\n[会话已结束——请点击“↻ 新会话”]\n"))
 
    def send(self, cmd):
        self.start()
        data = (cmd + "\n").encode()
        if self.ready:
            term_feed_child(self.term, data)
        else:
            self.pending.append(data)
        self.term.grab_focus()
 
 
# ════════════════════════════════════════════════════════════════════
#  ДИАЛОГ «ВЫПОЛНИТЬ» и СИСТЕМНЫЙ ЗАПУСК
# ════════════════════════════════════════════════════════════════════
class RunDialog(Gtk.Window):
    def __init__(self, parent, cmd, desc, danger, on_choice):
        super().__init__(transient_for=parent, modal=True,
                         title=L("Выполнить команду", "Run command", "执行命令"),
                         default_width=560, resizable=False)
        self.add_css_class("opaque-bg")        # диалог — непрозрачный
        self.on_choice = on_choice
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin_top=20, margin_bottom=20,
                      margin_start=22, margin_end=22)
        box.append(Gtk.Label(label=L("Где выполнить команду?", "Where to run the command?", "在哪里执行该命令？"),
                             xalign=0, css_classes=["section-title"]))
        box.append(Gtk.Label(label=desc, xalign=0, wrap=True, css_classes=["dim"]))
        self.entry = Gtk.Entry(text=cmd, css_classes=["cmd-entry"])
        self.entry.connect("activate", lambda *_: self.choose("sandbox"))
        box.append(self.entry)
        self.msg = Gtk.Label(xalign=0, wrap=True)
        if "<" in cmd:
            self.msg.set_text(L("✏ Замените части в <угловых скобках> на своё значение.",
                                "✏ Replace the parts in <angle brackets> with your own value.",
                                "✏ 请将 <尖括号> 中的部分替换为你自己的值。"))
            self.msg.add_css_class("dim")
        box.append(self.msg)
        if danger:
            box.append(Gtk.Label(
                label=L("⚠ Опасная команда! В системе она может безвозвратно удалить данные "
                        "или выключить компьютер. Для проб лучше песочница.",
                        "⚠ Dangerous command! On the real system it can irreversibly delete data "
                        "or shut the computer down. For experiments, use the sandbox.",
                        "⚠ 危险命令！在真实系统中它可能永久删除数据或关闭计算机。试验时建议使用沙盒。"),
                xalign=0, wrap=True, css_classes=["warn"]))
        btns = Gtk.Box(spacing=8, halign=Gtk.Align.END, margin_top=6)
        cancel = Gtk.Button(label=L("Отмена", "Cancel", "取消"), css_classes=["ghost-btn"])
        cancel.connect("clicked", lambda *_: self.close())
        sb = Gtk.Button(label=L("🧪 В песочнице", "🧪 In sandbox", "🧪 在沙盒中"), css_classes=["accent-btn"])
        sb.connect("clicked", lambda *_: self.choose("sandbox"))
        sy = Gtk.Button(label=L("🖥 В системе", "🖥 On system", "🖥 在系统中"),
                        css_classes=["danger-btn" if danger else "ghost-btn"])
        sy.connect("clicked", lambda *_: self.choose("system"))
        for b in (cancel, sy, sb):
            btns.append(b)
        box.append(btns)
        self.set_child(box)
        ctl = Gtk.EventControllerKey()
        ctl.connect("key-pressed", lambda _c, kv, *_: (self.close(), True)[1] if kv == Gdk.KEY_Escape else False)
        self.add_controller(ctl)
 
    def choose(self, target):
        cmd = self.entry.get_text().strip()
        if not cmd:
            return
        if re.search(r"<[^<>]+>", cmd):
            self.msg.set_text(L("⚠ Сначала замените <поля в скобках> на реальные значения.",
                                "⚠ First replace the <bracketed fields> with real values.",
                                "⚠ 请先将 <括号中的字段> 替换为实际值。"))
            self.msg.remove_css_class("dim")
            self.msg.add_css_class("warn")
            return
        self.close()
        self.on_choice(target, cmd)
 
 
class SystemRunWindow(Gtk.Window):
    """Окно с обычным терминалом — тоже полупрозрачное."""
 
    def __init__(self, parent, cmd):
        super().__init__(transient_for=parent,
                         title=L("Система — {cmd}", "System — {cmd}", "系统 — {cmd}").format(cmd=cmd),
                         default_width=840, default_height=460)
        t = Vte.Terminal()
        style_terminal(t)
        t.connect("child-exited", lambda *_: self.close())
        sw = Gtk.ScrolledWindow()
        sw.set_child(t)
        self.set_child(sw)
        script = ('eval "$1"; rc=$?; echo; echo "${2}${rc}${3}"; '
                  'read -rsn1 -p "$4"')
        done_a = L("── Завершено (код ", "── Finished (exit code ", "── 已完成（退出码 ")
        done_b = L(") ──", ") ──", "）──")
        press = L("Нажмите любую клавишу, чтобы закрыть…", "Press any key to close…", "按任意键关闭…")
        spawn(t, ["bash", "-c", script, "easyhelper", cmd, done_a, done_b, press], cwd=GLib.get_home_dir())
 
 
# ════════════════════════════════════════════════════════════════════
#  ГЛАВНОЕ ОКНО
# ════════════════════════════════════════════════════════════════════
class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app, page=None, size=(900, 800)):
        super().__init__(application=app, title="EasyHelper", default_width=size[0], default_height=size[1])
        self.app = app
        self.journal = JournalPage(app.journal_entries)
        self.sandbox = SandboxPage()
        self.shortcuts = ShortcutsPage(on_done=app.on_ui_ready)
        self.commands = CommandsPage(self.request_run)
 
        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE, vexpand=True)
        self.stack.add_titled(self.shortcuts, "keys", L("⌨ Горячие клавиши", "⌨ Shortcuts", "⌨ 快捷键"))
        self.stack.add_titled(self.commands, "cmds", L("📦 Команды", "📦 Commands", "📦 命令"))
        self.stack.add_titled(self.sandbox, "sandbox", L("🧪 Песочница", "🧪 Sandbox", "🧪 沙盒"))
        self.stack.add_titled(self.journal, "journal", L("📜 Журнал", "📜 Journal", "📜 日志"))
        self.stack.connect("notify::visible-child-name", self.on_page)
 
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.StackSwitcher(stack=self.stack))
        self.lang_btn, self._lang_label = make_lang_button(app.set_language)
        header.pack_end(self.lang_btn)
 
        # ── заголовок приложения: логотип + название + описание
        title_row = Gtk.Box(spacing=14)
        logo = load_logo(64)
        if logo:
            title_row.append(logo)
        title_row.append(Gtk.Label(label="EasyHelper", xalign=0, valign=Gtk.Align.CENTER,
                                   css_classes=["app-title"]))
 
        head = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin_top=14, margin_bottom=10,
                       margin_start=20, margin_end=20)
        head.append(title_row)
        head.append(Gtk.Label(
            xalign=0, wrap=True, css_classes=["app-sub"],
            label=L("Помощник для новичков в PixiumOS. Показывает полезные горячие клавиши вашей системы, "
                    "объясняет популярные команды простыми словами и даёт безопасную песочницу-терминал, "
                    "где можно пробовать что угодно.",
                    "A helper for newcomers to PixiumOS. Shows useful keyboard shortcuts of your system, "
                    "explains popular commands in plain words, and provides a safe sandbox terminal "
                    "where you can try anything.",
                    "PixiumOS 新手助手。展示你系统中实用的键盘快捷键，用通俗易懂的语言讲解常用命令，"
                    "并提供一个安全的沙盒终端，你可以在里面随意尝试。")))
 
        head_wrap = Gtk.Box(css_classes=["opaque-bg"])
        head_wrap.append(Adw.Clamp(maximum_size=760, child=head, hexpand=True))
 
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.append(header)
        root.append(head_wrap)
        root.append(self.stack)
        self.toasts = Adw.ToastOverlay()
        self.toasts.set_child(root)
        self.set_content(self.toasts)
        self.connect("close-request", self.on_close)
        if page and page != "keys":
            self.stack.set_visible_child_name(page)
 
    def set_busy(self, busy, pct=None):
        suffix = ""
        if busy:
            suffix = f" ⏳ {pct}%" if pct is not None else " ⏳"
        self.lang_btn.set_label(self._lang_label + suffix)
 
    def toast(self, text):
        self.toasts.add_toast(Adw.Toast.new(text))
 
    def on_page(self, *_):
        if self.stack.get_visible_child_name() == "sandbox":
            self.sandbox.start()
 
    def on_close(self, *_):
        self.sandbox.shutdown()
        return False
 
    def request_run(self, cmd, desc, danger):
        RunDialog(self, cmd, desc, danger, self.do_run).present()
 
    def do_run(self, target, cmd):
        if target == "sandbox":
            self.journal.add("sandbox", cmd)
            self.stack.set_visible_child_name("sandbox")
            self.sandbox.send(cmd)
        else:
            self.journal.add("system", cmd)
            SystemRunWindow(self, cmd).present()
 
 
class App(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID)
        self._css_ready = False
        self._prov = None
        self.main_win = None
        self.journal_entries = []
 
    def _apply_css(self, *_):
        sm = Adw.StyleManager.get_default()
        css = CSS_DARK if sm.get_dark() else CSS_LIGHT
        if hasattr(self._prov, "load_from_string"):
            self._prov.load_from_string(css)
        else:
            self._prov.load_from_data(css.encode())
 
    def make_window(self, page=None, size=(900, 800)):
        win = MainWindow(self, page, size)
        self.main_win = win
        return win
 
    # ── смена языка (мгновенно, всё встроено, интернет не нужен)
    def set_language(self, code):
        if code not in LANG_INDEX or code == CUR:
            return
        set_lang(code)
        save_lang(code)
        apply_direction()
        self.rebuild()
 
    def rebuild(self):
        old = self.main_win
        page, size = None, (900, 800)
        if old is not None:
            page = old.stack.get_visible_child_name()
            if page == "sandbox":       # сессия песочницы всё равно будет закрыта
                page = "keys"
            w, h = old.get_width(), old.get_height()
            if w > 0 and h > 0:
                size = (w, h)
        win = self.make_window(page, size)
        win.present()
        if old is not None:
            old.close()
 
    def on_ui_ready(self):
        """Интерфейс построен. Переводы встроены, догружать ничего не нужно."""
        return None
 
    def do_activate(self):
        apply_direction()
        if not self._css_ready:
            self._css_ready = True
            sm = Adw.StyleManager.get_default()
            # тема приложения = тема системы (светлая/тёмная), без принудительной тёмной
            sm.set_color_scheme(Adw.ColorScheme.DEFAULT)
            self._prov = Gtk.CssProvider()
            self._apply_css()
            Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), self._prov,
                                                      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            sm.connect("notify::dark", self._apply_css)
        win = self.props.active_window or self.make_window()
        win.present()
 
 
# ════════════════════════════════════════════════════════════════════
#  ОФЛАЙН-ПЕРЕВОДЫ (встроены в файл)
#  Порядок колонок: English, uk, fr, es, pt, de, fi, id, hi, ko, tr, ja
# ════════════════════════════════════════════════════════════════════
_SRC = "dconf/gsettings, /usr/share/glib-2.0/schemas, gnome-control-center."
 
# ── Интерфейс (строки из L(...))
reg_rows([
    ("Interface language", "Мова інтерфейсу", "Langue de l’interface", "Idioma de la interfaz",
     "Idioma da interface", "Sprache der Oberfläche", "Käyttöliittymän kieli", "Bahasa antarmuka",
     "इंटरफ़ेस की भाषा", "인터페이스 언어", "Arayüz dili", "インターフェースの言語"),
    ("Search language…", "Пошук мови…", "Rechercher une langue…", "Buscar idioma…", "Pesquisar idioma…",
     "Sprache suchen…", "Hae kieltä…", "Cari bahasa…", "भाषा खोजें…", "언어 검색…", "Dil ara…", "言語を検索…"),
    ("Search: action or key…", "Пошук: дія або клавіша…", "Recherche : action ou touche…",
     "Buscar: acción o tecla…", "Pesquisar: ação ou tecla…", "Suche: Aktion oder Taste…",
     "Haku: toiminto tai näppäin…", "Cari: aksi atau tombol…", "खोजें: क्रिया या कुंजी…",
     "검색: 동작 또는 키…", "Ara: eylem veya tuş…", "検索：操作またはキー…"),
    ("🔍 Analyzing GNOME settings…", "🔍 Аналізую налаштування GNOME…", "🔍 Analyse des paramètres GNOME…",
     "🔍 Analizando la configuración de GNOME…", "🔍 Analisando as configurações do GNOME…",
     "🔍 GNOME-Einstellungen werden analysiert…", "🔍 Analysoidaan GNOMEn asetuksia…",
     "🔍 Menganalisis pengaturan GNOME…", "🔍 GNOME सेटिंग्स का विश्लेषण हो रहा है…",
     "🔍 GNOME 설정을 분석하는 중…", "🔍 GNOME ayarları çözümleniyor…", "🔍 GNOME の設定を分析中…"),
    ("✔ Shortcuts found: {count} · GNOME schemas: {schemas}. Sources: " + _SRC,
     "✔ Знайдено комбінацій: {count} · схем GNOME: {schemas}. Джерела: " + _SRC,
     "✔ Raccourcis trouvés : {count} · schémas GNOME : {schemas}. Sources : " + _SRC,
     "✔ Atajos encontrados: {count} · esquemas de GNOME: {schemas}. Fuentes: " + _SRC,
     "✔ Atalhos encontrados: {count} · esquemas do GNOME: {schemas}. Fontes: " + _SRC,
     "✔ Gefundene Tastenkürzel: {count} · GNOME-Schemas: {schemas}. Quellen: " + _SRC,
     "✔ Pikanäppäimiä löytyi: {count} · GNOME-skeemoja: {schemas}. Lähteet: " + _SRC,
     "✔ Pintasan ditemukan: {count} · skema GNOME: {schemas}. Sumber: " + _SRC,
     "✔ मिले शॉर्टकट: {count} · GNOME स्कीमा: {schemas}। स्रोत: " + _SRC,
     "✔ 발견된 단축키: {count}개 · GNOME 스키마: {schemas}개. 출처: " + _SRC,
     "✔ Bulunan kısayollar: {count} · GNOME şemaları: {schemas}. Kaynaklar: " + _SRC,
     "✔ 見つかったショートカット：{count} 件 · GNOME スキーマ：{schemas} 件。情報源：" + _SRC),
    ("⚠ GNOME/gsettings not found — only universal shortcuts are shown.",
     "⚠ GNOME/gsettings не знайдено — показано лише універсальні комбінації.",
     "⚠ GNOME/gsettings introuvable — seuls les raccourcis universels sont affichés.",
     "⚠ No se encontró GNOME/gsettings: solo se muestran los atajos universales.",
     "⚠ GNOME/gsettings não encontrado — apenas os atalhos universais são mostrados.",
     "⚠ GNOME/gsettings nicht gefunden – es werden nur allgemeine Tastenkürzel angezeigt.",
     "⚠ GNOME/gsettings ei löytynyt — näytetään vain yleiset pikanäppäimet.",
     "⚠ GNOME/gsettings tidak ditemukan — hanya pintasan umum yang ditampilkan.",
     "⚠ GNOME/gsettings नहीं मिला — केवल सामान्य शॉर्टकट दिखाए गए हैं।",
     "⚠ GNOME/gsettings를 찾을 수 없습니다 — 범용 단축키만 표시됩니다.",
     "⚠ GNOME/gsettings bulunamadı — yalnızca genel kısayollar gösteriliyor.",
     "⚠ GNOME/gsettings が見つかりません — 汎用のショートカットのみ表示しています。"),
    ("Search command or description…", "Пошук команди або опису…", "Rechercher une commande ou une description…",
     "Buscar comando o descripción…", "Pesquisar comando ou descrição…", "Befehl oder Beschreibung suchen…",
     "Hae komentoa tai kuvausta…", "Cari perintah atau deskripsi…", "कमांड या विवरण खोजें…",
     "명령어 또는 설명 검색…", "Komut veya açıklama ara…", "コマンドまたは説明を検索…"),
    ("Press “Run” — you can edit the command and choose: system or sandbox.",
     "Натисніть «Виконати» — ви зможете відредагувати команду та вибрати: система чи пісочниця.",
     "Appuyez sur « Exécuter » — vous pourrez modifier la commande et choisir : système ou bac à sable.",
     "Pulsa «Ejecutar»: podrás editar el comando y elegir: sistema o sandbox.",
     "Clique em «Executar» — você poderá editar o comando e escolher: sistema ou sandbox.",
     "Klicken Sie auf „Ausführen“ – Sie können den Befehl bearbeiten und wählen: System oder Sandbox.",
     "Paina ”Suorita” — voit muokata komentoa ja valita: järjestelmä tai hiekkalaatikko.",
     "Tekan “Jalankan” — Anda dapat mengedit perintah dan memilih: sistem atau sandbox.",
     "“चलाएँ” दबाएँ — आप कमांड बदल सकते हैं और चुन सकते हैं: सिस्टम या सैंडबॉक्स।",
     "“실행”을 누르세요 — 명령어를 수정한 뒤 시스템 또는 샌드박스 중에서 선택할 수 있습니다.",
     "“Çalıştır”a basın — komutu düzenleyebilir ve sistem veya korumalı alan arasında seçim yapabilirsiniz.",
     "「実行」を押すと、コマンドを編集して、システムかサンドボックスかを選べます。"),
    ("▶ Run", "▶ Виконати", "▶ Exécuter", "▶ Ejecutar", "▶ Executar", "▶ Ausführen", "▶ Suorita",
     "▶ Jalankan", "▶ चलाएँ", "▶ 실행", "▶ Çalıştır", "▶ 実行"),
    ("Nothing here yet. Commands you run will appear here.",
     "Поки що порожньо. Тут з’являтимуться виконані вами команди.",
     "Rien pour l’instant. Les commandes que vous exécutez apparaîtront ici.",
     "Todavía no hay nada. Los comandos que ejecutes aparecerán aquí.",
     "Nada aqui ainda. Os comandos que você executar aparecerão aqui.",
     "Noch nichts vorhanden. Ausgeführte Befehle erscheinen hier.",
     "Täällä ei ole vielä mitään. Suorittamasi komennot näkyvät tässä.",
     "Belum ada apa pun. Perintah yang Anda jalankan akan muncul di sini.",
     "अभी यहाँ कुछ नहीं है। आपके चलाए गए कमांड यहाँ दिखाई देंगे।",
     "아직 비어 있습니다. 실행한 명령어가 여기에 표시됩니다.",
     "Henüz burada bir şey yok. Çalıştırdığınız komutlar burada görünecek.",
     "まだ何もありません。実行したコマンドがここに表示されます。"),
    ("Clear journal", "Очистити журнал", "Effacer le journal", "Borrar historial", "Limpar diário",
     "Protokoll leeren", "Tyhjennä loki", "Hapus jurnal", "जर्नल साफ़ करें", "기록 지우기",
     "Günlüğü temizle", "ログを消去"),
    ("sandbox", "пісочниця", "bac à sable", "sandbox", "sandbox", "Sandbox", "hiekkalaatikko", "sandbox",
     "सैंडबॉक्स", "샌드박스", "korumalı alan", "サンドボックス"),
    ("system", "система", "système", "sistema", "sistema", "System", "järjestelmä", "sistem",
     "सिस्टम", "시스템", "sistem", "システム"),
    ("The sandbox will start when you open this tab.",
     "Пісочниця запуститься під час відкриття вкладки.",
     "Le bac à sable démarrera à l’ouverture de cet onglet.",
     "El sandbox se iniciará al abrir esta pestaña.",
     "O sandbox será iniciado ao abrir esta aba.",
     "Die Sandbox startet, sobald Sie diesen Tab öffnen.",
     "Hiekkalaatikko käynnistyy, kun avaat tämän välilehden.",
     "Sandbox akan dimulai saat Anda membuka tab ini.",
     "इस टैब को खोलने पर सैंडबॉक्स शुरू हो जाएगा।",
     "이 탭을 열면 샌드박스가 시작됩니다.",
     "Bu sekmeyi açtığınızda korumalı alan başlayacak.",
     "このタブを開くとサンドボックスが起動します。"),
    ("↻ New session", "↻ Нова сесія", "↻ Nouvelle session", "↻ Nueva sesión", "↻ Nova sessão",
     "↻ Neue Sitzung", "↻ Uusi istunto", "↻ Sesi baru", "↻ नया सत्र", "↻ 새 세션", "↻ Yeni oturum",
     "↻ 新しいセッション"),
    ("Copy/paste: Ctrl+Shift+C / Ctrl+Shift+V. This is an isolated environment — "
     "system services (systemctl, ufw) and real disks do not work here.",
     "Копіювати/вставити: Ctrl+Shift+C / Ctrl+Shift+V. Це ізольоване середовище — "
     "системні служби (systemctl, ufw) і реальні диски тут не працюють.",
     "Copier/coller : Ctrl+Shift+C / Ctrl+Shift+V. Il s’agit d’un environnement isolé : "
     "les services système (systemctl, ufw) et les vrais disques n’y fonctionnent pas.",
     "Copiar/pegar: Ctrl+Shift+C / Ctrl+Shift+V. Es un entorno aislado: "
     "los servicios del sistema (systemctl, ufw) y los discos reales no funcionan aquí.",
     "Copiar/colar: Ctrl+Shift+C / Ctrl+Shift+V. Este é um ambiente isolado: "
     "os serviços do sistema (systemctl, ufw) e os discos reais não funcionam aqui.",
     "Kopieren/Einfügen: Strg+Umschalt+C / Strg+Umschalt+V. Dies ist eine isolierte Umgebung – "
     "Systemdienste (systemctl, ufw) und echte Laufwerke funktionieren hier nicht.",
     "Kopioi/liitä: Ctrl+Shift+C / Ctrl+Shift+V. Tämä on eristetty ympäristö — "
     "järjestelmäpalvelut (systemctl, ufw) ja todelliset levyt eivät toimi täällä.",
     "Salin/tempel: Ctrl+Shift+C / Ctrl+Shift+V. Ini adalah lingkungan terisolasi — "
     "layanan sistem (systemctl, ufw) dan disk asli tidak berfungsi di sini.",
     "कॉपी/पेस्ट: Ctrl+Shift+C / Ctrl+Shift+V। यह एक अलग-थलग वातावरण है — "
     "सिस्टम सेवाएँ (systemctl, ufw) और असली डिस्क यहाँ काम नहीं करते।",
     "복사/붙여넣기: Ctrl+Shift+C / Ctrl+Shift+V. 이곳은 격리된 환경이라 "
     "시스템 서비스(systemctl, ufw)와 실제 디스크는 작동하지 않습니다.",
     "Kopyala/yapıştır: Ctrl+Shift+C / Ctrl+Shift+V. Bu yalıtılmış bir ortamdır — "
     "sistem hizmetleri (systemctl, ufw) ve gerçek diskler burada çalışmaz.",
     "コピー/貼り付け：Ctrl+Shift+C / Ctrl+Shift+V。ここは隔離された環境のため、"
     "システムサービス（systemctl、ufw）や実際のディスクは動作しません。"),
    ("⏳ Preparing the sandbox…", "⏳ Готую пісочницю…", "⏳ Préparation du bac à sable…",
     "⏳ Preparando el sandbox…", "⏳ Preparando o sandbox…", "⏳ Sandbox wird vorbereitet…",
     "⏳ Valmistellaan hiekkalaatikkoa…", "⏳ Menyiapkan sandbox…", "⏳ सैंडबॉक्स तैयार किया जा रहा है…",
     "⏳ 샌드박스를 준비하는 중…", "⏳ Korumalı alan hazırlanıyor…", "⏳ サンドボックスを準備中…"),
    ("❌ No podman / docker / bubblewrap found.", "❌ Не знайдено podman / docker / bubblewrap.",
     "❌ Aucun podman / docker / bubblewrap trouvé.", "❌ No se encontró podman / docker / bubblewrap.",
     "❌ Nenhum podman / docker / bubblewrap encontrado.", "❌ Weder podman noch docker noch bubblewrap gefunden.",
     "❌ Podmania / dockeria / bubblewrapia ei löytynyt.", "❌ podman / docker / bubblewrap tidak ditemukan.",
     "❌ podman / docker / bubblewrap नहीं मिला।", "❌ podman / docker / bubblewrap을 찾을 수 없습니다.",
     "❌ podman / docker / bubblewrap bulunamadı.", "❌ podman / docker / bubblewrap が見つかりません。"),
    ("(best option, a full Ubuntu)", "(найкращий варіант, повноцінна Ubuntu)",
     "(meilleure option, un Ubuntu complet)", "(la mejor opción, un Ubuntu completo)",
     "(melhor opção, um Ubuntu completo)", "(beste Option, ein vollständiges Ubuntu)",
     "(paras vaihtoehto, täysi Ubuntu)", "(pilihan terbaik, Ubuntu lengkap)",
     "(सबसे अच्छा विकल्प, पूरा Ubuntu)", "(가장 좋은 선택, 완전한 Ubuntu)",
     "(en iyi seçenek, tam bir Ubuntu)", "（最良の選択肢、完全な Ubuntu）"),
    ("To use the sandbox, install one of the engines:", "Для пісочниці встановіть один із рушіїв:",
     "Pour utiliser le bac à sable, installez l’un des moteurs :",
     "Para usar el sandbox, instala uno de los motores:",
     "Para usar o sandbox, instale um dos motores:",
     "Um die Sandbox zu nutzen, installieren Sie eine der Engines:",
     "Hiekkalaatikon käyttämiseksi asenna jokin moottoreista:",
     "Untuk menggunakan sandbox, pasang salah satu mesin berikut:",
     "सैंडबॉक्स इस्तेमाल करने के लिए इनमें से कोई एक इंजन इंस्टॉल करें:",
     "샌드박스를 사용하려면 다음 엔진 중 하나를 설치하세요:",
     "Korumalı alanı kullanmak için motorlardan birini kurun:",
     "サンドボックスを使うには、次のいずれかのエンジンをインストールしてください："),
    ("and press “New session”.", "і натисніть «Нова сесія».", "puis appuyez sur « Nouvelle session ».",
     "y pulsa «Nueva sesión».", "e clique em «Nova sessão».", "und klicken Sie auf „Neue Sitzung“.",
     "ja paina ”Uusi istunto”.", "lalu tekan “Sesi baru”.", "और “नया सत्र” दबाएँ।",
     "그런 다음 “새 세션”을 누르세요.", "ve “Yeni oturum”a basın.", "その後「新しいセッション」を押してください。"),
    ("🧪 bubblewrap mode (light isolation, no apt install)",
     "🧪 Режим bubblewrap (легка ізоляція, без apt install)",
     "🧪 Mode bubblewrap (isolation légère, sans apt install)",
     "🧪 Modo bubblewrap (aislamiento ligero, sin apt install)",
     "🧪 Modo bubblewrap (isolamento leve, sem apt install)",
     "🧪 bubblewrap-Modus (leichte Isolierung, ohne apt install)",
     "🧪 bubblewrap-tila (kevyt eristys, ei apt install -asennusta)",
     "🧪 Mode bubblewrap (isolasi ringan, tanpa apt install)",
     "🧪 bubblewrap मोड (हल्का आइसोलेशन, apt install के बिना)",
     "🧪 bubblewrap 모드 (가벼운 격리, apt install 불필요)",
     "🧪 bubblewrap modu (hafif yalıtım, apt install gerekmez)",
     "🧪 bubblewrap モード（軽量な隔離、apt install 不要）"),
    ("· zsh not found, using bash", "· zsh не знайдено, використовується bash",
     "· zsh introuvable, utilisation de bash", "· zsh no encontrado, se usa bash",
     "· zsh não encontrado, usando bash", "· zsh nicht gefunden, bash wird verwendet",
     "· zsh ei löytynyt, käytetään bashia", "· zsh tidak ditemukan, memakai bash",
     "· zsh नहीं मिला, bash इस्तेमाल हो रहा है", "· zsh를 찾을 수 없어 bash를 사용합니다",
     "· zsh bulunamadı, bash kullanılıyor", "· zsh が見つからないため bash を使用します"),
    ("⏳ First run: building the sandbox image (internet required, 2–6 minutes)…",
     "⏳ Перший запуск: збираю образ пісочниці (потрібен інтернет, 2–6 хвилин)…",
     "⏳ Premier lancement : construction de l’image du bac à sable (Internet requis, 2 à 6 minutes)…",
     "⏳ Primera ejecución: creando la imagen del sandbox (requiere internet, 2–6 minutos)…",
     "⏳ Primeira execução: criando a imagem do sandbox (requer internet, 2–6 minutos)…",
     "⏳ Erster Start: Sandbox-Image wird erstellt (Internet erforderlich, 2–6 Minuten)…",
     "⏳ Ensimmäinen käynnistys: rakennetaan hiekkalaatikon levykuvaa (vaatii internetin, 2–6 minuuttia)…",
     "⏳ Pertama kali dijalankan: membangun image sandbox (perlu internet, 2–6 menit)…",
     "⏳ पहली बार चलाना: सैंडबॉक्स इमेज बनाई जा रही है (इंटरनेट ज़रूरी, 2–6 मिनट)…",
     "⏳ 최초 실행: 샌드박스 이미지를 빌드하는 중 (인터넷 필요, 2~6분)…",
     "⏳ İlk çalıştırma: korumalı alan imajı oluşturuluyor (internet gerekir, 2–6 dakika)…",
     "⏳ 初回起動：サンドボックスのイメージをビルド中（インターネット接続が必要、2〜6 分）…"),
    ("❌ Failed to build the image.", "❌ Не вдалося зібрати образ.", "❌ Échec de la construction de l’image.",
     "❌ No se pudo crear la imagen.", "❌ Falha ao criar a imagem.", "❌ Image konnte nicht erstellt werden.",
     "❌ Levykuvan rakentaminen epäonnistui.", "❌ Gagal membangun image.", "❌ इमेज बनाने में विफल।",
     "❌ 이미지를 빌드하지 못했습니다.", "❌ İmaj oluşturulamadı.", "❌ イメージのビルドに失敗しました。"),
    ("Press any key…", "Натисніть будь-яку клавішу…", "Appuyez sur une touche…", "Pulsa cualquier tecla…",
     "Pressione qualquer tecla…", "Beliebige Taste drücken…", "Paina mitä tahansa näppäintä…",
     "Tekan tombol apa saja…", "कोई भी कुंजी दबाएँ…", "아무 키나 누르세요…", "Bir tuşa basın…",
     "何かキーを押してください…"),
    ("🧪 Ubuntu 24.04 container via {eng} · changes disappear after the session",
     "🧪 Контейнер Ubuntu 24.04 через {eng} · зміни зникають після сесії",
     "🧪 Conteneur Ubuntu 24.04 via {eng} · les modifications disparaissent après la session",
     "🧪 Contenedor Ubuntu 24.04 mediante {eng} · los cambios desaparecen al terminar la sesión",
     "🧪 Contêiner Ubuntu 24.04 via {eng} · as alterações desaparecem após a sessão",
     "🧪 Ubuntu-24.04-Container über {eng} · Änderungen verschwinden nach der Sitzung",
     "🧪 Ubuntu 24.04 -kontti ({eng}) · muutokset katoavat istunnon jälkeen",
     "🧪 Kontainer Ubuntu 24.04 melalui {eng} · perubahan hilang setelah sesi berakhir",
     "🧪 {eng} के ज़रिए Ubuntu 24.04 कंटेनर · सत्र के बाद बदलाव मिट जाते हैं",
     "🧪 {eng}로 실행되는 Ubuntu 24.04 컨테이너 · 세션이 끝나면 변경 사항이 사라집니다",
     "🧪 {eng} üzerinden Ubuntu 24.04 kapsayıcısı · değişiklikler oturumdan sonra kaybolur",
     "🧪 {eng} 経由の Ubuntu 24.04 コンテナ · セッション終了後に変更は消えます"),
    ("[Session ended — press “↻ New session”]", "[Сесію завершено — натисніть «↻ Нова сесія»]",
     "[Session terminée — appuyez sur « ↻ Nouvelle session »]",
     "[Sesión finalizada — pulsa «↻ Nueva sesión»]",
     "[Sessão encerrada — clique em «↻ Nova sessão»]",
     "[Sitzung beendet – klicken Sie auf „↻ Neue Sitzung“]",
     "[Istunto päättyi — paina ”↻ Uusi istunto”]",
     "[Sesi berakhir — tekan “↻ Sesi baru”]",
     "[सत्र समाप्त — “↻ नया सत्र” दबाएँ]",
     "[세션이 종료되었습니다 — “↻ 새 세션”을 누르세요]",
     "[Oturum sona erdi — “↻ Yeni oturum”a basın]",
     "[セッションが終了しました — 「↻ 新しいセッション」を押してください]"),
    ("Run command", "Виконати команду", "Exécuter la commande", "Ejecutar comando", "Executar comando",
     "Befehl ausführen", "Suorita komento", "Jalankan perintah", "कमांड चलाएँ", "명령어 실행",
     "Komutu çalıştır", "コマンドを実行"),
    ("Where to run the command?", "Де виконати команду?", "Où exécuter la commande ?",
     "¿Dónde ejecutar el comando?", "Onde executar o comando?", "Wo soll der Befehl ausgeführt werden?",
     "Missä komento suoritetaan?", "Di mana perintah akan dijalankan?", "कमांड कहाँ चलानी है?",
     "명령어를 어디에서 실행할까요?", "Komut nerede çalıştırılsın?", "コマンドをどこで実行しますか？"),
    ("✏ Replace the parts in <angle brackets> with your own value.",
     "✏ Замініть частини в <кутових дужках> на своє значення.",
     "✏ Remplacez les parties entre <chevrons> par votre propre valeur.",
     "✏ Sustituye las partes entre <corchetes angulares> por tu propio valor.",
     "✏ Substitua as partes entre <colchetes angulares> pelo seu próprio valor.",
     "✏ Ersetzen Sie die Teile in <spitzen Klammern> durch Ihren eigenen Wert.",
     "✏ Korvaa <kulmasulkeissa> olevat osat omalla arvollasi.",
     "✏ Ganti bagian dalam <tanda kurung sudut> dengan nilai Anda sendiri.",
     "✏ <कोण कोष्ठक> वाले हिस्सों को अपने मान से बदलें।",
     "✏ <꺾쇠 괄호> 안의 부분을 원하는 값으로 바꾸세요.",
     "✏ <Açılı parantez> içindeki kısımları kendi değerinizle değiştirin.",
     "✏ <山かっこ> の部分を自分の値に置き換えてください。"),
    ("⚠ Dangerous command! On the real system it can irreversibly delete data "
     "or shut the computer down. For experiments, use the sandbox.",
     "⚠ Небезпечна команда! У системі вона може безповоротно видалити дані або вимкнути комп’ютер. "
     "Для дослідів краще пісочниця.",
     "⚠ Commande dangereuse ! Sur le vrai système, elle peut supprimer des données de façon irréversible "
     "ou éteindre l’ordinateur. Pour expérimenter, utilisez le bac à sable.",
     "⚠ ¡Comando peligroso! En el sistema real puede borrar datos de forma irreversible "
     "o apagar el equipo. Para experimentar, usa el sandbox.",
     "⚠ Comando perigoso! No sistema real, ele pode apagar dados de forma irreversível "
     "ou desligar o computador. Para experimentar, use o sandbox.",
     "⚠ Gefährlicher Befehl! Im echten System kann er Daten unwiderruflich löschen "
     "oder den Computer herunterfahren. Zum Ausprobieren nutzen Sie die Sandbox.",
     "⚠ Vaarallinen komento! Oikeassa järjestelmässä se voi poistaa tietoja peruuttamattomasti "
     "tai sammuttaa tietokoneen. Kokeiluihin käytä hiekkalaatikkoa.",
     "⚠ Perintah berbahaya! Pada sistem asli, perintah ini dapat menghapus data secara permanen "
     "atau mematikan komputer. Untuk bereksperimen, gunakan sandbox.",
     "⚠ ख़तरनाक कमांड! असली सिस्टम पर यह डेटा हमेशा के लिए मिटा सकती है "
     "या कंप्यूटर बंद कर सकती है। प्रयोग के लिए सैंडबॉक्स इस्तेमाल करें।",
     "⚠ 위험한 명령어입니다! 실제 시스템에서는 데이터를 영구적으로 삭제하거나 "
     "컴퓨터를 종료할 수 있습니다. 실험은 샌드박스에서 하세요.",
     "⚠ Tehlikeli komut! Gerçek sistemde verileri geri döndürülemez biçimde silebilir "
     "veya bilgisayarı kapatabilir. Denemeler için korumalı alanı kullanın.",
     "⚠ 危険なコマンドです！実際のシステムでは、データが完全に削除されたり、"
     "コンピューターがシャットダウンされたりする可能性があります。試すときはサンドボックスを使ってください。"),
    ("Cancel", "Скасувати", "Annuler", "Cancelar", "Cancelar", "Abbrechen", "Peruuta", "Batal", "रद्द करें",
     "취소", "İptal", "キャンセル"),
    ("🧪 In sandbox", "🧪 У пісочниці", "🧪 Dans le bac à sable", "🧪 En el sandbox", "🧪 No sandbox",
     "🧪 In der Sandbox", "🧪 Hiekkalaatikossa", "🧪 Di sandbox", "🧪 सैंडबॉक्स में", "🧪 샌드박스에서",
     "🧪 Korumalı alanda", "🧪 サンドボックスで"),
    ("🖥 On system", "🖥 У системі", "🖥 Sur le système", "🖥 En el sistema", "🖥 No sistema",
     "🖥 Im System", "🖥 Järjestelmässä", "🖥 Di sistem", "🖥 सिस्टम पर", "🖥 시스템에서",
     "🖥 Sistemde", "🖥 システムで"),
    ("⚠ First replace the <bracketed fields> with real values.",
     "⚠ Спочатку замініть <поля в дужках> на реальні значення.",
     "⚠ Remplacez d’abord les <champs entre chevrons> par de vraies valeurs.",
     "⚠ Primero sustituye los <campos entre corchetes> por valores reales.",
     "⚠ Primeiro substitua os <campos entre colchetes> por valores reais.",
     "⚠ Ersetzen Sie zuerst die <Felder in Klammern> durch echte Werte.",
     "⚠ Korvaa ensin <sulkeissa> olevat kentät oikeilla arvoilla.",
     "⚠ Ganti dulu <kolom dalam tanda kurung> dengan nilai sebenarnya.",
     "⚠ पहले <कोष्ठक वाले फ़ील्ड> को असली मानों से बदलें।",
     "⚠ 먼저 <괄호 안의 항목>을 실제 값으로 바꾸세요.",
     "⚠ Önce <parantez içindeki alanları> gerçek değerlerle değiştirin.",
     "⚠ 先に <かっこ内の項目> を実際の値に置き換えてください。"),
    ("System — {cmd}", "Система — {cmd}", "Système — {cmd}", "Sistema — {cmd}", "Sistema — {cmd}",
     "System — {cmd}", "Järjestelmä — {cmd}", "Sistem — {cmd}", "सिस्टम — {cmd}", "시스템 — {cmd}",
     "Sistem — {cmd}", "システム — {cmd}"),
    ("── Finished (exit code", "── Завершено (код", "── Terminé (code de sortie", "── Finalizado (código de salida",
     "── Concluído (código de saída", "── Beendet (Exit-Code", "── Valmis (poistumiskoodi",
     "── Selesai (kode keluar", "── समाप्त (एग्ज़िट कोड", "── 완료 (종료 코드", "── Tamamlandı (çıkış kodu",
     "── 完了 (終了コード"),
    ("Press any key to close…", "Натисніть будь-яку клавішу, щоб закрити…", "Appuyez sur une touche pour fermer…",
     "Pulsa cualquier tecla para cerrar…", "Pressione qualquer tecla para fechar…",
     "Beliebige Taste zum Schließen drücken…", "Sulje painamalla mitä tahansa näppäintä…",
     "Tekan tombol apa saja untuk menutup…", "बंद करने के लिए कोई भी कुंजी दबाएँ…",
     "닫으려면 아무 키나 누르세요…", "Kapatmak için bir tuşa basın…", "閉じるには何かキーを押してください…"),
    ("⌨ Shortcuts", "⌨ Гарячі клавіші", "⌨ Raccourcis", "⌨ Atajos", "⌨ Atalhos", "⌨ Tastenkürzel",
     "⌨ Pikanäppäimet", "⌨ Pintasan", "⌨ शॉर्टकट", "⌨ 단축키", "⌨ Kısayollar", "⌨ ショートカット"),
    ("📦 Commands", "📦 Команди", "📦 Commandes", "📦 Comandos", "📦 Comandos", "📦 Befehle",
     "📦 Komennot", "📦 Perintah", "📦 कमांड", "📦 명령어", "📦 Komutlar", "📦 コマンド"),
    ("🧪 Sandbox", "🧪 Пісочниця", "🧪 Bac à sable", "🧪 Sandbox", "🧪 Sandbox", "🧪 Sandbox",
     "🧪 Hiekkalaatikko", "🧪 Sandbox", "🧪 सैंडबॉक्स", "🧪 샌드박스", "🧪 Korumalı alan", "🧪 サンドボックス"),
    ("📜 Journal", "📜 Журнал", "📜 Journal", "📜 Historial", "📜 Diário", "📜 Protokoll",
     "📜 Loki", "📜 Jurnal", "📜 जर्नल", "📜 기록", "📜 Günlük", "📜 ログ"),
    ("A helper for newcomers to PixiumOS. Shows useful keyboard shortcuts of your system, "
     "explains popular commands in plain words, and provides a safe sandbox terminal "
     "where you can try anything.",
     "Помічник для новачків у PixiumOS. Показує корисні гарячі клавіші вашої системи, "
     "пояснює популярні команди простими словами та надає безпечний термінал-пісочницю, "
     "де можна пробувати що завгодно.",
     "Un assistant pour les débutants sous PixiumOS. Il affiche les raccourcis clavier utiles de votre système, "
     "explique les commandes courantes avec des mots simples et propose un terminal bac à sable sécurisé "
     "où vous pouvez tout essayer.",
     "Un asistente para quienes empiezan en PixiumOS. Muestra los atajos de teclado útiles de tu sistema, "
     "explica los comandos más populares con palabras sencillas y ofrece una terminal sandbox segura "
     "donde puedes probar lo que quieras.",
     "Um assistente para iniciantes no PixiumOS. Mostra os atalhos de teclado úteis do seu sistema, "
     "explica os comandos populares em palavras simples e oferece um terminal sandbox seguro "
     "onde você pode testar o que quiser.",
     "Ein Helfer für Einsteiger in PixiumOS. Er zeigt nützliche Tastenkürzel Ihres Systems, "
     "erklärt gängige Befehle in einfachen Worten und bietet ein sicheres Sandbox-Terminal, "
     "in dem Sie alles ausprobieren können.",
     "Apuri PixiumOS:n aloittelijoille. Näyttää järjestelmäsi hyödylliset pikanäppäimet, "
     "selittää suosittuja komentoja yksinkertaisin sanoin ja tarjoaa turvallisen hiekkalaatikkopäätteen, "
     "jossa voit kokeilla mitä tahansa.",
     "Asisten untuk pemula di PixiumOS. Menampilkan pintasan keyboard yang berguna di sistem Anda, "
     "menjelaskan perintah populer dengan kata-kata sederhana, dan menyediakan terminal sandbox yang aman "
     "tempat Anda bebas mencoba apa saja.",
     "PixiumOS के नए उपयोगकर्ताओं के लिए सहायक। यह आपके सिस्टम के उपयोगी कीबोर्ड शॉर्टकट दिखाता है, "
     "लोकप्रिय कमांड आसान शब्दों में समझाता है और एक सुरक्षित सैंडबॉक्स टर्मिनल देता है, "
     "जहाँ आप कुछ भी आज़मा सकते हैं।",
     "PixiumOS 입문자를 위한 도우미입니다. 시스템의 유용한 키보드 단축키를 보여 주고, "
     "자주 쓰는 명령어를 쉬운 말로 설명하며, 무엇이든 시도해 볼 수 있는 안전한 샌드박스 터미널을 제공합니다.",
     "PixiumOS 初心者のためのヘルパーです。システムの便利なキーボードショートカットを表示し、"
     "よく使うコマンドをやさしい言葉で説明し、何でも試せる安全なサンドボックス端末を提供します。"),
    ("command: {cmd}", "команда: {cmd}", "commande : {cmd}", "comando: {cmd}", "comando: {cmd}",
     "Befehl: {cmd}", "komento: {cmd}", "perintah: {cmd}", "कमांड: {cmd}", "명령어: {cmd}",
     "komut: {cmd}", "コマンド：{cmd}"),
    ("🧪 EasyHelper sandbox", "🧪 Пісочниця EasyHelper", "🧪 Bac à sable EasyHelper", "🧪 Sandbox de EasyHelper",
     "🧪 Sandbox do EasyHelper", "🧪 EasyHelper-Sandbox", "🧪 EasyHelperin hiekkalaatikko",
     "🧪 Sandbox EasyHelper", "🧪 EasyHelper सैंडबॉक्स", "🧪 EasyHelper 샌드박스",
     "🧪 EasyHelper korumalı alanı", "🧪 EasyHelper サンドボックス"),
    ("— this is not your system, break whatever you like.",
     "— це не ваша система, ламайте що завгодно.",
     "— ce n’est pas votre système, cassez ce que vous voulez.",
     "— este no es tu sistema, rompe lo que quieras.",
     "— este não é o seu sistema, quebre o que quiser.",
     "— das ist nicht Ihr System, machen Sie kaputt, was Sie wollen.",
     "— tämä ei ole sinun järjestelmäsi, rikkoa saa mitä vain.",
     "— ini bukan sistem Anda, rusak saja sesuka hati.",
     "— यह आपका सिस्टम नहीं है, जो चाहें तोड़ें।",
     "— 여기는 실제 시스템이 아니니 마음껏 망가뜨려도 됩니다.",
     "— bu sizin sisteminiz değil, canınız ne isterse bozun.",
     "— ここはあなたのシステムではないので、好きなだけ壊してかまいません。"),
    ("→ accepts the suggestion, ↑/↓ — history, Tab — completion",
     "→ приймає підказку, ↑/↓ — історія, Tab — доповнення",
     "→ accepte la suggestion, ↑/↓ — historique, Tab — complétion",
     "→ acepta la sugerencia, ↑/↓ — historial, Tab — autocompletar",
     "→ aceita a sugestão, ↑/↓ — histórico, Tab — autocompletar",
     "→ übernimmt den Vorschlag, ↑/↓ — Verlauf, Tab — Vervollständigung",
     "→ hyväksyy ehdotuksen, ↑/↓ — historia, Tab — täydennys",
     "→ menerima saran, ↑/↓ — riwayat, Tab — pelengkapan",
     "→ सुझाव स्वीकारता है, ↑/↓ — इतिहास, Tab — स्वतः पूर्ण",
     "→ 제안 수락, ↑/↓ — 기록, Tab — 자동 완성",
     "→ öneriyi kabul eder, ↑/↓ — geçmiş, Tab — tamamlama",
     "→ 候補を採用、↑/↓ — 履歴、Tab — 補完"),
])
 
# <<OFFLINE-DATA-END>>
 
 
if __name__ == "__main__":
    App().run(None)
 
