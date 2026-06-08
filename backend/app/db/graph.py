from neo4j import AsyncGraphDatabase

from app.core import get_settings

settings = get_settings()

neo4j_driver = AsyncGraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
)


async def init_neo4j():
    async with neo4j_driver.session() as session:
        # Create indexes
        # entity.group_id
        await session.run("""
            CREATE INDEX entity_group_id_index IF NOT EXISTS
            FOR (e:Entity)
            ON (e.group_id)
        """)

        # Create indexes
        await session.run("""
            CREATE INDEX relates_to_scenario_id_index IF NOT EXISTS
            FOR ()-[r:RELATES_TO]-()
            ON (r.scenario_id)
        """)
