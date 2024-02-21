import re
from sympy import sympify
from sympy.parsing.latex import parse_latex
import itertools
import numpy as np
import matplotlib.pyplot as plt

import streamlit as st

import rdquantum as rdq

from . import set_pulse

class Expt:
    """ A quantum experiment.

    """
    def __init__(
        self
    ):
        self.qspecies = {}
        self.qsystem = None
        self.qsystem_keys = []
        self.hamiltonian = {}
        self.hamiltonian_latex = {}
        self.qsim = None
        self.state_evo = None

    def set_qspecies(
        self
    ):
        """ Set the quantum species. """
        with st.container(border=True):
            st.write(':red[Step 1] - Quantum Species 👻')
            with st.form("add_qspecies", clear_on_submit=True, border=False):
                col1, col2 = st.columns([1,2])
                with col1:
                    species_name = st.text_input(
                        label='name', 
                        placeholder='Rb'
                    )
                with col2:
                    species_energy_levels = st.text_input(
                        label='energy levels', 
                        placeholder='g e for energy level g and e.'
                    )
                submitted = st.form_submit_button("Add")
                if submitted:
                    species_energy_levels = species_energy_levels.split(" ")
                    self.qspecies[species_name] = rdq.Quanta(species_name, species_energy_levels)

            for key in self.qspecies.keys():
                name = self.qspecies[key].name
                energy_levels = self.qspecies[key].energy_levels
                st.write("%s: %s" %(name, energy_levels))

    def set_qsystem(
        self
    ):
        """ Create your quantum system. """
        with st.form("set_qsystem", clear_on_submit=True):
            st.write(':orange[Step 2] - Quantum System ⚛️')
            _qsystem_keys = st.text_input(
                label='quantum system', 
                placeholder='Rb Rb Cs for ∣Rb⟩⊗∣Rb⟩⊗∣Cs⟩'
            )
            submitted = st.form_submit_button("Create")
            if submitted:
                qsystem = []
                _qsystem_keys = _qsystem_keys.split(" ")
                for _qsystem_key in _qsystem_keys:
                    if _qsystem_key not in self.qspecies.keys():
                        raise ValueError("Species `%s` does not exist." %(_qsystem_key))
                    else:
                        self.qsystem_keys.append(_qsystem_key)
                        qsystem.append(self.qspecies[_qsystem_key])
                self.qsystem = rdq.QSystem(qsystem)
                self.qsystem_keys = self.qsystem.info
            st.write('∣', *self.qsystem_keys, '⟩')

    def _temp_hamiltonian_subdmop_helper(
        self,
        operator: str
    ):
        dm = []
        subdm = []
        subop = []

        operators = re.split(r'\s*([+\-*/])\s*', operator)
        for _operator in operators:
            if _operator.strip() in ['+', '-', '*', '/']:
                subop.append(_operator.strip())
            else:
                dm.append(_operator.strip())

        for _subdm in dm:
            _subdm = re.findall(r'\\([^{]+){([^}]+)}', _subdm.strip())
            if _subdm[0][0] == "ket" and _subdm[1][0] == "bra":
                subdm.append((_subdm[0][1], _subdm[1][1]))
            else:
                raise ValueError("Not a valid operator.")

        return subdm, subop


    def _temp_hamiltonian_constant_helper(
        self,
        constant: str
    ):
        _constant = sympify(str(parse_latex(constant)))
        if _constant.is_real:
            constant = float(_constant.evalf())
        else:
            constant = complex(_constant.evalf())
        return constant

    def _temp_hamiltonian_target_helper(
        self,
        key
    ):
        # Check the number of targets.
        num_target = len(self.hamiltonian[key]["dm"]["subdm"][0][0])
        # Check op target species.
        # Find valid target subsystem.
        qsystem_list = list(range(len(self.qsystem_keys)))
        target = [list(comb) for comb in itertools.combinations(qsystem_list, num_target)]
        return target

    def set_hamiltonian(
        self
    ):
        with st.container(border=True):
            st.subheader("Hamiltonian ⚡")
            with st.form("set_H", clear_on_submit=True):
                st.write(':green[Step 3] - Operator 🤖')
                col1, col2, col3 = st.columns((1, 1, 2))
                with col1:
                    _label = st.text_input(
                        label='pulse label',
                        placeholder='\Omega'
                    )
                with col2:
                    _constant = st.text_input(
                        label='constant',
                        placeholder='2\pi'
                    )
                with col3:
                    _operator = st.text_input(
                        label='operator',
                        placeholder='\ket{e}\bra{g} + \ket{g}\bra{e}'
                    )

                submitted = st.form_submit_button("Add")
                if submitted:
                    constant = self._temp_hamiltonian_constant_helper(_constant)
                    subdm, subop = self._temp_hamiltonian_subdmop_helper(_operator) 
                    self.hamiltonian[_label] = {}
                    self.hamiltonian[_label]["dm"] = {
                        "constant": constant,
                        "subdm": subdm,
                        "subop": subop
                    }
                    self.hamiltonian_latex[_label] = '$%s\ %s\ (%s)$' %(_label, _constant, _operator)
            with st.container(border=True):
                st.write(':blue[Step 4] - Pulse (MHz) 🔦')
                for key in self.hamiltonian.keys():
                    col1, col2 = st.columns((1, 3))
                    with col1:
                        _pulse_shape = st.selectbox(
                            label=str('Shape of $\ %s$' %(key)),
                            options=('square', 'cos', 'sin')
                        )
                    with col2:
                        _pulse_args = set_pulse.pulse_params(key, _pulse_shape)
                    self.hamiltonian[key]['pulse'] = {}
                    self.hamiltonian[key]['pulse']["shape"] = _pulse_shape
                    self.hamiltonian[key]['pulse']["kwargs"] = _pulse_args
                    _constant = 1.0
                    _phase = 1.0
                    self.hamiltonian[key]['pulse']["constant"] = _constant
                    self.hamiltonian[key]['pulse']["phase"] = _phase

            with st.container(border=True):
                st.write(':violet[Step 5] - Target Subsystem 🎯')
                _delete = []
                for key in self.hamiltonian.keys():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button('Delete', key=key):
                            _delete.append(key)
                    with col2:
                        st.write(self.hamiltonian_latex[key])
                    with col3:
                        _selected_targets = []
                        targets = self._temp_hamiltonian_target_helper(key)
                        for _target in targets:
                            selected = st.checkbox(
                                label = str(_target),
                                key = key + str(_target)
                            )
                            if selected:
                                _selected_targets.append(_target)
                    self.hamiltonian[key]["target"] = _selected_targets
                for key in _delete:
                    del self.hamiltonian[key]

            if st.button("Submit"):
                self.qsim = rdq.QSim(self.qsystem)
                for key in self.hamiltonian.keys():
                    self.qsim.add_operator(
                        key = key,
                        target = self.hamiltonian[key]["target"],
                        pulse_info = self.hamiltonian[key]["pulse"],
                        dm_info = self.hamiltonian[key]["dm"]
                    )

        # Debug
        if self.qsim is not None:
            for key in self.qsim.hamiltonian.operators:
                st.write(key, self.qsim.hamiltonian.operators[key].dm)

    def popevo(
        self
    ):
        col1, col2, col3 = st.columns(3)
        # Enter initial state
        with col1:
            init_state = st.text_input(
                label = 'initial state',
                placeholder = '00 for ∣00⟩'
            )
        # Set operation time, number of samples and qutip.solver.Options
        with col2:
            operation_time = st.number_input(
                label = 'operation time ($\mu$s)',
                value = 10
            )
        with col3:
            num_samples = st.number_input(
                label = 'number of samples',
                value = 100
            )
        
        if st.button("set"):
            self.state_evo = self.qsim.run_expt(
                init_state = self.qsystem.generate_state(init_state),
                operation_time = operation_time,
                num_samples = num_samples
            )
            st.write(":green[You are all set!👍👍👍]")
            # Debug
            # st.write(state_evo)

        with st.container(border=True):
            st.write(':rainbow[State Evolution] 🌈')
            _target_states = st.text_input(
                label='States',
                placeholder = 'hint: "\ket{ge}, \ket{eg}" for state ∣ge⟩ and ∣eg⟩.'
            )
            target_states = []
            _target_states = re.findall(r'\\([^{]+){([^}]+)}', _target_states.strip())
            for _target_state in _target_states:
                if _target_state[0] == "ket":
                    target_states.append(self.qsystem.generate_state(_target_state[1]))

            if st.button('run'):
                amp = []
                phase = []
                for i in range(len(self.state_evo)):
                    state = self.state_evo[i]
                    amp.append(np.abs([s.dag().overlap(state) for s in target_states]))
                    phase.append(np.angle([s.dag().overlap(state) for s in target_states])/np.pi)
                times = np.linspace(0.0, operation_time, num_samples)

                col1, col2 = st.columns(2)
                with col1:
                    st.write('Amplitude')
                    fig, ax = plt.subplots()
                    for index in range(len(target_states)):
                        ax.plot(times, [x[index] for x in amp])
                    ax.set_xlabel('Time' r'$(\mu s)$')
                    ax.set_ylabel('Amplitude')
                    ax.legend(_target_states)
                    st.pyplot(fig)
                    st.write(amp)

                with col2:
                    st.write('Phase')
                    fig, ax = plt.subplots()
                    for index in range(len(target_states)):
                        ax.plot(times, [x[index] for x in phase])
                    ax.set_xlabel('Time' r'$(\mu s)$')
                    ax.set_ylabel('Arg/' r'$\pi$')
                    ax.legend(_target_states)
                    st.pyplot(fig)
                    st.write(phase)
