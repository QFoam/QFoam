import re
from sympy import sympify
from sympy.parsing.latex import parse_latex
import itertools

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
        self.qsim = None

    def set_qspecies(
        self
    ):
        """ Set the quantum species. """
        with st.container(border=True):
            st.write(':red[Step 1] - Add quantum specie👻')
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
                submitted = st.form_submit_button("Add Species")
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
            st.write(':orange[Step 2] - Create quantum system⚛️')
            _qsystem_keys = st.text_input(
                label='quantum system', 
                placeholder='Rb Rb Cs for ∣Rb⟩⊗∣Rb⟩⊗∣Cs⟩'
            )
            submitted = st.form_submit_button("Submit")
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
            with st.form("set_H", clear_on_submit=True):
                st.write(':green[Step 3] - Enter your Hamiltonian:')
                col1, col2, col3 = st.columns((1, 1, 2))
                with col1:
                    _label = st.text_input(
                        label='label',
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

            _delete = []
            _selected_targets = []
            for key in self.hamiltonian.keys():
                col1, col2, col3 = st.columns((1, 2, 1))
                with col1:
                    st.write("$%s$" %(key))
                with col2:
                    targets = self._temp_hamiltonian_target_helper(key)
                    for _target in targets:
                        selected = st.checkbox(
                            label = str(_target),
                        )
                        if selected:
                            _selected_targets.append(_target)
                with col3:
                    if st.button('Delete', key=key):
                        _delete.append(key)
                self.hamiltonian[key]["target"] = _selected_targets
            for key in _delete:
                del self.hamiltonian[key]

            with st.container(border=True):
                st.write(':blue[Step 4] - Enter pulse parameters:')
                for key in self.hamiltonian.keys():
                    col1, col2 = st.columns((1, 3))
                    with col1:
                        _pulse_shape = st.selectbox(
                            label=str('Shape of $\ %s$' %(key)),
                            options=('cos', 'sin', 'square')
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
                
                for key in self.hamiltonian.keys():
                    st.write('$%s$: '%(key), self.hamiltonian[key])

                if st.button("Submit"):
                    self.qsim = rdq.QSim(self.qsystem)
                    for key in self.hamiltonian.keys():
                        qsim.add_oprator(
                            key = key,
                            target = self.hamiltonian[key]["target"],
                            pulse_info = self.hamiltonian[key]["pulse"],
                            dm_info = self.hamiltonian[key]["dm"]
                        )
