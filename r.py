from cache import RedisCache
from config import settings
from dataclasses import dataclass

@dataclass
class User:
    cnpj: str

kaio = User(cnpj=0)

db = RedisCache(url=settings.URL_EXTERNO, empresa=kaio)