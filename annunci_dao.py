import sqlite3

def get_annunci():

    query = 'SELECT * FROM annunci ORDER BY prezzo DESC' #seleziona tutti i campi di tutti gli annunci in ordine di prezzo descrescente
    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    cursor.execute(query)

    annunci = cursor.fetchall()

    cursor.close()
    connection.close()
    
    return annunci


def get_annunci_ordinati_per_locali():

    query = 'SELECT * FROM annunci ORDER BY locali ASC' #seleziona tutti i campi di tutti gli annunci in ordine di locali crescenti
    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    cursor.execute(query)

    annunci = cursor.fetchall()
    print(annunci)

    cursor.close()
    connection.close()
    
    return annunci


def get_annuncio_by_id(id):

    query = 'SELECT * FROM annunci WHERE annunci.id = ?' #seleziona tutti i campi dell'annuncio che ha l'id passato come parametro 
    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    cursor.execute(query, (id,))

    annuncio = cursor.fetchone()
    print(annuncio)

    cursor.close()
    connection.close()
    
    return annuncio


def get_annunci_locatore(id_locatore):

    query = 'SELECT * FROM annunci LEFT JOIN utenti ON utenti.id = annunci.id_locatore WHERE utenti.id = ?' #seleziona tutti i campi dell'annuncio che ha l'id_locatore passato come parametro 
    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    cursor.execute(query, (id_locatore,))

    annunci = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return annunci



def add_annuncio(new_annuncio):

    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    last_id = None

    query = 'INSERT INTO annunci(titolo, tipologia, locali, descrizione, prezzo, arredata, disponibilita, indirizzo, id_locatore) VALUES (?,?,?,?,?,?,?,?,?)' #inserisce nella tabella 'annuncio' i campi del nuovo annuncio

    cursor.execute(query, (new_annuncio['titolo'], new_annuncio['tipologia'], new_annuncio['locali'], new_annuncio['descrizione'], new_annuncio['prezzo'], new_annuncio['arredata'], new_annuncio['disponibilita'], new_annuncio['indirizzo'], new_annuncio['id_locatore'],))

    try:
        connection.commit()
        last_id = cursor.lastrowid #prende l'ultimo id aggiunto nella tabella (ovvero l'id dell'annuncio appena creato)
    except Exception as e:
        print('ERROR', str(e))
        connection.rollback()
  
    cursor.close()
    connection.close()
    
    return last_id



def update_annuncio(annuncio):

    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    success = False
    
    query = 'UPDATE annunci SET titolo=?, tipologia=?, locali=?, descrizione=?, prezzo=?, arredata=?, disponibilita=? WHERE id=?' #aggiorna la tabella 'annunci' con i nuovi valori passati

    cursor.execute(query, (annuncio['titolo'], annuncio['tipologia'], annuncio['locali'], annuncio['descrizione'], annuncio['prezzo'], annuncio['arredata'], annuncio['disponibilita'], annuncio['id'],))

    try:
        connection.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        connection.rollback()
  
    cursor.close()
    connection.close()
    
    return success