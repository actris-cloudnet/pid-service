from fastapi import FastAPI

from .config import Settings
from .pid_service import PidGenerator, PidRequest

settings = Settings()
pid_gen = PidGenerator(settings)
app = FastAPI()


@app.post("/pid/")
def generate_pid(pid_request: PidRequest):
    pid = pid_gen.generate_pid(pid_request)
    return {"pid": pid}
