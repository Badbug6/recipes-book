import json
import os
import random
from collections import defaultdict
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from waitress import serve
from indexer import main as run_indexer

# --- CONFIGURAZIONE ---
RECIPES_BASE_FOLDER = 'le-mie-ricette'
# --------------------

app = Flask(__name__)

def load_and_process_recipes():
    try:
        with open('recipes.json', 'r', encoding='utf-8') as f:
            recipes_data = json.load(f)
    except FileNotFoundError:
        return {}, []

    recipes_by_folder = defaultdict(list)
    for recipe in recipes_data:
        folder_path = os.path.dirname(recipe['path'])
        display_folder = folder_path[len(RECIPES_BASE_FOLDER):].strip('/') if folder_path.startswith(RECIPES_BASE_FOLDER) else folder_path
        if not display_folder:
            display_folder = "(Ricette Principali)"
        recipes_by_folder[display_folder].append(recipe)
        
    return recipes_by_folder, recipes_data

recipes_by_folder, all_recipes = load_and_process_recipes()
sorted_folders = sorted(recipes_by_folder.keys())

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    selected_folder = request.args.get('folder', '')
    
    results = []
    display_title = ""

    if search_query:
        display_title = f'Risultati per "{search_query}"'
        query_lower = search_query.lower()
        results = [r for r in all_recipes if query_lower in r['title'].lower() or any(query_lower in t.lower() for t in r['tags'])]
    elif selected_folder:
        display_title = f'Ricette in "{selected_folder}"'
        results = recipes_by_folder.get(selected_folder, [])

    sample_size = min(15, len(sorted_folders))
    random_folders = random.sample(sorted_folders, k=sample_size) if sorted_folders else []

    return render_template('index.html', 
                           recipes=results,
                           folders=sorted_folders,
                           display_title=display_title,
                           search_query=search_query,
                           selected_folder=selected_folder,
                           random_folders=random_folders)

@app.route('/reindex', methods=['POST'])
def reindex_recipes():
    print("Avvio re-indicizzazione...")
    run_indexer()
    
    global recipes_by_folder, all_recipes, sorted_folders
    recipes_by_folder, all_recipes = load_and_process_recipes()
    sorted_folders = sorted(recipes_by_folder.keys())
    
    print("Re-indicizzazione completata!")
    return redirect(url_for('index'))

@app.route('/<path:filepath>')
def serve_recipe(filepath):
    return send_from_directory('.', filepath)

if __name__ == '__main__':
    print("Server di produzione avviato su http://0.0.0.0:8080")
    print("Apri nel browser: http://localhost:8080")
    serve(app, host='0.0.0.0', port=8080)