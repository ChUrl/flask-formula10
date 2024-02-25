from formula10.database.model.db_driver import DbDriver
from formula10.database.model.db_race_result import DbRaceResult
from formula10.database.model.db_user import DbUser
from formula10 import db

def race_has_result(race_name: str) -> bool:
    return db.session.query(DbRaceResult).filter_by(race_name=race_name).first() is not None


def user_exists_and_enabled(user_name: str) -> bool:
    return db.session.query(DbUser).filter_by(name=user_name, enabled=True).first() is not None


def user_exists_and_disabled(user_name: str) -> bool:
    return db.session.query(DbUser).filter_by(name=user_name, enabled=False).first() is not None


def find_single_driver_strict(driver_name: str) -> DbDriver:
    db_driver: DbDriver | None = db.session.query(DbDriver).filter_by(name=driver_name).first()
    if db_driver is None:
        raise Exception(f"Could not find driver with name {driver_name} in database")

    return db_driver