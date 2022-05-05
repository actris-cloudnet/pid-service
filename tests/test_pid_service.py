import pytest
import requests
import requests_mock
from fastapi import HTTPException
from pydantic import ValidationError

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
                "http://example.org/file/be8154c1-a6aa-4f44-b953-780b016987b5"
            ),
            json={"responseCode": 1, "handle": "21.T12995/1.be8154c1a6aa4f44"},
        )

        pid_gen = PidGenerator(options, session=session)
        pid = pid_gen.generate_pid(
            PidRequest(
                type="file",
                uuid="be8154c1-a6aa-4f44-b953-780b016987b5",
                url="http://example.org/file/be8154c1-a6aa-4f44-b953-780b016987b5",
            )
        )

        assert pid == "https://hdl.handle.net/21.T12995/1.be8154c1a6aa4f44"

    def test_generate_pid_for_collection(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri(
            "PUT",
            "mock://hdl.svc/api/handles/21.T12995/2.ce8154c1a6aa4f44",
            additional_matcher=validate_request(
                "http://example.org/collection/ce8154c1-a6aa-4f44-b953-780b016987b5"
            ),
            json={"responseCode": 1, "handle": "21.T12995/2.ce8154c1a6aa4f44"},
        )

        pid_gen = PidGenerator(options, session=session)
        pid = pid_gen.generate_pid(
            PidRequest(
                type="collection",
                uuid="ce8154c1-a6aa-4f44-b953-780b016987b5",
                url="http://example.org/collection/ce8154c1-a6aa-4f44-b953-780b016987b5",
            )
        )

        assert pid == "https://hdl.handle.net/21.T12995/2.ce8154c1a6aa4f44"

    def test_generate_pid_for_instrument(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri(
            "PUT",
            "mock://hdl.svc/api/handles/21.T12995/3.8c1680f6b530499a",
            additional_matcher=validate_request(
                "http://example.org/instrument/8c1680f6-b530-499a-b90c-ccb40d47e2bf"
            ),
            json={"responseCode": 1, "handle": "21.T12995/3.8c1680f6b530499a"},
        )

        pid_gen = PidGenerator(options, session=session)
        pid = pid_gen.generate_pid(
            PidRequest(
                type="instrument",
                uuid="8c1680f6-b530-499a-b90c-ccb40d47e2bf",
                url="http://example.org/instrument/8c1680f6-b530-499a-b90c-ccb40d47e2bf",
            )
        )

        assert pid == "https://hdl.handle.net/21.T12995/3.8c1680f6b530499a"

    def test_raises_error_on_failed_request(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri(
            "PUT", "mock://hdl.svc/api/handles/21.T12995/1.ac310789d9844172", status_code=403
        )

        pid_gen = PidGenerator(options, session=session)

        with pytest.raises(HTTPException):
            pid_gen.generate_pid(
                PidRequest(
                    type="file",
                    uuid="ac310789-d984-4172-84b7-84a4a2288af5",
                    url="http://example.org/file/ac310789-d984-4172-84b7-84a4a2288af5",
                )
            )


def validate_request(expected_target_url):
    def is_valid_json(request):
        json = {}
        try:
            json = request.json()
        except ValueError:
            return False
        print(json)
        return json["values"][0]["data"]["value"] == expected_target_url

    return is_valid_json
