import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import qutip as qt

from rdquantum.qsim import QSim

class YourExpt():
    def __init__(
        self
    ):
        self.num_atoms = 2
        self.num_levels = 2 
        self.map_levels = {}
        self.num_samples = 1000
        self.control_operators = {}
        self.interaction_operators = {}
        self.pulse_params = {
        }
        self.num_control_ops = 0
        self.control_keys = []
        self.num_interaction_ops = 0
        self.interaction_keys = []

    def sidebar(
        self
    ):
        with st.form("init_param"):
            self.num_atoms = st.number_input(
                "Number of atoms:",
                value=2,
                min_value=1,
                max_value=3
            )
            self.num_samples = st.number_input(
                "Number of samples:",
                value=100,
                min_value=100,
                max_value=10000
            )
            
            # Energy Levels
            with st.container(border=True):
                self.num_levels = st.number_input(
                    "Number of energy levels:",
                    value=2,
                    min_value=2,
                    max_value=5
                )

                keys = np.zeros(self.num_levels, dtype=str)
                for i_levels in range(self.num_levels): 
                    key = st.text_input(
                        'The symbol of energy level %s:' % i_levels,
                        value = str(i_levels),
                        max_chars = 1
                    )
                    keys[i_levels] = key
                self.map_levels = {}
                for i_key in range(len(keys)):
                    self.map_levels[keys[i_key]] = int(i_key)
            # st.write(self.map_levels)

            # Control Operators
            with st.container(border=True):
                self.num_control_ops = st.number_input(
                    "Number of control pulses:",
                    value=1,
                    min_value=1,
                    max_value=5
                )
                self.control_keys = []
                for i_contro_ops in range(self.num_control_ops):
                    key = st.text_input(
                        'The symbol of control pulse %s:' %i_contro_ops,
                        value = 'control%s' %i_contro_ops
                    )
                    self.control_keys.append(key)

            # Interaction Operators
            with st.container(border=True):
                self.num_interaction_ops = st.number_input(
                    "Number of interaction:",
                    value=1,
                    min_value=0,
                    max_value=5
                )
                self.interaction_keys = []
                for i_interaction_ops in range(self.num_interaction_ops):
                    key = st.text_input(
                        'The symbol of interaction %s:' %i_interaction_ops,
                        value = 'interaction%s' %i_interaction_ops
                    )
                    self.interaction_keys.append(key)

            submitted = st.form_submit_button("Generate Experiment")

            if submitted:
                # Pulse Parameters
                self.pulse_params = {
                    'T_gate': {}
                }
                for key in self.control_operators:
                    self.pulse_params[key] = {}
                for key in self.interaction_operators:
                    self.pulse_params[key] = {}
                st.write('pulse_params', self.pulse_params)

    def quantum_system(
        self
    ):
        with st.form("pulse_param"):
            col1, col2, col3 = st.columns(3)
            with col1:
                # Control Operators
                self.control_operators = {}
                for i_contro_ops in range(self.num_control_ops):
                    key = self.control_keys[i_contro_ops]
                    with st.expander("Control pulse %s:" %key):
                        self.control_operators[key] = {}
                        self.control_operators[key]['higher_level'] = st.selectbox(
                            'The higher level of control pulse %s:' %i_contro_ops,
                            (key for key in self.map_levels),
                        )
                        self.control_operators[key]['lower_level']= st.selectbox(
                            'The lower level of control pulse %s:' %i_contro_ops,
                            (key for key in self.map_levels),
                        )
                        st.write("Target Qubit")
                        target_qubit = []
                        for i_atoms in range(self.num_atoms):
                            checked = st.checkbox(
                                'Qubit %s' %i_atoms,
                                key = 10*i_contro_ops + i_atoms
                            )
                            if checked:
                                target_qubit.append(i_atoms)
                        self.control_operators[key]['target_qubit'] = target_qubit
                        self.control_operators[key]['constant'] = st.number_input(
                            "Constant value of control pulse %s:" %i_contro_ops,
                            value=1.0
                        )
                        self.control_operators[key]['pulse_shape'] = st.selectbox(
                            "The pulse shape of control pulse %s:" %i_contro_ops,
                            ('Square', ''),
                        )
                        self.control_operators[key]['Hermitian_conjugate'] = st.checkbox(
                            'Hermitian conjugate',
                            key = 100 + 10*i_contro_ops + i_atoms
                        )

            with col2:
                # Interaction Operators
                self.interaction_operators = {}
                for i_interaction_ops in range(self.num_interaction_ops):
                    key = self.interaction_keys[i_interaction_ops]
                    with st.expander("Interactions %s:" %key):
                        self.interaction_operators[key] = {}
                        self.interaction_operators[key]['qubit1_higher_level'] = st.selectbox(
                            'The qubit1 higher energy level of interaction %s:' %i_interaction_ops,
                            (key for key in self.map_levels),
                        )
                        self.interaction_operators[key]['qubit1_lower_level'] = st.selectbox(
                            'The qubit1 lower energy level of interaction %s:' %i_interaction_ops,
                            (key for key in self.map_levels),
                        )
                        self.interaction_operators[key]['qubit2_higher_level']= st.selectbox(
                            'The qubit2 higher energy level of interaction %s:' %i_interaction_ops,
                            (key for key in self.map_levels),
                        )
                        self.interaction_operators[key]['qubit2_lower_level']= st.selectbox(
                            'The qubit2 lower energy level of interaction %s:' %i_interaction_ops,
                            (key for key in self.map_levels),
                        )
                        st.write("Target Qubits Pair")
                        target_qubits_pair = []
                        for i_atom1 in range(self.num_atoms):
                            for i_atom2 in range(i_atom1+1, self.num_atoms):
                                checked = st.checkbox(
                                    'Qubits pair [%s,%s]' %(i_atom1,i_atom2),
                                    key = 10*i_interaction_ops + i_atom1 + 0.1*i_atom2
                                )
                                if checked:
                                    target_qubits_pair.append([i_atom1, i_atom2])
                        self.interaction_operators[key]['target_qubits_pair'] = target_qubits_pair
                        self.interaction_operators[key]['constant'] = st.number_input(
                            "Constant value of interaction %s:" %i_interaction_ops,
                            value=1.0
                        )
                        self.interaction_operators[key]['pulse_shape'] = st.selectbox(
                            "The pulse shape of interaction %s:" %i_interaction_ops,
                            ('Square', ''),
                        )
                        self.interaction_operators[key]['Hermitian_conjugate'] = st.checkbox(
                            'Hermitian conjugate',
                            key = 100 + 10*i_interaction_ops + 0.1*len(target_qubits_pair)
                        )

            with col3:
                with st.container(border=True):
                    for key in self.pulse_params:
                        col1, col2 = st.columns(2)
                        with col1:
                            param_value = st.number_input(
                                '%s param_value' %(key),
                                value = None, 
                                key = key
                            )
                        with col2:
                            st.write('')
                            st.write('')
                            is_complex = st.checkbox(
                                'is_complex',
                                key = 'param_value_c' + str(key)
                            )
                            if is_complex:
                                param_value = param_value * 1j
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

        col1, col2 = st.columns(2)
        with col1:
            init_state = st.text_input(
                label="Type your initial state: (hint: 00 for $$\ket{00}$$)",
                value="00",
                key = 'init_state'
            )
            st.write(init_state)
        with col2:
            num_target_state = st.number_input(
                label="Type the number of your target state.",
                value=1,
                min_value=1,
                max_value=5
            )
            target_states = []
            for index_target in range(num_target_state):
                target_state = st.text_input(
                    label="Type your target state: (hint: 00 for $$\ket{00}$$)",
                    value="00",
                    key = 'target_state' + str(index_target)
                )
                target_states.append(target_state)

        with st.form("run"):
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

                # To Do: do not use private method!!!
                self.rho_init = qt.tensor(model._map_state(init_state))
                self.rho_targets = []
                for index in range(len(target_states)):
                    rho_target = qt.tensor(model._map_state(target_states[index]))
                    self.rho_targets.append(rho_target)
                
                model.update_params(self.pulse_params)
                rho_init, rho_target, results = model.run_simulation(
                    state_init=self.rho_init,
                    #state_target=self.rho_targets,
                    pulse_params = self.pulse_params,
                    options=qt.Options(nsteps=15000, atol=1e-13, rtol=1e-13, rhs_reuse=False)
                )
                amp = []
                phase = []
                for i in range(len(results.states)):
                    state = results.states[i]
                    amp.append(np.abs([s.dag().overlap(state) for s in self.rho_targets]))
                    phase.append(np.angle([s.dag().overlap(state) for s in self.rho_targets])/np.pi)
                times = np.linspace(0.0, self.pulse_params['T_gate']['param_value'][0], self.num_samples)
                col1, col2 = st.columns(2)
                with col1:
                    fig, ax = plt.subplots()
                    for index in range(len(target_states)):
                        ax.plot(times, [x[index] for x in amp])
                    ax.set_xlabel('Time' r'$(\mu s)$')
                    ax.set_ylabel('Amplitude')
                    ax.legend(target_states)
                    st.pyplot(fig)
                    st.write("Amplitude: ", amp)
                with col2:
                    fig, ax = plt.subplots()
                    for index in range(len(target_states)):
                        ax.plot(times, [x[index] for x in phase])
                    ax.set_xlabel('Time' r'$(\mu s)$')
                    ax.set_ylabel('Arg/' r'$\pi$')
                    ax.legend(target_states)
                    st.pyplot(fig)
                    st.write("Phase: ", phase)

    def optimization(
        self
    ):
        pass
