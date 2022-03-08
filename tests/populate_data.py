from api.ecoindex.models.responses import ApiEcoindex
from api.helper import new_uuid
from api.models.enums import Version
from faker import Faker
from faker_enum import EnumProvider
from settings import DATABASE_URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from typer import progressbar


async def create_data(count: int = 10):
    engine = create_async_engine(DATABASE_URL)

    faker = Faker()
    faker.add_provider(EnumProvider)

    async with AsyncSession(engine) as session:
        with progressbar(range(count)) as progress:
            for _ in progress:
                id = new_uuid()
                base_url = faker.url()
                url = f"{base_url}{id}"
                initial_ranking = faker.pyint(min_value=0, max_value=100)

                session.add(
                    ApiEcoindex(
                        id=id,
                        version=faker.enum(Version),
                        width=faker.pyint(min_value=300, max_value=3000, step=10),
                        height=faker.pyint(min_value=200, max_value=2000, step=10),
                        host=base_url,
                        date=faker.date_time_this_year(),
                        page_type="",
                        size=faker.pyfloat(min_value=100, max_value=10000),
                        nodes=faker.pyint(min_value=10, max_value=1000),
                        requests=faker.pyint(min_value=1, max_value=100),
                        grade=faker.pystr(),
                        score=faker.pyint(min_value=0, max_value=100),
                        ges=faker.pyfloat(min_value=0),
                        water=faker.pyfloat(min_value=0),
                        url=url,
                        initial_ranking=initial_ranking,
                        initial_total_results=faker.pyint(min_value=initial_ranking),
                    )
                )
                await session.commit()
        await session.close()
