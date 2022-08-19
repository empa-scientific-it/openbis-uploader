from dataclasses import dataclass
import pydantic
from pydantic import BaseSettings
import pathlib as pl
from typing import List,Dict, Any, Literal
import yaml
from functools import lru_cache




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
    ldap_server: str
    ldap_port: int
    ldap_principal_name: str
    ldap_principal_password: str
    ldap_base: str
    openbis_server: str
    jws_secret_key: str
    jws_algorithm:str = "HS256"
    jws_access_token_expire_minutes = 30
    ldap_authentication: Literal['ANONYMOUS', 'SIMPLE', 'SASL', 'NTLM'] | None = 'SIMPLE'
    instances: List[str] | None = None 
    port: int = 8080
    host: str = "localhost"
    class Config:
        env_file = pl.Path(__file__).resolve().parent.parent.parent / ".env"
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                env_settings,
                file_secret_settings,
            )

@lru_cache()
def get_settings() -> DataStoreSettings:
    return DataStoreSettings()