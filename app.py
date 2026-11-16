import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import mysql.connector
app = Flask(__name__)
load_dotenv()
db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database= os.getenv('DB_NAME'),
    port= os.getenv('DB_PORT'))

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/ajoutCommande', methods=['POST'])
def ajout():
    id_client = -1
    requete = """
    SELECT id FROM pizzeria.clients c WHERE nom = %(nomClient)s AND c.nb_telephone = %(nb_telephone)s; 
    """
    parametres = {
        "nomClient": request.form['nomClient'],
        "nb_telephone": request.form['telephone']
    }
    curseur = db.cursor(dictionary=True)
    curseur.execute(requete, parametres)
    resultat = curseur.fetchone()
    if resultat is not None:
        id_client = resultat['id']
        db.commit()
    else:
        db.rollback()
        parametres = {
            "nom": request.form['nomClient'],
            "nb_telephone": request.form['telephone']
        }
        requete = """
            INSERT INTO pizzeria.clients (nom, nb_telephone) VALUES (%(nom)s,%(nb_telephone)s);
        """
        curseur.execute(requete, parametres)
        id_client = curseur.lastrowid
        db.commit()
    requete = """
    INSERT INTO pizzeria.commandes (heure, minute, adresse, client_id)
    VALUES(%(heure)s, %(minute)s, %(adresse)s, %(client_id)s)
    """
    temps = request.form['heure'].split(":")
    parametres = {
        "heure":  temps[0],
        "minute": temps[1],
        "adresse": request.form['adresse'],
        "client_id": (str)(id_client),
    }
    try:
        curseur.execute(requete, parametres)
        db.commit()
        curseur.close()
        return pizza()
    except mysql.connector.Error as erreur:
        db.rollback()
        return render_template("erreur.html", erreur=erreur.msg)
@app.route('/pizza')
def pizza():
    cursor = db.cursor()
    cursor.execute("SELECT nom FROM pizzeria.croutes ;")
    croutes = cursor.fetchall()
    cursor.execute("SELECT nom FROM pizzeria.sauces ;")
    sauces = cursor.fetchall()
    cursor.execute("SELECT nom FROM pizzeria.garnitures ;")
    garnitures = cursor.fetchall()
    liste = {"croutes":croutes, "sauces":sauces, "garnitures":garnitures}
    cursor.close()
    return render_template('choixPizza.html', data=liste)
if __name__ == '__main__':
    app.run(debug=True)