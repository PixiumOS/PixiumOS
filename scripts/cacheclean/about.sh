#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

# Критически важно для Wayland: задаем имя программы ДО создания окна
GLib.set_prgname('cacheclean')
GLib.set_application_name('cacheclean')
# Дублируем для X11
Gdk.set_program_class('cacheclean')

win = Gtk.Window(title="cacheclean — информация")
win.set_default_size(420, 420)
win.set_border_width(20)
win.set_resizable(False)

vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
win.add(vbox)

icon_path = "/usr/share/icons/Gemini_Generated_Image_3i3lq3i3lq3i3lq3-removebg-preview.png"
try:
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 96, 96, True)
    image = Gtk.Image.new_from_pixbuf(pixbuf)
    vbox.pack_start(image, False, False, 0)
except Exception as e:
    print(f"Ошибка загрузки иконки: {e}")

title_label = Gtk.Label()
title_label.set_markup("<b><span size='x-large'>cacheclean</span></b>")
vbox.pack_start(title_label, False, False, 0)

text = """Работает в фоне, вручную ничего запускать не нужно.

• Очищает кэш памяти каждые 15 минут
• Запускается автоматически после перезагрузки
• Присылает уведомления о свободной памяти

Проверить таймер:
systemctl list-timers cacheclean.timer

Запустить очистку вручную:
sudo systemctl start cacheclean.service

Посмотреть лог:
journalctl -u cacheclean.service -n 30 --no-pager"""

label = Gtk.Label(label=text)
label.set_selectable(True)
label.set_justify(Gtk.Justification.LEFT)
label.set_halign(Gtk.Align.START)
vbox.pack_start(label, True, True, 0)

close_btn = Gtk.Button(label="Закрыть")
close_btn.connect("clicked", lambda w: win.close())
vbox.pack_start(close_btn, False, False, 0)

win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
