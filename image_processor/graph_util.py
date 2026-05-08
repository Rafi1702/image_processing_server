import dataclasses
import numpy as np
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

@dataclasses
class Node():
    index: int
    weight: float
    nodes: list['Node']

class GraphBuilder(Generic[T],ABC):
    def __init__(self):
        self.nodes: list[Node] = []

    @abstractmethod
    def build_graph(self, source: T):
        pass


class GraphBuilderOpenCv(GraphBuilder[np.ndarray]):
    def __init__(self):
        super().__init__()
        

    def build_graph(self, source: np.ndarray):
        pass