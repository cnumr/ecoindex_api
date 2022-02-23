import sys
import uuid
from asyncio import run

from api.ecoindex.models.responses import ApiEcoindex
from api.models.enums import Version
from faker import Faker
from faker_enum import EnumProvider
from settings import DATABASE_URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

num_records = int(sys.argv[1])


async def create_data():
    engine = create_async_engine(DATABASE_URL)

    faker = Faker()
    faker.add_provider(EnumProvider)

    async with AsyncSession(engine) as session:
        for _ in range(num_records):
            session.add(
                ApiEcoindex(
                    id=uuid.uuid1(),
                    version=faker.enum(Version),
                    width=faker.pyint(min_value=300, max_value=3000, step=10),
                    height=faker.pyint(min_value=200, max_value=2000, step=10),
                    host=faker.url(),
                    date=faker.date_object(),
                    page_type="",
                    size=faker.pyfloat(min_value=100, max_value=10000),
                    nodes=faker.pyint(min_value=10, max_value=1000),
                    requests=faker.pyint(min_value=1, max_value=100),
                    grade=faker.pystr(),
                    score=faker.pyint(min_value=0, max_value=100),
                    ges=faker.pyfloat(min_value=0),
                    water=faker.pyfloat(min_value=0),
                )
            )
            await session.commit()
        await session.close()


if __name__ == "__main__":
    run(create_data())
