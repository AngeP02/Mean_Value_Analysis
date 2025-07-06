import streamlit as st

from Utils.FunzioniStampa import printresults


def approssimazione(output_buffer, dati_mva):
    num_stazioni = dati_mva['num_stazioni']
    num_utenti = dati_mva['num_utenti']
    num_medio_visite = dati_mva['num_medio_visite']
    tempi_servizio = dati_mva['tempi_servizio']
    disciplina_servizio = dati_mva['disciplina_servizio']
    varianze = dati_mva.get('varianze', {})


    tempo_medio_residuo = {}
    numero_medio_coda = {}
    utilizzazione = {}
    throughput = {}
    numero_medio_sistema = {}
    tempo_medio_attesa = {}
    tempo_medio_attesa_coda = {}

    somma_visite_servizio = 0.0
    for i in range(1, num_stazioni + 1):
        somma_visite_servizio += num_medio_visite.get(i, 0) * tempi_servizio.get(i, 0)

    while somma_visite_servizio == 0:
        st.warning("La somma di num_medio_visite[i]*tempi_servizio[i] è zero: controlla i dati di input!")

    for i in range(1, num_stazioni + 1):
        if disciplina_servizio[i] == 1:  # FCFS
            varianza_i = varianze.get(i)
            if varianza_i is None:
                st.warning(f"Non è stata fornita una varianza per la stazione {i}, allora si assume che sia una distribuzione esponenziale, e quindi si usa la varianza di un esponenziale, cioè tempi_servizio [stazione {i}] ** 2.")
                varianza_i = tempi_servizio[i] ** 2
            tempo_medio_residuo[i] = tempi_servizio[i] / 2 + varianza_i / (2 * tempi_servizio[i])
            numero_medio_coda[i] = 0.0
            utilizzazione[i] = num_medio_visite[i] * tempi_servizio[i] / somma_visite_servizio
        else:  # Infinite Server
            tempo_medio_residuo[i] = tempi_servizio[i]
            numero_medio_coda[i] = 0.0
            utilizzazione[i] = 0.0

    for j in range(1, num_utenti + 1):
        for i in range(1, num_stazioni + 1):
            if disciplina_servizio[i] == 1:
                if j == 1:
                    tempo_medio_attesa[i] = tempi_servizio[i]
                else:
                    tempo_medio_attesa[i] = tempi_servizio[i] + tempi_servizio[i] * numero_medio_coda[i] + tempo_medio_residuo[i] * utilizzazione[i]
            elif disciplina_servizio[i] == 0:
                tempo_medio_attesa[i] = tempi_servizio[i]

        tempo_permanenza = sum(num_medio_visite[i] * tempo_medio_attesa[i] for i in range(1, num_stazioni + 1))
        throughput_sistema = j / tempo_permanenza

        for i in range(1, num_stazioni + 1):
            throughput[i] = num_medio_visite[i] * throughput_sistema
            utilizzazione[i] = throughput[i] * tempi_servizio[i]
            numero_medio_sistema[i] = throughput[i] * tempo_medio_attesa[i]
            numero_medio_coda[i] = numero_medio_sistema[i] - utilizzazione[i]
            if throughput[i] == 0:
                st.warning(f"Attenzione: throughput[{i}] = 0 controllare dati modello.")
            while throughput[i] == 0:
                continue
            tempo_medio_attesa_coda[i] = numero_medio_coda[i] / throughput[i]


        st.session_state['risultati_mva'] = {
            'num_utenti': num_utenti,
            'num_stazioni': num_stazioni,
            'throughput_sistema': throughput_sistema,
            'tempo_permanenza': tempo_permanenza,
            'utilizzazione': utilizzazione,
            'throughput': throughput,
            'numero_medio_coda': numero_medio_coda,
            'tempo_medio_attesa_coda': tempo_medio_attesa_coda,
            'probabilita': {}
        }
    tipo_risultato = "Approssimazione"
    printresults(st.session_state['risultati_mva'], output_buffer, tipo_risultato)
