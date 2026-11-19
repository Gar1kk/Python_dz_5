from tkinter import *
from datetime import datetime, date
import sqlite3

# Подключаем базу данных и создаём таблицу событий, если её ещё нет.
db = sqlite3.connect("events.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_date TEXT, name TEXT)")
db.commit()

# Названия дней и месяцев для отображения дат на русском языке.
days = ["понедельник", "вторник", "среда", "четверг",
        "пятница", "суббота", "воскресенье"]

months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

# Главное окно с кнопками добавления и просмотра событий.
root = Tk()
root.title("Календарь событий")
root.geometry("400x300")


# Открывает форму ввода названия и даты по кнопке «Добавить событие».
def add_event():
    win = Toplevel(root)
    win.title("Добавить событие")
    win.geometry("350x300")

    Label(win, text="Название события:").pack(pady=5)
    name_entry = Entry(win, width=35)
    name_entry.pack()

    Label(win, text="Дата события (дд.мм.гггг):").pack(pady=5)
    date_entry = Entry(win, width=35)
    date_entry.pack()

    # Здесь будут появляться ошибки ввода и сообщение об успешном сохранении.
    info = Label(win, text="")
    info.pack(pady=10)

    # Обработчик кнопки «Сохранить»: проверяет введённые данные,
    # записывает событие в базу и очищает поля после сохранения.
    def save():
        name = name_entry.get()
        text_date = date_entry.get()

        if name == "":
            info["text"] = "Введите название события"
            return

        # Проверяем формат даты и существование такого дня в календаре.
        try:
            event_date = datetime.strptime(text_date, "%d.%m.%Y").date()
        except ValueError:
            info["text"] = "Неверная дата"
            return

        # Формат YYYY-MM-DD позволяет сортировать даты в SQLite как текст.
        cursor.execute(
            "INSERT INTO events (event_date, name) VALUES (?, ?)",
            (event_date.isoformat(), name)
        )
        db.commit()

        info["text"] = "Событие добавлено!"
        name_entry.delete(0, END)
        date_entry.delete(0, END)

    Button(win, text="Сохранить", command=save).pack(pady=5)
    Button(win, text="Назад", command=win.destroy).pack()


# Открывает окно просмотра с выбором года и месяца
# и областью для вывода найденных событий.
def open_events():
    win = Toplevel(root)
    win.title("Просмотр событий")
    win.geometry("750x450")

    today = date.today()

    # Четыре блока окна: текущая дата, кнопки, выбор периода и список событий.
    top = Frame(win, bg="lightblue")
    top.pack(side=TOP, fill=X)
    Label(top, text="Сегодня: " + today.strftime("%d.%m.%Y") +
          ", " + days[today.weekday()], bg="lightblue",
          font=("Arial", 14)).pack(pady=10)

    bottom = Frame(win)
    bottom.pack(side=BOTTOM, fill=X, pady=10)

    left = Frame(win)
    left.pack(side=LEFT, padx=15, pady=10, fill=Y)

    right = Frame(win)
    right.pack(side=LEFT, padx=10, pady=10, fill=BOTH, expand=True)

    # По умолчанию подставляем текущий год; месяц пользователь выбирает сам.
    Label(left, text="Введите год:").pack()
    year_entry = Entry(left, width=15)
    year_entry.pack(pady=5)
    year_entry.insert(0, str(today.year))

    Label(left, text="Выберите месяц:").pack(pady=5)
    # Сохраняем выбор месяца при переходе к другим полям.
    month_list = Listbox(left, height=12, selectmode=SINGLE,
                        exportselection=0)
    month_list.pack()

    for month in months:
        month_list.insert(END, month)

    Label(right, text="События", font=("Arial", 14)).pack()
    result = Text(right, width=45, height=18)
    result.pack(fill=BOTH, expand=True)

    # Обработчик кнопки «Просмотр»: находит события за выбранный месяц
    # и показывает их даты, дни недели и число дней до или после события.
    def show_events():
        # Убираем предыдущие результаты перед новым поиском.
        result.delete(1.0, END)
        year = year_entry.get()
        selected = month_list.curselection()

        # Для поиска нужны четырёхзначный ненулевой год и выбранный месяц.
        if not year.isdigit() or len(year) != 4 or year == "0000":
            result.insert(END, "Введите правильный год")
            return

        if len(selected) == 0:
            result.insert(END, "Выберите месяц")
            return

        month = selected[0] + 1
        # Шаблон YYYY-MM-% выбирает все даты нужного месяца.
        search_date = year + "-" + str(month).zfill(2) + "-%"

        cursor.execute(
            "SELECT event_date, name FROM events WHERE event_date LIKE ? ORDER BY event_date",
            (search_date,)
        )
        events = cursor.fetchall()

        if len(events) == 0:
            result.insert(END, "Событий нет")
            return

        for event_date, name in events:
            d = datetime.strptime(event_date, "%Y-%m-%d").date()
            # Положительная разница — событие впереди, отрицательная — уже прошло.
            difference = (d - date.today()).days

            if difference > 0:
                status = "Осталось дней: " + str(difference)
            elif difference < 0:
                status = "Прошло дней: " + str(-difference)
            else:
                status = "Сегодня"

            result.insert(END, "Событие: " + name + "\n")
            result.insert(END, "Дата: " + d.strftime("%d.%m.%Y") + "\n")
            result.insert(END, "День недели: " + days[d.weekday()] + "\n")
            result.insert(END, status + "\n\n")

    Button(bottom, text="Просмотр", width=15,
           command=show_events).pack(side=LEFT, padx=20)
    Button(bottom, text="Назад", width=15,
           command=win.destroy).pack(side=RIGHT, padx=20)


# Заголовок, логотип и кнопки главного меню.
Label(root, text="Календарь событий",
      font=("Arial", 20)).pack(pady=15)

try:
    # Сохраняем ссылку на изображение, чтобы Tkinter не удалил его.
    logo = PhotoImage(file="logo.gif")
    Label(root, image=logo).pack(pady=10)
# Если логотип отсутствует или не читается, показываем текст.
except TclError:
    Label(root, text="Календарь",
          font=("Arial", 24)).pack(pady=10)

Button(root, text="Добавить событие", width=25,
       command=add_event).pack(pady=10)
Button(root, text="Просмотр событий", width=25,
       command=open_events).pack(pady=10)

# Обрабатываем действия пользователя до закрытия главного окна.
root.mainloop()
# После закрытия окна освобождаем соединение с базой.
db.close()
