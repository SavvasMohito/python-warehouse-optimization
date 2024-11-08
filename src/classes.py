from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from src.constants import BAYS_PER_RACK, PALLETS_PER_SHELF, SHELVES_PER_BAY


class Category(Enum):
    A = "Category A"  # Bottom shelves only
    B = "Category B"  # Top shelves only
    C = "Category C"  # Any shelf


@dataclass
class Europallet:
    category: Category


@dataclass
class Shelf:
    level: int
    pallets: List[Optional[Europallet]]

    def __init__(self, level: int):
        self.level = level
        self.pallets = [None] * PALLETS_PER_SHELF

    def can_accept_category(self, category: Category) -> bool:
        if category == Category.A:
            return self.level == 0  # Bottom shelf
        elif category == Category.B:
            return self.level == SHELVES_PER_BAY - 1  # Top shelf
        return True  # Category C can go anywhere

    def has_space(self) -> bool:
        return None in self.pallets

    def add_pallet(self, pallet: Europallet) -> bool:
        if not self.can_accept_category(pallet.category) or not self.has_space():
            return False

        for i in range(PALLETS_PER_SHELF):
            if self.pallets[i] is None:
                self.pallets[i] = pallet
                return True
        return False


@dataclass
class Bay:
    position: int
    shelves: List[Shelf]

    def __init__(self, position: int):
        self.position = position
        self.shelves = [Shelf(i) for i in range(SHELVES_PER_BAY)]


class Rack:
    def __init__(self, rack_number: int):
        self.rack_number = rack_number
        self.bays = [Bay(i) for i in range(BAYS_PER_RACK)]
