from datetime import datetime
import json
from typing import Any, Callable, Dict, List, cast
from requests import Response, get

from formula10.openf1.model.api_driver import ApiDriver
from formula10.openf1.model.api_position import ApiPosition
from formula10.openf1.model.api_session import ApiSession
from formula10.openf1.openf1_definitions import OPENF1_DRIVER_ENDPOINT, OPENF1_POSITION_ENDPOINT, OPENF1_SESSION_ENDPOINT, OPENF1_SESSION_NAME_RACE, OPENF1_SESSION_NAME_SPRINT, OPENF1_SESSION_TYPE_RACE

def request_helper(endpoint: str, params: Dict[str, str]) -> List[Dict[str, str]]:
    response: Response = get(endpoint, params=params)
    if not response.ok:
        raise Exception(f"OpenF1 request to {response.request.url} failed")

    obj: Any = json.loads(response.text)
    if isinstance(obj, List):
        return cast(List[Dict[str, str]], obj)
    elif isinstance(obj, Dict):
        return [cast(Dict[str, str], obj)]
    else:
        # @todo Fail gracefully
        raise Exception(f"Unexpected OpenF1 response from {response.request.url}: {obj}")


def fetch_openf1_latest_session(session_name: str) -> ApiSession:
    # ApiSession object only supports integer session_keys
    response: List[Dict[str, str]] = request_helper(OPENF1_SESSION_ENDPOINT, {
        "session_key": "latest",
        "session_type": OPENF1_SESSION_TYPE_RACE,
        "session_name": session_name
    })

    return ApiSession(response[0])


def fetch_openf1_latest_race_session_key() -> int:
    return fetch_openf1_latest_session(OPENF1_SESSION_NAME_RACE).session_key


def fetch_openf1_latest_sprint_session_key() -> int:
    return fetch_openf1_latest_session(OPENF1_SESSION_NAME_SPRINT).session_key


def fetch_openf1_session(session_name: str, country_code: str) -> ApiSession:
    _session: ApiSession = ApiSession(None)
    _session.session_type = OPENF1_SESSION_TYPE_RACE  # includes races + sprints
    _session.year = 2024
    _session.country_code = country_code
    _session.session_name = session_name

    response: List[Dict[str, str]] = request_helper(OPENF1_SESSION_ENDPOINT, _session.to_params())

    return ApiSession(response[0])


def fetch_openf1_driver(session_key: int, name_acronym: str) -> ApiDriver:
    _driver: ApiDriver = ApiDriver(None)
    _driver.name_acronym = name_acronym
    _driver.session_key = session_key

    response: List[Dict[str, str]] = request_helper(OPENF1_DRIVER_ENDPOINT, _driver.to_params())

    return ApiDriver(response[0])


def fetch_openf1_position(session_key: int, position: int):
    _position: ApiPosition = ApiPosition(None)
    _position.session_key = session_key
    _position.position = position

    response: List[Dict[str, str]] = request_helper(OPENF1_POSITION_ENDPOINT, _position.to_params())

    # Find the last driver that was on this position at last
    predicate: Callable[[Dict[str, str]], datetime] = lambda position: datetime.strptime(position["date"], "%Y-%m-%dT%H:%M:%S.%f")
    return ApiPosition(max(response, key=predicate))