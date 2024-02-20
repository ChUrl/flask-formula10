from typing import Dict, List, cast
from urllib.parse import quote
from flask import redirect
from werkzeug import Response
from database_utils import race_has_result, user_exists
from model import PodiumDrivers, RaceResult, SeasonGuess, TeamWinners, User, db, RaceGuess
from validation_utils import any_is_none, positions_are_contiguous


def find_or_create_race_guess(user_name: str, race_name: str) -> RaceGuess:
    # There can be a single RaceGuess at most, since (user_name, race_name) is the composite primary key
    race_guess: RaceGuess | None = db.session.query(RaceGuess).filter_by(user_name=user_name, race_name=race_name).first()
    if race_guess is not None:
        return race_guess

    # Insert a new RaceGuess
    race_guess = RaceGuess(user_name=user_name, race_name=race_name)
    db.session.add(race_guess)
    db.session.commit()

    # Double check if database insertion worked and obtain any values set by the database
    race_guess = db.session.query(RaceGuess).filter_by(user_name=user_name, race_name=race_name).first()
    if race_guess is None:
        raise Exception("Failed adding RaceGuess to the database")

    return race_guess


def update_race_guess(race_name: str, user_name: str, pxx_select: str | None, dnf_select: str | None) -> Response:
    if any_is_none(pxx_select, dnf_select):
        return redirect(f"/race/{quote(user_name)}")

    pxx_driver_name: str = cast(str, pxx_select)
    dnf_driver_name: str = cast(str, dnf_select)

    # TODO: Date-lock this. Otherwise there is a period of time after the race
    #       but before the result where guesses can still be entered
    # We can't guess for races that are already over
    if race_has_result(race_name):
        return redirect(f"/race/{quote(user_name)}")

    race_guess: RaceGuess = find_or_create_race_guess(user_name, race_name)
    race_guess.pxx_driver_name = pxx_driver_name
    race_guess.dnf_driver_name = dnf_driver_name

    db.session.commit()

    return redirect("/race/Everyone")


def find_or_create_team_winners(user_name: str) -> TeamWinners:
    # There can be a single TeamWinners at most, since user_name is the primary key
    team_winners: TeamWinners | None = db.session.query(TeamWinners).filter_by(user_name=user_name).first()
    if team_winners is not None:
        return team_winners

    team_winners = TeamWinners(user_name=user_name)
    db.session.add(team_winners)
    db.session.commit()

    # Double check if database insertion worked and obtain any values set by the database
    team_winners = db.session.query(TeamWinners).filter_by(user_name=user_name).first()
    if team_winners is None:
        raise Exception("Failed adding TeamWinners to the database")

    return team_winners


def find_or_create_podium_drivers(user_name: str) -> PodiumDrivers:
    # There can be a single PodiumDrivers at most, since user_name is the primary key
    podium_drivers: PodiumDrivers | None = db.session.query(PodiumDrivers).filter_by(user_name=user_name).first()
    if podium_drivers is not None:
        return podium_drivers

    podium_drivers = PodiumDrivers(user_name=user_name)
    db.session.add(podium_drivers)
    db.session.commit()

    # Double check if database insertion worked and obtain any values set by the database
    podium_drivers = db.session.query(PodiumDrivers).filter_by(user_name=user_name).first()
    if podium_drivers is None:
        raise Exception("Failed adding PodiumDrivers to the database")

    return podium_drivers


def find_or_create_season_guess(user_name: str) -> SeasonGuess:
    # There can be a single SeasonGuess at most, since user_name is the primary key
    season_guess: SeasonGuess | None = db.session.query(SeasonGuess).filter_by(user_name=user_name).first()
    if season_guess is not None:
        # There can't be more than a single one, since both also use user_name as primary key
        if db.session.query(TeamWinners).filter_by(user_name=user_name).first() is None:
            raise Exception(f"SeasonGuess for {user_name} is missing associated TeamWinners")
        if db.session.query(PodiumDrivers).filter_by(user_name=user_name).first() is None:
            raise Exception(f"SeasonGuess for {user_name} is missing associated PodiumDrivers")

        return season_guess

    # Insert a new SeasonGuess
    team_winners: TeamWinners = find_or_create_team_winners(user_name)
    podium_drivers: PodiumDrivers = find_or_create_podium_drivers(user_name)

    season_guess = SeasonGuess(user_name=user_name, team_winners_user_name=team_winners.user_name, podium_drivers_user_name=podium_drivers.user_name)
    db.session.add(season_guess)
    db.session.commit()

    # Double check if database insertion worked and obtain any values set by the database
    season_guess = db.session.query(SeasonGuess).filter_by(user_name=user_name).first()
    if season_guess is None:
        raise Exception("Failed adding SeasonGuess to the database")

    return season_guess


def update_season_guess(user_name: str, guesses: List[str | None] | List[str], team_winner_guesses: List[str | None] | List[str], podium_driver_guesses: List[str]) -> Response:
    if any_is_none(*guesses) or any_is_none(*team_winner_guesses):
        return redirect(f"/season/{quote(user_name)}")

    guesses = cast(List[str], guesses)
    team_winner_guesses = cast(List[str], team_winner_guesses)

    season_guess: SeasonGuess = find_or_create_season_guess(user_name)
    season_guess.hot_take = guesses[0]
    season_guess.p2_team_name = guesses[1]
    season_guess.overtake_driver_name = guesses[2]
    season_guess.dnf_driver_name = guesses[3]
    season_guess.gained_driver_name = guesses[4]
    season_guess.lost_driver_name = guesses[5]
    season_guess.team_winners.teamwinner_driver_names = team_winner_guesses  # TODO: Or commit seperately?
    season_guess.podium_drivers.podium_driver_names = podium_driver_guesses  # TODO: Or commit separately?

    db.session.commit()

    return redirect(f"/season/{quote(user_name)}")


def find_or_create_race_result(race_name: str) -> RaceResult:
    # There can be a single RaceResult at most, since race_name is the primary key
    race_result: RaceResult | None = db.session.query(RaceResult).filter_by(race_name=race_name).first()
    if race_result is not None:
        return race_result

    race_result = RaceResult(race_name=race_name)
    db.session.add(race_result)
    db.session.commit()

    # Double check if database insertion worked and obtain any values set by the database
    race_result = db.session.query(RaceResult).filter_by(race_name=race_name).first()
    if race_result is None:
        raise Exception("Failed adding RaceResult to the database")

    return race_result


def update_race_result(race_name: str, pxx_driver_names_list: List[str], dnf_driver_names_list: List[str], excluded_driver_names_list: List[str]) -> Response:
    # Use strings as keys, as these dicts will be serialized to json
    pxx_driver_names: Dict[str, str] = {str(position + 1): driver for position, driver in enumerate(pxx_driver_names_list)}
    dnf_driver_names: Dict[str, str] = {str(position + 1): driver for position, driver in enumerate(pxx_driver_names_list) if driver in dnf_driver_names_list}

    # This one is only used for validation
    excluded_driver_names: Dict[str, str] = {str(position + 1): driver for position, driver in enumerate(pxx_driver_names_list) if driver in excluded_driver_names_list}
    best_excluded_driver_position: int = sorted(list(map(int, list(excluded_driver_names.keys()))))[0] if len(excluded_driver_names) > 0 else 21
    worst_dnf_driver_position: int = sorted(list(map(int, list(dnf_driver_names.keys()))), reverse=True)[0] if len(dnf_driver_names) > 0 else best_excluded_driver_position - 1

    if not positions_are_contiguous(list(dnf_driver_names.keys())):
        return redirect(f"/result/{quote(race_name)}")

    if not positions_are_contiguous(list(excluded_driver_names.keys())):
        return redirect(f"/result/{quote(race_name)}")

    # DNF + exclude is exclusive
    for driver_name in dnf_driver_names_list:
        if driver_name in excluded_driver_names_list:
            return redirect(f"/result/{quote(race_name)}")

    # Excluded drivers occupy the last positions, if any are excluded
    if len(excluded_driver_names_list) > 0 and not "20" in excluded_driver_names:
        return redirect(f"/result/{quote(race_name)}")

    # DNF drivers occupy the positions between finishing and excluded drivers
    if len(dnf_driver_names_list) > 0 and worst_dnf_driver_position + 1 != best_excluded_driver_position:
        print(dnf_driver_names, worst_dnf_driver_position)
        print(excluded_driver_names, best_excluded_driver_position)
        return redirect(f"/result/{quote(race_name)}")


    race_result: RaceResult = find_or_create_race_result(race_name)
    race_result.pxx_driver_names = pxx_driver_names
    race_result.dnf_driver_names = dnf_driver_names if len(dnf_driver_names_list) > 0 else {"20": "NONE"}
    race_result.excluded_driver_names = excluded_driver_names_list

    db.session.commit()

    return redirect(f"/result/{quote(race_name)}")


def update_user(user_name: str | None, add: bool = False, delete: bool = False) -> Response:
    if user_name is None or len(user_name) < 3:
        return redirect("/user")

    if not add and not delete:
        return redirect("/user")

    if add and delete:
        return redirect("/user")

    if add:
        if user_exists(user_name):
            return redirect("/user")

        user: User = User(name=user_name)
        db.session.add(user)
        db.session.commit()

        return redirect("/user")

    if delete:
        if not user_exists(user_name):
            return redirect("/user")

        db.session.query(User).filter_by(name=user_name).delete()
        db.session.commit()

        return redirect("/user")

    raise Exception("update_user received illegal combination of arguments")
