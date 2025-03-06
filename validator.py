#!/usr/bin/env python3
"""
Package Delivery Solution Validator

This script validates and scores a solution for the Package Delivery Algorithm Competition.
It checks if the solution is valid and calculates a score based on delivery time and penalties.

Usage:
    python validator.py input_file output_file

Args:
    input_file: Path to the input JSON file containing the problem definition
    output_file: Path to the output JSON file containing the solution to validate

Returns:
    A score for the solution (lower is better)
    Detailed breakdown of the score and any validation errors
"""

import json
import sys
import math
from typing import Dict, List, Any, Tuple, Set


class Validator:
    def __init__(self, input_file: str, output_file: str):
        """
        Initialize the validator with input and output files.
        
        Args:
            input_file: Path to the input JSON file
            output_file: Path to the output JSON file
        """
        self.input_file = input_file
        self.output_file = output_file
        self.input_data = None
        self.output_data = None
        self.locations = {}
        self.couriers = {}
        self.packages = {}
        self.errors = []
        self.warnings = []
        
        # Tracking variables
        self.courier_positions = {}
        self.courier_packages = {}
        self.package_status = {}
        self.package_point_contents = {}
        self.delivered_packages = set()
        
        # Score components
        self.completion_time = 0
        self.undelivered_penalty = 0
        self.invalid_action_penalty = 0
        
    def load_data(self) -> bool:
        """
        Load and parse the input and output JSON files.
        
        Returns:
            bool: True if loading was successful, False otherwise
        """
        try:
            with open(self.input_file, 'r') as f:
                self.input_data = json.load(f)
                
            with open(self.output_file, 'r') as f:
                self.output_data = json.load(f)
                
            return True
        except Exception as e:
            self.errors.append(f"Error loading files: {str(e)}")
            return False
            
    def initialize_tracking(self):
        """Initialize tracking data structures from input data."""
        # Process locations
        for location in self.input_data["map"]["locations"]:
            self.locations[location["id"]] = location
            if location["type"] == "package_point":
                self.package_point_contents[location["id"]] = []
        
        # Process couriers
        for courier in self.input_data["couriers"]:
            courier_id = courier["id"]
            self.couriers[courier_id] = courier
            
            # Set initial position
            start_loc = courier["start_location"]
            start_coords = self._get_location_coordinates(start_loc)
            self.courier_positions[courier_id] = start_coords
            
            # Initialize empty package list for each courier
            self.courier_packages[courier_id] = []
        
        # Process packages
        for package in self.input_data["packages"]:
            package_id = package["id"]
            self.packages[package_id] = package
            self.package_status[package_id] = {
                "status": "at_warehouse",
                "location": package["origin"],
                "arrival_time": package["arrival_time"],
                "delivery_time": None
            }
    
    def _get_location_coordinates(self, location_id: str) -> List[int]:
        """Get coordinates for a location by its ID."""
        for loc in self.input_data["map"]["locations"]:
            if loc["id"] == location_id:
                return loc["coordinates"]
        return None
    
    def _calculate_distance(self, point1: List[int], point2: List[int]) -> float:
        """Calculate the Euclidean distance between two points."""
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    def _is_valid_move(self, from_pos: List[int], to_pos: List[int]) -> bool:
        """Check if a move is valid (one cell horizontally, vertically, or diagonally)."""
        dx = abs(to_pos[0] - from_pos[0])
        dy = abs(to_pos[1] - from_pos[1])
        return dx <= 1 and dy <= 1 and (dx > 0 or dy > 0)
    
    def validate_solution(self) -> bool:
        """
        Validate the solution and calculate the score.
        
        Returns:
            bool: True if validation was successful, False otherwise
        """
        if not self.load_data():
            return False
            
        self.initialize_tracking()
        
        # Sort actions by time
        sorted_actions = sorted(self.output_data, key=lambda x: x["time"])
        
        # Process each action
        for action_data in sorted_actions:
            try:
                time = action_data["time"]
                courier_id = action_data["courier"]
                action_type = action_data["action"]
                
                # Update completion time
                if time > self.completion_time:
                    self.completion_time = time
                
                # Check if courier exists
                if courier_id not in self.couriers:
                    self.errors.append(f"Invalid courier ID: {courier_id}")
                    self.invalid_action_penalty += 10
                    continue
                    
                # Process action based on type
                if action_type == "pick_up":
                    self._process_pickup(action_data, time)
                elif action_type == "drop_off":
                    self._process_dropoff(action_data, time)
                elif action_type == "deliver":
                    self._process_deliver(action_data, time)
                elif action_type == "move":
                    self._process_move(action_data, time)
                elif action_type == "wait":
                    # Wait action is always valid as long as location is valid
                    location_id = action_data.get("location", None)
                    if location_id and location_id not in self.locations:
                        self.errors.append(f"Invalid location ID for wait action: {location_id}")
                        self.invalid_action_penalty += 10
                else:
                    self.errors.append(f"Invalid action type: {action_type}")
                    self.invalid_action_penalty += 10
            except KeyError as e:
                self.errors.append(f"Missing required field in action: {str(e)}")
                self.invalid_action_penalty += 10
            except Exception as e:
                self.errors.append(f"Error processing action: {str(e)}")
                self.invalid_action_penalty += 10
        
        # Check for undelivered packages
        undelivered = set(self.packages.keys()) - self.delivered_packages
        self.undelivered_penalty = len(undelivered) * 100
        
        if undelivered:
            self.errors.append(f"Undelivered packages: {', '.join(undelivered)}")
        
        return len(self.errors) == 0
    
    def _process_pickup(self, action_data: Dict[str, Any], time: int):
        """Process a pick_up action."""
        courier_id = action_data["courier"]
        location_id = action_data["location"]
        packages = action_data.get("packages", [])
        
        # Check if courier is at the location
        courier_pos = self.courier_positions[courier_id]
        location_pos = self._get_location_coordinates(location_id)
        
        if not location_pos:
            self.errors.append(f"Invalid location ID: {location_id}")
            self.invalid_action_penalty += 10
            return
            
        if courier_pos != location_pos:
            self.errors.append(f"Courier {courier_id} is not at location {location_id}")
            self.invalid_action_penalty += 10
            return
            
        # Check if location is a warehouse
        location = self.locations[location_id]
        if location["type"] != "warehouse":
            self.errors.append(f"Cannot pick up from non-warehouse location: {location_id}")
            self.invalid_action_penalty += 10
            return
            
        # Check courier capacity
        courier = self.couriers[courier_id]
        current_packages = self.courier_packages[courier_id]
        if len(current_packages) + len(packages) > courier["capacity"]:
            self.errors.append(f"Exceeding courier capacity for {courier_id}")
            self.invalid_action_penalty += 10
            return
            
        # Check if packages are available at the warehouse
        for package_id in packages:
            if package_id not in self.packages:
                self.errors.append(f"Invalid package ID: {package_id}")
                self.invalid_action_penalty += 10
                continue
                
            package = self.packages[package_id]
            package_status = self.package_status[package_id]
            
            # Check if package is at the warehouse and has arrived
            if package["origin"] != location_id:
                self.errors.append(f"Package {package_id} origin is not {location_id}")
                self.invalid_action_penalty += 10
                continue
                
            if package_status["status"] != "at_warehouse":
                self.errors.append(f"Package {package_id} is not at warehouse")
                self.invalid_action_penalty += 10
                continue
                
            if time < package["arrival_time"]:
                self.errors.append(f"Package {package_id} has not arrived yet at time {time}")
                self.invalid_action_penalty += 10
                continue
                
            # Update package status
            package_status["status"] = "with_courier"
            package_status["location"] = courier_id
            
            # Add package to courier
            self.courier_packages[courier_id].append(package_id)
    
    def _process_dropoff(self, action_data: Dict[str, Any], time: int):
        """Process a drop_off action."""
        courier_id = action_data["courier"]
        location_id = action_data["location"]
        packages = action_data.get("packages", [])
        
        # Check if courier is at the location
        courier_pos = self.courier_positions[courier_id]
        location_pos = self._get_location_coordinates(location_id)
        
        if not location_pos:
            self.errors.append(f"Invalid location ID: {location_id}")
            self.invalid_action_penalty += 10
            return
            
        if courier_pos != location_pos:
            self.errors.append(f"Courier {courier_id} is not at location {location_id}")
            self.invalid_action_penalty += 10
            return
            
        # Check if location is a package point
        location = self.locations[location_id]
        if location["type"] != "package_point":
            self.errors.append(f"Cannot drop off at non-package-point location: {location_id}")
            self.invalid_action_penalty += 10
            return
            
        # Check package point capacity
        current_pp_packages = self.package_point_contents[location_id]
        if len(current_pp_packages) + len(packages) > location["capacity"]:
            self.errors.append(f"Exceeding package point capacity for {location_id}")
            self.invalid_action_penalty += 10
            return
            
        # Check if courier has the packages
        current_packages = self.courier_packages[courier_id]
        for package_id in packages:
            if package_id not in current_packages:
                self.errors.append(f"Courier {courier_id} does not have package {package_id}")
                self.invalid_action_penalty += 10
                continue
                
            # Update package status
            self.package_status[package_id]["status"] = "at_package_point"
            self.package_status[package_id]["location"] = location_id
            
            # Remove package from courier
            self.courier_packages[courier_id].remove(package_id)
            
            # Add package to package point
            self.package_point_contents[location_id].append(package_id)
    
    def _process_deliver(self, action_data: Dict[str, Any], time: int):
        """Process a deliver action."""
        courier_id = action_data["courier"]
        location_id = action_data["location"]
        packages = action_data.get("packages", [])
        
        # Check if courier is at the location
        courier_pos = self.courier_positions[courier_id]
        location_pos = self._get_location_coordinates(location_id)
        
        if not location_pos:
            self.errors.append(f"Invalid location ID: {location_id}")
            self.invalid_action_penalty += 10
            return
            
        if courier_pos != location_pos:
            self.errors.append(f"Courier {courier_id} is not at location {location_id}")
            self.invalid_action_penalty += 10
            return
            
        # Check if location is a destination
        location = self.locations[location_id]
        if location["type"] != "destination":
            self.errors.append(f"Cannot deliver to non-destination location: {location_id}")
            self.invalid_action_penalty += 10
            return
            
        # Check if courier has the packages and if destination matches
        current_packages = self.courier_packages[courier_id]
        for package_id in packages:
            if package_id not in current_packages:
                self.errors.append(f"Courier {courier_id} does not have package {package_id}")
                self.invalid_action_penalty += 10
                continue
                
            package = self.packages[package_id]
            if package["destination"] != location_id:
                self.errors.append(f"Package {package_id} destination is not {location_id}")
                self.invalid_action_penalty += 10
                continue
                
            # Update package status
            self.package_status[package_id]["status"] = "delivered"
            self.package_status[package_id]["location"] = location_id
            self.package_status[package_id]["delivery_time"] = time
            
            # Remove package from courier
            self.courier_packages[courier_id].remove(package_id)
            
            # Mark package as delivered
            self.delivered_packages.add(package_id)
    
    def _process_move(self, action_data: Dict[str, Any], time: int):
        """Process a move action."""
        courier_id = action_data["courier"]
        from_pos = action_data["from"]
        to_pos = action_data["to"]
        packages = action_data.get("packages", [])
        
        # Check if courier is at the from position
        courier_pos = self.courier_positions[courier_id]
        if courier_pos != from_pos:
            self.errors.append(f"Courier {courier_id} is not at position {from_pos}")
            self.invalid_action_penalty += 10
            return
            
        # Check if move is valid (one cell horizontally, vertically, or diagonally)
        if not self._is_valid_move(from_pos, to_pos):
            self.errors.append(f"Invalid move from {from_pos} to {to_pos}")
            self.invalid_action_penalty += 10
            return
            
        # Check if packages match what courier is carrying
        current_packages = self.courier_packages[courier_id]
        if set(packages) != set(current_packages):
            self.errors.append(f"Packages in move action don't match what courier {courier_id} is carrying")
            self.invalid_action_penalty += 10
            return
            
        # Update courier position
        self.courier_positions[courier_id] = to_pos
    
    def calculate_score(self) -> Dict[str, Any]:
        """
        Calculate the final score for the solution.
        
        Returns:
            Dict containing the score and its components
        """
        total_score = self.completion_time + self.undelivered_penalty + self.invalid_action_penalty
        
        return {
            "score": total_score,
            "components": {
                "completion_time": self.completion_time,
                "undelivered_penalty": self.undelivered_penalty,
                "invalid_action_penalty": self.invalid_action_penalty
            },
            "errors": self.errors,
            "warnings": self.warnings,
            "delivered_packages": len(self.delivered_packages),
            "total_packages": len(self.packages),
            "is_valid": len(self.errors) == 0
        }
    
    def validate_and_score(self) -> Dict[str, Any]:
        """
        Validate the solution and calculate the score.
        
        Returns:
            Dict containing the validation result and score
        """
        is_valid = self.validate_solution()
        score_data = self.calculate_score()
        
        return score_data


def main():
    if len(sys.argv) != 3:
        print("Usage: python validator.py input_file output_file")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    validator = Validator(input_file, output_file)
    result = validator.validate_and_score()
    
    print(json.dumps(result, indent=2))
    
    # Return exit code based on validation result
    if not result["is_valid"]:
        sys.exit(1)
    
    return result["score"]


if __name__ == "__main__":
    main() 