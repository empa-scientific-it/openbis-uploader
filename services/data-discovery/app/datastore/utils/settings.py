from dataclasses import dataclass
import pydantic
from pydantic import BaseSettings
import pathlib as pl
from typing import List,Dict, Any, Literal
import yaml
from functools import lru_cache
from fastapi.logger import logger



def yaml_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    A BaseSetting settings source that loads variables from a YAML file
    """
    return yaml.load(pl.Path('config.yml').read_text(), yaml.Loader)


class DataStoreSettings(BaseSettings):
    """
    Class to represent the settings of the datastore
    """
    base_path: pl.Path = pl.Path('/usr/stores/') 
    ldap_group_attribute:str = 'cn'
    ldap_server: str
    ldap_port: int
    ldap_principal_name: str
    ldap_principal_password: str
    ldap_base: str
    redis_host: str 
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str
    openbis_server: str
    jws_secret_key: str
    jws_algorithm:str = "HS256"
    jws_access_token_expire_minutes: int = 30
    ldap_authentication: Literal['ANONYMOUS', 'SIMPLE', 'SASL', 'NTLM'] | None = 'SIMPLE'
    instances: List[str] | None = None 
    credentials_storage_key: str = None 
    port: int = 8080
    host: str = "localhost"
    task_serialiser: str = 'pickle'
    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = pl.Path(__file__).resolve().parent.parent.parent / ".env"
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                env_settings, init_settings
            )

@lru_cache()
def get_settings() -> DataStoreSettings:
    logger.info("Here")
    return DataStoreSettings()