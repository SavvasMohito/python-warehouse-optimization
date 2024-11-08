import time
from typing import Tuple, Union

from src.classes import Europallet, Rack
from src.constants import (
    BAYS_PER_RACK,
    DISTANCE_TO_AREAS,
    FORKLIFT_SPEED,
    LIFT_SPEED,
    PALLET_WIDTH,
    PALLETS_PER_SHELF,
    RACK_WIDTH,
    SHELF_HEIGHT,
    SHELVES_PER_BAY,
)


class Warehouse_FIFO:
    def __init__(self):
        self.racks = [Rack(i) for i in range(2)]
        self.total_operation_time = 0

    def calculate_operation_time(self, bay_position: int, shelf_level: int, pallet_position: int, is_output: bool) -> float:
        if is_output:
            bay_distance = (BAYS_PER_RACK - bay_position - 1) * RACK_WIDTH
            rack_distance = (PALLETS_PER_SHELF - pallet_position - 1) * PALLET_WIDTH
        else:
            bay_distance = bay_position * RACK_WIDTH
            rack_distance = pallet_position * PALLET_WIDTH

        one_way_distance = DISTANCE_TO_AREAS + bay_distance + rack_distance + (PALLET_WIDTH / 2)
        horizontal_time = 2 * one_way_distance / FORKLIFT_SPEED
        vertical_time = (shelf_level * SHELF_HEIGHT * 2) / LIFT_SPEED

        return horizontal_time + vertical_time

    def iter_warehouse_positions_reverse(self):
        for bay_num in reversed(range(BAYS_PER_RACK)):
            for rack_num in reversed(range(2)):
                for shelf_num in reversed(range(SHELVES_PER_BAY)):
                    shelf = self.racks[rack_num].bays[bay_num].shelves[shelf_num]
                    yield rack_num, bay_num, shelf_num, shelf

    # Finds the first available position for the pallet
    def find_closest_position_to_the_end(self, pallet: Europallet, is_input: bool) -> Union[None, Tuple[int, int, int, int]]:
        for rack_num, bay_num, shelf_num, shelf in self.iter_warehouse_positions_reverse():
            if is_input:
                if shelf.can_accept_category(pallet.category) and shelf.has_space():
                    return (rack_num, bay_num, shelf_num, shelf.pallets.index(None))
            else:
                if pallet in shelf.pallets:
                    pallet_pos = len(shelf.pallets) - 1 - shelf.pallets[::-1].index(pallet)
                    return (rack_num, bay_num, shelf_num, pallet_pos)
        return None

    def place_pallet(self, pallet: Europallet) -> bool:
        position = self.find_closest_position_to_the_end(pallet, True)
        if position is None:
            return False

        rack_num, bay_num, shelf_num, pallet_pos = position
        shelf = self.racks[rack_num].bays[bay_num].shelves[shelf_num]

        success = shelf.add_pallet(pallet)
        if not success:
            return False

        # Add operation time
        self.total_operation_time += self.calculate_operation_time(bay_num, shelf_num, pallet_pos, False)
        return True

    def retrieve_pallet(self, pallet_request: Europallet) -> bool:
        position = self.find_closest_position_to_the_end(pallet_request, False)
        if position is None:
            return False

        rack_num, bay_num, shelf_num, pallet_pos = position
        shelf = self.racks[rack_num].bays[bay_num].shelves[shelf_num]
        shelf.pallets[pallet_pos] = None

        # Add operation time
        self.total_operation_time += self.calculate_operation_time(bay_num, shelf_num, pallet_pos, True)
        return True
