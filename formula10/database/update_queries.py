import json
from typing import Dict, List, cast
from urllib.parse import quote
from flask import redirect
from werkzeug import Response
from formula10.controller.error_controller import error_redirect

from formula10.database.common_queries import race_has_result, user_exists_and_disabled, user_exists_and_enabled
from formula10.database.model.db_race_guess import DbRaceGuess
from formula10.database.model.db_race_result import DbRaceResult
from formula10.database.model.db_season_guess import DbSeasonGuess
from formula10.database.model.db_user import DbUser
from formula10.database.validation import any_is_none, positions_are_contiguous, race_has_started
from formula10 import ENABLE_TIMING, db


def find_or_create_race_guess(user_name: str, race_name: str) -> DbRaceGuess:
    # There can be a single RaceGuess at most, since (user_name, race_name) is the composite primary key
    race_guess: DbRaceGuess | None = db.session.query(DbRaceGuess).filter_by(user_name=user_name, race_name=race_name).first()
    if race_guess is not None:
        return race_guess

    # Insert a new RaceGuess
    race_guess = DbRaceGuess(user_name=user_name, race_name=race_name, pxx_driver_name="TEMP", dnf_driver_name="TEMP")
    db.session.add(race_guess)
    db.session.commit()

    # Double check if database insertion worked and obtain any values set by the database
    race_guess = db.session.query(DbRaceGuess).filter_by(user_name=user_name, race_name=race_name).first()
    if race_guess is None:
        raise Exception("Failed adding RaceGuess to the database")

    return race_guess


def update_race_guess(race_name: str, user_name: str, pxx_select: str | None, dnf_select: str | None) -> Response:
    if any_is_none(pxx_select, dnf_select):
        return error_redirect(f"Picks for race \"{race_name}\" were not saved, because you did not fill all the fields.")

    if ENABLE_TIMING and race_has_started(race_name=race_name):
        return error_redirect(f"No picks for race \"{race_name}\" can be entered, as this race has already started.")

    if race_has_result(race_name):
        return error_redirect(f"No picks for race \"{race_name}\" can be entered, as this race has already finished.")

    pxx_driver_name: str = cast(str, pxx_select)
    dnf_driver_name: str = cast(str, dnf_select)

    race_guess: DbRaceGuess = find_or_create_race_guess(user_name, race_name)
    race_guess.pxx_driver_name = pxx_driver_name
    race_guess.dnf_driver_name = dnf_driver_name

    db.session.commit()

    return redirect("/race/Everyone")


def delete_race_guess(race_name: str, user_name: str) -> Response:
    # Don't change guesses that are already over
    if ENABLE_TIMING and race_has_started(race_name=race_name):
        return error_redirect(f"No picks for race \"{race_name}\" can be deleted, as this race has already started.")

    if race_has_result(race_name):
        return error_redirect(f"No picks for race \"{race_name}\" can be deleted, as this race has already finished.")

    # Does not throw if row doesn't exist
    db.session.query(DbRaceGuess).filter_by(race_name=race_name, user_name=user_name).delete()
    db.session.commit()

    return redirect("/race/Everyone")


def find_or_create_season_guess(user_name: str) -> DbSeasonGuess:
    # There can be a single SeasonGuess at most, since user_name is the primary key
    season_guess: DbSeasonGuess | None = db.session.query(DbSeasonGuess).filter_by(user_name=user_name).first()
    if season_guess is not None:
        return season_guess

    # Insert a new SeasonGuess
    season_guess = DbSeasonGuess(user_name=user_name, team_winners_driver_names_json=json.dumps(["TEMP"]), podium_drivers_driver_names_json=json.dumps(["TEMP"]))
    db.session.add(season_guess)
    db.session.commit()

    # Double check if database insertion worked and obtain any values set by the database
    season_guess = db.session.query(DbSeasonGuess).filter_by(user_name=user_name).first()
    if season_guess is None:
        raise Exception("Failed adding SeasonGuess to the database")

    return season_guess


def update_season_guess(user_name: str, guesses: List[str | None], team_winner_guesses: List[str | None], podium_driver_guesses: List[str]) -> Response:
    # Pylance marks type errors here, but those are intended. Columns are marked nullable.

    if ENABLE_TIMING and race_has_started(race_name="Bahrain"):
        return error_redirect("No season picks can be entered, as the season has already begun!")

    season_guess: DbSeasonGuess = find_or_create_season_guess(user_name)
    season_guess.hot_take = guesses[0]  # type: ignore
    season_guess.p2_team_name = guesses[1]  # type: ignore
    season_guess.overtake_driver_name = guesses[2]  # type: ignore
    season_guess.dnf_driver_name = guesses[3]  # type: ignore
    season_guess.gained_driver_name = guesses[4]  # type: ignore
    season_guess.lost_driver_name = guesses[5]  # type: ignore
    season_guess.team_winners_driver_names_json = json.dumps(team_winner_guesses)
    season_guess.podium_drivers_driver_names_json = json.dumps(podium_driver_guesses)

    db.session.commit()

    return redirect(f"/season/Everyone")


def find_or_create_race_result(race_name: str) -> DbRaceResult:
    # There can be a single RaceResult at most, since race_name is the primary key
    race_result: DbRaceResult | None = db.session.query(DbRaceResult).filter_by(race_name=race_name).first()
    if race_result is not None:
        return race_result

    race_result = DbRaceResult(race_name=race_name,
                               pxx_driver_names_json=json.dumps(["TEMP"]),
                               first_dnf_driver_names_json=json.dumps(["TEMP"]),
                               dnf_driver_names_json=json.dumps(["TEMP"]),
                               excluded_driver_names_json=json.dumps(["TEMP"]))
    db.session.add(race_result)
    db.session.commit()

    # Double check if database insertion worked and obtain any values set by the database
    race_result = db.session.query(DbRaceResult).filter_by(race_name=race_name).first()
    if race_result is None:
        raise Exception("Failed adding RaceResult to the database")

    return race_result


def update_race_result(race_name: str, pxx_driver_names_list: List[str], first_dnf_driver_names_list: List[str], dnf_driver_names_list: List[str], excluded_driver_names_list: List[str]) -> Response:
    if ENABLE_TIMING and not race_has_started(race_name=race_name):
        return error_redirect("No race result can be entered, as the race has not begun!")

    # Use strings as keys, as these dicts will be serialized to json
    pxx_driver_names: Dict[str, str] = {
        str(position + 1): driver for position, driver in enumerate(pxx_driver_names_list)
    }

    # Not counted drivers have to be at the end
    excluded_driver_names: Dict[str, str] = {
        str(position + 1): driver for position, driver in enumerate(pxx_driver_names_list)
        if driver in excluded_driver_names_list
    }
    if len(excluded_driver_names) > 0 and (not "20" in excluded_driver_names or not positions_are_contiguous(list(excluded_driver_names.keys()))):
        return error_redirect("Race result was not saved, as excluded drivers must be contiguous and at the end of the field!")

    # First DNF drivers have to be contained in DNF drivers
    for driver_name in first_dnf_driver_names_list:
        if driver_name not in dnf_driver_names_list:
            dnf_driver_names_list.append(driver_name)

    # There can't be dnfs but no initial dnfs
    if len(dnf_driver_names_list) > 0 and len(first_dnf_driver_names_list) == 0:
        return error_redirect("Race result was not saved, as there cannot be DNFs without (an) initial DNF(s)!")

    race_result: DbRaceResult = find_or_create_race_result(race_name)
    race_result.pxx_driver_names_json = json.dumps(pxx_driver_names)
    race_result.first_dnf_driver_names_json = json.dumps(first_dnf_driver_names_list)
    race_result.dnf_driver_names_json = json.dumps(dnf_driver_names_list)
    race_result.excluded_driver_names_json = json.dumps(excluded_driver_names_list)

    db.session.commit()

    return redirect(f"/result/{quote(race_name)}")


def update_user(user_name: str | None, add: bool = False, delete: bool = False) -> Response:
    if user_name is None:
        return error_redirect("Invalid request: Cannot add/delete user because it is \"None\"!")

    if not add and not delete:
        return error_redirect("Invalid request: Can either add or delete user!")

    if add and delete:
        return error_redirect("Invalid request: Can either add or delete user!")

    if add:
        if len(user_name) < 3:
            return error_redirect(f"User \"{user_name}\" was not added, because the username must contain at least 3 characters!")

        if user_exists_and_enabled(user_name):
            return error_redirect(f"User \"{user_name}\" was not added, because it already exists!")

        elif user_exists_and_disabled(user_name):
            disabled_user: DbUser | None = db.session.query(DbUser).filter_by(name=user_name, enabled=False).first()
            if disabled_user is None:
                raise Exception("update_user couldn't reenable user")

            disabled_user.enabled = True

        else:
            user: DbUser = DbUser(name=user_name, enabled=True)
            db.session.add(user)

        db.session.commit()

        return redirect("/user")

    if delete:
        if user_exists_and_disabled(user_name):
            return error_redirect(f"User \"{user_name}\" was not deleted, because it does not exist!")

        elif user_exists_and_enabled(user_name):
            enabled_user: DbUser | None = db.session.query(DbUser).filter_by(name=user_name, enabled=True).first()
            if enabled_user is None:
                raise Exception("update_user couldn't disable user")

            enabled_user.enabled = False
            db.session.commit()

        else:
            return error_redirect(f"User \"{user_name}\" was not deleted, because it does not exist!")

        return redirect("/user")

    raise Exception("update_user received illegal combination of arguments")
