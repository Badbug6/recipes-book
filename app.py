import os
import json
import random
import time
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from indexer import main as run_indexer

app = Flask(__name__)

# --- CONFIGURAZIONI ---
app.config['SECRET_KEY'] = 'la-tua-chiave-segreta-super-difficile'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipebook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads/avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- INIZIALIZZAZIONE ESTENSIONI ---
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Per favore, accedi per vedere questa pagina."
login_manager.login_message_category = "info"

MEAL_PLAN_KEYWORDS = {
    "Colazione": ["colazione", "breakfast"], "Pranzo": ["pranzo", "lunch", "primi"],
    "Cena": ["cena", "dinner", "secondi"], "Spuntino": ["spuntino", "snack", "dolci", "dessert", "aperitivo"]
}

# --- TABELLA DI ASSOCIAZIONE PER I PREFERITI ---
favorites_association = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('recipe_title', db.String(255), db.ForeignKey('recipe_title.title'), primary_key=True)
)

# --- MODELLI DEL DATABASE ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    allergies_text = db.Column(db.String(500), nullable=True, default='')
    profile_image_url = db.Column(db.String(256), nullable=True, default='uploads/avatars/default_avatar.png')
    favorite_recipes = db.relationship('RecipeTitle', secondary=favorites_association, backref='favorited_by')
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class RecipeTitle(db.Model):
    title = db.Column(db.String(255), primary_key=True)

# --- CONFIGURAZIONI AGGIUNTIVE E FUNZIONI DI CARICAMENTO ---
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.context_processor
def inject_cache_buster():
    return dict(cache_buster=int(time.time()))

@app.before_request
def check_for_first_user():
    if not User.query.first():
        if request.endpoint and 'register' not in request.endpoint and 'static' not in request.endpoint:
            return redirect(url_for('register'))

# --- FUNZIONI DI UTILITÀ ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_for_allergens(ingredients, user_allergies_text):
    if not user_allergies_text: return []
    user_allergies = {}
    for line in user_allergies_text.strip().split('\n'):
        if ':' in line:
            allergen, keywords_str = line.split(':', 1)
            user_allergies[allergen.strip()] = [k.strip().lower() for k in keywords_str.split(',')]
    found_allergens = {allergen for ingredient in ingredients for allergen, keywords in user_allergies.items() if any(keyword in ingredient.lower() for keyword in keywords)}
    return sorted(list(found_allergens))

def load_and_process_recipes():
    try:
        with open('recipes.json', 'r', encoding='utf-8') as f: recipes_data = json.load(f)
    except FileNotFoundError: return [], []
    collections_map = {}
    for recipe in recipes_data:
        if 'collections' in recipe and recipe['collections']:
            for name in recipe['collections']:
                if name not in collections_map:
                    collections_map[name] = recipe.get('cover_image')
    sorted_collections = sorted([{'name': n, 'image': i} for n, i in collections_map.items()], key=lambda x: x['name'])
    return recipes_data, sorted_collections

all_recipes, all_collections = load_and_process_recipes()

# --- ROTTE DI AUTENTICAZIONE E PROFILO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        else: flash('Credenziali non valide. Riprova.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        if User.query.filter_by(username=username).first():
            flash('Questo nome utente esiste già.', 'warning')
            return redirect(url_for('register'))
        new_user = User(username=username)
        new_user.set_password(request.form.get('password'))
        db.session.add(new_user)
        db.session.commit()
        flash('Registrazione completata! Ora puoi effettuare il login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.allergies_text = request.form.get('allergies')
        file_to_upload = request.files.get('profile_photo')
        if file_to_upload and file_to_upload.filename != '':
            if allowed_file(file_to_upload.filename):
                filename = secure_filename(file_to_upload.filename)
                unique_filename = f"user_{current_user.id}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file_to_upload.save(filepath)
                current_user.profile_image_url = f'uploads/avatars/{unique_filename}'
            else:
                flash('Tipo di file non consentito. Scegli tra png, jpg, jpeg, gif.', 'danger')
        db.session.commit()
        flash('Profilo aggiornato!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html')

# --- API ENDPOINT PER I PREFERITI ---
@app.route('/toggle_favorite/<recipe_title>', methods=['POST'])
@login_required
def toggle_favorite(recipe_title):
    is_favorited = RecipeTitle.query.filter(RecipeTitle.title == recipe_title, RecipeTitle.favorited_by.any(id=current_user.id)).first()
    if is_favorited:
        fav_title = RecipeTitle.query.get(recipe_title)
        if fav_title: current_user.favorite_recipes.remove(fav_title)
        db.session.commit()
        return {'status': 'ok', 'favorited': False}
    else:
        fav_title = RecipeTitle.query.get(recipe_title)
        if not fav_title:
            fav_title = RecipeTitle(title=recipe_title)
            db.session.add(fav_title)
        current_user.favorite_recipes.append(fav_title)
        db.session.commit()
        return {'status': 'ok', 'favorited': True}

# --- ROTTE PRINCIPALI ---
# --- ROTTA HOMEPAGE (COMPLETAMENTE RISCRITTA) ---
@app.route('/')
@login_required
def index():
    user_favorites = [fav.title for fav in current_user.favorite_recipes]
    
    # Se c'è una ricerca, mostriamo i risultati come prima
    search_query = request.args.get('search', '')
    if search_query:
        display_title = f'Risultati per "{search_query}"'
        query_lower = search_query.lower()
        results = [r for r in all_recipes if query_lower in r['title'].lower() or any(query_lower in t.lower() for t in r.get('tags', []))]
        return render_template('index.html', is_search_result=True, recipes=results, display_title=display_title, user_favorites=user_favorites)

    # NUOVA LOGICA PER LA HOMEPAGE DI DEFAULT
    # 1. Prendiamo una ricetta "Trending" (una a caso)
    trending_recipe = random.choice(all_recipes) if all_recipes else None
    
    # 2. Prendiamo una lista di altre ricette per la griglia
    other_recipes = [r for r in all_recipes if r['title'] != (trending_recipe['title'] if trending_recipe else '')]
    random.shuffle(other_recipes)
    
    # 3. Prepariamo i filtri per le categorie
    filter_categories = list(MEAL_PLAN_KEYWORDS.keys())

    return render_template('index.html',
                           is_search_result=False,
                           trending_recipe=trending_recipe,
                           recipes=other_recipes[:10], # Mostriamo al massimo 10 ricette
                           user_favorites=user_favorites,
                           filter_categories=filter_categories)

@app.route('/collections')
@login_required
def collections():
    return render_template('collections.html', collections=all_collections)

@app.route('/recipe/<recipe_title>')
@login_required
def recipe_detail(recipe_title):
    recipe = next((r for r in all_recipes if r['title'] == recipe_title), None)
    if recipe:
        # LA MODIFICA È QUI: Passiamo la lista dei preferiti
        user_favorites = [fav.title for fav in current_user.favorite_recipes]
        found_allergens = check_for_allergens(recipe.get('ingredients', []), current_user.allergies_text)
        return render_template('recipe_detail.html', 
                               recipe=recipe, 
                               found_allergens=found_allergens,
                               user_favorites=user_favorites) # <-- AGGIUNTO
    return "Ricetta non trovata", 404

@app.route('/reindex', methods=['POST'])
@login_required
def reindex_recipes():
    run_indexer()
    global all_recipes, all_collections
    all_recipes, all_collections = load_and_process_recipes()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)