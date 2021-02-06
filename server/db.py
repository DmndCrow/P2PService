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
                                listen text NOT NULL,
                                folder text,
                                connect_date text NOT NULL
                            ); """

        sql_file_table = """ CREATE TABLE IF NOT EXISTS files (
                                id integer PRIMARY KEY,
                                name text NOT NULL,
                                userId integer NOT NULL
                            ); """
        self.cr.execute(sql_user_table)
        self.cr.execute(sql_file_table)
        self.conn.commit()

    def AddUser(self, host: str, port: str, listen_port: str):
        sql = 'INSERT INTO users(host, port, listen, connect_date) VALUES (?, ?, ?, ?)'
        vals = (host, port, listen_port, datetime.now())
        self.cr.execute(sql, vals)
        self.conn.commit()

    def GetUsers(self):
        sql = 'SELECT * FROM users'
        self.cr.execute(sql)
        data = []
        for row in self.cr.fetchall():
            data.append(
                dict(zip([column[0] for column in self.cr.description], row))
            )
        return data

    def GetFiles(self, host, port):
        user = self.GetUser(host, port)
        sql = 'SELECT name FROM files WHERE userId!=?'
        self.cr.execute(sql, (user['id'],))

        return [row for row in self.cr.fetchall()]

    def GetUser(self, host, port):
        sql = 'SELECT * FROM users WHERE host=? AND port=?'
        self.cr.execute(sql, (host, port))
        return dict(zip([column[0] for column in self.cr.description], self.cr.fetchone()))

    def AssignFolderPath(self, host, port, folder, files):
        user = self.GetUser(host, port)
        print(user)

        sql = 'UPDATE users SET folder=? WHERE id=?'
        vals = (folder, user['id'])
        self.cr.execute(sql, vals)

        sql = 'DELETE FROM files WHERE userId=?'
        self.cr.execute(sql, (user['id'],))

        for file in files:
            sql = 'INSERT INTO files (name, userId) VALUES (?, ?)'
            vals = (file, user['id'])
            self.cr.execute(sql, vals)
        self.conn.commit()

    def DeleteUser(self, host: str, port: str) -> None:
        """
        DELETE user and files that stored on his side
        :param host: client host
        :param port: client port
        :return: None
        """
        user = self.GetUser(host, port)

        sql = 'DELETE FROM files WHERE userId=?'
        self.cr.execute(sql, user['id'])

        sql = 'DELETE FROM users WHERE id=?'
        self.cr.execute(sql, user['id'])

        self.conn.commit()


class Action:
    get = 'GET'
    share = 'SHARE'
    download = 'DOWNLOAD'
    exit = 'EXIT'
