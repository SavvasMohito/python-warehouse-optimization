import csv
from collections import defaultdict
from typing import List, Union

from src.classes import Category, Europallet
from src.warehouse_fifo import Warehouse_FIFO
from src.warehouse_fill_ends import Warehouse_Fill_Ends
from src.warehouse_fill_middle import Warehouse_Fill_Middle
from src.warehouse_greedy import Warehouse_Greedy
from src.warehouse_lifo import Warehouse_LIFO


class Simulator:
    def __init__(
        self, warehouses: List[Union[Warehouse_FIFO, Warehouse_Fill_Ends, Warehouse_Fill_Middle, Warehouse_Greedy, Warehouse_LIFO]]
    ):
        self.warehouses = warehouses
        self.operations_by_date = self._load_operations()
        self.results = {}

    def _load_operations(self):
        operations = defaultdict(lambda: {"input": [], "output": []})
        # Add pre-existing pallets to satisfy output orders
        operations["31/8/2023"]["input"] = [Europallet(Category.A)] * 20 + [Europallet(Category.B)] * 20 + [Europallet(Category.C)] * 20

        # Import data from csv files
        for input_output in ["input", "output"]:
            with open(f"static/warehouse_log_{input_output}s.csv") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    date = row["Date"]
                    pallet = Europallet(Category(row["Category"]))
                    operations[date][input_output].append(pallet)

        return dict(operations)

    def run_simulation(self):
        # Run the same simulation for all warehouse placement strategies
        for warehouse in self.warehouses:
            for date, operations in self.operations_by_date.items():
                for input_output in ["input", "output"]:
                    for pallet in operations[input_output]:
                        if input_output == "input":
                            success = warehouse.place_pallet(pallet)
                        else:
                            success = warehouse.retrieve_pallet(pallet)
                        if not success:
                            print(f"Failed to {input_output} pallet")

            # Save the total operation time for each warehouse
            self.results[warehouse.__class__.__name__] = {
                "input": warehouse.input_operation_time,
                "output": warehouse.output_operation_time,
                "total": warehouse.input_operation_time + warehouse.output_operation_time,
            }

    def print_report(self):
        print("\nTotal operation times per placement strategy (sorted from quickest to slowest):\n")
        for warehouse_name, operation_times in sorted(self.results.items(), key=lambda x: x[1]["total"]):
            print(
                f"{warehouse_name}:"
                f" \tInput: {operation_times['input']:.2f} seconds"
                f" \tOutput: {operation_times['output']:.2f} seconds"
                f" \tTotal: {operation_times['total']:.2f} seconds"
            )


def main():
    # Initialize warehouses
    warehouse_lifo = Warehouse_LIFO()
    warehouse_fifo = Warehouse_FIFO()
    warehouse_greedy = Warehouse_Greedy()
    warehouse_fill_ends = Warehouse_Fill_Ends()
    warehouse_lifo_middle = Warehouse_Fill_Middle()

    # Initialize simulator
    simulator = Simulator(warehouses=[warehouse_lifo, warehouse_fifo, warehouse_greedy, warehouse_fill_ends, warehouse_lifo_middle])

    # Run simulation
    simulator.run_simulation()

    # Generate and print report
    simulator.print_report()


if __name__ == "__main__":
    main()
