
# Worstcase Attacker Framework

This repository contains the implementation of the cyber-physical integrated worst-case cyberattack framework in industial cyber-physical systems. 
The framework integrates attack graph models (representing the cyber system) with the linear time-invariant state-space model (representing the physical system dynamics) to evaluate the physical impact of attacks and identify critical vulnerabilities on the cyber system.
The cyber-to-physical impact of a cyberattack is quantified by MTTF of the physical process using its degradation signal.
For more details of this framework refer to our paper ``An Integrated Cyber-Physical Framework for Worst-Case Attacks in Industrial Control Systems."
Figure below shows the overall worst-case attack framework.

<p align=center>
    <img src="../main/img/fw.png" width="600"/>
</p>

## Features
- **Worst-case Attack Model:** Tools for generating the cyberattacks with highest physical impact on.
- **Simulation:** Simulates the behavior of the physical system under various attack scenarios.
- **Cyber-Physical Integration:** Evaluate the advantage of the holistic view of the ICS versus looking at the cyber and physical systems of an ICS separately.
- **Sensitivity Analysis:** Analyze the sensitivity of the attack stealthiness on the detection power of the ICS.

## Repository Structure
```
Worstcase_Attacker/
├── case_attack_graph.py          # Main script for for generating the attack graph for the case study on BWPP
├── sensitivity_analysis.py       # Sensitivity analysis implementation
├── solve_cyber.py                # Solving for the worst-case attack only looking at the cyber-system
├── solve_disjoint.py             # Solving for worst-case attack on the physical system considering the access gained from solve_cyber.py 
├── solve_physical.py             # Solving for the worst-case attack only looking at the physical-system ([Biehler et al.](https://www.tandfonline.com/doi/abs/10.1080/24725854.2023.2184004))
├── solve_scenario.py             # Solving for the worst-case attack on a pre-determined attack scenario ([Huang et al.](https://ieeexplore.ieee.org/abstract/document/8270567))
├── model/                        # Main implementation of our framework and other experiments
├── simulation/                   # Simulation script
├── data/                         # Data for case study on BWPP and random scenarios
├── plots.ipynb                   # Notebook for plotting results included in the paper
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
