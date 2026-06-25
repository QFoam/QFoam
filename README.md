# QFoam

> **YATAIGA** — Your Quantum Research Assistant.
>
> Quantum simulation with natural language.

QFoam is an interactive [Streamlit](https://streamlit.io/) web app for building
and running quantum experiments. Instead of writing simulation code by hand, you
describe your quantum system step by step — species, system, Hamiltonian, pulses
and targets — using familiar physics notation (LaTeX bra–ket operators), and the
app assembles and time-evolves the system for you. Numerics are handled by the
[`rdquantum`](https://pypi.org/project/rdquantum/) library (built on
[QuTiP](https://qutip.org/)).

## Features

- 🧩 **Define quantum species** with named energy levels (e.g. `Rb` with levels `g e`).
- ⚛️ **Compose a quantum system** as a tensor product of species (e.g. `Rb Rb Cs`
  for `∣Rb⟩⊗∣Rb⟩⊗∣Cs⟩`).
- ⚡ **Build a Hamiltonian** from LaTeX operators such as
  `\ket{e}\bra{g} + \ket{g}\bra{e}`, with constants like `2\pi`.
- 🔦 **Shape control pulses** (`square`, `cos`, `sin`) with editable parameters.
- 🎯 **Target subsystems** by selecting which qubits/sites each operator acts on.
- 🌈 **Evolve and visualize** the population (amplitude) and phase of chosen
  states over time.

## How it works

The app walks you through five steps in the sidebar and main panel:

1. **Quantum Species** 👻 — add a species by name and its energy levels.
2. **Quantum System** ⚛️ — combine species into the full Hilbert space.
3. **Operator** 🤖 — add Hamiltonian terms using a label, a constant, and a
   bra–ket operator written in LaTeX.
4. **Pulse (MHz)** 🔦 — pick a pulse shape and parameters for each operator.
5. **Target Subsystem** 🎯 — choose which subsystems each operator targets.

After submitting, set an initial state, operation time, and number of samples to
run the experiment, then plot the amplitude and phase of selected target states.

## Project structure

```
QFoam/
├── app.py                    # Streamlit entry point
└── expt/
    ├── __init__.py
    ├── expt.py               # Expt class: the full experiment workflow/UI
    └── set_pulse/
        ├── __init__.py
        ├── set_pulse.py      # Pulse-parameter input widgets
        └── shape.py
```

## Requirements

- Python 3.x
- [streamlit](https://streamlit.io/)
- [rdquantum](https://pypi.org/project/rdquantum/) (provides `Quanta`, `QSystem`,
  `QSim`, and pulse shapes; uses [QuTiP](https://qutip.org/))
- [sympy](https://www.sympy.org/) with LaTeX parsing support
  (`antlr4-python3-runtime`)
- numpy
- matplotlib

## Installation

```bash
# Clone the repository
git clone https://github.com/QFoam/QFoam.git
cd QFoam

# (Recommended) create a virtual environment
python -m venv env
source env/bin/activate        # On Windows: env\Scripts\activate

# Install dependencies
pip install streamlit rdquantum sympy antlr4-python3-runtime numpy matplotlib
```

## Usage

Launch the app with Streamlit:

```bash
streamlit run app.py
```

This opens the YATAIGA interface in your browser. Walk through the steps above to
define your experiment, then collect and plot the state evolution.

### Example

1. **Species:** name `Rb`, energy levels `g e`.
2. **System:** `Rb` → `∣Rb⟩`.
3. **Operator:** label `\Omega`, constant `2\pi`,
   operator `\ket{e}\bra{g} + \ket{g}\bra{e}`.
4. **Pulse:** shape `square` with your chosen amplitude.
5. **Target:** select the subsystem to drive.
6. **Run:** initial state `0` (i.e. `∣g⟩`), set an operation time and number of
   samples, then plot the amplitude/phase of `\ket{g}` and `\ket{e}`.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
