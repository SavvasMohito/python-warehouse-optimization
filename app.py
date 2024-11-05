from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

# Constants
FORKLIFT_SPEED = 1.2  # m/s
LIFT_SPEED = 0.5  # m/s
AISLE_LENGTH = 5  # meters (d1 = d2 = 5m)
RACK_WIDTH = 3  # meters (b_rack = 3m)
SHELF_HEIGHT = 1.8  # meters (h_shelf = 1.8m)
PALLET_WIDTH = 0.8  # meters (b_pallet = 0.8m)
PALLETS_PER_SHELF = 3
BAYS_PER_RACK = 10
SHELVES_PER_BAY = 4


class Category(Enum):
    A = "A"  # Bottom shelves only
    B = "B"  # Top shelves only
    C = "C"  # Any shelf


@dataclass
class Europallet:
    category: Category
    timestamp: datetime


@dataclass
class Shelf:
    level: int
    pallets: List[Optional[Europallet]]

    def __init__(self, level: int):
        self.level = level
        self.pallets = [None] * PALLETS_PER_SHELF


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

