import sqlite3




class DataBase:
    db_path = 'database/sqlite3.db'


    @staticmethod
    def execute(sql: str, parameters: tuple = tuple(),
                fetchone=False, fetchall=False, commit=False):
        connection = sqlite3.connect(DataBase.db_path)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)
        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data


    @staticmethod
    def extract_kwargs(sql: str, parameters: dict, _and: bool = True) -> tuple:
        sql += ('AND' if _and else ', ').join([f'{key} = ?' for key in parameters])
        return sql, tuple(parameters.values())
