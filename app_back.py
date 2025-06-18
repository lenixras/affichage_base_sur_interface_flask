import mysql.connector
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, session, send_file
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuration de la base de données (pointage)
db_config = {
    'host': '192.168.60.15',
    'user': 'pointeuse',
    'password': 'just4SI***',
    'database': 'pointeuse'
}

# Configuration d'une base SQLite pour les identifiants de login
import sqlite3
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'admin123')''')
    conn.commit()
    conn.close()

init_db()

# Page de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['logged_in'] = True
            return redirect(url_for('pointage'))
        return "Identifiants incorrects"
    return render_template('login.html')

# Page de pointage
@app.route('/pointage', methods=['GET', 'POST'])
def pointage():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Requête SQL de base
    query = """
    SELECT 
        subquery.matricule, 
        subquery.prenom, 
        subquery.date,
        MAX(CASE WHEN rn = 1 THEN subquery.time END) AS pointage_1,
        MAX(CASE WHEN rn = 2 THEN subquery.time END) AS pointage_2,
        MAX(CASE WHEN rn = 3 THEN subquery.time END) AS pointage_3,
        MAX(CASE WHEN rn = 4 THEN subquery.time END) AS pointage_4,
        MAX(CASE WHEN rn = 5 THEN subquery.time END) AS pointage_5,
        MAX(CASE WHEN rn = 6 THEN subquery.time END) AS pointage_6
    FROM (
        SELECT 
            donnees_pointage.matricule, 
            donnees_pointage.prenom, 
            donnees_pointage.date, 
            donnees_pointage.time,
            ROW_NUMBER() OVER (PARTITION BY donnees_pointage.matricule, donnees_pointage.date ORDER BY donnees_pointage.time) AS rn
        FROM donnees_pointage
        WHERE donnees_pointage.date BETWEEN %s AND %s
    ) AS subquery
    GROUP BY subquery.matricule, subquery.prenom, subquery.date
    ORDER BY subquery.date, subquery.matricule
    """

    # Date actuelle comme valeur par défaut
    current_date = date.today().strftime('%Y-%m-%d')
    start_date = request.form.get('start_date', current_date)
    end_date = request.form.get('end_date', current_date)

    matricule_option = request.form.get('matricule_option', 'ALL')
    matricule = request.form.get('matricule_input', '') if matricule_option != 'ALL' else 'ALL'
    prenom_option = request.form.get('prenom_option', 'ALL')
    prenom = request.form.get('prenom_input', '') if prenom_option != 'ALL' else 'ALL'

    error_message = None
    data = []

    # Validation des champs
    try:
        params = [start_date, end_date]
        if matricule != 'ALL':
            matricule_int = int(matricule)  # Vérifie que le matricule est un entier
            query = query.replace("WHERE donnees_pointage.date BETWEEN %s AND %s", 
                                  "WHERE donnees_pointage.date BETWEEN %s AND %s AND donnees_pointage.matricule = %s")
            params.append(matricule_int)
        if prenom != 'ALL':
            condition = " AND donnees_pointage.prenom = %s"
            if "donnees_pointage.matricule = %s" in query:
                query = query.replace("WHERE donnees_pointage.date BETWEEN %s AND %s AND donnees_pointage.matricule = %s", 
                                      "WHERE donnees_pointage.date BETWEEN %s AND %s AND donnees_pointage.matricule = %s" + condition)
            else:
                query = query.replace("WHERE donnees_pointage.date BETWEEN %s AND %s", 
                                      "WHERE donnees_pointage.date BETWEEN %s AND %s" + condition)
            params.append(prenom)

        # Exécuter la requête
        cursor.execute(query, params)
        results = cursor.fetchall()
        columns = ['matricule', 'prenom', 'date', 'pointage_1', 'pointage_2', 'pointage_3', 'pointage_4', 'pointage_5', 'pointage_6']
        data = [dict(zip(columns, row)) for row in results]

        # Vérifier si des données ont été trouvées
        if not data:
            error_message = "Aucune donnée trouvée pour les critères sélectionnés."

    except ValueError:
        error_message = "Le matricule doit être un nombre entier."
    except Exception as e:
        error_message = f"Une erreur est survenue : {str(e)}"
    finally:
        cursor.close()
        conn.close()

    # Exportation en Excel
    if 'export' in request.form and data:  # Export uniquement si des données existent
        df = pd.DataFrame(data)
        excel_file = "pointage_export.xlsx"
        df.to_excel(excel_file, index=False)
        return send_file(excel_file, as_attachment=True)

    return render_template('pointage.html', data=data, start_date=start_date, end_date=end_date, error_message=error_message)

# Route de déconnexion
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
