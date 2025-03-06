# Package Delivery Algorithm Competition

## Submission Process

1. After you invited @matteohorvath on github
2. Your algorithm should generate an output.json inside the competition/ folder. (see example at example/extreme/)  
**Please pay attention to the format of the output file, as validation only works with the example format!!**
3. Validate it yourself with validator.py
4. Push your submission to the git repo, and it will be pulled at the deadline of the competition, so make sure you are on time.

## Getting Started

1. "Use template" the repository, and make it private
2. Share it with (@matteohorvath)
3. Install the dependencies (pip install -r requirements)
4. Start building

## Overview

Welcome to the Package Delivery Algorithm Competition! This competition challenges participants to develop efficient algorithms for solving a complex package delivery optimization problem. Participants will create schedules for couriers to pick up, transport, and deliver packages across a 2D grid map containing warehouses, package points, and destinations.

## Problem Description

The problem involves optimizing the delivery of packages in a 2D grid map:

- **Map Structure**: An NxN grid where each location has (x, y) coordinates.
- **Locations**: Three types of locations on the map:
  - **Warehouses**: Where packages originate
  - **Package Points**: Intermediate locations with limited capacity for package exchanges
  - **Destinations**: Where packages need to be delivered
- **Couriers**: A fleet of N couriers, each with a capacity to carry M packages simultaneously.
- **Package Points**: Intermediate locations with limited storage capacity for package exchanges.
- **Packages**: Each package has an origin (warehouse), destination, and arrival time at the warehouse.

The goal is to minimize the total delivery time while ensuring all packages reach their destinations. Couriers can move one grid cell at a time (horizontally, vertically, or diagonally).

## Competition Format

### Input Data

Participants will receive JSON files containing:

- Map dimensions (N x N)
- Locations (warehouses, package points, destinations) with their coordinates
- Courier details (starting positions, capacities)
- Package information (origins, destinations, arrival times)

Example input format:

```json
{
  "map": {
    "dimensions": [10, 10],
    "locations": [
      {"id": "W1", "type": "warehouse", "coordinates": [1, 1]},
      {"id": "P1", "type": "package_point", "capacity": 5, "coordinates": [3, 4]},
      {"id": "D1", "type": "destination", "coordinates": [8, 7]}
    ]
  },
  "couriers": [
    {"id": "C1", "start_location": "W1", "capacity": 3},
    {"id": "C2", "start_location": "W1", "capacity": 3}
  ],
  "packages": [
    {"id": "P001", "origin": "W1", "destination": "D1", "arrival_time": 0},
    {"id": "P002", "origin": "W1", "destination": "D1", "arrival_time": 5}
  ]
}
```

### Output Format

Participants must submit a schedule of courier actions in JSON format:

```json
[
  {"time": 0, "courier": "C1", "action": "pick_up", "location": "W1", "packages": ["P001"]},
  {"time": 0, "courier": "C2", "action": "wait", "location": "W1", "packages": []},
  {"time": 1, "courier": "C1", "action": "move", "from": [1, 1], "to": [2, 2], "packages": ["P001"]},
  {"time": 5, "courier": "C2", "action": "pick_up", "location": "W1", "packages": ["P002"]},
  {"time": 10, "courier": "C1", "action": "drop_off", "location": "P1", "packages": ["P001"]},
  {"time": 15, "courier": "C1", "action": "move", "from": [3, 4], "to": [4, 5], "packages": []},
  {"time": 30, "courier": "C1", "action": "deliver", "location": "D1", "packages": ["P001"]}
]
```

### Scoring System

Submissions are scored based on:

- **Base Score**: The shortest time required to successfully deliver **all** packages (lower is better).
- **Penalties**:
  - +100 points per undelivered package
  - +10 points per invalid action

Final Score = Base Score + Penalties (lower is better)



## Tools

We provide several tools to help you develop and test your algorithms:

### 1. Input Generator

This tool generates large, random input files for the package delivery problem with configurable parameters.

#### Usage

```bash
# Generate a default input file (50x50 grid, 100 packages)
python generate_input.py

# Generate a large input file (100x100 grid, 500 packages)
python generate_input.py --size 100 --packages 500 --output large_input.json

# Generate an input file with specific parameters and print statistics
python generate_input.py --size 75 --warehouses 8 --package-points 15 --destinations 20 --couriers 30 --packages 200 --stats
```

#### Options

- `--size SIZE`: Size of the grid map (default: 50)
- `--warehouses N`: Number of warehouses (default: 5)
- `--package-points N`: Number of package points (default: 10)
- `--destinations N`: Number of destinations (default: 15)
- `--couriers N`: Number of couriers (default: 20)
- `--packages N`: Number of packages (default: 100)
- `--max-capacity N`: Maximum capacity of couriers (default: 5)
- `--max-pp-capacity N`: Maximum capacity of package points (default: 10)
- `--max-arrival-time N`: Maximum arrival time for packages (default: 50)
- `--output FILE`: Output file (default: generated_input.json)
- `--seed SEED`: Random seed for reproducibility
- `--stats`: Print statistics about the generated input

### 2. Problem Visualizer

This tool creates a graphical representation of the problem state, showing warehouses, package points, destinations, couriers, and packages on the 2D grid map.

#### Installation

```bash
# Install required dependencies
pip install -r requirements.txt
```

#### Usage

```bash
# Visualize a problem state and display it
python visualize_problem.py sample_input.json

# Visualize a problem state and save it to a file
python visualize_problem.py sample_input.json output.png
```

### 3. Solution Visualizer

This tool creates an animated visualization of your solution, showing the movement of couriers and packages over time.

#### Usage

```bash
# Visualize a solution and display the animation
python visualize_solution.py sample_input.json sample_output.json

# Visualize a solution and save it as an animated GIF
python visualize_solution.py sample_input.json sample_output.json --save solution.gif
```

### Visualization Features

The visualizations include:
- 2D grid map with locations colored by type (warehouses, package points, destinations)
- Package points sized according to their capacity
- Couriers positioned at their starting locations with capacity information
- Packages shown as paths from origin to destination with arrival times
- For the solution visualizer:
  - Animated movement of couriers across the grid
  - Color-coded courier actions (pick up, drop off, deliver, move, wait)
  - Package status tracking (at warehouse, with courier, at package point, delivered)
  - Delivery progress counter

These tools can help you:
- Generate test cases of varying complexity
- Understand the problem structure
- Verify your understanding of the input data
- Debug your solution by visualizing the problem state and courier movements
- Create diagrams and animations for documentation or presentations

## Resources

- [Detailed Problem Specification](docs/problem_spec.md)
- [Sample Test Cases](data/samples/)
- [Starter Kit](code/starter_kit/)
- [Submission Guidelines](docs/submission_guidelines.md)

Good luck to all participants!
