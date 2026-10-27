"""Reproducible original diagrams and animated learning examples."""
from pathlib import Path
from html import escape
import math
import json
import re
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'notes' / 'Вложения' / 'Основы'
QA = Path(tempfile.gettempdir()) / 'backend-brain-visual-qa'
OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
W, H = 1120, 660
STYLE = json.loads(Path(__file__).with_name('visual-style.json').read_text(encoding='utf-8'))
BG, INK, MUTED = (STYLE[key] for key in ('background', 'text', 'muted'))
SURFACE, BORDER, PANEL = (STYLE[key] for key in ('surface', 'border', 'panel'))
FONT_FAMILY = STYLE['font_family']
PRIMARY, SUCCESS, EMPHASIS, SUBDUED, SECONDARY = (STYLE[key] for key in ('primary', 'success', 'emphasis', 'subdued', 'secondary'))
FILLS = {STYLE[key]: value for key, value in STYLE['fills'].items()}
FONTS = Path('C:/Windows/Fonts')


def font(size=22, bold=False):
    return ImageFont.truetype(str(FONTS / ('seguisb.ttf' if bold else 'segoeui.ttf')), size)


class Canvas:
    def __init__(self, title, subtitle='', svg=False):
        self.title = title
        self.im = Image.new('RGB', (W, H), BG)
        self.d = ImageDraw.Draw(self.im)
        self.svg = [] if svg else None
        self.text(40, 27, title, 32, bold=True)
        self.text(40, 78, subtitle, 20, MUTED, width=1040)

    def rect(self, box, fill=SURFACE, outline=BORDER, radius=16, stroke=2):
        self.d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=stroke)
        if self.svg is not None:
            x, y, r, b = box
            self.svg.append(f'<rect x="{x}" y="{y}" width="{r-x}" height="{b-y}" rx="{radius}" fill="{fill}" stroke="{outline}" stroke-width="{stroke}"/>')

    def line(self, points, color=MUTED, stroke=3):
        self.d.line(points, fill=color, width=stroke)
        if self.svg is not None:
            coords = ' '.join(f'{x},{y}' for x, y in points)
            self.svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linejoin="round"/>')

    def circle(self, x, y, r, fill, outline=None, stroke=2):
        self.d.ellipse((x-r, y-r, x+r, y+r), fill=fill, outline=outline, width=stroke)
        if self.svg is not None:
            self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{outline or fill}" stroke-width="{stroke}"/>')

    def text(self, x, y, value, size=22, color=INK, bold=False, width=None, center=False):
        f = font(size, bold)
        lines = []
        for paragraph in str(value).split('\n'):
            current = ''
            for word in paragraph.split(' '):
                candidate = (current+' '+word).strip()
                if width and self.d.textlength(candidate, font=f) > width and current:
                    lines.append(current)
                    current = word
                else:
                    current = candidate
            lines.append(current)
        for line in lines:
            px = x - self.d.textlength(line, font=f)/2 if center else x
            self.d.text((px, y), line, font=f, fill=color, anchor='lt')
            if self.svg is not None:
                weight = 600 if bold else 400
                self.svg.append(f'<text x="{px:.2f}" y="{y}" font-family="{escape(FONT_FAMILY)}" font-size="{size}" font-weight="{weight}" fill="{color}" dominant-baseline="text-before-edge">{escape(line)}</text>')
            y += size+8
        return y

    def arrow(self, start, end, color=PRIMARY, stroke=4, progress=None):
        self.line([start, end], color, stroke)
        angle = math.atan2(end[1]-start[1], end[0]-start[0])
        wing = 11
        points = [(end[0]-wing*math.cos(angle-a), end[1]-wing*math.sin(angle-a)) for a in [-0.5, 0.5]]
        self.line([points[0], end, points[1]], color, stroke)
        if progress is not None:
            x = start[0]+(end[0]-start[0])*progress
            y = start[1]+(end[1]-start[1])*progress
            self.circle(x, y, 8, color)

    def card(self, x, y, w, h, title, body='', color=PRIMARY, active=False):
        self.rect((x, y, x+w, y+h), FILLS[color] if active else SURFACE, color if active else BORDER)
        bottom = self.text(x+20, y+18, title, 23, color, True, w-40)
        if body:
            self.text(x+20, bottom+12, body, 21, INK, width=w-40)

    def banner(self, step, total, title, detail):
        self.rect((40, 490, 1080, 605), PANEL, PANEL)
        self.text(60, 506, f'{step+1} / {total}   {title}', 24, INK, True, 1000)
        self.text(60, 547, detail, 20, MUTED, width=1000)

    def footer(self, text):
        self.text(40, 625, text, 17, MUTED, width=1040)

    def save_svg(self, name):
        payload = '\n'.join(self.svg)
        (OUT / f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"><title>{escape(self.title)}</title><rect width="{W}" height="{H}" fill="{BG}"/>{payload}</svg>', encoding='utf-8')
        self.im.save(QA / f'{name}.png')


def static_diagrams():
    c = Canvas('Компьютер: четыре роли', 'Кто выполняет работу, где находятся данные и как они попадают в систему', True)
    c.card(40, 175, 280, 220, 'ПРОЦЕССОР', 'Инструкции\nВычисления\nРегистры и кэши', PRIMARY, True)
    c.card(405, 175, 310, 220, 'ОПЕРАТИВНАЯ ПАМЯТЬ', 'Рабочие данные\nИнструкции программы\nБуферы обмена', SUCCESS, True)
    c.card(800, 145, 280, 120, 'НАКОПИТЕЛЬ', 'Файлы между запусками', EMPHASIS, True)
    c.card(800, 285, 280, 160, 'СЕТЕВОЙ ИНТЕРФЕЙС', 'Обмен с другими узлами', SECONDARY, True)
    c.arrow((330, 270), (393, 270))
    c.arrow((393, 300), (330, 300), SUCCESS)
    c.arrow((730, 225), (786, 205), EMPHASIS)
    c.arrow((786, 205), (730, 225), EMPHASIS)
    c.arrow((786, 350), (730, 330), SECONDARY)
    c.arrow((730, 330), (786, 350), SECONDARY)
    c.rect((40, 470, 1080, 570), PANEL, PANEL)
    c.text(65, 488, 'Операционная система', 24, bold=True)
    c.text(65, 529, 'Управляет ресурсами и предоставляет программам доступ к ним', 22)
    c.footer('Стрелки показывают обмен данными; точная схема шин и контроллеров здесь опущена.')
    c.save_svg('computer-overview')

    c = Canvas('Байты одинаковые — смысл задаёт формат', 'Биты, числовая интерпретация и кодировка текста', True)
    c.text(40, 135, 'Один байт = 8 бит', 25, bold=True)
    for i in range(8):
        x = 40+i*65
        c.rect((x, 185, x+54, 243), FILLS[PRIMARY], PRIMARY, radius=8)
        c.text(x+27, 197, '1', 28, PRIMARY, True, center=True)
    c.card(650, 130, 430, 145, '11111111', 'Без знака: 255\nДополнительный код: −1', SECONDARY, True)
    c.text(40, 300, 'Текст в UTF-8', 25, bold=True)
    columns = [(40, 'A', 'U+0041', '41', '1 байт'), (405, 'Я', 'U+042F', 'D0 AF', '2 байта'), (770, 'Кодовая позиция', 'U+1F600', 'F0 9F 98 80', '4 байта')]
    for x, title, code, data, size in columns:
        c.card(x, 350, 310, 195, title, f'{code}\nБайты: {data}\n{size}', SUCCESS, True)
    c.footer('Число байт, число кодовых позиций и число видимых символов — разные величины.')
    c.save_svg('data-representation')

    c = Canvas('HDD и SSD: разные способы хранения', 'Характер доступа влияет на задержку и скорость устройства', True)
    c.card(40, 140, 490, 340, 'HDD · магнитный накопитель', '', PRIMARY)
    for r in (92, 67, 42):
        c.circle(175, 305, r, PANEL, PRIMARY)
    c.circle(175, 305, 15, PRIMARY)
    c.line([(255, 220), (195, 290)], EMPHASIS, 11)
    c.circle(255, 220, 12, EMPHASIS)
    c.text(300, 245, 'Вращение\nПеремещение\nголовки', 23, width=205)
    c.card(590, 140, 490, 340, 'SSD · электронная память', '', SUCCESS)
    for row in range(3):
        for col in range(4):
            x, y = 635+col*54, 235+row*54
            c.rect((x, y, x+38, y+38), FILLS[SUCCESS], SUCCESS, radius=5)
    c.text(880, 245, 'Ячейки памяти\nКонтроллер\nБез механики', 22, width=170)
    c.text(40, 520, 'Задержка', 25, PRIMARY, True)
    c.text(40, 560, 'Время одной операции', 21)
    c.text(405, 520, 'Пропускная способность', 25, SUCCESS, True)
    c.text(405, 560, 'Байт за секунду', 21)
    c.text(850, 520, 'IOPS', 25, EMPHASIS, True)
    c.text(850, 560, 'Операций за секунду', 21)
    c.footer('Размер блока, доля чтения и записи и порядок обращений меняют результат.')
    c.save_svg('storage-devices')

    c = Canvas('Граница между приложением и ядром', 'Обычные вычисления выполняет CPU; привилегированные операции проходят через ядро', True)
    c.card(40, 145, 470, 110, 'ПРИЛОЖЕНИЕ A', 'Пользовательское пространство', PRIMARY, True)
    c.card(610, 145, 470, 110, 'ПРИЛОЖЕНИЕ B', 'Пользовательское пространство', SECONDARY, True)
    c.arrow((275, 270), (275, 345), PRIMARY)
    c.arrow((845, 270), (845, 345), SECONDARY)
    c.text(340, 292, 'Системные вызовы', 23, MUTED, True, width=440)
    c.card(40, 360, 1040, 125, 'ЯДРО ОПЕРАЦИОННОЙ СИСТЕМЫ', 'Проверка прав · планирование · память · файлы · драйверы', SUCCESS, True)
    c.arrow((560, 495), (560, 535), SUCCESS)
    c.rect((40, 550, 1080, 602), PANEL, PANEL)
    c.text(560, 562, 'ОБОРУДОВАНИЕ: CPU · RAM · накопители · сеть', 22, center=True)
    c.footer('Переход в ядро не обязательно означает переключение на другую задачу.')
    c.save_svg('kernel-boundary')


def sync_mermaid_style():
    variables = {
        'darkMode': True, 'background': BG, 'fontFamily': FONT_FAMILY,
        'primaryColor': SURFACE, 'primaryTextColor': INK, 'primaryBorderColor': PRIMARY,
        'secondaryColor': PANEL, 'secondaryTextColor': INK, 'secondaryBorderColor': BORDER,
        'tertiaryColor': STYLE['fills']['secondary'], 'tertiaryTextColor': INK, 'tertiaryBorderColor': BORDER,
        'lineColor': PRIMARY, 'textColor': INK, 'mainBkg': SURFACE,
        'edgeLabelBackground': BG, 'nodeTextColor': INK,
        'noteBkgColor': PANEL, 'noteTextColor': INK, 'noteBorderColor': BORDER,
        'actorBkg': SURFACE, 'actorBorder': PRIMARY, 'actorTextColor': INK,
        'actorLineColor': BORDER, 'signalColor': PRIMARY, 'signalTextColor': INK,
        'labelBoxBkgColor': PANEL, 'labelBoxBorderColor': BORDER, 'labelTextColor': INK,
        'loopTextColor': INK, 'activationBkgColor': PANEL, 'activationBorderColor': PRIMARY,
    }
    directive = '%%{init: ' + json.dumps({'theme': 'base', 'themeVariables': variables}, ensure_ascii=False, separators=(',', ':')) + '}%%'
    marker = chr(96)*3 + 'mermaid\n'
    for path in (ROOT / 'notes').rglob('*.md'):
        content = path.read_text(encoding='utf-8')
        updated = re.sub(re.escape(marker) + r'(?:%%\{init: [^\n]*\}%%\n)?', marker + directive + '\n', content)
        if updated != content:
            path.write_text(updated, encoding='utf-8', newline='\n')
    css_path = ROOT / 'notes' / '.obsidian' / 'snippets' / 'reading.css'
    css = css_path.read_text(encoding='utf-8')
    begin, end = '/* BEGIN learning visual theme */', '/* END learning visual theme */'
    css = re.sub(re.escape(begin) + r'.*?' + re.escape(end), '', css, flags=re.S).rstrip()
    block = f'''{begin}
.markdown-rendered .mermaid {{
  background: {BG};
  border-radius: 16px;
  padding: 16px;
  overflow-x: auto;
}}
.markdown-rendered img {{ border-radius: 16px; }}
{end}'''
    css_path.write_text(css + '\n\n' + block + '\n', encoding='utf-8', newline='\n')


def make_gif(name, states, painter):
    frames, durations, samples = [], [], []
    for state in range(len(states)):
        for tick in range(9):
            c = painter(state, tick/8)
            frames.append(c.im)
            durations.append(100 if tick < 8 else (1300 if state == len(states)-1 else 900))
        samples.append(frames[-1].copy())
    # Use a shared palette so stable regions retain their colors across frames.
    atlas = Image.new('RGB', (W, H*len(samples)), BG)
    for i, sample in enumerate(samples):
        atlas.paste(sample, (0, i*H))
    palette = atlas.quantize(colors=128)
    encoded = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in frames]
    encoded[0].save(OUT / f'{name}.gif', save_all=True, append_images=encoded[1:], duration=durations, loop=0, disposal=1, optimize=True)
    sheet = Image.new('RGB', (W*3//2, H*((len(samples)+2)//3)//2), BG)
    for i, sample in enumerate(samples):
        sample = sample.resize((W//2, H//2), Image.Resampling.LANCZOS)
        sheet.paste(sample, ((i % 3)*W//2, (i // 3)*H//2))
    sheet.save(QA / f'{name}-steps.png')


def processor():
    states = [
        ('Прочитать первое значение', 'Адрес 100 → регистр R1: значение 2'),
        ('Прочитать второе значение', 'Адрес 104 → регистр R2: значение 3'),
        ('Выполнить сложение', 'Устройство вычисления складывает 2 и 3'),
        ('Записать результат', 'Значение 5 из регистра передаётся по адресу 108'),
    ]
    def paint(s, p):
        c = Canvas('Процессор: прочитать → вычислить → записать', 'Последовательность действий для сложения двух значений')
        c.card(40, 165, 300, 245, 'ПАМЯТЬ', f'Адрес 100: 2\nАдрес 104: 3\nАдрес 108: {"5" if s == 3 else "—"}', SUCCESS, s in (0, 1, 3))
        c.card(410, 165, 300, 245, 'РЕГИСТРЫ CPU', f'R1: {"5" if s >= 2 else "2"}\nR2: {"3" if s >= 1 else "—"}', PRIMARY, s in (0, 1, 3))
        c.card(780, 165, 300, 245, 'ВЫЧИСЛЕНИЕ', '2 + 3 = 5' if s >= 2 else 'Ожидание данных', EMPHASIS, s == 2)
        if s in (0, 1):
            c.arrow((350, 285), (398, 285), SUCCESS, progress=p)
        elif s == 2:
            c.arrow((720, 285), (768, 285), EMPHASIS, progress=p)
        else:
            c.arrow((398, 285), (350, 285), PRIMARY, progress=p)
        c.banner(s, len(states), *states[s])
        c.footer('Показан порядок действий, без привязки к набору команд и длительности такта.')
        return c
    make_gif('processor-cycle', states, paint)


def cache():
    states = [
        ('Запрос адреса 100: промах', 'В кэше пока нет нужного блока данных'),
        ('Заполнение кэша', 'Из RAM приходит блок, содержащий адреса 100–103'),
        ('Запрос адреса 101: попадание', 'Соседнее значение уже в кэше — RAM не нужна'),
        ('Запрос адреса 200: новый промах', 'Этот адрес относится к другому блоку'),
    ]
    def paint(s, p):
        address = 100 if s < 2 else (101 if s == 2 else 200)
        c = Canvas('Как соседние данные оказываются в кэше', 'Пространственная локальность · схема с одним уровнем кэша')
        c.card(40, 180, 300, 220, 'ПРОЦЕССОР', f'Нужно прочитать\nадрес {address}', PRIMARY, True)
        c.card(410, 180, 300, 220, 'КЭШ CPU', 'Пусто' if s == 0 else '100: 12    101: 34\n102: 56    103: 78', SUCCESS, s in (1, 2))
        c.card(780, 180, 300, 220, 'RAM', 'Блок 100–103\nБлок 200–203\nДругие блоки', EMPHASIS, s in (0, 1, 3))
        if s == 2:
            c.arrow((398, 275), (350, 275), SUCCESS, progress=p)
        else:
            c.arrow((350, 275), (398, 275), PRIMARY, progress=p if s in (0, 3) else None)
        c.arrow((768, 305), (720, 305), SUCCESS if s == 1 else EMPHASIS, progress=p if s == 1 else None)
        c.banner(s, len(states), *states[s])
        c.footer('Адреса и блоки условные; линия кэша содержит сразу несколько соседних значений.')
        return c
    make_gif('cache-locality', states, paint)


def context_switch():
    states = [
        ('Задача A выполняется', 'На одном CPU сейчас исполняются инструкции только A'),
        ('Сохранить состояние A', 'Положение в программе и регистры A сохраняются'),
        ('Восстановить состояние B', 'CPU получает сохранённое состояние B'),
        ('Задача B выполняется', 'B продолжает с собственного места в программе'),
        ('Вернуться к задаче A', 'Состояние A восстановлено; выполнение продолжается'),
    ]
    def paint(s, p):
        b = s in (2, 3)
        c = Canvas('Переключение задач на одном CPU', 'Конкурентное продвижение без одновременного исполнения на этом CPU')
        c.card(40, 165, 300, 250, 'СОСТОЯНИЕ A', 'Позиция: шаг 12\nРегистр: 42\nСобственный стек', PRIMARY, not b)
        c.card(410, 165, 300, 250, 'CPU', f'Исполняет: {"B" if b else "A"}\nПозиция: {80 if b else 12}\nРегистр: {7 if b else 42}', SECONDARY, True)
        c.card(780, 165, 300, 250, 'СОСТОЯНИЕ B', 'Позиция: шаг 80\nРегистр: 7\nСобственный стек', SUCCESS, b)
        if s == 1:
            c.arrow((398, 285), (350, 285), PRIMARY, progress=p)
        elif s == 2:
            c.arrow((768, 285), (720, 285), SUCCESS, progress=p)
        elif s == 4:
            c.arrow((350, 285), (398, 285), PRIMARY, progress=p)
        c.banner(s, len(states), *states[s])
        c.footer('Переключение контекста не требует копирования всей памяти задачи.')
        return c
    make_gif('context-switch', states, paint)


def virtual_memory():
    states = [
        ('Обращение к виртуальному адресу', 'Процессу нужны данные: страница 2, смещение 16'),
        ('Страница пока не подготовлена', 'Возникает page fault; управление получает ОС'),
        ('ОС подготавливает данные', 'Для страницы выделяется физический кадр 7'),
        ('Обновление таблицы страниц', 'Виртуальная страница 2 теперь связана с кадром 7'),
        ('Обращение продолжается', 'Кадр 7, смещение 16: прочитано значение 42'),
    ]
    def paint(s, p):
        c = Canvas('Виртуальная память: первый доступ к странице', 'Page fault может быть обычным этапом подготовки памяти')
        c.card(40, 170, 300, 245, 'АДРЕС ПРОЦЕССА', 'Страница: 2\nСмещение: 16', PRIMARY, True)
        mapping = '2 → кадр 7' if s >= 3 else '2 → нет готовой страницы'
        c.card(410, 170, 300, 245, 'ТАБЛИЦА СТРАНИЦ', mapping, SUBDUED if s == 1 else SECONDARY, True)
        body = 'Кадр 7\nСмещение 16: 42' if s >= 2 else 'Свободный кадр'
        c.card(780, 170, 300, 245, 'ФИЗИЧЕСКАЯ RAM', body, SUCCESS, s >= 2)
        c.arrow((350, 275), (398, 275), PRIMARY, progress=p if s in (0, 4) else None)
        if s >= 2:
            c.arrow((720, 310), (768, 310), SUCCESS, progress=p)
        c.banner(s, len(states), *states[s])
        c.footer('Смещение внутри страницы сохраняется; номер виртуальной страницы и кадра может различаться.')
        return c
    make_gif('virtual-memory', states, paint)


def race():
    left = [(10, 'Начальное значение'), (10, 'A читает 10'), (10, 'B читает 10'), (10, 'A вычисляет 11'), (10, 'B вычисляет 11'), (11, 'A записывает 11'), (11, 'B записывает 11'), (11, 'Одно обновление потеряно')]
    right = [(10, 'Начальное значение'), (10, 'A захватывает mutex'), (10, 'A читает 10, вычисляет 11'), (11, 'A записывает 11'), (11, 'A освобождает mutex'), (11, 'B читает 11, вычисляет 12'), (12, 'B записывает 12'), (12, 'Оба обновления сохранены')]
    def paint(s, p):
        c = Canvas('Два увеличения счётчика: 10 → 12', 'Взаимное исключение защищает всю последовательность «прочитать — изменить — записать»')
        for x, records, title, color in [(40, left, 'БЕЗ СОГЛАСОВАНИЯ', SUBDUED), (590, right, 'ПОД ОДНИМ MUTEX', SUCCESS)]:
            value, message = records[s]
            c.card(x, 165, 490, 285, title, '', color, True)
            c.text(x+245, 235, str(value), 78, color, True, center=True)
            c.text(x+245, 355, message, 22, INK, width=440, center=True)
        c.banner(s, len(left), 'Наблюдаем порядок действий', 'Общий ресурс должен изменяться по одному согласованному протоколу')
        c.footer('Потеря обновления возможна и на одном CPU: достаточно такого чередования шагов.')
        return c
    make_gif('lost-update', left, paint)


def file_buffers():
    states = [
        ('Данные в буфере приложения', 'Файл ещё не получил эти байты'),
        ('Буфер передан операционной системе', 'Данные попали в файловый кэш RAM'),
        ('Обычная запись вернула результат', 'Возврат write ещё не гарантирует устойчивое сохранение'),
        ('Синхронизация файла', 'fsync дожидается записи данных и необходимой информации файла'),
        ('Синхронизация успешно завершена', 'Подтверждено сохранение в рамках контракта ОС и устройства'),
    ]
    def paint(s, p):
        c = Canvas('Когда данные становятся сохранёнными', 'Путь обычной буферизованной записи файла')
        c.card(40, 180, 300, 235, 'БУФЕР ПРИЛОЖЕНИЯ', 'Данные: ABC' if s == 0 else 'Нет ожидающих байтов', PRIMARY, s == 0)
        cache_body = '—' if s == 0 else ('Данные: ABC\nСтраница чистая' if s == 4 else 'Данные: ABC\nСтраница изменена')
        c.card(410, 180, 300, 235, 'ФАЙЛОВЫЙ КЭШ ОС', cache_body, SUCCESS if s == 4 else EMPHASIS, s >= 1)
        disk_body = 'Данные: ABC' if s == 4 else ('Идёт запись...' if s == 3 else '—')
        c.card(780, 180, 300, 235, 'НАКОПИТЕЛЬ', disk_body, SUCCESS, s >= 3)
        c.arrow((350, 300), (398, 300), PRIMARY, progress=p if s == 1 else None)
        c.arrow((720, 300), (768, 300), SUCCESS if s >= 3 else MUTED, progress=p if s == 3 else None)
        c.banner(s, len(states), *states[s])
        c.footer('Синхронизация записи имени файла в каталоге — отдельный вопрос.')
        return c
    make_gif('file-buffers', states, paint)


def queue_growth():
    states = list(range(7))
    def paint(s, p):
        c = Canvas('Когда входящий поток быстрее обработки', 'Приходит 3 задачи за шаг · завершается 2 · очередь растёт на 1')
        c.card(40, 155, 250, 270, 'ПОСТУПЛЕНИЕ', f'Всего: {3*s}\n3 задачи / шаг', PRIMARY, True)
        c.card(360, 155, 390, 270, 'ОЧЕРЕДЬ', f'Ожидают: {s}', EMPHASIS, s > 0)
        c.card(820, 155, 260, 270, 'ЗАВЕРШЕНО', f'Всего: {2*s}\n2 задачи / шаг', SUCCESS, True)
        for i in range(s):
            x, y = 395+(i % 4)*76, 280+(i // 4)*65
            c.rect((x, y, x+55, y+45), FILLS[EMPHASIS], EMPHASIS, radius=8)
            c.text(x+27, y+10, str(i+1), 20, EMPHASIS, True, center=True)
        c.arrow((300, 285), (348, 285), PRIMARY, progress=p)
        c.arrow((760, 285), (808, 285), SUCCESS, progress=p)
        c.banner(s, len(states), f'После {s} шагов: {3*s} поступило − {2*s} завершено = {s} ожидают', 'Без ограничения приёма растут задержка и память очереди')
        c.footer('Числа задают простую модель с постоянной скоростью поступления и обработки.')
        return c
    make_gif('queue-growth', states, paint)


if __name__ == '__main__':
    sync_mermaid_style()
    static_diagrams()
    for build in [processor, cache, context_switch, virtual_memory, race, file_buffers, queue_growth]:
        build()
        print('Built', build.__name__, flush=True)
    print('Assets:', OUT)
    print('QA previews:', QA)
