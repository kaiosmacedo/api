import logging
import pickle
from typing import Any, Optional
import redis  # type: ignore
from contextlib import suppress
 
with suppress(ModuleNotFoundError):
    from config import settings as s
 
 
class RedisCache:
    def __init__(self, url:str, empresa: Any):
        
        self.db = Optional[redis.Redis]
        try:
            self.db = redis.Redis.from_url(url)
            self.db.config_set("maxmemory-policy", "allkeys-lru")
            # logging.info("Redis inicializado")
        except Exception:
            self.db = None
 
        self.empresa = empresa
 
    def __str__(self):
        try:
            cls = type(self).__name__
            return "{}(host={}, port={}, data={})".format(
                cls, self.__host, self.__port, list(self.dict().keys())
            )
        except Exception:
            return None
 
    def __getitem__(self, key: str) -> Any:
        """Método para recuperar um valor do cache."""
        try:
            if not s.CACHING:
                return None
            value = self.get(key)
            if value:
                # logging.debug(f"Retornando cache do redis: {value}")
                return value
 
            raise ValueError("Item não encontrado")
        except Exception:
            return None
 
    def set(self, key: str, value: Any):
        try:
            if not s.CACHING:
                return None
 
            value = pickle.dumps(value)
 
            self.db.hset(self.empresa.cnpj, key, value)  # type: ignore
 
            # self.db.set(key, value)
        except Exception:
            return None
 
    def get(self, key: str) -> Optional[Any]:
        """Método para recuperar um valor do cache."""
        try:
            if not s.CACHING:
                return None
 
            value = self.db.hget(self.empresa.cnpj, key)  # type: ignore
            try:
                if value is not None:
                    # value = self.db.get(key)
                    processed_value = int(value.decode("utf-8"))
                    return processed_value
            except Exception:
                pass
 
            if isinstance(value, int):
                return value
 
            if value:
                serialized = pickle.loads(value)
                # logging.debug(f"Retornando cache do redis {serialized}")
                return serialized
 
            return None
        except Exception:
            return None
 
    def __setitem__(self, key: str, value: Any) -> None:
        """Método para definir um valor no cache."""
        try:
            if not s.CACHING:
                return None
 
            value_dumped = pickle.dumps(value)
 
            if isinstance(key, tuple):
                key_ttl = key[1]
                if key_ttl is None:
                    key_ttl = int(str(s.CACHE_DEFAULT_TIMEOUT))
                    key_name = key[0]
                    self.db.hset(self.empresa.cnpj, key_name, value_dumped)  # type: ignore
                    self.db.expire(self.empresa.cnpj, int(key_ttl))  # type: ignore
                    logging.debug(f"Ajustando ttl como {key_ttl} para {key_name}, {value}")
 
                elif key_ttl == 0:
                    key_name = key[0]
                    self.db.hset(self.empresa.cnpj, key_name, value_dumped)  # type: ignore
                    logging.debug(f"Ajustando ttl como indefinido para {key_name}, {value}")
 
            else:
                t = str(s.CACHE_DEFAULT_TIMEOUT)
                self.db.hset(self.empresa.cnpj, key, value_dumped)  # type: ignore
                self.db.expire(self.empresa.cnpj, int(t))  # type: ignore
 
            logging.debug(f"Atribuindo valor ao redis: {value}")
        except Exception:
            pass
 
    def store_dict(self, data: dict) -> None:
        """Método para armazenar um dicionário completo no cache."""
 
        try:
            for key, value in data.items():
                self[key] = value
            logging.info(f"Armazenando dicionario ao redis: {data}")
        except Exception:
            pass
 
    def dict(self) -> dict:
        """
        Método para recuperar todos os pares chave-valor
        do cache como um dicionário.
        """
        try:
            hash_data = {}
            hash_data_bytes = self.db.hgetall(self.empresa.cnpj)  # type: ignore
            for field, value in hash_data_bytes.items():
                decoded_key = field.decode("utf-8")
                decoded_value = pickle.loads(value)
                hash_data[decoded_key] = decoded_value
 
            return hash_data
        except Exception:
            return {}
 
    def delete(self, key: str) -> None:
        try:
            hash_set_name = self.empresa.cnpj
            self.db.hdel(hash_set_name, key)  # type: ignore
            self.db.delete(key)  # type: ignore
            logging.info(f"Deletando chave do redis: {key}")
        except Exception:
            return None
 
    def clear(self) -> None:
        try:
            self.db.delete(self.empresa.cnpj)  # type: ignore
            logging.info("Limpando cache do redis")
        except Exception:
            return None
 
    def set_user(self, user):
        r = self.db
        if not isinstance(r, redis.Redis):
            raise
 
        r.sadd('ws::users', pickle.dumps(user))
 
    def disconnect_user(self, user):
        r = self.db
        if not isinstance(r, redis.Redis):
            raise
 
        r.srem('ws::users', pickle.dumps(user))
    
    def get_users(self):
        r = self.db
        if not isinstance(r, redis.Redis):
            raise
 
        users = r.smembers('ws::users')
        users = [pickle.loads(user) for user in users]
                
        return set(users) if users else set()