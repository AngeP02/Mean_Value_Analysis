import math
import streamlit as st
import pandas as pd

def esponenziale(stazione, tempi_servizio, varianze, coefficienti_variazione):
    varianze[stazione] = tempi_servizio[stazione] ** 2
    coefficienti_variazione[stazione] = varianze[stazione] / (tempi_servizio[stazione] ** 2)
    st.write(f"Distribuzione esponenziale: varianza: {varianze[stazione]:.5f}, CV²={coefficienti_variazione[stazione]:.5f}")

def erlang(stazione, tempi_servizio, varianze, coefficienti_variazione):
    ordine = st.number_input(f'Valore ordine Erlang', min_value=1, step=1, key=f'kappa_{stazione}')
    if ordine > 0:
        varianze[stazione] = tempi_servizio[stazione] ** 2 / ordine
        coefficienti_variazione[stazione] = varianze[stazione] / (tempi_servizio[stazione] ** 2)
        st.write(f"Distribuzione Erlang: varianza={varianze[stazione]:.5f}, CV²={coefficienti_variazione[stazione]:.5f}")

def iperesponenziale(stazione, tempi_servizio_indipendenti, varianze, coefficienti_variazione, probabilita_branching, tasso_esponenziale1, tasso_esponenziale2):
    coefficiente_quadrato = st.number_input(f'Valore del quadrato del coefficiente di varianza (CV²)', min_value=1.0, format="%.4f", key=f'iperexp_coeff_{stazione}')
    if coefficiente_quadrato > 1:
        coefficienti_variazione[stazione] = coefficiente_quadrato
        varianze[stazione] = tempi_servizio_indipendenti[stazione] ** 2 * coefficiente_quadrato
        utile = 2 / (1 + coefficiente_quadrato)
        utile = math.sqrt(1 - utile)
        probabilita_branching[stazione] = coefficiente_quadrato * (1 - utile)
        tasso_esponenziale1[stazione] = (1 + utile) / tempi_servizio_indipendenti[stazione]
        tasso_esponenziale2[stazione] = (1 - utile) / tempi_servizio_indipendenti[stazione]
        st.write(f"Distribuzione iper-esponenziale:")
        st.write(f"  Varianza = {varianze[stazione]:.5f}")
        st.write(f"  Probabilità branching = {probabilita_branching[stazione]:.5f}")
        st.write(f"  Tasso primo esponenziale = {tasso_esponenziale1[stazione]:.5f}")
        st.write(f"  Tasso secondo esponenziale = {tasso_esponenziale2[stazione]:.5f}")
    else:
        st.warning("Il coefficiente di variazione al quadrato deve essere > 1 per iper-esponenziale.")


def metriche_affidabilita_completamento(stazione, tempi_servizio_indipendenti, mean_time_to_failure, mean_time_to_repair):      #defcompletion
    steady_state_availability = mean_time_to_failure[stazione] / (mean_time_to_failure[stazione] + mean_time_to_repair[stazione])
    tasso_guasto_servente = 1 / mean_time_to_failure[stazione]
    tasso_servizio_servente = 1 / tempi_servizio_indipendenti[stazione]
    tempo_medio_prima_evento = 1 / (tasso_guasto_servente + tasso_servizio_servente)
    probabilita_uscita = tasso_servizio_servente / (tasso_servizio_servente + tasso_guasto_servente)
    parametro_secondo_stadio = 1 / mean_time_to_repair[stazione] + tempo_medio_prima_evento
    '''
    tasso_riparazione = 1 / mean_time_to_repair[stazione]
    st.write(f"Tasso di riparazione (1/MTTR): {tasso_riparazione:.5f}")
    st.write(f"Tempo medio prima evento (age): {tempo_medio_prima_evento:.5f}")
    st.write(f"Parametro secondo stadio esponenziale (somma): {tasso_riparazione + tempo_medio_prima_evento:.5f}")
    '''
    tempo_medio_completamento_servizio = tempo_medio_prima_evento + tempi_servizio_indipendenti[stazione] * tasso_guasto_servente * (mean_time_to_repair[stazione] + tempo_medio_prima_evento)
    varianza_tempo_esatto_completamento = (tempo_medio_prima_evento ** 2) + (tempi_servizio_indipendenti[stazione] * tasso_guasto_servente) ** 2 * (mean_time_to_repair[stazione] ** 2) + (tempi_servizio_indipendenti[stazione] * tasso_guasto_servente) ** 2 * (tempo_medio_prima_evento ** 2)
    coefficiente_quadratico_variazione = varianza_tempo_esatto_completamento / (tempo_medio_completamento_servizio ** 2)

    dati = {
        "Metrica": [
            "Disponibilità a regime (steady state availability)",
            "Tasso di guasto (failure rate)",
            "Tasso di servizio (service rate)",
            "Tempo medio prima evento (age)",
            "Probabilità di uscita con successo",
            "Parametro secondo stadio esponenziale",
            "Tempo medio preciso di completamento",
            "Varianza del tempo preciso di completamento",
            "Coefficiente quadratico di variazione",
        ],
        "Valore": [
            f"{steady_state_availability:.3f}",
            f"{tasso_guasto_servente:.5f}",
            f"{tasso_servizio_servente:.5f}",
            f"{tempo_medio_prima_evento:.5f}",
            f"{probabilita_uscita:.5f}",
            f"{parametro_secondo_stadio:.5f}",
            f"{tempo_medio_completamento_servizio:.5f}",
            f"{varianza_tempo_esatto_completamento:.5f}",
            f"{coefficiente_quadratico_variazione:.5f}",
        ],
    }

    df = pd.DataFrame(dati)
    st.table(df)

    return {
        'steady_state_availability': steady_state_availability,
        'tasso_guasto_servente': tasso_guasto_servente,
        'tasso_servizio_servente': tasso_servizio_servente,
        'tempo_medio_prima_evento': tempo_medio_prima_evento,
        'probabilita_uscita': probabilita_uscita,
        'tempo_medio_completamento_servizio': tempo_medio_completamento_servizio,
        'varianza_tempo_esatto_completamento': varianza_tempo_esatto_completamento,
        'coefficiente_quadratico_variazione': coefficiente_quadratico_variazione
    }


def definizione_distribuzione_servizio(stazione, tempi_servizio_indipendenti, varianze, coefficienti_variazione, probabilita_branching, tasso_esponenziale1, tasso_esponenziale2):
    distribuzione = st.selectbox(f'Tipo di distribuzione', options=[0, 1, 2, 3],format_func=lambda x: {0: 'Esponenziale', 1: 'Erlang', 2: 'Iperesponenziale', 3: 'Personalizzata'}[x], key=f'distr_{stazione}')
    if distribuzione == 0:
        esponenziale(stazione, tempi_servizio_indipendenti, varianze, coefficienti_variazione)
    elif distribuzione == 1:
        erlang(stazione, tempi_servizio_indipendenti, varianze, coefficienti_variazione)
    elif distribuzione == 2:
        iperesponenziale(stazione, tempi_servizio_indipendenti, varianze, coefficienti_variazione, probabilita_branching, tasso_esponenziale1, tasso_esponenziale2)
    elif distribuzione == 3:
        coeff_i = st.number_input(f'Inserisci il coefficiente di variazione al quadrato (CV²)', min_value=0.0, format="%.4f", key=f'gen_coeff_{stazione}')
        coefficienti_variazione[stazione] = coeff_i
        varianze[stazione] = coeff_i * (tempi_servizio_indipendenti[stazione] ** 2)
        st.write(f"Distribuzione generica con CV²: {coefficienti_variazione[stazione]:.5f}, varianza: {varianze[stazione]:.5f}")

