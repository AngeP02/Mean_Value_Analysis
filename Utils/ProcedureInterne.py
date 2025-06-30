import streamlit as st

import streamlit as st

from Utils.Utils import metriche_affidabilita_completamento, definizione_distribuzione_servizio


def read_data(output_buffer):
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
                        num_medio_visite[stazione] = st.number_input(f'Numero medio di visite)', min_value=0.0, format="%.4f", key=f'v_{stazione}')
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
                                sono_previsti_guasti[stazione] = st.radio(f'Occorrenza sono_previsti_guasti', options=['Si', 'No'], key=f'guasti_{stazione}')

                                if sono_previsti_guasti[stazione] == 'Si':
                                    st.write('Il tempo di servizio è considerato esponenziale.')
                                    distribuzione_servizio[stazione] = 0
                                    mean_time_to_failure[stazione] = st.number_input(f'Mean Time to Failure',min_value=0.0001, format="%.4f",key=f'mttf_{stazione}')
                                    mean_time_to_repair[stazione] = st.number_input(f'Mean Time to Repair',min_value=0.0001, format="%.4f", key=f'mttr_{stazione}')
                                    metriche_affidabilita_completamento(stazione, tempi_servizio_indipendenti, mean_time_to_failure, mean_time_to_repair)

                                else:
                                    tempi_servizio_indipendenti[stazione] = st.number_input( f'Tempo di thinking', min_value=0.0001, format="%.4f", key=f's_think_{stazione}')
                                    definizione_distribuzione_servizio(stazione, tempi_servizio_indipendenti, varianze, coefficienti_variazione, probabilita_branching, tasso_esponenziale1, tasso_esponenziale2)
                        else:
                            sono_previsti_guasti[stazione] = 'No'
                            load_independence_indicator[stazione] = 'Si'
                            tempi_servizio_indipendenti[stazione] = st.number_input(f'Tempo di thinking', min_value=0.0001, format="%.4f",key=f's_think_{stazione}')
                            definizione_distribuzione_servizio(stazione, tempi_servizio_indipendenti, varianze, coefficienti_variazione, probabilita_branching, tasso_esponenziale1, tasso_esponenziale2)

    return {
        'num_stazioni': num_stazioni, 'num_utenti': num_utenti,
        'num_medio_visite': num_medio_visite, 'discliplina_servizio': discliplina_servizio, 'load_independence_indicator': load_independence_indicator,
        'distribuzione_servizio': distribuzione_servizio, 'sono_previsti_guasti': sono_previsti_guasti,
        'tempi_servizio_dipendenti': tempi_servizio_dipendenti, 'tempi_servizio_indipendenti': tempi_servizio_indipendenti, 'carico_calcolato': carico_calcolato
    }


def print_data():
    print()

def soluzione(dati_modello, output_buffer):
    print()

def update(dati_modello, output_buffer):
    print()