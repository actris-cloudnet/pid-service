#!/usr/bin/env python3
"""A script for assigning PIDs for data files."""
import argparse
import configparser
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import pid_service


def read_config(config_dir):
    config_path = f'{config_dir}/main.ini'
    config = configparser.ConfigParser()
    config.read_file(open(config_path, 'r'))
    return config


app = FastAPI()

parser = argparse.ArgumentParser(description='Run API for minting PIDs')
parser.add_argument('--config-dir', type=str, metavar='/FOO/BAR',
                    help='Path to directory containing config files. Default: ./config.',
                    default='./config')
ARGS = parser.parse_args()

config = read_config(ARGS.config_dir)
pid_gen = pid_service.PidGenerator(config['PID-SERVICE'])


class PidRequest(BaseModel):
    type: str
    uuid: str


@app.post("/pid/")
def generate_pid(pid_request: PidRequest):
    pid = pid_gen.generate_pid(pid_request.type, pid_request.uuid)
    return {"pid": pid}


if __name__ == "__main__":
    server_config = config['UVICORN']
    uvicorn.run("run-api:app",
                host=server_config['host'],
                port=int(server_config['port']),
                reload=bool(server_config['reload']),
                debug=bool(server_config['debug']),
                workers=int(server_config['workers']))
