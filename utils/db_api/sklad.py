import asyncpg
from asyncpg.pool import Pool

from data import config


class Sklad:
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

    async def create_table_new(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Electronika (
            id INT NOT NULL,
            name varchar(255) NOT NULL,
            description varchar(255) NOT NULL,
            price int NOT NULL,
            photo varchar(255) NOT NULL,
            PRIMARY KEY (id)
            );
"""
        await self.pool.execute(sql)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num + 1}" for num, item in enumerate(parameters)
        ])
        return sql, tuple(parameters.values())

    async def add_item(self, id: int, name: str, description: str, price: int, photo: str):
        sql = """
        INSERT INTO Electronika (id, name,description,price,photo) VALUES($1, $2, $3, $4 ,$5)
        """
        await self.pool.execute(sql, id, name, description, price, photo)

    async def select_all_items(self):
        sql = """
        SELECT * FROM Electronika
        """
        return await self.pool.fetch(sql)

    async def one_item(self, **kwargs):
        sql = f"""
        SELECT * FROM Electronika WHERE 
        """
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.pool.fetchrow(sql, *parameters)

    async def all(self):
        return await self.pool.fetchval("SELECT COUNT(*) FROM Electronika")


    async def delete(self):
        await self.pool.execute("DELETE FROM New WHERE TRUE")

    async def like(self, exp):
        sql = f"""
SELECT * FROM Electronika WHERE name LIKE '%{exp}%' OR description LIKE '%{exp}%'
"""
        return await self.pool.fetch(sql)


    async def sort(self):
        sql = 'SELECT * FROM Electronika name ORDER BY name'
        return await self.pool.fetch(sql)
