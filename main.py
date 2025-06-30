import streamlit as st
import io

from Soluzioni.Approssimazione import approssimazione
from Soluzioni.Bound import bound
from Soluzioni.Failure import failure
from Soluzioni.Large import large
from Soluzioni.LoadDependent import load_dependent
from Utils.ProcedureInterne import read_data, update, soluzione

st.set_page_config(page_title="Progetto MVA", layout="wide")
st.header("Mean Value Analysis")

#TODO da togliere parte sottostante
if st.button("🔄 Reset sessione", help="Pulisce tutti i dati salvati nella sessione corrente (sviluppo)"):
    st.session_state.clear()
    st.rerun()

if 'nome_file_sottomesso' not in st.session_state:
    st.session_state['nome_file_sottomesso'] = False
if 'nome_file_output' not in st.session_state:
    st.session_state['nome_file_output'] = "output.txt"

with st.container(border=True):
    if not st.session_state.nome_file_sottomesso:
        temp_nome_file = st.text_input("Imposta il nome del file di output:", value=st.session_state.nome_file_output)
        if st.button("Conferma nome file"):
            st.session_state.nome_file_output = temp_nome_file
            st.session_state.nome_file_sottomesso = True
            st.success(f"Nome file di output impostato su: {st.session_state.nome_file_output}")
            st.rerun()
    else:
        st.write(f"**Nome del file di output:** `{st.session_state.nome_file_output}`")
        if st.button("Modifica nome file"):
            st.session_state.nome_file_sottomesso = False
            st.rerun()

output_buffer = io.StringIO()
output_buffer.write("QUEUEING NETWORKS SOLUTION BASED UPON MEAN VALUE ANALYSIS\n\n")


if 'modello_definito' not in st.session_state:
    st.session_state['modello_definito'] = False
if 'dati_modello' not in st.session_state:
    st.session_state['dati_modello'] = None

if not st.session_state.modello_definito:
    azione = ""
    with st.container(border=True):
        st.session_state.dati_modello = read_data(output_buffer)
    if st.button("Configurazione delle stazioni"):
        st.session_state.modello_definito = True
        st.success("Modello definito con successo!")
        st.rerun()
else:
    azione = st.selectbox("Cosa vuoi fare?", [
        "Definisci nuovo modello", "Aggiorna modello", "Visualizza soluzione"
    ])

if azione == "Aggiorna modello":
    st.session_state.dati_modello = update(st.session_state.dati_modello, output_buffer)
    st.success("Modello aggiornato!")

elif azione == "Visualizza soluzione":
    if st.session_state.dati_modello is not None:
        soluzione(st.session_state.dati_modello, output_buffer)
    else:
        st.warning("Devi prima definire un modello.")


css = """
<style>
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
  font-size: 20px;
  margin-right: 10px;
  padding: 8px 95px;  
  color: black;
}
button[data-baseweb="tab"] {
    margin-right: 12px;
    padding: 10px 20px;
    border-radius: 8px;
    background-color: #f5e4bc;
    transition: all 0.2s ease-in-out;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #f0b37a;
    color: white !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

sezione1, sezione2, sezione3, sezione4, sezione5 = st.tabs(["Approssimazione", "Load Dependent", "Large", "Bound", "Failure"])

with sezione1:
    approssimazione(output_buffer)
with sezione2:
    load_dependent(output_buffer)
with sezione3:
    large(output_buffer)
with sezione4:
    bound(output_buffer)
with sezione5:
    failure(output_buffer)