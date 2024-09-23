# https://docs.fastf1.dev/events.html#event-formats
from typing import Optional

from fastf1.core import Lap, DriverResult
from fastf1.events import Event
from pandas import Timestamp, Timedelta
from typing_extensions import deprecated

FASTF1_SESSIONTYPE_NORMAL: str = "conventional"
FASTF1_SESSIONTYPE_SPRINT: str = "sprint_qualifying"

FASTF1_SPRINT_QUALIFYING_SESSION: int = 2
FASTF1_SPRINT_SESSION: int = 3
FASTF1_QUALIFYING_SESSION: int = 4
FASTF1_RACE_SESSION: int = 5

class EventDataHelper:
    """
    Helper class that provides easy access to EventDataFrame columns.
    """

    def __init__(self, event: Event):
        self.__event = event

    __event: Event

    @property
    def round_number(self) -> int:
        return self.__event["RoundNumber"]

    @property
    def country(self) -> str:
        return self.__event["Country"]

    @property
    def location(self) -> str:
        return self.__event["Location"]

    @property
    def official_event_name(self) -> str:
        """
        Get the event name including sponsor names etc.
        """
        return self.__event["OfficialEventName"]

    @property
    def event_name(self) -> str:
        return self.__event["EventName"]

    @property
    def event_date(self) -> Timestamp:
        return self.__event["EventDate"]

    @property
    def event_format(self) -> str:
        """
        Get the event format.
        @return: Either conventional, sprint, sprint_shootout, sprint_qualifying or testing (sprint_qualifying is the 2024 sprint format).
        """
        return self.__event["EventFormat"]

    def session(self, session_number: int) -> str:
        """
        Get the format of a session belonging to this event.
        @param session_number: Either 1, 2, 3, 4 or 5
        @return: Either Pactice 1, Practice 2, Practice 3, Qualifying, Sprint, Sprint Shootout or Race
        """
        return self.__event[f"Session{session_number}"]

    def session_date(self, session_number: int) -> Timestamp:
        """
        Get the date of a session belonging to this event.
        @param session_number: Either 1, 2, 3, 4 or 5
        """
        return self.__event[f"Session{session_number}Date"]

    def session_date_utc(self, session_number: int) -> Timestamp:
        """
        Get the date a session belonging to this event in coordinated universal time.
        @param session_number: Either 1, 2, 3, 4 or 5
        """
        return self.__event[f"Session{session_number}DateUtc"]

    @property
    def f1_api_support(self) -> bool:
        return self.__event["F1ApiSupport"]


class LapDataHelper:
    """
    Helper class that provides easy access to Lap DataFrame columns.
    """

    def __init__(self, lap: Lap):
        self.__lap = lap

    __lap: Lap

    @property
    def time(self) -> Timedelta:
        return self.__lap["Time"]

    @property
    def driver(self) -> str:
        return self.__lap["Driver"]

    @property
    def driver_number(self) -> str:
        return self.__lap["DriverNumber"]

    @property
    def lap_time(self) -> Timedelta:
        return self.__lap["LapTime"]

    @property
    def lap_number(self) -> int:
        return self.__lap["LapNumber"]

    @property
    def stint(self) -> int:
        return self.__lap["Stint"]

    @property
    def pit_out_time(self) -> Timedelta:
        """
        Get the session time when the car left the pit.
        """
        return self.__lap["PitOutTime"]

    @property
    def pit_in_time(self) -> Timedelta:
        """
        Get the session time when the car entered the pit.
        """
        return self.__lap["PitInTime"]

    def sector_time(self, sector_number: int) -> Timedelta:
        """
        Get the sector times set in this lap.
        @param sector_number: Either 1, 2 or 3.
        """
        return self.__lap[f"Sector{sector_number}Time"]

    def sector_session_time(self, sector_number: int) -> Timedelta:
        """
        Get the session time when the sector time was set.
        @param sector_number: Either 1, 2 or 3.
        """
        return self.__lap[f"Sector{sector_number}SessionTime"]

    def speed(self, speedtrap: str) -> float:
        """
        Get car speed at measure point in this lap.
        @param speedtrap: Either I1, I2, FL or ST (sector 1, sector 2, finish line or longest straight)
        """
        return self.__lap[f"Speed{speedtrap}"]

    @property
    def is_personal_best(self) -> bool:
        return self.__lap["IsPersonalBest"]

    @property
    def compound(self) -> str:
        """
        Get compound used in this lap.
        @return: Either SOFT, MEDIUM, HARD, INTERMEDIATE or WET
        """
        return self.__lap["Compound"]

    @property
    def tyre_life(self) -> int:
        """
        Get laps driven on the current tyre (includes laps from other sessions).
        """
        return self.__lap["TyreLife"]

    @property
    def fresh_tyre(self) -> bool:
        return self.__lap["FreshTyre"]

    @property
    def team(self) -> str:
        return self.__lap["Team"]

    @property
    def lap_start_time(self) -> Timedelta:
        return self.__lap["LapStartTime"]

    @property
    def lap_start_date(self) -> Timestamp:
        return self.__lap["LapStartDate"]

    @property
    def track_status(self) -> str:
        """
        Get the track status in this lap.
        @return: Either 1, 2, 3, 4, 5, 6 or 7 (clear, yellow flag, ?, SC, red flag, VSC and VSC ending).
        """
        return self.__lap["TrackStatus"]

    @property
    def position(self) -> int:
        return self.__lap["Position"]

    @property
    def deleted(self) -> Optional[bool]:
        """
        Determine if the lap was deleted (only available if race control messages are loaded).
        """
        return self.__lap["Deleted"]

    @property
    def deleted_reason(self) -> str:
        return self.__lap["DeletedReason"]

    @property
    def fast_f1_generated(self) -> bool:
        """
        Determine if the lap was generated by FastF1 (information is interpolated).
        """
        return self.__lap["FastF1Generated"]

    @property
    def is_accurate(self) -> bool:
        """
        Determine if lap start and end match with other laps before and after.
        """
        return self.__lap["IsAccurate"]


class DriverResultDataHelper:
    """
    Helper class that provides easy access to DriverResult DataFrame columns.
    """

    def __init__(self, driver_result: DriverResult):
        self.__driver_result = driver_result

    __driver_result: DriverResult

    @property
    def driver_number(self) -> str:
        return self.__driver_result["DriverNumber"]

    @property
    def broadcast_name(self) -> str:
        """
        Get this driver's broadcast name.
        @return: For example P GASLY
        """
        return self.__driver_result["BroadcastName"]

    @property
    def full_name(self) -> str:
        return self.__driver_result["FullName"]

    @property
    def abbreviation(self) -> str:
        return self.__driver_result["Abbreviation"]

    # @property
    # def driver_id(self) -> str:
    #     """
    #     Get the driverId used by the Ergast API.
    #     """
    #     return self.__driver_result["DriverID"]
    
    @property
    def team_name(self) -> str:
        return self.__driver_result["TeamName"]

    @property
    def team_color(self) -> str:
        return self.__driver_result["TeamColor"]

    # @property
    # def team_id(self) -> str:
    #     """
    #     Get the constructorId used by the Ergast API.
    #     @return:
    #     """
    #     return self.__driver_result["TeamID"]

    @property
    def first_name(self) -> str:
        return self.__driver_result["FirstName"]

    @property
    def last_name(self) -> str:
        return self.__driver_result["LastName"]

    @property
    def headshot_url(self) -> str:
        return self.__driver_result["HeadshotUrl"]

    @property
    def country_code(self) -> str:
        """
        Get a driver's three-letter country code.
        @return: For example FRA
        """
        return self.__driver_result["CountryCode"]

    @property
    def position(self) -> int:
        return self.__driver_result["Position"]

    @property
    def classified_position(self) -> str:
        """
        Get the classification result for this driver.
        @return: Either R, D, E, W, F, N (retired, disqualified, excluded, withdrawn, failed to qualify and not classified)
        """
        return self.__driver_result["ClassifiedPosition"]

    @property
    def grid_position(self) -> int:
        """
        Get the driver's starting position.
        """
        return self.__driver_result["GridPosition"]

    def qualifying_time(self, qualifying_number: int) -> Timedelta:
        """
        Get the driver's best qualifying time.
        @param qualifying_number: Either 1, 2 or 3 (for Q1, Q2 and Q3)
        """
        return self.__driver_result[f"Q{qualifying_number}"]

    @property
    def time(self) -> Timedelta:
        """
        Get the driver's total race time.
        """
        return self.__driver_result["Time"]

    @property
    def status(self) -> str:
        """
        Get the driver's finishing status.
        @return: For example Finished, +1 Lap, Crash, Gearbox...
        """
        return self.__driver_result["Status"]

    @property
    def points(self) -> int:
        return self.__driver_result["Points"]