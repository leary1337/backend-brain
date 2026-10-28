"""Reproducible original diagrams and animated learning examples."""
from pathlib import Path
from functools import lru_cache
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
ACTIVE_TEXT = STYLE['active_text']
PRIMARY, SUCCESS, EMPHASIS, SUBDUED, SECONDARY = (STYLE[key] for key in ('primary', 'success', 'emphasis', 'subdued', 'secondary'))
FILLS = {STYLE[key]: value for key, value in STYLE['fills'].items()}
BODY_FONT = Path(__file__).parent / STYLE['font_file']
HEADING_FONT = Path(STYLE['heading_font_file'])


@lru_cache(maxsize=64)
def font(size=22, bold=False, heading=False):
    result = ImageFont.truetype(str(HEADING_FONT if heading else BODY_FONT), size)
    if not heading:
        axes = result.get_variation_axes()
        result.set_variation_by_axes([700 if bold else 400 for _ in axes])
    return result


class Canvas:
    def __init__(self, title, subtitle=''):
        self.title = title
        self.im = Image.new('RGB', (W, H), BG)
        self.d = ImageDraw.Draw(self.im)
        self.text(40, 27, title.upper(), 36, bold=True, heading=True, width=1040)
        self.text(40, 82, subtitle, 18, MUTED, width=1040)

    def rect(self, box, fill=SURFACE, outline=BORDER, radius=0, stroke=1):
        self.d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=stroke)

    def line(self, points, color=MUTED, stroke=2):
        self.d.line(points, fill=color, width=stroke)

    def circle(self, x, y, r, fill, outline=None, stroke=2):
        self.d.ellipse((x-r, y-r, x+r, y+r), fill=fill, outline=outline, width=stroke)

    def text(self, x, y, value, size=22, color=INK, bold=False, width=None, center=False, heading=False):
        f = font(size, bold, heading)
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
            y += size+8
        return y

    def arrow(self, start, end, color=PRIMARY, stroke=2, progress=None):
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
        fill = FILLS[color] if active else SURFACE
        text_color = ACTIVE_TEXT if active and fill == PRIMARY else INK
        self.rect((x, y, x+w, y+h), fill, fill)
        bottom = self.text(x+20, y+18, title, 23, text_color, False, w-40)
        if body:
            self.text(x+20, bottom+12, body, 21, text_color, width=w-40)

    def banner(self, step, total, title, detail):
        self.line([(40, 493), (40, 598)], PRIMARY, 3)
        self.text(60, 506, f'{step+1} / {total}   {title}', 24, INK, True, 1000)
        self.text(60, 547, detail, 20, MUTED, width=1000)

    def footer(self, text):
        self.text(40, 625, text, 15, MUTED, width=1040)

    def save_static(self, name):
        self.im.save(OUT / f'{name}.png', optimize=True)
        self.im.save(QA / f'{name}.png')


def static_diagrams():
    c = Canvas('Компьютер: четыре роли', 'Кто выполняет работу, где находятся данные и как они попадают в систему')
    c.card(40, 175, 280, 220, 'ПРОЦЕССОР', 'Инструкции\nВычисления\nРегистры и кэши', PRIMARY, True)
    c.card(405, 175, 310, 220, 'ОПЕРАТИВНАЯ ПАМЯТЬ', 'Рабочие данные\nИнструкции программы\nБуферы обмена', SUCCESS)
    c.card(800, 145, 280, 120, 'НАКОПИТЕЛЬ', 'Файлы между запусками', EMPHASIS)
    c.card(800, 285, 280, 160, 'СЕТЕВОЙ ИНТЕРФЕЙС', 'Обмен с другими узлами', SECONDARY)
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
    c.save_static('computer-overview')

    c = Canvas('Байты одинаковые — смысл задаёт формат', 'Биты, числовая интерпретация и кодировка текста')
    c.text(40, 135, 'Биты одного байта', 25, bold=True)
    for i in range(8):
        x = 40+i*65
        c.rect((x, 185, x+54, 243), FILLS[PRIMARY], PRIMARY, radius=8)
        c.text(x+27, 197, '1', 28, ACTIVE_TEXT, False, center=True)
    c.card(650, 130, 430, 145, '11111111', 'Без знака: 255\nДополнительный код: −1', SECONDARY, True)
    c.text(40, 300, 'Текст в UTF-8', 25, bold=True)
    columns = [(40, 'A', 'U+0041', '41', '1 байт'), (405, 'Я', 'U+042F', 'D0 AF', '2 байта'), (770, 'Кодовая позиция', 'U+1F600', 'F0 9F 98 80', '4 байта')]
    for x, title, code, data, size in columns:
        c.card(x, 350, 310, 195, title, f'{code}\nБайты: {data}\n{size}', SUCCESS, True)
    c.footer('Число байт, число кодовых позиций и число видимых символов — разные величины.')
    c.save_static('data-representation')

    c = Canvas('HDD и SSD: разные способы хранения', 'Характер доступа влияет на задержку и скорость устройства')
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
    c.save_static('storage-devices')

    c = Canvas('Граница между приложением и ядром', 'Обычные вычисления выполняет CPU; привилегированные операции проходят через ядро')
    c.card(40, 145, 470, 110, 'ПРИЛОЖЕНИЕ A', 'Пользовательское пространство', PRIMARY)
    c.card(610, 145, 470, 110, 'ПРИЛОЖЕНИЕ B', 'Пользовательское пространство', SECONDARY)
    c.arrow((275, 270), (275, 345), PRIMARY)
    c.arrow((845, 270), (845, 345), SECONDARY)
    c.text(340, 292, 'Системные вызовы', 23, MUTED, True, width=440)
    c.card(40, 360, 1040, 125, 'ЯДРО ОПЕРАЦИОННОЙ СИСТЕМЫ', 'Проверка прав · планирование · память · файлы · драйверы', SUCCESS, True)
    c.arrow((560, 495), (560, 535), SUCCESS)
    c.rect((40, 550, 1080, 602), PANEL, PANEL)
    c.text(560, 562, 'ОБОРУДОВАНИЕ: CPU · RAM · накопители · сеть', 22, center=True)
    c.footer('Переход в ядро не обязательно означает переключение на другую задачу.')
    c.save_static('kernel-boundary')


def replacement_diagrams():
    c = Canvas('Иерархия памяти', 'Регистры, кэши и RAM решают разные задачи')
    c.card(40, 190, 300, 215, 'РЕГИСТРЫ', 'Текущие значения\nвнутри CPU', PRIMARY, True)
    c.card(410, 190, 300, 215, 'КЭШИ CPU', 'Копии рабочих\nданных', PRIMARY)
    c.card(780, 190, 300, 215, 'RAM', 'Основная\nрабочая память', PRIMARY)
    for a, b in [(350, 398), (720, 768)]:
        c.arrow((a, 270), (b, 270), INK)
        c.arrow((b, 325), (a, 325), INK)
    c.text(40, 485, 'От быстрых малых хранилищ — к большему рабочему объёму', 24, width=1030)
    c.footer('Реальные размеры, задержки и разделение кэшей зависят от процессора.')
    c.save_static('memory-hierarchy')

    c = Canvas('Системный вызов', 'Запрос к ядру проходит через проверку аргументов и прав')
    c.card(100, 150, 300, 95, 'ПРИЛОЖЕНИЕ', '', PRIMARY)
    c.card(720, 150, 300, 95, 'ЯДРО', '', PRIMARY, True)
    c.line([(250, 250), (250, 515)], MUTED, 1)
    c.line([(870, 250), (870, 515)], MUTED, 1)
    c.arrow((250, 295), (870, 295), INK)
    c.text(560, 258, 'Запрос операции', 21, center=True)
    c.rect((620, 330, 1070, 412), SURFACE, BORDER)
    c.text(845, 346, 'Проверка аргументов,\nправ и состояния ресурса', 20, width=420, center=True)
    c.arrow((870, 475), (250, 475), PRIMARY)
    c.text(560, 437, 'Результат или ошибка', 21, center=True)
    c.footer('Переход в ядро не обязательно приводит к переключению на другую задачу.')
    c.save_static('system-call')

    c = Canvas('Состояния задачи', 'Готовность к работе и ожидание события — разные состояния')
    def node(x, y, label, active=False):
        fill = PRIMARY if active else SURFACE
        c.rect((x, y, x+330, y+125), fill, fill)
        c.text(x+165, y+30, label, 22, ACTIVE_TEXT if active else INK, width=300, center=True)
    node(40, 170, 'Готова выполнять\nработу')
    node(750, 170, 'Выполняется\nна CPU', True)
    node(395, 405, 'Ожидает событие')
    c.arrow((385, 203), (735, 203), INK)
    c.text(560, 163, 'получила CPU', 19, center=True)
    c.arrow((735, 261), (385, 261), INK)
    c.text(560, 279, 'вытеснена', 19, center=True)
    c.arrow((865, 311), (740, 435), INK)
    c.text(915, 349, 'требуется\nожидание', 19, center=True)
    c.arrow((380, 435), (205, 311), PRIMARY)
    c.text(170, 351, 'событие\nпроизошло', 19, center=True)
    c.footer('Готовая задача ждёт CPU; ожидающая задача ещё не может продолжить выполнение.')
    c.save_static('task-states')

    c = Canvas('Виртуальные и физические страницы', 'Разные процессы могут управляемо разделять одну физическую страницу')
    c.card(40, 150, 420, 110, 'ПРОЦЕСС A', 'Виртуальная страница 2')
    c.card(40, 290, 420, 110, 'ПРОЦЕСС B', 'Виртуальная страница 8')
    c.card(40, 430, 420, 110, 'ПРОЦЕСС A', 'Виртуальная страница 4')
    c.card(720, 205, 360, 145, 'RAM · КАДР 7', 'Общие физические данные', PRIMARY, True)
    c.card(720, 430, 360, 110, 'RAM · КАДР 9', 'Другие данные')
    c.arrow((475, 205), (705, 250), INK)
    c.arrow((475, 345), (705, 300), INK)
    c.arrow((475, 485), (705, 485), INK)
    c.footer('Номер виртуальной страницы не задаёт её физическое расположение.')
    c.save_static('shared-pages')


def update_article_images():
    replacements = {
        '04 Оперативная память и кэши.md': ('memory-hierarchy', 'Регистры, кэши CPU и оперативная память'),
        '01 Операционная система.md': ('system-call', 'Запрос приложения к ядру и возврат результата'),
        '02 Процессы и потоки.md': ('task-states', 'Переходы задачи между готовностью, выполнением и ожиданием'),
        '03 Виртуальная память.md': ('shared-pages', 'Две виртуальные страницы разделяют один физический кадр'),
    }
    fence = chr(96)*3
    static_names = ['computer-overview', 'data-representation', 'storage-devices', 'kernel-boundary']
    for path in (ROOT / 'notes').rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        updated = text
        for name in static_names:
            updated = updated.replace(f'/{name}.svg)', f'/{name}.png)')
        if path.name in replacements:
            name, alt = replacements[path.name]
            image = f'![{alt}](../Вложения/Основы/{name}.png)'
            updated = re.sub('^'+fence+'mermaid.*?^'+fence, image, updated, flags=re.M | re.S)
        if updated != text:
            path.write_text(updated, encoding='utf-8', newline='\n')


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
        ('ОС подготавливает данные', 'Кадр 7 заполняется данными страницы файла'),
        ('Обновление таблицы страниц', 'Виртуальная страница 2 теперь связана с кадром 7'),
        ('Обращение продолжается', 'Кадр 7, смещение 16: прочитано значение 42'),
    ]
    def paint(s, p):
        c = Canvas('Виртуальная память: первый доступ к странице', 'Пример: отображённая страница файла содержит значение 42')
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
    right = [(10, 'Начальное значение'), (10, 'A захватывает mutex'), (10, 'A читает 10, вычисляет 11'), (11, 'A записывает 11'), (11, 'A освобождает mutex'), (11, 'B захватывает mutex\nи читает 11'), (12, 'B вычисляет и записывает 12'), (12, 'B освобождает mutex')]
    def paint(s, p):
        c = Canvas('Два увеличения счётчика: 10 → 12', 'Взаимное исключение защищает всю последовательность «прочитать — изменить — записать»')
        for x, records, title, color in [(40, left, 'БЕЗ СОГЛАСОВАНИЯ', SUBDUED), (590, right, 'ПОД ОДНИМ MUTEX', SUCCESS)]:
            value, message = records[s]
            c.card(x, 165, 490, 285, title, '', color, True)
            ink = ACTIVE_TEXT if color == PRIMARY else INK
            c.text(x+245, 235, str(value), 78, ink, False, center=True)
            c.text(x+245, 355, message, 22, ink, width=440, center=True)
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
        c.footer('ОС может начать фоновую запись данных ещё до вызова fsync.')
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
            c.text(x+27, y+10, str(i+1), 20, ACTIVE_TEXT, False, center=True)
        c.arrow((300, 285), (348, 285), PRIMARY, progress=p)
        c.arrow((760, 285), (808, 285), SUCCESS, progress=p)
        c.banner(s, len(states), f'После {s} шагов: {3*s} поступило − {2*s} завершено = {s} ожидают', 'Без ограничения приёма растут задержка и память очереди')
        c.footer('Числа задают простую модель с постоянной скоростью поступления и обработки.')
        return c
    make_gif('queue-growth', states, paint)


if __name__ == '__main__':
    static_diagrams()
    replacement_diagrams()
    update_article_images()
    for build in [processor, cache, context_switch, virtual_memory, race, file_buffers, queue_growth]:
        build()
        print('Built', build.__name__, flush=True)
    print('Assets:', OUT)
    print('QA previews:', QA)
