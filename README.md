A secure and efficient cash transportation management system designed to optimize routes, manage vehicle capacities, and ensure timely deliveries.

## Features

- Real-time tracking of cash pickups and deliveries
- Secure authentication and authorization
- Route optimization for efficient deliveries
- Detailed transaction history and reporting
- Mobile-friendly interface

## Getting Started

### Prerequisites

- Python 3.12
- Requirements.txt

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cash-pickup-delivery.git
   ```
2. Navigate to the project directory:
   ```bash
   cd cash-pickup-delivery
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

The system uses a configuration file located at `input_files/parameters.csv` to set various parameters for the algorithm:

- **File Paths:**
  - `input_file_path`: Path to input files.
  - `output_file_path`: Path to output files.

- **Algorithm Parameters:**
  - `MAX_ITERATIONS`: Maximum number of iterations for the algorithm.
  - `MAX_TIME`: Maximum time allowed for the algorithm to run.
  - `ALGORITHM_OPTION`: Option to choose between different algorithm strategies.
  - `MAX_STOCK`: Maximum stock capacity.
  - `VEHICLE_CAPACITY`: Capacity of each vehicle.
  - `MAX_DISTANCE`: Maximum distance a vehicle can travel.
  - `USE_ALL_FLEET`: Boolean to decide if the entire fleet should be used.
  - `n_vehicles`: Number of vehicles available.

### Algorithm Overview

The algorithm is implemented in `src/algorithm/Algorithm.py` and `src/algorithm/Solution.py`. It consists of the following key components:

- **Algorithm Class:**
  - Initializes with a context and instance.
  - Executes the algorithm by constructing and improving solutions.
  - Maintains a list of solutions and tracks the best solution based on fitness.

- **Solution Class:**
  - Initializes with a context and instance, setting up routes and capacities.
  - Uses a greedy approach to solve the cash pickup and delivery problem.
  - Evaluates feasible nodes for each vehicle, considering capacity, distance, and stock constraints.
  - Calculates the fitness of each solution based on total distance, storage cost, and unserved nodes.

### Usage

#### Main Execution Script

The main execution is handled by the `src/main.py` script. This script is responsible for setting up the problem context, initializing the algorithm, and processing the results. Below is a brief overview of its components:

- **ASCII Logo**: The script begins by printing an ASCII art logo for visual appeal.
  
- **Execution Function**: 
  - Initializes the problem context and logs the parameters.
  - Creates an instance of the problem to be solved.
  - Initializes and executes the algorithm, logging the process.
  - Processes and stores the results of the algorithm.
  - Measures and logs the total execution time.

To run the algorithm, execute the following command:
```bash
python src/main.py
```