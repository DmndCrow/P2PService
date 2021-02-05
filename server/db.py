import sqlite3
from datetime import datetime


class DB:
    def __init__(self, db_file: str) -> None:
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cr = self.conn.cursor()

        self.GenerateTables()

    def GenerateTables(self) -> None:
        sql_user_table = """ CREATE TABLE IF NOT EXISTS users (
                                id integer PRIMARY KEY,
                                host text NOT NULL,
                                port text NOT NULL,
                                folder text,
                                connect_date text NOT NULL
                            ); """
        self.cr.execute(sql_user_table)

    def AddUser(self, host: str, port: str):
        sql = 'INSERT INTO users(host, port, connect_date) VALUES (?, ?, ?)'
        vals = (host, port, datetime.now())
        self.cr.execute(sql, vals)
        self.conn.commit()

    def GetData(self):
        sql = 'SELECT * FROM users'
        self.cr.execute(sql)
        data = []
        for row in self.cr.fetchall():
            data.append(
                dict(zip([column[0] for column in self.cr.description], row))
            )
        return data

    def AssignFolderPath(self, host, port, folder):
        sql = 'UPDATE users SET folder=? WHERE host=? AND port=?'
        vals = (folder, host, port)
        self.cr.execute(sql, vals)
        self.conn.commit()

    def DeleteUser(self, host: str, port: str) -> None:
        sql = 'DELETE FROM users WHERE host=? AND port=?'
        vals = (host, port)
        self.cr.execute(sql, vals)
        self.conn.commit()


class Action:
    get = 'GET'
    share = 'SHARE'
    download = 'DOWNLOAD'
    exit = 'EXIT'
