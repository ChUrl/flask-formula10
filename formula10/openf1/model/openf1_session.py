from datetime import datetime, time
from typing import Any, Callable, Dict


class OpenF1Session:
    __type_conversion_map__: Dict[str, Callable[[Any], Any]] = {
        "location": str,
        "country_key": int,
        "country_code": str,
        "country_name": str,
        "circuit_key": int,
        "circuit_short_name": str,
        "session_type": str,
        "session_name": str,
        "date_start": lambda date: datetime.strptime(date, "%Y-%m-%dT%H:%M:%S"),
        "date_end": lambda date: datetime.strptime(date, "%Y-%m-%dT%H:%M:%S"),
        "gmt_offset": lambda time: datetime.strptime(time, "%H:%M:%S").time(),
        "session_key": int,
        "meeting_key": int,
        "year": int
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

        print("OpenF1Session:", self.__dict__)

    def to_params(self) -> Dict[str, str]:
        params: Dict[str, str] = dict()
        for key in self.__dict__:
            params[str(key)] = str(self.__dict__[key])

        return params

    location:           str      = None # type: ignore
    country_key:        int      = None # type: ignore
    country_code:       str      = None # type: ignore
    country_name:       str      = None # type: ignore
    circuit_key:        int      = None # type: ignore
    circuit_short_name: str      = None # type: ignore
    session_type:       str      = None # type: ignore
    session_name:       str      = None # type: ignore
    date_start:         datetime = None # type: ignore
    date_end:           datetime = None # type: ignore
    gmt_offset:         time     = None # type: ignore
    session_key:        int      = None # type: ignore
    meeting_key:        int      = None # type: ignore
    year:               int      = None # type: ignore
