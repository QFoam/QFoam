import streamlit as st

from expt import Expt

if __name__ == "__main__":
    st.set_page_config(
        page_title='YATAIGA', 
        layout='wide',
        menu_items={
            'About': "# Made by YATAIGA"
        }
    )
    if "expt" not in st.session_state:
        st.session_state.expt = Expt()

    with st.sidebar:
        st.title('YATAIGA \n :rainbow[Quantum Simulation with Natural Language.]')
        st.session_state.expt.set_qspecies()
        st.session_state.expt.set_qsystem()

    st.session_state.expt.set_hamiltonian()

    st.divider()

    st.subheader('Collect Data 🏃‍♀️') 
    st.session_state.expt.popevo()
