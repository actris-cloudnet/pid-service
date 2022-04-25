import pytest
import requests
import requests_mock
from fastapi import HTTPException

from pid_service import pid_service

options = dict(
    handle_server_url="mock://test/",
    prefix="21.T12995",
    certificate_only=None,
    private_key=None,
    ca_verify="False",
)

handle_response = {"responseCode": 1, "handle": "21.T12995/1.be8154c1a6aa4f44"}


@pytest.fixture(scope="session")
def session_adapter(tmpdir_factory):
    adapter = requests_mock.Adapter()
    session = requests.Session()
    session.mount("mock://", adapter)

    sess_response = {
        "sessionId": "fnoskvnqmxlc8ihllcl566sk",
        "nonce": "3sBJALp5eXKWVB9jSDtnGQ==",
        "authenticated": True,
        "id": "309:21.T12995/USER01",
    }
    adapter.register_uri("POST", "mock://test/api/sessions", json=sess_response)
    adapter.register_uri("DELETE", "mock://test/api/sessions/this")

    return session, adapter


class TestPidService:
    def test_generate_pid_for_file(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri(
            "PUT",
            "mock://test/api/handles/21.T12995/1.be8154c1a6aa4f44",
            additional_matcher=validate_request(
                "https://cloudnet.fmi.fi/file/be815-4c1a6aa4f4-4b953780b016-987b5"
            ),
            json=handle_response,
        )

        pid_gen = pid_service.PidGenerator(options, session=session)
        pid = pid_gen.generate_pid("file", "be815-4c1a6aa4f4-4b953780b016-987b5")

        assert pid == "https://hdl.handle.net/21.T12995/1.be8154c1a6aa4f44"

    def test_generate_pid_for_collection(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri(
            "PUT",
            "mock://test/api/handles/21.T12995/2.ce8154c1a6aa4f44",
            additional_matcher=validate_request(
                "https://cloudnet.fmi.fi/collection/ce8154c1a6aa4f44b953780b016987b5"
            ),
            json=handle_response,
        )

        pid_gen = pid_service.PidGenerator(options, session=session)
        pid = pid_gen.generate_pid("collection", "ce8154c1a6aa4f44b953780b016987b5")

        assert pid == "https://hdl.handle.net/21.T12995/1.be8154c1a6aa4f44"

    def test_generate_pid_for_instrument(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri(
            "PUT",
            "mock://test/api/handles/21.T12995/3.ce8154c1a6aa4f44",
            additional_matcher=validate_request(
                "https://instrumentdb.out.ocp.fmi.fi/instrument/ce8154c1a6aa4f44b953780b016987b5"
            ),
            json=handle_response,
        )

        pid_gen = pid_service.PidGenerator(options, session=session)
        pid = pid_gen.generate_pid("instrument", "ce8154c1a6aa4f44b953780b016987b5")
        assert pid == "https://hdl.handle.net/21.T12995/1.be8154c1a6aa4f44"

    def test_raises_error_on_failed_request(self, session_adapter):
        session, adapter = session_adapter
        adapter.register_uri("PUT", "mock://test/api/handles/21.T12995/1.fail", status_code=403)

        pid_gen = pid_service.PidGenerator(options, session=session)

        with pytest.raises(HTTPException):
            pid_gen.generate_pid("file", "fail")

    def test_raises_error_on_unknown_type(self, session_adapter):
        session, adapter = session_adapter

        pid_gen = pid_service.PidGenerator(options, session=session)

        with pytest.raises(HTTPException):
            pid_gen.generate_pid("wtf", "fail")

    def test_str2bool(self, session_adapter):
        session, adapter = session_adapter
        pid_gen = pid_service.PidGenerator(options, session=session)
        assert pid_gen.str2bool("True") is True
        assert pid_gen.str2bool("False") is False
        assert pid_gen.str2bool("kissa") == "kissa"


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
