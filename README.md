# Mean Value Analysis (MVA)

Applicazione web interattiva per l'analisi di reti di code chiuse, sviluppata con Streamlit. Permette di modellare sistemi con più stazioni di servizio, definire i parametri del modello e ottenere la soluzione tramite diversi metodi basati sulla Mean Value Analysis.

Progetto sviluppato per il corso di **Processi Aleatori e Valutazione delle Prestazioni**

## Funzionalità

- **Definizione del modello**: numero di stazioni, numero di utenti, numero medio di visite, disciplina di servizio (FCFS o Infinite Server)
- **Distribuzione del servizio**: esponenziale, Erlang, iper-esponenziale o personalizzata (tramite CV²)
- **Gestione dei guasti**: MTTF e MTTR per stazione, con calcolo automatico delle metriche di affidabilità
- **Server load-dependent**: tempi di servizio che variano in base al numero di utenti presenti alla stazione
- **Metodi di soluzione**:
  - *Approssimazione* – versione semplificata dell'MVA esatto
  - *Load Dependent* – MVA esatto con supporto a stazioni dipendenti dal carico
  - *Large* – due varianti iterative per sistemi con molti utenti (Metodo 1 e Metodo 2)
  - *Bound* – (da sviluppare)
  - *Failure* – (da sviluppare)
- **Aggiornamento del modello**: modifica dei parametri senza perdere la sessione
- **Export dell'output**: scarica un file `.txt` con tutti i risultati

Per ogni metodo di soluzione vengono riportati:
- Throughput del sistema
- Tempo medio nel sistema
- Per ogni stazione: utilizzazione, throughput, lunghezza media della coda, ritardo medio in coda
