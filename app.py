from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Union

import pandas as pd

# Constants
FORKLIFT_SPEED = 1.2  # m/s
LIFT_SPEED = 0.5  # m/s
DISTANCE_TO_AREAS = 5  # meters (d1 = d2 = 5m)
RACK_WIDTH = 3  # meters (b_rack = 3m)
SHELF_HEIGHT = 1.8  # meters (h_shelf = 1.8m)
PALLET_WIDTH = 0.8  # meters (b_pallet = 0.8m)
PALLETS_PER_SHELF = 3
BAYS_PER_RACK = 10
SHELVES_PER_BAY = 4


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

    def add_pallet(self, pallet: Europallet) -> Union[None, int]:
        if not self.can_accept_category(pallet.category) or not self.has_space():
            return None

        for i in range(PALLETS_PER_SHELF):
            if self.pallets[i] is None:
                self.pallets[i] = pallet
                return i
        return None


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


class Warehouse:
    def __init__(self):
        self.racks = [Rack(i) for i in range(2)]
        self.total_operation_time = 0

    def calculate_travel_time(self, bay_position: int, shelf_level: int, position: int, has_more: bool) -> float:
        # Calculate horizontal travel time in seconds
        one_way_distance = DISTANCE_TO_AREAS + bay_position * RACK_WIDTH + position * PALLET_WIDTH + PALLET_WIDTH / 2
        print("owd", one_way_distance)
        # TODO: check if its the last pallet
        # if has_more:
        #     distance += DISTANCE_TO_AREAS  # Add distance to pickup/dropoff area
        horizontal_time = 2 * one_way_distance / FORKLIFT_SPEED

        # Calculate vertical travel time in seconds
        vertical_time = (shelf_level * SHELF_HEIGHT) / LIFT_SPEED

        return horizontal_time + vertical_time


    def place_pallet(self, pallet: Europallet, rack_num: int, bay_num: int, shelf_num: int) -> bool:
        shelf = self.racks[rack_num].bays[bay_num].shelves[shelf_num]
        shelf_spot = shelf.add_pallet(pallet)

        if shelf_spot is None:
            print("Error placing pallet in shelf")
            return False

        # Add operation time
        self.total_operation_time += self.calculate_travel_time(bay_num, shelf_num, shelf_spot, True)
        return True


class WarehouseSimulator:
    def __init__(self):
        self.warehouse = Warehouse()
        self.inputs = pd.read_csv("static/warehouse_log_inputs.csv")
        self.outputs = pd.read_csv("static/warehouse_log_outputs.csv")
        self.dates = pd.to_datetime(self.inputs["Date"].unique(), format="%d/%m/%Y").tolist()

    def run_simulation(self):
        for date in self.dates:
            print(f"Simulating date {date}")
            for p in self.inputs.iloc():
                # Skip input logs before the simulation date
                if pd.to_datetime(p["Date"], format="%d/%m/%Y") < date:
                    continue
                # Stop reading input logs after the simulation date
                if pd.to_datetime(p["Date"], format="%d/%m/%Y") > date:
                    break

                pallet = Europallet(Category(p["Category"]))
                success = self.warehouse.place_pallet(
                    pallet,
                    rack_num=int(str(p["Rack"]).strip()[-1]) - 1,
                    bay_num=int(p["Bay"]) - 1,
                    shelf_num=int(p["Shelf"]) - 1,
                )
                if not success:
                    print(f"Failed to place pallet")

    def generate_report(self):
        return {
            "total_operation_time": self.warehouse.total_operation_time,
            "average_input_operation_time": self.warehouse.total_operation_time / (len(self.inputs)),
            # "average_operation_time": self.warehouse.total_operation_time / (len(self.inputs) + len(self.outputs)),
        }


def main():
    # Initialize simulator
    simulator = WarehouseSimulator()

    # Run simulation
    simulator.run_simulation()

    # Generate and print report
    report = simulator.generate_report()
    print("\nSimulation Report:")
    print(f"Total Operation Time: {report['total_operation_time']:.2f} seconds")
    print(f"Average Operation Time: {report['average_input_operation_time']:.2f} seconds")


if __name__ == "__main__":
    main()
