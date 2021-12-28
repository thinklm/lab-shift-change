'''
Filename: streamlit_test.py
Path: d:\Emanuel\Projetos\lab-shift-change
Created Date: Monday, December 27th 2021, 12:41:59 pm
Author: Emanuel Monção Lima

Copyright (c) 2021 AmBev Latas Minas / THINK
'''

### IMPORTS


import pandas as pd
from google.cloud import firestore
from datetime import datetime
import json
import streamlit as st
st.set_page_config(layout="wide")

### DB CONN
#db = firestore.Client.from_service_account_json("firestore_key.json")
key_dict = json.loads(st.secrets["textkey"])
db = firestore.Client.from_service_account_info(key_dict)



### FUNCTIONS

def db_check() -> None:
    # Authenticate to Firestore with the JSON account key.
    db = firestore.Client.from_service_account_json("firestore_key.json")

    # Create a reference to the Google post.
    doc_ref = db.collection("fechamentos").document("28122021A")

    # Then get the data at that reference.
    doc = doc_ref.get()

    # Let's see what we got!
    st.write("The id is: ", doc.id)
    st.write("The contents are: ", doc.to_dict())



def get_shift(now: datetime, mode: str="current") -> str:
    if (int(now.strftime("%H")) == 23) | (int(now.strftime("%H")) < 7):
        current_shift = "A"
    elif (int(now.strftime("%H")) >= 7) | (int(now.strftime("%H")) < 15):
        current_shift = "B"
    elif (int(now.strftime("%H")) >= 15) | (int(now.strftime("%H")) < 23):
        current_shift = "C"
    else: 
        current_shift = None


    if mode == "current":
        return current_shift

    elif mode == "previous":
        if current_shift == "A":
            return "C"
        elif current_shift == "B":
            return "A"
        elif current_shift == "C":
            return "B"
        else: 
            return None

    



def upload_shift_data(submit_args: dict) -> None:
    now = datetime.now()
    previous_shift = get_shift(now, mode='previous')
    new_id  = now.strftime("%d%m%Y") + previous_shift

    doc_ref = db.collection("fechamentos").document(new_id)
    doc_ref.set(submit_args)





def _submit_callback(submit_args: dict) -> None:
    try:
        df = pd.DataFrame(submit_args, index=[0])
    except Exception as e:
        st.error(f'Erro ao salvar dados:\n\n{e}')

    # Mensagem de sucesso
    upload_shift_data(submit_args)
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
            washer1 = st.text_input("Lavadora", placeholder="Lavadora da Linha 571")
            sos1 = st.text_input("SOS", placeholder="SOS da Linha 571")
            uvbc1 = st.text_input("UVBC", placeholder="UVBC da Linha 571")

        with col2:
            st.subheader("Linha 572")
            washer2 = st.text_input("Lavadora", placeholder="Lavadora da Linha 572")
            sos2 = st.text_input("SOS", placeholder="SOS da Linha 572")
            uvbc2 = st.text_input("UVBC", placeholder="UVBC da Linha 572")
                
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




def display_current_time() -> None:
    now = datetime.now()
    #current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%d/%m/%Y")
    current_shift = get_shift(now, mode='current')

    st.write(f"Dia: {current_date} \nTurno: {current_shift}")



def main() -> None:
    #db_check()

    st.title("Troca de Turno - Laboratório")
    menu = ['Inserir', 'Buscar']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Inserir":
        _inserir_dados()

    else:
        st.subheader("Funcionalidade em desenvolvimento!")
       



if __name__ == '__main__':
    main()