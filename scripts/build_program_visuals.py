"""Original program-build diagram using the repository's existing visual system."""
from pathlib import Path
import build_learning_visuals as visuals


def build():
    visuals.OUT = Path(__file__).resolve().parents[1] / 'notes' / 'Вложения' / 'Программы'
    visuals.OUT.mkdir(parents=True, exist_ok=True)
    c = visuals.Canvas('От текста к работающей программе', 'Сборка подготавливает файл; запуск подготавливает его исполнение')
    c.card(40, 145, 310, 170, 'Исходники', 'Функции и данные\nВ нескольких файлах', active=True)
    c.card(405, 145, 310, 170, 'Компиляция', 'Проверка и перевод\nОбъектные файлы')
    c.card(770, 145, 310, 170, 'Компоновка', 'Объектные файлы\nи библиотеки')
    c.arrow((360, 230), (393, 230))
    c.arrow((725, 230), (758, 230))
    c.arrow((925, 325), (925, 380))
    c.card(670, 395, 410, 180, 'Исполняемый файл', 'Код + данные + метаданные\nНа накопителе')
    c.card(40, 395, 410, 180, 'Исполнение в процессе', 'Стартовый код\nПрикладная логика')
    c.arrow((655, 485), (465, 485))
    c.text(550, 415, 'Загрузка\nОС', 20, visuals.PRIMARY, center=True)
    c.footer('Типичный путь сборки в машинный код. Файл и процесс — разные объекты.')
    c.save_static('build-and-launch')
    print(visuals.OUT / 'build-and-launch.png')


def values():
    c = visuals.Canvas('Копия указателя сохраняет общий объект', 'Одинаковая цель доступа и независимая копия значения — разные отношения')
    c.card(40, 165, 230, 110, 'p', 'Адрес записи')
    c.card(40, 350, 230, 110, 'q = копия p', 'Тот же адрес')
    c.card(415, 250, 280, 170, 'Общая запись', 'count = 11', active=True)
    c.arrow((280, 220), (402, 295))
    c.arrow((280, 405), (402, 365))
    c.card(810, 250, 270, 170, 'Копия записи', 'count = 10')
    c.text(40, 520, 'Запись через q меняет то, что читается через p.', 23)
    c.text(40, 560, 'Независимая копия числового поля сохраняет прежнее значение.', 21, visuals.MUTED)
    c.footer('Пример с одним числовым полем. Копирование вложенных ссылок не копирует их цели.')
    c.save_static('values-and-aliases')


def frames():
    c = visuals.Canvas('Вложенный вызов сохраняет незавершённое', 'Три снимка стека; верхний активный кадр выделен зелёным')
    for x, names in [(40, ['A']), (405, ['A', 'B']), (770, ['A', 'B', 'C'])]:
        for i, name in enumerate(names):
            y = 460-i*110
            c.card(x, y, 310, 90, f'Кадр {name}', active=i == len(names)-1)
    c.text(195, 155, 'Выполняется A', 23, center=True)
    c.text(560, 155, 'A вызвала B', 23, center=True)
    c.text(925, 155, 'B вызвала C', 23, center=True)
    c.arrow((360, 345), (390, 345))
    c.arrow((725, 345), (755, 345))
    c.footer('После возврата C продолжится B, затем A. Размещение кадров здесь условное.')
    c.save_static('call-frames')


def array_list():
    c = visuals.Canvas('Индекс массива и переходы по списку', 'Три значения: 7, 4, 9. Адреса условные, размер элемента массива — 4 байта')
    c.text(40, 150, 'Массив', 26, bold=True)
    for i, value in enumerate([7, 4, 9]):
        x = 370+i*140
        c.rect((x, 150, x+140, 230), visuals.PRIMARY, visuals.BG)
        c.text(x+70, 175, str(value), 30, visuals.ACTIVE_TEXT, center=True)
        c.text(x+70, 250, str(1000+i*4), 20, center=True)
    c.text(40, 300, 'Адрес элемента i = 1000 + i × 4', 22, visuals.MUTED)
    c.text(40, 365, 'Список', 26, bold=True)
    coords = [(290, 385, 7, 1000), (615, 460, 4, 8100), (880, 360, 9, 4600)]
    for x, y, value, addr in coords:
        c.card(x, y, 180, 110, str(value), f'Адрес {addr}')
    c.arrow((480, 440), (603, 505))
    c.arrow((805, 505), (868, 415))
    c.footer('Последовательность значений не требует соседства узлов списка в памяти.')
    c.save_static('array-and-list')


def hashing():
    c = visuals.Canvas('Коллизия не означает равенство ключей', 'Учебное распределение: индекс корзины = ключ mod 4')
    for i in range(4):
        y = 155+i*100
        c.card(40, y, 160, 75, f'Корзина {i}', active=i == 2)
    c.card(360, 255, 240, 75, 'Ключ 13')
    c.arrow((210, 292), (345, 292))
    c.card(360, 355, 240, 75, 'Ключ 2', active=True)
    c.card(755, 355, 240, 75, 'Ключ 6', active=True)
    c.arrow((210, 392), (345, 392))
    c.arrow((610, 392), (740, 392))
    c.card(360, 455, 240, 75, 'Ключ 3')
    c.arrow((210, 492), (345, 492))
    c.footer('Показан вариант с цепочками. Учебная функция не предназначена для реальных ключей.')
    c.save_static('hash-collisions')


def tree_height():
    c = visuals.Canvas('Одинаковые ключи, разная высота', 'Высота h здесь считается в узлах: у единственного узла h = 1')
    c.text(280, 130, 'h = 3', 25, center=True)
    c.text(870, 130, 'h = 7', 25, center=True)
    nodes = {8: (280, 215), 4: (150, 340), 12: (410, 340), 2: (80, 465), 6: (220, 465), 10: (350, 465), 14: (480, 465)}
    for a, b in [(8,4),(8,12),(4,2),(4,6),(12,10),(12,14)]:
        c.line([nodes[a], nodes[b]], visuals.PRIMARY)
    for value, (x, y) in nodes.items():
        c.circle(x, y, 28, visuals.SURFACE, visuals.PRIMARY)
        c.text(x, y-11, str(value), 23, center=True)
    chain = [(755+i*38, 190+i*62) for i in range(7)]
    for a, b in zip(chain, chain[1:]): c.line([a,b], visuals.PRIMARY)
    for value, (x,y) in zip([2,4,6,8,10,12,14],chain):
        c.circle(x, y, 24, visuals.SURFACE, visuals.PRIMARY)
        c.text(x, y-10, str(value), 22, center=True)
    c.footer('Оба примера — двоичные деревья поиска. Порядок ключей не гарантирует балансировку.')
    c.save_static('tree-height')


def ring():
    c = visuals.Canvas('Логический порядок и позиции массива', 'Кольцевая очередь: ёмкость 4, голова 3, длина 3')
    for i, value in enumerate(['B','C','свободно','A']):
        x = 80+i*250
        c.text(x+110, 165, f'Индекс {i}', 22, center=True)
        c.card(x, 225, 220, 120, value, active=value == 'A')
    c.line([(940,365),(940,405),(190,405)],visuals.PRIMARY)
    c.arrow((190,405),(190,360))
    c.text(40, 460, 'Извлечение: A, затем B, затем C', 25)
    c.text(40, 515, 'Следующая вставка: ячейка 2', 24, visuals.MUTED)
    c.footer('Переход от последней физической ячейки к первой сохраняет порядок очереди.')
    c.save_static('ring-queue')


if __name__ == '__main__':
    visuals.OUT = Path(__file__).resolve().parents[1] / 'notes' / 'Вложения' / 'Программы'
    visuals.OUT.mkdir(parents=True, exist_ok=True)
    for make in [build, values, frames, array_list, hashing, tree_height, ring]:
        make()
        print('Built', make.__name__)
