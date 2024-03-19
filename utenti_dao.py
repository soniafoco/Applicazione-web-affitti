import sqlite3

def get_utente_by_email(email):

    query = 'SELECT * FROM utenti WHERE email = ?' #seleziona tutti i campi dell'utente che ha l'email passata come parametro 
    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    cursor.execute(query, (email,))

    utente = cursor.fetchone()

    cursor.close()
    connection.close()
    
    return utente


def get_utente_by_id(id):

    query = 'SELECT * FROM utenti WHERE id = ?' #seleziona tutti i campi dell'utente che ha l'id passato come parametro 
    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    cursor.execute(query, (id,))

    utente = cursor.fetchone()

    cursor.close()
    connection.close()
    
    return utente



def create_user(new_user):

    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    success = False
    
    query = 'INSERT INTO utenti(email, nome, cognome, password, tipologia_utente) VALUES (?,?,?,?,?)' #inserisce nella tabella 'utenti' i campi del nuovo utente 

    cursor.execute(query, (new_user['email'], new_user['nome'], new_user['cognome'], new_user['password'], new_user['tipologia_utente'],))

    try:
        connection.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        connection.rollback()
  
    cursor.close()
    connection.close()
    
    return success