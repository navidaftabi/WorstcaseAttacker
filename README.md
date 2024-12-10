
# Worstcase Attacker Framework

This repository contains the implementation of ``[An Integrated Cyber-Physical Framework for Worst-Case Attacks in Industrial Control Systems](https://doi.org/10.1080/24725854.2024.2439856)". 
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
├── sensitivity_analysis.py       # Sensitivity analysis implementation
├── solve_cyber.py                # Solving for the worst-case attack only looking at the cyber-system
├── solve_disjoint.py             # Solving for worst-case attack on the physical system considering the access gained from solve_cyber.py 
├── solve_physical.py             # Solving for the worst-case attack only looking at the physical-system 
├── solve_scenario.py             # Solving for the worst-case attack on a pre-determined attack scenario 
├── solve_wa.py                   # Solves for the worst-case attack on numerical and case studies
├── model/                        # Main implementation of our framework and other experiments
├── simulation/                   # Simulation script
├── data/                         # Data for case study on BWPP and random scenarios
├── plots.ipynb                   # Notebook for plotting results included in the paper
```
## Setup and Installation
1. **Install Gurobi**:
    This framework uses Gurobi Optimizer for solving optimization problems. To use Gurobi, you need to:
    - Obtain a Gurobi license (free for academic use).
    - Install Gurobi and Python package.

    For detailed installation instructions, please visit the [Gurobi website](https://www.gurobi.com).
2. Clone this repository:
    ```bash
    git clone https://github.com/navidaftabi/WorstcaseAttacker.git
    cd WorstcaseAttacker
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
To reproduce our results follow the following steps:
1. Run `python solve_wa.py --experiment random` to solve for the worst-case attack across three types of numerical scenarion. Use `--generate` to create new random attack graphs; otherwise, the default graphs from the paper are used.

2. Run `python solve_wa.py --experiment case` to solve for the worst-case attack the BWPP case study. Use `--generate` to create attack graph from `data/case/graph.txt`.

3. Run `python sensitivity_analysis.py` to generate results of the sensitivity analysis.

4. Run `python solve_cyber.py`, and then `python solve_disjoint.py` to solve for the worst-case attack with disjoint look.

5. Run `python solve_physical.py` ([Biehler et al.](https://www.tandfonline.com/doi/abs/10.1080/24725854.2023.2184004)), and then `python solve_scenario.py` ([Huang et al.](https://ieeexplore.ieee.org/abstract/document/8270567)) to generate the results for the comparative experiment.
    
6. Open `plots.ipynb` to visualize the results.

## Data
- **case/**: Contains data specific to a case study on BWPP ([Huang et al.](https://ieeexplore.ieee.org/abstract/document/8270567)).
- **random/**: Includes randomly generated data for experimentation.

## Cite Our Paper

If you use this code or framework in your research, please cite our paper:

> **An Integrated Cyber-Physical Framework for Worst-Case Attacks in Industrial Control Systems**  
> Navid Aftabi, Dan Li, and Thomas C. Sharkey  
> ISE Transactions, 1–26, 2024 
> [Link to the Paper](https://doi.org/10.1080/24725854.2024.2439856)

### BibTeX
```bibtex
@article{Aftabi09122024,
    author = {Navid Aftabi, Dan Li and Thomas C. Sharkey},
    title = {An Integrated Cyber-Physical Framework for Worst-Case Attacks in Industrial Control Systems},
    journal = {IISE Transactions},
    volume = {0},
    number = {ja},
    pages = {1--26},
    year = {2024},
    publisher = {Taylor \& Francis},
    doi = {10.1080/24725854.2024.2439856},
    URL = {https://doi.org/10.1080/24725854.2024.2439856},
    eprint = {https://doi.org/10.1080/24725854.2024.2439856}
}

