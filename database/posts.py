from database.Base import DataBase


class Posts(DataBase):
    __slots__ = ('hashtag', 'post_id', 'id', 'name', 'Description', 'link', 'photo_id')

    def __init__(self, data: int | dict):
        super().__init__()
        if isinstance(data, int):
            post_data = self.read(id=data)
            if post_data is not None:
                data = {self.__slots__[i]: post_data[i] for i in range(len(self.__slots__))}
            else:
                # Обработка случая, когда запись с заданным id не найдена
                # Например, возбуждение исключения или установка значений по умолчанию
                pass
        self.hashtag = data.get('hashtag')
        self.id = data.get('id')
        self.name = data.get('name')
        self.Description = data.get('Description')
        self.link = data.get('link')
        self.photo_id = data.get('photo_id')
        self.create()
        self.post_id = self.read(id=self.id)[0] if self.read(id=self.id) is not None else None


    @staticmethod
    def create_table():
        sql = '''
            CREATE TABLE IF NOT EXISTS Posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                id INTEGER,
                name TEXT,
                Description TEXT,
                link TEXT,
                photo_id TEXT
                hashtag TEXT
            
            )
        '''
        DataBase.execute(sql, commit=True)

    def create(self):
        sql = '''INSERT INTO Posts (hashtag, id, name, Description, link, photo_id) VALUES ( ?, ?, ?, ?, ?, ?)'''
        DataBase.execute(sql, (self.id, self.hashtag, self.name, self.Description, self.link, self.photo_id), commit=True)




    def read(self, **kwargs):
        sql = '''SELECT * FROM Posts WHERE '''
        sql, params = DataBase.extract_kwargs(sql, kwargs)
        return DataBase.execute(sql, params, fetchone=True)




    def update(self, **kwargs):
        sql = '''UPDATE Posts SET'''
        sql, params = DataBase.extract_kwargs(sql, kwargs, _and=False)
        sql = sql + f' WHERE post_id = {self.post_id}'
        self.execute(sql, params, commit=True)




    def delete(self):
        sql = f'DELETE FROM Posts WHERE post_id = {self.post_id}'
        del self
        return DataBase.execute(sql, commit=True)