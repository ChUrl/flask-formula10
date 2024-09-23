from typing import List

from formula10 import cache


def cache_invalidate_user_updated() -> None:
    caches: List[str] = [
        "domain_all_users",
        "domain_all_race_guesses",
        "domain_all_season_guesses",
        "points_points_per_step",
        "points_user_standing",
    ]

    memoized_caches: List[str] = [
        "points_by",
        "race_guesses_by",
        "season_guesses_by",
    ]

    for c in caches:
        cache.delete(c)

    for c in memoized_caches:
        cache.delete_memoized(c)


def cache_invalidate_race_result_updated() -> None:
    caches: List[str] = [
        "domain_all_race_results",
        "points_points_per_step",
        "points_team_points_per_step",
        "points_dnfs",
        "points_driver_points_per_step_cumulative",
        "points_wdc_standing_by_position",
        "points_wdc_standing_by_driver",
        "points_most_dnf_names",
        "points_most_gained_names",
        "points_most_lost_names",
        "points_team_points_per_step_cumulative",
        "points_teams_sorted_by_points",
        "points_wcc_standing_by_position",
        "points_wcc_standing_by_team",
        "points_user_standing",
        "template_first_race_without_result",
    ]

    memoized_caches: List[str] = [
        "driver_points_per_step",
        "driver_points_by",
        "total_driver_points_by",
        "drivers_sorted_by_points",
        "total_team_points_by",
        "points_by",
        "is_team_winner",
        "has_podium",
        "picks_with_points_count",
    ]

    for c in caches:
        cache.delete(c)

    for c in memoized_caches:
        cache.delete_memoized(c)


def cache_invalidate_race_guess_updated() -> None:
    caches: List[str] = [
        "domain_all_race_guesses",
    ]

    memoized_caches: List[str] = [
        "race_guesses_by",
    ]

    for c in caches:
        cache.delete(c)

    for c in memoized_caches:
        cache.delete_memoized(c)


def cache_invalidate_season_guess_updated() -> None:
    caches: List[str] = [
        "domain_all_season_guesses"
    ]

    memoized_caches: List[str] = [
        "season_guesses_by"
    ]

    for c in caches:
        cache.delete(c)

    for c in memoized_caches:
        cache.delete_memoized(c)
