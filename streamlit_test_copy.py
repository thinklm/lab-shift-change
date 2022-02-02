'''
Filename: streamlit_test.py
Path: d:\Emanuel\Projetos\lab-shift-change
Created Date: Monday, December 27th 2021, 12:41:59 pm
Author: Emanuel Monção Lima

Copyright (c) 2021 AmBev Latas Minas / THINK
'''

### IMPORTS

from sqlite3 import Timestamp
from google.cloud import firestore
from datetime import datetime, time, timedelta
from google.cloud.firestore_v1.query import Query
import pytz
import pandas as pd
import json
import re
import random
import streamlit as st
from streamlit_echarts import st_echarts
st.set_page_config(layout="wide")



### DB CONN

try:
    key_dict = json.loads(st.secrets["textkey"])
    db = firestore.Client.from_service_account_info(key_dict)
except Exception as e:
    st.write(f"Erro na conexão com o Banco de Dados:\n{e}")
    st.write("Se persistir o erro, contate o desenvolvedor!")




### FUNCTIONS

def _query(mode: str="search") -> Query.stream:
    """Busca no Banco de Dados com filtros.

    Args:
        home (bool, optional): Opção para identificar a busca específica para a Home. Defaults to False.

    Returns:
        Query.stream: Generator com objetos correspondentes aos filtros de busca aplicados.
    """

    if mode=="home":
        fechamentos_ref = db.collection(u"fechamentos")
        docs = fechamentos_ref.order_by(
            u"date", direction=firestore.Query.DESCENDING
        ).limit(1)

        start_date = datetime.strptime(
            f"{docs.get()[0].to_dict()['date'].astimezone(pytz.timezone('America/Sao_Paulo')).date()}", "%Y-%m-%d"
        )
        end_date = start_date + timedelta(days=1)
        shift = docs.get()[0].to_dict()["endedshift"]

    else:
        start_date = datetime.strptime(f"{st.session_state.date_search}", "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)
        shift = st.session_state.sft_search

    fechamentos_ref = db.collection(u"fechamentos")
    doc_ref = fechamentos_ref.where(
        u"date", u">", start_date.astimezone(pytz.timezone("America/Sao_Paulo"))
    ).where(
        u"date", u"<", end_date.astimezone(pytz.timezone("America/Sao_Paulo"))
    ).where(
        u"endedshift", u"==", f"{shift}"
    ).order_by(
        u"date", direction=firestore.Query.ASCENDING
    )

    return doc_ref.stream()





def _analysis_query(date_list: list) -> dict:

    start_date = date_list[0]
    end_date = date_list[-1]

    doc_ref = db.collection(u"fechamentos").where(
        u"date", u">", start_date.tz_localize(pytz.timezone("America/Sao_Paulo"))
    ).where(
        u"date", u"<", end_date.tz_localize(pytz.timezone("America/Sao_Paulo"))
    ).order_by(
        u"date", direction=firestore.Query.ASCENDING
    )

    registry_count = dict()
    for doc in doc_ref.stream():
        #st.write(doc.to_dict()["endedshift"])
        if (doc.to_dict()["date"].astimezone(pytz.timezone("America/SAo_paulo")) == "") | \
         (doc.to_dict()["date"] >= datetime.today().astimezone(pytz.timezone("America/SAo_paulo"))):
            registry_count[doc.to_dict()["date"].strftime("%Y-%m-%d")] = -1
        elif doc.to_dict()["date"].astimezone(pytz.timezone("America/SAo_paulo")).strftime("%Y-%m-%d") in registry_count:
            #st.write(doc.to_dict()["date"].strftime("%Y-%m-%d"))
            if doc.to_dict()["endedshift"] in registry_count[doc.to_dict()["date"].astimezone(pytz.timezone("America/SAo_paulo")).strftime("%Y-%m-%d")]:
                pass
            else: 
                registry_count[doc.to_dict()["date"].astimezone(pytz.timezone("America/SAo_paulo")).strftime("%Y-%m-%d")].append(doc.to_dict()["endedshift"])

        else: 
            registry_count[doc.to_dict()["date"].astimezone(pytz.timezone("America/SAo_paulo")).strftime("%Y-%m-%d")] = list(doc.to_dict()["endedshift"])


    return registry_count





def _merge_docs(query: Query.stream) -> dict:
    """Concatena os documentos com a mesma especificação em um só.

    Args:
        query (Query.stream): Stream de queries resultantes da busca filtrada no banco de dados

    Returns:
        dict: Objeto com as informações concatenadas. 
        Retorna None caso não haja registros para a busca aplicada.
    """

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
            
            elif (key == "endedshift") | (merged[key] == ""):
                merged[key] = doc.to_dict()[key]   
            
            else:
                merged[key] = merged[key] + "\n\n" + doc.to_dict()[key]

    return merged






def _upload_shift_data(submit_args: dict, teste: bool=False) -> None:
    """Faz o upload de dados do turno selecionado para o banco de dados.

    Args:
        submit_args (dict): Objeto com os valores a serem salvos
        teste (bool, optional): Modo de teste configurável para o desenvolvedor. Defaults to False.
    """

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
    """Apresenta as informações de um turno na aplicação.

    Args:
        query (dict): Objeto com os valores a serem apresentados na aplicação
    """

    # Verifica a ausência de registro
    if (query == None) | (query["date"] == ""):
        st.write("## :warning: Busca não encontrada!")

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

        # Coluna 571
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

        # Coluna 572
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
        else:
            st.write("Nenhuma pendência")

        st.write("\n\n")

        st.write("#### Observações Gerais:")
        if ("obs" in query.keys()) & (not query["obs"] == ""):
            for s in re.split(r"\n{2,}", query["obs"]):
                st.write(f" > {s}")  
        else:
            st.write("Nenhuma observação")

        






def _submit_callback() -> None:
    """Callback Function para o Submit do Forms para Inserir Dados.
    """
    
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
        _upload_shift_data(submit_args)
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





def _search_callback(mode: str="search") -> None:
    """Callback Function para Buscar dados e apresentá-los na aplicação.
    Serve tanto para a Home quanto para a tela de Buscar.

    Args:
        home (bool, optional): Opção para identificar a busca específica para a Home. Defaults to False.
    """

    # Busca todos os dados da data e turno escolhidos
    query = _query(mode)
    # junta todas as informações
    merged_query = _merge_docs(query)
    # mostra as informações na tela
    _display_shift_info(merged_query)
    




def _inserir_dados() -> None:
    """Estrutura de Formulário para inserir novos dados de turno para o Banco de Dados.
    """

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





def _buscar_dados() -> None:
    """Estrutura no menu lateral para definir o filtro de busca por data e turno.
    """
    
    # Menu lateral para busca
    st.sidebar.write("")
    st.sidebar.write("\n\nFaça sua busca:\n\n")
    st.sidebar.date_input("Data", key="date_search")
    st.sidebar.selectbox(label="Turno", options=["Selecione", "A", "B", "C"], key="sft_search")
    st.sidebar.button(label="Buscar", key="search_button")

    # Search button click
    if st.session_state.search_button:
        _search_callback()





def _analysis() -> None:
    month_options = {
        "01": "Janeiro", 
        "02": "Fevereiro", 
        "03": "Março",
        "04": "Abril", 
        "05": "Maio",
        "06": "Junho",
        "07": "Julho", 
        "08": "Agosto",
        "09": "Setembro",
        "10": "Outubro",
        "11": "Novembro",
        "12": "Dezembro"
    }

    # Interação Com Usuário
    st.write("### Preenchimento do Diário de Turno")
    col_1, col_2, col_spare = st.columns([1, 1, 5])
    with col_1:
        st.selectbox("Ano", options=['2022'], key="an_year")
    with col_2:
        st.selectbox("Mês", options=month_options.values(), key="an_month", index=datetime.today().month-1)
    with col_spare:
        st.empty()
    # Numero do mes escolhido
    month_number = [month for month, name in month_options.items() if name == st.session_state.an_month][0]
    


    def _get_date_list(year: int=2022, month: int=1) -> list:
        month_next = month +1 if (month > 0 and month < 12) else 1
        year_next = year if (month > 0 and month < 12) else year + 1
        date_list = pd.date_range(
            start=f"{year}-{month}-01", end=f"{year_next}-{month_next}-01", freq="D"
        )
        #st.write(date_list)
        return date_list
    
    

    # def _get_virtual_data(month: int, year: int=2022):    #-- Random Data OK
    #     date_list = _get_date_list(year, month)
    #     #shift_count = _analysis_query()
    #     return [[d.strftime("%Y-%m-%d"), random.randint(0, 3)] for d in date_list]

    # ''' FUNCIONA, MAS CUSTOSO DEMAIS '''
    # def _get_virtual_data(month: int, year: int=2022) -> list:  
    #     date_list = _get_date_list(year, month)
    #     #shift_count = _analysis_query()
    #     return [[d.strftime("%Y-%m-%d"), _analysis_query(d)] for d in date_list]

    def _get_virtual_data(query: dict, month: int, year: int=2022) -> list:  
        #date_list = _get_date_list(year, month)
        

        return [[d.strftime("%Y-%m-%d"), len(query[d.strftime("%Y-%m-%d")]) if d.strftime("%Y-%m-%d") in query else -1] for d in date_list]

    def _label_formatter(date_list: list) -> list:
        #date_list = _get_date_list(int(st.session_state.an_year), int(month_number))
        return [[d.strftime("%Y-%m-%d"), f'{d.strftime("%d")}\n'] for d in date_list]
        

    def _tooltip_formatter(query: dict) -> str:
        #date_list = _get_date_list(int(st.session_state.an_year), int(month_number))
        #return [[d.strftime("%Y-%m-%d"), f'{d.strftime("%d")}\n'] for d in date_list]
        turnos = ["A", "B", "C"]
        params = dict()
        params["values"] = query


        return f"Registros:{params.values[1]}"
        


    date_list = _get_date_list(int(st.session_state.an_year), int(month_number))
    query = _analysis_query(date_list)
    virtual_data = _get_virtual_data(query, int(month_number), int(st.session_state.an_year))

    ''' Configurar Tooltip '''
    option = {
        "tooltip": {
            "position": "top",
            "formatter": f"Turno A:\nTurno B:\nTurno C:",     #-- NOT OK]
            # "formatter": _tooltip_formatter(query),
            "renderMode": "richText"
        },
        "visualMap": {
            "show": False,
            "min": -1,
            "max": 3,
            "calculable": True,
            "orient": "horizontal",
            "left": 40,
            "bottom": 170,
            "inRange": {
                # "color": ['#e63946', '#2ec4b6', '#2ec4b6', '#2ec4b6'],
                "color": ['#dee2e6','#ef476f', '#ef476f', '#ef476f', '#06d6a0'],
                "opacity": [.9]
            }
        },
        "calendar": [
            {
                "orient": 'vertical',
                "yearLabel": {
                    "margin": 45
                },
                "dayLabel": {
                    "firstDay": 1,
                    "nameMap": ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
                    "color": "#aaa"
                },
                "monthLabel": {
                    "nameMap": 'en',
                    "margin": 20,
                    "color": "#aaa",
                    "fontSize": 13
                },
                "cellSize": 50,
                "top": 100,
                "left": 50,
                "range": f'{st.session_state.an_year}-{month_number}'
            },
        ],
        "series": [
            {       
                "type": 'scatter',
                "coordinateSystem": 'calendar',
                "symbolSize": 1,
                "top": "top",
                "label": {
                    "show": True,
                    "fontSize": 14,
                    "fontWeight": 500,
                    "color": '#fff'
                },
                "data": _label_formatter(date_list)
            },
            {   
                "type": "heatmap",
                "coordinateSystem": "calendar",
                "symbolsize": 1,
                "calendarIndex": 0,
                "data": virtual_data,
            }
        ],
    }

    st_echarts(option, height="640px", key="echarts")
    





def main() -> None:
    """Função principal para guia de execuções na aplicação.
    """

    st.title("Diário de Turno - Laboratório")

    # Side menu
    menu = ['Home', 'Inserir', 'Buscar', 'Análise']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        _search_callback(mode="home")
    elif choice == "Inserir":
        _inserir_dados()
    elif choice == "Buscar":
        _buscar_dados()
    elif choice == "Análise":
        _analysis()
    

       


### EXECUTAR
if __name__ == '__main__':
    main()
