'''
Filename: streamlit_test.py
Path: d:\Emanuel\Projetos\lm-env-shift-change
Created Date: Monday, December 27th 2021, 12:41:59 pm
Author: Emanuel Monção Lima

Copyright (c) 2021 AmBev Latas Minas / THINK
'''

### IMPORTS

import pandas as pd
import streamlit as st
import pandas as pd



### FUNCTIONS

def _submit_callback(submit_args: dict) -> None:
    try:
        df = pd.DataFrame(submit_args, index=[0])
    except Exception as e:
        st.error(f'Erro ao salvar dados:\n\n{e}')

    # Mensagem de sucesso
    st.success("Dados enviados com sucesso!")

    # Mostra os dados efetuados
    st.dataframe(df)






def _inserir_dados() -> None:
    st.header("Inserir Dados")

    # FORMS
    with st.form(key='form1', clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Linha 571")
            washer1 = st.text_input("Lavadora - 571", placeholder="Digite os dados de troca de turno referentes à Lavadora da Linha 571")
            sos1 = st.text_input("SOS - 571", placeholder="Digite os dados de troca de turno referentes ao SOS da Linha 571")
            uvbc1 = st.text_input("UVBC - 571", placeholder="Digite os dados de troca de turno referentes à UVBC da Linha 571")

        with col2:
            st.subheader("Linha 572")
            washer2 = st.text_input("Lavadora - 572", placeholder="Digite os dados de troca de turno referentes à Lavadora da Linha 572")
            sos2 = st.text_input("SOS - 572", placeholder="Digite os dados de troca de turno referentes ao SOS da Linha 572")
            uvbc2 = st.text_input("UVBC - 572", placeholder="Digite os dados de troca de turno referentes à UVBC da Linha 572")
                
        submit_button = st.form_submit_button(label="Enviar")            

        if submit_button:
            submit_args = {
                "washer1": washer1,
                "sos1": sos1,
                "uvbc1": uvbc1,
                "washer2": washer2,
                "sos2": sos2,
                "uvbc2": uvbc2
            }
            _submit_callback(submit_args=submit_args)





def main() -> None:
    st.title("Troca de Turno - Laboratório")
    menu = ['Inserir', 'Buscar']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Inserir":
        _inserir_dados()
       



if __name__ == '__main__':
    main()