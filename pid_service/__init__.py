"""Module containing classes / functions for PID generation."""
import sys
from configparser import SectionProxy

import requests
from fastapi import HTTPException
from typing import Union

from requests import HTTPError, Timeout, TooManyRedirects, Session


class PidGenerator:
    """The PidGenerator class."""

    def __init__(self, options: SectionProxy, session=requests.Session()):
        self._options = options
        self._session = self._init_session(options, session)
        self._types = {
           'file': '1',
           'collection': '2'
        }

    def __del__(self):
        if hasattr(self, '_session'):
            session_url = f'{self._options["handle_server_url"]}api/sessions/this'
            self._session.delete(session_url)
            self._session.close()

    def generate_pid(self, type: str, uuid: str) -> str:
        """Generates PID from given UUID."""
        server_url = f'{self._options["handle_server_url"]}api/handles/'
        prefix = self._options['prefix']

        if type not in self._types:
            raise HTTPException(status_code=422, detail=f"Unknown type: {type}")

        typeid = self._types[type]
        short_uuid = uuid[:16]
        suffix = f'{typeid}.{short_uuid}'
        handle = f'{prefix}/{suffix}'
        target_url = '/'.join([self._options["resolve_to_url"], type, uuid])
        print(target_url)

        try:
            res = self._session.put(f'{server_url}{handle}',
                                    json=self._get_payload(target_url))
            res.raise_for_status()
        except HTTPError:
            raise HTTPException(
                status_code=502,
                detail=f'Upstream PID service failed with status {res.status_code}:\n{res.text}')
        except (ConnectionError, TooManyRedirects, Timeout):
            raise HTTPException(
                status_code=503,
                detail=f'Could not connect to upstream PID service')

        if res.status_code == 200:
            print(f'WARN: Handle {handle} already exists, updating handle.', file=sys.stderr)

        return f'https://hdl.handle.net/{res.json()["handle"]}'

    def _init_session(self, options: SectionProxy, session: Session) -> Session:
        session.verify = self.str2bool(options['ca_verify'])
        session.headers['Content-Type'] = 'application/json'

        # Authenticate session
        session_url = f'{options["handle_server_url"]}api/sessions'
        session.headers['Authorization'] = 'Handle clientCert="true"'
        cert = (self.str2bool(options['certificate_only']), self.str2bool(options['private_key']))
        res = session.post(session_url, cert=cert)
        res.raise_for_status()
        session_id = res.json()['sessionId']
        session.headers['Authorization'] = f'Handle sessionId={session_id}'

        return session

    def _get_payload(self, target_url: str) -> dict:
        return {
            'values': [{
                'index': 1,
                'type': 'URL',
                'data': {
                    'format': 'string',
                    'value': target_url
                }
            }, {
                'index': 100,
                'type': 'HS_ADMIN',
                'data': {
                    'format': 'admin',
                    'value': {
                        'handle': f'0.NA/{self._options["prefix"]}',
                        'index': 200,
                        'permissions': '011111110011'
                    }
                }
            }]
        }

    @staticmethod
    def str2bool(s: str) -> Union[bool, str]:
        return False if s == 'False' else True if s == 'True' else s
