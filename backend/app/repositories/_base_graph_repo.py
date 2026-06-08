from neo4j import AsyncSession as Neo4jAsyncSession


class BaseGraphRepo:
    def __init__(self, session: Neo4jAsyncSession) -> None:
        self.session = session
