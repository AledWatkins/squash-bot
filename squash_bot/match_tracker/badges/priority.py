import decimal
import typing

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

priority_modifiers: dict[type[badge.Badge], typing.Callable] = {
    # Scale the priority based on the streak length
    badge_definitions.WinStreak: lambda badge_: decimal.Decimal(badge_.streak_length / 10),
    badge_definitions.LossStreak: lambda badge_: decimal.Decimal(badge_.streak_length / 10),
}


def get_priority(badge_: badge.Badge) -> decimal.Decimal:
    additional_priority = 0
    if priority_modifier := priority_modifiers.get(badge_.__class__):
        additional_priority = priority_modifier(badge_)
    return base_priority[badge_.__class__] + additional_priority
