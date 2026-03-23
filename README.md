# Budget Buddy

Application de gestion financiere avec interface graphique (CustomTkinter) et base de donnees MySQL.

## Fonctionnalites

- Authentification securisee (bcrypt + sel + poivre)
- Validation du mot de passe (10 car, majuscule, minuscule, chiffre, special) avec indicateur de force
- Tableau de bord avec graphiques (revenus/depenses par mois, repartition par categorie)
- Transactions : depot, retrait, transfert entre comptes
- Filtres multi-criteres : date, plage de dates, categorie, type, tri par montant
- Plafonds budgetaires par categorie avec alertes automatiques
- Transactions recurrentes (abonnements, prelevements)
- Export CSV de l'historique
- Notifications (decouvert, solde bas, depassement de budget)
- Espace banquier : gestion de portefeuille clients, operations pour le compte du client

## Prerequis

- Python 3.10+
- MySQL Server

## Installation

```bash
pip install -r requirements.txt
mysql -u root -p < schema.sql
cp .env.example .env
# editer .env avec vos identifiants MySQL
python main.py
```

## Securite

Les mots de passe sont haches avec bcrypt. Le sel est genere automatiquement et integre au hash.
Un poivre (valeur secrete stockee dans `.env`) est concatene au mot de passe avant le hachage.
Toutes les requetes SQL utilisent des parametres pour eviter les injections.

## Structure

```
budget_buddy/
├── main.py
├── config.py
├── database.py
├── auth.py
├── schema.sql
├── views/
│   ├── login_view.py
│   ├── register_view.py
│   ├── dashboard_view.py
│   ├── transactions_view.py
│   ├── settings_view.py
│   └── banker_view.py
└── utils/helpers.py
```
