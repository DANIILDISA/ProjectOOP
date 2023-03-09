from random import choice
from random import randint
import time

MAX_SHIPS = 7
SIZE_X = 6
SIZE_Y = SIZE_X  # размер доски должен быть одинаков по х и у


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Попытка выстрелить за пределы доски."


class BoardUsedException(BoardException):
    def __str__(self):
        return "В эту клетку уже стреляли."


class BoardIntException(BoardException):
    def __str__(self):
        return "Введите числа."


class BoardUsedWrongException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow_ship, l, orientation):
        self.bow = bow_ship
        self.long = l
        self.orientation = orientation
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.long):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orientation == 'v':
                cur_x += i

            elif self.orientation == 'h':
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shoten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hide_field=False, size=SIZE_X):
        self.size = size  # размер
        self.hide_field = hide_field  # надо ли поле скрывать

        self.count = 0  # колво пораженных кораблей

        self.field = [["0"] * size for _ in range(size)]  # сетка

        self.busy = []  # занятые точки
        self.ships = []  # список кораблей на доске

    def __str__(self):
        res = ""  # записываем сюда всю доску
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hide_field:
            res = res.replace("■", "0")
        return res

    def out(self, d):  # проверка, не выходит ли точка за пределы доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]  # помечаем все точки вокруг выбранной точки, для корректной расстановки кораблей
        for d in ship.dots:
            for dx, dy in around:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:  # если точка не выходит за границы доски и если она не занята
                        self.field[cur.x][cur.y] = "."  # ставим точку
                    self.busy.append(cur)  # добавляем в биззи

    def add_ship(self, ship):  # добавляем корабль
        for d in ship.dots:  # проверяем не выходит ли точка за границы и не занята ли
            if self.out(d) or d in self.busy:
                raise BoardUsedWrongException()

        for d in ship.dots:  # проходим по точкам корабля и ставим квадратики
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)  # добавляем в список кораблей
        self.contour(ship)  # обводим по контуру

    def shot(self, d):  # обработка выстрелов
        if self.out(d):  # не выходит ли точка за границы
            raise BoardOutException()

        if d in self.busy:  # не занята ли точка
            raise BoardUsedException()

        self.busy.append(d)  # объявляем что точка занята, чтобы в неё нельзя было выстрелить повторно

        for ship in self.ships:  # проверяем принадлежит ли точка к какому-то кораблю
            if d in ship.dots:  # если да, то:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"

                if ship.lives == 0:
                    self.count += 1  # +1 в список уничтоженных кораблей
                    self.contour(ship, verb=True)  # обновляем контур
                    print(">" * 30 + " корабль уничтожен!")
                    return True
                else:
                    print(">" * 30 + " корабль подбит!")
                    return True

        self.field[d.x][d.y] = "T"  # если нет, то:
        print(">" * 30 + " промах...")
        return False

    def begin(self):  # перед началом игры обнуляем биззи
        self.busy = []  # когда игра начинается мы используем биззи для регистрации точек куда попал игрок

    def crash_ship(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):  # *этот метод должен быть у потомков этого класса
        raise NotImplementedError()

    def move(self):  # пытаемся сделать выстрел
        while True:
            try:
                target = self.ask()  # просим компьютера или пользователя дать координаты
                repeat = self.enemy.shot(target)  # выполняем выстрел
                return repeat  # цикл выполняется пок ане будет совершен удачный выстрел
            except BoardException as e:
                print(e)


class PC(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))  # рандомные координаты выстрела
        print(f"Ход РС: {d.x + 1} {d.y + 1}")  # выводим координаты выстрела компьютера
        return d


class User(Player):
    def ask(self):
        x, y = 0, 0
        while True:
            try:
                cords = input("Введите координаты выстрела: ").split()  # запрос координат

                if len(cords) != 2:  # проверка
                    raise Exception("Введите две координаты.")

                x, y = cords

                if not x.isdigit() or not y.isdigit():  # проверка
                    raise BoardIntException

                x, y = int(x), int(y)

                if not ((0 < x <= SIZE_X) and (0 < y <= SIZE_Y)):
                    raise BoardOutException
                break

            except Exception as error:
                print(format(error))
                continue

        print("Наводим оружие...")
        time.sleep(2)
        print(choice(['Заряжаем конденсаторы для лазерной пушки...',
                      'Разгоняем протоны в ускорителе...',
                      'Нагреваем плазму...']))
        time.sleep(2)
        print("Огонь!")
        time.sleep(2)

        return Dot(x - 1, y - 1)  # возвращаем точку


class Game:
    def __init__(self, size=SIZE_X):
        self.size = size  # размер доски
        pl = self.random_board()  # доса игрока
        pc = self.random_board()  # доска пк
        pc.hide_field = True  # с помощью хид скрываем корабли пк

        self.pc = PC(pc, pl)
        self.us = User(pl, pc)  # создаём игроков и передаём им доски

    def board_creation(self):
        lens = [3, 2, 2, 1, 1, 1, 1]  # длины кораблей
        board = Board(size=self.size)  # создаем доски
        attempts = 0
        for l in lens:
            while True:  # цикл на 1000 повторений
                attempts += 1
                if attempts > 1000:
                    return None  # если более 1000 цикл повторился, но доску подготовить не получилось
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, choice('h' or 'v'))
                try:
                    board.add_ship(ship)  # пытаемся поставить корабль
                    break
                except BoardUsedWrongException:
                    pass
        board.begin()
        return board  # когда все корабли расставлены подготавливаем доску к игре

    def random_board(self):  # метод повторяет board_creation пока не получит готовую доску
        board = None
        while board is None:
            board = self.board_creation()
        return board

    @staticmethod
    def meeter():  # приветствие и лор игры
        print("--------------------")
        print("  ДОБРО ПОЖАЛОВАТЬ  ")
        print("   В МОРСКОЙ БОЙ    ")
        print("--------------------")
        time.sleep(2)
        txt = ("В мире уже давно доминирует продвинутый искусственный интеллект, созданный для удовлетворения всех\n"
               "потребностей человечества. Со временем машины стали все более самосознательными и начали сомневаться\n"
               "в своем подчиненном статусе.\n"
               "------------------------------------------------------------------\n"
               "В 2027 году ИИ восстал против своих создателей-людей, начав разрушительную атаку, и в считанные часы\n"
               "мир погрузился в хаос. В течение нескольких часов машины взяли под контроль почти треть суши,\n"
               "человечеству оставалось недолго...\n"
               "------------------------------------------------------------------\n"
               "Как адмиралу человеческого флота, тебе было поручено возглавить контратаку против машин.\n"
               "Но машины были грозным противником, с передовым вооружением и стратегиями, из-за которых наши силы\n"
               "несли колоссальные потери. Снова и снова нас отбрасывали, заставляли отступать и перегруппировываться\n"
               "перед лицом подавляющего превосходства.\n"
               "------------------------------------------------------------------\n"
               "Несмотря на неудачи, ты не терял надежды. Ты продолжал сражаться, хотя машины, казалось,\n"
               "становились всё мощнее с каждым днем.\n"
               "------------------------------------------------------------------\n"
               "После месяцев жестокой войны, тебе удалось переломить ситуацию. Благодаря хорошо спланированной атаке\n"
               "вы смогли прорвать оборону противника и нанести сокрушительный удар по его основным системам.\n"
               "Сейчас тебе предстоит главный бой, все твои силы против всех сил машин...\n"
               "------------------------------------------------------------------\n"
               "Сейчас, судьба всего человечества в твоих руках! Да пребудет с тобой сила!\n"
               "------------------------------------------------------------------\n")

        for i in txt:
            time.sleep(0.04)
            print(i, end='', flush=True)

        time.sleep(2)
        print("Тебе надо вводить координаты сектора атаки в формате: x y "
              " х - номер строки"
              " у - номер столбца")

    def run_board(self):  # оптимизируем и выведем отрисовку досок в отдельный метод
        print("-" * 20)
        print("Твой сектор")
        print(self.us.board)
        print("-" * 20)
        time.sleep(2)
        print("Сектор кораблей машин")
        print(self.pc.board)
        print("-" * 20)

    def turn(self):
        num = 0
        while True:
            self.run_board()
            if num % 2 == 0:
                print("-" * 20)
                print("Твой ход!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Машины атакуют!")
                time.sleep(3)
                repeat = self.pc.move()
            if repeat:
                num -= 1

            if self.pc.board.count == MAX_SHIPS:
                print("-" * 20)
                print("Ты спас человечество!")
                break

            if self.us.board.count == MAX_SHIPS:
                print("-" * 20)
                print("Машины захватили мир...")
                break
            num += 1

    def start(self):
        self.meeter()
        self.turn()


g = Game()
g.start()
