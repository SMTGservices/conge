import json, datetime
from flask import Flask, render_template, session, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField,  DateField
from wtforms.validators import NumberRange
from wtforms.validators import DataRequired


app = Flask(__name__)
# Configurer une clé secrète SECRET_KEY
# Nous apprendrons plus tard de bien meilleures façons de le faire !!
app.config['SECRET_KEY'] = 'mysecretkey'

@app.route('/', methods=['GET', 'POST'])
def index():
    # Créer une instance du formulaire.
    form = CongeForm()
    # Si le formulaire est valide lors de la soumission
    # (nous parlerons ensuite de validation)
    if form.validate_on_submit():
        # Récupérer les données de l'espèce sur le formulaire
        session['date_derniere_reprise'] = form.date_derniere_reprise.data
        session['date_depart'] = form.date_depart.data
        session['jours_anciennete'] = form.jours_anciennete.data
        session['jours_enfants'] = form.jours_enfants.data
        session['jours_permission'] = form.jours_permission.data
        #print(session['date_derniere_reprise'])
        return redirect(url_for("conge"))

    return render_template('base.html', form=form)

def calculer_jours_conge(date_debut, date_fin):
    jours = (date_fin.year - date_debut.year) * 360 + (date_fin.month - date_debut.month) * 30 + (date_fin.day - date_debut.day)
    return round(jours / 15)

def est_jour_ouvrable(date, jours_feries):
    return date.weekday() < 6 and date not in jours_feries

def trouver_premier_jour_ouvrable(date, jours_feries):
    while not est_jour_ouvrable(date, jours_feries):
        date += datetime.timedelta(days=1)
    return date

def calculer_date_reprise(date_debut_conge, jours_conge, jours_supplementaires, jours_feries):
    date_courante = trouver_premier_jour_ouvrable(date_debut_conge + datetime.timedelta(days=1), jours_feries)
    jours_comptes = 0
    
    while jours_comptes < (jours_conge + jours_supplementaires):
        if est_jour_ouvrable(date_courante, jours_feries):
            jours_comptes += 1
        date_courante += datetime.timedelta(days=1)
    
    if est_jour_ouvrable(date_courante, jours_feries):
        date_courante -= datetime.timedelta(days=1)

    # Trouver le prochain jour ouvrable pour la reprise
    while not est_jour_ouvrable(date_courante, jours_feries):
        date_courante += datetime.timedelta(days=1)

    return date_courante

def valider_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Format de date invalide. Utilisez le format YYYY-MM-DD.")
        return None

def saisir_entier_positif(message):
    while True:
        try:
            valeur = int(input(message))
            if valeur >= 0:
                return valeur
            else:
                print("Veuillez entrer un nombre positif ou nul.")
        except ValueError:
            print("Veuillez entrer un nombre entier valide.")

@app.route('/conge')
def conge():
    content = {}
    # Calcul des jours de congé
    from datetime import datetime
    dr = datetime.strptime(session['date_derniere_reprise'], "%a, %d %b %Y %H:%M:%S %Z")
    date_derniere_reprise= dr.strftime("%Y-%m-%d")
    date_derniere_reprise=datetime.strptime(date_derniere_reprise, '%Y-%m-%d').date()
    
    #print('La date de reprise :'+ str(date_derniere_reprise.year))
    dd = datetime.strptime(session['date_depart'], "%a, %d %b %Y %H:%M:%S %Z")
    date_depart= dd.strftime("%Y-%m-%d")
    date_depart=datetime.strptime(date_depart, '%Y-%m-%d').date()
    
    #print('La date de depart :'+ str(date_depart.month))

    #print('La date: '+session['date_depart'])

    jours_conge = calculer_jours_conge(date_derniere_reprise, date_depart)
    # Calcul du total des jours supplémentaires
    jours_supplementaires = int(session['jours_anciennete']) + int(session['jours_enfants']) + int(session['jours_permission'])
    # Calcul de la date de reprise
    date_reprise = calculer_date_reprise(date_depart, jours_conge, jours_supplementaires, jours_feries)

    content['jours_conge']= jours_conge
    content['jours_supplementaires']= jours_supplementaires
    content['date_reprise']= date_reprise

    return render_template('conge.html',results=content)

# Jours fériés 2024-2025
jours_feries = [
    datetime.date(2024, 5, 1),   # fete du travail
    datetime.date(2024, 5, 9),   # Jour de ascension
    datetime.date(2024, 5, 20),  # Lundi Pentecote
    datetime.date(2024, 7, 16),  # 16 Juillet 2024 Tamkharit
    datetime.date(2024, 8, 15),  # 15 Aout 2024
    datetime.date(2024, 9, 16),  # 16 septembre 2024
    datetime.date(2024, 11, 1),  # 1er novembre 2024
    datetime.date(2024, 12, 25), # 25 décembre 2024
    datetime.date(2025, 1, 1),   # 1er janvier 2025
]


class CongeForm(FlaskForm):
    date_derniere_reprise = DateField('Date dernier reprise', format='%Y-%m-%d', validators=[DataRequired()])
    date_depart = DateField('Date Depart', format='%Y-%m-%d', validators=[DataRequired()])
    #date_depart = DateField(label='date_depart',format='%Y-%m-%d',validators = [DataRequired('selectionner la date de depart')])
    jours_anciennete = IntegerField('Jours anciennete')
    jours_enfants = IntegerField('Jours enfants')
    jours_permission =   IntegerField('Jours permission') 

    submit = SubmitField('Calcul Conge')



if __name__== '__main__':
    app.run(debug=True) 