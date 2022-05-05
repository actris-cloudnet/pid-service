"""pid-service module"""
import sys
from enum import Enum
from uuid import UUID

import requests
from fastapi import HTTPException
from pydantic import BaseModel, HttpUrl
from requests import HTTPError, Session, Timeout, TooManyRedirects

from .config import Settings


class PidType(str, Enum):
    FILE = "file"
    COLLECTION = "collection"
    INSTRUMENT = "instrument"


class PidRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """PidRequest class."""

    type: PidType
    uuid: UUID
    url: HttpUrl


class PidGenerator:
    """A class for interfacing with Handle-server."""

    def __init__(self, settings: Settings, session=requests.Session()):
        self._settings = settings
        self._session = self._init_session(session)
        self._types = {PidType.FILE: "1", PidType.COLLECTION: "2", PidType.INSTRUMENT: "3"}

    def __del__(self):
        if hasattr(self, "_session"):
            session_url = f"{self._settings.handle_server_url}api/sessions/this"
            self._session.delete(session_url)
            self._session.close()

    def generate_pid(self, request: PidRequest) -> str:
        """Generates PID from given UUID."""

        typeid = self._types[request.type]
        short_uuid = request.uuid.hex[:16]
        suffix = f"{typeid}.{short_uuid}"
        handle = f"{self._settings.prefix}/{suffix}"

        try:
            server_url = f"{self._settings.handle_server_url}api/handles/{handle}"
            res = self._session.put(server_url, json=self._get_payload(request))
            res.raise_for_status()
        except HTTPError as err:
            if res.status_code == 401:
                self._session = self._init_session(requests.Session())
                raise HTTPException(
                    status_code=503,
                    detail="Upstream PID service failed with status 401, resetting session.",
                ) from err
            raise HTTPException(
                status_code=502,
                detail=f"Upstream PID service failed with status {res.status_code}:\n{res.text}",
            ) from err
        except (ConnectionError, TooManyRedirects, Timeout) as err:
            raise HTTPException(
                status_code=503, detail="Could not connect to upstream PID service"
            ) from err

        if res.status_code == 200:
            print(f"WARN: Handle {handle} already exists, updating handle.", file=sys.stderr)

        return f'https://hdl.handle.net/{res.json()["handle"]}'

    def _init_session(self, session: Session) -> Session:
        """Initialize session with Handle server."""
        session.verify = self._settings.ca_verify
        session.headers["Content-Type"] = "application/json"

        # Authenticate session
        session_url = f"{self._settings.handle_server_url}api/sessions"
        session.headers["Authorization"] = 'Handle clientCert="true"'
        if self._settings.certificate_only and self._settings.private_key:
            cert = (self._settings.certificate_only, self._settings.private_key)
        else:
            cert = None
        res = session.post(session_url, cert=cert)
        res.raise_for_status()
        session_id = res.json()["sessionId"]
        session.headers["Authorization"] = f"Handle sessionId={session_id}"

        return session

    def _get_payload(self, request: PidRequest) -> dict:
        """Form a Handle-compliant payload."""
        return {
            "values": [
                {"index": 1, "type": "URL", "data": {"format": "string", "value": request.url}},
                {
                    "index": 100,
                    "type": "HS_ADMIN",
                    "data": {
                        "format": "admin",
                        "value": {
                            "handle": f"0.NA/{self._settings.prefix}",
                            "index": 200,
                            "permissions": "011111110011",
                        },
                    },
                },
            ]
        }
