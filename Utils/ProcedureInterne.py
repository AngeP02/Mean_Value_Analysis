import streamlit as st

from Soluzioni.Approssimazione import approssimazione
from Soluzioni.Bound import bound
from Soluzioni.Failure import failure
from Soluzioni.Large import large
from Soluzioni.LoadDependent import load_dependent
from Utils.Utils import metriche_affidabilita_completamento, definizione_distribuzione_servizio


def read_data():
    st.markdown("#### Definizione del nuovo modello")
    col1, col2 = st.columns(2)
    with col1:
        num_stazioni = st.number_input('Numero di stazioni', min_value=1, step=1)
    with col2:
        num_utenti = st.number_input('Numero totale di utenti', min_value=1, step=1)

    num_medio_visite = {}
    discliplina_servizio = {}
    load_independence_indicator = {}    # y = indipendente dal carico; n = dipendente dal carico
    distribuzione_servizio = {}
    sono_previsti_guasti = {}
    tempi_servizio_dipendenti = {}
    tempi_servizio_indipendenti = {}
    carico_calcolato = {}

    mean_time_to_failure = {}           # per stazione (tempo medio prima che un componente si guasti)
    mean_time_to_repair = {}            # per stazione (tempo medio per riparare il guasto)

    varianze = {}
    coefficienti_variazione = {}
    probabilita_branching = {}
    tasso_esponenziale1 = {}
    tasso_esponenziale2 = {}

    for row_start in range(0, num_stazioni, 3):
        cols = st.columns(3)
        for i in range(3):
            stazione_index = row_start + i
            if stazione_index < num_stazioni:
                with cols[i]:
                    with st.container(border=True):
                        stazione = stazione_index+1
                        st.markdown(f"##### Stazione {stazione}")
                        num_medio_visite[stazione] = st.number_input(f'Numero medio di visite', min_value=0.0, format="%.4f", key=f'v_{stazione}')
                        discliplina_servizio[stazione] = st.radio(f'Disciplina di servizio', options=[1, 0], format_func=lambda x: 'FCFS' if x == 1 else 'InfiniteServer', key=f'disc_{stazione}')

                        if discliplina_servizio[stazione] == 1:
                            load_independence_indicator[stazione] = st.radio(f'Server indipendente dal carico', options=['Si', 'No'], key=f'loind_{stazione}')

                            if load_independence_indicator[stazione] == 'No':
                                distribuzione_servizio[stazione] = 0
                                sono_previsti_guasti[stazione] = 'No'
                                st.write("Inserisci tempi di servizio esponenziali dipendenti dal carico:")
                                tempi_servizio_dipendenti[stazione] = {}
                                for row in range(0, num_utenti, 3):
                                    cols2 = st.columns(3)
                                    for j in range(3):
                                        utente_index = row + j
                                        if utente_index < num_utenti:
                                            with cols2[j]:
                                                utente = utente_index+1
                                                tempi_servizio_dipendenti[stazione][utente] = st.number_input(f'Utente {utente}', min_value=0.0001, format="%.4f",
                                                                                       key=f'seq_{stazione}_{utente}')
                            else:
                                tempi_servizio_indipendenti[stazione] = st.number_input(f'Tempo di servizio indipendente dal carico', min_value=0.0001, format="%.4f", key=f's_{stazione}')
                                carico_calcolato[i] = num_medio_visite[stazione] * tempi_servizio_indipendenti[stazione]
                                sono_previsti_guasti[stazione] = st.radio(f'Sono previsti guasti?', options=['Si', 'No'], index=1, key=f'guasti_{stazione}')

                                if sono_previsti_guasti[stazione] == 'Si':
                                    st.write('Il tempo di servizio è considerato esponenziale.')
                                    distribuzione_servizio[stazione] = 0
                                    mean_time_to_failure[stazione] = st.number_input(f'Mean Time to Failure',min_value=0.0001, format="%.4f",key=f'mttf_{stazione}')
                                    mean_time_to_repair[stazione] = st.number_input(f'Mean Time to Repair',min_value=0.0001, format="%.4f", key=f'mttr_{stazione}')
                                    metriche_affidabilita_completamento(stazione, tempi_servizio_indipendenti, mean_time_to_failure, mean_time_to_repair)

                                else:
                                    #tempi_servizio_indipendenti[stazione] = st.number_input( f'Tempo di thinking', min_value=0.0001, format="%.4f", key=f's_think_{stazione}')
                                    definizione_distribuzione_servizio(stazione, tempi_servizio_indipendenti, varianze, coefficienti_variazione, probabilita_branching, tasso_esponenziale1, tasso_esponenziale2)
                        else:
                            sono_previsti_guasti[stazione] = 'No'
                            load_independence_indicator[stazione] = 'Si'
                            tempi_servizio_indipendenti[stazione] = st.number_input(f'Tempo di thinking', min_value=0.0001, format="%.4f",key=f's_think_{stazione}')
                            definizione_distribuzione_servizio(stazione, tempi_servizio_indipendenti, varianze, coefficienti_variazione, probabilita_branching, tasso_esponenziale1, tasso_esponenziale2)

    return {
        'num_stazioni': num_stazioni,
        'num_utenti': num_utenti,
        'num_medio_visite': num_medio_visite,
        'discliplina_servizio': discliplina_servizio,
        'load_independence_indicator': load_independence_indicator,
        'distribuzione_servizio': distribuzione_servizio,
        'sono_previsti_guasti': sono_previsti_guasti,
        'tempi_servizio_dipendenti': tempi_servizio_dipendenti,
        'tempi_servizio_indipendenti': tempi_servizio_indipendenti,
        'carico_calcolato': carico_calcolato,
        'varianze': varianze,
        'coefficienti_variazione': coefficienti_variazione,
        'probabilita_branching': probabilita_branching,
        'tasso_esponenziale1': tasso_esponenziale1,
        'tasso_esponenziale2': tasso_esponenziale2,
        'mean_time_to_failure': mean_time_to_failure,
        'mean_time_to_repair': mean_time_to_repair,
    }


def print_data(buffer, dati_modello):
    def scrivi_riga(testo="", indent=0):
        buffer.write("    " * indent + testo + "\n")

    scrivi_riga("\n\n\n ******************* Parametri del Modello *******************\n")
    scrivi_riga(f"Numero stazioni: {dati_modello.get('num_stazioni', 'N/A')}")
    scrivi_riga(f"Numero totale utenti: {dati_modello.get('num_utenti', 'N/A')}")
    scrivi_riga()

    for stazione in range(1, dati_modello.get('num_stazioni', 0) + 1):
        scrivi_riga(f"--- Stazione {stazione} ---")
        scrivi_riga(f"Numero medio visite: {dati_modello['num_medio_visite'].get(stazione, 'N/A')}", 1)

        disciplina = dati_modello['discliplina_servizio'].get(stazione, 'N/A')
        disciplina_str = 'FCFS' if disciplina == 1 else ('InfiniteServer' if disciplina == 0 else disciplina)
        scrivi_riga(f"Disciplina servizio: {disciplina_str}", 1)

        load_ind = dati_modello['load_independence_indicator'].get(stazione, 'N/A')
        scrivi_riga(f"Server indipendente dal carico: {load_ind}", 1)

        guasti = dati_modello['sono_previsti_guasti'].get(stazione, 'N/A')
        scrivi_riga(f"Sono previsti guasti: {guasti}", 1)

        if stazione in dati_modello['tempi_servizio_dipendenti']:
            scrivi_riga(f"Tempi servizio dipendenti dal carico per utenti:", 1)
            tempi_dip = dati_modello['tempi_servizio_dipendenti'][stazione]
            for utente, tempo in tempi_dip.items():
                scrivi_riga(f"Utente {utente}: {tempo:.4f}", 2)
        elif stazione in dati_modello['tempi_servizio_indipendenti']:
            tempo_ind = dati_modello['tempi_servizio_indipendenti'][stazione]
            scrivi_riga(f"Tempo servizio indipendente dal carico: {tempo_ind:.4f}", 1)

        carico = dati_modello['carico_calcolato'].get(stazione - 1, None)  # nota: in codice carico_calcolato usa i
        if carico is not None:
            scrivi_riga(f"Carico calcolato: {carico:.4f}", 1)

        varianza = dati_modello['varianze'].get(stazione, None)
        cv2 = dati_modello['coefficienti_variazione'].get(stazione, None)
        if varianza is not None and cv2 is not None:
            scrivi_riga(f"Varianza: {varianza:.5f}", 1)
            scrivi_riga(f"Coefficiente di variazione al quadrato (CV²): {cv2:.5f}", 1)

        if guasti == 'Si':
            mttf = dati_modello['mean_time_to_failure'].get(stazione, None)
            mttr = dati_modello['mean_time_to_repair'].get(stazione, None)
            if mttf is not None and mttr is not None:
                scrivi_riga(f"Mean Time To Failure (MTTF): {mttf:.4f}", 1)
                scrivi_riga(f"Mean Time To Repair (MTTR): {mttr:.4f}", 1)

        scrivi_riga()

    scrivi_riga("### Fine dati modello ###")

def soluzione(dati_modello, output_buffer):
    css = """
    <style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
      font-size: 15px;
      margin-right: 10px;
      padding: 8px 80px;  
      color: black;
    }
    button[data-baseweb="tab"] {
        margin-right: 8px;
        padding: 10px 2px;
        border-radius: 8px;
        transition: all 0.2s ease-in-out;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #f0b37a;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    sezione1, sezione2, sezione3, sezione4, sezione5 = st.tabs(
        ["Approssimazione", "Load Dependent", "Large", "Bound", "Failure"])

    with sezione1:
        dati_mva = {
            'num_stazioni': dati_modello['num_stazioni'],
            'num_utenti': dati_modello['num_utenti'],
            'num_medio_visite': dati_modello['num_medio_visite'],
            'tempi_servizio': dati_modello['tempi_servizio_indipendenti'],
            'disciplina_servizio': dati_modello['discliplina_servizio'],
            'varianze': {int(k): v for k, v in dati_modello['varianze'].items()}
        }
        approssimazione(output_buffer, dati_mva)

    with sezione2:
        dati_mva = {
            'num_stazioni': dati_modello['num_stazioni'],
            'num_utenti': dati_modello['num_utenti'],
            'num_medio_visite': dati_modello['num_medio_visite'],
            'tempi_servizio': dati_modello['tempi_servizio_indipendenti'],
            'disciplina_servizio': dati_modello['discliplina_servizio'],
            'varianze': {int(k): v for k, v in dati_modello['varianze'].items()},
            'tempi_servizio_dipendenti': dati_modello['tempi_servizio_dipendenti'],
            'tempi_servizio_indipendenti': dati_modello['tempi_servizio_indipendenti'],
            'discliplina_servizio': dati_modello['discliplina_servizio'],
            'load_independence_indicator': dati_modello['load_independence_indicator']  # AGGIUNGI QUESTA RIGA
        }
        load_dependent(output_buffer, dati_mva)
    with sezione3:
        large(output_buffer, dati_mva)
    with sezione4:
        bound(output_buffer)
    with sezione5:
        failure(output_buffer)

def aggiorna(dati_modello):
    st.markdown("#### Modifica del modello esistente")

    col1, col2 = st.columns(2)
    with col1:
        num_stazioni = st.number_input('Numero di stazioni', min_value=1, step=1, value=dati_modello['num_stazioni'])
    with col2:
        num_utenti = st.number_input('Numero totale di utenti', min_value=1, step=1, value=dati_modello['num_utenti'])

    num_medio_visite = {}
    discliplina_servizio = {}
    load_independence_indicator = {}
    distribuzione_servizio = {}
    sono_previsti_guasti = {}
    tempi_servizio_dipendenti = {}
    tempi_servizio_indipendenti = {}
    carico_calcolato = {}

    mean_time_to_failure = {}
    mean_time_to_repair = {}
    varianze = {}
    coefficienti_variazione = {}
    probabilita_branching = {}
    tasso_esponenziale1 = {}
    tasso_esponenziale2 = {}

    for row_start in range(0, num_stazioni, 3):
        cols = st.columns(3)
        for i in range(3):
            stazione_index = row_start + i
            if stazione_index < num_stazioni:
                with cols[i]:
                    with st.container(border=True):
                        stazione = stazione_index + 1
                        st.markdown(f"##### Stazione {stazione}")
                        num_medio_visite[stazione] = st.number_input(
                            f'Numero medio di visite',
                            min_value=0.0,
                            format="%.4f",
                            value=dati_modello['num_medio_visite'].get(stazione, 0.0),
                            key=f'v_{stazione}'
                        )

                        discliplina_servizio[stazione] = st.radio(
                            f'Disciplina di servizio',
                            options=[1, 0],
                            format_func=lambda x: 'FCFS' if x == 1 else 'InfiniteServer',
                            index=[1, 0].index(dati_modello['discliplina_servizio'].get(stazione, 1)),
                            key=f'disc_{stazione}'
                        )

                        if discliplina_servizio[stazione] == 1:
                            load_independence_indicator[stazione] = st.radio(
                                f'Server indipendente dal carico',
                                options=['Si', 'No'],
                                index=['Si', 'No'].index(dati_modello['load_independence_indicator'].get(stazione, 'Si')),
                                key=f'loind_{stazione}'
                            )

                            if load_independence_indicator[stazione] == 'No':
                                distribuzione_servizio[stazione] = 0
                                sono_previsti_guasti[stazione] = 'No'
                                st.write("Inserisci tempi di servizio esponenziali dipendenti dal carico:")
                                tempi_servizio_dipendenti[stazione] = {}
                                for row in range(0, num_utenti, 3):
                                    cols2 = st.columns(3)
                                    for j in range(3):
                                        utente_index = row + j
                                        if utente_index < num_utenti:
                                            utente = utente_index + 1
                                            tempi_servizio_dipendenti[stazione][utente] = st.number_input(
                                                f'Utente {utente}',
                                                min_value=0.0001,
                                                format="%.4f",
                                                value=dati_modello['tempi_servizio_dipendenti']
                                                    .get(stazione, {})
                                                    .get(utente, 0.0001),
                                                key=f'seq_{stazione}_{utente}'
                                            )
                            else:
                                tempi_servizio_indipendenti[stazione] = st.number_input(
                                    f'Tempo di servizio indipendente dal carico',
                                    min_value=0.0001,
                                    format="%.4f",
                                    value=dati_modello['tempi_servizio_indipendenti'].get(stazione, 0.0001),
                                    key=f's_{stazione}'
                                )
                                carico_calcolato[i] = num_medio_visite[stazione] * tempi_servizio_indipendenti[stazione]

                                sono_previsti_guasti[stazione] = st.radio(
                                    f'Sono previsti guasti?',
                                    options=['Si', 'No'],
                                    index=['Si', 'No'].index(dati_modello['sono_previsti_guasti'].get(stazione, 'No')),
                                    key=f'guasti_{stazione}'
                                )

                                if sono_previsti_guasti[stazione] == 'Si':
                                    distribuzione_servizio[stazione] = 0
                                    mean_time_to_failure[stazione] = st.number_input(
                                        f'Mean Time to Failure',
                                        min_value=0.0001,
                                        format="%.4f",
                                        value=dati_modello['mean_time_to_failure'].get(stazione, 1.0),
                                        key=f'mttf_{stazione}'
                                    )
                                    mean_time_to_repair[stazione] = st.number_input(
                                        f'Mean Time to Repair',
                                        min_value=0.0001,
                                        format="%.4f",
                                        value=dati_modello['mean_time_to_repair'].get(stazione, 1.0),
                                        key=f'mttr_{stazione}'
                                    )
                                    metriche_affidabilita_completamento(stazione, tempi_servizio_indipendenti,
                                                                        mean_time_to_failure, mean_time_to_repair)
                                else:
                                    definizione_distribuzione_servizio(stazione, tempi_servizio_indipendenti,
                                                                       varianze, coefficienti_variazione,
                                                                       probabilita_branching,
                                                                       tasso_esponenziale1, tasso_esponenziale2)
                        else:
                            sono_previsti_guasti[stazione] = 'No'
                            load_independence_indicator[stazione] = 'Si'
                            tempi_servizio_indipendenti[stazione] = st.number_input(
                                f'Tempo di thinking',
                                min_value=0.0001,
                                format="%.4f",
                                value=dati_modello['tempi_servizio_indipendenti'].get(stazione, 0.0001),
                                key=f's_think_{stazione}'
                            )
                            definizione_distribuzione_servizio(stazione, tempi_servizio_indipendenti,
                                                               varianze, coefficienti_variazione,
                                                               probabilita_branching,
                                                               tasso_esponenziale1, tasso_esponenziale2)

    dati_modello_aggiornato = {
        'num_stazioni': num_stazioni,
        'num_utenti': num_utenti,
        'num_medio_visite': num_medio_visite,
        'discliplina_servizio': discliplina_servizio,
        'load_independence_indicator': load_independence_indicator,
        'distribuzione_servizio': distribuzione_servizio,
        'sono_previsti_guasti': sono_previsti_guasti,
        'tempi_servizio_dipendenti': tempi_servizio_dipendenti,
        'tempi_servizio_indipendenti': tempi_servizio_indipendenti,
        'carico_calcolato': carico_calcolato,
        'varianze': varianze,
        'coefficienti_variazione': coefficienti_variazione,
        'probabilita_branching': probabilita_branching,
        'tasso_esponenziale1': tasso_esponenziale1,
        'tasso_esponenziale2': tasso_esponenziale2,
        'mean_time_to_failure': mean_time_to_failure,
        'mean_time_to_repair': mean_time_to_repair,
    }


    return dati_modello_aggiornato
