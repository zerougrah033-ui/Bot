import sqlite3

conn = sqlite3.connect("database/database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS warnings (
    guild_id INTEGER,
    user_id INTEGER,
    warns INTEGER DEFAULT 0,
    PRIMARY KEY (guild_id, user_id)
)
""")

conn.commit()


def add_warning(guild_id: int, user_id: int):
    cursor.execute(
        "INSERT OR IGNORE INTO warnings (guild_id, user_id, warns) VALUES (?, ?, 0)",
        (guild_id, user_id)
    )

    cursor.execute(
        "UPDATE warnings SET warns = warns + 1 WHERE guild_id = ? AND user_id = ?",
        (guild_id, user_id)
    )

    conn.commit()


def get_warnings(guild_id: int, user_id: int):
    cursor.execute(
        "SELECT warns FROM warnings WHERE guild_id = ? AND user_id = ?",
        (guild_id, user_id)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    return 0


def remove_warning(guild_id: int, user_id: int):
    cursor.execute(
        "UPDATE warnings SET warns = CASE WHEN warns > 0 THEN warns - 1 ELSE 0 END WHERE guild_id = ? AND user_id = ?",
        (guild_id, user_id)
    )

    conn.commit()


def reset_warnings(guild_id: int, user_id: int):
    cursor.execute(
        "DELETE FROM warnings WHERE guild_id = ? AND user_id = ?",
        (guild_id, user_id)
    )

    conn.commit()
