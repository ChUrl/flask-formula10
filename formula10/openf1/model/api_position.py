from datetime import datetime
from typing import Any, Callable, Dict


class ApiPosition():
    __type_conversion_map__: Dict[str, Callable[[Any], Any]] = {
        "session_key": int,
        "meeting_key": int,
        "driver_number": int,
        "date": lambda date: datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f"),
        "position": int
    }

    def __init__(self, response: dict[str, str] | None):
        if response is None:
            return

        for key in response:
            if not hasattr(self, key):
                raise Exception(f"Mismatch between response data and {type(self).__name__} (key={key})")

            if not key in self.__type_conversion_map__:
                raise Exception(f"Mismatch between response data and {type(self).__name__}.__type_map__ (key={key})")

            setattr(self, key, self.__type_conversion_map__[key](response[key]))

        print("ApiPosition:", self.__dict__)

    def to_params(self) -> Dict[str, str]:
        params: Dict[str, str] = dict()
        for key in self.__dict__:
            params[str(key)] = str(self.__dict__[key])

        return params

    session_key:   int      = None # type: ignore
    meeting_key:   int      = None # type: ignore
    driver_number: int      = None # type: ignore
    date:          datetime = None # type: ignore
    position:      int      = None # type: ignore