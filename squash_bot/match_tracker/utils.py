import random

from squash_bot.match_tracker.data import dataclasses, static


def build_match_string(match_result: dataclasses.MatchResult) -> str:
    winner_loser_string = generate_winner_loser_string(match_result).format(
        winner=match_result.winner.name, loser=match_result.loser.name
    )
    return f"{winner_loser_string} with a score of {match_result.winner_score}-{match_result.loser_score}"


def generate_winner_loser_string(match_result: dataclasses.MatchResult) -> str:
    language_strength = calculate_language_strength(
        match_result.winner_score, match_result.loser_score
    )
    return random.choice(static.winner_loser_strings[language_strength])


def calculate_language_strength(winner_score: int, loser_score: int) -> int:
    """
    This function will return a number that represents the strength of the language to use when describing the match.

    The strength will be a number between 0 and 5, where 0 is the weakest language and 5 is the strongest language.
    """
    max_difference = 11
    difference = winner_score - loser_score
    return max(int(((difference / max_difference) * 100) // 20), 1)
