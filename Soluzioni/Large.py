import streamlit as st

from Utils.FunzioniStampa import printresults


def large(output_buffer, dati_mva):
    num_stazioni = dati_mva['num_stazioni']
    num_utenti = dati_mva['num_utenti']
    num_medio_visite = dati_mva['num_medio_visite']
    tempi_servizio = dati_mva['tempi_servizio']
    disciplina_servizio = dati_mva['disciplina_servizio']

    epsilon = 0.000000001
    max_iterations = 200

    tempo_medio_attesa = {}
    numero_medio_sistema = {}
    old_n = {}
    throughput = {}
    utilizzazione = {}
    numero_medio_coda = {}
    tempo_medio_attesa_coda = {}
    for i in range(1, num_stazioni+1):
        old_n[i] = 0.0
        throughput[i] = 0.0
        utilizzazione[i] = 0.0
        numero_medio_coda[i] = 0.0
        tempo_medio_attesa_coda[i] = 0.0
        tempo_medio_attesa[i] = tempi_servizio.get(i, 0.0)
        if num_stazioni > 0:
            numero_medio_sistema[i] = num_utenti / num_stazioni
        else:
            numero_medio_sistema[i] = 0.0
    iteration_number = 0
    convergence_flag = False

    while not convergence_flag and iteration_number <= max_iterations:
        convergence_flag = True
        for i in range(1, num_stazioni + 1):
            if disciplina_servizio.get(i) == 1:  # FCFS
                term = 0.0
                if num_utenti > 0:
                    term = (num_utenti - 1) / num_utenti
                tempo_medio_attesa[i] = tempi_servizio.get(i, 0.0) * (1 + term * numero_medio_sistema[i])
            else:  # Infinite Server
                tempo_medio_attesa[i] = tempi_servizio.get(i, 0.0)
        wtot_current = sum(num_medio_visite.get(l, 0.0) * tempo_medio_attesa[l] for l in range(1, num_stazioni + 1))
        if wtot_current == 0:
            st.warning( "ATTENZIONE: Il tempo totale di permanenza nel sistema (wtot) è zero per il Metodo 1. Controlla i dati di input.")
            break
        throughput_sistema_current = num_utenti / wtot_current
        for i in range(1, num_stazioni + 1):
            throughput[i] = throughput_sistema_current * num_medio_visite.get(i, 0.0)
            old_n[i] = numero_medio_sistema[i]
            numero_medio_sistema[i] = tempo_medio_attesa[i] * throughput[i]
        iteration_number += 1
        for i in range(1, num_stazioni + 1):
            if (old_n[i] - numero_medio_sistema[i]) ** 2 > epsilon:
                convergence_flag = False
                break
    output_buffer.write(f"Numero di iterazioni (Metodo 1): {iteration_number}\n\n")
    for i in range(1, num_stazioni + 1):
        utilizzazione[i] = throughput[i] * tempi_servizio.get(i, 0.0)
        numero_medio_coda[i] = numero_medio_sistema[i] - utilizzazione[i]
        if throughput[i] > 0:
            tempo_medio_attesa_coda[i] = numero_medio_coda[i] / throughput[i]
        else:
            tempo_medio_attesa_coda[i] = 0.0
        if numero_medio_coda[i] < 0:
            numero_medio_coda[i] = 0.0
        if tempo_medio_attesa_coda[i] < 0:
            tempo_medio_attesa_coda[i] = 0.0

    results_to_print_1 = {
        'num_utenti': num_utenti,
        'num_stazioni': num_stazioni,
        'throughput_sistema': throughput_sistema_current,
        'tempo_permanenza': wtot_current,
        'utilizzazione': utilizzazione,
        'throughput': throughput,
        'numero_medio_sistema': numero_medio_sistema,
        'numero_medio_coda': numero_medio_coda,
        'tempo_medio_attesa_coda': tempo_medio_attesa_coda,
        'probabilita': None,
        'num_iterazioni': iteration_number
    }
    printresults(results_to_print_1, output_buffer, "Large (Metodo 1)")

    for i in range(1, num_stazioni + 1):
        tempo_medio_attesa[i] = tempi_servizio.get(i, 0.0)
        if num_stazioni > 0:
            numero_medio_sistema[i] = num_utenti / num_stazioni
        else:
            numero_medio_sistema[i] = 0.0
    iteration_number = 0
    convergence_flag = False
    wtot_current = 0.0
    while not convergence_flag and iteration_number <= max_iterations:
        convergence_flag = True
        if iteration_number == 0:
            wtot_current = sum(num_medio_visite.get(l, 0.0) * tempo_medio_attesa[l] for l in range(1, num_stazioni + 1))
            if wtot_current == 0:
                st.warning("ATTENZIONE: wtot iniziale è zero per il Metodo 2. Controlla i dati di input.")
                break
        for i in range(1, num_stazioni + 1):
            if disciplina_servizio.get(i) == 1:  # FCFS
                term = 0.0
                if wtot_current > 0:
                    term = num_medio_visite.get(i, 0.0) * tempo_medio_attesa[i] / wtot_current
                tempo_medio_attesa[i] = tempi_servizio.get(i, 0.0) * (1 + numero_medio_sistema[i] - term)
            else:  # IS
                tempo_medio_attesa[i] = tempi_servizio.get(i, 0.0)
        wtot_current = sum(num_medio_visite.get(l, 0.0) * tempo_medio_attesa[l] for l in range(1, num_stazioni + 1))
        if wtot_current == 0:
            st.warning(
                "ATTENZIONE: Il tempo totale di permanenza nel sistema (wtot) è zero per il Metodo 2. Controlla i dati di input.")
            break
        throughput_sistema_current = num_utenti / wtot_current
        for i in range(1, num_stazioni + 1):
            throughput[i] = throughput_sistema_current * num_medio_visite.get(i, 0.0)
            old_n[i] = numero_medio_sistema[i]
            numero_medio_sistema[i] = tempo_medio_attesa[i] * throughput[i]
        iteration_number += 1
        for i in range(1, num_stazioni + 1):
            if (old_n[i] - numero_medio_sistema[i]) ** 2 > epsilon:
                convergence_flag = False
                break
    output_buffer.write(f"Numero di iterazioni (Metodo 2): {iteration_number}\n\n")
    for i in range(1, num_stazioni + 1):
        utilizzazione[i] = throughput[i] * tempi_servizio.get(i, 0.0)
        numero_medio_coda[i] = numero_medio_sistema[i] - utilizzazione[i]
        if throughput[i] > 0:
            tempo_medio_attesa_coda[i] = numero_medio_coda[i] / throughput[i]
        else:
            tempo_medio_attesa_coda[i] = 0.0
        if numero_medio_coda[i] < 0:
            numero_medio_coda[i] = 0.0
        if tempo_medio_attesa_coda[i] < 0:
            tempo_medio_attesa_coda[i] = 0.0
    results_to_print_2 = {
        'num_utenti': num_utenti,
        'num_stazioni': num_stazioni,
        'throughput_sistema': throughput_sistema_current,
        'tempo_permanenza': wtot_current,
        'utilizzazione': utilizzazione,
        'throughput': throughput,
        'numero_medio_sistema': numero_medio_sistema,
        'numero_medio_coda': numero_medio_coda,
        'tempo_medio_attesa_coda': tempo_medio_attesa_coda,
        'probabilita': None,
        'num_iterazioni': iteration_number
    }
    printresults(results_to_print_2, output_buffer, "Large (Metodo 2)")