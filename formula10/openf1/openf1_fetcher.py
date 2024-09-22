from datetime import datetime
import json
from typing import Any, Callable, Dict, List, cast
from requests import Response, get

from formula10.openf1.model.openf1_driver import OpenF1Driver
from formula10.openf1.model.openf1_position import OpenF1Position
from formula10.openf1.model.openf1_session import OpenF1Session
from formula10.openf1.openf1_definitions import OPENF1_DRIVER_ENDPOINT, OPENF1_POSITION_ENDPOINT, OPENF1_SESSION_ENDPOINT, OPENF1_SESSION_NAME_RACE, OPENF1_SESSION_NAME_SPRINT, OPENF1_SESSION_TYPE_RACE

def openf1_request_helper(endpoint: str, params: Dict[str, str]) -> List[Dict[str, str]]:
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


def openf1_fetch_latest_session(session_name: str) -> OpenF1Session:
    # ApiSession object only supports integer session_keys
    response: List[Dict[str, str]] = openf1_request_helper(OPENF1_SESSION_ENDPOINT, {
        "session_key": "latest",
        "session_type": OPENF1_SESSION_TYPE_RACE,
        "session_name": session_name
    })

    return OpenF1Session(response[0])


def openf1_fetch_latest_race_session_key() -> int:
    return openf1_fetch_latest_session(OPENF1_SESSION_NAME_RACE).session_key


def openf1_fetch_latest_sprint_session_key() -> int:
    return openf1_fetch_latest_session(OPENF1_SESSION_NAME_SPRINT).session_key


def openf1_fetch_session(session_name: str, country_code: str) -> OpenF1Session:
    _session: OpenF1Session = OpenF1Session(None)
    _session.session_type = OPENF1_SESSION_TYPE_RACE  # includes races + sprints
    _session.year = 2024
    _session.country_code = country_code
    _session.session_name = session_name

    response: List[Dict[str, str]] = openf1_request_helper(OPENF1_SESSION_ENDPOINT, _session.to_params())

    return OpenF1Session(response[0])


def openf1_fetch_driver(session_key: int, name_acronym: str) -> OpenF1Driver:
    _driver: OpenF1Driver = OpenF1Driver(None)
    _driver.name_acronym = name_acronym
    _driver.session_key = session_key

    response: List[Dict[str, str]] = openf1_request_helper(OPENF1_DRIVER_ENDPOINT, _driver.to_params())

    return OpenF1Driver(response[0])


def openf1_fetch_position(session_key: int, position: int):
    _position: OpenF1Position = OpenF1Position(None)
    _position.session_key = session_key
    _position.position = position

    response: List[Dict[str, str]] = openf1_request_helper(OPENF1_POSITION_ENDPOINT, _position.to_params())

    # Find the last driver that was on this position at last
    predicate: Callable[[Dict[str, str]], datetime] = lambda position: datetime.strptime(position["date"], "%Y-%m-%dT%H:%M:%S.%f")
    return OpenF1Position(max(response, key=predicate))