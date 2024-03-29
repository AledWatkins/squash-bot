import pytest

from squash_bot.match_tracker import utils


class TestCalculateLanguageStrength:
    @pytest.mark.parametrize(
        "winner_score, loser_score, expected",
        [
            (11, 0, 5),
            (10, 1, 4),
            (9, 2, 3),
            (8, 3, 2),
            (7, 4, 1),
            (6, 5, 1),
        ],
    )
    def test_calculate(self, winner_score, loser_score, expected):
        assert utils.calculate_language_strength(winner_score, loser_score) == expected
