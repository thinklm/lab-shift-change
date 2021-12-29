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
key_dict = json.loads(st.secrets["textkey"])
db = firestore.Client.from_service_account_info(key_dict)



### FUNCTIONS

# def db_check() -> None:
#     # Authenticate to Firestore with the JSON account key.
#     db = firestore.Client.from_service_account_json("firestore_key.json")

#     # Create a reference to the Google post.
#     doc_ref = db.collection("fechamentos").document("28122021A")

#     # Then get the data at that reference.
#     doc = doc_ref.get()

#     # Let's see what we got!
#     st.write("The id is: ", doc.id)
#     st.write("The contents are: ", doc.to_dict())



# def get_shift(now: datetime, mode: str="current") -> str:
#     if (int(now.strftime("%H")) == 23) | (int(now.strftime("%H")) < 7):
#         current_shift = "A"
#     elif (int(now.strftime("%H")) >= 7) | (int(now.strftime("%H")) < 15):
#         current_shift = "B"
#     elif (int(now.strftime("%H")) >= 15) | (int(now.strftime("%H")) < 23):
#         current_shift = "C"
#     else: 
#         current_shift = None


#     if mode == "current":
#         return current_shift

#     elif mode == "previous":
#         if current_shift == "A":
#             return "C"
#         elif current_shift == "B":
#             return "A"
#         elif current_shift == "C":
#             return "B"
#         else: 
#             return None

    



def upload_shift_data(submit_args: dict) -> None:
    now = datetime.now()
    new_id  = now.strftime("%d%m%Y") + st.session_state.sft
    submit_args["date"] = now

    doc_ref = db.collection(u"fechamentos").document(new_id)
    doc_ref.set(submit_args)





def _submit_callback() -> None:
    
    if st.session_state.sft == "Selecione":
        st.error("Turno não selecionado!")
    else:   
        submit_args = {
            "endedshift": st.session_state.sft,
            "washer1": st.session_state.w1,
            "washer1pend": st.session_state.w1p,
            "sos1": st.session_state.s1,
            "sos1pend": st.session_state.s1p,
            "uvbc1": st.session_state.u1,
            "uvbc1pend": st.session_state.u1p,
            "washer2": st.session_state.w2,
            "washer2pend": st.session_state. w2p,
            "sos2": st.session_state.s2,
            "sos2pend": st.session_state.s2p,
            "uvbc2": st.session_state.u2,
            "uvbc2pend": st.session_state.u2p,
        }

        
        # Sobe os dados do turno para o banco de dados
        upload_shift_data(submit_args)

        # Mensagem de sucesso
        st.success("Dados enviados com sucesso!")
        
        # Limpa os campos de entrada pro usuário
        clear_list = ["sft", "w1", "w1p", "s1", "s1p", "u1", "u1p", "w2", "w2p", "s2", "s2p", "u2", "u2p"]
        for key in clear_list:
            if key not in st.session_state.keys():
                st.error("Chave inexistente")
            elif key == "sft":
                st.session_state[key] = "Selecione"
            else:
                st.session_state[key] = ""




def _inserir_dados() -> None:

    # Header
    st.header("Inserir Dados")
    col_shift, col_empty  = st.columns([1,5])
    with col_shift:
        st.selectbox(label="Turno: ", options=["Selecione", "A", "B", "C"], key="sft")
    with col_empty:
        st.empty()    
    
    
    # FORMS
    with st.form(key='form1', clear_on_submit=False):
        col1, col2 = st.columns([3,3])

        with col1:
            st.subheader("Linha 571")
            st.text_area("Lavadora", placeholder="Lavadora da Linha 571", key="w1")
            st.text_area("", placeholder="Pendências", key="w1p")
            st.text_area("SOS", placeholder="SOS da Linha 571", key="s1")
            st.text_area("", placeholder="Pendências", key="s1p")
            st.text_area("UVBC", placeholder="UVBC da Linha 571", key="u1")
            st.text_area("", placeholder="Pendências", key="u1p")

        with col2:
            st.subheader("Linha 572")            
            st.text_area("Lavadora", placeholder="Lavadora da Linha 572", key="w2")
            st.text_area("", placeholder="Pendências", key="w2p")
            st.text_area("SOS", placeholder="SOS da Linha 572", key="s2")
            st.text_area("", placeholder="Pendências", key="s2p")
            st.text_area("UVBC", placeholder="UVBC da Linha 572", key="u2")
            st.text_area("", placeholder="Pendências", key="u2p")

        st.form_submit_button(label="Enviar", on_click=_submit_callback)



# def display_current_time() -> None:
#     now = datetime.now()
#     #current_time = now.strftime("%H:%M:%S")
#     current_date = now.strftime("%d/%m/%Y")
#     current_shift = get_shift(now, mode='current')

#     st.write(f"Dia: {current_date} \nTurno: {current_shift}")




def _home() -> None:
    st.write("## :hammer: Funcionalidade em desenvolvimento! ")
    
    # Buscar último dado inserido
    fechamentos_ref = db.collection(u"fechamentos")
    doc_ref = fechamentos_ref.order_by(
        u"date", direction=firestore.Query.DESCENDING).limit(1)
    query = doc_ref.get()[0].to_dict()


    # Mostra o resultado teste
    st.subheader("Última Modificação:")

    # dia, hora e turno da última modificação
    col_data, col_hora, col_turno = st.columns(3)
    with col_data:
        st.write(f"Dia: {query['date'].strftime('%d/%m/%Y')}")
    with col_hora:
        st.write(f"Hora: {query['date'].strftime('%H:%M:%S')}")
    with col_turno:
        st.write(f"Turno: {query['endedshift']}")

    # Detalhes da úlitma modificação
    col3, col4 = st.columns(2)

    with col3:
        st.write("### Linha 571")

        st.write("#### Lavadora")
        st.write(f"Fechamento\n\n > {query['washer1']}\n\n")
        st.write(f"Pendências\n\n > {query['washer1pend']}\n\n")

        st.write("#### SOS")
        st.write(f"Fechamento\n\n > {query['sos1']}\n\n")
        st.write(f"Pendências\n\n > {query['sos1pend']}\n\n")

        st.write("#### UVBC:")
        st.write(f"Fechamento\n\n > {query['uvbc1']}\n\n")
        st.write(f"Pendências\n\n > {query['uvbc1pend']}\n\n")

    with col4:
        st.write("### Linha 572")

        st.write("#### Lavadora")
        st.write(f"Fechamento\n\n > {query['washer2']}\n\n")
        st.write(f"Pendências\n\n > {query['washer2pend']}\n\n")

        st.write("#### SOS")
        st.write(f"Fechamento\n\n > {query['sos2']}\n\n")
        st.write(f"Pendências\n\n > {query['sos2pend']}\n\n")

        st.write("#### UVBC:")
        st.write(f"Fechamento\n\n > {query['uvbc2']}\n\n")
        st.write(f"Pendências\n\n > {query['uvbc2pend']}\n\n")





def _buscar_dados() -> None:
    st.subheader("Funcionalidade em desenvolvimento!")
    pass




def main() -> None:
    st.title("Troca de Turno - Laboratório")

    # Side manu
    menu = ['Home', 'Inserir', 'Buscar']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        _home()
    elif choice == "Inserir":
        _inserir_dados()
    elif choice == "Buscar":
        _buscar_dados()
       



if __name__ == '__main__':
    main()