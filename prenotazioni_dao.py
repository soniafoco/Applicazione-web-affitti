import sqlite3

def get_prenotazioni_annuncio(id_annuncio):

    query = 'SELECT prenotazioni.data, prenotazioni.orario, prenotazioni.stato, prenotazioni.id_utente FROM annunci LEFT JOIN prenotazioni ON prenotazioni.id_annuncio = annunci.id WHERE annunci.id = ?' #seleziona i campi delle prenotazioni per un certo immobile
    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    cursor.execute(query, (id_annuncio,))

    prenotazioni = cursor.fetchall()
    for campo in prenotazioni:
        print(campo)

    cursor.close()
    connection.close()
    
    return prenotazioni



def add_prenotazione(new_prenotazione):

    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    success = False
    
    query = 'INSERT INTO prenotazioni(modalita, data, orario, stato, id_utente, id_annuncio, id_locatore) VALUES (?,?,?,?,?,?,?)'

    cursor.execute(query, (new_prenotazione['modalita'], new_prenotazione['data'], new_prenotazione['orario'], new_prenotazione['stato'], new_prenotazione['id_utente'], new_prenotazione['id_annuncio'], new_prenotazione['id_locatore'],))

    try:
        connection.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        connection.rollback()
  
    cursor.close()
    connection.close()
    
    return success


def get_prenotazioni_utente(id_utente):

    query = 'SELECT * FROM prenotazioni LEFT JOIN annunci ON annunci.id = prenotazioni.id_annuncio WHERE id_utente = ? ORDER BY prenotazioni.data ASC' #seleziona i campi delle prenotazioni di un certo utente
    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    cursor.execute(query, (id_utente,))

    prenotazioni = cursor.fetchall()
    for campo in prenotazioni:
        print(campo)

    cursor.close()
    connection.close()
    
    return prenotazioni


def get_prenotazioni_locatore_ricevute(id_locatore):

    query = 'SELECT * FROM prenotazioni LEFT JOIN annunci ON annunci.id = prenotazioni.id_annuncio LEFT JOIN utenti ON utenti.id = prenotazioni.id_utente WHERE prenotazioni.id_locatore=? ORDER BY prenotazioni.data ASC' #seleziona i campi delle prenotazioni ricevute di un certo locatore
    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    cursor.execute(query, (id_locatore,))

    prenotazioni = cursor.fetchall()
    for campo in prenotazioni:
        print(campo)

    cursor.close()
    connection.close()
    
    return prenotazioni



def update_prenotazione(aggiornamento):

    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    success = False
    
    query = 'UPDATE prenotazioni SET stato=?, motivo_rifiuto=? WHERE id=?' #aggiorna la prenotazione

    cursor.execute(query, (aggiornamento['stato'], aggiornamento['motivo_rifiuto'], aggiornamento['id'],))

    try:
        connection.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        connection.rollback()
  
    cursor.close()
    connection.close()
    
    return success



def get_prenotazioni_locatore_filtrate(filtro):

    #seleziona i campi delle prenotazioni ricevute di un certo locatore, il cui stato è quello passato come parametro filtro['stato']
    query = 'SELECT * FROM prenotazioni LEFT JOIN annunci ON annunci.id = prenotazioni.id_annuncio LEFT JOIN utenti ON utenti.id = prenotazioni.id_utente WHERE prenotazioni.id_locatore=? AND prenotazioni.stato=? ORDER BY prenotazioni.data ASC' 
    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    cursor.execute(query, (filtro['id_locatore'], filtro['stato']))

    prenotazioni = cursor.fetchall()

    cursor.close()
    connection.close()
    
    return prenotazioni

