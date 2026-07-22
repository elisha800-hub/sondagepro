# SondagePro - Application de Sondage en Ligne

Application Django professionnelle pour créer et gérer des sondages en ligne avec authentification utilisateur, partage par lien et visualisation des résultats.

## 🚀 Hébergement Gratuit

### Option 1: Render (Recommandé - Plus facile)

1. **Créer un compte sur [render.com](https://render.com)**
2. **Créer un nouveau Web Service**
   - Connectez votre repository GitHub
   - Configurez:
     - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
     - **Start Command**: `gunicorn sondage.wsgi:application`
     - **Python Version**: 3.11.7

3. **Configurer les variables d'environnement**:
   ```
   DEBUG=False
   SECRET_KEY=votre_clé_secrète_ici
   ALLOWED_HOSTS=votre-app.onrender.com
   ```

4. **Configurer la base de données** (PostgreSQL gratuit sur Render):
   - Ajoutez une base de données PostgreSQL
   - Ajoutez la variable d'environnement `DATABASE_URL`

5. **Déployer** - Render déploiera automatiquement votre application

### Option 2: PythonAnywhere

1. **Créer un compte sur [pythonanywhere.com](https://pythonanywhere.com)**
2. **Créer un nouveau Web App** (Python 3.11)
3. **Uploader votre code** via Git ou drag-and-drop
4. **Configurer les variables d'environnement** dans le WSGI configuration file
5. **Installer les dépendances**: `pip install -r requirements.txt`
6. **Configurer la base de données** SQLite (inclus) ou PostgreSQL
7. **Lancer l'application**

### Option 3: Railway

1. **Créer un compte sur [railway.app](https://railway.app)**
2. **Déployer depuis GitHub**
3. **Railway détectera automatiquement Django**
4. **Configurer les variables d'environnement**
5. **Ajouter une base de données PostgreSQL**

### Option 4: Heroku (Plan gratuit limité)

1. **Installer Heroku CLI**
2. **Créer un compte sur [heroku.com](https://heroku.com)**
3. **Commandes**:
   ```bash
   heroku create
   heroku addons:create heroku-postgresql:mini
   heroku config:set DEBUG=False SECRET_KEY=votre_clé ALLOWED_HOSTS=votre-app.herokuapp.com
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   heroku open
   ```

## 📋 Prérequis

- Python 3.11+
- pip
- Git

## 🔧 Installation Locale

```bash
# Cloner le repository
git clone https://github.com/elisha800-hub/sondagepro.git
cd sondagepro

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
export DEBUG=True
export SECRET_KEY=votre_clé_secrète
export ALLOWED_HOSTS=localhost,127.0.0.1

# Exécuter les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## 🗄️ Base de Données

- **Développement**: SQLite (par défaut)
- **Production**: PostgreSQL (recommandé)

## 🔐 Sécurité

- Validation des mots de passe avec indicateur de force
- Protection CSRF
- Sessions sécurisées
- Tokens de partage uniques pour les sondages

## 📱 Fonctionnalités

- ✅ Authentification utilisateur sécurisée
- ✅ Création de sondages avec plusieurs types de questions
- ✅ Questions conditionnelles
- ✅ Partage par lien unique
- ✅ Réponses anonymes ou authentifiées
- ✅ Visualisation des résultats avec graphiques
- ✅ Export CSV des réponses
- ✅ Interface responsive moderne
- ✅ Design professionnel

## 🎨 Design

- Interface moderne avec gradient violet/bleu
- Animations fluides
- 100% responsive
- Typographie professionnelle (Inter)
- Effets glassmorphism

## 📞 Support

Pour toute question concernant le déploiement, consultez la documentation de la plateforme d'hébergement choisie.
