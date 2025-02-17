import pytest
import requests
import requests_mock
from fastapi import HTTPException

from pid_service.config import Settings
from pid_service.pid_service import PidGenerator, PidRequest

options = Settings(
    handle_server_url="mock://hdl.svc/",
    prefix="21.T12995",
    certificate_only=None,
    private_key=None,
    ca_verify=False,
)


@pytest.fixture(scope="session")
def session_adapter():
    adapter = requests_mock.Adapter()
    session = requests.Session()
    session.mount("mock://", adapter)

    sess_response = {
        "sessionId": "fnoskvnqmxlc8ihllcl566sk",
        "nonce": "3sBJALp5eXKWVB9jSDtnGQ==",
        "authenticated": True,
        "id": "309:21.T12995/USER01",
    }
    adapter.register_uri("POST", "mock://hdl.svc/api/sessions", json=sess_response)
    adapter.register_uri("DELETE", "mock://hdl.svc/api/sessions/this")

    return session, adapter


class TestPidService:
    def test_generate_pid_for_file(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri(
            "PUT",
            "mock://hdl.svc/api/handles/21.T12995/1.be8154c1a6aa4f44",
            additional_matcher=validate_request(
                [
                    (
                        "URL",
                        "http://example.org/file/be8154c1-a6aa-4f44-b953-780b016987b5",
                    )
                ]
            ),
            json={"responseCode": 1, "handle": "21.T12995/1.be8154c1a6aa4f44"},
        )

        request = {
            "type": "file",
            "uuid": "be8154c1-a6aa-4f44-b953-780b016987b5",
            "url": "http://example.org/file/be8154c1-a6aa-4f44-b953-780b016987b5",
        }
        pid_gen = PidGenerator(options, session=session)
        pid = pid_gen.generate_pid(PidRequest(**request))

        assert pid == "https://hdl.handle.net/21.T12995/1.be8154c1a6aa4f44"

    def test_generate_pid_for_collection(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri(
            "PUT",
            "mock://hdl.svc/api/handles/21.T12995/2.ce8154c1a6aa4f44",
            additional_matcher=validate_request(
                [
                    (
                        "URL",
                        "http://example.org/collection/ce8154c1-a6aa-4f44-b953-780b016987b5",
                    )
                ]
            ),
            json={"responseCode": 1, "handle": "21.T12995/2.ce8154c1a6aa4f44"},
        )

        request = {
            "type": "collection",
            "uuid": "ce8154c1-a6aa-4f44-b953-780b016987b5",
            "url": "http://example.org/collection/ce8154c1-a6aa-4f44-b953-780b016987b5",
        }
        pid_gen = PidGenerator(options, session=session)
        pid = pid_gen.generate_pid(PidRequest(**request))

        assert pid == "https://hdl.handle.net/21.T12995/2.ce8154c1a6aa4f44"

    def test_generate_pid_for_instrument(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri(
            "PUT",
            "mock://hdl.svc/api/handles/21.T12995/3.8c1680f6b530499a",
            additional_matcher=validate_request(
                [
                    (
                        "URL",
                        "http://example.org/instrument/8c1680f6-b530-499a-b90c-ccb40d47e2bf",
                    )
                ]
            ),
            json={"responseCode": 1, "handle": "21.T12995/3.8c1680f6b530499a"},
        )

        request = {
            "type": "instrument",
            "uuid": "8c1680f6-b530-499a-b90c-ccb40d47e2bf",
            "url": "http://example.org/instrument/8c1680f6-b530-499a-b90c-ccb40d47e2bf",
        }
        pid_gen = PidGenerator(options, session=session)
        pid = pid_gen.generate_pid(PidRequest(**request))

        assert pid == "https://hdl.handle.net/21.T12995/3.8c1680f6b530499a"

    def test_generate_pid_with_data(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri(
            "PUT",
            "mock://hdl.svc/api/handles/21.T12995/3.8c1680f6b530499a",
            additional_matcher=validate_request(
                [
                    (
                        "URL",
                        "http://example.org/instrument/8c1680f6-b530-499a-b90c-ccb40d47e2bf",
                    ),
                    ("msg", "hello world"),
                ]
            ),
            json={"responseCode": 1, "handle": "21.T12995/3.8c1680f6b530499a"},
        )

        request = {
            "type": "instrument",
            "uuid": "8c1680f6-b530-499a-b90c-ccb40d47e2bf",
            "url": "http://example.org/instrument/8c1680f6-b530-499a-b90c-ccb40d47e2bf",
            "data": [{"type": "msg", "value": "hello world"}],
        }
        pid_gen = PidGenerator(options, session=session)
        pid = pid_gen.generate_pid(PidRequest(**request))

        assert pid == "https://hdl.handle.net/21.T12995/3.8c1680f6b530499a"

    def test_raises_error_on_failed_request(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri(
            "PUT",
            "mock://hdl.svc/api/handles/21.T12995/1.ac310789d9844172",
            status_code=403,
        )

        request = {
            "type": "file",
            "uuid": "ac310789-d984-4172-84b7-84a4a2288af5",
            "url": "http://example.org/file/ac310789-d984-4172-84b7-84a4a2288af5",
        }

        pid_gen = PidGenerator(options, session=session)

        with pytest.raises(HTTPException):
            pid_gen.generate_pid(PidRequest(**request))


def validate_request(expected_values):
    def is_valid_json(request):
        data = {}
        try:
            data = request.json()
        except ValueError:
            return False
        for (expected_type, expected_value), item in zip(
            expected_values, data["values"]
        ):
            if item["type"] != expected_type or item["data"]["value"] != expected_value:
                return False
        return True

    return is_valid_json
