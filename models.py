from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, nome, cognome, password, tipologia_utente):
        self.id = id
        self.email = email
        self.nome = nome
        self.cognome = cognome
        self.password = password 
        self.tipologia_utente = tipologia_utente

        