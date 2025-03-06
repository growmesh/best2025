#!/usr/bin/env python3
"""
Package Delivery Input Generator

This script generates large input files for the Package Delivery Algorithm Competition.
It creates random problem instances with configurable parameters.

Usage:
    python generate_input.py [options]

Options:
    --size SIZE             Size of the grid map (default: 50)
    --warehouses N          Number of warehouses (default: 5)
    --package-points N      Number of package points (default: 10)
    --destinations N        Number of destinations (default: 15)
    --couriers N            Number of couriers (default: 20)
    --packages N            Number of packages (default: 100)
    --max-capacity N        Maximum capacity of couriers (default: 5)
    --max-pp-capacity N     Maximum capacity of package points (default: 10)
    --max-arrival-time N    Maximum arrival time for packages (default: 50)
    --output FILE           Output file (default: generated_input.json)
    --seed SEED             Random seed for reproducibility (default: None)

Example:
    python generate_input.py --size 100 --packages 500 --output large_input.json
"""

import json
import random
import argparse
from typing import Dict, List, Any, Tuple


def generate_input(
    size: int = 50,
    num_warehouses: int = 5,
    num_package_points: int = 10,
    num_destinations: int = 15,
    num_couriers: int = 20,
    num_packages: int = 100,
    max_courier_capacity: int = 5,
    max_pp_capacity: int = 10,
    max_arrival_time: int = 50,
    seed: int = None
) -> Dict[str, Any]:
    """
    Generate a random input for the package delivery problem.
    
    Args:
        size: Size of the grid map (NxN)
        num_warehouses: Number of warehouses
        num_package_points: Number of package points
        num_destinations: Number of destinations
        num_couriers: Number of couriers
        num_packages: Number of packages
        max_courier_capacity: Maximum capacity of couriers
        max_pp_capacity: Maximum capacity of package points
        max_arrival_time: Maximum arrival time for packages
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary containing the generated input
    """
    if seed is not None:
        random.seed(seed)
    
    # Ensure we don't have too many locations for the grid size
    total_locations = num_warehouses + num_package_points + num_destinations
    max_locations = size * size // 4  # Use at most 25% of the grid for locations
    if total_locations > max_locations:
        scale_factor = max_locations / total_locations
        num_warehouses = max(1, int(num_warehouses * scale_factor))
        num_package_points = max(1, int(num_package_points * scale_factor))
        num_destinations = max(1, int(num_destinations * scale_factor))
        print(f"Warning: Too many locations for grid size. Scaled down to {num_warehouses} warehouses, "
              f"{num_package_points} package points, and {num_destinations} destinations.")
    
    # Generate locations
    locations = []
    used_coordinates = set()
    
    # Generate warehouses
    for i in range(num_warehouses):
        while True:
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            if (x, y) not in used_coordinates:
                used_coordinates.add((x, y))
                locations.append({
                    "id": f"W{i+1}",
                    "type": "warehouse",
                    "coordinates": [x, y]
                })
                break
    
    # Generate package points
    for i in range(num_package_points):
        while True:
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            if (x, y) not in used_coordinates:
                used_coordinates.add((x, y))
                capacity = random.randint(1, max_pp_capacity)
                locations.append({
                    "id": f"P{i+1}",
                    "type": "package_point",
                    "capacity": capacity,
                    "coordinates": [x, y]
                })
                break
    
    # Generate destinations
    for i in range(num_destinations):
        while True:
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            if (x, y) not in used_coordinates:
                used_coordinates.add((x, y))
                locations.append({
                    "id": f"D{i+1}",
                    "type": "destination",
                    "coordinates": [x, y]
                })
                break
    
    # Generate couriers
    couriers = []
    warehouse_ids = [loc["id"] for loc in locations if loc["type"] == "warehouse"]
    
    for i in range(num_couriers):
        start_location = random.choice(warehouse_ids)
        capacity = random.randint(1, max_courier_capacity)
        couriers.append({
            "id": f"C{i+1}",
            "start_location": start_location,
            "capacity": capacity
        })
    
    # Generate packages
    packages = []
    destination_ids = [loc["id"] for loc in locations if loc["type"] == "destination"]
    
    for i in range(num_packages):
        origin = random.choice(warehouse_ids)
        destination = random.choice(destination_ids)
        arrival_time = random.randint(0, max_arrival_time)
        
        packages.append({
            "id": f"P{i+1:03d}",
            "origin": origin,
            "destination": destination,
            "arrival_time": arrival_time
        })
    
    # Create the final input
    input_data = {
        "map": {
            "dimensions": [size, size],
            "locations": locations
        },
        "couriers": couriers,
        "packages": packages
    }
    
    return input_data


def save_input(input_data: Dict[str, Any], output_file: str):
    """
    Save the generated input to a JSON file.
    
    Args:
        input_data: Dictionary containing the input data
        output_file: Path to save the input file
    """
    with open(output_file, 'w') as f:
        json.dump(input_data, f, indent=2)
    print(f"Input saved to {output_file}")


def print_statistics(input_data: Dict[str, Any]):
    """
    Print statistics about the generated input.
    
    Args:
        input_data: Dictionary containing the input data
    """
    map_size = input_data["map"]["dimensions"]
    locations = input_data["map"]["locations"]
    couriers = input_data["couriers"]
    packages = input_data["packages"]
    
    warehouses = [loc for loc in locations if loc["type"] == "warehouse"]
    package_points = [loc for loc in locations if loc["type"] == "package_point"]
    destinations = [loc for loc in locations if loc["type"] == "destination"]
    
    print("\nInput Statistics:")
    print(f"Map Size: {map_size[0]}x{map_size[1]}")
    print(f"Warehouses: {len(warehouses)}")
    print(f"Package Points: {len(package_points)}")
    print(f"Destinations: {len(destinations)}")
    print(f"Couriers: {len(couriers)}")
    print(f"Packages: {len(packages)}")
    
    avg_courier_capacity = sum(c["capacity"] for c in couriers) / len(couriers)
    avg_pp_capacity = sum(p["capacity"] for p in package_points) / len(package_points)
    avg_arrival_time = sum(p["arrival_time"] for p in packages) / len(packages)
    
    print(f"Average Courier Capacity: {avg_courier_capacity:.2f}")
    print(f"Average Package Point Capacity: {avg_pp_capacity:.2f}")
    print(f"Average Package Arrival Time: {avg_arrival_time:.2f}")
    
    # Calculate package distribution
    packages_per_warehouse = {}
    packages_per_destination = {}
    
    for package in packages:
        origin = package["origin"]
        destination = package["destination"]
        
        if origin not in packages_per_warehouse:
            packages_per_warehouse[origin] = 0
        packages_per_warehouse[origin] += 1
        
        if destination not in packages_per_destination:
            packages_per_destination[destination] = 0
        packages_per_destination[destination] += 1
    
    print("\nPackage Distribution:")
    print("Packages per Warehouse:")
    for warehouse, count in packages_per_warehouse.items():
        print(f"  {warehouse}: {count}")
    
    print("Packages per Destination:")
    for destination, count in packages_per_destination.items():
        print(f"  {destination}: {count}")


def main():
    """Main function to handle command line arguments and generate input."""
    parser = argparse.ArgumentParser(description='Generate input for the Package Delivery Problem')
    parser.add_argument('--size', type=int, default=500, help='Size of the grid map (default: 50)')
    parser.add_argument('--warehouses', type=int, default=10, help='Number of warehouses (default: 5)')
    parser.add_argument('--package-points', type=int, default=5, help='Number of package points (default: 10)')
    parser.add_argument('--destinations', type=int, default=40, help='Number of destinations (default: 15)')
    parser.add_argument('--couriers', type=int, default=10, help='Number of couriers (default: 20)')
    parser.add_argument('--packages', type=int, default=500, help='Number of packages (default: 100)')
    parser.add_argument('--max-capacity', type=int, default=5, help='Maximum capacity of couriers (default: 5)')
    parser.add_argument('--max-pp-capacity', type=int, default=10, help='Maximum capacity of package points (default: 10)')
    parser.add_argument('--max-arrival-time', type=int, default=1000, help='Maximum arrival time for packages (default: 50)')
    parser.add_argument('--output', type=str, default='generated_input.json', help='Output file (default: generated_input.json)')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility (default: None)')
    parser.add_argument('--stats', action='store_true', help='Print statistics about the generated input')
    
    args = parser.parse_args()
    
    input_data = generate_input(
        size=args.size,
        num_warehouses=args.warehouses,
        num_package_points=args.package_points,
        num_destinations=args.destinations,
        num_couriers=args.couriers,
        num_packages=args.packages,
        max_courier_capacity=args.max_capacity,
        max_pp_capacity=args.max_pp_capacity,
        max_arrival_time=args.max_arrival_time,
        seed=args.seed
    )
    
    save_input(input_data, args.output)
    
    if args.stats:
        print_statistics(input_data)


if __name__ == "__main__":
    main() 