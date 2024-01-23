import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import qutip as qt

from rdquantum.qsim import QSim

class CZGate():
    def __init__(
        self
    ):
        self.num_atoms = 2
        self.num_levels = 4
        self.map_levels = {
            '0': int(0),
            '1': int(1),
            'p': int(2),
            'r': int(3),
        }
        self.num_samples = 100
        self.control_operators = {
			'Omega_p': {
				'higher_level': 'p', 
				'lower_level': '1',
				'target_qubit': [0,1],
				'constant': 3.14,
				'pulse_shape': 'Square',
				# 'pulse_shape': 'SuperGaussian',
				# 'pulse_shape': 'SquarePhase',
				'Hermitian_conjugate': True
			},
			'Omega_r': {
				'higher_level': 'r', 
				'lower_level': 'p',
				'target_qubit': [0,1],
				'constant': 3.14,
				'pulse_shape': 'Square',
				'Hermitian_conjugate': True
			},
			'Delta_p': {
				'higher_level': 'p', 
				'lower_level': 'p',
				'target_qubit': [0,1],
				'constant': 2 * 3.14,
				'pulse_shape': 'Square',
				'Hermitian_conjugate': False
			}
        }
        self.interaction_operators = {
			'Brr': {
				'qubit1_higher_level': 'r', 
				'qubit1_lower_level': 'r', 
				'qubit2_higher_level': 'r',
				'qubit2_lower_level': 'r',
				'target_qubits_pair': [[0,1]],
				'constant': 2 * 3.14,
				'pulse_shape': 'Square',
				'Hermitian_conjugate': False
			}
		}
        self.pulse_params = {
            'Omega_p': {
                'tune': [False],
                'param_value': [400.0]
            },
            'Omega_r': {
                'tune': [False],
                'param_value': [500.0],
                'phase': False
            },
            'Delta_p': {
                'tune': [False],
                'param_value': [-2000.],
                'phase': False
            },
            'Brr': {
                'tune': [False],
                'param_value': [500],
                'phase': False
            },
            'T_gate': {
                'tune': [False],
                'param_value': [0.54]
            }
        }
        self.num_control_ops = 3
        self.control_keys = ['Omega_p', 'Omega_r', 'Delta_p']
        self.num_interaction_ops = 1
        self.interaction_keys = ['Brr']

    def sidebar(
        self
    ):
        with st.form("init_param"):
            st.write("Number of atoms: ", self.num_atoms)
            
            # Energy Levels
            with st.container(border=True):
                st.write("Number of energy levels: ", self.num_levels)
                st.write(self.map_levels)

            # Control Operators
            with st.container(border=True):
                st.write("Number of control pulses: ", len(self.control_keys))
                st.write(self.control_keys)

            # Interaction Operators
            with st.container(border=True):
                st.write("Number of interaction: ", len(self.interaction_keys))
                st.write(self.interaction_keys)

            submitted = st.form_submit_button("Generate Experiment")

    def quantum_system(
        self
    ):
        with st.form("pulse_param"):
            col1, col2, col3 = st.columns(3)
            with col1:
                # Control Operators
                for key in self.control_keys:
                    with st.expander("Control pulse %s:" %key):
                        control_operator = self.control_operators[key]
                        control_operator['higher_level'] = st.selectbox(
                            'The higher level of control pulse %s:' %key,
                            options = (key for key in self.map_levels),
                            index = self.map_levels[control_operator['higher_level']]
                        )
                        control_operator['lower_level']= st.selectbox(
                            'The lower level of control pulse %s:' %key,
                            options = (key for key in self.map_levels),
                            index = self.map_levels[control_operator['lower_level']]
                        )
                        st.write("Target Qubit")
                        target_qubit = []
                        for i_atoms in range(self.num_atoms):
                            checked = st.checkbox(
                                'Qubit %s' %i_atoms,
                                key = key + 'tar' + str(i_atoms),
                                value=True
                            )
                            if checked:
                                target_qubit.append(i_atoms)
                        control_operator['target_qubit'] = target_qubit
                        control_operator['constant'] = st.number_input(
                            "Constant value of control pulse %s:" %key,
                            value = control_operator['constant']
                        )
                        control_operator['pulse_shape'] = st.selectbox(
                            "The pulse shape of control pulse %s:" %key,
                            ('Square', ''),
                        )
                        control_operator['Hermitian_conjugate'] = st.checkbox(
                            'Hermitian conjugate',
                            key = key + 'hc' + str(i_atoms),
                            value = control_operator['Hermitian_conjugate']
                        )
                        self.control_operators[key] = control_operator

            with col2:
                # Interaction Operators
                for key in self.interaction_keys:
                    with st.expander("Interactions %s:" %key):
                        interaction_operator = self.interaction_operators[key]
                        interaction_operator['qubit1_higher_level'] = st.selectbox(
                            'The qubit1 higher energy level of interaction %s:' %key,
                            options = (key for key in self.map_levels),
                            index = self.map_levels[interaction_operator['qubit1_higher_level']]
                        )
                        interaction_operator['qubit1_lower_level'] = st.selectbox(
                            'The qubit1 lower energy level of interaction %s:' %key,
                            options = (key for key in self.map_levels),
                            index = self.map_levels[interaction_operator['qubit1_lower_level']]
                        )
                        interaction_operator['qubit2_higher_level'] = st.selectbox(
                            'The qubit2 higher energy level of interaction %s:' %key,
                            options = (key for key in self.map_levels),
                            index = self.map_levels[interaction_operator['qubit2_higher_level']]
                        )
                        interaction_operator['qubit2_lower_level'] = st.selectbox(
                            'The qubit2 lower energy level of interaction %s:' %key,
                            options = (key for key in self.map_levels),
                            index = self.map_levels[interaction_operator['qubit2_lower_level']]
                        )
                        st.write("Target Qubits Pair")
                        target_qubits_pair = []
                        for i_atom1 in range(self.num_atoms):
                            for i_atom2 in range(i_atom1+1, self.num_atoms):
                                checked = st.checkbox(
                                    'Qubits pair [%s,%s]' %(i_atom1,i_atom2),
                                    key = key + 'tar' + str(i_atom1) + str(i_atom2),
                                    value = True
                                )
                                if checked:
                                    target_qubits_pair.append([i_atom1, i_atom2])
                        interaction_operator['target_qubits_pair'] = target_qubits_pair
                        interaction_operator['constant'] = st.number_input(
                            "Constant value of interaction %s:" %key,
                            value = interaction_operator['constant']
                        )
                        interaction_operator['pulse_shape'] = st.selectbox(
                            "The pulse shape of interaction %s:" %key,
                            ('Square', ''),
                        )
                        interaction_operator['Hermitian_conjugate'] = st.checkbox(
                            'Hermitian conjugate',
                            key = key + 'hc' + str(i_atom1) + str(i_atom2),
                            value = interaction_operator['Hermitian_conjugate']
                        )

            with col3:
                with st.container(border=True):
                    for key in self.pulse_params:
                        param_value = st.number_input(
                            '%s param_value' %(key),
                            value = self.pulse_params[key]['param_value'][0], 
                            key = key
                        )
                        self.pulse_params[key]['param_value'] = [param_value]
                        self.pulse_params[key]['tune'] = [False]

            submitted = st.form_submit_button("Generate Parameters")

            if submitted:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("control_operators", self.control_operators)
                with col2:
                    st.write("interaction_operators", self.interaction_operators)
                with col3: 
                    st.write("pulse_params", self.pulse_params)

    def population_evolution(
        self
    ):
        with st.form("run"):
            Had = np.zeros((self.num_levels, self.num_levels))
            Had[0][0] = 1
            Had[0][1] = 1
            Had[1][0] = 1
            Had[1][1] = -1

            I = qt.qeye(self.num_levels)
            Had = qt.Qobj(Had/np.sqrt(2))

            ket00 = qt.tensor(qt.basis(self.num_levels,0), qt.basis(self.num_levels,0))
            ket01 = qt.tensor(qt.basis(self.num_levels,0), qt.basis(self.num_levels,1))
            ket10 = qt.tensor(qt.basis(self.num_levels,1), qt.basis(self.num_levels,0))
            ket11 = qt.tensor(qt.basis(self.num_levels,1), qt.basis(self.num_levels,1))

            self.rho_init = qt.tensor(Had, Had) * ket01

            submitted = st.form_submit_button("Run")
            if submitted:
                model = QSim(
                    self.num_atoms,
                    self.num_levels,
                    self.map_levels,
                    self.num_samples,
                    self.control_operators,
                    self.interaction_operators,
                    self.pulse_params
                )
                
                model.update_params(self.pulse_params)
                rho_init, rho_target, results = model.run_simulation(
                    state_init=self.rho_init,
                    state_target=[qt.ket2dm(self.rho_init)],
                    pulse_params = self.pulse_params,
                    options=qt.Options(nsteps=15000, atol=1e-13, rtol=1e-13, rhs_reuse=False)
                )
                col1, col2 = st.columns(2)
                with col1:
                    times = np.linspace(0.0, self.pulse_params['T_gate']['param_value'][0], self.num_samples)
                    fig, ax = plt.subplots()
                    ax.plot(times, np.log10(results.expect[0]))
                    ax.set_xlabel('Time' r'$(\mu s)$')
                    ax.set_ylabel(r'$log_{10}$' '(population)')
                    ax.set_ylim(-6, 1)
                    st.pyplot(fig)
                with col2:
                    st.write(results.expect)

    def optimization(
        self
    ):
        pass
