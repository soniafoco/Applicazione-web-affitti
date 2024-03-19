import sqlite3

def get_foto_annuncio(id_annuncio):

    query = 'SELECT * FROM foto WHERE id_annuncio=?' #seleziona tutte le foto dell'annuncio
    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    cursor.execute(query, (id_annuncio,))

    foto = cursor.fetchall()

    cursor.close()
    connection.close()
    
    return foto


def add_foto(new_foto):

    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    success = False

    query = 'INSERT INTO foto(id_annuncio, foto_annuncio) VALUES (?,?)' #inserisce nella tabella 'foto' la nuova foto dell'annuncio

    cursor.execute(query, (new_foto['id_annuncio'], new_foto['foto_annuncio'],))
    try:
        connection.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        connection.rollback()
  
    cursor.close()
    connection.close()
    
    return success



def delete_foto(id_foto):

    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    success = False

    query = 'DELETE FROM foto WHERE id_foto=?' #rimuove dalla tabella 'foto' la foto con id_foto passato come parametro

    cursor.execute(query, (id_foto,))
    try:
        connection.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        connection.rollback()
  
    cursor.close()
    connection.close()
    
    return success



def update_foto(new_foto):

    connection = sqlite3.connect('db/db-affitti.db')
    connection.row_factory = sqlite3.Row  #converte la tupla a dizionario
    cursor = connection.cursor()

    success = False

    query = 'UPDATE foto SET foto_annuncio=? WHERE id_foto=?' #aggiorna la tabella 'foto' con le info della foto passate come parametro

    cursor.execute(query, (new_foto['foto_annuncio'], new_foto['id_foto'],))
    try:
        connection.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        connection.rollback()
  
    cursor.close()
    connection.close()
    
    return success
