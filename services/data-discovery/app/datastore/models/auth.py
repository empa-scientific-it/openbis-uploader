from pydantic import BaseModel
from typing import Dict, Optional, Tuple, List

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: str | None = None
    aud: str | None | List[str] = None




class TokenCache(BaseModel):
    items: Dict[Tuple[str, str], str]  = {}

    def store(self, url: str, user: str, token:str):
        """
        Stores an entry (token) of (url, user)
        """
        
        self.items.update((url, user), token)
    
    def retreive(self, url: str, user: str) -> Optional[str]:
        """
        Given an url and the corresponding user, retreive
        the token (if available)
        """
        self.items.get((url, user))