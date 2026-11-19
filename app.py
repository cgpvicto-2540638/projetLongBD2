import os
from flask import Flask, render_template, request, redirect, url_for
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
    try:
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
        curseur.execute(requete, parametres)
        db.commit()
        return redirect(url_for('pizza'))
    except Exception as erreur:
        db.rollback()
        return render_template("erreur.html", erreur=erreur)
    finally:
        curseur.close()

@app.route('/pizza')
def pizza():
    curseur = db.cursor()
    curseur.execute("SELECT nom,id FROM pizzeria.croutes;")
    croutes = curseur.fetchall()
    curseur.execute("SELECT nom,id FROM pizzeria.sauces;")
    sauces = curseur.fetchall()
    curseur.execute("SELECT nom,id FROM pizzeria.garnitures;")
    garnitures = curseur.fetchall() 
    curseur.close()
    return render_template('choixPizza.html',croutes=croutes, sauces=sauces, garnitures=garnitures)

@app.route('/ajoutPizza', methods=['POST'])
def Ajoutpizza():
    id_commandes = 0
    curseur = db.cursor(dictionary=True)
    requete = "SELECT id FROM pizzeria.commandes ORDER BY id DESC LIMIT 1;"
    curseur.execute(requete)
    resultat =curseur.fetchone()
    if resultat is not None:
        id_commandes = resultat['id']
    else:
        return render_template("erreur.html", erreur="une erreur est survenu lors du chargement de la commandes")
    requete = """
        INSERT INTO pizzeria.pizza (croute_id, sauce_id, commande_id) VALUES (%(croute_id)s,%(sauce_id)s, %(commande_id)s);
        """
    parametres = {
        "croute_id":  request.form['croutes'],
        "sauce_id": request.form['sauces'],
        "commande_id": (str)(id_commandes)
    }
    try:
        curseur.execute(requete, parametres)
        id_pizza = curseur.lastrowid
        db.commit()
        requete = """
            INSERT INTO pizzeria.garnituesPizza (pizza_id, gariture_id) VALUES (%(pizza_id)s,%(gariture_id)s);
        """
        garnitures_id = request.form.getlist('garnitures')
        for garniture_id in garnitures_id:
            parametres = {
                "pizza_id": id_pizza,
                "gariture_id": garniture_id
            }
            curseur.execute(requete, parametres)
            db.commit()
        return redirect(url_for('Resume'))
    except Exception as erreur:
        db.rollback()
        return render_template("erreur.html", erreur=erreur)
    finally:
        curseur.close()

@app.route('/Resume')
def Resume():
    curseur = db.cursor(dictionary=True)
    requete = """
        SELECT p.id as id, heure, minute, adresse, c2.nom AS nomClient, nb_telephone, c3.nom AS nomCroute, s.nom AS nomSauce FROM pizzeria.commandes c 
            JOIN pizzeria.clients c2 ON c.client_id = c2.id
            JOIN pizzeria.pizza p ON c.id = p.commande_id 
            JOIN pizzeria.croutes c3 ON c3.id = p.croute_id 
            JOIN pizzeria.sauces s ON p.sauce_id = s.id ORDER BY c.id DESC LIMIT 1;
        """
    curseur.execute(requete)
    donneClient =curseur.fetchone()
    requete = """
        SELECT nom AS garniture FROM pizzeria.commandes c 
            JOIN pizzeria.pizza p ON c.id = p.commande_id
            JOIN pizzeria.garnituespizza g ON p.id = g.pizza_id
            JOIN pizzeria.garnitures g2 ON g.gariture_id = g2.id WHERE p.id = %(pizza_id)s;
        """
    parametres = {"pizza_id": donneClient['id']}
    curseur.execute(requete, parametres)
    donneGarniture =curseur.fetchall()
    curseur.close()
    return render_template('Resume.html', donneClient=donneClient, donneGarniture=donneGarniture)

def DonneEtatAttente():
    curseur = db.cursor(dictionary=True)
    requete = """
        SELECT id FROM pizzeria.etats e WHERE nom = "en attente de livraison";
        """
    curseur.execute(requete)
    donneEtat = curseur.fetchone()
    curseur.close()
    return donneEtat

def ResumeTousClient():
    curseur = db.cursor(dictionary=True)
    requete = """
        SELECT p.id as pizza_id,c.id as commande_id, heure, minute, adresse, c2.nom AS nomClient, nb_telephone, c3.nom AS nomCroute, s.nom AS nomSauce FROM pizzeria.commandes c 
            JOIN pizzeria.clients c2 ON c.client_id = c2.id
            JOIN pizzeria.pizza p ON c.id = p.commande_id 
            JOIN pizzeria.croutes c3 ON c3.id = p.croute_id 
            JOIN pizzeria.sauces s ON p.sauce_id = s.id WHERE etat_id = %(etat)s;
        """
    curseur.execute(requete, {"etat":DonneEtatAttente()['id']})
    donneClient = curseur.fetchall()
    curseur.close()
    return donneClient

def ResumeTousGarniture():
    curseur = db.cursor(dictionary=True)
    requete = """
    SELECT nom AS garniture, p.id as id FROM pizzeria.commandes c 
        JOIN pizzeria.pizza p ON c.id = p.commande_id
        JOIN pizzeria.garnituespizza g ON p.id = g.pizza_id
        JOIN pizzeria.garnitures g2 ON g.gariture_id = g2.id;
    """
    curseur.execute(requete)
    donneGarniture =curseur.fetchall()
    curseur.close()
    return donneGarniture

@app.route('/listeCommande')
def listeCommande():
    return render_template('ListeCommande.html', donneClient=ResumeTousClient(), donneGarniture=ResumeTousGarniture(), donneEtat=DonneEtatAttente())

@app.route('/LivrerCommande/<int:id>')
def LivrerCommande(id):
    commande = id
    curseur = db.cursor(dictionary=True)
    requete = """
        SELECT id FROM pizzeria.etats e WHERE e.nom = "livraison fait";
        """
    curseur.execute(requete)
    idLivrer =curseur.fetchone()
    requete = """
        UPDATE pizzeria.commandes c 
            SET etat_id = %(nouveau_etat)s WHERE c.id = %(id_commande)s;
    """
    parametres = {"nouveau_etat": idLivrer['id'],
                    "id_commande": commande}
    try:
        curseur.execute(requete, parametres)
        db.commit()
    except Exception as erreur:
            db.rollback()
            return render_template("erreur.html", erreur=erreur)
    finally:
        curseur.close()
    return render_template('ListeCommande.html',donneClient=ResumeTousClient(), donneGarniture=ResumeTousGarniture(),donneEtat=DonneEtatAttente())
if __name__ == '__main__':
    app.run(debug=True)