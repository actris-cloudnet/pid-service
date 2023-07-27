from typing import Optional

from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    handle_server_url: AnyUrl
    prefix: str
    certificate_only: Optional[str] = None
    private_key: Optional[str] = None
    ca_verify: bool
