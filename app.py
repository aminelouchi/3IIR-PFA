from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import traceback
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Engine, text
import pandas as pd
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from datetime import datetime, timezone

now = datetime.now(timezone.utc)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_ici'
from sqlalchemy import create_engine
initialized = False

EXCEL_FILE = "data.xlsx"
data = []

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'mnlouchi@gmail.com'
SMTP_PASSWORD = 'wzva lgbm hqgy cbde'

def send_email_notification(to_email, subject, message, solution):
    try:
        print(f"📤 Tentative d'envoi à {to_email}...")  # LOG
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = 'litchymakeupme@gmail.com'
        msg['Subject'] = subject

        body = f"""
        <h3>{message}</h3>
        <p><strong>Solution :</strong> {solution}</p>
        """
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(1)  # 💥 LOG SMTP complet
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        print(f"✅ Email envoyé à {to_email}")

    except Exception as e:
        print(f"❌ Erreur mail : {str(e)}")


def load_data():
    global data
    try:
        df = pd.read_excel(EXCEL_FILE)
        data = df.to_dict(orient="records")
        print("🔄 Données rechargées automatiquement")
    except Exception as e:
        print(f"⚠️ Erreur : {e}")

# Configuration SQL Server
server = r'LOUCHI\SQLEXPRESS'
database = 'PFAFINAL'
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc://@{server}/{database}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True 
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    adresse = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Serre(db.Model):
    __tablename__ = 'Serres'
    id_serre = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nom_serre = db.Column(db.String(100), nullable=False)
    superficie = db.Column(db.Numeric(10, 2), nullable=False)  # Changé pour DECIMAL(10,2)
    adresse = db.Column(db.String(255), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    excel_path = db.Column(db.String(255), nullable=False)
    temperature_min = db.Column(db.Numeric(5, 2), nullable=False)
    temperature_max = db.Column(db.Numeric(5, 2), nullable=False)
    luminosite_min = db.Column(db.Integer, nullable=False)
    luminosite_max = db.Column(db.Integer, nullable=False)
    humidite_sol_min = db.Column(db.Numeric(5, 2), nullable=False)
    humidite_sol_max = db.Column(db.Numeric(5, 2), nullable=False)
    humidite_air_min = db.Column(db.Numeric(5, 2), nullable=False)
    humidite_air_max = db.Column(db.Numeric(5, 2), nullable=False)
    co2_min = db.Column(db.Numeric(6, 2), nullable=False)
    co2_max = db.Column(db.Numeric(6, 2), nullable=False)
    arrosage_auto = db.Column(db.Boolean, default=True)
    frequence_arrosage = db.Column(db.Integer)
    duree_arrosage = db.Column(db.Integer)
    fertilisation_auto = db.Column(db.Boolean, default=True)
    frequence_fertilisation = db.Column(db.Integer)
    type_fertilisant = db.Column(db.String(100))
    date_creation = db.Column(db.DateTime, server_default=db.func.now())
    date_mise_a_jour = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    actif = db.Column(db.Boolean, default=True)

class Notification(db.Model):
    __tablename__ = 'Notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50))       # Ex: "Température"
    seuil = db.Column(db.String(10))      # "min" ou "max"
    message = db.Column(db.String(255))
    solution = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class DerniereAlerte(db.Model):
    __tablename__ = 'DernieresAlertes'
    id = db.Column(db.Integer, primary_key=True)
    serre_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50))
    valeur = db.Column(db.Float)
    pourcentage = db.Column(db.Float)
    seuil_min = db.Column(db.Float)
    seuil_max = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class ExcelFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(EXCEL_FILE):
            print("📢 Modification détectée")
            load_data()

def start_watcher():
    event_handler = ExcelFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

@app.route('/data')
def get_data():
    return jsonify(data)

@app.route('/latest_data')
def latest_data():
    if 'user_id' not in session:
        return jsonify({"error": "Non connecté"}), 403

    serre_id = request.args.get('serre_id', type=int)
    if not serre_id:
        serre = Serre.query.filter_by(id_user=session['user_id']).first()
    else:
        serre = Serre.query.filter_by(id_user=session['user_id'], id_serre=serre_id).first()

    if not serre:
        return jsonify({"error": "Serre non trouvée"}), 404

    # lecture live
    data = live_data.get(serre.id_serre)
    if not data:
        return jsonify({"error": "Pas de données disponibles"}), 404

    valeurs = {
        "Température": data['temperature']['value'],
        "Humidité du sol": data['humidite_sol']['value'],
        "Humidité air": data['humidite_air']['value'],
        "CO2": data['co2']['value'],
        "Luminosité": data['luminosite']['value'],
        "Arrosage": data['arrosage']['value'],
        "Fertilisation": data['fertilisation']['value'],
    }

    alertes = {
        "Température": not (serre.temperature_min <= valeurs["Température"] <= serre.temperature_max),
        "Humidité du sol": not (serre.humidite_sol_min <= valeurs["Humidité du sol"] <= serre.humidite_sol_max),
        "Humidité air": not (serre.humidite_air_min <= valeurs["Humidité air"] <= serre.humidite_air_max),
        "CO2": not (serre.co2_min <= valeurs["CO2"] <= serre.co2_max),
        "Luminosité": not (serre.luminosite_min <= valeurs["Luminosité"] <= serre.luminosite_max),
    }

    return jsonify({"valeurs": valeurs, "alertes": alertes})


@app.route('/accueil')
def accueil():
    return render_template('accueil.html')

@app.route('/rapport')
def rapport():
    return render_template('rapport.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        # Gestion de l'inscription
        if 'email' in request.form and 'num' in request.form:  # Formulaire d'inscription
            username = request.form.get('txt')
            email = request.form.get('email')
            telephone = request.form.get('num')
            adresse = request.form.get('txt')  # Note: même nom que username, à ajuster
            password = request.form.get('pswd')
            
            # Validation simple
            if not all([username, email, telephone, adresse, password]):
                flash('Tous les champs sont obligatoires', 'error')
                return redirect(url_for('auth'))
            
            # Vérification si l'email existe déjà
            if User.query.filter_by(email=email).first():
                flash('Cet email est déjà utilisé', 'error')
                return redirect(url_for('auth'))
            
            # Création du nouvel utilisateur
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(
                username=username,
                email=email,
                telephone=telephone,
                adresse=adresse,
                password=hashed_password
            )
            
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Inscription réussie! Vous pouvez maintenant vous connecter', 'success')
                return redirect(url_for('auth'))
            except Exception as e:
                db.session.rollback()
                flash("Une erreur s'est produite lors de l'inscription", 'error')
                return redirect(url_for('auth'))

        # Gestion de la connexion
        elif 'username' in request.form:  # Formulaire de connexion
            username = request.form.get('username')
            password = request.form.get('pswd')
            
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id  # Stocke l'ID utilisateur dans la session
                flash('Connexion réussie!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
                return redirect(url_for('auth'))

    return render_template('auth.html')

@app.route('/serres', methods=['GET', 'POST'])
def serres():
    if 'user_id' not in session:
        flash('Veuillez vous connecter', 'error')
        return redirect(url_for('auth'))
    
    if request.method == 'POST':
        # Debug: Afficher les données reçues
        app.logger.info("Données du formulaire reçues: %s", request.form)
        
        try:
            required_fields = [
                'serreName', 'adresse', 'city', 'superficie',
                'temperature_min', 'temperature_max',
                'humidite_air_min', 'humidite_air_max',
                'humidite_sol_min', 'humidite_sol_max',
                'luminosite_min', 'luminosite_max',
                'co2_min', 'co2_max'
            ]
            
            for field in required_fields:
                if field not in request.form:
                    flash(f'Champ {field} manquant', 'error')
                    app.logger.error("Champ manquant: %s", field)
                    return redirect(url_for('serres'))

            try:
                data = {
                    'id_user': session['user_id'],
                    'nom_serre': request.form['serreName'],
                    'adresse': request.form['adresse'],
                    'ville': request.form['city'],
                    'superficie': float(request.form['superficie']),
                    'temperature_min': float(request.form['temperature_min']),
                    'temperature_max': float(request.form['temperature_max']),
                    'humidite_air_min': float(request.form['humidite_air_min']),
                    'humidite_air_max': float(request.form['humidite_air_max']),
                    'humidite_sol_min': float(request.form['humidite_sol_min']),
                    'humidite_sol_max': float(request.form['humidite_sol_max']),
                    'luminosite_min': int(request.form['luminosite_min']),
                    'luminosite_max': int(request.form['luminosite_max']),
                    'co2_min': float(request.form['co2_min']),
                    'co2_max': float(request.form['co2_max']),
                    'excel_path': request.form['excel_path']  # 👈 Ajout obligatoire ici
                }
            except ValueError as e:
                flash('Valeurs invalides dans le formulaire', 'error')
                app.logger.error("Erreur de conversion: %s", str(e))
                return redirect(url_for('serres'))

            new_serre = Serre(
                **data,
                arrosage_auto=True,
                fertilisation_auto=True
            )
            
            db.session.add(new_serre)
            db.session.commit()
            
            app.logger.info("Insertion réussie dans la base de données")
            flash('Serre ajoutée avec succès!', 'success')
            return redirect(url_for('serres'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Erreur lors de l\'enregistrement en base de données', 'error')
            app.logger.error("Erreur SQLAlchemy: %s", str(e))
        except Exception as e:
            db.session.rollback()
            flash('Une erreur inattendue est survenue', 'error')
            app.logger.error("Erreur inattendue: %s", traceback.format_exc())

        return redirect(url_for('serres'))

    # 👉 Ici, partie GET : je récupère les serres de cet utilisateur
    serres = Serre.query.all()
    serres = Serre.query.filter_by(id_user=session['user_id']).all()

    return render_template('serres.html', serres=serres)

# Suppression
@app.route('/delete_serre/<int:id>', methods=['POST'])
def delete_serre(id):
    serre = Serre.query.get(id)
    if serre:
        db.session.delete(serre)
        db.session.commit()
    return '', 204

# Récupérer les données d'une serre (pour pré-remplir le modal)
@app.route('/get_serre/<int:serre_id>', methods=['GET', 'POST'])
def get_serre(serre_id):
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Non autorisé'}), 401

        serre = Serre.query.filter_by(id_serre=serre_id, id_user=session['user_id']).first()
        if not serre:
            return jsonify({'error': 'Serre introuvable'}), 404

        return jsonify({
            'nom_serre': serre.nom_serre,
            'adresse': serre.adresse,
            'ville': serre.ville,
            'superficie': float(serre.superficie),
            'excel_path': serre.excel_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Pour modifier une serre existante
@app.route('/edit_serre/<int:serre_id>', methods=['POST'])
def edit_serre(serre_id):
    if 'user_id' not in session:
        flash('Veuillez vous connecter', 'error')
        return redirect(url_for('auth'))

    serre = Serre.query.filter_by(id_serre=serre_id, id_user=session['user_id']).first()
    if not serre:
        flash('Serre introuvable', 'error')
        return redirect(url_for('serres'))

    try:
        # Mise à jour des données de la serre
        serre.nom_serre = request.form['serreName']
        serre.adresse = request.form['adresse']
        serre.ville = request.form['city']
        serre.superficie = float(request.form['superficie'])
        serre.excel_path = request.form.get('excel_path', serre.excel_path)

        # Mise à jour seulement si les champs existent dans le formulaire
        serre.temperature_min = float(request.form.get('temperature_min', serre.temperature_min))
        serre.temperature_max = float(request.form.get('temperature_max', serre.temperature_max))
        serre.humidite_air_min = float(request.form.get('humidite_air_min', serre.humidite_air_min))
        serre.humidite_air_max = float(request.form.get('humidite_air_max', serre.humidite_air_max))
        serre.humidite_sol_min = float(request.form.get('humidite_sol_min', serre.humidite_sol_min))
        serre.humidite_sol_max = float(request.form.get('humidite_sol_max', serre.humidite_sol_max))
        serre.luminosite_min = int(request.form.get('luminosite_min', serre.luminosite_min))
        serre.luminosite_max = int(request.form.get('luminosite_max', serre.luminosite_max))
        serre.co2_min = float(request.form.get('co2_min', serre.co2_min))
        serre.co2_max = float(request.form.get('co2_max', serre.co2_max))

        db.session.commit()
        flash('Serre modifiée avec succès!', 'success')
        return redirect(url_for('serres'))

    except Exception as e:
        db.session.rollback()
        app.logger.error("Erreur lors de la modification: %s", str(e))
        return jsonify({"error": f"Erreur lors de la modification : {str(e)}"}), 500

@app.after_request
def log_response(response):
    app.logger.info("Status: %s", response.status)
    app.logger.info("Headers: %s", response.headers)
    return response

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'user_id' not in session:
        flash('Veuillez vous connecter', 'error')
        return redirect(url_for('auth'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        adresse = request.form.get('adresse')

        # Vérifier si l'email est unique (sauf si c'est le même utilisateur)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user.id:
            flash('Cet email est déjà utilisé par un autre compte', 'error')
            return redirect(url_for('profil'))

        try:
            user.username = username
            user.email = email
            user.telephone = telephone
            user.adresse = adresse
            db.session.commit()
            flash('Profil mis à jour avec succès !', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la mise à jour du profil', 'error')
            app.logger.error("Erreur lors de la mise à jour: %s", str(e))

        return redirect(url_for('profil'))

    return render_template('profil.html', user=user)

@app.route('/change-password', methods=['POST'])
def change_password():
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    # Imaginons que l'utilisateur actuel est dans session['user_id']
    user = User.query.get(session['user_id'])

    # Vérifier l'ancien mot de passe
    if not check_password_hash(user.password, old_password):
        flash('Ancien mot de passe incorrect', 'danger')
        return redirect('/profil')

    # Vérifier que les nouveaux mots de passe correspondent
    if new_password != confirm_password:
        flash('Les nouveaux mots de passe ne correspondent pas', 'danger')
        return redirect('/profil')

    # Tout est bon : on met à jour
    user.password = generate_password_hash(new_password)
    db.session.commit()

    flash('Mot de passe changé avec succès', 'success')
    return redirect('/profil')

@app.route('/security')
def security():
    return render_template('security.html')

####################################################################################################################################
# Dashboard d'une seule serre !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
####################################################################################################################################

# Variables globales pour stocker les données
# Variables globales pour stocker les données - MODIFIÉ
# Après : dictionnaire avec id_serre comme clé
live_data = {}


# Lecture des données depuis le fichier Excel - MODIFIÉ
def read_excel_data(path, serre=None):
    try:
        print(f"Tentative de lecture du fichier Excel : {path}")
        df = pd.read_excel(path, sheet_name='Feuil1')
        print("Fichier Excel lu avec succès. Colonnes disponibles:", df.columns.tolist())

        correspondances = {
            "temperature": "Température",
            "humidite_sol": "Humidité du sol",
            "humidite_air": "Humidité air",
            "co2": "CO2",
            "luminosite": "Luminosité",
            "arrosage": "Arrosage",
            "fertilisation": "Fertilisation"
        }

        serre_data = {key: {'value': 0, 'percent': 0} for key in correspondances.keys()}

        for key, column_name in correspondances.items():
            if column_name in df.columns:
                raw_value = df[column_name].iloc[-1]
                value = float(raw_value)
                serre_data[key]['value'] = value
                serre_data[key]['percent'] = value

                print(f"{key}: {value} (valeur brute: {raw_value})")

        # Gestion des notifications
        if serre:
            valeurs = {
                "Température": serre_data['temperature']['value'],
                "Humidité du sol": serre_data['humidite_sol']['value'],
                "Humidité air": serre_data['humidite_air']['value'],
                "CO2": serre_data['co2']['value'],
                "Luminosité": serre_data['luminosite']['value']
            }

            user_id = serre.id_user
            serre_id = serre.id_serre

            manage_notification(user_id, serre_id, "Température", valeurs["Température"], serre.temperature_min, serre.temperature_max)
            manage_notification(user_id, serre_id, "Humidité sol", valeurs["Humidité du sol"], serre.humidite_sol_min, serre.humidite_sol_max)
            manage_notification(user_id, serre_id, "Humidité air", valeurs["Humidité air"], serre.humidite_air_min, serre.humidite_air_max)
            manage_notification(user_id, serre_id, "CO2", valeurs["CO2"], serre.co2_min, serre.co2_max)
            manage_notification(user_id, serre_id, "Luminosité", valeurs["Luminosité"], serre.luminosite_min, serre.luminosite_max)

        return serre_data

    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier Excel: {str(e)}")
        traceback.print_exc()
        return None

# Route de base pour le dashboard - MODIFIÉ
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Veuillez vous connecter', 'error')
        return redirect(url_for('auth'))

    # Récupérer toutes les serres de l'utilisateur
    serres = Serre.query.filter_by(id_user=session['user_id']).all()
    if not serres:
        flash('Aucune serre trouvée', 'error')
        return redirect(url_for('serres'))

    # Récupérer l'ID de la serre sélectionnée depuis l'URL (GET ?serre_id=...)
    selected_id = request.args.get('serre_id', type=int)
    selected_serre = next((s for s in serres if s.id_serre == selected_id), serres[0])

    # Lecture du fichier Excel de cette serre et mise à jour du live_data spécifique
    data = read_excel_data(selected_serre.excel_path, selected_serre)
    if data:
        live_data[selected_serre.id_serre] = data

    # Récupérer les données de cette serre uniquement
    serre_data = live_data.get(selected_serre.id_serre, {
        'temperature': {'value': 0},
        'humidite_air': {'value': 0},
        'humidite_sol': {'value': 0},
        'luminosite': {'value': 0},
        'co2': {'value': 0},
        'arrosage': {'value': 0},
        'fertilisation': {'value': 0},
    })

    # Détection des alertes
    alertes = {
        'temperature': not (selected_serre.temperature_min <= serre_data['temperature']['value'] <= selected_serre.temperature_max),
        'humidite_air': not (selected_serre.humidite_air_min <= serre_data['humidite_air']['value'] <= selected_serre.humidite_air_max),
        'humidite_sol': not (selected_serre.humidite_sol_min <= serre_data['humidite_sol']['value'] <= selected_serre.humidite_sol_max),
        'luminosite': not (selected_serre.luminosite_min <= serre_data['luminosite']['value'] <= selected_serre.luminosite_max),
        'co2': not (selected_serre.co2_min <= serre_data['co2']['value'] <= selected_serre.co2_max)
    }

    return render_template(
        'dashboard.html',
        serres=serres,
        selected_serre=selected_serre,
        live_data=serre_data,
        alertes=alertes
    )


def insert_data_into_db(serre_id):
    try:
        now = datetime.utcnow()

        # Utilise les données spécifiques à cette serre
        data = live_data.get(serre_id, {})

        historique = {
            'id_serre': serre_id,
            'temperature': data.get('temperature', {}).get('value', 0),
            'humidite_sol': data.get('humidite_sol', {}).get('value', 0),
            'humidite_air': data.get('humidite_air', {}).get('value', 0),
            'co2': data.get('co2', {}).get('value', 0),
            'luminosite': data.get('luminosite', {}).get('value', 0),
            'arrosage': data.get('arrosage', {}).get('value', 0),
            'fertilisation': data.get('fertilisation', {}).get('value', 0),
            'timestamp': now
        }

        # Insertion dans la base
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO Historique (
                    id_serre, temperature, humidite_sol, humidite_air,
                    co2, luminosite, arrosage, fertilisation, timestamp
                ) VALUES (
                    :id_serre, :temperature, :humidite_sol, :humidite_air,
                    :co2, :luminosite, :arrosage, :fertilisation, :timestamp
                )
            """), historique)

        print(f"✅ Données live insérées dans Historique pour serre {serre_id} à {now}")

    except Exception as e:
        print(f"❌ Erreur insert_data_into_db : {e}")

# Fonction pour simuler l'actualisation des données - MODIFIÉ
def update_data(serre_id, excel_path, serre):
    with app.app_context():  # Activer le contexte Flask manuellement
        try:
            print(f"📥 Mise à jour des données pour la serre {serre_id} à partir de {excel_path}")
            data = read_excel_data(excel_path, serre)
            if data:
                live_data[serre_id] = data
            insert_data_into_db(serre_id)
        except Exception as e:
            print(f"[{serre_id}] ❌ Erreur dans update_data: {e}")



from datetime import datetime, timezone

def manage_notification(user_id, serre_id, param, value, min_val, max_val):
    min_val = float(min_val)
    max_val = float(max_val)

    # Protection contre division par zéro
    if max_val == min_val:
        print(f"⚠️ Impossible de calculer le pourcentage pour {param} car max == min ({max_val})")
        return

    seuil = None
    if value < min_val:
        seuil = "min"
    elif value > max_val:
        seuil = "max"

    if seuil:
        # Calcul du pourcentage de dépassement
        percent = (value - min_val) / (max_val - min_val) * 100

        # Enregistrement ou mise à jour dans DernieresAlertes (lié à la serre)
        existing_alert = DerniereAlerte.query.filter_by(serre_id=serre_id, type=param).first()
        if existing_alert:
            existing_alert.valeur = value
            existing_alert.pourcentage = percent
            existing_alert.seuil_min = min_val
            existing_alert.seuil_max = max_val
            existing_alert.timestamp = datetime.now(timezone.utc)
        else:
            new_alert = DerniereAlerte(
                serre_id=serre_id,
                type=param,
                valeur=value,
                pourcentage=percent,
                seuil_min=min_val,
                seuil_max=max_val,
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(new_alert)

        # Crée une notification uniquement si pas encore enregistrée
        existing_notif = Notification.query.filter_by(user_id=user_id, type=param, seuil=seuil).first()
        if not existing_notif:
            solutions = {
                ("Température", "max"): "Activez le système de refroidissement et augmentez l'aération.",
                ("Température", "min"): "Activez le chauffage pour maintenir une température stable.",
                ("Humidité air", "max"): "Réduisez l'humidification ou augmentez la ventilation.",
                ("Humidité air", "min"): "Vérifiez les systèmes d'humidification de l'air.",
                ("Humidité du sol", "max"): "Réduisez la fréquence ou la durée d’arrosage automatique.",
                ("Humidité du sol", "min"): "Vérifiez les systèmes d'irrigation et arrosez manuellement si nécessaire.",
                ("CO2", "max"): "Augmentez l’aération ou ouvrez les fenêtres pour évacuer le CO₂.",
                ("CO2", "min"): "Assurez-vous que les systèmes d'enrichissement en CO₂ fonctionnent correctement.",
                ("Luminosité", "max"): "Utilisez des filets d’ombrage ou réduisez l’exposition directe au soleil.",
                ("Luminosité", "min"): "Allumez les lampes de culture ou améliorez l’éclairage naturel."
            }

            msg = f"{param} a dépassé le seuil {seuil} ({value})."
            sol = solutions.get((param, seuil), "Aucune solution définie.")

            notif = Notification(
                user_id=user_id,
                type=param,
                seuil=seuil,
                message=msg,
                solution=sol
            )
            db.session.add(notif)

            user = User.query.get(user_id)
            if user and user.email:
                send_email_notification(
                    to_email=user.email,
                    subject=f"Alerte de serre : {param} hors seuil",
                    message=msg,
                    solution=sol
                )

        db.session.commit()

    else:
        # Suppression si retour à la normale
        Notification.query.filter_by(user_id=user_id, type=param).delete()
        DerniereAlerte.query.filter_by(serre_id=serre_id, type=param).delete()
        db.session.commit()

@app.route('/dernieres_alertes')
def get_dernieres_alertes():
    if 'user_id' not in session:
        return jsonify([])

    serre = Serre.query.filter_by(id_user=session['user_id']).first()
    if not serre:
        return jsonify([])

    alertes = DerniereAlerte.query.filter_by(serre_id=serre.id_serre).all()
    return jsonify([
        {
            'type': a.type,
            'valeur': round(a.valeur, 2),
            'pourcentage': round(a.pourcentage, 1)
        } for a in alertes
    ])


# Lancement de la mise à jour en temps réel dans un thread séparé
def before_first_request():
    # Code que vous souhaitez exécuter avant la première requête
    thread = threading.Thread(target=update_data)
    thread.daemon = True
    thread.start()

def handle_connect():
    print("Client connecté")

class Watcher(FileSystemEventHandler):
    def on_modified(self, event):
        path_modifie = event.src_path
        print(f"🟡 Fichier modifié : {path_modifie}")

        # On cherche la serre correspondant à ce path
        with app.app_context():
            serres = Serre.query.all()
            for serre in serres:
                if path_modifie == serre.excel_path:
                    print(f"🔁 Mise à jour pour serre {serre.nom_serre}")
                    update_data(serre.id_serre, serre.excel_path, serre)
            
def start_watcher():
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()


@app.route('/notifications')
def get_notifications():
    if 'user_id' not in session:
        return jsonify([])

    notifs = Notification.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        "type": n.type,
        "seuil": n.seuil,
        "message": n.message,
        "solution": n.solution
    } for n in notifs])

@app.route("/historique")
def historique_serre():
    if 'user_id' not in session:
        return jsonify([])

    serre = Serre.query.filter_by(id_user=session['user_id']).first()
    if not serre:
        return jsonify([])

    # Calcul des 48 dernières heures
    now = datetime.now()
    past = now - timedelta(hours=48)

    # Requête brute si la table n'est pas un modèle SQLAlchemy :
    query = text("""
        SELECT timestamp, Température_mean, Humidité_sol_mean, Humidité_air_mean,
               CO2_mean, Luminosité_mean
        FROM DonnéesAggregées
        WHERE serre_id = :serre_id AND timestamp >= :past
        ORDER BY timestamp DESC
    """)

    try:
        with db.engine.connect() as conn:
            result = conn.execute(query, {"serre_id": serre.id_serre, "past": past})
            rows = result.fetchall()

        # Conversion pour le frontend
        data = []
        for r in rows:
            data.append({
                "timestamp": r[0].strftime('%d/%m %H:%M'),
                "Température": round(r[1], 2),
                "Humidité_sol": round(r[2], 2),
                "Humidité_air": round(r[3], 2),
                "CO2": round(r[4], 2),
                "Luminosité": round(r[5], 2)
            })

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

def insert_aggregated_data(serre_id):
    try:
        serre = Serre.query.get(serre_id)
        if not serre:
            print(f"Serre introuvable pour id {serre_id}")
            return

        df = pd.read_excel(serre.excel_path)

        df["timestamp"] = pd.to_datetime(df["Horaire"])
        df.set_index("timestamp", inplace=True)

        df_grouped = df.resample("4h").agg({
            "Température": ["min", "max", "mean"],
            "Humidité du sol": ["min", "max", "mean"],
            "Humidité air": ["min", "max", "mean"],
            "CO2": ["min", "max", "mean"],
            "Luminosité": ["min", "max", "mean"]
        }).dropna().reset_index()

        for _, row in df_grouped.iterrows():
            ts = row["timestamp"]
            if isinstance(ts, pd.Series):
                ts = ts.iloc[0]  # extraire la première valeur
            if hasattr(ts, "to_pydatetime"):
                ts = ts.to_pydatetime()

            try:
                with engine.begin() as conn:
                    conn.execute(text("""
                        INSERT INTO DonnéesAggregées (
                            serre_id, timestamp,
                            Température_min, Température_max, Température_mean,
                            Humidité_sol_min, Humidité_sol_max, Humidité_sol_mean,
                            Humidité_air_min, Humidité_air_max, Humidité_air_mean,
                            CO2_min, CO2_max, CO2_mean,
                            Luminosité_min, Luminosité_max, Luminosité_mean
                        ) VALUES (
                            :serre_id, :timestamp,
                            :t_min, :t_max, :t_mean,
                            :hs_min, :hs_max, :hs_mean,
                            :ha_min, :ha_max, :ha_mean,
                            :co2_min, :co2_max, :co2_mean,
                            :lux_min, :lux_max, :lux_mean
                        )
                    """), {
                        "serre_id": serre_id,
                        "timestamp": ts,
                        "t_min": row[("Température", "min")],
                        "t_max": row[("Température", "max")],
                        "t_mean": row[("Température", "mean")],
                        "hs_min": row[("Humidité du sol", "min")],
                        "hs_max": row[("Humidité du sol", "max")],
                        "hs_mean": row[("Humidité du sol", "mean")],
                        "ha_min": row[("Humidité air", "min")],
                        "ha_max": row[("Humidité air", "max")],
                        "ha_mean": row[("Humidité air", "mean")],
                        "co2_min": row[("CO2", "min")],
                        "co2_max": row[("CO2", "max")],
                        "co2_mean": row[("CO2", "mean")],
                        "lux_min": row[("Luminosité", "min")],
                        "lux_max": row[("Luminosité", "max")],
                        "lux_mean": row[("Luminosité", "mean")]
                    })
            except Exception as e:
                print(f"❌ Erreur d'insertion agrégée (serre {serre_id}) : {e}")
    except Exception as e:
        print(f"Erreur lors de l'exécution SQL : {e}")

def schedule_insert(serre_id, interval=2*60):
    def run():
        while True:
            try:
                with app.app_context():
                    insert_aggregated_data(serre_id)
                print(f"✅ Données insérées pour serre {serre_id}")
                time.sleep(interval)
            except Exception as e:
                print(f"❌ Erreur dans l'insertion pour serre {serre_id} : {e}")
                time.sleep(60)  # petit délai avant retry
    threading.Thread(target=run, daemon=True).start()

@app.route("/test_insertion")
def test_insertion():
    if 'user_id' not in session:
        return "Non connecté", 403

    serre = Serre.query.filter_by(id_user=session['user_id']).first()
    if not serre:
        return "Aucune serre trouvée", 404

    insert_aggregated_data(serre.id_serre)
    return "✅ Insertion test effectuée."

@app.route("/graph_data")
def graph_data():
    if 'user_id' not in session:
        return jsonify({"error": "Non connecté"}), 403

    user_id = session['user_id']
    serre = Serre.query.filter_by(id_user=user_id).first()
    if not serre:
        return jsonify({"error": "Serre introuvable"}), 404

    cutoff = datetime.now() - timedelta(hours=48)

    # Si tu as un modèle SQLAlchemy pour cette table, adapte ça
    result = db.session.execute(text("""
        SELECT timestamp, Température_mean, Humidité_sol_mean, Humidité_air_mean, CO2_mean, Luminosité_mean
        FROM DonnéesAggregées
        WHERE serre_id = :serre_id AND timestamp >= :cutoff
        ORDER BY timestamp
    """), {"serre_id": serre.id_serre, "cutoff": cutoff})

    rows = result.fetchall()

    labels = [r.timestamp.strftime("%d/%m %Hh") for r in rows]
    temp = [r.Température_mean for r in rows]
    soil = [r.Humidité_sol_mean for r in rows]
    air = [r.Humidité_air_mean for r in rows]
    co2 = [r.CO2_mean for r in rows]
    light = [r.Luminosité_mean for r in rows]

    return jsonify({
        "labels": labels,
        "Température": temp,
        "Humidité_sol": soil,
        "Humidité_air": air,
        "CO2": co2,
        "Luminosité": light
    })

if __name__ == "__main__":
    load_data()
    threading.Thread(target=start_watcher, daemon=True).start()

    with app.app_context():
        serres = Serre.query.all()
        for serre in serres:
            schedule_insert(serre.id_serre)
            threading.Thread(
                target=update_data,
                args=(serre.id_serre, serre.excel_path, serre),
                daemon=True
            ).start()

    app.run(debug=True)

