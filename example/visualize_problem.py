#!/usr/bin/env python3
"""
Package Delivery Problem Visualizer

This script visualizes the input data for the Package Delivery Algorithm Competition.
It creates a 2D grid map representation of the problem state, showing warehouses, 
package points, destinations, couriers, and packages.

Usage:
    python visualize_problem.py <input_file.json>

Requirements:
    - matplotlib
    - numpy
    - json

Example:
    python visualize_problem.py sample_input.json
"""

import json
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.lines import Line2D
from typing import Dict, List, Any, Tuple


def load_problem_data(file_path: str) -> Dict[str, Any]:
    """
    Load problem data from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing problem data
        
    Returns:
        Dictionary containing the problem data
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{file_path}' contains invalid JSON.")
        sys.exit(1)


def get_location_by_id(data: Dict[str, Any], location_id: str) -> Dict[str, Any]:
    """
    Get location details by ID.
    
    Args:
        data: Dictionary containing the problem data
        location_id: ID of the location to find
        
    Returns:
        Dictionary containing location details
    """
    for location in data['map']['locations']:
        if location['id'] == location_id:
            return location
    return None


def visualize_problem(data: Dict[str, Any], output_file: str = None):
    """
    Visualize the package delivery problem on a 2D grid map.
    
    Args:
        data: Dictionary containing the problem data
        output_file: Path to save the visualization (if None, display instead)
    """
    # Get map dimensions
    map_width, map_height = data['map']['dimensions']
    
    # Create figure
    plt.figure(figsize=(12, 10))
    
    # Create grid
    plt.xlim(-0.5, map_width - 0.5)
    plt.ylim(-0.5, map_height - 0.5)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Plot locations
    warehouse_xs, warehouse_ys = [], []
    package_point_xs, package_point_ys = [], []
    destination_xs, destination_ys = [], []
    package_point_capacities = []
    location_coords = {}
    
    for location in data['map']['locations']:
        x, y = location['coordinates']
        location_coords[location['id']] = (x, y)
        
        if location['type'] == 'warehouse':
            warehouse_xs.append(x)
            warehouse_ys.append(y)
            plt.text(x, y + 0.3, location['id'], fontsize=10, ha='center')
        elif location['type'] == 'package_point':
            package_point_xs.append(x)
            package_point_ys.append(y)
            package_point_capacities.append(location['capacity'])
            plt.text(x, y + 0.3, f"{location['id']} (Cap: {location['capacity']})", fontsize=10, ha='center')
        elif location['type'] == 'destination':
            destination_xs.append(x)
            destination_ys.append(y)
            plt.text(x, y + 0.3, location['id'], fontsize=10, ha='center')
    
    # Plot warehouses (blue squares)
    plt.scatter(warehouse_xs, warehouse_ys, color='skyblue', s=200, marker='s', edgecolors='black', zorder=10, label='Warehouse')
    
    # Plot package points (green circles with size based on capacity)
    sizes = [100 + cap * 30 for cap in package_point_capacities]
    plt.scatter(package_point_xs, package_point_ys, color='lightgreen', s=sizes, edgecolors='black', zorder=10, label='Package Point')
    
    # Plot destinations (red triangles)
    plt.scatter(destination_xs, destination_ys, color='salmon', s=200, marker='^', edgecolors='black', zorder=10, label='Destination')
    
    # Plot couriers
    courier_positions = {}
    for i, courier in enumerate(data['couriers']):
        start_location_id = courier['start_location']
        start_location = get_location_by_id(data, start_location_id)
        
        if start_location:
            x, y = start_location['coordinates']
            
            # Offset courier position slightly from the location
            angle = 2 * np.pi * i / len(data['couriers'])
            offset_x = 0.2 * np.cos(angle)
            offset_y = 0.2 * np.sin(angle)
            courier_pos = (x + offset_x, y + offset_y)
            courier_positions[courier['id']] = courier_pos
            
            plt.scatter(*courier_pos, color='purple', s=150, marker='s', edgecolors='black', zorder=15)
            plt.text(courier_pos[0], courier_pos[1] + 0.2, courier['id'], fontsize=8, ha='center')
            plt.text(courier_pos[0], courier_pos[1] - 0.2, f"Cap: {courier['capacity']}", fontsize=7, ha='center')
    
    # Plot packages as paths from origin to destination
    for i, package in enumerate(data['packages']):
        origin_id = package['origin']
        destination_id = package['destination']
        
        origin_location = get_location_by_id(data, origin_id)
        destination_location = get_location_by_id(data, destination_id)
        
        if origin_location and destination_location:
            origin_x, origin_y = origin_location['coordinates']
            dest_x, dest_y = destination_location['coordinates']
            
            # Calculate path with slight curve
            dx = dest_x - origin_x
            dy = dest_y - origin_y
            
            # Number of points in the path
            num_points = 20
            
            # Create a curved path
            t = np.linspace(0, 1, num_points)
            
            # Add some curvature
            curve_height = 0.5 + (i * 0.1)  # Different curve for each package
            
            # Parametric curve
            x = origin_x + dx * t
            y = origin_y + dy * t + curve_height * np.sin(np.pi * t)
            
            # Draw the path as a dashed line
            plt.plot(x, y, 'r--', alpha=0.4, linewidth=1)
            
            # Add package label at the midpoint
            mid_idx = num_points // 2
            mid_x, mid_y = x[mid_idx], y[mid_idx]
            
            plt.text(mid_x, mid_y, package['id'], fontsize=7, ha='center', va='center',
                    bbox=dict(facecolor='yellow', alpha=0.7, edgecolor='none'))
            
            # Add arrival time
            plt.text(mid_x, mid_y - 0.3, f"Arrival: {package['arrival_time']}", fontsize=6, ha='center',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color='skyblue', label='Warehouse'),
        mpatches.Patch(color='lightgreen', label='Package Point'),
        mpatches.Patch(color='salmon', label='Destination'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='purple', markersize=10, label='Courier'),
        Line2D([0], [0], linestyle='--', color='r', label='Package Route')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    # Set title and labels
    plt.title('Package Delivery Problem Visualization')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    
    # Set integer ticks
    plt.xticks(range(map_width))
    plt.yticks(range(map_height))
    
    # Save or display
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {output_file}")
    else:
        plt.tight_layout()
        plt.show()


def main():
    """Main function to handle command line arguments and run the visualization."""
    if len(sys.argv) < 2:
        print("Usage: python visualize_problem.py <input_file.json> [output_file.png]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    data = load_problem_data(input_file)
    visualize_problem(data, output_file)


if __name__ == "__main__":
    main() 