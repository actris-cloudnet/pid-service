"""pid-service module"""
import sys
from configparser import SectionProxy
from typing import Union

import requests
from fastapi import HTTPException
from requests import HTTPError, Session, Timeout, TooManyRedirects


class PidGenerator:
    """A class for interfacing with Handle-server."""

    def __init__(self, options: SectionProxy, session=requests.Session()):
        self._options = options
        self._session = self._init_session(options, session)
        self._types = {"file": "1", "collection": "2", "instrument": "3"}

    def __del__(self):
        if hasattr(self, "_session"):
            session_url = f'{self._options["handle_server_url"]}api/sessions/this'
            self._session.delete(session_url)
            self._session.close()

    def generate_pid(self, pid_type: str, uuid: str, url: str) -> str:
        """Generates PID from given UUID."""
        server_url = f'{self._options["handle_server_url"]}api/handles/'
        prefix = self._options["prefix"]

        if pid_type not in self._types:
            raise HTTPException(status_code=422, detail=f"Unknown type: {pid_type}")

        typeid = self._types[pid_type]
        uuid_nodashes = uuid.replace("-", "")
        short_uuid = uuid_nodashes[:16]
        suffix = f"{typeid}.{short_uuid}"
        handle = f"{prefix}/{suffix}"

        try:
            res = self._session.put(f"{server_url}{handle}", json=self._get_payload(url))
            res.raise_for_status()
        except HTTPError as err:
            if res.status_code == 401:
                self._session = self._init_session(self._options, requests.Session())
                raise HTTPException(
                    status_code=503,
                    detail="Upstream PID service failed with status 401, " "resetting session.",
                ) from err
            raise HTTPException(
                status_code=502,
                detail=f"Upstream PID service failed with status "
                f"{res.status_code}:\n{res.text}",
            ) from err
        except (ConnectionError, TooManyRedirects, Timeout) as err:
            raise HTTPException(
                status_code=503, detail="Could not connect to upstream PID service"
            ) from err

        if res.status_code == 200:
            print(f"WARN: Handle {handle} already exists, updating handle.", file=sys.stderr)

        return f'https://hdl.handle.net/{res.json()["handle"]}'

    def _init_session(self, options: SectionProxy, session: Session) -> Session:
        """Initialize session with Handle server."""
        session.verify = self.str2bool(options["ca_verify"])
        session.headers["Content-Type"] = "application/json"

        # Authenticate session
        session_url = f'{options["handle_server_url"]}api/sessions'
        session.headers["Authorization"] = 'Handle clientCert="true"'
        cert = (self.str2bool(options["certificate_only"]), self.str2bool(options["private_key"]))
        res = session.post(session_url, cert=cert)
        res.raise_for_status()
        session_id = res.json()["sessionId"]
        session.headers["Authorization"] = f"Handle sessionId={session_id}"

        return session

    def _get_payload(self, target_url: str) -> dict:
        """Form a Handle-compliant payload."""
        return {
            "values": [
                {"index": 1, "type": "URL", "data": {"format": "string", "value": target_url}},
                {
                    "index": 100,
                    "type": "HS_ADMIN",
                    "data": {
                        "format": "admin",
                        "value": {
                            "handle": f'0.NA/{self._options["prefix"]}',
                            "index": 200,
                            "permissions": "011111110011",
                        },
                    },
                },
            ]
        }

    @staticmethod
    def str2bool(the_string: str) -> Union[bool, str]:
        """Converts string to bool"""
        return False if the_string == "False" else True if the_string == "True" else the_string
