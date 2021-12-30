'''
Filename: streamlit_test.py
Path: d:\Emanuel\Projetos\lab-shift-change
Created Date: Monday, December 27th 2021, 12:41:59 pm
Author: Emanuel Monção Lima

Copyright (c) 2021 AmBev Latas Minas / THINK
'''

### IMPORTS

from google.cloud import firestore
from datetime import datetime
import pytz
import json
import re
import streamlit as st
st.set_page_config(layout="wide")



### DB CONN

key_dict = json.loads(st.secrets["textkey"])
db = firestore.Client.from_service_account_info(key_dict)



### FUNCTIONS

def _upload_shift_data(submit_args: dict, teste: bool=False) -> None:
    now = datetime.now()

    if teste:
        new_id  = "29122021A"
        submit_args["date"] = datetime.strptime("29/12/2021 07:10:23", "%d/%m/%Y %H:%M:%S")
    else:
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
            "sos1": st.session_state.s1,
            "uvbc1": st.session_state.u1,
            "washer2": st.session_state.w2,
            "sos2": st.session_state.s2,
            "uvbc2": st.session_state.u2,
            "pends": st.session_state.pends,
            "obs": st.session_state.obs,
        }

        
        # Sobe os dados do turno para o banco de dados
        #_upload_shift_data(submit_args, teste=True)
        _upload_shift_data(submit_args)

        # Mensagem de sucesso
        st.success("Dados enviados com sucesso!")
        
        # Limpa os campos de entrada pro usuário
        clear_list = ["sft", "w1", "s1", "u1", "w2", "s2", "u2", "pends", "obs"]
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
            st.text_area("SOS", placeholder="SOS da Linha 571", key="s1")
            st.text_area("UVBC", placeholder="UVBC da Linha 571", key="u1")           

        with col2:
            st.subheader("Linha 572")            
            st.text_area("Lavadora", placeholder="Lavadora da Linha 572", key="w2")
            st.text_area("SOS", placeholder="SOS da Linha 572", key="s2")
            st.text_area("UVBC", placeholder="UVBC da Linha 572", key="u2")

        st.subheader("Geral")
        st.text_area("Pendências", placeholder="Pendências", key="pends")
        st.text_area("Observações", placeholder="Observações", key="obs")

        st.form_submit_button(label="Enviar", on_click=_submit_callback)







def _home() -> None:
    st.write("## :hammer: Funcionalidade em desenvolvimento! ")
    
    # Buscar último dado inserido
    fechamentos_ref = db.collection(u"fechamentos")
    doc_ref = fechamentos_ref.order_by(
       u"date", direction=firestore.Query.DESCENDING).limit(1)
    query = doc_ref.get()[0].to_dict()


    # INIT TESTE
    # doc_ref = db.collection(u"fechamentos").document("29122021A")
    # query = doc_ref.get().to_dict()
    # FIM TESTE

    # Mostra o resultado teste
    st.subheader("Última Modificação:")

    # dia, hora e turno da última modificação
    col_data, col_hora, col_turno = st.columns(3)
    with col_data:
        st.write(f"Dia: {query['date'].strftime('%d/%m/%Y')}")
    with col_hora:
        st.write(f"Hora: {query['date'].astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M:%S')}")
    with col_turno:
        st.write(f"Turno: {query['endedshift']}")

    

    # Detalhes da úlitma modificação
    col3, col4 = st.columns(2)

    with col3:
        st.write("### Linha 571")

        st.write("#### Lavadora")
        for s in re.split(r"\s{2,}", query['washer1']):
            st.write(f"> {s}")
        st.write("\n\n")

        st.write("#### SOS")
        for s in re.split(r"\s{2,}", query['sos1']):
            st.write(f"> {s}")
        st.write("\n\n")

        st.write("#### UVBC:")
        for s in re.split(r"\s{2,}", query['uvbc1']):
            st.write(f"> {s}")
        st.write("\n\n")

    with col4:
        st.write("### Linha 572")

        st.write("#### Lavadora")
        for s in re.split(r"\s{2,}", query['washer2']):
            st.write(f"> {s}")
        st.write("\n\n")

        st.write("#### SOS")
        for s in re.split(r"\s{2,}", query['sos2']):
            st.write(f"> {s}")
        st.write("\n\n")

        st.write("#### UVBC:")
        for s in re.split(r"\s{2,}", query['uvbc2']):
            st.write(f"> {s}")
        st.write("\n\n")

    st.write("#### Pendências:")
    if ("pends" in query.keys()) & (not query["pends"] == ""):
        for s in re.split(r"\s{2,}", query["pends"]):
            st.write(f" > {s}")  
    else:
        st.write("Nenhuma pendência")

    st.write("#### Observações Gerais:")
    if ("obs" in query.keys()) & (not query["obs"] == ""):
        for s in re.split(r"\s{2,}", query["obs"]):
            st.write(f" > {s}")  
    else:
        st.write("Nenhuma observação")





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