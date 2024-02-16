import inspect

import streamlit as st

from rdquantum.qsim.pulse import pulse_shape

def pulse_params(
    key: str,
    shape: str
):
    _pulse = getattr(pulse_shape, shape)
    _param_dict = inspect.getfullargspec(_pulse).annotations
    del _param_dict["tlist"]
    del _param_dict["return"]

    row = st.columns(len(_param_dict.keys()))
    for i in range(len(_param_dict.keys())):
        param_key = list(_param_dict.keys())[i]
        col = row[i]
        with col:
            _param_dict[param_key] = st.number_input(
                label = str(param_key),
                key = key + "_pulse_param_" + str(i),
                placeholder = str(_param_dict[param_key])
            )

    return _param_dict
