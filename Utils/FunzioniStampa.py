import copy
import streamlit as st


import pandas as pd
import streamlit as st

def innerprint(num_stazioni, paginazione, num_utenti, probabilita, output_buffer):
    colonne = [f"probabilità[{j}]" for j in range(num_utenti + 1)]
    stazioni = [f"Stazione {i}" for i in range(paginazione + 1, num_stazioni + 1)]
    dati = []
    for j in range(num_utenti + 1):
        riga = []
        for i in range(paginazione + 1, num_stazioni + 1):
            val = probabilita.get(i, {}).get(j, 0.0)
            riga.append(val)
        dati.append(riga)

    df = pd.DataFrame(dati, columns=stazioni, index=colonne)
    st.table(df.style.format("{:.5f}"))
    header = "probabilità | " + " | ".join(f"{s:>10}" for s in stazioni) + "\n"
    sep = "-" * len(header) + "\n"
    output_buffer.write(header)
    output_buffer.write(sep)
    for j, riga in enumerate(dati):
        line = f"[{j:2}]        | " + " | ".join(f"{val:10.5f}" for val in riga) + "\n"
        output_buffer.write(line)



def printproba(num_stazioni, num_utenti, probabilita, output_buffer):
    st.markdown("### Distribuzioni marginali delle stazioni")
    output_buffer.write("----- Distribuzioni Marginali delle stazioni -----\n\n")
    paginazione = 0
    while True:
        output_buffer.write("\n")
        if paginazione + 5 < num_stazioni:
            innerprint(paginazione + 5, paginazione, num_utenti, probabilita, output_buffer)
            paginazione += 5
        else:
            innerprint(num_stazioni, paginazione, num_utenti, probabilita, output_buffer)
            break

    probabilita_queue = copy.deepcopy(probabilita)
    for i in range(1, num_stazioni + 1):
        if i in probabilita_queue:
            probabilita_queue[i][0] = probabilita_queue[i].get(0, 0.0) + probabilita_queue[i].get(1, 0.0)
            for j in range(1, num_utenti):
                probabilita_queue[i][j] = probabilita_queue[i].get(j + 1, 0.0)
            probabilita_queue[i][num_utenti] = 0.0  # Warning: one server
    st.markdown("### Distribuzioni marginali delle code")
    output_buffer.write("----- Distribuzioni Marginali delle code -----\n\n")
    paginazione = 0
    while True:
        output_buffer.write("\n")
        if paginazione + 5 < num_stazioni:
            innerprint(paginazione + 5, paginazione, num_utenti, probabilita_queue, output_buffer)
            paginazione += 5
        else:
            innerprint(num_stazioni, paginazione, num_utenti, probabilita_queue, output_buffer)
            break


def printresults(dati, output_buffer):
    num_utenti = dati['num_utenti']
    num_stazioni = dati['num_stazioni']
    throughput_sistema = dati['throughput_sistema']
    tempo_permanenza = dati['tempo_permanenza']
    utilizzazione = dati['utilizzazione']
    throughput = dati['throughput']
    numero_medio_coda = dati['numero_medio_coda']
    tempo_medio_attesa_coda = dati['tempo_medio_attesa_coda']
    probabilita = dati['probabilita']

    with st.container(border=True):
        st.markdown(f"### **Risultati per {num_utenti} utenti**")
        col1,col2 = st.columns(2)
        with col1:
            st.markdown(f"#### **Throughput del sistema:** {throughput_sistema:.5f}")
        with col2:
            st.markdown(f"#### **Tempo medio nel sistema:** {tempo_permanenza:.5f}")

        header_tabella = (
            "| Stazione | % Occupazione | Throughput | Lunghezza coda | Ritardo in coda |\n"
            "|---------|---------|------------|--------------|-------------|"
        )
        righe_tabella = ""
        for i in range(1, num_stazioni + 1):
            righe_tabella += f"| {i:^7} | {utilizzazione[i]:>7.5f} | {throughput[i]:>10.5f} | {numero_medio_coda[i]:>12.5f} | {tempo_medio_attesa_coda[i]:>11.5f} |\n"

        st.markdown(header_tabella + "\n" + righe_tabella)

        output_buffer.write(f"\n***********  RISULTATI per {num_utenti:3} UTENTI  *******************\n\n")
        output_buffer.write(f"Throughput del sistema ..: {throughput_sistema:9.5f}\n")
        output_buffer.write(f"Tempo medio nel sistema ..: {tempo_permanenza:9.5f}\n\n")
        output_buffer.write("STAZIONE   %OCCUPAZIONE   THROUGHPUT   LUNGHEZZA CODA   RITARDO CODA\n")
        output_buffer.write("--------   ------------   ----------   --------------   ------------\n")
        for i in range(1, num_stazioni + 1):
            output_buffer.write( f"{i:3}       {utilizzazione[i]:9.5f}     {throughput[i]:9.5f}     {numero_medio_coda[i]:9.5f}     {tempo_medio_attesa_coda[i]:9.5f}\n")

        printproba(num_stazioni, num_utenti, probabilita, output_buffer)