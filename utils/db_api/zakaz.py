import asyncio

import asyncpg
from asyncpg.pool import Pool

from data import config



class Zakaz:
    def __init__(self, pool):
        self.pool: Pool = pool

    @classmethod
    async def create(cls):
        pool = await asyncpg.create_pool(
            user=config.PGUSER,
            password=config.PGPASSWORD,
            host=config.ip,
        )
        return cls(pool)

    async def create_table_zakaz(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Zakaz (
            id_zakaz INT NOT NULL,
            id_user INT NOT NULL,
            id_item INT NOT NULL,
            status VARCHAR(255) NOT NULL,
            name_user VARCHAR(255),
            PRIMARY KEY (id_zakaz)
            );
"""
        await self.pool.execute(sql)


    async def add_zakaz(self, id_zakaz: int,id_user: int , id_item: int , status:str,name_user:str =None ):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO Zakaz(id_zakaz,id_user,id_item,status,name_user) VALUES($1, $2, $3 ,$4 ,$5)
        """
        await self.pool.execute(sql, id_zakaz,id_user,id_item,status,name_user)


    async def update_status(self, status:str, id):
        sql = f"""
        UPDATE Users SET status=$1 WHERE id=$2
        """
        return await self.pool.execute(sql, status, id)