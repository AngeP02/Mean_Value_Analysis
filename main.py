import streamlit as st
import io

from Utils.ProcedureInterne import read_data, soluzione, print_data, aggiorna

st.set_page_config(page_title="Progetto MVA", layout="wide")
st.header("Mean Value Analysis")

if 'output_content_log' not in st.session_state:
    st.session_state['output_content_log'] = "QUEUEING NETWORKS SOLUTION BASED UPON MEAN VALUE ANALYSIS\n\n"
if 'soluzione_aggiunta_al_log' not in st.session_state:
    st.session_state['soluzione_aggiunta_al_log'] = False



#TODO da togliere parte sottostante
if st.button("Reset sessione"):
    st.session_state.clear()
    st.session_state['output_content_log'] = "QUEUEING NETWORKS SOLUTION BASED UPON MEAN VALUE ANALYSIS\n\n" # Reinizializza anche il log
    st.session_state['soluzione_aggiunta_al_log'] = False
    st.rerun()

if 'nome_file_sottomesso' not in st.session_state:
    st.session_state['nome_file_sottomesso'] = False
if 'nome_file_output' not in st.session_state:
    st.session_state['nome_file_output'] = "output.txt"
if 'almeno_1nome_definito' not in st.session_state:
    st.session_state['almeno_1nome_definito'] = False
if 'switch_nome_file' not in st.session_state:
    st.session_state['switch_nome_file'] = False

with st.container(border=True):
    if not st.session_state.nome_file_sottomesso or st.session_state.switch_nome_file:
        col1, col2 = st.columns([1,3])
        with col1:
            temp_nome_file = st.text_input("Imposta il nome del file di output:", value=st.session_state.nome_file_output, label_visibility="collapsed",key="temp_nome_file_input")
        with col2:
            if st.button("Conferma nome file"):
                st.session_state.nome_file_output = temp_nome_file
                st.session_state.nome_file_sottomesso = True
                st.session_state.almeno_1nome_definito = True
                st.session_state.switch_nome_file = True
    if st.session_state.nome_file_sottomesso:
        st.success(f"Nome file di output impostato su: {st.session_state.nome_file_output}")

if 'modello_definito' not in st.session_state:
    st.session_state['modello_definito'] = False
if 'dati_modello' not in st.session_state:
    st.session_state['dati_modello'] = None
if 'azione' not in st.session_state:
    st.session_state['azione'] = None

temp_output_buffer = io.StringIO()

if st.session_state.almeno_1nome_definito:
    if not st.session_state.modello_definito:
        with st.container(border=True):

            temp_output_buffer.seek(0)
            temp_output_buffer.truncate(0)

            st.session_state.dati_modello = read_data()
            print_data(temp_output_buffer, st.session_state.dati_modello)
        if st.button("Conferma modello"):
            st.session_state.modello_definito = True
            st.success("Modello definito con successo!")
            st.session_state['output_content_log'] += temp_output_buffer.getvalue()
            st.session_state['soluzione_aggiunta_al_log'] = False
            st.rerun()
    else:
        st.session_state.azione = st.selectbox("Scelta",
            ["Definizione nuovo modello", "Aggiorna modello", "Visualizza soluzione"],
            index=2
        )

    if st.session_state.azione == "Definizione nuovo modello":
        for key in ['modello_definito', 'dati_modello']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    elif st.session_state.azione == "Aggiorna modello":
        dati_temp = aggiorna(st.session_state.dati_modello)
        if st.button("Conferma aggiornamento modello"):
            st.session_state.dati_modello = dati_temp

            temp_output_buffer.seek(0)
            temp_output_buffer.truncate(0)

            print_data(temp_output_buffer, st.session_state.dati_modello)
            st.success("Modello aggiornato. Puoi ora visualizzare la soluzione o modificarlo ulteriormente.")
            st.session_state['output_content_log'] += temp_output_buffer.getvalue()
            st.session_state['soluzione_aggiunta_al_log'] = False
            st.rerun()

    elif st.session_state.azione == "Visualizza soluzione":
        if st.session_state.dati_modello is not None:

            temp_output_buffer.seek(0)
            temp_output_buffer.truncate(0)

            soluzione(st.session_state.dati_modello, temp_output_buffer)
            if not st.session_state['soluzione_aggiunta_al_log']:
                st.session_state['output_content_log'] += temp_output_buffer.getvalue()
            st.session_state['soluzione_aggiunta_al_log'] = True
        else:
            st.warning("Devi prima definire un modello.")

contenuto = st.session_state['output_content_log']
st.session_state['output_file_content'] = contenuto

if contenuto:
    st.download_button(
        label=f"Scarica file {st.session_state.nome_file_output}",
        data=contenuto,
        file_name=st.session_state.get('nome_file_output', 'output.txt'),
        mime='text/plain'
    )
else:
    st.warning("Nessun contenuto da scaricare")
