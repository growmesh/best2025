#!/usr/bin/env python3
"""
Package Delivery Solution Visualizer

This script visualizes the solution (output) for the Package Delivery Algorithm Competition.
It creates an animated visualization showing the movement of couriers and packages over time.

Usage:
    python visualize_solution.py <input_file.json> <output_file.json> [--save animation.gif]

Requirements:
    - matplotlib
    - numpy
    - json

Example:
    python visualize_solution.py sample_input.json sample_output.json
    python visualize_solution.py sample_input.json sample_output.json --save solution.gif
"""

import json
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
import numpy as np
from matplotlib.lines import Line2D
from typing import Dict, List, Any, Tuple
import argparse


def load_json_data(file_path: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the data
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


def get_location_by_id(input_data: Dict[str, Any], location_id: str) -> Dict[str, Any]:
    """
    Get location details by ID.
    
    Args:
        input_data: Dictionary containing the problem data
        location_id: ID of the location to find
        
    Returns:
        Dictionary containing location details
    """
    for location in input_data['map']['locations']:
        if location['id'] == location_id:
            return location
    return None


def get_courier_positions(input_data: Dict[str, Any], output_data: List[Dict[str, Any]], time: int) -> Dict[str, Tuple]:
    """
    Get positions of all couriers at a specific time.
    
    Args:
        input_data: Dictionary containing the problem data
        output_data: List of actions from the solution
        time: The time slice to get positions for
        
    Returns:
        Dictionary mapping courier IDs to (x, y) positions and packages carried
    """
    # Initialize courier positions with their starting locations
    courier_positions = {}
    for courier in input_data['couriers']:
        start_location = get_location_by_id(input_data, courier['start_location'])
        if start_location:
            courier_positions[courier['id']] = {
                'position': start_location['coordinates'],
                'packages': [],
                'action': 'wait',
                'location_id': courier['start_location']
            }
    
    # Update positions based on actions up to the given time
    for action in output_data:
        if action['time'] > time:
            break
            
        courier_id = action['courier']
        
        if action['action'] == 'move':
            courier_positions[courier_id]['position'] = action['to']
            courier_positions[courier_id]['packages'] = action['packages']
            courier_positions[courier_id]['action'] = 'move'
            courier_positions[courier_id]['location_id'] = None
        elif action['action'] in ['pick_up', 'drop_off', 'deliver', 'wait']:
            # For non-move actions, get the coordinates from the location
            location = get_location_by_id(input_data, action['location'])
            if location:
                courier_positions[courier_id]['position'] = location['coordinates']
                courier_positions[courier_id]['packages'] = action['packages']
                courier_positions[courier_id]['action'] = action['action']
                courier_positions[courier_id]['location_id'] = action['location']
    
    return courier_positions


def get_package_status(input_data: Dict[str, Any], output_data: List[Dict[str, Any]], time: int) -> Dict[str, Dict]:
    """
    Get the status of all packages at a specific time.
    
    Args:
        input_data: Dictionary containing the problem data
        output_data: List of actions from the solution
        time: The time slice to get statuses for
        
    Returns:
        Dictionary mapping package IDs to their status information
    """
    # Initialize package statuses
    package_status = {}
    for package in input_data['packages']:
        # Check if package has arrived at warehouse
        if package['arrival_time'] <= time:
            package_status[package['id']] = {
                'status': 'at_warehouse',
                'location': package['origin'],
                'position': get_location_by_id(input_data, package['origin'])['coordinates'],
                'carrier': None
            }
        else:
            package_status[package['id']] = {
                'status': 'not_arrived',
                'location': None,
                'position': None,
                'carrier': None
            }
    
    # Update statuses based on actions up to the given time
    for action in output_data:
        if action['time'] > time:
            break
            
        courier_id = action['courier']
        
        if action['action'] == 'pick_up':
            for package_id in action['packages']:
                if package_id in package_status:
                    package_status[package_id]['status'] = 'with_courier'
                    package_status[package_id]['location'] = action['location']
                    package_status[package_id]['position'] = get_location_by_id(input_data, action['location'])['coordinates']
                    package_status[package_id]['carrier'] = courier_id
        
        elif action['action'] == 'drop_off':
            for package_id in action['packages']:
                if package_id in package_status:
                    package_status[package_id]['status'] = 'at_package_point'
                    package_status[package_id]['location'] = action['location']
                    package_status[package_id]['position'] = get_location_by_id(input_data, action['location'])['coordinates']
                    package_status[package_id]['carrier'] = None
        
        elif action['action'] == 'deliver':
            for package_id in action['packages']:
                if package_id in package_status:
                    package_status[package_id]['status'] = 'delivered'
                    package_status[package_id]['location'] = action['location']
                    package_status[package_id]['position'] = get_location_by_id(input_data, action['location'])['coordinates']
                    package_status[package_id]['carrier'] = None
        
        elif action['action'] == 'move':
            # Update positions of packages carried by the courier
            for package_id in action['packages']:
                if package_id in package_status and package_status[package_id]['carrier'] == courier_id:
                    package_status[package_id]['status'] = 'with_courier'
                    package_status[package_id]['location'] = None
                    package_status[package_id]['position'] = action['to']
    
    return package_status


def create_animation(input_data: Dict[str, Any], output_data: List[Dict[str, Any]], save_path: str = None):
    """
    Create an animation of the solution.
    
    Args:
        input_data: Dictionary containing the problem data
        output_data: List of actions from the solution
        save_path: Path to save the animation (if None, display instead)
    """
    # Get map dimensions
    map_width, map_height = input_data['map']['dimensions']
    
    # Get max time from output data
    max_time = max(action['time'] for action in output_data) + 1
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Function to draw a single frame
    def draw_frame(time):
        ax.clear()
        
        # Set up the grid
        ax.set_xlim(-0.5, map_width - 0.5)
        ax.set_ylim(-0.5, map_height - 0.5)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Set integer ticks
        ax.set_xticks(range(map_width))
        ax.set_yticks(range(map_height))
        
        # Plot locations
        warehouse_xs, warehouse_ys = [], []
        package_point_xs, package_point_ys = [], []
        destination_xs, destination_ys = [], []
        package_point_capacities = []
        location_coords = {}
        
        for location in input_data['map']['locations']:
            x, y = location['coordinates']
            location_coords[location['id']] = (x, y)
            
            if location['type'] == 'warehouse':
                warehouse_xs.append(x)
                warehouse_ys.append(y)
                ax.text(x, y + 0.3, location['id'], fontsize=10, ha='center')
            elif location['type'] == 'package_point':
                package_point_xs.append(x)
                package_point_ys.append(y)
                package_point_capacities.append(location['capacity'])
                ax.text(x, y + 0.3, f"{location['id']} (Cap: {location['capacity']})", fontsize=10, ha='center')
            elif location['type'] == 'destination':
                destination_xs.append(x)
                destination_ys.append(y)
                ax.text(x, y + 0.3, location['id'], fontsize=10, ha='center')
        
        # Plot warehouses (blue squares)
        ax.scatter(warehouse_xs, warehouse_ys, color='skyblue', s=200, marker='s', edgecolors='black', zorder=10)
        
        # Plot package points (green circles with size based on capacity)
        sizes = [100 + cap * 30 for cap in package_point_capacities]
        ax.scatter(package_point_xs, package_point_ys, color='lightgreen', s=sizes, edgecolors='black', zorder=10)
        
        # Plot destinations (red triangles)
        ax.scatter(destination_xs, destination_ys, color='salmon', s=200, marker='^', edgecolors='black', zorder=10)
        
        # Get courier positions and package statuses for this time
        courier_positions = get_courier_positions(input_data, output_data, time)
        package_status = get_package_status(input_data, output_data, time)
        
        # Plot couriers
        for courier_id, courier_info in courier_positions.items():
            x, y = courier_info['position']
            packages = courier_info['packages']
            action = courier_info['action']
            
            # Different colors for different actions
            color = 'purple'  # default
            if action == 'pick_up':
                color = 'green'
            elif action == 'drop_off':
                color = 'orange'
            elif action == 'deliver':
                color = 'red'
            
            ax.scatter(x, y, color=color, s=150, marker='s', edgecolors='black', zorder=15)
            ax.text(x, y + 0.2, courier_id, fontsize=8, ha='center')
            
            # Show packages carried
            if packages:
                ax.text(x, y - 0.2, f"{', '.join(packages)}", fontsize=7, ha='center',
                       bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
        
        # Plot packages
        for package_id, status in package_status.items():
            if status['status'] == 'not_arrived':
                continue  # Don't show packages that haven't arrived yet
                
            if status['status'] == 'delivered':
                continue  # Don't show delivered packages
                
            if status['position']:
                x, y = status['position']
                
                # Different colors for different statuses
                color = 'yellow'  # default
                if status['status'] == 'at_warehouse':
                    color = 'blue'
                elif status['status'] == 'at_package_point':
                    color = 'green'
                
                # Only show packages not carried by couriers
                if status['carrier'] is None:
                    ax.scatter(x, y, color=color, s=80, marker='o', edgecolors='black', alpha=0.7, zorder=12)
                    ax.text(x, y, package_id, fontsize=6, ha='center', va='center')
        
        # Set title with current time
        ax.set_title(f'Package Delivery Solution - Time: {time}')
        
        # Add legend
        legend_elements = [
            mpatches.Patch(color='skyblue', label='Warehouse'),
            mpatches.Patch(color='lightgreen', label='Package Point'),
            mpatches.Patch(color='salmon', label='Destination'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='purple', markersize=10, label='Courier (Moving/Waiting)'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='green', markersize=10, label='Courier (Picking Up)'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='orange', markersize=10, label='Courier (Dropping Off)'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=10, label='Courier (Delivering)'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Package at Warehouse'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='Package at Package Point')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize='small')
        
        # Add delivery status
        delivered_count = sum(1 for status in package_status.values() if status['status'] == 'delivered')
        total_packages = len(package_status)
        ax.text(0.02, 0.02, f'Delivered: {delivered_count}/{total_packages}', 
                transform=ax.transAxes, fontsize=12, 
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='black'))
        
        return []
    
    # Create animation
    ani = animation.FuncAnimation(fig, draw_frame, frames=range(max_time), interval=500, blit=True)
    
    # Save or display
    if save_path:
        ani.save(save_path, writer='pillow', fps=2)
        print(f"Animation saved to {save_path}")
    else:
        plt.tight_layout()
        plt.show()


def main():
    """Main function to handle command line arguments and run the visualization."""
    parser = argparse.ArgumentParser(description='Visualize a solution for the Package Delivery Problem')
    parser.add_argument('input_file', help='Path to the input JSON file')
    parser.add_argument('output_file', help='Path to the output JSON file (solution)')
    parser.add_argument('--save', help='Path to save the animation (e.g., solution.gif)')
    
    args = parser.parse_args()
    
    input_data = load_json_data(args.input_file)
    output_data = load_json_data(args.output_file)
    
    create_animation(input_data, output_data, args.save)


if __name__ == "__main__":
    main() 