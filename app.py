import streamlit as st

from expt import CZGate
from expt import YourExpt

def update_expt():
    if st.session_state['expt_name'] == 'CZ gate':
        st.session_state['expt'] = CZGate() 
    elif st.session_state['expt_name'] == 'Your experiment':
        st.session_state['expt'] = YourExpt() 

if __name__ == "__main__":
    st.set_page_config(
        page_title='YATAIGA', 
        layout='wide',
        menu_items={
            'About': "# Made by YATAIGA"}
    )
    st.title('YATAIGA - Your Quantum Research Assistant.')

    if 'expt_name' not in st.session_state:
        st.session_state['expt_name'] = 'Your experiment'
        update_expt()

    st.write("---")
    st.header('Prepare Your Quantum System⚛️')
    st.session_state['expt'].quantum_system()

    st.write("---")
    st.header('Collect Data🏃‍♀️')   
    st.session_state['expt'].population_evolution()
    
    # st.write("---")
    # st.header("Let's Optimize Your Quantum Operation!📈")
    # st.session_state['expt'].optimization()

    with st.sidebar:
        st.title('YATAIGA')
        st.selectbox('Choose an experiment.',
                     ['Your experiment', 'CZ gate'],
                     key='expt_name',
                     on_change=update_expt)
        st.session_state['expt'].sidebar()
