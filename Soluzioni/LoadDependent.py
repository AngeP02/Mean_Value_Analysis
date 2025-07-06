import streamlit as st

from Utils.FunzioniStampa import printresults


def load_dependent(output_buffer, dati_mva):
    num_stazioni = dati_mva['num_stazioni']
    num_utenti = dati_mva['num_utenti']
    num_medio_visite = dati_mva['num_medio_visite']
    disciplina_servizio = dati_mva['discliplina_servizio']
    load_independence_indicator = dati_mva['load_independence_indicator']
    tempi_servizio_indipendenti = dati_mva['tempi_servizio_indipendenti']
    tempi_servizio_dipendenti = dati_mva['tempi_servizio_dipendenti']

    n_k_station = {}
    w_k_station = {}
    probabilita_stazione_clienti_sistema = {}
    for i in range(1, num_stazioni + 1):
        n_k_station[i] = []
        w_k_station[i] = []
        probabilita_stazione_clienti_sistema[i] = []
        for _ in range(num_utenti + 1):
            n_k_station[i].append(0.0)
            w_k_station[i].append(0.0)
            inner_list = []
            for __ in range(num_utenti + 1):
                inner_list.append(0.0)
            probabilita_stazione_clienti_sistema[i].append(inner_list)

    for i in range(1, num_stazioni + 1):
        probabilita_stazione_clienti_sistema[i][0][0] = 1.0

    for i in range(1, num_stazioni + 1):
        if i not in tempi_servizio_dipendenti:
            tempi_servizio_dipendenti[i] = {}
        tempi_servizio_dipendenti[i][0] = 0.0

    throughput_sistema_k = [0.0] * (num_utenti + 1)

    for k_utenti_sistema in range(1, num_utenti + 1):
        for i in range(1, num_stazioni + 1):
            if disciplina_servizio[i] == 0:
                w_k_station[i][k_utenti_sistema] = tempi_servizio_indipendenti.get(i,0.0)
            elif disciplina_servizio[i] == 1:
                if load_independence_indicator.get(i) == 'Si':
                    w_k_station[i][k_utenti_sistema] = tempi_servizio_indipendenti.get(i, 0.0) * (1 + n_k_station[i][k_utenti_sistema - 1])
                elif load_independence_indicator.get(i) == 'No':
                    expected_service_time_for_kth_customer = 0.0
                    for j_clienti_at_station in range(k_utenti_sistema):
                        service_time_at_current_load = tempi_servizio_dipendenti.get(i, {}).get(j_clienti_at_station + 1, 0.0)
                        expected_service_time_for_kth_customer += probabilita_stazione_clienti_sistema[i][j_clienti_at_station][k_utenti_sistema - 1] * service_time_at_current_load
                    w_k_station[i][k_utenti_sistema] = expected_service_time_for_kth_customer
        sum_V_W_current_k = sum(
            num_medio_visite.get(j, 0.0) * w_k_station[j][k_utenti_sistema] for j in range(1, num_stazioni + 1))
        if sum_V_W_current_k > 0:
            throughput_sistema_k[k_utenti_sistema] = k_utenti_sistema / sum_V_W_current_k
        else:
            throughput_sistema_k[k_utenti_sistema] = 0.0
        for i in range(1, num_stazioni + 1):
            n_k_station[i][k_utenti_sistema] = num_medio_visite.get(i, 0.0) *throughput_sistema_k[k_utenti_sistema] * w_k_station[i][k_utenti_sistema]
            if disciplina_servizio[i] == 1:
                current_prob_sum = 0.0
                for j_clients_at_station in range(k_utenti_sistema, 0, -1):
                    term_prob = 0.0
                    if load_independence_indicator.get(i) == 'No':
                        service_time_at_load_jp = tempi_servizio_dipendenti.get(i, {}).get(j_clients_at_station, 0.0)
                        if service_time_at_load_jp > 0:
                            term_prob = service_time_at_load_jp * throughput_sistema_k[k_utenti_sistema] * num_medio_visite.get(i, 0.0) * probabilita_stazione_clienti_sistema[i][j_clients_at_station - 1][k_utenti_sistema - 1]
                    else:
                        service_time_independent = tempi_servizio_indipendenti.get(i, 0.0)
                        term_prob = service_time_independent * throughput_sistema_k[k_utenti_sistema] * num_medio_visite.get(i, 0.0) * probabilita_stazione_clienti_sistema[i][j_clients_at_station - 1][k_utenti_sistema - 1]
                    probabilita_stazione_clienti_sistema[i][j_clients_at_station][k_utenti_sistema] = term_prob
                    current_prob_sum += term_prob
                probabilita_stazione_clienti_sistema[i][0][k_utenti_sistema] = 1.0 - current_prob_sum
                if probabilita_stazione_clienti_sistema[i][0][k_utenti_sistema] < 0:
                    st.warning(f"Probabilità negativa alla stazione {i}: {probabilita_stazione_clienti_sistema[i][0][k_utenti_sistema]:.5f}")
                    probabilita_stazione_clienti_sistema[i][0][k_utenti_sistema] = 0.0
                total_sum_for_station = sum(
                    probabilita_stazione_clienti_sistema[i][j][k_utenti_sistema] for j in range(k_utenti_sistema + 1))
                if total_sum_for_station > 0:
                    for j in range(k_utenti_sistema + 1):
                        probabilita_stazione_clienti_sistema[i][j][k_utenti_sistema] /= total_sum_for_station
                else:
                    probabilita_stazione_clienti_sistema[i][0][
                        k_utenti_sistema] = 1.0
    final_throughput_sistema = throughput_sistema_k[num_utenti]
    final_tempo_permanenza = sum(num_medio_visite.get(j, 0.0) * w_k_station[j][num_utenti] for j in range(1, num_stazioni + 1))

    final_utilizzazione = {}
    final_throughput_stazione = {}
    final_numero_medio_sistema = {}
    final_numero_medio_coda = {}
    final_tempo_medio_attesa_coda = {}
    prob_for_print = {i: {j: probabilita_stazione_clienti_sistema[i][j][num_utenti] for j in range(num_utenti + 1)} for i in range(1, num_stazioni + 1)}
    for i in range(1, num_stazioni + 1):
        final_throughput_stazione[i] = num_medio_visite.get(i, 0.0) * final_throughput_sistema
        final_numero_medio_sistema[i] = n_k_station[i][num_utenti]
        if load_independence_indicator.get(i) == 'Si':
            final_utilizzazione[i] = final_throughput_stazione[i] * tempi_servizio_indipendenti.get(i, 0.0)
        else:
            final_utilizzazione[i] = 1 - probabilita_stazione_clienti_sistema[i][0][num_utenti]
        final_numero_medio_coda[i] = final_numero_medio_sistema[i] - final_utilizzazione[i]
        if final_throughput_stazione[i] > 0:
            final_tempo_medio_attesa_coda[i] = final_numero_medio_coda[i] / final_throughput_stazione[i]
        else:
            final_tempo_medio_attesa_coda[i] = 0.0
        if final_numero_medio_coda[i] < 0:
            final_numero_medio_coda[i] = 0.0
        if final_tempo_medio_attesa_coda[i] < 0:
            final_tempo_medio_attesa_coda[i] = 0.0

    results_to_print = {
        'num_utenti': num_utenti,
        'num_stazioni': num_stazioni,
        'throughput_sistema': final_throughput_sistema,
        'tempo_permanenza': final_tempo_permanenza,
        'utilizzazione': final_utilizzazione,
        'throughput': final_throughput_stazione,
        'numero_medio_sistema': final_numero_medio_sistema,
        'numero_medio_coda': final_numero_medio_coda,
        'tempo_medio_attesa_coda': final_tempo_medio_attesa_coda,
        'probabilita': prob_for_print
    }
    printresults(results_to_print, output_buffer, "Load Dependent")
