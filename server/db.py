import sqlite3
from datetime import datetime
from typing import List, Dict, Tuple


class DB:
    def __init__(self, db_file: str) -> None:
        """
        Initialize connection to db and create tables
        :param db_file: Sqlite3 database path
        """
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cr = self.conn.cursor()

        self.GenerateTables()

    def GenerateTables(self) -> None:
        """
        Generate tables if not exist
        :return: None
        """
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
                                size text NOT NULL,
                                userId integer NOT NULL
                            ); """
        self.cr.execute(sql_user_table)
        self.cr.execute(sql_file_table)
        self.conn.commit()

    def AddUser(self, host: str, port: str, listen_port: str) -> None:
        """
        Add client to database
        :param host: client host
        :param port: client port
        :param listen_port: client port that will listen to other clients
        :return: None
        """
        sql = 'INSERT INTO users(host, port, listen, connect_date) VALUES (?, ?, ?, ?)'
        vals = (host, port, listen_port, datetime.now())
        self.cr.execute(sql, vals)
        self.conn.commit()

    def GetUsers(self) -> List[Dict]:
        """
        Get all users from db
        :return: all users
        """
        sql = 'SELECT * FROM users'
        self.cr.execute(sql)
        data = []
        for row in self.cr.fetchall():
            data.append(
                dict(zip([column[0] for column in self.cr.description], row))
            )
        return data

    def GetFiles(self, host: str, port: str) -> List[Dict]:
        """
        Get all files that dont belong to client
        :param host: client host
        :param port: client port
        :return: List of files
        """
        # find user
        user = self.GetUser(host=host, port=port)

        # find files that dont belong to user
        sql = 'SELECT name, size FROM files WHERE userId!=?'
        self.cr.execute(sql, (user['id'],))

        return [row for row in self.cr.fetchall()]

    def GetFileInfo(self, host: str, port: str, file: str) -> Dict:
        """
        Get info about file
        :param host: client host
        :param port: client port
        :param file: name file, which we will search info about
        :return: info about filename
        """
        # find user
        user = self.GetUser(host=host, port=port)

        # find file by name and which doesnt belong to client
        sql = 'SELECT * FROM files WHERE name=? and userId!=?'
        self.cr.execute(sql, (file, user['id']))

        file_info = dict(zip([column[0] for column in self.cr.description], self.cr.fetchone()))
        user_to_connect = self.GetUser(user_id=file_info['userId'])
        return {
            'host': user_to_connect['host'],
            'port': user_to_connect['listen'],
            'folder': user_to_connect['folder'],
            'filename': file_info['name'],
            'size': file_info['size']
        }

    def GetUser(self, host=None, port=None, user_id=None) -> Dict:
        """
        Find user by params
        :param host: client host
        :param port: client port
        :param user_id: client id in database
        :return: client info
        """
        if user_id:
            sql = 'SELECT * FROM users WHERE id=?'
            self.cr.execute(sql, (user_id,))
        else:
            sql = 'SELECT * FROM users WHERE host=? AND port=?'
            self.cr.execute(sql, (host, port))
        return dict(zip([column[0] for column in self.cr.description], self.cr.fetchone()))

    def AssignFolderPath(self, host: str, port: str, folder: str, files: List[Tuple]) -> None:
        """
        Update data in database
        :param host: client host
        :param port: client port
        :param folder: new folder that client is sharing
        :param files: files from new folder
        :return: None
        """
        # find client
        user = self.GetUser(host=host, port=port)

        # update folder path
        sql = 'UPDATE users SET folder=? WHERE id=?'
        vals = (folder, user['id'])
        self.cr.execute(sql, vals)

        # delete files from previos folder
        sql = 'DELETE FROM files WHERE userId=?'
        self.cr.execute(sql, (user['id'],))

        # store files for new folder
        for file in files:
            sql = 'INSERT INTO files (name, size, userId) VALUES (?, ?, ?)'
            vals = (file[0], file[1], user['id'])
            self.cr.execute(sql, vals)
        self.conn.commit()

    def DeleteUser(self, host: str, port: str) -> None:
        """
        DELETE user and files that stored on his side
        :param host: client host
        :param port: client port
        :return: None
        """
        # find client
        user = self.GetUser(host=host, port=port)

        # delete user files
        sql = 'DELETE FROM files WHERE userId=?'
        self.cr.execute(sql, (user['id'],))

        # delete user
        sql = 'DELETE FROM users WHERE id=?'
        self.cr.execute(sql, (user['id'],))

        self.conn.commit()


# client actions
class Action:
    get = 'GET'
    share = 'SHARE'
    download = 'DOWNLOAD'
    exit = 'EXIT'
