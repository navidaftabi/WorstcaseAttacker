
# Worstcase Attacker Framework

This repository contains the implementation of a framework for simulating and analyzing worst-case attack scenarios in cyber-physical systems. The framework integrates attack graph models with physical system dynamics to evaluate the impact of attacks and identify vulnerabilities.

## Features
- **Attack Graph Models:** Tools for generating and solving attack graph-based scenarios.
- **Simulation:** Simulates the behavior of the physical system under various attack scenarios.
- **Sensitivity Analysis:** Evaluate the robustness of the system to parameter variations.
- **Data and Visualization:** Includes pre-generated data and scripts for creating insightful plots.

## Repository Structure
```
Worstcase_Attacker/
├── case_attack_graph.py          # Main script for case-specific attack graph analysis
├── sensitivity_analysis.py       # Sensitivity analysis implementation
├── solve_cyber.py                # Cyber-layer solutions
├── solve_physical.py             # Physical-layer solutions
├── model/                        # Models for the attack graph and physical system
├── simulation/                   # Simulation scripts
├── data/                         # Data for case and random scenarios
├── plots.ipynb                   # Notebook for plotting results
```
## Setup and Installation
1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/Worstcase_Attacker.git
    cd Worstcase_Attacker
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. Run the scripts for generating results, e.g.:
    ```bash
    python case_attack_graph.py
    ```
2. Open `plots.ipynb` to visualize the results.

## Data
- **case/**: Contains data specific to a predefined case study.
- **random/**: Includes randomly generated data for experimentation.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
This project was developed as part of research on cyber-physical system security. For questions, please contact the authors.
