from dataclasses import dataclass, asdict
from typing import TypeVar, Generic, Optional, Any, List
import json
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler

T = TypeVar('T')

@dataclass
class BaseResponse(Generic[T]):    
    success: bool
    message: str
    data: Optional[T] = None

    def _to_json(self) -> str:
        """Mengonversi object dataclass menjadi string JSON."""
        # asdict otomatis mengubah dataclass menjadi dictionary
        return json.dumps(asdict(self))

    def to_bytes(self) -> bytes:
        return self._to_json.encode('utf-8')
    
@dataclass
class KMeansResponse():
    ret: float
    labels: List[int]
    centers: List[List[float]]


    
