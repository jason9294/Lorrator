from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    type: str
    label: str
    description: str


class GraphEdge(BaseModel):
    id: str
    type: str
    source: str
    target: str
    directed: bool


class Graph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
