# RegressionPlotly
Plugin QGIS Plugin che offfre analisi spaziali tramite modelli di regressione

Nella sua prima versione il plugin QGIS RegressionPlotly si compone di tre tabs all'interno di un dock:
1. Scatter Plot tab: disegna uno scatterplot selezionando due variabili da uno Shapefile o GPKG file
2. Regression Analysis tab: offre tecniche statistiche più avanzate, ricorrendo alla regressione lineare bivariata e multipla supportata visivamente da scatterplot; esporta GPGK file includendo valori stimati della regressione con relativa tematizzazione in un nuovo QGIS layer
3. CSV to Geopackage file Tool: esporta Geopackage file da un CSV

  
# 1. Scatter Plot tab
Nella schermata si può selezionare il layer tra quelli disponibili da cui attingere i dati con il dropdown "Select Layer", oppure si può importare un GPKG o SHP file tramite il bottone "Import Shapefile". Si consiglia di importare un GPKG invece che un SHP file, in quanto in questo modo si mantengono integri i nomi dei campi della tabella attributi. Se necessario si può fare un refresh dei layer disponibili con il pulsante "Refresh Layer".
Importato un GPKG o SHP idoneo, si può scegliere una variabile dipendente (Y) e una covariata (X) per la successiva produzione di uno scatterplot, tramite il bottone "Draw Scatter Plot", e per l'avvio di una piu' avanzata analisi di regressione, con il pulsante "To Regression Analysis".

# 2. Regression Analysis tab
Il tab offre al momento due opzioni di analisi di regressione ("Simple Linear Regression" e "Multiple Linear Regression") selezionabili dal dropdown piu' in alto.
Di default compare la prima opzione "Simple Linear Regression" con le stesse variabili X e Y passate dal precedente "Scatter Plot tab". Si può comunque selezionare una diversa variabile X e una Y, tramite i dropdown dedicati
Selezionando invece l'opzione "Multiple Linear Regression", il dropdown per la X viene sostituito da un multi-selettore per selezionare piu' variabili X. Premendo l'opzione "Select All", si selezionano tutte le variabili, tranne quella al momento selezionata nel dropdown della Y (per evitare ovviamente che una variabile venga spiegata da se stessa). Premendo un'altra volta "Select All" oppure il tasto a destra "Clear" si deselezionano tutte le variabili dal multi-selettore
Il dropdown "Geographic Label" permette di selezionare il nome geografico delle feature del layer e di default è il primo campo avente come valori stringhe.
Premendo il bottone in basso a sinistra "Start Regression Analysis" verranno compiuti i calcoli di regressione dopo dei quali verrà restituita una tabella rappresentante varie statistiche di regressione e verranno abilitati anche gli altri due bottoni in basso. Inoltre verrà prodotto uno scatterplot con le variabili X e Y nel caso dell'opzione "Simple Linear Regression". Se invece viene selezionata "Multiple Linear Regression" si produrrà un altro scatterplot che mette in relazione i valori osservati della Y con quelli stimati dalla regressione.
Il bottone in basso al centro "Show Fit and Residual Value Table" mostra i valori stimati dalla regressione, i residui, i reali valori della Y e i dati delle covariate utilizzate per ogni feature geografica.
Infine il bottone in basso a destra "Export GPKG file with Fit Statistics" aggiunge due colonne alla tabella degli attributi del file originale "Fitted values {dependent variable}" e "Residuals values {dependent variable}" e crea un nuovo layer QGIS tematizzando le stime della regressione. Viene inoltre offerta la possibilità di esportare un nuovo GPKG file, contenente anche i valori della regressione.

# 3. CSV to Geopackage file Tool
Il bottone in alto consente l'importazione di un CSV file. Avvenuta l'importazione, se il file contiene campi del tipo "lat" e "lon", questi verranno automaticamente assegnati ai successivi dropdown di scelta delle variabili considerate per la "Latitude" e "Longitude". I valori dei campi immessi in questi dropdown verranno utilizzati per produrre le geometrie puntuali del GPKG file. Con l'importazione si potrà anche vedere una tabella contente un fragment del dataset del CSV.
Il bottone "Create GPKG File" esporterà un GPKG File e aggiungerà un nuovo layer alla mappa, utilizzabile per le operazioni nei tabs 1. e 2.

# Note e Avvertenze
- Nella cartella sample_data del progetto si trovano un file CSV e uno GPKG, che sono stati impiegati per lo sviluppo del plugin. In particolare il file GPKG è stato ottenuto usando il "CSV to Geopackage file Tool". Il CSV è stato tratto dal dataset utilizzato per la pubblicazione "Planning a novel regional methane network: Demand forecasting and economic evaluation" di T. Barbiero e C. Grillenzoni
- Si sconsiglia al momento di importare nel plugin CSV o file geografici con dati mancanti o NULL, perché non verranno gestiti per le analisi di regressione. Si potranno introdurre strategie per risolvere il problema, come eliminare le righe con dati mancanti, oppure utilizzare questo stesso plugin per fornire stime di regressione per questi dati, e/o utilizzare algoritmi di interpolazione spaziale



