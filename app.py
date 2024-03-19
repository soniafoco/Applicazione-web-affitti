from datetime import date, timedelta, datetime
import datetime
from flask import Flask, flash, render_template, request, redirect, url_for
import annunci_dao, utenti_dao, prenotazioni_dao, foto_dao
from models import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from PIL import Image

# creo l'applicazione
app = Flask(__name__)
app.config['SECRET_KEY']='my secret key'


login_manager = LoginManager() #creo un'oggetto LoginManager
login_manager.init_app(app)



# definisce la home 
@app.route('/')
def home():
    
    ordina = request.args.get('ordina')
    print(ordina)

    if not ordina:
        annunci_db = annunci_dao.get_annunci()
        ordina = 0
    elif int(ordina)==1:
        annunci_db = annunci_dao.get_annunci_ordinati_per_locali()
    
    annunci = [dict(row) for row in annunci_db] #copia i dati ottenuti dal db in una lista di dizionari, in modo che siano modificabili

    for annuncio in annunci:
        foto_db = foto_dao.get_foto_annuncio(annuncio['id']) #prende le foto della tabella 'foto' associate al id_annunci0
        if (len(foto_db)>0):
            foto_list=[]
            for foto in foto_db:
                foto_list.append(foto['foto_annuncio'])
        annuncio['foto']=foto_list

    return render_template('home.html', annunci = annunci , ordinamento = ordina)



# definisce la pagina del singolo annuncio
@app.route('/annuncio/<int:id>')
def annuncio(id):

    annuncio_db = annunci_dao.get_annuncio_by_id(id)
    annuncio = dict(annuncio_db) #copia i dati ottenuti dal db in un dizionario, in modo che siano modificabili
    prenotazioni_db = prenotazioni_dao.get_prenotazioni_annuncio(id)
    email_locatore = utenti_dao.get_utente_by_id(annuncio_db['id_locatore'])['email']

    foto_db = foto_dao.get_foto_annuncio(annuncio['id']) #prende le foto della tabella 'foto' associate al id_annunci0
    if (len(foto_db)>0):
        foto_list=[]
        for foto in foto_db:
            foto_list.append(foto)
    annuncio['foto']=foto_list 

    if current_user.is_authenticated: #verifico se l'utente (loggato) può richiedere una visita per l'immobile
        richiesta = True  
        for prenotazione in prenotazioni_db:
            if prenotazione['id_utente']==current_user.id and prenotazione['stato']!='rifiutata': #se l'utente ha già effettuato una richiesta per l'immobile e questa non è stata rifiutata, non può farne altre
                richiesta = False
    else:
        richiesta = False

    data_min = datetime.date.today()+timedelta(days=1) #definisco la data minima per la prenotazione (dal giorno dopo la richiesta di prenotazione della visita) 
    data_max = datetime.date.today()+timedelta(days=7) #definisco la data massima per la prenotazione (fino a 7 giorni dopo la richiesta di prenotazione della visita)

    return render_template('single.html', annuncio = annuncio, richiesta = richiesta, data_min = data_min, data_max = data_max, email_locatore = email_locatore)



# definisce la funzione load_user()
@login_manager.user_loader 
def load_user(user_id):

    utente_db = utenti_dao.get_utente_by_id(user_id) #prendo i dati dell'utente corrispondente all'id passata come parametro 

    if utente_db: # se l'utente esiste, creo un oggetto User() con i campi dell'utente 
        user = User(id=utente_db['id'], email=utente_db['email'], nome=utente_db['nome'], cognome=utente_db['cognome'], password=utente_db['password'], tipologia_utente=utente_db['tipologia_utente']) #creo un nuovo oggetto User
    else:
        user=None

    return user



# definisco la pagina login
@app.route('/login')
def login():
    return render_template('login.html')



# definisco la route login per l'accesso degli utenti
@app.route('/login', methods=['POST'])
def login_post():

    user = request.form.to_dict() #prende le informazioni del form e le converte in un dizionario

    if user['email']=='' or user['email'].strip=="":
        flash('Inserire la email!', 'danger')
        return redirect(url_for('login_post'))
    
    if user['password']=='' or user['password'].strip=="":
        flash('Inserire la password!', 'danger')
        return redirect(url_for('login_post'))
    
    utente_db = utenti_dao.get_utente_by_email(user['email']) #prende i dati dell'utente che corrisponde all'email inserita nel form
        
    if not utente_db: #se non esiste l'utente nel database 
        flash('Questo utente non esiste, riprovare!', 'danger')
        return redirect(url_for('login_post')) #il login non ha successo, ritorna alla pagina di login iniziale
    elif not check_password_hash(utente_db['password'], user['password']): #se la password non corrisponde a quella del database
        flash('La password è sbagliata, riprovare!', 'danger')
        return redirect(url_for('login_post')) #il login non ha successo, ritorna alla pagina di login iniziale
    else:
        new_user = User(id=utente_db['id'], email=utente_db['email'], nome=utente_db['nome'], cognome=utente_db['cognome'], password=utente_db['password'], tipologia_utente=utente_db['tipologia_utente']) #il login ha successo, viene creato l'oggetto User corrispondente
        login_user(new_user, True)
        flash('Ciao '+utente_db['nome']+'!', 'success')
    
    return redirect(url_for('home'))



# definisco la pagina signup
@app.route('/signup')
def signup():
    return render_template('signup.html')



# definisco la route signup per la registrazione
@app.route('/signup', methods=['POST'])
def signup_post():
   
    new_user = request.form.to_dict()

    if 'tipologia_utente' not in new_user.keys():
        flash('Inserire la tipologia di utente!', 'danger')
        return redirect(url_for('signup'))
    
    if new_user['nome']=='' or new_user['nome'].strip=="":
        flash('Inserire il nome!', 'danger')
        return redirect(url_for('signup'))
    else:
        new_user['nome']=new_user['nome'][0].upper()+new_user['nome'][1:len(new_user['nome'])].lower() #converte in maiuscola l'iniziale del nome e in minuscolo il resto del nome
    
    if new_user['cognome']=='' or new_user['cognome'].strip=="":
        flash('Inserire il cognome!', 'danger')
        return redirect(url_for('signup'))
    else:
        new_user['cognome']=new_user['cognome'][0].upper()+new_user['cognome'][1:len(new_user['cognome'])].lower()
    
    if new_user['email']=='' or not "@" in new_user['email'] or new_user['email'].strip=="":
        flash('Inserire la email!', 'danger')
        return redirect(url_for('signup'))
    
    if utenti_dao.get_utente_by_email(new_user['email']):
        flash('Esiste già un utente con questa email!', 'danger')
        return redirect(url_for('signup'))
   
    if new_user['password']=='' or new_user['password'].strip=="":
        flash('Inserire la password!', 'danger')
        return redirect(url_for('signup'))
    
    new_user['password'] = generate_password_hash(new_user['password'])

    success = utenti_dao.create_user(new_user)
    
    if success:
        flash('Registrazione avvenuta con successo!', 'success')
        return redirect(url_for('home'))
    else:
        flash('Registrazione non avvenuta', 'danger')
    
    return redirect(url_for('signup'))



# definisco la route logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))



# definisco la pagina di profilo personale
@app.route('/profile/<int:id>')
@login_required
def profile(id):

    prenotazioni_utente_db = prenotazioni_dao.get_prenotazioni_utente(id)

    prenotazioni = [dict(row) for row in prenotazioni_utente_db] #copia i dati ottenuti dal db in una lista di dizionari, in modo che siano modificabili

    for prenotazione in prenotazioni:
        foto_db = foto_dao.get_foto_annuncio(prenotazione['id_annuncio']) #prende le foto della tabella 'foto' associate al id_annuncio
        if (len(foto_db)>0):
            prenotazione['foto1']=foto_db[0]['foto_annuncio'] #aggiunge un campo 'foto1' al dizionario che contiene la prima foto dell'annuncio

    if current_user.tipologia_utente=='locatore':

        annunci_locatore_db = annunci_dao.get_annunci_locatore(id)

        annunci = [dict(row) for row in annunci_locatore_db] #copia i dati ottenuti dal db in una lista di dizionari, in modo che siano modificabili

        for annuncio in annunci:
            foto_db = foto_dao.get_foto_annuncio(annuncio['id']) #prende le foto della tabella 'foto' associate al id_annuncio
            if (len(foto_db)>0):
                annuncio['foto1']=foto_db[0]['foto_annuncio']

        disponibili = []
        no_disponibili = []
        for annuncio in annunci:
            if annuncio['disponibilita']==1:
                disponibili.append(annuncio)
            elif annuncio['disponibilita']==0:
                no_disponibili.append(annuncio)
        
        filtro = request.args.get('filtro')
        
        if not filtro:
            prenotazioni_locatore_db = prenotazioni_dao.get_prenotazioni_locatore_ricevute(id)
            filtro=None
        elif filtro=='accettata' or filtro=='rifiutata' or filtro=='richiesta':
            filtro_query = {'id_locatore':current_user.id, 'stato':filtro}
            prenotazioni_locatore_db = prenotazioni_dao.get_prenotazioni_locatore_filtrate(filtro_query)

        return render_template('profile.html', prenotazioni = prenotazioni, annunci = annunci, disponibili = disponibili, no_disponibili = no_disponibili, prenotazioni_locatore = prenotazioni_locatore_db, filtro = filtro)
    
    return render_template('profile.html', prenotazioni = prenotazioni)



# definisco la route della prenotazione
@app.route('/prenotazione', methods=['POST'])
@login_required
def prenotazione():

    prenotazione = request.form.to_dict()

    if 'modalita' not in prenotazione.keys():
        flash('Inserire la modalità di visita!', 'danger')
        return redirect(url_for('annuncio', id=int(prenotazione['id_annuncio'])))
    
    if prenotazione['data']=='':
        flash('Inserire una data!', 'danger')
        return redirect(url_for('annuncio', id=int(prenotazione['id_annuncio'])))
    
    if datetime.datetime.strptime(prenotazione['data'], '%Y-%m-%d').date() <= datetime.date.today() or datetime.datetime.strptime(prenotazione['data'], '%Y-%m-%d').date() > datetime.date.today()+timedelta(days=7):
        flash('Non è possibile prenotare in questa data!', 'danger')
        return redirect(url_for('annuncio', id=int(prenotazione['id_annuncio'])))
    
    if 'orario' not in prenotazione.keys():
        flash('Inserire un orario!', 'danger')
        return redirect(url_for('annuncio', id=int(prenotazione['id_annuncio'])))
    
    prenotazioni_annuncio_db = prenotazioni_dao.get_prenotazioni_annuncio(int(prenotazione['id_annuncio'])) #prende le prenotazioni già effettuate per l'immobile che si vuole visitare
    
    if len(prenotazioni_annuncio_db)!=0: #se il dizionario non è vuoto 
        for prenotazione_db in prenotazioni_annuncio_db: 
            if prenotazione_db['data']==prenotazione['data'] and prenotazione_db['orario']==prenotazione['orario'] and prenotazione_db['stato']=='accettata': 
                flash('Errore nella prenotazione: la fascia oraria selezionata non è disponibile, inserirne una nuova!', 'danger') #se esiste già una prenotazione ACCETTATA per la casa in quella data-orario, non può essere aggiunta
                return redirect(url_for('annuncio', id=int(prenotazione['id_annuncio'])))

    prenotazione['stato']='richiesta'

    success = prenotazioni_dao.add_prenotazione(prenotazione)
    
    if success:
        flash('La richiesta di prenotazione è andata a buon fine, attendi che il locatore la accetti', 'success')
    else:
        flash('Errore durante la richiesta di prenotazione, riprovare', 'danger')

    return redirect(url_for('annuncio', id=int(prenotazione['id_annuncio'])))



# definisco la route per creare un nuovo annuncio
@app.route('/nuovo_annuncio', methods=['POST'])
@login_required
def nuovo_annuncio():

    annuncio = request.form.to_dict()
        
    if annuncio['titolo']=='' or annuncio['titolo'].strip()=="" or len(annuncio['titolo'])<10 or len(annuncio['titolo'])>200:
        flash('Inserire il titolo!', 'danger')
        return redirect(url_for('profile', id=int(current_user.id)))
    
    if annuncio['indirizzo']=='' or annuncio['indirizzo'].strip()=="" or len(annuncio['indirizzo'])<5 or len(annuncio['indirizzo'])>100:
        flash('Inserire indirizzo!', 'danger')
        return redirect(url_for('profile', id=int(current_user.id)))
    
    if 'tipologia' not in annuncio.keys():
        flash('Inserire la tipologia!', 'danger')
        return redirect(url_for('profile', id=int(current_user.id)))
    
    if 'locali' not in annuncio.keys():
        flash('Inserire il numero di locali!', 'danger')
        return redirect(url_for('profile', id=int(current_user.id)))
    
    if annuncio['descrizione']=='' or annuncio['descrizione'].strip()=="" or len(annuncio['descrizione'])<10:
        flash('Inserire la descrizione!', 'danger')
        return redirect(url_for('profile', id=int(current_user.id)))

    if annuncio['prezzo']=='' or int(annuncio['prezzo'])<0:
        flash('Inserire il prezzo!', 'danger')
        return redirect(url_for('profile', id=int(current_user.id)))

    if 'arredata' not in annuncio.keys():
        flash('Inserire se è arredato!', 'danger')
        return redirect(url_for('profile', id=int(current_user.id)))
    
    if 'disponibilita' not in annuncio.keys():
        flash('Inserire la disponibilita!', 'danger')
        return redirect(url_for('profile', id=int(current_user.id)))
    
    last_id = annunci_dao.add_annuncio(annuncio) #creo prima l'annuncio senza le foto, così ho l'id dell'annuncio a cui associare le foto
    print(last_id)

    if last_id==None:
        flash('Errore durante la creazione del nuovo annuncio, riprovare', 'danger')
        return redirect(url_for('profile', id=int(current_user.id)))

    foto_all = [] #copio in una lista i nomi dei file delle immagini
    count_foto = 0
    for i in range(5):
        if request.files['foto'+str(i)]:
            foto_all.append(request.files['foto'+str(i)])
            count_foto+=1

    if count_foto==0:
        flash('Inserire almeno una immagine!', 'danger')
        return redirect(url_for('profile', id=int(current_user.id)))
    
    for foto in foto_all:
        if foto:
            foto_tagliata = dimensiona_foto(foto) #taglia la foto in formato 3:2
            foto_tagliata.save('static/' + foto.filename) #salvo la foto nella cartella 'static'
            new_foto={'id_annuncio':last_id, 'foto_annuncio':foto.filename}
            success = foto_dao.add_foto(new_foto) #aggiunge l'immagine alla tabella 'foto'
            if not success:
                flash('Errore durante la creazione del nuovo annuncio, riprovare', 'danger')
                return redirect(url_for('profile', id=int(current_user.id)))
     
    flash('Annuncio creato con successo!', 'success')

    return redirect(url_for('home'))



# definisco la route per modificare un annuncio
@app.route('/modifica_annuncio', methods=['POST'])
@login_required
def modifica_annuncio():

    annuncio = request.form.to_dict()

    old_annuncio = annunci_dao.get_annuncio_by_id(int(annuncio['id'])) #prendo l'annuncio non modificato, per prendere le vecchie informazioni nel caso in cui alcuni campi non vadano modificati

    if not old_annuncio: #se non esiste il vecchio annuncio
        return redirect(url_for('annuncio', id=int(annuncio['id'])))
    
    if annuncio['titolo']=='': #se non ci sono modifiche da fare, assegno il vecchio titolo
        annuncio['titolo']=old_annuncio['titolo']
    elif annuncio['titolo'].strip()=="" or len(annuncio['titolo'])<10: #altrimenti, controllo che rispetti le condizioni del titolo
        flash('Inserire un titolo valido!', 'danger')
        return redirect(url_for('annuncio', id=int(annuncio['id'])))
    
    annuncio['indirizzo']=old_annuncio['indirizzo'] 

    if 'tipologia' not in annuncio.keys():
        annuncio['tipologia']=old_annuncio['tipologia']
    
    if 'locali' not in annuncio.keys():
        annuncio['locali']=old_annuncio['locali']
    
    if annuncio['descrizione']=='':
        annuncio['descrizione']=old_annuncio['descrizione'] 
    elif annuncio['descrizione'].strip()=="" or len(annuncio['descrizione'])<10:
        flash('Inserire una descrizione valida!', 'danger')
        return redirect(url_for('annuncio', id=int(annuncio['id'])))

    if annuncio['prezzo']=='':
        annuncio['prezzo']=old_annuncio['prezzo'] 
    elif int(annuncio['prezzo'])<0:
        flash('Inserire un prezzo maggiore di zero!', 'danger')
        return redirect(url_for('annuncio', id=int(annuncio['id'])))

    if 'arredata' not in annuncio.keys():
        annuncio['arredata']=old_annuncio['arredata']

    if 'disponibilita' not in annuncio.keys():
        annuncio['disponibilita']=old_annuncio['disponibilita']
    

    old_foto = foto_dao.get_foto_annuncio(old_annuncio['id']) #prendo le foto del vecchio annuncio 

    count_elimina = 0
    for i in range(0,len(old_foto)):
        if 'modifica'+str(old_foto[i]['id_foto']) in annuncio.keys() and annuncio['modifica'+str(old_foto[i]['id_foto'])]=='elimina':
            count_elimina += 1

    if count_elimina==len(old_foto):
        flash('Non puoi eliminare tutte le foto!', 'danger')
        return redirect(url_for('annuncio', id=int(annuncio['id'])))

    for foto in old_foto:
        print(foto['foto_annuncio'])
        modifica=annuncio['modifica'+str(foto['id_foto'])] #nel form ho chiamato 'modifica<id_foto>' i radio-check che dicono se l'utente vuole modificare o eliminare la foto
        if modifica=='elimina':
            success = foto_dao.delete_foto(foto['id_foto'])
            if not success:
                flash('Errore durante la rimozione della foto, riprovare', 'danger')
                return redirect(url_for('annuncio', id=int(annuncio['id'])))
                
        elif modifica=='sostituisci':
            foto_sostituita = request.files['foto'+str(foto['id_foto'])]
            if foto_sostituita:
                foto_tagliata = dimensiona_foto(foto_sostituita)
                foto_tagliata.save('static/' + foto_sostituita.filename) #salvo la foto nella cartella 'static'
                update_query={'id_foto':foto['id_foto'], 'foto_annuncio':foto_sostituita.filename}
                success = foto_dao.update_foto(update_query)
                if not success:
                    flash('Errore durante la sostituzione della foto, riprovare', 'danger')
                    return redirect(url_for('annuncio', id=int(annuncio['id'])))
            else:
                flash('Inserire la immagine da sostituire!', 'danger') #non c'è il file della foto ma è stato selezionato il radio-check 'modifica'
                return redirect(url_for('annuncio', id=int(annuncio['id'])))
    
    if len(old_foto)<5:
        for i in range(len(old_foto),5):
            foto_aggiunta = request.files['newfoto'+str(i+1)]
            if foto_aggiunta and foto_aggiunta!="": 
                foto_tagliata = dimensiona_foto(foto_aggiunta)
                foto_tagliata.save('static/' + foto_aggiunta.filename)
                add_query={'id_annuncio':annuncio['id'], 'foto_annuncio':foto_aggiunta.filename}
                success = foto_dao.add_foto(add_query)
                if not success:
                    flash('Errore durante la aggiunta della nuova foto, riprovare', 'danger')
                    return redirect(url_for('annuncio', id=int(annuncio['id'])))
                
    success = annunci_dao.update_annuncio(annuncio) 
    
    if success:
        flash('Annuncio modificato con successo!', 'success')
    else:
        flash('Errore durante la modifica del nuovo annuncio, riprovare', 'danger')

    return redirect(url_for('annuncio', id=int(annuncio['id'])))


@app.route('/modifica_prenotazione', methods=['POST'])
@login_required
def modifica_prenotazione():

    aggiornamento = request.form.to_dict()

    if aggiornamento['stato']=='':
        flash('Selezionare se accettare o rifiutare la prenotazione!', 'danger')
        return redirect(url_for('profile', id=current_user.id))
    
    if aggiornamento['stato']=='rifiutata':
        if aggiornamento['motivo_rifiuto']=='' or aggiornamento['motivo_rifiuto'].strip()=="":
            flash('Inserire un motivo per cui si vuole rifiutare la prenotazione!', 'danger')
            return redirect(url_for('profile', id=current_user.id))

    if aggiornamento['stato']=='accettata':
        aggiornamento['motivo_rifiuto']='' #inserisco una stringa vuota per non avere problemi nella query SQL
                
    success = prenotazioni_dao.update_prenotazione(aggiornamento)

    if success:
        flash('Aggiornamento andato a buon fine! La prenotazione è stata '+aggiornamento['stato'], 'success')
    else:
        flash('Aggiornamento dello stato della prenotazione non andato a buon fine!', 'danger')

    return redirect(url_for('profile', id=current_user.id))
   


#taglia la foto in formato 3:2
def dimensiona_foto(foto):

    img = Image.open(foto)

    width, height = img.size

    new_height = width * 2/3

    #coordinate del taglio
    left = 0
    top = (height - new_height)/2
    right = width
    bottom = top + new_height

    cropped_img = img.crop((left, top, right, bottom))

    return cropped_img



    