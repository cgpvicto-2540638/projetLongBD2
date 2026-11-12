DROP DATABASE IF EXISTS pizzeria;

CREATE DATABASE pizzeria;

USE pizzeria;

CREATE TABLE croutes(
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nom VARCHAR(255)
);

CREATE TABLE sauces(
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nom VARCHAR(255)
);

CREATE TABLE garnitures(
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nom VARCHAR(255)
);

CREATE TABLE etats(
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nom VARCHAR(255)
);

CREATE TABLE clients(
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nom VARCHAR(255),
	nb_telephone VARCHAR(12)
);

CREATE TABLE commandes(
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	date DATETIME,
	adresse VARCHAR(255),
	etat_id INTEGER,
	client_id INTEGER,
	FOREIGN KEY (etat_id) REFERENCES etats(id),
	FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE pizza(
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	croute_id INTEGER,
	sauce_id INTEGER,
	commande_id INTEGER,
	FOREIGN KEY (croute_id) REFERENCES croutes(id),
	FOREIGN KEY (sauce_id) REFERENCES sauces(id),
	FOREIGN KEY (commande_id) REFERENCES croutes(id)
);
CREATE TABLE garnituesPizza(
	pizza_id INTEGER,
	gariture_id INTEGER,
	PRIMARY KEY(pizza_id, gariture_id),
	FOREIGN KEY (pizza_id) REFERENCES pizza(id),
	FOREIGN KEY (gariture_id) REFERENCES garnitures(id)
);

INSERT INTO pizzeria.croutes (nom) VALUES
	("Classique"),
	("Mince"),
	("Épaisse");

INSERT INTO pizzeria.sauces (nom) VALUES
	("Tomate"),
	("Spaghetti"),
	("Alfredo");

INSERT INTO pizzeria.garnitures (nom) VALUES
	("Pepperoni"),
	("Champignons"),
	("Oignons"),
	("Poivrons"),
	("Olives"),
	("Anchois"),
	("Bacon"),
	("Poulet"),
	("Maïs"),
	("Fromage"),
	("Piments forts");

INSERT INTO pizzeria.etats (nom) VALUES
	("en attente de livraison"),
	("livraison fait");

DELIMITER %%
CREATE TRIGGER ajouter_attente BEFORE INSERT ON commandes FOR EACH ROW
BEGIN
	SET NEW.etat_id = 1;
END %%
DELIMITER ;


