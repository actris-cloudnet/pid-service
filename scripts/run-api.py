#!/usr/bin/env python3
"""A script for assigning PIDs for data files."""
from os import environ as env

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from pid_service import pid_service


def read_config() -> dict:
    """Read config function."""
    env_config = {
        "PID-SERVICE": {
            "handle_server_url": env["PS_HANDLE_SERVER_URL"],
            "prefix": env["PS_PREFIX"],
            "certificate_only": env["PS_CERTIFICATE_ONLY"],
            "private_key": env["PS_PRIVATE_KEY"],
            "ca_verify": bool(env["PS_CA_VERIFY"]),
        },
        "UVICORN": {
            "host": "0.0.0.0",
            "port": 5800,
            "reload": bool(env["PS_UVICORN_RELOAD"]),
            "debug": bool(env["PS_UVICORN_DEBUG"]),
            "workers": 1,
        },
    }
    return env_config


app = FastAPI()

config = read_config()
pid_gen = pid_service.PidGenerator(config["PID-SERVICE"])


class PidRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """PidRequest class."""

    type: str
    uuid: str


@app.post("/pid/")
def generate_pid(pid_request: PidRequest):
    """Generates PID."""
    pid = pid_gen.generate_pid(pid_request.type, pid_request.uuid)
    return {"pid": pid}


if __name__ == "__main__":
    server_config = config["UVICORN"]
    uvicorn.run(
        "run-api:app",
        host=server_config["host"],
        port=int(server_config["port"]),
        reload=bool(server_config["reload"]),
        debug=bool(server_config["debug"]),
        workers=int(server_config["workers"]),
    )
