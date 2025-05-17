import sqlite3
import os
import time

DB_PATH = os.path.join("data", "plango.db")

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS masterclasses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            time TEXT NOT NULL,
            location TEXT NOT NULL,
            capacity INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            user_id INTEGER NOT NULL,
            masterclass_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('registered', 'waitlist', 'confirmed')),
            timestamp INTEGER NOT NULL,
            PRIMARY KEY (user_id, masterclass_id),
            FOREIGN KEY (masterclass_id) REFERENCES masterclasses(id)
        )
    """)

    conn.commit()
    conn.close()

def get_all_masterclasses():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, time, location, capacity FROM masterclasses")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_masterclass_by_id(mc_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM masterclasses WHERE id = ?", (mc_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_registration(user_id, mc_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT status FROM registrations WHERE user_id = ? AND masterclass_id = ?", (user_id, mc_id))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def count_registered(mc_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM registrations WHERE masterclass_id = ? AND status = 'registered'", (mc_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count

def count_waiting(mc_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM registrations WHERE masterclass_id = ? AND status = 'waiting'", (mc_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count

def register_user(user_id, mc_id):
    mc = get_masterclass_by_id(mc_id)
    if not mc:
        return "Такого мастер-класса не существует."

    capacity = mc[4]
    status = get_registration(user_id, mc_id)

    if status == "registered":
        return "Вы уже зарегистрированы на этот мастер-класс."
    if status == "waiting":
        return "Вы уже в листе ожидания."

    current_registered = count_registered(mc_id)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if current_registered < capacity:
        cur.execute("INSERT OR REPLACE INTO registrations VALUES (?, ?, ?, ?)", (user_id, mc_id, "registered", int(time.time())))
        result = "Вы успешно записались на мастер-класс!"
    else:
        cur.execute("INSERT OR REPLACE INTO registrations VALUES (?, ?, ?, ?)", (user_id, mc_id, "waiting", int(time.time())))
        position = count_waiting(mc_id) + 1
        result = f"Мест нет. Вы добавлены в лист ожидания. Ваш номер: {position}"
    conn.commit()
    conn.close()
    return result

def add_test_masterclasses():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("INSERT OR REPLACE INTO masterclasses VALUES (1, 'AI Basics', '15:00', 'Аудитория 101', 2)")
    cur.execute("INSERT OR REPLACE INTO masterclasses VALUES (2, 'Design Thinking', '16:30', 'Аудитория 202', 3)")
    cur.execute("INSERT OR REPLACE INTO masterclasses VALUES (3, 'Презентации и Питчинг', '18:00', 'Зал конференций', 1)")

    conn.commit()
    conn.close()
