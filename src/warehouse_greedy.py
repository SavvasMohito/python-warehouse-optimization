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


class Warehouse_Greedy:
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

    def iter_warehouse_positions(self):
        for bay_num in range(BAYS_PER_RACK):
            for rack_num in range(2):
                for shelf_num in range(SHELVES_PER_BAY):
                    shelf = self.racks[rack_num].bays[bay_num].shelves[shelf_num]
                    yield rack_num, bay_num, shelf_num, shelf

    def find_optimal_position(self, pallet: Europallet) -> Union[None, Tuple[Tuple[int, int, int, int], float]]:
        best_time = float("inf")
        best_position = None

        # For input operations, prefer positions closer to input area (left side)
        for rack_num, bay_num, shelf_num, shelf in self.iter_warehouse_positions():
            if not shelf.can_accept_category(pallet.category) or not shelf.has_space():
                continue

            pallet_pos = shelf.pallets.index(None)

            # Calculate operation time for this position
            operation_time = self.calculate_operation_time(bay_num, shelf_num, pallet_pos, False)

            if operation_time < best_time:
                best_time = operation_time
                best_position = (rack_num, bay_num, shelf_num, pallet_pos)

        return best_position, best_time

    def find_closest_available_pallet(self, pallet_request: Europallet) -> Union[None, Tuple[Tuple[int, int, int, int], float]]:
        best_time = float("inf")
        best_position = None

        # Find the pallet position that minimizes retrieval time
        for rack_num, bay_num, shelf_num, shelf in self.iter_warehouse_positions():
            for pallet_pos, pallet in enumerate(shelf.pallets):
                if pallet and pallet.category == pallet_request.category:
                    operation_time = self.calculate_operation_time(bay_num, shelf_num, pallet_pos, True)
                    if operation_time < best_time:
                        best_time = operation_time
                        best_position = (rack_num, bay_num, shelf_num, pallet_pos)

        return best_position, best_time

    def place_pallet(self, pallet: Europallet) -> bool:
        # Place pallet in the optimal position with the lowest operation time
        position, time = self.find_optimal_position(pallet)
        if position is None:
            return False

        rack_num, bay_num, shelf_num, pallet_pos = position
        shelf = self.racks[rack_num].bays[bay_num].shelves[shelf_num]
        success = shelf.add_pallet(pallet)
        if not success:
            return False

        self.total_operation_time += time
        return True

    def retrieve_pallet(self, pallet_request: Europallet) -> bool:
        # Retrieve the pallet of requested category with the lowest retrieval time
        position, time = self.find_closest_available_pallet(pallet_request)
        if position is None:
            return False

        rack_num, bay_num, shelf_num, pallet_pos = position
        shelf = self.racks[rack_num].bays[bay_num].shelves[shelf_num]
        shelf.pallets[pallet_pos] = None

        self.total_operation_time += time
        return True
