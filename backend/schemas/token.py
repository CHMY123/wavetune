from pydantic import BaseModel
from typing import Optional, Dict

class Token(BaseModel):
    code: int
    msg: str
    data: Dict[str, Optional[str | Dict]]