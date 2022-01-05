'''
Filename: streamlit_test.py
Path: d:\Emanuel\Projetos\lab-shift-change
Created Date: Monday, December 27th 2021, 12:41:59 pm
Author: Emanuel Monção Lima

Copyright (c) 2021 AmBev Latas Minas / THINK
'''

### IMPORTS

from google.cloud import firestore
from datetime import datetime, time, timedelta
from google.cloud.firestore_v1.query import Query
import pytz
import json
import re
import random
import streamlit as st
st.set_page_config(layout="wide")



### DB CONN

try:
    key_dict = json.loads(st.secrets["textkey"])
    db = firestore.Client.from_service_account_info(key_dict)
except Exception as e:
    st.write(f"Erro na conexão com o Banco de Dados:\n{e}")
    st.write("Se persistir o erro, contate o desenvolvedor!")



### FUNCTIONS


def _query(home: bool=False) -> dict:
    if home:
        fechamentos_ref = db.collection(u"fechamentos")
        doc_ref = fechamentos_ref.order_by(
            u"date", direction=firestore.Query.DESCENDING
        ).limit(1)
        
        return doc_ref.get()[0].to_dict()

    else:
        date_query = datetime.strptime(f"{st.session_state.date_search}", "%Y-%m-%d")
        # doc_id = st.session_state.date_search.strftime("%d%m%Y") + st.session_state.sft_search
        # doc_ref = db.collection(u"fechamentos").document(doc_id)

        # return doc_ref.get().to_dict()
        fechamentos_ref = db.collection(u"fechamentos")
        doc_ref = fechamentos_ref.where(
            u"date", u">", date_query
        ).where(
            u"date", u"<", date_query + timedelta(days=1)
        ).where(
            u"endedshift", u"==", f"{st.session_state.sft_search}"
        ).order_by(
            u"date", direction=firestore.Query.ASCENDING
        )

        return doc_ref.stream()





def _merge_docs(query: Query.stream) -> dict:
    merged = {
        #"date": datetime.combine(st.session_state.date_search, time(hour=0, minute=0, second=1)).astimezone(pytz.timezone("America/Sao_Paulo")),
        "date": "",
        "endedshift": "",
        "washer1": "",
        "sos1": "",
        "uvbc1": "",
        "washer2": "",
        "sos2": "",
        "uvbc2": "",
        "pends": "",
        "obs": "",
    }

    for doc in query:
        for key in merged.keys():

            if key == "date":
                if doc.to_dict()[key] == "":
                    return None
                merged[key] = doc.to_dict()[key].astimezone(pytz.timezone("America/Sao_Paulo"))
            elif key == "endedshift":
                merged[key] = doc.to_dict()[key]   
            else:
                merged[key] = merged[key] + "\n\n" + doc.to_dict()[key]

    return merged






def _upload_shift_data(submit_args: dict, teste: bool=False) -> None:
    now = datetime.now().astimezone(pytz.timezone("America/Sao_Paulo"))

    if teste:
        new_id  = "29122021A" + str(random.randrange(1, 10**3)).zfill(4) 
        submit_args["date"] = datetime.strptime("29/12/2021 07:10:23", "%d/%m/%Y %H:%M:%S")
    else:
        new_id  = now.strftime("%d%m%Y") + st.session_state.sft + str(random.randrange(1, 10**3)).zfill(4)  
        submit_args["date"] = now

    doc_ref = db.collection(u"fechamentos").document(new_id)
    doc_ref.set(submit_args)





def _display_shift_info(query: dict) -> None:
    if (query == None) | (query["date"] == ""):
        st.write("## :warning: Busca não encontrada!")
        return None
    else:
        # dia, hora e turno da última modificação
        st.subheader("Última Modificação:\n\n")
        col_data, col_hora, col_turno, col_spare = st.columns([1, 1, 1, 3])
        with col_data:
            st.write(f"Dia: {query['date'].astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y')}")
        with col_hora:
            st.write(f"Hora: {query['date'].astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M:%S')}")
        with col_turno:
            st.write(f"Turno: {query['endedshift']}")
        with col_spare:
            st.empty()


        

        # Detalhes da úlitma modificação
        col3, col_spare2, col4 = st.columns([4,1,4])

        with col3:
            st.write("## Linha 571")

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

        # Coluna de marcação de espaço (layout-only)
        with col_spare2:
            st.empty()

        with col4:
            st.write("## Linha 572")

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



        st.write("\n\n")
        st.write("## Geral:")

        st.write("#### Pendências:")
        if ("pends" in query.keys()) & (not query["pends"] == ""):
            for s in re.split(r"\n{2,}", query["pends"]):
                st.write(f" > {s}")  
            # st.write(f" > {query['pends']}")
                 
        else:
            st.write("Nenhuma pendência")

            

        st.write("#### Observações Gerais:")
        if ("obs" in query.keys()) & (not query["obs"] == ""):
            for s in re.split(r"\n{2,}", query["obs"]):
                st.write(f" > {s}")  
            # st.write(f" > {query['obs']}")
        else:
            st.write("Nenhuma observação")

        






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
        _upload_shift_data(submit_args, teste=True)
        #_upload_shift_data(submit_args)

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





def _search_callback() -> None:
    query = _query()
    merged_query = _merge_docs(query)
    _display_shift_info(merged_query)
    




def _inserir_dados() -> None:

    # Header
    st.header("Inserir Dados")

    col_shift, col_empty  = st.columns([1,5])
    with col_shift:
        st.selectbox(label="Turno: ", options=["Selecione", "A", "B", "C"], key="sft")
    with col_empty:
        st.empty()    
    
    
    # FORMS
    with st.form(key='form_in', clear_on_submit=False):
        col1, col2 = st.columns(2)

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
    st.write(":warning: Funcionalidade em desenvolvimento! :hammer:")
    
    # Buscar último dado inserido
    query = _query(home=True)

    # Mostra o resultado da busca
    _display_shift_info(query=query)
    




def _buscar_dados() -> None:
    st.write("## :hammer: Funcionalidade em desenvolvimento!")

    # Menu lateral para busca
    st.sidebar.write("")
    st.sidebar.write("\n\nFaça sua busca:\n\n")
    st.sidebar.date_input("Data", key="date_search")
    st.sidebar.selectbox(label="Turno", options=["Selecione", "A", "B", "C"], key="sft_search")
    st.sidebar.button(label="Buscar", key="search_button")

    # Search button click
    if st.session_state.search_button:
        st.write(_search_callback())





def main() -> None:
    st.title("Diário de Turno - Laboratório")

    # Side menu
    menu = ['Home', 'Inserir', 'Buscar']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        _home()
    elif choice == "Inserir":
        _inserir_dados()
    elif choice == "Buscar":
        _buscar_dados()
       


### EXECUTAR
if __name__ == '__main__':
    main()