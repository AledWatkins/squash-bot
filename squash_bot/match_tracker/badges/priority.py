import decimal

from . import badge, badge_definitions

base_priority: dict[type[badge.Badge], decimal.Decimal] = {
    badge_definitions.Crush: decimal.Decimal("4"),
    badge_definitions.CleanSweep: decimal.Decimal("4"),
    badge_definitions.WoodenSpoon: decimal.Decimal("1"),
    badge_definitions.WinStreak: decimal.Decimal("2"),
    badge_definitions.LossStreak: decimal.Decimal("1"),
    badge_definitions.StreakBreaker: decimal.Decimal("3"),
    badge_definitions.FirstWinAgainst: decimal.Decimal("4"),
    badge_definitions.MVP: decimal.Decimal("2"),
}


def get_priority(badge_: badge.Badge) -> decimal.Decimal:
    return base_priority[badge_.__class__]
