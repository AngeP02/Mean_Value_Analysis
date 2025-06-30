import streamlit as st
import io

from Utils.ProcedureInterne import read_data, update, soluzione, print_data

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

if 'modello_definito' not in st.session_state:
    st.session_state['modello_definito'] = False
if 'dati_modello' not in st.session_state:
    st.session_state['dati_modello'] = None
output_buffer = io.StringIO()
output_buffer.write("QUEUEING NETWORKS SOLUTION BASED UPON MEAN VALUE ANALYSIS\n\n")

if not st.session_state.modello_definito:
    azione = ""
    with st.container(border=True):
        st.session_state.dati_modello = read_data()
        print_data(output_buffer,st.session_state.dati_modello )
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



# Se modello non definito
if not st.session_state.modello_definito:
    st.session_state.dati_modello = read_data()
    print_data(output_buffer, st.session_state.dati_modello)
else:
    # Qui gestisci azioni
    if azione == "Aggiorna modello":
        st.session_state.dati_modello = update(st.session_state.dati_modello, output_buffer)
    elif azione == "Visualizza soluzione":
        if st.session_state.dati_modello is not None:
            soluzione(st.session_state.dati_modello, output_buffer)
        else:
            st.warning("Devi prima definire un modello.")
    else:
        print_data(output_buffer, st.session_state.dati_modello)

# Adesso il contenuto completo nel buffer
contenuto = output_buffer.getvalue()
st.session_state['output_file_content'] = contenuto

# Bottone di download
if contenuto:
    st.download_button(
        label=f"Scarica file {st.session_state.nome_file_output}",
        data=contenuto,
        file_name=st.session_state.get('nome_file_output', 'output.txt'),
        mime='text/plain'
    )
else:
    st.warning("Definire il nome del file")
