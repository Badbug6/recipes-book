import os
import json
import shutil
from bs4 import BeautifulSoup
from tqdm import tqdm

# --- CONFIGURAZIONE ---
RECIPES_FOLDER = 'le-mie-ricette' 
OUTPUT_FILE = 'recipes.json'
DUPLICATES_FOLDER = 'duplicati' 
# --------------------

def extract_recipe_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')
            title_tag = soup.find('h1', class_='recipe-card__title')
            title = title_tag.get_text(strip=True) if title_tag else 'Senza Titolo'
            tags = []
            tags_container = soup.find('div', class_='core-tags-wrapper__tags-container')
            if tags_container:
                tag_links = tags_container.find_all('a')
                tags = [link.get_text(strip=True).lstrip('#') for link in tag_links]
            return {
                'title': title,
                'tags': tags,
                'path': file_path.replace('\\', '/')
            }
    except Exception:
        return None

def main():
    all_recipes_data = []
    titles_map = {}
    os.makedirs(DUPLICATES_FOLDER, exist_ok=True)

    print("Passo 1: Scansione dei file in corso...")
    files_to_process = []
    for root, _, files in os.walk(RECIPES_FOLDER):
        for filename in files:
            if filename.lower().endswith(('.html', '.htm')):
                files_to_process.append(os.path.join(root, filename))

    print(f"Trovati {len(files_to_process)} file da analizzare.")
    print("Passo 2: Indicizzazione e controllo duplicati...")

    for file_path in tqdm(files_to_process, desc="Indicizzazione"):
        data = extract_recipe_data(file_path)
        
        if not data or not data['title'] or data['title'] == 'Senza Titolo':
            continue

        if data['title'] not in titles_map:
            titles_map[data['title']] = file_path
            all_recipes_data.append(data)
        else:
            try:
                destination_path = os.path.join(DUPLICATES_FOLDER, file_path)
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                shutil.move(file_path, destination_path)
            except Exception as e:
                print(f"ERRORE durante lo spostamento del duplicato {file_path}: {e}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_recipes_data, f, ensure_ascii=False, indent=4)

    print(f"\nIndicizzazione completata! {len(all_recipes_data)} ricette uniche salvate in '{OUTPUT_FILE}'")
    print(f"Eventuali file duplicati sono stati spostati nella cartella '{DUPLICATES_FOLDER}'.")

if __name__ == '__main__':
    main()