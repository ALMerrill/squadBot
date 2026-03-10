import os
import time
from enum import Enum
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

AMP_BASE_URL = os.getenv("AMP_BASE_URL", "").rstrip("/")
AMP_USERNAME = os.getenv("AMP_USERNAME", "")
AMP_PASSWORD = os.getenv("AMP_PASSWORD", "")
ARK_INSTANCE_ID = os.getenv("ARK_INSTANCE_ID", "")
ARK_SAVE_DELAY_SECONDS = int(os.getenv("ARK_SAVE_DELAY_SECONDS", "15"))
ARK_CONNECT_URL = os.getenv("ARK_CONNECT_URL", "")

_session_id: Optional[str] = None


class AmpServerState(Enum):
    STOPPED = 0
    RUNNING = 1
    STARTING = 2
    STOPPING = 3
    UNKNOWN = -1


def _require_config():
    missing = []
    if not AMP_BASE_URL:
        missing.append("AMP_BASE_URL")
    if not AMP_USERNAME:
        missing.append("AMP_USERNAME")
    if not AMP_PASSWORD:
        missing.append("AMP_PASSWORD")
    if not ARK_INSTANCE_ID:
        missing.append("ARK_INSTANCE_ID")
    if missing:
        raise ValueError(f"Missing required env vars: {', '.join(missing)}")


def _login() -> str:
    _require_config()
    url = f"{AMP_BASE_URL}/API/Core/Login"
    payload = {
        "username": AMP_USERNAME,
        "password": AMP_PASSWORD,
        "token": "",
        "rememberMe": False,
    }
    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()
    data = response.json()
    session_id = data.get("result", {}).get("sessionID")
    if not session_id:
        raise RuntimeError("AMP login failed: missing sessionID in response")
    return session_id


def _request(path: str, json: Optional[dict] = None) -> dict:
    global _session_id
    if _session_id is None:
        _session_id = _login()

    url = f"{AMP_BASE_URL}{path}"
    headers = {"X-AMP-SessionID": _session_id}
    response = requests.post(url, json=json, headers=headers, timeout=30)

    if response.status_code in (401, 403):
        _session_id = _login()
        headers = {"X-AMP-SessionID": _session_id}
        response = requests.post(url, json=json, headers=headers, timeout=30)

    response.raise_for_status()
    return response.json() if response.content else {}


def get_status() -> AmpServerState:
    data = _request(f"/API/ADSModule/Servers/{ARK_INSTANCE_ID}/GetStatus")
    state_value = data.get("State")
    if state_value in (0, 1, 2, 3):
        return AmpServerState(state_value)
    return AmpServerState.UNKNOWN


def start_server() -> bool:
    data = _request(f"/API/ADSModule/Servers/{ARK_INSTANCE_ID}/Start")
    return bool(data) if isinstance(data, dict) else True


def restart_server() -> bool:
    data = _request(f"/API/ADSModule/Servers/{ARK_INSTANCE_ID}/Restart")
    return bool(data) if isinstance(data, dict) else True


def update_server() -> bool:
    data = _request(f"/API/ADSModule/Servers/{ARK_INSTANCE_ID}/Update")
    return bool(data) if isinstance(data, dict) else True


def stop_server() -> bool:
    data = _request(f"/API/ADSModule/Servers/{ARK_INSTANCE_ID}/Stop")
    return bool(data) if isinstance(data, dict) else True


def send_console_command(command: str) -> bool:
    payload = {"command": command}
    data = _request(f"/API/ADSModule/Servers/{ARK_INSTANCE_ID}/Console/Send", json=payload)
    return bool(data) if isinstance(data, dict) else True


def graceful_stop_with_save() -> None:
    send_console_command("saveworld")
    time.sleep(ARK_SAVE_DELAY_SECONDS)
    stop_server()
