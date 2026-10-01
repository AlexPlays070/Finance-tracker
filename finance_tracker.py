"""
Проект: «Учёт личных финансов»
Консольное приложение на Python (только стандартная библиотека).

Возможности:
  1. Добавление доходов и расходов
  2. Просмотр всех операций
  3. Статистика по категориям (с текстовой диаграммой)
  4. Удаление операции
  5. Экспорт в CSV
Данные хранятся в базе SQLite (файл finance.db).
"""

import csv
import sqlite3
from datetime import date, datetime

DB_NAME = "finance.db"
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Учёба", "Здоровье", "Зарплата", "Другое"]


# ---------- Работа с базой данных ----------

def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                kind TEXT NOT NULL CHECK (kind IN ('доход', 'расход')),
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                note TEXT
            )
            """
        )


def add_record(rec_date, kind, category, amount, note=""):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO records (date, kind, category, amount, note) VALUES (?, ?, ?, ?, ?)",
            (rec_date, kind, category, amount, note),
        )


def get_records():
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, date, kind, category, amount, note FROM records ORDER BY date, id"
        ).fetchall()


def delete_record(rec_id):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM records WHERE id = ?", (rec_id,))
        return cur.rowcount > 0


# ---------- Ввод данных с проверкой ----------

def input_amount():
    while True:
        text = input("Сумма: ").replace(",", ".").strip()
        try:
            value = float(text)
            if value <= 0:
                raise ValueError
            return round(value, 2)
        except ValueError:
            print("  Ошибка: введите положительное число.")


def input_date():
    while True:
        text = input("Дата (ГГГГ-ММ-ДД, Enter = сегодня): ").strip()
        if not text:
            return date.today().isoformat()
        try:
            return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
        except ValueError:
            print("  Ошибка: неверный формат даты.")


def choose_category():
    for i, name in enumerate(CATEGORIES, 1):
        print(f"  {i}. {name}")
    while True:
        text = input("Номер категории: ").strip()
        if text.isdigit() and 1 <= int(text) <= len(CATEGORIES):
            return CATEGORIES[int(text) - 1]
        print("  Ошибка: выберите номер из списка.")


# ---------- Пункты меню ----------

def menu_add():
    print("\n--- Новая операция ---")
    kind = "доход" if input("Тип (1 - доход, 2 - расход): ").strip() == "1" else "расход"
    rec_date = input_date()
    category = choose_category()
    amount = input_amount()
    note = input("Комментарий (необязательно): ").strip()
    add_record(rec_date, kind, category, amount, note)
    print("Операция добавлена!")


def menu_list():
    records = get_records()
    print("\n--- Все операции ---")
    if not records:
        print("Пока пусто.")
        return
    print(f"{'ID':<4}{'Дата':<12}{'Тип':<8}{'Категория':<14}{'Сумма':>10}  Комментарий")
    for rec_id, d, kind, cat, amount, note in records:
        sign = "+" if kind == "доход" else "-"
        print(f"{rec_id:<4}{d:<12}{kind:<8}{cat:<14}{sign}{amount:>9.2f}  {note or ''}")


def menu_stats():
    records = get_records()
    print("\n--- Статистика ---")
    if not records:
        print("Нет данных.")
        return
    income = sum(r[4] for r in records if r[2] == "доход")
    expense = sum(r[4] for r in records if r[2] == "расход")
    print(f"Доходы:  {income:10.2f}")
    print(f"Расходы: {expense:10.2f}")
    print(f"Баланс:  {income - expense:10.2f}")

    by_cat = {}
    for _, _, kind, cat, amount, _ in records:
        if kind == "расход":
            by_cat[cat] = by_cat.get(cat, 0) + amount
    if by_cat:
        print("\nРасходы по категориям:")
        for cat, total in sorted(by_cat.items(), key=lambda x: -x[1]):
            share = total / expense * 100
            bar = "█" * int(share / 4)
            print(f"  {cat:<13}{total:9.2f} {share:5.1f}% {bar}")


def menu_delete():
    menu_list()
    text = input("\nID для удаления (Enter - отмена): ").strip()
    if text.isdigit():
        print("Удалено." if delete_record(int(text)) else "Запись не найдена.")


def menu_export():
    records = get_records()
    filename = "finance_export.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["ID", "Дата", "Тип", "Категория", "Сумма", "Комментарий"])
        writer.writerows(records)
    print(f"Экспортировано записей: {len(records)} -> {filename}")


def main():
    init_db()
    actions = {
        "1": menu_add,
        "2": menu_list,
        "3": menu_stats,
        "4": menu_delete,
        "5": menu_export,
    }
    while True:
        print(
            "\n===== УЧЁТ ФИНАНСОВ =====\n"
            "1. Добавить операцию\n"
            "2. Показать все операции\n"
            "3. Статистика\n"
            "4. Удалить операцию\n"
            "5. Экспорт в CSV\n"
            "0. Выход"
        )
        choice = input("Выбор: ").strip()
        if choice == "0":
            print("До свидания!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Неверный пункт меню.")


if __name__ == "__main__":
    main()
