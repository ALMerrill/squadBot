import os
import time
from enum import Enum
from typing import Optional, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

AMP_BASE_URL = os.getenv("AMP_BASE_URL", "").rstrip("/")
AMP_USERNAME = os.getenv("AMP_USERNAME", "")
AMP_PASSWORD = os.getenv("AMP_PASSWORD", "")
AMP_API_ACCEPT = "application/vnd.cubecoders-ampapi"
AMP_API_USE_BEARER = True

ARK_INSTANCE_ID = os.getenv("ARK_INSTANCE_ID", "")
ARK_INSTANCE_NAME = os.getenv("ARK_INSTANCE_NAME", "")
ARK_SAVE_DELAY_SECONDS = int(os.getenv("ARK_SAVE_DELAY_SECONDS", "15"))
ARK_CONNECT_URL = os.getenv("ARK_CONNECT_URL", "")

AMP_DEBUG = os.getenv("AMP_DEBUG", "false").lower() == "true"

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
    if not ARK_INSTANCE_NAME:
        missing.append("ARK_INSTANCE_NAME")
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
    headers = {"Accept": AMP_API_ACCEPT}
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    session_id = (
        data.get("sessionID")
        or data.get("sessionId")
        or data.get("SessionID")
        or data.get("SessionId")
    )
    if not session_id and isinstance(data.get("result"), dict):
        session_id = (
            data["result"].get("sessionID")
            or data["result"].get("sessionId")
            or data["result"].get("SessionID")
            or data["result"].get("SessionId")
        )
    if not session_id:
        raise RuntimeError("AMP login failed: missing sessionID")
    return session_id


def _api_headers(session_id: str) -> dict:
    headers = {"Accept": AMP_API_ACCEPT, "Content-Type": "application/json"}
    if AMP_API_USE_BEARER:
        headers["Authorization"] = f"Bearer {session_id}"
    else:
        headers["X-AMP-SessionID"] = session_id
    return headers


def _request(path: str, payload: Optional[dict] = None) -> dict:
    global _session_id
    if _session_id is None:
        _session_id = _login()

    url = f"{AMP_BASE_URL}{path}"
    headers = _api_headers(_session_id)
    body = payload.copy() if isinstance(payload, dict) else {}
    body.setdefault("SESSIONID", _session_id)

    response = requests.post(url, json=body, headers=headers, timeout=30)
    if response.status_code in (401, 403):
        _session_id = _login()
        headers = _api_headers(_session_id)
        body["SESSIONID"] = _session_id
        response = requests.post(url, json=body, headers=headers, timeout=30)

    content_type = response.headers.get("Content-Type", "")
    if "text/html" in content_type:
        raise RuntimeError("AMP API returned HTML. Check base URL and credentials.")

    if response.status_code >= 400:
        raise RuntimeError(f"AMP API error {response.status_code}: {response.text}")

    response.raise_for_status()
    if not response.content:
        return {}
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


def _api_call(module: str, method: str, parameters: Optional[dict] = None) -> dict:
    params = parameters or {}
    payload = {"parameters": params, **params}
    return _request(f"/API/{module}/{method}", payload)


def _action_ok(data: object) -> bool:
    if not isinstance(data, dict):
        return True
    if "Title" in data and "Message" in data:
        return False
    if "success" in data:
        return bool(data.get("success"))
    result = data.get("result")
    if isinstance(result, dict) and "success" in result:
        return bool(result.get("success"))
    if "Status" in data and isinstance(data.get("Status"), bool):
        return bool(data.get("Status"))
    return True


def _action_reason(data: object) -> str:
    if not isinstance(data, dict):
        return ""
    if "Title" in data or "Message" in data:
        title = data.get("Title") or ""
        message = data.get("Message") or ""
        return f"{title}: {message}".strip(": ")
    for key in ["resultReason", "message", "Message", "error", "Error", "Reason"]:
        if key in data and data[key]:
            return str(data[key])
    result = data.get("result")
    if isinstance(result, dict):
        for key in ["resultReason", "message", "Message", "error", "Error", "Reason"]:
            if key in result and result[key]:
                return str(result[key])
    return ""


def get_instance_info() -> dict:
    if not ARK_INSTANCE_ID:
        raise RuntimeError("ARK_INSTANCE_ID is required for GetInstance.")
    return _api_call("ADSModule", "GetInstance", {"InstanceId": ARK_INSTANCE_ID})


def extract_instance_status(info: dict) -> Optional[str]:
    if not isinstance(info, dict):
        return None
    for key in [
        "Status",
        "StatusText",
        "StateText",
        "State",
        "CurrentState",
        "DeploymentState",
        "UpdateStatus",
        "InstallState",
        "StartupState",
    ]:
        val = info.get(key)
        if isinstance(val, str) and val:
            return val
    return None


def get_status_raw() -> dict:
    return _api_call("ADSModule", "GetInstanceStatuses")


def get_status_info() -> Tuple[AmpServerState, str]:
    data = get_status_raw()
    if isinstance(data, dict) and "result" in data:
        data = data["result"]

    state_value = None
    status_text = ""
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("InstanceName") or item.get("Name")
            iid = item.get("InstanceID") or item.get("InstanceId")
            if name == ARK_INSTANCE_NAME or iid == ARK_INSTANCE_ID:
                state_value = item.get("State") or item.get("StateCode")
                raw_status = item.get("Status")
                if isinstance(raw_status, str):
                    status_text = raw_status
                if state_value is None and isinstance(raw_status, int):
                    state_value = raw_status
                if state_value is None and "Running" in item:
                    return (AmpServerState.RUNNING if item.get("Running") else AmpServerState.STOPPED), status_text
                break
    elif isinstance(data, dict):
        state_value = data.get("State") or data.get("StateCode")
        raw_status = data.get("Status")
        if isinstance(raw_status, str):
            status_text = raw_status
        if state_value is None and isinstance(raw_status, int):
            state_value = raw_status
        if state_value is None and "Running" in data:
            return (AmpServerState.RUNNING if data.get("Running") else AmpServerState.STOPPED), status_text

    if state_value in (0, 1, 2, 3):
        return AmpServerState(state_value), status_text
    return AmpServerState.UNKNOWN, status_text


def get_status() -> AmpServerState:
    return get_status_info()[0]


def start_server() -> dict:
    return _api_call("ADSModule", "StartInstance", {"InstanceName": ARK_INSTANCE_NAME})


def restart_server() -> dict:
    return _api_call("ADSModule", "RestartInstance", {"InstanceName": ARK_INSTANCE_NAME})


def update_server() -> dict:
    return _api_call("ADSModule", "UpgradeInstance", {"InstanceName": ARK_INSTANCE_NAME})


def stop_server() -> dict:
    return _api_call("ADSModule", "StopInstance", {"InstanceName": ARK_INSTANCE_NAME})


def send_console_command(command: str) -> dict:
    return _api_call("Core", "SendConsoleMessage", {"message": command})


def graceful_stop_with_save() -> dict:
    save_result = send_console_command("saveworld")
    time.sleep(ARK_SAVE_DELAY_SECONDS)
    stop_result = stop_server()
    return {"save": save_result, "stop": stop_result}

