from typing import Any, Callable, Dict


class ApiDriver:
    __type_conversion_map__: Dict[str, Callable[[Any], Any]] = {
        "session_key": int,
        "meeting_key": int,
        "full_name": str,
        "first_name": str,
        "last_name": str,
        "name_acronym": str,
        "broadcast_name": str,
        "country_code": str,
        "headshot_url": str,
        "driver_number": int,
        "team_colour": str,
        "team_name": str
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

        print("ApiDriver:", self.__dict__)

    def to_params(self) -> Dict[str, str]:
        params: Dict[str, str] = dict()
        for key in self.__dict__:
            params[str(key)] = str(self.__dict__[key])

        return params

    # Set all members to None so hasattr works above

    session_key:    int = None # type: ignore
    meeting_key:    int = None # type: ignore
    full_name:      str = None # type: ignore
    first_name:     str = None # type: ignore
    last_name:      str = None # type: ignore
    name_acronym:   str = None # type: ignore
    broadcast_name: str = None # type: ignore
    country_code:   str = None # type: ignore
    headshot_url:   str = None # type: ignore
    driver_number:  int = None # type: ignore
    team_colour:    str = None # type: ignore
    team_name:      str = None # type: ignore