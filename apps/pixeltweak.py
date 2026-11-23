#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PixelTweak — единый файл: локальный словарь переводов (офлайн) + слой интерфейса
(системная светлая/тёмная тема + кнопка выбора языка).
 
Объединены бывшие pixeltweak_i18n.py и pixeltweak_ui.py. Логика не менялась:
вся работа (helper, polkit, бэкапы, откаты, журнал) выполняется оригинальным
ядром приложения, которое подключается как модуль pixeltweak_core.
 
ВАЖНО: оригинальный (старый) pixeltweak.py с ядром нужно переименовать в
pixeltweak_core.py и положить рядом с этим файлом — иначе имя pixeltweak.py
заняло бы это объединённое приложение.
 
Запуск:  python3 pixeltweak.py
 
Переводы: без сети и без ИИ, все написаны вручную и лежат прямо в этом файле.
Исходный язык интерфейса — русский (строки оригинала служат ключами).
Порядок переводов в каждой строке:
    uk, en, fr, es, pt, de, fi, id, zh, hi, ko, tr, ja
«{}» — место для подстановки (число, имя, путь и т. п.).
Строки, которых нет в словаре, показываются по-русски (как в оригинале).
"""
import os
import re
import sys
 
# ══════════════════════════════════════════════════════════════════════
#  ЧАСТЬ 1. Словарь переводов
# ══════════════════════════════════════════════════════════════════════
 
LANGS = [
    ("ru", "Русский"),
    ("uk", "Українська"),
    ("en", "English"),
    ("fr", "Français"),
    ("es", "Español"),
    ("pt", "Português"),
    ("de", "Deutsch"),
    ("fi", "Suomi"),
    ("id", "Bahasa Indonesia"),
    ("zh", "简体中文"),
    ("hi", "हिन्दी"),
    ("ko", "한국어"),
    ("tr", "Türkçe"),
    ("ja", "日本語"),
]
CODES = [c for c, _n in LANGS]
 
# Английские названия — для второй колонки в окне выбора языка
LANG_EN = {
    "ru": "Russian",
    "uk": "Ukrainian",
    "en": "",
    "fr": "French",
    "es": "Spanish",
    "pt": "Portuguese",
    "de": "German",
    "fi": "Finnish",
    "id": "Indonesian",
    "zh": "Chinese (Mandarin)",
    "hi": "Hindi",
    "ko": "Korean",
    "tr": "Turkish",
    "ja": "Japanese",
}
 
_RAW = [
    # ── общие элементы ───────────────────────────────────────────────
    ("Поиск языка…", "Пошук мови…", "Search language…", "Rechercher une langue…", "Buscar idioma…",
     "Pesquisar idioma…", "Sprache suchen…", "Hae kieltä…", "Cari bahasa…", "搜索语言…", "भाषा खोजें…",
     "언어 검색…", "Dil ara…", "言語を検索…"),
    ("Текущее состояние", "Поточний стан", "Current status", "État actuel", "Estado actual", "Estado atual",
     "Aktueller Status", "Nykytila", "Status saat ini", "当前状态", "वर्तमान स्थिति", "현재 상태",
     "Mevcut durum", "現在の状態"),
    ("Перечитать live-статус", "Перечитати live-статус", "Re-read live status", "Relire l'état en direct",
     "Releer el estado en vivo", "Reler o estado em tempo real", "Live-Status neu einlesen",
     "Lue live-tila uudelleen", "Baca ulang status langsung", "重新读取实时状态",
     "लाइव स्थिति दोबारा पढ़ें", "실시간 상태 다시 읽기", "Canlı durumu yeniden oku", "ライブ状態を再読み込み"),
    ("↻ Обновить", "↻ Оновити", "↻ Refresh", "↻ Actualiser", "↻ Actualizar", "↻ Atualizar", "↻ Aktualisieren",
     "↻ Päivitä", "↻ Segarkan", "↻ 刷新", "↻ रीफ़्रेश", "↻ 새로고침", "↻ Yenile", "↻ 更新"),
    ("Статус обновлён", "Статус оновлено", "Status updated", "État actualisé", "Estado actualizado",
     "Estado atualizado", "Status aktualisiert", "Tila päivitetty", "Status diperbarui", "状态已更新",
     "स्थिति अपडेट हुई", "상태를 새로 고쳤습니다", "Durum güncellendi", "状態を更新しました"),
    ("Применить настройки", "Застосувати налаштування", "Apply settings", "Appliquer les réglages",
     "Aplicar ajustes", "Aplicar configurações", "Einstellungen anwenden", "Ota asetukset käyttöön",
     "Terapkan pengaturan", "应用设置", "सेटिंग्स लागू करें", "설정 적용", "Ayarları uygula", "設定を適用"),
    ("Сохранить", "Зберегти", "Save", "Enregistrer", "Guardar", "Salvar", "Speichern", "Tallenna", "Simpan",
     "保存", "सहेजें", "저장", "Kaydet", "保存"),
    ("Применить", "Застосувати", "Apply", "Appliquer", "Aplicar", "Aplicar", "Anwenden", "Käytä", "Terapkan",
     "应用", "लागू करें", "적용", "Uygula", "適用"),
    ("Откатить «{}»", "Відкотити «{}»", "Roll back “{}”", "Restaurer « {} »", "Revertir «{}»",
     "Reverter «{}»", "„{}“ zurücksetzen", "Palauta «{}»", "Kembalikan «{}»", "回滚「{}」", "«{}» वापस लाएँ",
     "「{}」 되돌리기", "«{}» geri al", "「{}」を元に戻す"),
    ("↩ Откатить", "↩ Відкотити", "↩ Roll back", "↩ Restaurer", "↩ Revertir", "↩ Reverter", "↩ Zurücksetzen",
     "↩ Palauta", "↩ Kembalikan", "↩ 回滚", "↩ वापस लाएँ", "↩ 되돌리기", "↩ Geri al", "↩ 元に戻す"),
    ("Откатить настройки «{}»?", "Відкотити налаштування «{}»?", "Roll back the “{}” settings?",
     "Restaurer les réglages de « {} » ?", "¿Revertir los ajustes de «{}»?",
     "Reverter as configurações de «{}»?", "Einstellungen „{}“ zurücksetzen?",
     "Palautetaanko «{}»-asetukset?", "Kembalikan pengaturan «{}»?", "要回滚「{}」的设置吗？",
     "«{}» की सेटिंग्स वापस लाएँ?", "「{}」 설정을 되돌릴까요?", "«{}» ayarları geri alınsın mı?",
     "「{}」の設定を元に戻しますか？"),
    ("«Предыдущая» — то, что было до последнего сохранения.",
     "«Попередня» — те, що було до останнього збереження.",
     "“Previous” is what you had before the last save.",
     "« Précédente » : l'état avant la dernière sauvegarde.",
     "«Anterior»: lo que había antes del último guardado.",
     "«Anterior»: o que havia antes do último salvamento.",
     "„Vorherige“ ist der Stand vor dem letzten Speichern.",
     "«Edellinen» on tila ennen viimeisintä tallennusta.",
     "«Sebelumnya» adalah kondisi sebelum penyimpanan terakhir.",
     "「上一个」是上次保存之前的状态。",
     "«पिछला» — पिछली बार सहेजने से पहले की स्थिति।",
     "「이전」은 마지막 저장 이전의 상태입니다.",
     "«Önceki», son kaydetmeden önceki durumdur.",
     "「前回」は直前の保存より前の状態です。"),
    ("«Исходная» — самая первая версия до PixelTweak (если файла раньше не было, он будет удалён).",
     "«Початкова» — найперша версія до PixelTweak (якщо файла раніше не було, його буде видалено).",
     "“Original” is the very first version from before PixelTweak (if the file didn't exist before, it will be deleted).",
     "« D'origine » : la toute première version, avant PixelTweak (si le fichier n'existait pas, il sera supprimé).",
     "«Original»: la primera versión, anterior a PixelTweak (si el archivo no existía, se eliminará).",
     "«Original»: a primeira versão, anterior ao PixelTweak (se o arquivo não existia, ele será excluído).",
     "„Ursprünglich“ ist die allererste Version vor PixelTweak (existierte die Datei vorher nicht, wird sie gelöscht).",
     "«Alkuperäinen» on aivan ensimmäinen versio ennen PixelTweakia (jos tiedostoa ei ollut, se poistetaan).",
     "«Asli» adalah versi paling awal sebelum PixelTweak (jika berkas sebelumnya tidak ada, berkas akan dihapus).",
     "「原始」是使用 PixelTweak 之前的最初版本（如果之前没有该文件，则会将其删除）。",
     "«मूल» — PixelTweak से पहले का सबसे पहला संस्करण (यदि फ़ाइल पहले नहीं थी, तो उसे हटा दिया जाएगा)।",
     "「원본」은 PixelTweak 이전의 가장 처음 버전입니다(이전에 파일이 없었다면 삭제됩니다).",
     "«Orijinal», PixelTweak öncesindeki en ilk sürümdür (dosya daha önce yoksa silinir).",
     "「元の状態」は PixelTweak 導入前の最初のバージョンです（以前ファイルがなかった場合は削除されます）。"),
    ("Предыдущую", "Попередню", "Previous", "Précédente", "Anterior", "Anterior", "Vorherige", "Edellinen",
     "Sebelumnya", "上一个", "पिछला", "이전", "Önceki", "前回"),
    ("Исходную", "Початкову", "Original", "D'origine", "Original", "Original", "Ursprüngliche", "Alkuperäinen",
     "Asli", "原始", "मूल", "원본", "Orijinal", "元の状態"),
    ("Отмена", "Скасувати", "Cancel", "Annuler", "Cancelar", "Cancelar", "Abbrechen", "Peruuta", "Batal",
     "取消", "रद्द करें", "취소", "İptal", "キャンセル"),
    ("Закрыть", "Закрити", "Close", "Fermer", "Cerrar", "Fechar", "Schließen", "Sulje", "Tutup", "关闭",
     "बंद करें", "닫기", "Kapat", "閉じる"),
    ("Журнал", "Журнал", "Log", "Journal", "Registro", "Registro", "Protokoll", "Loki", "Log", "日志",
     "लॉग", "로그", "Günlük", "ログ"),
    ("Отменить", "Скасувати", "Cancel", "Annuler", "Cancelar", "Cancelar", "Abbrechen", "Peruuta", "Batalkan",
     "取消", "रद्द करें", "취소", "İptal et", "中止"),
    ("Журнал PixelTweak", "Журнал PixelTweak", "PixelTweak log", "Journal de PixelTweak",
     "Registro de PixelTweak", "Registro do PixelTweak", "PixelTweak-Protokoll", "PixelTweak-loki",
     "Log PixelTweak", "PixelTweak 日志", "PixelTweak लॉग", "PixelTweak 로그", "PixelTweak günlüğü",
     "PixelTweak ログ"),
    ("Подробности", "Подробиці", "Details", "Détails", "Detalles", "Detalhes", "Details", "Tiedot", "Detail",
     "详情", "विवरण", "자세히", "Ayrıntılar", "詳細"),
    ("Удалить помощник", "Видалити помічник", "Remove helper", "Supprimer l'assistant",
     "Eliminar el asistente", "Remover o auxiliar", "Helfer entfernen", "Poista apuohjelma", "Hapus helper",
     "移除辅助程序", "हेल्पर हटाएँ", "도우미 제거", "Yardımcıyı kaldır", "ヘルパーを削除"),
    ("Удалить системный помощник?", "Видалити системний помічник?", "Remove the system helper?",
     "Supprimer l'assistant système ?", "¿Eliminar el asistente del sistema?",
     "Remover o auxiliar do sistema?", "Systemhelfer entfernen?", "Poistetaanko järjestelmän apuohjelma?",
     "Hapus helper sistem?", "要移除系统辅助程序吗？", "सिस्टम हेल्पर हटाएँ?", "시스템 도우미를 제거할까요?",
     "Sistem yardımcısı kaldırılsın mı?", "システムヘルパーを削除しますか？"),
    ("Будут удалены /usr/libexec/pixeltweak-helper и polkit-правило.",
     "Буде видалено /usr/libexec/pixeltweak-helper і правило polkit.",
     "/usr/libexec/pixeltweak-helper and the polkit rule will be removed.",
     "/usr/libexec/pixeltweak-helper et la règle polkit seront supprimés.",
     "Se eliminarán /usr/libexec/pixeltweak-helper y la regla de polkit.",
     "/usr/libexec/pixeltweak-helper e a regra do polkit serão removidos.",
     "/usr/libexec/pixeltweak-helper und die polkit-Regel werden entfernt.",
     "/usr/libexec/pixeltweak-helper ja polkit-sääntö poistetaan.",
     "/usr/libexec/pixeltweak-helper dan aturan polkit akan dihapus.",
     "将删除 /usr/libexec/pixeltweak-helper 和 polkit 规则。",
     "/usr/libexec/pixeltweak-helper और polkit नियम हटा दिए जाएँगे।",
     "/usr/libexec/pixeltweak-helper와 polkit 규칙이 삭제됩니다.",
     "/usr/libexec/pixeltweak-helper ve polkit kuralı kaldırılacak.",
     "/usr/libexec/pixeltweak-helper と polkit ルールが削除されます。"),
    ("Настройки, сервисы и бэкапы останутся.", "Налаштування, сервіси та резервні копії залишаться.",
     "Settings, services and backups will remain.", "Les réglages, services et sauvegardes seront conservés.",
     "Los ajustes, servicios y copias de seguridad se conservarán.",
     "As configurações, serviços e backups serão mantidos.",
     "Einstellungen, Dienste und Backups bleiben erhalten.",
     "Asetukset, palvelut ja varmuuskopiot säilyvät.", "Pengaturan, layanan, dan cadangan tetap ada.",
     "设置、服务和备份将保留。", "सेटिंग्स, सेवाएँ और बैकअप बने रहेंगे।",
     "설정, 서비스, 백업은 그대로 유지됩니다.", "Ayarlar, hizmetler ve yedekler korunur.",
     "設定、サービス、バックアップはそのまま残ります。"),
    ("При следующем действии программа предложит установить помощник заново.",
     "Під час наступної дії програма запропонує встановити помічник знову.",
     "On your next action the app will offer to install the helper again.",
     "Lors de la prochaine action, l'application proposera de réinstaller l'assistant.",
     "En la siguiente acción, la aplicación ofrecerá instalar el asistente de nuevo.",
     "Na próxima ação, o aplicativo oferecerá instalar o auxiliar novamente.",
     "Bei der nächsten Aktion bietet die Anwendung an, den Helfer erneut zu installieren.",
     "Seuraavan toiminnon yhteydessä sovellus tarjoutuu asentamaan apuohjelman uudelleen.",
     "Pada tindakan berikutnya, aplikasi akan menawarkan untuk memasang helper lagi.",
     "下次执行操作时，程序会提示重新安装辅助程序。",
     "अगली कार्रवाई पर ऐप हेल्पर को फिर से इंस्टॉल करने का सुझाव देगा।",
     "다음 작업 시 앱이 도우미를 다시 설치하도록 안내합니다.",
     "Bir sonraki işlemde uygulama yardımcıyı yeniden kurmayı önerecektir.",
     "次の操作時に、ヘルパーの再インストールを案内します。"),
    ("Удалить", "Видалити", "Delete", "Supprimer", "Eliminar", "Excluir", "Löschen", "Poista", "Hapus",
     "删除", "हटाएँ", "삭제", "Sil", "削除"),
    ("Системный помощник и polkit-правило удалены", "Системний помічник і правило polkit видалено",
     "System helper and polkit rule removed", "Assistant système et règle polkit supprimés",
     "Asistente del sistema y regla de polkit eliminados", "Auxiliar do sistema e regra do polkit removidos",
     "Systemhelfer und polkit-Regel entfernt", "Järjestelmän apuohjelma ja polkit-sääntö poistettu",
     "Helper sistem dan aturan polkit dihapus", "已移除系统辅助程序和 polkit 规则",
     "सिस्टम हेल्पर और polkit नियम हटा दिए गए", "시스템 도우미와 polkit 규칙을 제거했습니다",
     "Sistem yardımcısı ve polkit kuralı kaldırıldı", "システムヘルパーと polkit ルールを削除しました"),
    ("Удаление помощника", "Видалення помічника", "Removing the helper", "Suppression de l'assistant",
     "Eliminación del asistente", "Remoção do auxiliar", "Entfernen des Helfers", "Apuohjelman poisto",
     "Penghapusan helper", "移除辅助程序", "हेल्पर हटाना", "도우미 제거", "Yardımcının kaldırılması",
     "ヘルパーの削除"),
 
    # ── установка помощника ──────────────────────────────────────────
    ("Одноразовая установка помощника", "Одноразове встановлення помічника", "One-time helper installation",
     "Installation unique de l'assistant", "Instalación única del asistente", "Instalação única do auxiliar",
     "Einmalige Installation des Helfers", "Apuohjelman kertaluonteinen asennus",
     "Pemasangan helper satu kali", "一次性安装辅助程序", "हेल्पर की एकबारगी स्थापना", "도우미 1회 설치",
     "Yardımcının tek seferlik kurulumu", "ヘルパーの初回インストール"),
    ("Установить", "Встановити", "Install", "Installer", "Instalar", "Instalar", "Installieren", "Asenna",
     "Pasang", "安装", "इंस्टॉल करें", "설치", "Kur", "インストール"),
    ("Чтобы менять системные настройки, PixelTweak один раз устанавливает небольшой системный помощник ({}) и правило polkit.",
     "Щоб змінювати системні налаштування, PixelTweak один раз встановлює невеликий системний помічник ({}) і правило polkit.",
     "To change system settings, PixelTweak installs a small system helper ({}) and a polkit rule, once.",
     "Pour modifier les réglages système, PixelTweak installe une seule fois un petit assistant système ({}) et une règle polkit.",
     "Para cambiar los ajustes del sistema, PixelTweak instala una sola vez un pequeño asistente del sistema ({}) y una regla de polkit.",
     "Para alterar as configurações do sistema, o PixelTweak instala uma única vez um pequeno auxiliar do sistema ({}) e uma regra do polkit.",
     "Um Systemeinstellungen zu ändern, installiert PixelTweak einmalig einen kleinen Systemhelfer ({}) und eine polkit-Regel.",
     "Järjestelmäasetusten muuttamiseksi PixelTweak asentaa kerran pienen järjestelmän apuohjelman ({}) ja polkit-säännön.",
     "Untuk mengubah pengaturan sistem, PixelTweak memasang sekali sebuah helper sistem kecil ({}) dan aturan polkit.",
     "为了更改系统设置，PixelTweak 会一次性安装一个小型系统辅助程序（{}）和一条 polkit 规则。",
     "सिस्टम सेटिंग्स बदलने के लिए PixelTweak एक बार एक छोटा सिस्टम हेल्पर ({}) और polkit नियम इंस्टॉल करता है।",
     "시스템 설정을 변경하기 위해 PixelTweak는 작은 시스템 도우미({})와 polkit 규칙을 한 번 설치합니다.",
     "Sistem ayarlarını değiştirmek için PixelTweak, küçük bir sistem yardımcısını ({}) ve bir polkit kuralını bir kez kurar.",
     "システム設定を変更するため、PixelTweak は小さなシステムヘルパー（{}）と polkit ルールを一度だけインストールします。"),
    ("Помощник умеет только заранее разрешённые операции (файлы настроек и несколько команд systemctl/sysctl).",
     "Помічник вміє виконувати лише заздалегідь дозволені операції (файли налаштувань і кілька команд systemctl/sysctl).",
     "The helper can only perform pre-approved operations (settings files and a few systemctl/sysctl commands).",
     "L'assistant ne peut effectuer que des opérations préalablement autorisées (fichiers de réglages et quelques commandes systemctl/sysctl).",
     "El asistente solo puede realizar operaciones permitidas de antemano (archivos de ajustes y algunos comandos systemctl/sysctl).",
     "O auxiliar só pode executar operações previamente permitidas (arquivos de configuração e alguns comandos systemctl/sysctl).",
     "Der Helfer beherrscht nur vorab erlaubte Operationen (Einstellungsdateien und einige systemctl/sysctl-Befehle).",
     "Apuohjelma osaa tehdä vain etukäteen sallittuja toimintoja (asetustiedostot ja muutama systemctl/sysctl-komento).",
     "Helper hanya dapat melakukan operasi yang telah diizinkan sebelumnya (berkas pengaturan dan beberapa perintah systemctl/sysctl).",
     "辅助程序只能执行预先允许的操作（设置文件和少数 systemctl/sysctl 命令）。",
     "हेल्पर केवल पहले से अनुमत कार्य कर सकता है (सेटिंग्स फ़ाइलें और कुछ systemctl/sysctl कमांड)।",
     "도우미는 미리 허용된 작업(설정 파일과 일부 systemctl/sysctl 명령)만 수행할 수 있습니다.",
     "Yardımcı yalnızca önceden izin verilen işlemleri yapabilir (ayar dosyaları ve birkaç systemctl/sysctl komutu).",
     "ヘルパーは、あらかじめ許可された操作（設定ファイルと一部の systemctl/sysctl コマンド）のみ実行できます。"),
    ("Сейчас система спросит пароль для установки — в этом окне будет упомянут python3, это нормально.",
     "Зараз система запитає пароль для встановлення — у цьому вікні буде згадано python3, це нормально.",
     "The system will now ask for your password to install it — this prompt will mention python3, which is normal.",
     "Le système va maintenant demander votre mot de passe pour l'installation — cette fenêtre mentionnera python3, c'est normal.",
     "Ahora el sistema pedirá su contraseña para instalarlo; en esa ventana aparecerá python3, es normal.",
     "Agora o sistema pedirá sua senha para instalar — nessa janela aparecerá python3, o que é normal.",
     "Das System fragt jetzt nach dem Passwort für die Installation – in diesem Fenster wird python3 erwähnt, das ist normal.",
     "Järjestelmä pyytää nyt salasanaa asennusta varten – tässä ikkunassa mainitaan python3, se on normaalia.",
     "Sistem akan meminta kata sandi untuk pemasangan — jendela ini akan menyebut python3, itu normal.",
     "系统现在会要求输入密码以进行安装——该窗口中会提到 python3，这是正常的。",
     "अब सिस्टम इंस्टॉल करने के लिए पासवर्ड माँगेगा — इस विंडो में python3 का उल्लेख होगा, यह सामान्य है।",
     "이제 시스템이 설치를 위한 비밀번호를 요청합니다. 이 창에는 python3가 표시되는데, 정상입니다.",
     "Sistem şimdi kurulum için parolanızı soracak — bu pencerede python3 geçecek, bu normaldir.",
     "これからシステムがインストール用のパスワードを求めます。このウィンドウには python3 と表示されますが、問題ありません。"),
    ("Дальше окно пароля будет называться «PixelTweak хочет изменить настройки производительности».",
     "Далі вікно пароля називатиметься «PixelTweak хоче змінити налаштування продуктивності».",
     "After that, the password prompt will read “PixelTweak wants to change system performance settings”.",
     "Ensuite, la fenêtre de mot de passe s'intitulera « PixelTweak souhaite modifier les réglages de performances ».",
     "Después, la ventana de contraseña mostrará «PixelTweak quiere cambiar los ajustes de rendimiento».",
     "Depois disso, a janela de senha exibirá «O PixelTweak quer alterar as configurações de desempenho».",
     "Danach lautet der Passwortdialog „PixelTweak möchte die Leistungseinstellungen ändern“.",
     "Jatkossa salasanaikkunan otsikkona on ”PixelTweak haluaa muuttaa suorituskykyasetuksia”.",
     "Selanjutnya, jendela kata sandi akan berjudul «PixelTweak ingin mengubah pengaturan kinerja».",
     "之后密码窗口将显示为「PixelTweak 想要更改性能设置」。",
     "इसके बाद पासवर्ड विंडो का शीर्षक होगा «PixelTweak प्रदर्शन सेटिंग्स बदलना चाहता है»।",
     "이후 비밀번호 창에는 「PixelTweak이(가) 성능 설정을 변경하려고 합니다」라고 표시됩니다.",
     "Bundan sonra parola penceresinde «PixelTweak performans ayarlarını değiştirmek istiyor» yazacak.",
     "以降、パスワード画面には「PixelTweak がパフォーマンス設定の変更を求めています」と表示されます。"),
    ("Помощник установлен", "Помічник встановлено", "Helper installed", "Assistant installé",
     "Asistente instalado", "Auxiliar instalado", "Helfer installiert", "Apuohjelma asennettu",
     "Helper terpasang", "辅助程序已安装", "हेल्पर इंस्टॉल हो गया", "도우미가 설치되었습니다",
     "Yardımcı kuruldu", "ヘルパーをインストールしました"),
    ("Установка отменена", "Встановлення скасовано", "Installation cancelled", "Installation annulée",
     "Instalación cancelada", "Instalação cancelada", "Installation abgebrochen", "Asennus peruttu",
     "Pemasangan dibatalkan", "安装已取消", "इंस्टॉलेशन रद्द किया गया", "설치가 취소되었습니다",
     "Kurulum iptal edildi", "インストールをキャンセルしました"),
    ("Не удалось установить помощник: {}", "Не вдалося встановити помічник: {}",
     "Could not install the helper: {}", "Impossible d'installer l'assistant : {}",
     "No se pudo instalar el asistente: {}", "Não foi possível instalar o auxiliar: {}",
     "Helfer konnte nicht installiert werden: {}", "Apuohjelman asennus epäonnistui: {}",
     "Gagal memasang helper: {}", "无法安装辅助程序：{}", "हेल्पर इंस्टॉल नहीं हो सका: {}",
     "도우미를 설치하지 못했습니다: {}", "Yardımcı kurulamadı: {}", "ヘルパーをインストールできませんでした: {}"),
    ("Установка помощника: {}", "Встановлення помічника: {}", "Helper installation: {}",
     "Installation de l'assistant : {}", "Instalación del asistente: {}", "Instalação do auxiliar: {}",
     "Installation des Helfers: {}", "Apuohjelman asennus: {}", "Pemasangan helper: {}", "安装辅助程序：{}",
     "हेल्पर इंस्टॉलेशन: {}", "도우미 설치: {}", "Yardımcı kurulumu: {}", "ヘルパーのインストール: {}"),
    ("Подождите: другая операция ещё выполняется", "Зачекайте: інша операція ще виконується",
     "Please wait: another operation is still running", "Veuillez patienter : une autre opération est en cours",
     "Espere: otra operación sigue en curso", "Aguarde: outra operação ainda está em andamento",
     "Bitte warten: Ein anderer Vorgang läuft noch", "Odota: toinen toiminto on vielä käynnissä",
     "Harap tunggu: operasi lain masih berjalan", "请稍候：另一项操作仍在进行",
     "कृपया प्रतीक्षा करें: दूसरी प्रक्रिया अभी चल रही है", "잠시 기다려 주세요: 다른 작업이 아직 진행 중입니다",
     "Lütfen bekleyin: başka bir işlem hâlâ sürüyor", "お待ちください: 別の処理が実行中です"),
    ("Запрос отменён. Если пароль уже был введён, часть шагов могла выполниться — см. журнал",
     "Запит скасовано. Якщо пароль уже було введено, частина кроків могла виконатися — див. журнал",
     "Request cancelled. If the password was already entered, some steps may have run — see the log",
     "Demande annulée. Si le mot de passe a déjà été saisi, certaines étapes ont pu s'exécuter — voir le journal",
     "Solicitud cancelada. Si ya se introdujo la contraseña, es posible que se hayan ejecutado algunos pasos; consulte el registro",
     "Solicitação cancelada. Se a senha já foi digitada, algumas etapas podem ter sido executadas — veja o registro",
     "Anfrage abgebrochen. Wurde das Passwort bereits eingegeben, wurden eventuell einige Schritte ausgeführt – siehe Protokoll",
     "Pyyntö peruttu. Jos salasana ehdittiin jo antaa, osa vaiheista on voinut suorittua – katso loki",
     "Permintaan dibatalkan. Jika kata sandi sudah dimasukkan, sebagian langkah mungkin telah dijalankan — lihat log",
     "请求已取消。如果密码已输入，部分步骤可能已执行——请查看日志",
     "अनुरोध रद्द किया गया। यदि पासवर्ड पहले ही दर्ज हो चुका था, तो कुछ चरण पूरे हो चुके हो सकते हैं — लॉग देखें",
     "요청이 취소되었습니다. 비밀번호를 이미 입력했다면 일부 단계가 실행되었을 수 있습니다 — 로그를 확인하세요",
     "İstek iptal edildi. Parola zaten girildiyse bazı adımlar çalışmış olabilir — günlüğe bakın",
     "リクエストを取り消しました。パスワード入力済みの場合、一部の手順が実行された可能性があります — ログを確認してください"),
    ("отменено (пароль не введён)", "скасовано (пароль не введено)", "cancelled (password not entered)",
     "annulé (mot de passe non saisi)", "cancelado (contraseña no introducida)",
     "cancelado (senha não digitada)", "abgebrochen (Passwort nicht eingegeben)",
     "peruttu (salasanaa ei annettu)", "dibatalkan (kata sandi tidak dimasukkan)", "已取消（未输入密码）",
     "रद्द (पासवर्ड दर्ज नहीं किया गया)", "취소됨(비밀번호 미입력)", "iptal edildi (parola girilmedi)",
     "キャンセルされました（パスワード未入力）"),
    ("неизвестная ошибка", "невідома помилка", "unknown error", "erreur inconnue", "error desconocido",
     "erro desconhecido", "unbekannter Fehler", "tuntematon virhe", "kesalahan tidak diketahui", "未知错误",
     "अज्ञात त्रुटि", "알 수 없는 오류", "bilinmeyen hata", "不明なエラー"),
    ("выполнено {} из {}", "виконано {} з {}", "completed {} of {}", "{} sur {} effectués",
     "completados {} de {}", "concluídos {} de {}", "{} von {} ausgeführt", "suoritettu {} / {}",
     "selesai {} dari {}", "已完成 {}/{}", "{}/{} पूरे", "{}/{} 완료", "{}/{} tamamlandı", "{}/{} 完了"),
    ("не удалось: {}", "не вдалося: {}", "failed: {}", "échec : {}", "falló: {}", "falhou: {}",
     "fehlgeschlagen: {}", "epäonnistui: {}", "gagal: {}", "失败：{}", "विफल: {}", "실패: {}",
     "başarısız: {}", "失敗: {}"),
    ("pkexec не найден", "pkexec не знайдено", "pkexec not found", "pkexec introuvable",
     "pkexec no encontrado", "pkexec não encontrado", "pkexec nicht gefunden", "pkexec ei löytynyt",
     "pkexec tidak ditemukan", "未找到 pkexec", "pkexec नहीं मिला", "pkexec를 찾을 수 없습니다",
     "pkexec bulunamadı", "pkexec が見つかりません"),
    ("откат", "відкат", "rollback", "restauration", "reversión", "reversão", "Zurücksetzen", "palautus",
     "pengembalian", "回滚", "वापसी", "되돌리기", "geri alma", "元に戻す"),
    ("сброс", "скидання", "reset", "réinitialisation", "restablecimiento", "redefinição", "Zurücksetzen",
     "nollaus", "penyetelan ulang", "重置", "रीसेट", "초기화", "sıfırlama", "リセット"),
    ("удаление", "видалення", "removal", "suppression", "eliminación", "remoção", "Entfernen", "poisto",
     "penghapusan", "删除", "हटाना", "삭제", "kaldırma", "削除"),
    ("Сначала", "Спочатку", "First", "D'abord", "Primero", "Primeiro", "Zuerst", "Ensin", "Pertama", "请先",
     "पहले", "먼저", "Önce", "まず"),
    ("{}: откат выполнен (перезапустите PixelTweak, чтобы обновить поля)",
     "{}: відкат виконано (перезапустіть PixelTweak, щоб оновити поля)",
     "{}: rolled back (restart PixelTweak to refresh the fields)",
     "{} : restauration effectuée (redémarrez PixelTweak pour actualiser les champs)",
     "{}: reversión realizada (reinicie PixelTweak para actualizar los campos)",
     "{}: reversão feita (reinicie o PixelTweak para atualizar os campos)",
     "{}: Zurücksetzen durchgeführt (PixelTweak neu starten, um die Felder zu aktualisieren)",
     "{}: palautus tehty (käynnistä PixelTweak uudelleen päivittääksesi kentät)",
     "{}: pengembalian selesai (mulai ulang PixelTweak untuk menyegarkan kolom)",
     "{}：已回滚（重启 PixelTweak 以刷新字段）",
     "{}: वापसी हो गई (फ़ील्ड अपडेट करने के लिए PixelTweak फिर से चलाएँ)",
     "{}: 되돌리기 완료(입력란을 갱신하려면 PixelTweak를 다시 시작하세요)",
     "{}: geri alındı (alanları yenilemek için PixelTweak'i yeniden başlatın)",
     "{}: 元に戻しました（入力欄を更新するには PixelTweak を再起動してください）"),
 
    # ── ZRAM ─────────────────────────────────────────────────────────
    ("ZRAM-генератор", "ZRAM-генератор", "ZRAM generator", "Générateur ZRAM", "Generador de ZRAM",
     "Gerador de ZRAM", "ZRAM-Generator", "ZRAM-generaattori", "Generator ZRAM", "ZRAM 生成器",
     "ZRAM जनरेटर", "ZRAM 생성기", "ZRAM üretici", "ZRAM ジェネレーター"),
    ("Размер в MiB (например: ram / 2 или 4096)", "Розмір у MiB (наприклад: ram / 2 або 4096)",
     "Size in MiB (for example: ram / 2 or 4096)", "Taille en MiB (par ex. : ram / 2 ou 4096)",
     "Tamaño en MiB (por ejemplo: ram / 2 o 4096)", "Tamanho em MiB (por exemplo: ram / 2 ou 4096)",
     "Größe in MiB (z. B.: ram / 2 oder 4096)", "Koko MiB:nä (esim. ram / 2 tai 4096)",
     "Ukuran dalam MiB (mis.: ram / 2 atau 4096)", "大小（MiB，例如：ram / 2 或 4096）",
     "आकार MiB में (उदा.: ram / 2 या 4096)", "크기(MiB, 예: ram / 2 또는 4096)",
     "MiB cinsinden boyut (örn. ram / 2 veya 4096)", "サイズ（MiB、例: ram / 2 または 4096）"),
    ("Алгоритм сжатия (из ядра)", "Алгоритм стиснення (з ядра)", "Compression algorithm (from the kernel)",
     "Algorithme de compression (du noyau)", "Algoritmo de compresión (del kernel)",
     "Algoritmo de compressão (do kernel)", "Kompressionsalgorithmus (vom Kernel)",
     "Pakkausalgoritmi (ytimestä)", "Algoritma kompresi (dari kernel)", "压缩算法（来自内核）",
     "संपीड़न एल्गोरिदम (कर्नेल से)", "압축 알고리즘(커널 제공)", "Sıkıştırma algoritması (çekirdekten)",
     "圧縮アルゴリズム（カーネルから）"),
    ("Swap активен", "Swap активний", "Swap active", "Swap actif", "Swap activo", "Swap ativo", "Swap aktiv",
     "Swap aktiivinen", "Swap aktif", "Swap 已启用", "Swap सक्रिय", "Swap 활성", "Swap etkin", "Swap 有効"),
    ("занято {} MB", "зайнято {} MB", "in use: {} MB", "utilisé : {} MB", "en uso: {} MB", "em uso: {} MB",
     "belegt: {} MB", "käytössä: {} MB", "terpakai: {} MB", "已用 {} MB", "उपयोग में: {} MB", "사용 중: {} MB",
     "kullanımda: {} MB", "使用中: {} MB"),
    ("управляется не zram-generator (настройки ниже не повлияют)",
     "керується не zram-generator (налаштування нижче не подіють)",
     "not managed by zram-generator (settings below will have no effect)",
     "non géré par zram-generator (les réglages ci-dessous sont sans effet)",
     "no lo gestiona zram-generator (los ajustes de abajo no tendrán efecto)",
     "não é gerenciado pelo zram-generator (as configurações abaixo não terão efeito)",
     "nicht von zram-generator verwaltet (die Einstellungen unten haben keine Wirkung)",
     "ei zram-generatorin hallinnassa (alla olevat asetukset eivät vaikuta)",
     "tidak dikelola oleh zram-generator (pengaturan di bawah tidak berpengaruh)",
     "并非由 zram-generator 管理（下方设置不会生效）",
     "zram-generator द्वारा प्रबंधित नहीं (नीचे की सेटिंग्स का असर नहीं होगा)",
     "zram-generator가 관리하지 않음(아래 설정은 적용되지 않음)",
     "zram-generator tarafından yönetilmiyor (aşağıdaki ayarlar etkili olmaz)",
     "zram-generator の管理外（下の設定は反映されません）"),
    ("Устройство zram0 есть, но swap не включён", "Пристрій zram0 є, але swap не ввімкнено",
     "The zram0 device exists, but swap is not enabled",
     "Le périphérique zram0 existe, mais le swap n'est pas activé",
     "El dispositivo zram0 existe, pero el swap no está activado",
     "O dispositivo zram0 existe, mas o swap não está ativado",
     "Das Gerät zram0 ist vorhanden, aber Swap ist nicht aktiviert",
     "zram0-laite on olemassa, mutta swap ei ole käytössä",
     "Perangkat zram0 ada, tetapi swap tidak diaktifkan", "存在 zram0 设备，但未启用 swap",
     "zram0 डिवाइस मौजूद है, लेकिन swap चालू नहीं है", "zram0 장치는 있지만 swap이 켜져 있지 않습니다",
     "zram0 aygıtı var, ancak swap etkin değil", "zram0 デバイスはありますが、swap は有効ではありません"),
    ("ZRAM не активен", "ZRAM не активний", "ZRAM is not active", "ZRAM inactif", "ZRAM no está activo",
     "ZRAM não está ativo", "ZRAM ist nicht aktiv", "ZRAM ei ole aktiivinen", "ZRAM tidak aktif",
     "ZRAM 未启用", "ZRAM सक्रिय नहीं है", "ZRAM이 활성화되어 있지 않습니다", "ZRAM etkin değil",
     "ZRAM は無効です"),
    ("не установлен systemd-zram-generator", "systemd-zram-generator не встановлено",
     "systemd-zram-generator is not installed", "systemd-zram-generator n'est pas installé",
     "systemd-zram-generator no está instalado", "systemd-zram-generator não está instalado",
     "systemd-zram-generator ist nicht installiert", "systemd-zram-generator ei ole asennettu",
     "systemd-zram-generator belum terpasang", "未安装 systemd-zram-generator",
     "systemd-zram-generator इंस्टॉल नहीं है", "systemd-zram-generator가 설치되어 있지 않습니다",
     "systemd-zram-generator kurulu değil", "systemd-zram-generator がインストールされていません"),
    ("ZRAM: неверный размер — {}", "ZRAM: неправильний розмір — {}", "ZRAM: invalid size — {}",
     "ZRAM : taille invalide — {}", "ZRAM: tamaño no válido — {}", "ZRAM: tamanho inválido — {}",
     "ZRAM: ungültige Größe — {}", "ZRAM: virheellinen koko — {}", "ZRAM: ukuran tidak valid — {}",
     "ZRAM：大小无效 — {}", "ZRAM: अमान्य आकार — {}", "ZRAM: 잘못된 크기 — {}", "ZRAM: geçersiz boyut — {}",
     "ZRAM: サイズが不正です — {}"),
    ("ZRAM: {} MiB вне разумных пределов (64 MiB … 4×RAM)",
     "ZRAM: {} MiB поза розумними межами (64 MiB … 4×RAM)",
     "ZRAM: {} MiB is outside reasonable limits (64 MiB … 4×RAM)",
     "ZRAM : {} MiB hors des limites raisonnables (64 MiB … 4×RAM)",
     "ZRAM: {} MiB está fuera de los límites razonables (64 MiB … 4×RAM)",
     "ZRAM: {} MiB está fora dos limites razoáveis (64 MiB … 4×RAM)",
     "ZRAM: {} MiB liegt außerhalb sinnvoller Grenzen (64 MiB … 4×RAM)",
     "ZRAM: {} MiB on kohtuullisten rajojen ulkopuolella (64 MiB … 4×RAM)",
     "ZRAM: {} MiB di luar batas wajar (64 MiB … 4×RAM)",
     "ZRAM：{} MiB 超出合理范围（64 MiB … 4×RAM）",
     "ZRAM: {} MiB उचित सीमा से बाहर है (64 MiB … 4×RAM)",
     "ZRAM: {} MiB은(는) 합리적인 범위를 벗어났습니다(64 MiB … 4×RAM)",
     "ZRAM: {} MiB makul sınırların dışında (64 MiB … 4×RAM)",
     "ZRAM: {} MiB は妥当な範囲外です（64 MiB … 4×RAM）"),
    ("ZRAM: сохранено, применится после перезагрузки", "ZRAM: збережено, застосується після перезавантаження",
     "ZRAM: saved, will apply after reboot", "ZRAM : enregistré, sera appliqué après le redémarrage",
     "ZRAM: guardado, se aplicará tras reiniciar", "ZRAM: salvo, será aplicado após reiniciar",
     "ZRAM: gespeichert, wird nach dem Neustart angewendet",
     "ZRAM: tallennettu, otetaan käyttöön uudelleenkäynnistyksen jälkeen",
     "ZRAM: tersimpan, akan diterapkan setelah reboot", "ZRAM：已保存，重启后生效",
     "ZRAM: सहेजा गया, रीबूट के बाद लागू होगा", "ZRAM: 저장됨, 재부팅 후 적용됩니다",
     "ZRAM: kaydedildi, yeniden başlatmadan sonra uygulanacak", "ZRAM: 保存しました。再起動後に適用されます"),
    ("ZRAM: применено ({} MiB, {})", "ZRAM: застосовано ({} MiB, {})", "ZRAM: applied ({} MiB, {})",
     "ZRAM : appliqué ({} MiB, {})", "ZRAM: aplicado ({} MiB, {})", "ZRAM: aplicado ({} MiB, {})",
     "ZRAM: angewendet ({} MiB, {})", "ZRAM: otettu käyttöön ({} MiB, {})", "ZRAM: diterapkan ({} MiB, {})",
     "ZRAM：已应用（{} MiB，{}）", "ZRAM: लागू किया गया ({} MiB, {})", "ZRAM: 적용됨({} MiB, {})",
     "ZRAM: uygulandı ({} MiB, {})", "ZRAM: 適用しました（{} MiB、{}）"),
    ("Перезапустить ZRAM?", "Перезапустити ZRAM?", "Restart ZRAM?", "Redémarrer ZRAM ?", "¿Reiniciar ZRAM?",
     "Reiniciar o ZRAM?", "ZRAM neu starten?", "Käynnistetäänkö ZRAM uudelleen?", "Mulai ulang ZRAM?",
     "要重启 ZRAM 吗？", "ZRAM पुनः चालू करें?", "ZRAM을 다시 시작할까요?", "ZRAM yeniden başlatılsın mı?",
     "ZRAM を再起動しますか？"),
    ("Сейчас в ZRAM занято {} MB, свободно RAM ≈ {} MB.",
     "Зараз у ZRAM зайнято {} MB, вільної RAM ≈ {} MB.",
     "Currently {} MB is used in ZRAM; free RAM is ≈ {} MB.",
     "Actuellement, {} MB sont utilisés dans ZRAM ; RAM libre ≈ {} MB.",
     "Ahora hay {} MB en uso en ZRAM; RAM libre ≈ {} MB.",
     "Agora há {} MB em uso no ZRAM; RAM livre ≈ {} MB.",
     "Derzeit sind {} MB in ZRAM belegt, freier RAM ≈ {} MB.",
     "ZRAMissa on tällä hetkellä käytössä {} MB, vapaata RAMia ≈ {} MB.",
     "Saat ini ZRAM terpakai {} MB, RAM bebas ≈ {} MB.",
     "ZRAM 当前已用 {} MB，可用 RAM ≈ {} MB。",
     "अभी ZRAM में {} MB उपयोग में है, खाली RAM ≈ {} MB है।",
     "현재 ZRAM 사용량은 {} MB, 여유 RAM은 약 {} MB입니다.",
     "Şu anda ZRAM'de {} MB kullanımda, boş RAM ≈ {} MB.",
     "現在 ZRAM は {} MB 使用中で、空き RAM は約 {} MB です。"),
    ("Для применения ZRAM-swap временно отключается: данные из него возвращаются в память.",
     "Для застосування ZRAM-swap тимчасово вимикається: дані з нього повертаються в пам'ять.",
     "To apply the change, ZRAM swap is temporarily turned off: its data is moved back into memory.",
     "Pour appliquer le changement, le swap ZRAM est temporairement désactivé : ses données retournent en mémoire.",
     "Para aplicar el cambio, el swap de ZRAM se desactiva temporalmente: sus datos vuelven a la memoria.",
     "Para aplicar a alteração, o swap do ZRAM é desativado temporariamente: seus dados voltam para a memória.",
     "Zum Anwenden wird der ZRAM-Swap vorübergehend deaktiviert: Seine Daten werden zurück in den Speicher verschoben.",
     "Käyttöönottoa varten ZRAM-swap poistetaan hetkeksi käytöstä: sen data siirretään takaisin muistiin.",
     "Untuk menerapkan perubahan, swap ZRAM dinonaktifkan sementara: datanya dikembalikan ke memori.",
     "应用时会暂时停用 ZRAM swap：其中的数据会回到内存。",
     "लागू करने के लिए ZRAM swap अस्थायी रूप से बंद किया जाता है: उसका डेटा वापस मेमोरी में चला जाता है।",
     "적용하려면 ZRAM swap을 일시적으로 끕니다. 그 안의 데이터는 메모리로 되돌아갑니다.",
     "Uygulamak için ZRAM swap geçici olarak kapatılır: içindeki veriler belleğe geri döner.",
     "適用のため ZRAM swap を一時的に無効にします。その中のデータはメモリに戻されます。"),
    ("Памяти достаточно — можно применить сейчас.", "Пам'яті достатньо — можна застосувати зараз.",
     "There is enough memory — you can apply it now.",
     "La mémoire est suffisante — vous pouvez l'appliquer maintenant.",
     "Hay memoria suficiente: puede aplicarlo ahora.", "Há memória suficiente — você pode aplicar agora.",
     "Der Speicher reicht aus – Sie können jetzt anwenden.",
     "Muistia on riittävästi – voit ottaa muutoksen käyttöön heti.",
     "Memori cukup — bisa diterapkan sekarang.", "内存充足——可以立即应用。",
     "मेमोरी पर्याप्त है — अभी लागू किया जा सकता है।", "메모리가 충분하므로 지금 적용할 수 있습니다.",
     "Bellek yeterli — şimdi uygulayabilirsiniz.", "メモリは十分です。今すぐ適用できます。"),
    ("Свободной RAM не хватает для безопасного перезапуска (нужно ≈ {} MB), иначе система может убить процессы.",
     "Вільної RAM не вистачає для безпечного перезапуску (потрібно ≈ {} MB), інакше система може вбити процеси.",
     "There isn't enough free RAM for a safe restart (≈ {} MB needed); otherwise the system may kill processes.",
     "Pas assez de RAM libre pour un redémarrage sûr (≈ {} MB nécessaires), sinon le système risque de tuer des processus.",
     "No hay suficiente RAM libre para reiniciar con seguridad (se necesitan ≈ {} MB); de lo contrario el sistema podría matar procesos.",
     "Não há RAM livre suficiente para reiniciar com segurança (necessário ≈ {} MB); caso contrário o sistema pode encerrar processos.",
     "Nicht genug freier RAM für einen sicheren Neustart (≈ {} MB nötig), sonst könnte das System Prozesse beenden.",
     "Vapaata RAMia ei riitä turvalliseen uudelleenkäynnistykseen (tarvitaan ≈ {} MB), muuten järjestelmä voi tappaa prosesseja.",
     "RAM bebas tidak cukup untuk memulai ulang dengan aman (perlu ≈ {} MB); jika tidak, sistem bisa menghentikan proses.",
     "可用 RAM 不足以安全重启（需要约 {} MB），否则系统可能会终止进程。",
     "सुरक्षित पुनः आरंभ के लिए खाली RAM पर्याप्त नहीं है (≈ {} MB चाहिए), वरना सिस्टम प्रक्रियाएँ बंद कर सकता है।",
     "안전하게 다시 시작하기에 여유 RAM이 부족합니다(약 {} MB 필요). 그렇지 않으면 시스템이 프로세스를 종료할 수 있습니다.",
     "Güvenli yeniden başlatma için boş RAM yetersiz (≈ {} MB gerekli), aksi halde sistem işlemleri sonlandırabilir.",
     "安全に再起動するには空き RAM が足りません（約 {} MB が必要です）。足りないと、システムがプロセスを強制終了する可能性があります。"),
    ("Настройка применится после перезагрузки.", "Налаштування застосується після перезавантаження.",
     "The setting will apply after a reboot.", "Le réglage sera appliqué après le redémarrage.",
     "El ajuste se aplicará tras reiniciar.", "A configuração será aplicada após reiniciar.",
     "Die Einstellung wird nach dem Neustart angewendet.",
     "Asetus otetaan käyttöön uudelleenkäynnistyksen jälkeen.",
     "Pengaturan akan diterapkan setelah reboot.", "该设置将在重启后生效。",
     "सेटिंग रीबूट के बाद लागू होगी।", "설정은 재부팅 후 적용됩니다.",
     "Ayar yeniden başlatmadan sonra uygulanacak.", "設定は再起動後に適用されます。"),
    ("Только сохранить", "Лише зберегти", "Save only", "Enregistrer seulement", "Solo guardar",
     "Apenas salvar", "Nur speichern", "Vain tallenna", "Simpan saja", "仅保存", "केवल सहेजें", "저장만",
     "Yalnızca kaydet", "保存のみ"),
    ("Применить сейчас", "Застосувати зараз", "Apply now", "Appliquer maintenant", "Aplicar ahora",
     "Aplicar agora", "Jetzt anwenden", "Käytä nyt", "Terapkan sekarang", "立即应用", "अभी लागू करें",
     "지금 적용", "Şimdi uygula", "今すぐ適用"),
    ("ZRAM: откат выполнен и применён", "ZRAM: відкат виконано та застосовано",
     "ZRAM: rolled back and applied", "ZRAM : restauration effectuée et appliquée",
     "ZRAM: reversión realizada y aplicada", "ZRAM: reversão feita e aplicada",
     "ZRAM: Zurücksetzen durchgeführt und angewendet", "ZRAM: palautus tehty ja otettu käyttöön",
     "ZRAM: pengembalian selesai dan diterapkan", "ZRAM：已回滚并应用",
     "ZRAM: वापसी हो गई और लागू की गई", "ZRAM: 되돌리기 완료 및 적용됨", "ZRAM: geri alındı ve uygulandı",
     "ZRAM: 元に戻して適用しました"),
    ("ZRAM: конфиг откачен, размер обновится после перезагрузки (мало свободной RAM)",
     "ZRAM: конфіг відкочено, розмір оновиться після перезавантаження (мало вільної RAM)",
     "ZRAM: config rolled back, size will update after reboot (low free RAM)",
     "ZRAM : configuration restaurée, la taille sera mise à jour après le redémarrage (peu de RAM libre)",
     "ZRAM: configuración revertida, el tamaño se actualizará tras reiniciar (poca RAM libre)",
     "ZRAM: configuração revertida, o tamanho será atualizado após reiniciar (pouca RAM livre)",
     "ZRAM: Konfiguration zurückgesetzt, Größe wird nach dem Neustart aktualisiert (wenig freier RAM)",
     "ZRAM: asetukset palautettu, koko päivittyy uudelleenkäynnistyksen jälkeen (vähän vapaata RAMia)",
     "ZRAM: konfigurasi dikembalikan, ukuran diperbarui setelah reboot (RAM bebas sedikit)",
     "ZRAM：配置已回滚，大小将在重启后更新（可用 RAM 不足）",
     "ZRAM: कॉन्फ़िग वापस लाई गई, आकार रीबूट के बाद अपडेट होगा (खाली RAM कम है)",
     "ZRAM: 설정을 되돌렸으며 크기는 재부팅 후 갱신됩니다(여유 RAM 부족)",
     "ZRAM: yapılandırma geri alındı, boyut yeniden başlatmadan sonra güncellenecek (boş RAM az)",
     "ZRAM: 設定を元に戻しました。サイズは再起動後に更新されます（空き RAM が少ないため）"),
 
    # ── ядро (sysctl) ────────────────────────────────────────────────
    ("Ядро", "Ядро", "Kernel", "Noyau", "Kernel", "Kernel", "Kernel", "Ydin", "Kernel", "内核", "कर्नेल",
     "커널", "Çekirdek", "カーネル"),
    ("Параметры vm.*", "Параметри vm.*", "vm.* parameters", "Paramètres vm.*", "Parámetros vm.*",
     "Parâmetros vm.*", "vm.*-Parameter", "vm.*-parametrit", "Parameter vm.*", "vm.* 参数", "vm.* पैरामीटर",
     "vm.* 매개변수", "vm.* parametreleri", "vm.* パラメーター"),
    ("в файл попадают только изменённые параметры", "у файл потрапляють лише змінені параметри",
     "only changed parameters are written to the file",
     "seuls les paramètres modifiés sont écrits dans le fichier",
     "solo se escriben en el archivo los parámetros modificados",
     "apenas os parâmetros alterados são gravados no arquivo",
     "nur geänderte Parameter werden in die Datei geschrieben",
     "tiedostoon kirjoitetaan vain muutetut parametrit",
     "hanya parameter yang diubah yang ditulis ke berkas", "仅将修改过的参数写入文件",
     "फ़ाइल में केवल बदले गए पैरामीटर लिखे जाते हैं", "변경된 매개변수만 파일에 기록됩니다",
     "dosyaya yalnızca değiştirilen parametreler yazılır", "変更したパラメーターのみがファイルに書き込まれます"),
    ("в ядре сейчас: {}", "у ядрі зараз: {}", "in kernel now: {}", "dans le noyau actuellement : {}",
     "en el kernel ahora: {}", "no kernel agora: {}", "im Kernel derzeit: {}", "ytimessä nyt: {}",
     "di kernel saat ini: {}", "内核当前值：{}", "कर्नेल में अभी: {}", "현재 커널 값: {}",
     "çekirdekte şu an: {}", "カーネルの現在値: {}"),
    ("задано PixelTweak", "задано PixelTweak", "set by PixelTweak", "défini par PixelTweak",
     "definido por PixelTweak", "definido pelo PixelTweak", "von PixelTweak gesetzt",
     "PixelTweakin asettama", "diatur oleh PixelTweak", "由 PixelTweak 设置", "PixelTweak द्वारा सेट",
     "PixelTweak에서 설정됨", "PixelTweak tarafından ayarlandı", "PixelTweak が設定"),
    ("Применить параметры ядра", "Застосувати параметри ядра", "Apply kernel parameters",
     "Appliquer les paramètres du noyau", "Aplicar parámetros del kernel", "Aplicar parâmetros do kernel",
     "Kernel-Parameter anwenden", "Käytä ytimen parametrit", "Terapkan parameter kernel", "应用内核参数",
     "कर्नेल पैरामीटर लागू करें", "커널 매개변수 적용", "Çekirdek parametrelerini uygula",
     "カーネルパラメーターを適用"),
    ("Ядро: нечего применять — значения совпадают с текущими",
     "Ядро: нічого застосовувати — значення збігаються з поточними",
     "Kernel: nothing to apply — values match the current ones",
     "Noyau : rien à appliquer — les valeurs correspondent aux valeurs actuelles",
     "Kernel: nada que aplicar: los valores coinciden con los actuales",
     "Kernel: nada a aplicar — os valores coincidem com os atuais",
     "Kernel: Nichts anzuwenden – die Werte entsprechen den aktuellen",
     "Ydin: ei mitään otettavaa käyttöön – arvot vastaavat nykyisiä",
     "Kernel: tidak ada yang diterapkan — nilai sama dengan yang sekarang",
     "内核：无需应用——数值与当前相同",
     "कर्नेल: लागू करने के लिए कुछ नहीं — मान वर्तमान मानों जैसे ही हैं",
     "커널: 적용할 것이 없습니다 — 값이 현재와 같습니다",
     "Çekirdek: uygulanacak bir şey yok — değerler mevcutlarla aynı",
     "カーネル: 適用するものはありません — 値は現在と同じです"),
    ("Ядро: dirty_background_ratio не может быть больше dirty_ratio",
     "Ядро: dirty_background_ratio не може бути більшим за dirty_ratio",
     "Kernel: dirty_background_ratio cannot be greater than dirty_ratio",
     "Noyau : dirty_background_ratio ne peut pas dépasser dirty_ratio",
     "Kernel: dirty_background_ratio no puede ser mayor que dirty_ratio",
     "Kernel: dirty_background_ratio não pode ser maior que dirty_ratio",
     "Kernel: dirty_background_ratio darf nicht größer als dirty_ratio sein",
     "Ydin: dirty_background_ratio ei voi olla suurempi kuin dirty_ratio",
     "Kernel: dirty_background_ratio tidak boleh lebih besar dari dirty_ratio",
     "内核：dirty_background_ratio 不能大于 dirty_ratio",
     "कर्नेल: dirty_background_ratio, dirty_ratio से बड़ा नहीं हो सकता",
     "커널: dirty_background_ratio는 dirty_ratio보다 클 수 없습니다",
     "Çekirdek: dirty_background_ratio, dirty_ratio'dan büyük olamaz",
     "カーネル: dirty_background_ratio は dirty_ratio より大きくできません"),
    ("Ядро: применено ({} парам.)", "Ядро: застосовано ({} парам.)", "Kernel: applied ({} params)",
     "Noyau : appliqué ({} param.)", "Kernel: aplicado ({} parám.)", "Kernel: aplicado ({} parâm.)",
     "Kernel: angewendet ({} Param.)", "Ydin: otettu käyttöön ({} param.)", "Kernel: diterapkan ({} param.)",
     "内核：已应用（{} 个参数）", "कर्नेल: लागू किया गया ({} पैरामीटर)", "커널: 적용됨({}개 매개변수)",
     "Çekirdek: uygulandı ({} parametre)", "カーネル: 適用しました（{} 個）"),
 
    # ── EarlyOOM ─────────────────────────────────────────────────────
    ("Защита от OOM", "Захист від OOM", "OOM protection", "Protection contre l'OOM", "Protección contra OOM",
     "Proteção contra OOM", "OOM-Schutz", "OOM-suojaus", "Perlindungan OOM", "OOM 保护", "OOM सुरक्षा",
     "OOM 보호", "OOM koruması", "OOM 保護"),
    ("earlyoom не установлен (sudo apt install earlyoom)", "earlyoom не встановлено (sudo apt install earlyoom)",
     "earlyoom is not installed (sudo apt install earlyoom)",
     "earlyoom n'est pas installé (sudo apt install earlyoom)",
     "earlyoom no está instalado (sudo apt install earlyoom)",
     "earlyoom não está instalado (sudo apt install earlyoom)",
     "earlyoom ist nicht installiert (sudo apt install earlyoom)",
     "earlyoomia ei ole asennettu (sudo apt install earlyoom)",
     "earlyoom belum terpasang (sudo apt install earlyoom)", "未安装 earlyoom（sudo apt install earlyoom）",
     "earlyoom इंस्टॉल नहीं है (sudo apt install earlyoom)",
     "earlyoom이 설치되어 있지 않습니다(sudo apt install earlyoom)",
     "earlyoom kurulu değil (sudo apt install earlyoom)",
     "earlyoom がインストールされていません（sudo apt install earlyoom）"),
    ("Служба активна", "Служба активна", "Service active", "Service actif", "Servicio activo",
     "Serviço ativo", "Dienst aktiv", "Palvelu aktiivinen", "Layanan aktif", "服务运行中", "सेवा सक्रिय",
     "서비스 실행 중", "Hizmet etkin", "サービス稼働中"),
    ("Служба остановлена", "Службу зупинено", "Service stopped", "Service arrêté", "Servicio detenido",
     "Serviço parado", "Dienst gestoppt", "Palvelu pysäytetty", "Layanan dihentikan", "服务已停止",
     "सेवा रुकी हुई है", "서비스 중지됨", "Hizmet durduruldu", "サービス停止中"),
    ("Порог свободной памяти (%) -m", "Поріг вільної пам'яті (%) -m", "Free memory threshold (%) -m",
     "Seuil de mémoire libre (%) -m", "Umbral de memoria libre (%) -m", "Limite de memória livre (%) -m",
     "Schwellenwert freier Speicher (%) -m", "Vapaan muistin raja (%) -m", "Ambang memori bebas (%) -m",
     "可用内存阈值 (%) -m", "खाली मेमोरी सीमा (%) -m", "여유 메모리 임계값(%) -m", "Boş bellek eşiği (%) -m",
     "空きメモリのしきい値 (%) -m"),
    ("если свободно меньше — убиваем процесс", "якщо вільно менше — вбиваємо процес",
     "if free memory drops below this, a process is killed",
     "si la mémoire libre passe en dessous, un processus est tué",
     "si queda menos libre, se mata un proceso", "se houver menos livre, um processo é encerrado",
     "wenn weniger frei ist, wird ein Prozess beendet", "jos vapaata on vähemmän, prosessi tapetaan",
     "jika bebas kurang dari ini, proses dihentikan", "可用量低于此值时终止进程",
     "खाली मेमोरी इससे कम होने पर प्रक्रिया बंद की जाती है", "여유가 이보다 적으면 프로세스를 종료합니다",
     "boş bellek bunun altına düşerse bir işlem sonlandırılır", "空きがこれ未満になるとプロセスを終了します"),
    ("сохраняется «{}»", "зберігається «{}»", "«{}» is kept", "« {} » est conservé", "se conserva «{}»",
     "«{}» é mantido", "„{}“ bleibt erhalten", "«{}» säilytetään", "«{}» dipertahankan", "保留「{}」",
     "«{}» सुरक्षित रखा जाता है", "「{}」 유지됨", "«{}» korunur", "「{}」を保持"),
    ("Порог свободного swap (%) -S", "Поріг вільного swap (%) -S", "Free swap threshold (%) -S",
     "Seuil de swap libre (%) -S", "Umbral de swap libre (%) -S", "Limite de swap livre (%) -S",
     "Schwellenwert freier Swap (%) -S", "Vapaan swapin raja (%) -S", "Ambang swap bebas (%) -S",
     "可用 swap 阈值 (%) -S", "खाली swap सीमा (%) -S", "여유 swap 임계값(%) -S", "Boş swap eşiği (%) -S",
     "空き swap のしきい値 (%) -S"),
    ("аналогично для swap", "аналогічно для swap", "same for swap", "idem pour le swap",
     "lo mismo para el swap", "o mesmo para o swap", "entsprechend für Swap", "sama swapille",
     "sama untuk swap", "对 swap 同理", "swap के लिए भी यही", "swap에도 동일하게 적용", "swap için de aynı",
     "swap にも同様"),
    ("Не убивать (regex) --avoid", "Не вбивати (regex) --avoid", "Do not kill (regex) --avoid",
     "Ne pas tuer (regex) --avoid", "No matar (regex) --avoid", "Não encerrar (regex) --avoid",
     "Nicht beenden (Regex) --avoid", "Älä tapa (regex) --avoid", "Jangan hentikan (regex) --avoid",
     "不要终止（正则）--avoid", "न बंद करें (regex) --avoid", "종료하지 않음(정규식) --avoid",
     "Sonlandırma (regex) --avoid", "終了させない (regex) --avoid"),
    ("--avoid: нельзя кавычки, обратный слэш, переводы строк и подстановки команд",
     "--avoid: не можна лапки, зворотний слеш, переноси рядків і підстановки команд",
     "--avoid: quotes, backslashes, line breaks and command substitutions are not allowed",
     "--avoid : guillemets, antislash, sauts de ligne et substitutions de commandes interdits",
     "--avoid: no se permiten comillas, barras invertidas, saltos de línea ni sustituciones de comandos",
     "--avoid: não são permitidas aspas, barra invertida, quebras de linha e substituições de comandos",
     "--avoid: Anführungszeichen, Backslash, Zeilenumbrüche und Befehlsersetzungen sind nicht erlaubt",
     "--avoid: lainausmerkit, kenoviiva, rivinvaihdot ja komentokorvaukset eivät ole sallittuja",
     "--avoid: tanda kutip, backslash, baris baru, dan substitusi perintah tidak diizinkan",
     "--avoid：不允许引号、反斜杠、换行和命令替换",
     "--avoid: उद्धरण चिह्न, बैकस्लैश, नई पंक्तियाँ और कमांड प्रतिस्थापन की अनुमति नहीं है",
     "--avoid: 따옴표, 백슬래시, 줄바꿈, 명령 치환은 사용할 수 없습니다",
     "--avoid: tırnak, ters eğik çizgi, satır sonu ve komut yerine koyma kullanılamaz",
     "--avoid: 引用符、バックスラッシュ、改行、コマンド置換は使用できません"),
    ("earlyoom: в аргументах есть двойная кавычка, запись отменена",
     "earlyoom: в аргументах є подвійна лапка, запис скасовано",
     "earlyoom: the arguments contain a double quote, write cancelled",
     "earlyoom : les arguments contiennent un guillemet double, écriture annulée",
     "earlyoom: los argumentos contienen comillas dobles, escritura cancelada",
     "earlyoom: os argumentos contêm aspas duplas, gravação cancelada",
     "earlyoom: Die Argumente enthalten ein doppeltes Anführungszeichen, Schreiben abgebrochen",
     "earlyoom: argumenteissa on lainausmerkki, kirjoitus peruttu",
     "earlyoom: argumen mengandung tanda kutip ganda, penulisan dibatalkan",
     "earlyoom：参数中含有双引号，已取消写入",
     "earlyoom: आर्गुमेंट में दोहरे उद्धरण चिह्न हैं, लिखना रद्द किया गया",
     "earlyoom: 인수에 큰따옴표가 있어 기록을 취소했습니다",
     "earlyoom: bağımsız değişkenlerde çift tırnak var, yazma iptal edildi",
     "earlyoom: 引数に二重引用符が含まれているため、書き込みを中止しました"),
    ("EarlyOOM: применено и перезапущено", "EarlyOOM: застосовано та перезапущено",
     "EarlyOOM: applied and restarted", "EarlyOOM : appliqué et redémarré",
     "EarlyOOM: aplicado y reiniciado", "EarlyOOM: aplicado e reiniciado",
     "EarlyOOM: angewendet und neu gestartet", "EarlyOOM: otettu käyttöön ja käynnistetty uudelleen",
     "EarlyOOM: diterapkan dan dimulai ulang", "EarlyOOM：已应用并重启",
     "EarlyOOM: लागू किया गया और पुनः आरंभ किया गया", "EarlyOOM: 적용 후 다시 시작했습니다",
     "EarlyOOM: uygulandı ve yeniden başlatıldı", "EarlyOOM: 適用して再起動しました"),
 
    # ── GameMode ─────────────────────────────────────────────────────
    ("Оптимизация для игр", "Оптимізація для ігор", "Game optimization", "Optimisation pour les jeux",
     "Optimización para juegos", "Otimização para jogos", "Spieleoptimierung", "Pelioptimointi",
     "Optimasi untuk game", "游戏优化", "गेम के लिए ऑप्टिमाइज़ेशन", "게임 최적화", "Oyun optimizasyonu",
     "ゲーム最適化"),
    ("записываются только изменённые параметры", "записуються лише змінені параметри",
     "only changed parameters are written", "seuls les paramètres modifiés sont écrits",
     "solo se escriben los parámetros modificados", "apenas os parâmetros alterados são gravados",
     "nur geänderte Parameter werden geschrieben", "vain muutetut parametrit kirjoitetaan",
     "hanya parameter yang diubah yang ditulis", "仅写入修改过的参数",
     "केवल बदले गए पैरामीटर लिखे जाते हैं", "변경된 매개변수만 기록됩니다",
     "yalnızca değiştirilen parametreler yazılır", "変更したパラメーターのみ書き込まれます"),
    ("gamemode не установлен (sudo apt install gamemode)", "gamemode не встановлено (sudo apt install gamemode)",
     "gamemode is not installed (sudo apt install gamemode)",
     "gamemode n'est pas installé (sudo apt install gamemode)",
     "gamemode no está instalado (sudo apt install gamemode)",
     "gamemode não está instalado (sudo apt install gamemode)",
     "gamemode ist nicht installiert (sudo apt install gamemode)",
     "gamemodea ei ole asennettu (sudo apt install gamemode)",
     "gamemode belum terpasang (sudo apt install gamemode)", "未安装 gamemode（sudo apt install gamemode）",
     "gamemode इंस्टॉल नहीं है (sudo apt install gamemode)",
     "gamemode가 설치되어 있지 않습니다(sudo apt install gamemode)",
     "gamemode kurulu değil (sudo apt install gamemode)",
     "gamemode がインストールされていません（sudo apt install gamemode）"),
    ("Демон: {}", "Демон: {}", "Daemon: {}", "Démon : {}", "Demonio: {}", "Daemon: {}", "Daemon: {}",
     "Taustaprosessi: {}", "Daemon: {}", "守护进程：{}", "डेमॉन: {}", "데몬: {}", "Daemon: {}", "デーモン: {}"),
    ("статус неизвестен", "статус невідомий", "status unknown", "état inconnu", "estado desconocido",
     "estado desconhecido", "Status unbekannt", "tila tuntematon", "status tidak diketahui", "状态未知",
     "स्थिति अज्ञात", "상태 알 수 없음", "durum bilinmiyor", "状態不明"),
    ("готов (ожидание игры)", "готовий (очікування гри)", "ready (waiting for a game)",
     "prêt (en attente d'un jeu)", "listo (esperando un juego)", "pronto (aguardando um jogo)",
     "bereit (wartet auf ein Spiel)", "valmis (odottaa peliä)", "siap (menunggu game)", "就绪（等待游戏）",
     "तैयार (गेम की प्रतीक्षा)", "준비됨(게임 대기 중)", "hazır (oyun bekleniyor)", "待機中（ゲーム待ち）"),
    ("активен (игра запущена)", "активний (гру запущено)", "active (game running)", "actif (jeu lancé)",
     "activo (juego en ejecución)", "ativo (jogo em execução)", "aktiv (Spiel läuft)",
     "aktiivinen (peli käynnissä)", "aktif (game berjalan)", "活动中（游戏已运行）",
     "सक्रिय (गेम चल रहा है)", "활성(게임 실행 중)", "etkin (oyun çalışıyor)", "動作中（ゲーム実行中）"),
    ("конфиг найден", "конфіг знайдено", "config found", "configuration trouvée", "configuración encontrada",
     "configuração encontrada", "Konfiguration gefunden", "asetukset löytyivät", "konfigurasi ditemukan",
     "已找到配置", "कॉन्फ़िग मिली", "설정 파일 있음", "yapılandırma bulundu", "設定ファイルあり"),
    ("конфиг не создан (по умолчанию)", "конфіг не створено (типові)", "config not created (defaults)",
     "configuration non créée (valeurs par défaut)", "configuración no creada (valores por defecto)",
     "configuração não criada (padrão)", "Konfiguration nicht erstellt (Standardwerte)",
     "asetuksia ei luotu (oletukset)", "konfigurasi belum dibuat (bawaan)", "未创建配置（使用默认值）",
     "कॉन्फ़िग नहीं बनी (डिफ़ॉल्ट)", "설정 파일 없음(기본값)", "yapılandırma oluşturulmadı (varsayılan)",
     "設定ファイル未作成（デフォルト）"),
    ("renice (0 = не менять)", "renice (0 = не змінювати)", "renice (0 = don't change)",
     "renice (0 = ne pas modifier)", "renice (0 = no cambiar)", "renice (0 = não alterar)",
     "renice (0 = nicht ändern)", "renice (0 = ei muutosta)", "renice (0 = jangan ubah)", "renice（0 = 不更改）",
     "renice (0 = बदलें नहीं)", "renice(0 = 변경 안 함)", "renice (0 = değiştirme)", "renice（0 = 変更しない）"),
    ("1–20: применяется как отрицательный nice (10 → −10); больше — выше приоритет",
     "1–20: застосовується як від'ємний nice (10 → −10); більше — вищий пріоритет",
     "1–20: applied as a negative nice value (10 → −10); higher means higher priority",
     "1–20 : appliqué comme valeur nice négative (10 → −10) ; plus grand = priorité plus élevée",
     "1–20: se aplica como nice negativo (10 → −10); mayor valor, mayor prioridad",
     "1–20: aplicado como nice negativo (10 → −10); maior valor, maior prioridade",
     "1–20: wird als negativer Nice-Wert angewendet (10 → −10); höher bedeutet höhere Priorität",
     "1–20: käytetään negatiivisena nice-arvona (10 → −10); suurempi = korkeampi prioriteetti",
     "1–20: diterapkan sebagai nilai nice negatif (10 → −10); makin besar, prioritas makin tinggi",
     "1–20：作为负的 nice 值应用（10 → −10）；数值越大优先级越高",
     "1–20: ऋणात्मक nice मान के रूप में लागू (10 → −10); बड़ा मान = ऊँची प्राथमिकता",
     "1–20: 음수 nice 값으로 적용됩니다(10 → −10). 클수록 우선순위가 높습니다",
     "1–20: negatif nice değeri olarak uygulanır (10 → −10); büyük değer = yüksek öncelik",
     "1–20: 負の nice 値として適用されます（10 → −10）。大きいほど優先度が高くなります"),
    ("CPU governor во время игры", "CPU governor під час гри", "CPU governor during games",
     "Governor CPU pendant les jeux", "Governor de CPU durante los juegos",
     "Governor da CPU durante os jogos", "CPU-Governor während des Spiels",
     "Suorittimen governor pelin aikana", "Governor CPU saat bermain game", "游戏期间的 CPU governor",
     "गेम के दौरान CPU governor", "게임 중 CPU 거버너", "Oyun sırasında CPU governor",
     "ゲーム中の CPU ガバナー"),
    ("GameMode: изменений нет", "GameMode: змін немає", "GameMode: no changes", "GameMode : aucun changement",
     "GameMode: sin cambios", "GameMode: sem alterações", "GameMode: keine Änderungen",
     "GameMode: ei muutoksia", "GameMode: tidak ada perubahan", "GameMode：无更改",
     "GameMode: कोई बदलाव नहीं", "GameMode: 변경 사항 없음", "GameMode: değişiklik yok", "GameMode: 変更なし"),
    ("GameMode: сохранено", "GameMode: збережено", "GameMode: saved", "GameMode : enregistré",
     "GameMode: guardado", "GameMode: salvo", "GameMode: gespeichert", "GameMode: tallennettu",
     "GameMode: tersimpan", "GameMode：已保存", "GameMode: सहेजा गया", "GameMode: 저장됨",
     "GameMode: kaydedildi", "GameMode: 保存しました"),
 
    # ── CPU ──────────────────────────────────────────────────────────
    ("Управление частотой CPU", "Керування частотою CPU", "CPU frequency control",
     "Contrôle de la fréquence du CPU", "Control de la frecuencia de la CPU",
     "Controle da frequência da CPU", "CPU-Frequenzsteuerung", "Suorittimen taajuuden hallinta",
     "Kontrol frekuensi CPU", "CPU 频率控制", "CPU आवृत्ति नियंत्रण", "CPU 주파수 제어",
     "CPU frekans denetimi", "CPU 周波数の制御"),
    ("Запись напрямую в sysfs (cpupower не нужен)", "Запис напряму в sysfs (cpupower не потрібен)",
     "Writes directly to sysfs (cpupower not needed)", "Écriture directe dans sysfs (cpupower inutile)",
     "Escritura directa en sysfs (no hace falta cpupower)",
     "Gravação direta no sysfs (cpupower não é necessário)", "Schreibt direkt in sysfs (cpupower nicht nötig)",
     "Kirjoittaa suoraan sysfs:ään (cpupower ei tarvita)", "Menulis langsung ke sysfs (tidak perlu cpupower)",
     "直接写入 sysfs（无需 cpupower）", "सीधे sysfs में लिखता है (cpupower की आवश्यकता नहीं)",
     "sysfs에 직접 기록(cpupower 불필요)", "Doğrudan sysfs'e yazar (cpupower gerekmez)",
     "sysfs に直接書き込み（cpupower 不要）"),
    ("сохраняется после перезагрузки", "зберігається після перезавантаження", "persists after reboot",
     "conservé après le redémarrage", "se conserva tras reiniciar", "mantido após reiniciar",
     "bleibt nach dem Neustart erhalten", "säilyy uudelleenkäynnistyksen jälkeen",
     "tetap berlaku setelah reboot", "重启后保留", "रीबूट के बाद भी बना रहता है",
     "재부팅 후에도 유지됨", "yeniden başlatmadan sonra korunur", "再起動後も保持"),
    ("Губернатор частоты", "Губернатор частоти", "Frequency governor", "Gouverneur de fréquence",
     "Gobernador de frecuencia", "Governador de frequência", "Frequenz-Governor", "Taajuusgovernor",
     "Governor frekuensi", "频率调节器", "आवृत्ति गवर्नर", "주파수 거버너", "Frekans governor'ı",
     "周波数ガバナー"),
    ("сейчас: {}", "зараз: {}", "now: {}", "actuellement : {}", "ahora: {}", "agora: {}", "aktuell: {}",
     "nyt: {}", "saat ini: {}", "当前：{}", "अभी: {}", "현재: {}", "şu an: {}", "現在: {}"),
    ("Мин. частота (МГц)", "Мін. частота (МГц)", "Min. frequency (MHz)", "Fréquence min. (MHz)",
     "Frecuencia mín. (MHz)", "Frequência mín. (MHz)", "Min. Frequenz (MHz)", "Min. taajuus (MHz)",
     "Frekuensi min. (MHz)", "最低频率 (MHz)", "न्यूनतम आवृत्ति (MHz)", "최소 주파수(MHz)",
     "Min. frekans (MHz)", "最小周波数 (MHz)"),
    ("Макс. частота (МГц)", "Макс. частота (МГц)", "Max. frequency (MHz)", "Fréquence max. (MHz)",
     "Frecuencia máx. (MHz)", "Frequência máx. (MHz)", "Max. Frequenz (MHz)", "Maks. taajuus (MHz)",
     "Frekuensi maks. (MHz)", "最高频率 (MHz)", "अधिकतम आवृत्ति (MHz)", "최대 주파수(MHz)",
     "Maks. frekans (MHz)", "最大周波数 (MHz)"),
    ("{} МГц", "{} МГц", "{} MHz", "{} MHz", "{} MHz", "{} MHz", "{} MHz", "{} MHz", "{} MHz", "{} MHz",
     "{} MHz", "{} MHz", "{} MHz", "{} MHz"),
    ("сейчас: {} МГц", "зараз: {} МГц", "now: {} MHz", "actuellement : {} MHz", "ahora: {} MHz",
     "agora: {} MHz", "aktuell: {} MHz", "nyt: {} MHz", "saat ini: {} MHz", "当前：{} MHz", "अभी: {} MHz",
     "현재: {} MHz", "şu an: {} MHz", "現在: {} MHz"),
    ("допустимо {} (для каждого ядра — по его пределам)", "допустимо {} (для кожного ядра — за його межами)",
     "allowed {} (per core, within its own limits)", "autorisé {} (pour chaque cœur, selon ses limites)",
     "permitido {} (por núcleo, según sus límites)", "permitido {} (para cada núcleo, dentro de seus limites)",
     "zulässig {} (pro Kern innerhalb seiner Grenzen)", "sallittu {} (kullekin ytimelle sen rajojen mukaan)",
     "diizinkan {} (per inti, sesuai batasnya)", "允许范围 {}（每个核心按其自身上下限）",
     "अनुमत {} (प्रत्येक कोर के लिए उसकी सीमाओं के अनुसार)", "허용 범위 {}(코어별로 해당 한계 적용)",
     "izin verilen {} (her çekirdek için kendi sınırlarına göre)",
     "許容範囲 {}（コアごとにそれぞれの上限・下限）"),
    ("cpufreq недоступен (виртуалка или драйвер без cpufreq)",
     "cpufreq недоступний (віртуалка або драйвер без cpufreq)",
     "cpufreq is unavailable (virtual machine or a driver without cpufreq)",
     "cpufreq indisponible (machine virtuelle ou pilote sans cpufreq)",
     "cpufreq no disponible (máquina virtual o controlador sin cpufreq)",
     "cpufreq indisponível (máquina virtual ou driver sem cpufreq)",
     "cpufreq nicht verfügbar (virtuelle Maschine oder Treiber ohne cpufreq)",
     "cpufreq ei ole käytettävissä (virtuaalikone tai ajuri ilman cpufreqia)",
     "cpufreq tidak tersedia (mesin virtual atau driver tanpa cpufreq)",
     "cpufreq 不可用（虚拟机或驱动不支持 cpufreq）",
     "cpufreq उपलब्ध नहीं (वर्चुअल मशीन या बिना cpufreq वाला ड्राइवर)",
     "cpufreq를 사용할 수 없음(가상 머신이거나 cpufreq 없는 드라이버)",
     "cpufreq kullanılamıyor (sanal makine veya cpufreq'siz sürücü)",
     "cpufreq は利用できません（仮想マシン、または cpufreq 非対応ドライバー）"),
    ("разные: {}", "різні: {}", "different: {}", "différents : {}", "distintos: {}", "diferentes: {}",
     "verschieden: {}", "eri arvoja: {}", "berbeda: {}", "不一致：{}", "अलग-अलग: {}", "서로 다름: {}",
     "farklı: {}", "異なる: {}"),
    ("governor: {}", "governor: {}", "governor: {}", "governor : {}", "governor: {}", "governor: {}",
     "Governor: {}", "governor: {}", "governor: {}", "governor：{}", "governor: {}", "거버너: {}",
     "governor: {}", "ガバナー: {}"),
    ("сейчас до {} MHz", "зараз до {} MHz", "now up to {} MHz", "actuellement jusqu'à {} MHz",
     "ahora hasta {} MHz", "agora até {} MHz", "aktuell bis zu {} MHz", "nyt enintään {} MHz",
     "saat ini hingga {} MHz", "当前最高 {} MHz", "अभी अधिकतम {} MHz", "현재 최대 {} MHz",
     "şu an en fazla {} MHz", "現在 最大 {} MHz"),
    ("политика PixelTweak включена", "політика PixelTweak увімкнена", "PixelTweak policy enabled",
     "politique PixelTweak activée", "política de PixelTweak activada", "política do PixelTweak ativada",
     "PixelTweak-Richtlinie aktiv", "PixelTweak-käytäntö käytössä", "kebijakan PixelTweak aktif",
     "PixelTweak 策略已启用", "PixelTweak नीति सक्षम", "PixelTweak 정책 사용 중", "PixelTweak ilkesi etkin",
     "PixelTweak ポリシー有効"),
    ("Применить к CPU", "Застосувати до CPU", "Apply to CPU", "Appliquer au CPU", "Aplicar a la CPU",
     "Aplicar à CPU", "Auf CPU anwenden", "Käytä suorittimeen", "Terapkan ke CPU", "应用到 CPU",
     "CPU पर लागू करें", "CPU에 적용", "CPU'ya uygula", "CPU に適用"),
    ("Сбросить к исходным и удалить сервис", "Скинути до початкових і видалити сервіс",
     "Reset to original and remove the service", "Revenir aux valeurs d'origine et supprimer le service",
     "Restablecer a los originales y eliminar el servicio",
     "Redefinir para os originais e remover o serviço",
     "Auf Ursprungswerte zurücksetzen und Dienst entfernen", "Palauta alkuperäiset ja poista palvelu",
     "Setel ulang ke semula dan hapus layanan", "恢复原始值并删除服务",
     "मूल पर रीसेट करें और सेवा हटाएँ", "원래대로 초기화하고 서비스 삭제",
     "Orijinale sıfırla ve hizmeti kaldır", "元に戻してサービスを削除"),
    ("↩ Сбросить", "↩ Скинути", "↩ Reset", "↩ Réinitialiser", "↩ Restablecer", "↩ Redefinir",
     "↩ Zurücksetzen", "↩ Nollaa", "↩ Setel ulang", "↩ 重置", "↩ रीसेट", "↩ 초기화", "↩ Sıfırla", "↩ リセット"),
    ("CPU: cpufreq недоступен в этой системе", "CPU: cpufreq недоступний у цій системі",
     "CPU: cpufreq is unavailable on this system", "CPU : cpufreq indisponible sur ce système",
     "CPU: cpufreq no está disponible en este sistema", "CPU: cpufreq indisponível neste sistema",
     "CPU: cpufreq ist auf diesem System nicht verfügbar",
     "CPU: cpufreq ei ole käytettävissä tässä järjestelmässä",
     "CPU: cpufreq tidak tersedia di sistem ini", "CPU：此系统上 cpufreq 不可用",
     "CPU: इस सिस्टम पर cpufreq उपलब्ध नहीं है", "CPU: 이 시스템에서는 cpufreq를 사용할 수 없습니다",
     "CPU: bu sistemde cpufreq kullanılamıyor", "CPU: このシステムでは cpufreq を利用できません"),
    ("CPU: минимум должен быть меньше максимума", "CPU: мінімум має бути меншим за максимум",
     "CPU: the minimum must be lower than the maximum", "CPU : le minimum doit être inférieur au maximum",
     "CPU: el mínimo debe ser menor que el máximo", "CPU: o mínimo deve ser menor que o máximo",
     "CPU: Das Minimum muss kleiner als das Maximum sein", "CPU: minimin on oltava pienempi kuin maksimi",
     "CPU: minimum harus lebih kecil dari maksimum", "CPU：最小值必须小于最大值",
     "CPU: न्यूनतम, अधिकतम से कम होना चाहिए", "CPU: 최소값은 최대값보다 작아야 합니다",
     "CPU: minimum, maksimumdan küçük olmalı", "CPU: 最小値は最大値より小さくしてください"),
    ("CPU: странное имя governor'а", "CPU: дивна назва governor'а", "CPU: unusual governor name",
     "CPU : nom de governor inhabituel", "CPU: nombre de governor extraño", "CPU: nome de governor estranho",
     "CPU: ungewöhnlicher Governor-Name", "CPU: outo governorin nimi", "CPU: nama governor tidak lazim",
     "CPU：governor 名称异常", "CPU: governor का नाम असामान्य है", "CPU: governor 이름이 이상합니다",
     "CPU: tuhaf governor adı", "CPU: governor 名が不正です"),
    ("CPU: {}, {}–{} МГц (сохранено и после перезагрузки)",
     "CPU: {}, {}–{} МГц (збережено і після перезавантаження)",
     "CPU: {}, {}–{} MHz (saved, persists after reboot)",
     "CPU : {}, {}–{} MHz (enregistré, conservé après redémarrage)",
     "CPU: {}, {}–{} MHz (guardado, se conserva tras reiniciar)",
     "CPU: {}, {}–{} MHz (salvo, mantido após reiniciar)",
     "CPU: {}, {}–{} MHz (gespeichert, bleibt nach Neustart erhalten)",
     "CPU: {}, {}–{} MHz (tallennettu, säilyy uudelleenkäynnistyksessä)",
     "CPU: {}, {}–{} MHz (tersimpan, tetap berlaku setelah reboot)",
     "CPU：{}，{}–{} MHz（已保存，重启后仍有效）",
     "CPU: {}, {}–{} MHz (सहेजा गया, रीबूट के बाद भी रहेगा)",
     "CPU: {}, {}–{} MHz(저장됨, 재부팅 후에도 유지)",
     "CPU: {}, {}–{} MHz (kaydedildi, yeniden başlatmadan sonra da geçerli)",
     "CPU: {}、{}–{} MHz（保存済み・再起動後も有効）"),
    ("CPU: сброшено, сервис автозагрузки удалён", "CPU: скинуто, сервіс автозапуску видалено",
     "CPU: reset, autostart service removed", "CPU : réinitialisé, service de démarrage automatique supprimé",
     "CPU: restablecido, servicio de inicio automático eliminado",
     "CPU: redefinido, serviço de inicialização automática removido",
     "CPU: zurückgesetzt, Autostart-Dienst entfernt",
     "CPU: nollattu, automaattikäynnistyspalvelu poistettu",
     "CPU: disetel ulang, layanan mulai otomatis dihapus", "CPU：已重置，自启动服务已删除",
     "CPU: रीसेट किया गया, ऑटोस्टार्ट सेवा हटाई गई", "CPU: 초기화됨, 자동 시작 서비스 삭제됨",
     "CPU: sıfırlandı, otomatik başlatma hizmeti kaldırıldı",
     "CPU: リセットしました。自動起動サービスを削除しました"),
    ("Сбросить настройки CPU?", "Скинути налаштування CPU?", "Reset CPU settings?",
     "Réinitialiser les réglages du CPU ?", "¿Restablecer los ajustes de la CPU?",
     "Redefinir as configurações da CPU?", "CPU-Einstellungen zurücksetzen?",
     "Nollataanko suorittimen asetukset?", "Setel ulang pengaturan CPU?", "要重置 CPU 设置吗？",
     "CPU सेटिंग्स रीसेट करें?", "CPU 설정을 초기화할까요?", "CPU ayarları sıfırlansın mı?",
     "CPU 設定をリセットしますか？"),
    ("Governor и пределы частоты вернутся к значениям, которые были до первого применения (если исходные не сохранены — к аппаратным пределам и стандартному governor'у).",
     "Governor і межі частоти повернуться до значень, що були до першого застосування (якщо початкові не збережено — до апаратних меж і стандартного governor'а).",
     "The governor and frequency limits will return to the values from before the first apply (if the originals weren't saved — to hardware limits and the default governor).",
     "Le governor et les limites de fréquence reviendront aux valeurs d'avant la première application (si les originales ne sont pas enregistrées : aux limites matérielles et au governor par défaut).",
     "El governor y los límites de frecuencia volverán a los valores previos a la primera aplicación (si no se guardaron los originales: a los límites de hardware y al governor estándar).",
     "O governor e os limites de frequência voltarão aos valores anteriores à primeira aplicação (se os originais não foram salvos: aos limites de hardware e ao governor padrão).",
     "Governor und Frequenzgrenzen kehren zu den Werten vor der ersten Anwendung zurück (sind die ursprünglichen nicht gespeichert: zu den Hardwaregrenzen und dem Standard-Governor).",
     "Governor ja taajuusrajat palaavat arvoihin ennen ensimmäistä käyttöönottoa (jos alkuperäisiä ei ole tallennettu: laitteiston rajoihin ja oletusgovernoriin).",
     "Governor dan batas frekuensi akan kembali ke nilai sebelum penerapan pertama (jika nilai asli tidak tersimpan — ke batas perangkat keras dan governor standar).",
     "Governor 和频率上下限将恢复为首次应用前的值（若未保存原始值，则恢复为硬件上下限和默认 governor）。",
     "Governor और आवृत्ति सीमाएँ पहली बार लागू करने से पहले के मानों पर लौट जाएँगी (यदि मूल मान सहेजे नहीं गए हैं — तो हार्डवेयर सीमाओं और मानक governor पर)।",
     "거버너와 주파수 한계는 처음 적용하기 전의 값으로 돌아갑니다(원래 값이 저장되어 있지 않으면 하드웨어 한계와 기본 거버너로 복원).",
     "Governor ve frekans sınırları ilk uygulamadan önceki değerlere döner (orijinal değerler kayıtlı değilse donanım sınırlarına ve varsayılan governor'a).",
     "ガバナーと周波数の上限・下限は、最初に適用する前の値に戻ります（元の値が保存されていない場合は、ハードウェアの上限・下限と標準ガバナーに戻ります）。"),
    ("Сервис автозагрузки будет удалён.", "Сервіс автозапуску буде видалено.",
     "The autostart service will be removed.", "Le service de démarrage automatique sera supprimé.",
     "Se eliminará el servicio de inicio automático.", "O serviço de inicialização automática será removido.",
     "Der Autostart-Dienst wird entfernt.", "Automaattikäynnistyspalvelu poistetaan.",
     "Layanan mulai otomatis akan dihapus.", "自启动服务将被删除。", "ऑटोस्टार्ट सेवा हटा दी जाएगी।",
     "자동 시작 서비스가 삭제됩니다.", "Otomatik başlatma hizmeti kaldırılacak.",
     "自動起動サービスは削除されます。"),
    ("Сбросить", "Скинути", "Reset", "Réinitialiser", "Restablecer", "Redefinir", "Zurücksetzen", "Nollaa",
     "Setel ulang", "重置", "रीसेट", "초기화", "Sıfırla", "リセット"),
    ("активен: может перезаписывать governor (наш сервис запускается после него, но смена профиля в GNOME снова всё перетрёт)",
     "активний: може перезаписувати governor (наш сервіс запускається після нього, але зміна профілю в GNOME знову все перезапише)",
     "active: may overwrite the governor (our service starts after it, but switching the profile in GNOME will override everything again)",
     "actif : peut écraser le governor (notre service démarre après lui, mais un changement de profil dans GNOME écrasera tout de nouveau)",
     "activo: puede sobrescribir el governor (nuestro servicio se inicia después, pero cambiar el perfil en GNOME lo sobrescribirá de nuevo)",
     "ativo: pode sobrescrever o governor (nosso serviço inicia depois dele, mas trocar o perfil no GNOME substituirá tudo novamente)",
     "aktiv: kann den Governor überschreiben (unser Dienst startet danach, aber ein Profilwechsel in GNOME überschreibt wieder alles)",
     "aktiivinen: voi ylikirjoittaa governorin (palvelumme käynnistyy sen jälkeen, mutta profiilin vaihto GNOMEssa ylikirjoittaa kaiken uudelleen)",
     "aktif: dapat menimpa governor (layanan kami berjalan setelahnya, tetapi mengganti profil di GNOME akan menimpa semuanya lagi)",
     "已启用：可能覆盖 governor（我们的服务在其之后启动，但在 GNOME 中切换配置文件会再次覆盖所有设置）",
     "सक्रिय: governor को अधिलिखित कर सकता है (हमारी सेवा उसके बाद शुरू होती है, लेकिन GNOME में प्रोफ़ाइल बदलने पर सब कुछ फिर बदल जाएगा)",
     "활성: 거버너를 덮어쓸 수 있음(우리 서비스는 그 뒤에 시작되지만 GNOME에서 프로필을 바꾸면 다시 모두 덮어씀)",
     "etkin: governor'ı ezebilir (hizmetimiz ondan sonra başlar, ancak GNOME'da profil değiştirmek her şeyi yine ezer)",
     "有効: governor を上書きする場合があります（このサービスはその後に起動しますが、GNOME でプロファイルを切り替えると再び上書きされます）"),
    ("замаскирован (mask): GNOME не сможет запустить службу по D-Bus",
     "замасковано (mask): GNOME не зможе запустити службу через D-Bus",
     "masked: GNOME will not be able to start the service via D-Bus",
     "masqué (mask) : GNOME ne pourra pas démarrer le service via D-Bus",
     "enmascarado (mask): GNOME no podrá iniciar el servicio por D-Bus",
     "mascarado (mask): o GNOME não poderá iniciar o serviço via D-Bus",
     "maskiert (mask): GNOME kann den Dienst nicht per D-Bus starten",
     "peitetty (mask): GNOME ei voi käynnistää palvelua D-Busin kautta",
     "dimasker (mask): GNOME tidak dapat memulai layanan lewat D-Bus",
     "已屏蔽（mask）：GNOME 无法通过 D-Bus 启动该服务",
     "मास्क किया गया (mask): GNOME D-Bus से सेवा शुरू नहीं कर पाएगा",
     "마스크됨(mask): GNOME이 D-Bus로 서비스를 시작할 수 없음",
     "maskelendi (mask): GNOME hizmeti D-Bus ile başlatamaz",
     "マスク済み（mask）: GNOME は D-Bus 経由でサービスを起動できません"),
    ("остановлен, но не замаскирован (GNOME может запустить по D-Bus)",
     "зупинений, але не замаскований (GNOME може запустити через D-Bus)",
     "stopped, but not masked (GNOME can start it via D-Bus)",
     "arrêté, mais non masqué (GNOME peut le démarrer via D-Bus)",
     "detenido, pero no enmascarado (GNOME puede iniciarlo por D-Bus)",
     "parado, mas não mascarado (o GNOME pode iniciá-lo via D-Bus)",
     "gestoppt, aber nicht maskiert (GNOME kann ihn per D-Bus starten)",
     "pysäytetty, mutta ei peitetty (GNOME voi käynnistää sen D-Busin kautta)",
     "dihentikan, tetapi tidak dimasker (GNOME dapat memulainya lewat D-Bus)",
     "已停止，但未屏蔽（GNOME 可通过 D-Bus 启动）",
     "रुका हुआ, पर मास्क नहीं किया गया (GNOME D-Bus से शुरू कर सकता है)",
     "중지됨, 하지만 마스크되지 않음(GNOME이 D-Bus로 시작할 수 있음)",
     "durduruldu ancak maskelenmedi (GNOME D-Bus ile başlatabilir)",
     "停止中ですが、マスクされていません（GNOME が D-Bus 経由で起動できます）"),
    ("Отключить", "Вимкнути", "Disable", "Désactiver", "Desactivar", "Desativar", "Deaktivieren",
     "Poista käytöstä", "Nonaktifkan", "禁用", "बंद करें", "끄기", "Devre dışı bırak", "無効にする"),
    ("Включить", "Увімкнути", "Enable", "Activer", "Activar", "Ativar", "Aktivieren", "Ota käyttöön",
     "Aktifkan", "启用", "चालू करें", "켜기", "Etkinleştir", "有効にする"),
    ("Отключить и замаскировать power-profiles-daemon?", "Вимкнути та замаскувати power-profiles-daemon?",
     "Disable and mask power-profiles-daemon?", "Désactiver et masquer power-profiles-daemon ?",
     "¿Desactivar y enmascarar power-profiles-daemon?", "Desativar e mascarar o power-profiles-daemon?",
     "power-profiles-daemon deaktivieren und maskieren?",
     "Poistetaanko power-profiles-daemon käytöstä ja peitetäänkö se?",
     "Nonaktifkan dan masker power-profiles-daemon?", "要禁用并屏蔽 power-profiles-daemon 吗？",
     "power-profiles-daemon बंद करके मास्क करें?", "power-profiles-daemon을 끄고 마스크할까요?",
     "power-profiles-daemon devre dışı bırakılıp maskelensin mi?",
     "power-profiles-daemon を無効化してマスクしますか？"),
    ("Служба будет остановлена и замаскирована (systemctl mask), чтобы GNOME не мог перезапустить её через D-Bus и сбросить governor.",
     "Службу буде зупинено та замасковано (systemctl mask), щоб GNOME не міг перезапустити її через D-Bus і скинути governor.",
     "The service will be stopped and masked (systemctl mask) so that GNOME cannot restart it via D-Bus and reset the governor.",
     "Le service sera arrêté et masqué (systemctl mask) afin que GNOME ne puisse pas le relancer via D-Bus et réinitialiser le governor.",
     "El servicio se detendrá y se enmascarará (systemctl mask) para que GNOME no pueda reiniciarlo por D-Bus y restablecer el governor.",
     "O serviço será parado e mascarado (systemctl mask) para que o GNOME não possa reiniciá-lo via D-Bus e redefinir o governor.",
     "Der Dienst wird gestoppt und maskiert (systemctl mask), damit GNOME ihn nicht per D-Bus neu starten und den Governor zurücksetzen kann.",
     "Palvelu pysäytetään ja peitetään (systemctl mask), jotta GNOME ei voi käynnistää sitä uudelleen D-Busin kautta ja nollata governoria.",
     "Layanan akan dihentikan dan dimasker (systemctl mask) agar GNOME tidak dapat memulainya ulang lewat D-Bus dan mengatur ulang governor.",
     "该服务将被停止并屏蔽（systemctl mask），以防 GNOME 通过 D-Bus 重新启动它并重置 governor。",
     "सेवा रोकी जाएगी और मास्क की जाएगी (systemctl mask), ताकि GNOME उसे D-Bus से दोबारा शुरू करके governor रीसेट न कर सके।",
     "서비스를 중지하고 마스크합니다(systemctl mask). GNOME이 D-Bus로 다시 시작해 거버너를 초기화하는 것을 막기 위해서입니다.",
     "Hizmet durdurulup maskelenecek (systemctl mask); böylece GNOME onu D-Bus ile yeniden başlatıp governor'ı sıfırlayamaz.",
     "GNOME が D-Bus 経由でサービスを再起動してガバナーをリセットしないよう、サービスを停止してマスクします（systemctl mask）。"),
    ("Переключатель профилей питания в настройках GNOME перестанет работать.",
     "Перемикач профілів живлення в налаштуваннях GNOME перестане працювати.",
     "The power profile switcher in GNOME settings will stop working.",
     "Le sélecteur de profils d'alimentation dans les paramètres GNOME cessera de fonctionner.",
     "El selector de perfiles de energía en los ajustes de GNOME dejará de funcionar.",
     "O seletor de perfis de energia nas configurações do GNOME deixará de funcionar.",
     "Der Energieprofil-Umschalter in den GNOME-Einstellungen funktioniert dann nicht mehr.",
     "GNOMEn asetusten virtaprofiilin vaihtaja lakkaa toimimasta.",
     "Pengalih profil daya di pengaturan GNOME tidak akan berfungsi lagi.",
     "GNOME 设置中的电源模式切换将停止工作。",
     "GNOME सेटिंग्स में पावर प्रोफ़ाइल स्विचर काम करना बंद कर देगा।",
     "GNOME 설정의 전원 프로필 전환기가 작동하지 않게 됩니다.",
     "GNOME ayarlarındaki güç profili anahtarı çalışmayı bırakacak.",
     "GNOME 設定の電源プロファイル切り替えは動作しなくなります。"),
    ("Включить обратно можно этой же кнопкой.", "Увімкнути назад можна цією ж кнопкою.",
     "You can turn it back on with the same button.", "Vous pouvez le réactiver avec ce même bouton.",
     "Puede volver a activarlo con este mismo botón.", "Você pode ativá-lo novamente com o mesmo botão.",
     "Mit derselben Schaltfläche lässt er sich wieder einschalten.",
     "Voit ottaa sen takaisin käyttöön samalla painikkeella.",
     "Anda dapat mengaktifkannya kembali dengan tombol yang sama.", "可用同一个按钮重新启用。",
     "इसी बटन से इसे वापस चालू किया जा सकता है।", "같은 버튼으로 다시 켤 수 있습니다.",
     "Aynı düğmeyle yeniden etkinleştirebilirsiniz.", "同じボタンで再び有効にできます。"),
    ("power-profiles-daemon отключён и замаскирован (mask)",
     "power-profiles-daemon вимкнено та замасковано (mask)", "power-profiles-daemon disabled and masked",
     "power-profiles-daemon désactivé et masqué (mask)", "power-profiles-daemon desactivado y enmascarado (mask)",
     "power-profiles-daemon desativado e mascarado (mask)", "power-profiles-daemon deaktiviert und maskiert (mask)",
     "power-profiles-daemon poistettu käytöstä ja peitetty (mask)",
     "power-profiles-daemon dinonaktifkan dan dimasker (mask)", "power-profiles-daemon 已禁用并屏蔽 (mask)",
     "power-profiles-daemon बंद और मास्क किया गया (mask)", "power-profiles-daemon을 끄고 마스크했습니다(mask)",
     "power-profiles-daemon devre dışı bırakıldı ve maskelendi (mask)",
     "power-profiles-daemon を無効化しマスクしました (mask)"),
    ("power-profiles-daemon размаскирован и включён", "power-profiles-daemon розмасковано та ввімкнено",
     "power-profiles-daemon unmasked and enabled", "power-profiles-daemon démasqué et activé",
     "power-profiles-daemon desenmascarado y activado", "power-profiles-daemon desmascarado e ativado",
     "power-profiles-daemon entmaskiert und aktiviert", "power-profiles-daemon palautettu ja otettu käyttöön",
     "power-profiles-daemon di-unmask dan diaktifkan", "power-profiles-daemon 已取消屏蔽并启用",
     "power-profiles-daemon अनमास्क और चालू किया गया", "power-profiles-daemon의 마스크를 해제하고 켰습니다",
     "power-profiles-daemon maskesi kaldırıldı ve etkinleştirildi",
     "power-profiles-daemon のマスクを解除して有効にしました"),
 
    # ── Cache ────────────────────────────────────────────────────────
    ("Очистка кэша", "Очищення кешу", "Cache cleaning", "Nettoyage du cache", "Limpieza de caché",
     "Limpeza de cache", "Cache-Bereinigung", "Välimuistin tyhjennys", "Pembersihan cache", "清理缓存",
     "कैश साफ़ करना", "캐시 정리", "Önbellek temizliği", "キャッシュのクリーンアップ"),
    ("Скрипт: {}", "Скрипт: {}", "Script: {}", "Script : {}", "Script: {}", "Script: {}", "Skript: {}",
     "Komentosarja: {}", "Skrip: {}", "脚本：{}", "स्क्रिप्ट: {}", "스크립트: {}", "Betik: {}", "スクリプト: {}"),
    ("сброс кэша обычно не ускоряет систему", "скидання кешу зазвичай не прискорює систему",
     "dropping the cache usually doesn't speed up the system",
     "vider le cache n'accélère généralement pas le système",
     "vaciar la caché normalmente no acelera el sistema",
     "limpar o cache normalmente não acelera o sistema",
     "das Leeren des Caches beschleunigt das System meist nicht",
     "välimuistin tyhjennys ei yleensä nopeuta järjestelmää",
     "mengosongkan cache biasanya tidak mempercepat sistem", "清空缓存通常不会加快系统",
     "कैश साफ़ करने से आमतौर पर सिस्टम तेज़ नहीं होता", "캐시를 비운다고 보통 시스템이 빨라지지는 않습니다",
     "önbelleği boşaltmak genellikle sistemi hızlandırmaz", "キャッシュを破棄しても通常は高速化しません"),
    ("Включить таймер", "Увімкнути таймер", "Enable timer", "Activer la minuterie",
     "Activar el temporizador", "Ativar o temporizador", "Timer aktivieren", "Ota ajastin käyttöön",
     "Aktifkan timer", "启用定时器", "टाइमर चालू करें", "타이머 켜기", "Zamanlayıcıyı etkinleştir",
     "タイマーを有効にする"),
    ("активен", "активний", "active", "actif", "activo", "ativo", "aktiv", "aktiivinen", "aktif", "已启用",
     "सक्रिय", "활성", "etkin", "有効"),
    ("выключен", "вимкнено", "off", "désactivé", "desactivado", "desativado", "aus", "pois päältä",
     "nonaktif", "已关闭", "बंद", "꺼짐", "kapalı", "無効"),
    ("Интервал", "Інтервал", "Interval", "Intervalle", "Intervalo", "Intervalo", "Intervall", "Aikaväli",
     "Interval", "间隔", "अंतराल", "간격", "Aralık", "間隔"),
    ("Каждые 30 минут", "Кожні 30 хвилин", "Every 30 minutes", "Toutes les 30 minutes", "Cada 30 minutos",
     "A cada 30 minutos", "Alle 30 Minuten", "Joka 30. minuutti", "Setiap 30 menit", "每 30 分钟", "हर 30 मिनट",
     "30분마다", "Her 30 dakikada", "30分ごと"),
    ("Каждый час", "Щогодини", "Every hour", "Toutes les heures", "Cada hora", "A cada hora", "Jede Stunde",
     "Joka tunti", "Setiap jam", "每小时", "हर घंटे", "매시간", "Her saat", "1時間ごと"),
    ("Каждые 3 часа", "Кожні 3 години", "Every 3 hours", "Toutes les 3 heures", "Cada 3 horas",
     "A cada 3 horas", "Alle 3 Stunden", "Joka 3. tunti", "Setiap 3 jam", "每 3 小时", "हर 3 घंटे",
     "3시간마다", "Her 3 saatte", "3時間ごと"),
    ("Каждые 6 часов", "Кожні 6 годин", "Every 6 hours", "Toutes les 6 heures", "Cada 6 horas",
     "A cada 6 horas", "Alle 6 Stunden", "Joka 6. tunti", "Setiap 6 jam", "每 6 小时", "हर 6 घंटे",
     "6시간마다", "Her 6 saatte", "6時間ごと"),
    ("Каждые 12 часов", "Кожні 12 годин", "Every 12 hours", "Toutes les 12 heures", "Cada 12 horas",
     "A cada 12 horas", "Alle 12 Stunden", "Joka 12. tunti", "Setiap 12 jam", "每 12 小时", "हर 12 घंटे",
     "12시간마다", "Her 12 saatte", "12時間ごと"),
    ("Раз в сутки", "Раз на добу", "Once a day", "Une fois par jour", "Una vez al día", "Uma vez por dia",
     "Einmal täglich", "Kerran päivässä", "Sekali sehari", "每天一次", "दिन में एक बार", "하루에 한 번",
     "Günde bir kez", "1日1回"),
    ("Сохранить настройки таймера", "Зберегти налаштування таймера", "Save timer settings",
     "Enregistrer les réglages de la minuterie", "Guardar los ajustes del temporizador",
     "Salvar as configurações do temporizador", "Timer-Einstellungen speichern",
     "Tallenna ajastimen asetukset", "Simpan pengaturan timer", "保存定时器设置",
     "टाइमर सेटिंग्स सहेजें", "타이머 설정 저장", "Zamanlayıcı ayarlarını kaydet", "タイマー設定を保存"),
    ("Очистить кэш сейчас", "Очистити кеш зараз", "Clean the cache now", "Vider le cache maintenant",
     "Limpiar la caché ahora", "Limpar o cache agora", "Cache jetzt leeren", "Tyhjennä välimuisti nyt",
     "Bersihkan cache sekarang", "立即清理缓存", "अभी कैश साफ़ करें", "지금 캐시 정리",
     "Önbelleği şimdi temizle", "今すぐキャッシュをクリア"),
    ("Очистить", "Очистити", "Clean", "Vider", "Limpiar", "Limpar", "Leeren", "Tyhjennä", "Bersihkan", "清理",
     "साफ़ करें", "정리", "Temizle", "クリア"),
    ("Удалить таймер и сервис", "Видалити таймер і сервіс", "Remove timer and service",
     "Supprimer la minuterie et le service", "Eliminar el temporizador y el servicio",
     "Remover o temporizador e o serviço", "Timer und Dienst entfernen", "Poista ajastin ja palvelu",
     "Hapus timer dan layanan", "删除定时器和服务", "टाइमर और सेवा हटाएँ", "타이머와 서비스 삭제",
     "Zamanlayıcıyı ve hizmeti kaldır", "タイマーとサービスを削除"),
    ("✖ Удалить", "✖ Видалити", "✖ Delete", "✖ Supprimer", "✖ Eliminar", "✖ Excluir", "✖ Löschen",
     "✖ Poista", "✖ Hapus", "✖ 删除", "✖ हटाएँ", "✖ 삭제", "✖ Sil", "✖ 削除"),
    ("Таймер ещё не создан", "Таймер ще не створено", "The timer hasn't been created yet",
     "La minuterie n'a pas encore été créée", "El temporizador aún no se ha creado",
     "O temporizador ainda não foi criado", "Der Timer wurde noch nicht erstellt",
     "Ajastinta ei ole vielä luotu", "Timer belum dibuat", "定时器尚未创建", "टाइमर अभी बनाया नहीं गया",
     "타이머가 아직 생성되지 않았습니다", "Zamanlayıcı henüz oluşturulmadı", "タイマーはまだ作成されていません"),
    ("Таймер неактивен", "Таймер неактивний", "The timer is inactive", "La minuterie est inactive",
     "El temporizador está inactivo", "O temporizador está inativo", "Der Timer ist inaktiv",
     "Ajastin ei ole aktiivinen", "Timer tidak aktif", "定时器未启用", "टाइमर निष्क्रिय है",
     "타이머가 비활성 상태입니다", "Zamanlayıcı etkin değil", "タイマーは無効です"),
    ("Активен", "Активний", "Active", "Actif", "Activo", "Ativo", "Aktiv", "Aktiivinen", "Aktif", "已启用",
     "सक्रिय", "활성", "Etkin", "有効"),
    ("следующий запуск: {}", "наступний запуск: {}", "next run: {}", "prochaine exécution : {}",
     "próxima ejecución: {}", "próxima execução: {}", "nächster Lauf: {}", "seuraava ajo: {}",
     "eksekusi berikutnya: {}", "下次运行：{}", "अगला रन: {}", "다음 실행: {}", "sonraki çalışma: {}",
     "次回実行: {}"),
    ("время следующего запуска неизвестно", "час наступного запуску невідомий", "next run time unknown",
     "heure de la prochaine exécution inconnue", "hora de la próxima ejecución desconocida",
     "horário da próxima execução desconhecido", "Zeitpunkt des nächsten Laufs unbekannt",
     "seuraavan ajon aikaa ei tiedetä", "waktu eksekusi berikutnya tidak diketahui", "下次运行时间未知",
     "अगले रन का समय अज्ञात", "다음 실행 시간을 알 수 없음", "sonraki çalışma zamanı bilinmiyor",
     "次回実行時刻は不明"),
    ("Таймер включён ({})", "Таймер увімкнено ({})", "Timer enabled ({})", "Minuterie activée ({})",
     "Temporizador activado ({})", "Temporizador ativado ({})", "Timer aktiviert ({})",
     "Ajastin käytössä ({})", "Timer diaktifkan ({})", "定时器已启用（{}）", "टाइमर चालू ({})",
     "타이머 켜짐({})", "Zamanlayıcı etkinleştirildi ({})", "タイマーを有効にしました（{}）"),
    ("Таймер выключен", "Таймер вимкнено", "Timer disabled", "Minuterie désactivée",
     "Temporizador desactivado", "Temporizador desativado", "Timer deaktiviert", "Ajastin pois käytöstä",
     "Timer dinonaktifkan", "定时器已关闭", "टाइमर बंद", "타이머 꺼짐", "Zamanlayıcı devre dışı",
     "タイマーを無効にしました"),
    ("Кэш очищен", "Кеш очищено", "Cache cleaned", "Cache vidé", "Caché limpiada", "Cache limpo",
     "Cache geleert", "Välimuisti tyhjennetty", "Cache dibersihkan", "缓存已清理", "कैश साफ़ किया गया",
     "캐시를 정리했습니다", "Önbellek temizlendi", "キャッシュをクリアしました"),
    ("Таймер и сервис очистки удалены", "Таймер і сервіс очищення видалено",
     "Cleaning timer and service removed", "Minuterie et service de nettoyage supprimés",
     "Temporizador y servicio de limpieza eliminados", "Temporizador e serviço de limpeza removidos",
     "Reinigungs-Timer und -Dienst entfernt", "Tyhjennysajastin ja -palvelu poistettu",
     "Timer dan layanan pembersihan dihapus", "已删除清理定时器和服务",
     "सफ़ाई टाइमर और सेवा हटाई गई", "정리 타이머와 서비스를 삭제했습니다",
     "Temizlik zamanlayıcısı ve hizmeti kaldırıldı", "クリーンアップのタイマーとサービスを削除しました"),
    ("cacheclean: удаление", "cacheclean: видалення", "cacheclean: removal", "cacheclean : suppression",
     "cacheclean: eliminación", "cacheclean: remoção", "cacheclean: Entfernen", "cacheclean: poisto",
     "cacheclean: penghapusan", "cacheclean：删除", "cacheclean: हटाना", "cacheclean: 삭제",
     "cacheclean: kaldırma", "cacheclean: 削除"),
    ("Удалить таймер очистки кэша?", "Видалити таймер очищення кешу?", "Remove the cache cleaning timer?",
     "Supprimer la minuterie de nettoyage du cache ?", "¿Eliminar el temporizador de limpieza de caché?",
     "Remover o temporizador de limpeza de cache?", "Cache-Bereinigungs-Timer entfernen?",
     "Poistetaanko välimuistin tyhjennysajastin?", "Hapus timer pembersihan cache?",
     "要删除缓存清理定时器吗？", "कैश सफ़ाई टाइमर हटाएँ?", "캐시 정리 타이머를 삭제할까요?",
     "Önbellek temizleme zamanlayıcısı kaldırılsın mı?", "キャッシュのクリーンアップ用タイマーを削除しますか？"),
    ("Таймер отключится, файлы cacheclean.timer, cacheclean.service и drop-in 99-pixeltweak.conf будут удалены (копии останутся в бэкапах).",
     "Таймер вимкнеться, файли cacheclean.timer, cacheclean.service і drop-in 99-pixeltweak.conf буде видалено (копії залишаться в резервних копіях).",
     "The timer will be disabled and the files cacheclean.timer, cacheclean.service and the drop-in 99-pixeltweak.conf will be deleted (copies stay in the backups).",
     "La minuterie sera désactivée, les fichiers cacheclean.timer, cacheclean.service et le drop-in 99-pixeltweak.conf seront supprimés (des copies resteront dans les sauvegardes).",
     "El temporizador se desactivará y los archivos cacheclean.timer, cacheclean.service y el drop-in 99-pixeltweak.conf se eliminarán (quedarán copias en las copias de seguridad).",
     "O temporizador será desativado e os arquivos cacheclean.timer, cacheclean.service e o drop-in 99-pixeltweak.conf serão excluídos (cópias permanecerão nos backups).",
     "Der Timer wird deaktiviert, die Dateien cacheclean.timer, cacheclean.service und das Drop-in 99-pixeltweak.conf werden gelöscht (Kopien bleiben in den Backups).",
     "Ajastin poistetaan käytöstä ja tiedostot cacheclean.timer, cacheclean.service sekä drop-in 99-pixeltweak.conf poistetaan (kopiot jäävät varmuuskopioihin).",
     "Timer akan dinonaktifkan, berkas cacheclean.timer, cacheclean.service, dan drop-in 99-pixeltweak.conf akan dihapus (salinannya tetap ada di cadangan).",
     "定时器将被停用，文件 cacheclean.timer、cacheclean.service 和 drop-in 99-pixeltweak.conf 将被删除（副本仍保留在备份中）。",
     "टाइमर बंद हो जाएगा, फ़ाइलें cacheclean.timer, cacheclean.service और drop-in 99-pixeltweak.conf हटा दी जाएँगी (प्रतियाँ बैकअप में रहेंगी)।",
     "타이머가 비활성화되고 cacheclean.timer, cacheclean.service 파일과 drop-in 99-pixeltweak.conf가 삭제됩니다(사본은 백업에 남습니다).",
     "Zamanlayıcı devre dışı kalacak, cacheclean.timer, cacheclean.service dosyaları ve 99-pixeltweak.conf drop-in'i silinecek (kopyalar yedeklerde kalır).",
     "タイマーが無効になり、cacheclean.timer・cacheclean.service ファイルと drop-in 99-pixeltweak.conf が削除されます（コピーはバックアップに残ります）。"),
    ("Скрипт cacheclean.sh и чужие drop-in'ы (например 30min.conf) не затрагиваются.",
     "Скрипт cacheclean.sh і чужі drop-in (наприклад 30min.conf) не чіпаються.",
     "The cacheclean.sh script and other drop-ins (for example 30min.conf) are not touched.",
     "Le script cacheclean.sh et les autres drop-ins (par ex. 30min.conf) ne sont pas touchés.",
     "El script cacheclean.sh y otros drop-ins (p. ej. 30min.conf) no se tocan.",
     "O script cacheclean.sh e outros drop-ins (por exemplo, 30min.conf) não são afetados.",
     "Das Skript cacheclean.sh und fremde Drop-ins (z. B. 30min.conf) bleiben unberührt.",
     "Komentosarjaa cacheclean.sh ja muita drop-in-tiedostoja (esim. 30min.conf) ei kosketa.",
     "Skrip cacheclean.sh dan drop-in lain (mis. 30min.conf) tidak disentuh.",
     "脚本 cacheclean.sh 和其他 drop-in（例如 30min.conf）不受影响。",
     "स्क्रिप्ट cacheclean.sh और अन्य drop-in (जैसे 30min.conf) अछूते रहते हैं।",
     "cacheclean.sh 스크립트와 다른 drop-in(예: 30min.conf)은 건드리지 않습니다.",
     "cacheclean.sh betiğine ve diğer drop-in'lere (örn. 30min.conf) dokunulmaz.",
     "cacheclean.sh スクリプトと他の drop-in（例: 30min.conf）には手を付けません。"),
    ("интервал {}", "інтервал {}", "interval {}", "intervalle {}", "intervalo {}", "intervalo {}", "Intervall {}",
     "aikaväli {}", "interval {}", "间隔 {}", "अंतराल {}", "간격 {}", "aralık {}", "間隔 {}"),
    ("Текущее: {}", "Поточне: {}", "Current: {}", "Actuel : {}", "Actual: {}", "Atual: {}", "Aktuell: {}",
     "Nykyinen: {}", "Saat ini: {}", "当前：{}", "वर्तमान: {}", "현재: {}", "Geçerli: {}", "現在: {}"),
    ("интервал без изменений", "інтервал без змін", "interval unchanged", "intervalle inchangé",
     "intervalo sin cambios", "intervalo sem alterações", "Intervall unverändert", "aikaväli ennallaan",
     "interval tidak berubah", "间隔不变", "अंतराल अपरिवर्तित", "간격 변경 없음", "aralık değişmedi",
     "間隔は変更なし"),
    ("Cache: drop-in PixelTweak откачен (скрипт и остальные drop-in не тронуты)",
     "Cache: drop-in PixelTweak відкочено (скрипт і решта drop-in не змінені)",
     "Cache: PixelTweak drop-in rolled back (script and other drop-ins untouched)",
     "Cache : drop-in PixelTweak restauré (script et autres drop-ins intacts)",
     "Cache: drop-in de PixelTweak revertido (script y otros drop-ins sin cambios)",
     "Cache: drop-in do PixelTweak revertido (script e outros drop-ins intactos)",
     "Cache: PixelTweak-Drop-in zurückgesetzt (Skript und andere Drop-ins unberührt)",
     "Cache: PixelTweakin drop-in palautettu (skripti ja muut drop-init koskemattomia)",
     "Cache: drop-in PixelTweak dikembalikan (skrip dan drop-in lain tidak disentuh)",
     "Cache：已回滚 PixelTweak 的 drop-in（脚本和其他 drop-in 未改动）",
     "Cache: PixelTweak drop-in वापस लाया गया (स्क्रिप्ट और अन्य drop-in अछूते)",
     "Cache: PixelTweak drop-in을 되돌렸습니다(스크립트와 다른 drop-in은 그대로)",
     "Cache: PixelTweak drop-in'i geri alındı (betik ve diğer drop-in'lere dokunulmadı)",
     "Cache: PixelTweak の drop-in を元に戻しました（スクリプトと他の drop-in は変更なし）"),
    ("Уже существующий скрипт очистки кэша (cacheclean.sh) не изменяется.",
     "Наявний скрипт очищення кешу (cacheclean.sh) не змінюється.",
     "An existing cache-cleaning script (cacheclean.sh) is left unchanged.",
     "Un script de nettoyage du cache existant (cacheclean.sh) n'est pas modifié.",
     "Un script de limpieza de caché existente (cacheclean.sh) no se modifica.",
     "Um script de limpeza de cache existente (cacheclean.sh) não é alterado.",
     "Ein vorhandenes Cache-Bereinigungsskript (cacheclean.sh) bleibt unverändert.",
     "Olemassa olevaa välimuistin tyhjennyskomentosarjaa (cacheclean.sh) ei muuteta.",
     "Skrip pembersihan cache yang sudah ada (cacheclean.sh) tidak diubah.",
     "已存在的缓存清理脚本（cacheclean.sh）不会被修改。",
     "मौजूदा कैश-सफ़ाई स्क्रिप्ट (cacheclean.sh) में कोई बदलाव नहीं किया जाता।",
     "기존 캐시 정리 스크립트(cacheclean.sh)는 변경되지 않습니다.",
     "Mevcut önbellek temizleme betiği (cacheclean.sh) değiştirilmez.",
     "既存のキャッシュ清掃スクリプト（cacheclean.sh）は変更されません。"),
]
 
# ══════════════════════════════════════════════════════════════════════
#  Движок перевода
# ══════════════════════════════════════════════════════════════════════
 
_N_TRANSLATIONS = len(CODES) - 1  # без русского
_EXACT = {}
_TEMPLATES = []
 
 
def _build():
    for row in _RAW:
        key, vals = row[0], row[1:]
        if len(vals) != _N_TRANSLATIONS:
            raise ValueError("словарь: %d переводов вместо %d у «%s»" % (len(vals), _N_TRANSLATIONS, key[:40]))
        if "{}" in key:
            rx = re.compile("(.+?)".join(re.escape(p) for p in key.split("{}")), re.S)
            _TEMPLATES.append((len(key.replace("{}", "")), rx, vals))
        else:
            _EXACT[key] = vals
    _TEMPLATES.sort(key=lambda t: -t[0])
 
 
_build()
 
_lang = "ru"
_idx = -1
_TIERS = (" · ", "; ", " — ", ": ")
_SENT = re.compile(r"(?<=[.!?])\s+")
 
 
def set_lang(code):
    global _lang, _idx
    if code not in CODES:
        code = "ru"
    _lang = code
    _idx = CODES.index(code) - 1
 
 
def get_lang():
    return _lang
 
 
def lang_name(code):
    for c, n in LANGS:
        if c == code:
            return n
    return code
 
 
def _fill(tpl, parts):
    chunks = tpl.split("{}")
    out = chunks[0]
    for i, tail in enumerate(chunks[1:]):
        out += (parts[i] if i < len(parts) else "") + tail
    return out
 
 
def _lookup(s):
    vals = _EXACT.get(s)
    if vals is not None:
        return vals[_idx]
    for _n, rx, vals in _TEMPLATES:
        m = rx.fullmatch(s)
        if m:
            return _fill(vals[_idx], [_tr(g) for g in m.groups()])
    return None
 
 
def _tr(s):
    if not s:
        return s
    stripped = s.strip()
    if stripped != s:
        lead = s[: len(s) - len(s.lstrip())]
        trail = s[len(s.rstrip()):]
        return lead + _tr(stripped) + trail
    found = _lookup(s)
    if found is not None:
        return found
    if "\n" in s:
        return "\n".join(_tr(p) if p.strip() else p for p in s.split("\n"))
    sentences = _SENT.split(s)
    if len(sentences) > 1:
        return " ".join(_tr(x) for x in sentences)
    for sep in _TIERS:
        if sep in s:
            return sep.join(_tr(p) for p in s.split(sep))
    return s
 
 
def tr(s):
    """Перевести строку (русский → выбранный язык). Неизвестное остаётся как есть."""
    if _idx < 0 or not isinstance(s, str):
        return s
    return _tr(s)
 
 
# ══════════════════════════════════════════════════════════════════════
#  ЧАСТЬ 2. Слой интерфейса: системная тема + кнопка выбора языка
#  Ядро (pixeltweak_core.py) НЕ изменяется: здесь подменяется только
#  оформление (CSS по теме системы), тосты/диалоги (перевод) и окно-оболочка.
#  Вся логика (helper, polkit, бэкапы, откаты, журнал) работает как раньше.
# ══════════════════════════════════════════════════════════════════════
 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import pixeltweak_core as core  # оригинальное приложение, без изменений
except ImportError as _e:
    sys.stderr.write(
        f"Не найден оригинальный файл ядра pixeltweak_core.py рядом с этим файлом ({_e}).\n"
        "Переименуйте старый (оригинальный) pixeltweak.py в pixeltweak_core.py "
        "и положите его в эту же папку.\n"
    )
    sys.exit(1)
 
from gi.repository import Gtk, Adw, Gdk, Gio, GLib  # noqa: E402  (версии уже заданы в core)
 
 
# ── Пиксельные шрифты: Pixelify Sans (интерфейс) + GNU Unifont (запасной/моно)
def register_local_fonts():
    """Подключает .ttf/.otf из папок fonts/:
       ~/.local/share/pixeltweak/fonts, fonts/ рядом с программой,
       ~/.local/share/easyhelper/fonts (если шрифты уже лежат у EasyHelper)."""
    try:
        import ctypes
        import ctypes.util
        from pathlib import Path
        lib = ctypes.util.find_library("fontconfig")
        if not lib:
            return
        fc = ctypes.CDLL(lib)
        fc.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        fc.FcConfigAppFontAddFile.restype = ctypes.c_int
        data = Path(GLib.get_user_data_dir())
        for d in (data / "pixeltweak" / "fonts",
                  Path(__file__).resolve().parent / "fonts",
                  data / "easyhelper" / "fonts"):
            if d.is_dir():
                for p in sorted(list(d.glob("*.ttf")) + list(d.glob("*.otf"))):
                    fc.FcConfigAppFontAddFile(None, str(p).encode())
    except Exception as e:  # noqa: BLE001
        print("font register error:", e)
 
 
register_local_fonts()
 
# ── Палитры. Тёмная — ровно как в оригинале; светлая — под системную светлую тему.
DARK = dict(core.COLORS)
DARK.update(
    lang_bg="#0f1a3d", lang_fg="#ffffff", lang_hover="#1a2a68", lang_pop="#141f45",
    pop_bg="#2b2b2d", pop_list="#232325",
    wc_bg="rgba(255,255,255,0.10)", wc_hover="rgba(255,255,255,0.17)",
)
 
LIGHT = {
    "window_bg":     "#f3eefa",
    "panel_bg":      "#ffffff",
    "panel_bg2":     "#ece6f6",
    "border_color":  "#c8bbdc",
    "accent_purple": "#8a45f5",
    "accent_orange": "#e07000",
    "text_neutral":  "#241c34",
    "text_muted":    "#5d5070",
    "lang_bg":       "#e3eaff",
    "lang_fg":       "#14204a",
    "lang_hover":    "#d0dcff",
    "lang_pop":      "#ffffff",
    "pop_bg":        "#f6f4fa",
    "pop_list":      "#ffffff",
    "wc_bg":         "rgba(0,0,0,0.08)",
    "wc_hover":      "rgba(0,0,0,0.14)",
}
 
# ══════════════════════════════════════════════════════════════════════
#  ПИКСЕЛЬНЫЙ ДИЗАЙН (скопирован из EasyHelper)
#  Шрифт интерфейса: «Pixelify Sans», запасные: Silkscreen, Press Start 2P,
#  «Unifont» / «Unifont Upper» (покрывает CJK, хинди, корейский и т. д.)
# ══════════════════════════════════════════════════════════════════════
DARK.update(dict(
    window_bg="#181326", panel_bg="#2a2142", panel_bg2="#1e182f", border_color="#4a3d6e",
    accent_purple="#a855f7", text_neutral="#e8e3f3", text_muted="#a29bb8",
    shadow="#0d0916", hover="#34285a", checked="#3b2d63", accent_edge="#6b21a8",
    rowline="#3a3058", title="#d8b4fe",
    lang_bg="#2a2142", lang_fg="#e8e3f3", lang_hover="#34285a", lang_pop="#2a2142",
    pop_bg="#2a2142", pop_list="#1e182f", wc_bg="#2a2142", wc_hover="#34285a",
))
LIGHT.update(dict(
    window_bg="#f6f3fb", panel_bg="#ffffff", panel_bg2="#ece7f6", border_color="#b5a6d6",
    accent_purple="#a855f7", text_neutral="#241c3a", text_muted="#5f5778",
    shadow="#d6cde8", hover="#ece4fa", checked="#e3d6fb", accent_edge="#7e22ce",
    rowline="#e3dcf0", title="#7e22ce",
    lang_bg="#ffffff", lang_fg="#241c3a", lang_hover="#ece4fa", lang_pop="#ffffff",
    pop_bg="#ffffff", pop_list="#f6f3fb", wc_bg="#ffffff", wc_hover="#ece4fa",
))
 
PIXEL_CSS = """
* { font-family: 'Pixelify Sans', 'Silkscreen', 'Press Start 2P', 'Unifont', 'Unifont Upper', sans-serif; }
window, window.csd, window.csd > decoration, window.background,
window.dialog, window.messagedialog, dialog, dialog.csd { border-radius: 0; }
window.background { background-color: @window_bg; color: @text_neutral; }
 
/* ── шапка */
headerbar, window headerbar {
    background-image: none; background-color: @panel_bg2; box-shadow: none; border-radius: 0;
    border: none; border-bottom: 2px solid @border_color; color: @text_neutral; }
 
/* ── кнопки */
button, window headerbar button {
    border-radius: 0; border: 2px solid @border_color; background-image: none;
    background-color: @panel_bg; color: @text_neutral; box-shadow: 2px 2px 0 @shadow;
    padding: 4px 10px; outline: none; }
button:hover, window headerbar button:hover { background-image: none; background-color: @hover; }
button:active, button:checked, window headerbar button:active { box-shadow: none; background-color: @checked; }
button.suggested-action, button.accent-btn {
    background-image: none; background-color: @accent_purple; color: #ffffff; font-weight: 600;
    border: 2px solid @accent_edge; border-radius: 0; box-shadow: 3px 3px 0 @shadow; }
button.suggested-action:hover { background-color: #b66cfa; }
button.suggested-action:active { box-shadow: none; }
button.destructive-action, window headerbar button.destructive-action {
    background-image: none; background-color: #dc2626; color: #ffffff;
    border: 2px solid #7f1d1d; border-radius: 0; box-shadow: 3px 3px 0 @shadow; }
button.destructive-action:hover { background-color: #ef4444; }
button.destructive-action:active { box-shadow: none; }
 
/* ── «Журнал» и вкладки */
window headerbar button.log-btn {
    background-image: none; background-color: @panel_bg; color: @text_neutral;
    border: 2px solid @border_color; border-radius: 0; padding: 4px 12px; min-height: 28px;
    font-weight: 700; box-shadow: 2px 2px 0 @shadow; }
window headerbar button.log-btn:hover { background-image: none; background-color: @hover; }
window headerbar button.log-btn:active { box-shadow: none; }
.tab-switcher button, window headerbar .tab-switcher button {
    background-image: none; background-color: transparent; color: @text_neutral;
    border: 2px solid @border_color; border-radius: 0; margin: 0 4px; padding: 4px 14px;
    min-height: 28px; font-weight: 600; box-shadow: 2px 2px 0 @shadow; }
.tab-switcher button:hover, window headerbar .tab-switcher button:hover {
    background-image: none; background-color: @hover; }
.tab-switcher button:checked, window headerbar .tab-switcher button:checked {
    background-image: none; background-color: @checked; border-color: @accent_purple; box-shadow: none; }
.tab-bar { background-color: @panel_bg2; border-bottom: 2px solid @border_color; padding: 6px 8px; }
 
/* ── кнопка языка */
.lang-menu > button {
    background-image: none; background-color: @lang_bg; color: @lang_fg;
    border: 2px solid @border_color; border-radius: 0; padding: 4px 10px; min-height: 28px;
    box-shadow: 2px 2px 0 @shadow; }
.lang-menu > button:hover, .lang-menu > button:checked {
    background-image: none; background-color: @lang_hover; color: @lang_fg; }
.lang-menu > button:active { box-shadow: none; }
 
/* ── кнопки окна (свернуть / развернуть / закрыть) */
window headerbar windowcontrols button, window headerbar windowcontrols button.titlebutton {
    background-image: none; background-color: @wc_bg; color: @text_neutral;
    border: 2px solid @border_color; border-radius: 0; box-shadow: 2px 2px 0 @shadow;
    min-width: 22px; min-height: 22px; padding: 2px 4px; outline: none; }
window headerbar windowcontrols button:hover, window headerbar windowcontrols button:focus,
window headerbar windowcontrols button:focus-visible {
    background-image: none; background-color: @wc_hover; border-radius: 0; }
window headerbar windowcontrols button:active, window headerbar windowcontrols button:checked {
    background-image: none; background-color: @checked; box-shadow: none; border-radius: 0; }
 
/* ── поп-ап меню, выбор языка, подсказки, тосты */
popover > contents, popover.lang-pop > contents, popover.menu > contents {
    background-color: @panel_bg; color: @text_neutral; border: 2px solid @border_color;
    border-radius: 0; box-shadow: 4px 4px 0 @shadow; padding: 8px; }
popover > arrow { background: transparent; border: none; box-shadow: none; }
popover list, popover row, popover modelbutton { background: transparent; border-radius: 0; }
popover row:hover, popover modelbutton:hover { background-color: @hover; }
.lang-search, searchentry.lang-search {
    background-image: none; background-color: @panel_bg; color: @text_neutral;
    border: 2px solid @border_color; border-radius: 0; box-shadow: none; min-height: 36px; margin-bottom: 8px; }
.lang-search:focus-within { border-color: @accent_purple; box-shadow: 2px 2px 0 @accent_purple; }
.lang-list { background-color: @pop_list; color: @text_neutral; border: 2px solid @border_color; border-radius: 0; }
.lang-list > row { background-color: transparent; color: @text_neutral; border-radius: 0;
    border-bottom: 2px solid @rowline; padding: 7px 12px; font-weight: 500; }
.lang-list > row:last-child { border-bottom: none; }
.lang-list > row:hover { background-color: @hover; }
.lang-list > row:active, .lang-list > row:selected { background-color: @checked; }
.lang-list > row.active { background-color: @checked; }
tooltip, tooltip.background {
    background-color: @panel_bg; color: @text_neutral; border: 2px solid @border_color;
    border-radius: 0; box-shadow: 3px 3px 0 @shadow; }
tooltip > box { background: transparent; }
toast { background-color: @panel_bg; color: @text_neutral; border: 2px solid @border_color;
    border-radius: 0; box-shadow: 3px 3px 0 @shadow; }
 
/* ── диалоги (Adw.MessageDialog / AlertDialog) */
window.messagedialog, window.dialog, dialog.alert, .alert-sheet {
    background-color: @window_bg; color: @text_neutral; border: 2px solid @border_color;
    border-radius: 0; box-shadow: 4px 4px 0 @shadow; }
 
/* ── карточки, списки, строки */
list.boxed-list, list.card, .card, .boxed-list {
    background-color: @panel_bg; color: @text_neutral; border: 2px solid @border_color;
    border-radius: 0; box-shadow: 4px 4px 0 @shadow; }
list.boxed-list > row, list.card > row, row, row.activatable, row.card {
    border-radius: 0; background-color: transparent; }
list.boxed-list > row, list.card > row { border-bottom: 2px solid @rowline; }
list.boxed-list > row:last-child, list.card > row:last-child { border-bottom: none; }
row:hover { background-color: @hover; }
preferencesgroup > box > label.heading, preferencesgroup > box > box > label.heading,
.title-1, .title-2, .title-3, .title-4, .heading { color: @title; font-weight: 700; }
.dim-label, .dim, .caption, row subtitle, row .subtitle { color: @text_muted; }
 
/* ── поля ввода, выпадающие списки, счётчики */
entry, searchentry, spinbutton, spinbutton text, dropdown > button, combobox > box > button,
row.entry, row.spin, row.combo {
    background-image: none; background-color: @panel_bg; color: @text_neutral;
    border: 2px solid @border_color; border-radius: 0; box-shadow: none; }
entry:focus-within, searchentry:focus-within, spinbutton:focus-within {
    border-color: @accent_purple; box-shadow: 2px 2px 0 @accent_purple; }
spinbutton button { border-radius: 0; box-shadow: none; border-width: 0 0 0 2px; }
 
/* ── переключатели, чекбоксы, ползунки, прогресс */
switch { border-radius: 0; border: 2px solid @border_color; background-color: @panel_bg2; box-shadow: none; }
switch:checked { background-color: @accent_purple; border-color: @accent_edge; }
switch slider { border-radius: 0; background-color: @text_neutral; background-image: none;
    border: 2px solid @shadow; box-shadow: none; }
check, radio { border-radius: 0; border: 2px solid @border_color; background-color: @panel_bg; background-image: none; }
check:checked, radio:checked { background-color: @accent_purple; border-color: @accent_edge; color: #ffffff; }
scale trough, scale highlight, progressbar trough, progressbar progress, levelbar trough, levelbar block {
    border-radius: 0; }
scale trough, progressbar trough { background-color: @panel_bg2; border: 2px solid @border_color; min-height: 8px; }
scale highlight, progressbar progress { background-color: @accent_purple; border: none; }
scale slider { border-radius: 0; background-color: @accent_purple; background-image: none;
    border: 2px solid @accent_edge; box-shadow: none; min-width: 14px; min-height: 14px; }
 
/* ── полосы прокрутки */
scrollbar trough { background-color: @panel_bg; border-radius: 0; }
scrollbar slider { background-color: @accent_purple; border: 2px solid @accent_edge; border-radius: 0;
    min-width: 10px; min-height: 10px; }
scrolledwindow, viewport { background-color: transparent; }
"""
 
# Оформление поверх ядра:
#  • кнопка языка — компактная, тёмно-синяя, как на фото;
#  • окно выбора языка — с поиском и двумя колонками (родное и английское название);
#  • «Журнал» и вкладки сверху — скруглённые, с фиолетовой обводкой;
#  • кнопки окна (свернуть / развернуть / закрыть) — без фиолетового свечения;
#  • вторая строка со вкладками для узкого окна.
LANG_CSS = """
/* ── кнопка языка ── */
.lang-menu > button {
    background-image: none;
    background-color: @lang_bg;
    color: @lang_fg;
    border: none;
    border-radius: 10px;
    padding: 2px 10px;
    min-height: 28px;
    box-shadow: none;
    outline: none;
}
.lang-menu > button:hover,
.lang-menu > button:checked {
    background-image: none;
    background-color: @lang_hover;
    color: @lang_fg;
}
.lang-menu .lang-name {
    font-weight: 700;
    color: @lang_fg;
}
.lang-menu .lang-globe {
    font-size: 15px;
}
.lang-menu image {
    color: @lang_fg;
}
 
/* ── окно выбора языка ── */
popover.lang-pop > contents {
    background-color: @pop_bg;
    color: @text_neutral;
    border-radius: 16px;
    border: 1px solid @border_color;
    padding: 10px;
}
.lang-search {
    background-image: none;
    background-color: @pop_list;
    color: @text_neutral;
    border: 1px solid @border_color;
    border-radius: 9px;
    min-height: 36px;
    margin-bottom: 8px;
    box-shadow: none;
}
.lang-search:focus-within {
    border-color: @accent_purple;
    box-shadow: 0 0 0 1px @accent_purple;
}
.lang-list {
    background-color: @pop_list;
    color: @text_neutral;
    border-radius: 6px;
}
.lang-list > row {
    background-color: transparent;
    color: @text_neutral;
    padding: 7px 12px;
    font-weight: 500;
}
.lang-list > row:hover {
    background-color: alpha(@text_neutral, 0.10);
}
.lang-list > row:active,
.lang-list > row:selected {
    background-color: alpha(@text_neutral, 0.16);
}
.lang-list > row.active {
    background-color: alpha(@text_neutral, 0.06);
}
.lang-sub {
    font-size: 11px;
    color: @text_muted;
}
.lang-check {
    color: @text_neutral;
}
 
/* ── «Журнал» и вкладки сверху ── */
window headerbar button.log-btn {
    background-image: none;
    background-color: alpha(@accent_purple, 0.20);
    color: @text_neutral;
    border: 1px solid @accent_purple;
    border-radius: 9px;
    padding: 2px 12px;
    min-height: 28px;
    font-weight: 700;
    box-shadow: inset 0 0 0 1px alpha(@accent_purple, 0.25);
    outline: none;
}
window headerbar button.log-btn:hover {
    background-image: none;
    background-color: alpha(@accent_purple, 0.32);
}
.tab-switcher button,
window headerbar .tab-switcher button {
    background-image: none;
    background-color: alpha(@accent_purple, 0.12);
    color: @text_neutral;
    border: 1px solid alpha(@accent_purple, 0.70);
    border-radius: 9px;
    margin: 0 3px;
    padding: 2px 12px;
    min-height: 28px;
    font-weight: 600;
    box-shadow: none;
    outline: none;
}
.tab-switcher button:hover,
window headerbar .tab-switcher button:hover {
    background-image: none;
    background-color: alpha(@accent_purple, 0.24);
}
.tab-switcher button:checked,
window headerbar .tab-switcher button:checked {
    background-image: none;
    background-color: alpha(@accent_purple, 0.40);
    border-color: @accent_purple;
    box-shadow: inset 0 0 0 1px alpha(@accent_purple, 0.30);
}
.tab-bar {
    background-color: @panel_bg;
    border-bottom: 1px solid @border_color;
    padding: 5px 8px;
}
 
/* ── кнопки окна: просто серые кружки, без фиолетового ── */
window headerbar windowcontrols button,
window headerbar windowcontrols button.titlebutton {
    background-image: none;
    background-color: @wc_bg;
    color: @text_neutral;
    border: none;
    box-shadow: none;
    outline: none;
}
window headerbar windowcontrols button:hover,
window headerbar windowcontrols button:active,
window headerbar windowcontrols button:focus,
window headerbar windowcontrols button:focus-visible,
window headerbar windowcontrols button:checked {
    background-image: none;
    background-color: @wc_hover;
    color: @text_neutral;
    border: none;
    box-shadow: none;
    outline: none;
}
"""
 
# ── Сохранение выбранного языка
LANG_FILE = os.path.join(
    os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"),
    "pixeltweak", "lang",
)
 
 
def load_lang() -> str:
    code = core.read_file(LANG_FILE).strip()
    return code if code in CODES else "ru"
 
 
def save_lang(code: str):
    try:
        os.makedirs(os.path.dirname(LANG_FILE), exist_ok=True)
        with open(LANG_FILE, "w", encoding="utf-8") as f:
            f.write(code + "\n")
    except OSError:
        pass
 
 
# ── Перевод всплывающих сообщений и диалогов (подмена функций ядра)
_orig_ask = core.ask
 
 
def ask(parent, heading, body, options, on_choice, extra=None, cancel_label="Отмена"):
    opts = [(rid, tr(label), destructive) for rid, label, destructive in options]
    _orig_ask(parent, tr(heading), tr(body), opts, on_choice, extra, tr(cancel_label))
 
 
def toast(text: str, details: bool = False):
    overlay = core._toast_overlay
    if overlay is None:
        return
    t = Adw.Toast.new(tr(text)[:200])
    if hasattr(t, "set_use_markup"):
        t.set_use_markup(False)
    if details:
        t.set_button_label(tr("Подробности"))
        t.set_action_name("win.show-log")
        t.set_timeout(10)
    overlay.add_toast(t)
 
 
core.ask = ask
core.toast = toast
 
 
# ── Перевод виджетов страниц (заголовки, подписи, кнопки, списки)
def _bind(obj, prop, getter, setter):
    """Переводит текущее значение и все последующие (асинхронные обновления статусов)."""
    key = "_pt_last_" + prop
 
    def apply(*_a):
        try:
            cur = getter()
        except Exception:  # noqa: BLE001
            return
        if not cur or cur == getattr(obj, key, None):
            return
        new = tr(cur)
        setattr(obj, key, new)
        if new != cur:
            setter(new)
 
    apply()
    obj.connect("notify::" + prop, apply)
 
 
def _translate_combo(row):
    model = row.get_model()
    if not isinstance(model, Gtk.StringList):
        return
    items = [model.get_string(i) for i in range(model.get_n_items())]
    new = [tr(t) for t in items]
    if new != items:
        selected = row.get_selected()
        row.set_model(Gtk.StringList.new(new))
        row.set_selected(selected)
 
 
_FALLBACK_ICONS = (
    "dialog-information-symbolic", "help-about-symbolic",
    "emblem-system-symbolic", "preferences-system-symbolic",
    "applications-system-symbolic", "view-more-symbolic",
)


def _icon_theme():
    try:
        return Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
    except Exception:  # noqa: BLE001
        return None


def _fallback_icon_name():
    theme = _icon_theme()
    if theme is None:
        return None
    for name in _FALLBACK_ICONS:
        try:
            if theme.has_icon(name):
                return name
        except Exception:  # noqa: BLE001
            pass
    return None


def _fix_missing_icon(img):
    """Если иконки нет в теме — подставляем запасную (или прячем), чтобы не было белого квадрата."""
    if getattr(img, "_pt_fixing", False):
        return
    try:
        name = img.get_icon_name()
    except Exception:  # noqa: BLE001
        return
    if not name:
        return
    theme = _icon_theme()
    if theme is None:
        return
    try:
        if theme.has_icon(name):
            return
    except Exception:  # noqa: BLE001
        return
    img._pt_fixing = True
    try:
        fb = _fallback_icon_name()
        if fb:
            img.set_from_icon_name(fb)
        else:
            img.set_visible(False)
    finally:
        img._pt_fixing = False


def localize(root):
    def visit(w):
        if isinstance(w, Adw.PreferencesGroup):
            _bind(w, "title", w.get_title, w.set_title)
            _bind(w, "description", w.get_description, w.set_description)
        elif isinstance(w, Adw.PreferencesRow):
            _bind(w, "title", w.get_title, w.set_title)
            if isinstance(w, Adw.ActionRow):
                _bind(w, "subtitle", w.get_subtitle, w.set_subtitle)
                try:
                    ico = w.get_icon_name()
                    theme = _icon_theme()
                    if ico and theme is not None and not theme.has_icon(ico):
                        fb = _fallback_icon_name()
                        if fb:
                            w.set_icon_name(fb)
                except Exception:  # noqa: BLE001
                    pass
            if isinstance(w, Adw.ComboRow):
                _translate_combo(w)
        elif isinstance(w, Gtk.Button):
            if w.get_label():
                _bind(w, "label", w.get_label, w.set_label)
        elif isinstance(w, Gtk.Image):
            _fix_missing_icon(w)
            if not getattr(w, "_pt_icon_hooked", False):
                w._pt_icon_hooked = True
                w.connect("notify::icon-name", lambda img, _p: _fix_missing_icon(img))
        child = w.get_first_child()
        while child is not None:
            visit(child)
            child = child.get_next_sibling()

    visit(root)
 
 
# Ширина (sp), при которой вкладки уходят из шапки во вторую строку,
# и ширина, при которой «Журнал» и язык сжимаются до значков.
WIDTH_TABS_ROW = 900
WIDTH_COMPACT = 440
 
 
# ── Приложение
class App(core.PixelTweakApp):
    def on_activate(self, app):
        win = self.props.active_window
        if win is not None:
            win.present()
            return
 
        set_lang(load_lang())
 
        # CSS подгружается заново при смене системной темы (светлая ↔ тёмная)
        self.css = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), self.css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        sm = Adw.StyleManager.get_default()
        sm.set_color_scheme(Adw.ColorScheme.DEFAULT)  # следуем системной теме
        sm.connect("notify::dark", lambda *_a: self.apply_css())
        self.apply_css()
 
        win = Adw.ApplicationWindow(application=app)
        win.set_title(core.APP_NAME)
        win.set_default_size(940, 760)
        win.set_size_request(320, 360)  # окно можно сильно сузить
        self.win = win
 
        log_action = Gio.SimpleAction.new("show-log", None)
        log_action.connect("activate", lambda *_a: core.show_log(win))
        win.add_action(log_action)
 
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self._pages = []
 
        # вкладки в шапке (широкое окно)
        switcher = Gtk.StackSwitcher()
        switcher.set_stack(self.stack)
        switcher.remove_css_class("linked")
        switcher.add_css_class("tab-switcher")
        self.header_tabs = Gtk.ScrolledWindow()
        self.header_tabs.set_policy(Gtk.PolicyType.EXTERNAL, Gtk.PolicyType.NEVER)
        self.header_tabs.set_propagate_natural_width(True)
        self.header_tabs.set_min_content_width(240)
        self.header_tabs.set_child(switcher)
 
        # те же вкладки отдельной строкой (узкое окно)
        switcher2 = Gtk.StackSwitcher()
        switcher2.set_stack(self.stack)
        switcher2.remove_css_class("linked")
        switcher2.add_css_class("tab-switcher")
        switcher2.set_halign(Gtk.Align.CENTER)
        bar_scroll = Gtk.ScrolledWindow()
        bar_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        bar_scroll.set_hexpand(True)
        bar_scroll.set_child(switcher2)
        self.tab_bar = Gtk.Box()
        self.tab_bar.add_css_class("tab-bar")
        self.tab_bar.append(bar_scroll)
        self.tab_bar.set_visible(False)
 
        header = Adw.HeaderBar()
        header.set_title_widget(self.header_tabs)
 
        # кнопка «Журнал» с иконкой-свитком
        self.log_btn = Gtk.Button()
        self.log_btn.add_css_class("log-btn")
        log_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.log_icon = Gtk.Label(label="📜")
        self.log_text = Gtk.Label()
        log_box.append(self.log_icon)
        log_box.append(self.log_text)
        self.log_btn.set_child(log_box)
        self.log_btn.connect("clicked", lambda _b: core.show_log(win))
        header.pack_start(self.log_btn)
 
        core._cancel_btn = Gtk.Button()
        core._cancel_btn.add_css_class("destructive-action")
        core._cancel_btn.set_visible(False)
        core._cancel_btn.connect("clicked", core.cancel_current_job)
        header.pack_start(core._cancel_btn)
 
        header.pack_end(self.build_lang_button())
 
        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        toolbar.add_top_bar(self.tab_bar)
        toolbar.set_content(self.stack)
 
        core._toast_overlay = Adw.ToastOverlay()
        core._toast_overlay.set_child(toolbar)
        win.set_content(core._toast_overlay)
 
        self.setup_adaptive(win)
 
        def fix_arrows(*_a):
            GLib.idle_add(lambda: (core.kill_popover_arrows(win), False)[1])
 
        win.connect("map", fix_arrows)
        self.stack.connect("notify::visible-child", fix_arrows)
 
        self.refresh_lang_ui()
        self.build_pages()
        win.present()
 
    # ── адаптация под маленькое окно ─────────────────────────────────
    def setup_adaptive(self, win):
        """Вкладки уходят во вторую строку, а «Журнал»/язык сжимаются до значков."""
        try:
            bp1 = Adw.Breakpoint.new(
                Adw.BreakpointCondition.parse("max-width: %dsp" % WIDTH_TABS_ROW))
            bp1.add_setter(self.header_tabs, "visible", False)
            bp1.add_setter(self.tab_bar, "visible", True)
            win.add_breakpoint(bp1)
 
            bp2 = Adw.Breakpoint.new(
                Adw.BreakpointCondition.parse("max-width: %dsp" % WIDTH_COMPACT))
            bp2.add_setter(self.lang_label, "visible", False)
            bp2.add_setter(self.log_text, "visible", False)
            win.add_breakpoint(bp2)
        except Exception:  # noqa: BLE001  (libadwaita < 1.4 — запасной вариант)
            state = {"w": -1}
 
            def tick(_widget, _clock):
                w = win.get_width()
                if w != state["w"] and w > 0:
                    state["w"] = w
                    tabs_row = w <= WIDTH_TABS_ROW
                    compact = w <= WIDTH_COMPACT
                    self.header_tabs.set_visible(not tabs_row)
                    self.tab_bar.set_visible(tabs_row)
                    self.lang_label.set_visible(not compact)
                    self.log_text.set_visible(not compact)
                return GLib.SOURCE_CONTINUE
 
            win.add_tick_callback(tick)
 
    # ── тема ─────────────────────────────────────────────────────────
    def apply_css(self):
        palette = DARK if Adw.StyleManager.get_default().get_dark() else LIGHT
        css = re.sub(
            r"@(\w+)",
            lambda m: palette.get(m.group(1)) or DARK[m.group(1)],
            core.CSS_TEMPLATE + LANG_CSS + PIXEL_CSS,
        )
        self.css.load_from_data(css.encode("utf-8"))
 
    # ── кнопка языка и окно выбора ───────────────────────────────────
    def build_lang_button(self):
        btn = Gtk.MenuButton()
        btn.add_css_class("lang-menu")
        btn.set_valign(Gtk.Align.CENTER)
        self.lang_btn = btn
 
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
        globe = Gtk.Label(label="🌐")
        globe.add_css_class("lang-globe")
        self.lang_label = Gtk.Label()
        self.lang_label.add_css_class("lang-name")
        chevron = Gtk.Image.new_from_icon_name("pan-down-symbolic")
        box.append(globe)
        box.append(self.lang_label)
        box.append(chevron)
        btn.set_child(box)
 
        self.pop = Gtk.Popover()
        self.pop.add_css_class("lang-pop")
        self.pop.set_has_arrow(False)
 
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
 
        # поиск языка
        self.lang_search = Gtk.SearchEntry()
        self.lang_search.add_css_class("lang-search")
        self.lang_search.connect("search-changed", lambda *_a: self.lang_list.invalidate_filter())
        self.lang_search.connect("activate", self.on_search_activate)
        outer.append(self.lang_search)
 
        # список: родное название слева, английское справа, галочка у текущего
        self.lang_list = Gtk.ListBox()
        self.lang_list.add_css_class("lang-list")
        self.lang_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.lang_list.set_activate_on_single_click(True)
        self.lang_list.set_filter_func(self._lang_filter)
        self.lang_list.connect("row-activated", lambda _l, row: self.on_pick_language(row.code))
 
        self.lang_items = {}
        self.lang_checks = {}
        for code, name in LANGS:
            row = Gtk.ListBoxRow()
            row.code = code
            row.set_activatable(True)
            rbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
            native = Gtk.Label(label=name, xalign=0)
            native.set_hexpand(True)
            english = Gtk.Label(label=LANG_EN.get(code, ""), xalign=1)
            english.add_css_class("lang-sub")
            check = Gtk.Image.new_from_icon_name("object-select-symbolic")
            check.add_css_class("lang-check")
            check.set_opacity(0.0)
            rbox.append(native)
            rbox.append(english)
            rbox.append(check)
            row.set_child(rbox)
            self.lang_list.append(row)
            self.lang_items[code] = row
            self.lang_checks[code] = check
 
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_width(270)
        scroll.set_max_content_height(380)
        scroll.set_propagate_natural_height(True)
        scroll.set_propagate_natural_width(True)
        scroll.set_child(self.lang_list)
        outer.append(scroll)
 
        self.pop.set_child(outer)
        self.pop.connect("show", self.on_pop_show)
        btn.set_popover(self.pop)
        return btn
 
    def _lang_filter(self, row):
        q = self.lang_search.get_text().strip().lower()
        if not q:
            return True
        code = getattr(row, "code", "")
        hay = " ".join((lang_name(code), LANG_EN.get(code, ""), code)).lower()
        return q in hay
 
    def on_pop_show(self, *_a):
        self.lang_search.set_text("")
        self.lang_list.invalidate_filter()
        GLib.idle_add(lambda: (self.lang_search.grab_focus(), False)[1])
 
    def on_search_activate(self, *_a):
        for code, _n in LANGS:
            row = self.lang_items[code]
            if self._lang_filter(row):
                self.on_pick_language(code)
                return
 
    def on_pick_language(self, code):
        self.pop.popdown()
        if code == get_lang():
            return
        set_lang(code)
        save_lang(code)
        self.refresh_lang_ui()
        self.build_pages()
 
    def refresh_lang_ui(self):
        current = get_lang()
        self.lang_label.set_label(lang_name(current))
        self.lang_btn.set_tooltip_text(lang_name(current))
        for code, row in self.lang_items.items():
            if code == current:
                row.add_css_class("active")
                self.lang_checks[code].set_opacity(1.0)
            else:
                row.remove_css_class("active")
                self.lang_checks[code].set_opacity(0.0)
        self.lang_search.set_placeholder_text(tr("Поиск языка…"))
        self.log_text.set_label(tr("Журнал"))
        self.log_btn.set_tooltip_text(tr("Журнал"))
        core._cancel_btn.set_label(tr("Отменить"))
 
    # ── страницы (пересобираются при смене языка) ────────────────────
    def build_pages(self):
        keep = self.stack.get_visible_child_name()
        for page in self._pages:
            self.stack.remove(page)
        self._pages = []
        core._ACTION_BUTTONS.clear()
        specs = [
            (core.page_zram,       "zram",     "💾 ZRAM"),
            (core.page_sysctl,     "sysctl",   "⚙️ " + tr("Ядро")),
            (core.page_earlyoom,   "earlyoom", "🛡️ EarlyOOM"),
            (core.page_gamemode,   "gamemode", "🎮 GameMode"),
            (core.page_cpupower,   "cpu",      "🧠 CPU"),
            (core.page_cacheclean, "cache",    "🧹 Cache"),
        ]
        for builder, name, title in specs:
            page = builder()
            localize(page)
            self.stack.add_titled(page, name, title)
            self._pages.append(page)
        if keep:
            self.stack.set_visible_child_name(keep)
        core.set_busy(core._busy)
        GLib.idle_add(lambda: (localize(self.stack), False)[1])   # ← добавить
        GLib.idle_add(lambda: (core.kill_popover_arrows(self.win), False)[1])
 
 
if __name__ == "__main__":
    if "--uninstall-helper" in sys.argv:
        if os.path.exists(core.HELPER_PATH):
            res = core.run_root([{"op": "uninstall_helper"}])
            ok, msg = core.summarize(res)
            print("Помощник удалён." if ok else f"Ошибка: {msg}")
            sys.exit(0 if ok else 1)
        print("Помощник не установлен.")
        sys.exit(0)
    sys.exit(App().run(sys.argv))
 
