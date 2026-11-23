#!/usr/bin/env python3
import json
import os
 
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Pango, PangoCairo
 
# Критически важно для Wayland: задаем имя программы ДО создания окна
GLib.set_prgname('cacheclean')
GLib.set_application_name('cacheclean')
# Дублируем для X11
Gdk.set_program_class('cacheclean')
 
# ════════════════════════════════════════════════════════════════════
#  ЯЗЫКИ (тот же список и тот же файл настроек, что и в EasyHelper —
#  выбранный язык общий для обеих программ)
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
DEFAULT_LANG = "ru"
RTL_LANGS = set()
 
APP_DIR = os.path.join(GLib.get_user_data_dir(), "easyhelper")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
 
CUR = DEFAULT_LANG
 
 
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
        os.makedirs(APP_DIR, exist_ok=True)
        data = {}
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = {}
        data["lang"] = code
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        print("settings error:", e)
 
 
def apply_direction():
    rtl = CUR.split("_")[0] in RTL_LANGS
    Gtk.Widget.set_default_direction(Gtk.TextDirection.RTL if rtl else Gtk.TextDirection.LTR)
 
 
# Порядок значений: win, intro, b1, b2, b3, t_timer, t_manual, t_log, close, lang_tip, lang_search
_KEYS = ("win", "intro", "b1", "b2", "b3", "t_timer", "t_manual", "t_log", "close", "lang_tip", "lang_search")
_TX_ROWS = {
    "ru": ("cacheclean — информация",
           "Работает в фоне, вручную ничего запускать не нужно.",
           "• Очищает кэш памяти каждые 15 минут",
           "• Запускается автоматически после перезагрузки",
           "• Присылает уведомления о свободной памяти",
           "Проверить таймер:", "Запустить очистку вручную:", "Посмотреть лог:", "Закрыть",
           "Язык интерфейса", "Поиск языка…"),
    "uk": ("cacheclean — інформація",
           "Працює у фоні, вручну нічого запускати не потрібно.",
           "• Очищує кеш пам’яті кожні 15 хвилин",
           "• Запускається автоматично після перезавантаження",
           "• Надсилає сповіщення про вільну пам’ять",
           "Перевірити таймер:", "Запустити очищення вручну:", "Переглянути лог:", "Закрити",
           "Мова інтерфейсу", "Пошук мови…"),
    "en": ("cacheclean — information",
           "Runs in the background, nothing to launch manually.",
           "• Clears the memory cache every 15 minutes",
           "• Starts automatically after reboot",
           "• Sends notifications about free memory",
           "Check the timer:", "Run cleaning manually:", "View the log:", "Close",
           "Interface language", "Search language…"),
    "fr": ("cacheclean — informations",
           "Fonctionne en arrière-plan, rien à lancer manuellement.",
           "• Vide le cache mémoire toutes les 15 minutes",
           "• Démarre automatiquement après le redémarrage",
           "• Envoie des notifications sur la mémoire libre",
           "Vérifier le minuteur :", "Lancer le nettoyage manuellement :", "Consulter le journal :", "Fermer",
           "Langue de l’interface", "Rechercher une langue…"),
    "es": ("cacheclean — información",
           "Funciona en segundo plano, no hace falta iniciar nada manualmente.",
           "• Limpia la caché de memoria cada 15 minutos",
           "• Se inicia automáticamente tras reiniciar",
           "• Envía notificaciones sobre la memoria libre",
           "Comprobar el temporizador:", "Ejecutar la limpieza manualmente:", "Ver el registro:", "Cerrar",
           "Idioma de la interfaz", "Buscar idioma…"),
    "pt": ("cacheclean — informações",
           "Funciona em segundo plano, não é preciso iniciar nada manualmente.",
           "• Limpa o cache de memória a cada 15 minutos",
           "• Inicia automaticamente após a reinicialização",
           "• Envia notificações sobre a memória livre",
           "Verificar o temporizador:", "Executar a limpeza manualmente:", "Ver o registro:", "Fechar",
           "Idioma da interface", "Pesquisar idioma…"),
    "de": ("cacheclean — Informationen",
           "Läuft im Hintergrund, es muss nichts manuell gestartet werden.",
           "• Leert den Speicher-Cache alle 15 Minuten",
           "• Startet nach einem Neustart automatisch",
           "• Sendet Benachrichtigungen über freien Speicher",
           "Timer prüfen:", "Bereinigung manuell starten:", "Protokoll anzeigen:", "Schließen",
           "Sprache der Oberfläche", "Sprache suchen…"),
    "fi": ("cacheclean — tiedot",
           "Toimii taustalla, mitään ei tarvitse käynnistää käsin.",
           "• Tyhjentää muistivälimuistin 15 minuutin välein",
           "• Käynnistyy automaattisesti uudelleenkäynnistyksen jälkeen",
           "• Lähettää ilmoituksia vapaasta muistista",
           "Tarkista ajastin:", "Suorita puhdistus käsin:", "Katso loki:", "Sulje",
           "Käyttöliittymän kieli", "Hae kieltä…"),
    "id": ("cacheclean — informasi",
           "Berjalan di latar belakang, tidak perlu menjalankan apa pun secara manual.",
           "• Membersihkan cache memori setiap 15 menit",
           "• Berjalan otomatis setelah reboot",
           "• Mengirim notifikasi tentang memori bebas",
           "Periksa timer:", "Jalankan pembersihan secara manual:", "Lihat log:", "Tutup",
           "Bahasa antarmuka", "Cari bahasa…"),
    "zh_CN": ("cacheclean — 信息",
              "在后台运行，无需手动启动任何东西。",
              "• 每 15 分钟清理一次内存缓存",
              "• 重启后自动启动",
              "• 发送可用内存通知",
              "检查定时器：", "手动运行清理：", "查看日志：", "关闭",
              "界面语言", "搜索语言…"),
    "hi": ("cacheclean — जानकारी",
           "बैकग्राउंड में चलता है, कुछ भी हाथ से शुरू करने की ज़रूरत नहीं।",
           "• हर 15 मिनट में मेमोरी कैश साफ़ करता है",
           "• रीबूट के बाद अपने-आप शुरू हो जाता है",
           "• खाली मेमोरी की सूचनाएँ भेजता है",
           "टाइमर जाँचें:", "सफ़ाई हाथ से चलाएँ:", "लॉग देखें:", "बंद करें",
           "इंटरफ़ेस की भाषा", "भाषा खोजें…"),
    "ko": ("cacheclean — 정보",
           "백그라운드에서 동작하므로 직접 실행할 필요가 없습니다.",
           "• 15분마다 메모리 캐시를 정리합니다",
           "• 재부팅 후 자동으로 시작됩니다",
           "• 여유 메모리에 대한 알림을 보냅니다",
           "타이머 확인:", "수동으로 정리 실행:", "로그 보기:", "닫기",
           "인터페이스 언어", "언어 검색…"),
    "tr": ("cacheclean — bilgi",
           "Arka planda çalışır, elle bir şey başlatmanız gerekmez.",
           "• Bellek önbelleğini her 15 dakikada bir temizler",
           "• Yeniden başlatmadan sonra otomatik başlar",
           "• Boş bellek hakkında bildirim gönderir",
           "Zamanlayıcıyı kontrol et:", "Temizliği elle çalıştır:", "Günlüğü görüntüle:", "Kapat",
           "Arayüz dili", "Dil ara…"),
    "ja": ("cacheclean — 情報",
           "バックグラウンドで動作するため、手動で起動する必要はありません。",
           "• 15分ごとにメモリキャッシュを消去します",
           "• 再起動後に自動で起動します",
           "• 空きメモリについて通知します",
           "タイマーを確認：", "手動でクリーニングを実行：", "ログを表示：", "閉じる",
           "インターフェースの言語", "言語を検索…"),
}
TX = {code: dict(zip(_KEYS, row)) for code, row in _TX_ROWS.items()}
 
 
def tx(key):
    return TX.get(CUR, TX[DEFAULT_LANG]).get(key) or TX["ru"][key]
 
 
def build_text():
    return (
        tx("intro") + "\n\n"
        + tx("b1") + "\n"
        + tx("b2") + "\n"
        + tx("b3") + "\n\n"
        + tx("t_timer") + "\n"
        + "systemctl list-timers cacheclean.timer\n\n"
        + tx("t_manual") + "\n"
        + "sudo systemctl start cacheclean.service\n\n"
        + tx("t_log") + "\n"
        + "journalctl -u cacheclean.service -n 30 --no-pager"
    )
 
 
CUR = load_lang()
apply_direction()
 
# Обычный (не пиксельный) шрифт для заголовка. Если первого нет — берётся следующий.
TITLE_FONT = "Ubuntu Bold, DejaVu Sans Bold, Sans Bold 28"
TITLE_TEXT = "cacheclean"
# Плавный градиент: фиолетовый -> оранжевый (с промежуточной точкой для мягкости)
GRADIENT_STOPS = [
    (0.00, (0xa8 / 255, 0x55 / 255, 0xf7 / 255)),   # фиолетовый #a855f7
    (0.25, (0xba / 255, 0x5c / 255, 0xc0 / 255)),
    (0.50, (0xd0 / 255, 0x64 / 255, 0x86 / 255)),
    (0.75, (0xe4 / 255, 0x6b / 255, 0x50 / 255)),
    (1.00, (0xf9 / 255, 0x73 / 255, 0x16 / 255)),   # оранжевый #f97316
]
 
 
def make_gradient_title():
    """Заголовок с градиентом. Если нет pycairo — обычная подпись без градиента."""
    try:
        import cairo
    except Exception:
        lbl = Gtk.Label()
        lbl.set_markup("<b><span size='x-large'>%s</span></b>" % TITLE_TEXT)
        return lbl
 
    area = Gtk.DrawingArea()
    area.set_halign(Gtk.Align.CENTER)
    font = Pango.FontDescription(TITLE_FONT)
 
    probe = area.create_pango_layout(TITLE_TEXT)
    probe.set_font_description(font)
    w, h = probe.get_pixel_size()
    area.set_size_request(w + 4, h + 6)
 
    def on_draw(widget, cr):
        layout = PangoCairo.create_layout(cr)
        layout.set_font_description(font)
        layout.set_text(TITLE_TEXT, -1)
        tw, th = layout.get_pixel_size()
        alloc = widget.get_allocation()
        x = (alloc.width - tw) / 2
        y = (alloc.height - th) / 2
        grad = cairo.LinearGradient(x, 0, x + tw, 0)
        for pos, (r, g, b) in GRADIENT_STOPS:
            grad.add_color_stop_rgb(pos, r, g, b)
        cr.move_to(x, y)
        PangoCairo.layout_path(cr, layout)
        cr.set_source(grad)
        cr.fill()
        return False
 
    area.connect("draw", on_draw)
    return area
 
 
# ════════════════════════════════════════════════════════════════════
#  КНОПКА ВЫБОРА ЯЗЫКА (как в EasyHelper: 🌐 + название языка,
#  всплывающее окно с поиском и списком языков, ✓ у текущего)
# ════════════════════════════════════════════════════════════════════
def make_lang_button(on_pick):
    cur = LANG_INDEX[CUR]
    btn = Gtk.MenuButton()
    btn.set_label("🌐 " + cur[1])
    btn.set_tooltip_text(tx("lang_tip"))
 
    pop = Gtk.Popover()
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    box.set_margin_top(8)
    box.set_margin_bottom(8)
    box.set_margin_start(8)
    box.set_margin_end(8)
 
    search = Gtk.SearchEntry()
    search.set_placeholder_text(tx("lang_search"))
    lb = Gtk.ListBox()
    lb.set_selection_mode(Gtk.SelectionMode.NONE)
 
    for code, native, eng, _g in LANGUAGES:
        row = Gtk.ListBoxRow()
        h = Gtk.Box(spacing=10)
        h.set_margin_top(4)
        h.set_margin_bottom(4)
        h.set_margin_start(6)
        h.set_margin_end(6)
        n = Gtk.Label(label=native)
        n.set_xalign(0)
        n.set_hexpand(True)
        h.pack_start(n, True, True, 0)
        if eng != native:
            e = Gtk.Label(label=eng)
            e.get_style_context().add_class("dim-label")
            h.pack_start(e, False, False, 0)
        h.pack_start(Gtk.Label(label="✓" if code == CUR else "  "), False, False, 0)
        row.add(h)
        lb.add(row)
 
    def flt(row, _data=None):
        q = search.get_text().strip().lower()
        if not q:
            return True
        code, native, eng, _g = LANGUAGES[row.get_index()]
        return q in (native + " " + eng + " " + code).lower()
 
    lb.set_filter_func(flt, None)
    search.connect("search-changed", lambda *_: lb.invalidate_filter())
 
    def activated(_lb, row):
        code = LANGUAGES[row.get_index()][0]
        pop.popdown()
        GLib.idle_add(lambda: (on_pick(code), False)[1])
 
    lb.connect("row-activated", activated)
    lb.set_activate_on_single_click(True)
 
    sw = Gtk.ScrolledWindow()
    sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    sw.set_min_content_height(360)
    sw.set_min_content_width(320)
    sw.add(lb)
    box.pack_start(search, False, False, 0)
    box.pack_start(sw, True, True, 0)
    pop.add(box)
    box.show_all()
    btn.set_popover(pop)
    return btn
 
 
win = Gtk.Window(title=tx("win"))
win.set_default_size(420, 420)
win.set_border_width(20)
win.set_resizable(False)
 
vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
win.add(vbox)
 
# ── сверху: кнопка выбора языка (справа)
top_bar = Gtk.Box()
vbox.pack_start(top_bar, False, False, 0)
 
icon_path = "/usr/share/icons/Gemini_Generated_Image_3i3lq3i3lq3i3lq3-removebg-preview.png"
try:
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 96, 96, True)
    image = Gtk.Image.new_from_pixbuf(pixbuf)
    vbox.pack_start(image, False, False, 0)
except Exception as e:
    print(f"Ошибка загрузки иконки: {e}")
 
title_label = make_gradient_title()
vbox.pack_start(title_label, False, False, 0)
 
label = Gtk.Label(label=build_text())
label.set_selectable(True)
label.set_justify(Gtk.Justification.LEFT)
label.set_halign(Gtk.Align.START)
label.set_line_wrap(True)
label.set_max_width_chars(52)
vbox.pack_start(label, True, True, 0)
 
close_btn = Gtk.Button(label=tx("close"))
close_btn.connect("clicked", lambda w: win.close())
vbox.pack_start(close_btn, False, False, 0)
 
lang_holder = {"btn": None}
 
 
def place_lang_button():
    old = lang_holder["btn"]
    if old is not None:
        top_bar.remove(old)
    btn = make_lang_button(set_language)
    btn.set_halign(Gtk.Align.END)
    top_bar.pack_end(btn, False, False, 0)
    btn.show_all()
    lang_holder["btn"] = btn
 
 
def set_language(code):
    """Мгновенная смена языка: всё встроено, интернет не нужен."""
    global CUR
    if code not in LANG_INDEX or code == CUR:
        return
    CUR = code
    save_lang(code)
    apply_direction()
    win.set_title(tx("win"))
    label.set_text(build_text())
    close_btn.set_label(tx("close"))
    place_lang_button()
 
 
place_lang_button()
 
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
