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
            
            # --- DIZIONARIO DI TRADUZIONE ---
            TRANSLATION_MAP = {
                "Nutrition": "Riferimento", "Calories": "Calorie", "Protein": "Proteine",
                "Fat": "Grassi", "Carbohydrates": "Carboidrati", "Fibre": "Fibre"
            }

            # --- DATI DI BASE ---
            title = soup.find('h1', class_='recipe-card__title').get_text(strip=True) if soup.find('h1', class_='recipe-card__title') else 'Senza Titolo'
            tags_container = soup.find('div', class_='core-tags-wrapper__tags-container')
            tags = [link.get_text(strip=True).lstrip('#') for link in tags_container.find_all('a')] if tags_container else []
            picture_container = soup.find('div', class_='recipe-card__picture')
            cover_image = picture_container.find('img')['src'] if picture_container and picture_container.find('img') else None

            # --- METADATI ---
            def clean_text_from_label(label_tag):
                if not label_tag: return 'N/D'
                subtitle = label_tag.find('span', class_='core-feature-icons__subtitle')
                if subtitle: subtitle.extract()
                return label_tag.get_text(strip=True)
            prep_time = clean_text_from_label(soup.find('label', id='rc-icon-active-time-text'))
            total_time = clean_text_from_label(soup.find('label', id='rc-icon-total-time-text'))
            servings = clean_text_from_label(soup.find('label', id='rc-icon-quantity-icon-text'))

            # --- DETTAGLI RICETTA ---
            ingredients = [li.get_text(strip=True) for group in soup.select('ul[id^="ingredients-"]') for li in group.find_all('li')]
            steps_container = soup.find('div', id='preparation-steps')
            steps = [li.get_text(strip=True) for li in steps_container.find('ol').find_all('li')] if steps_container and steps_container.find('ol') else []
            
            # --- VALORI NUTRIZIONALI (con traduzione) ---
            nutritions = {}
            nutrition_container = soup.find('div', id='nutritions-desktop')
            if nutrition_container:
                terms = nutrition_container.find_all('dt')
                values = nutrition_container.find_all('dd')
                for term, value in zip(terms, values):
                    key = term.get_text(strip=True)
                    translated_key = TRANSLATION_MAP.get(key, key) # Traduce la chiave
                    nutritions[translated_key] = value.get_text(strip=True)
            
            useful_items = []
            items_container = soup.find('div', id='useful-items')
            if items_container:
                if items_container.find('h3'): items_container.find('h3').extract()
                items_text = items_container.get_text(strip=True)
                if items_text: useful_items = [item.strip() for item in items_text.split(',')]
            
            collections = []
            collections_container = soup.find('div', id='in-collections')
            if collections_container:
                for div in collections_container.select('a > div'):
                    if div.find('span'): div.find('span').extract()
                    collection_name = div.get_text(strip=True)
                    if collection_name: collections.append(collection_name)

            return {
                'title': title, 'tags': tags, 'path': file_path.replace('\\', '/'),
                'cover_image': cover_image, 'prep_time': prep_time, 'total_time': total_time,
                'servings': servings, 'ingredients': ingredients, 'steps': steps,
                'nutritions': nutritions, 'useful_items': useful_items, 'collections': collections
            }
            
    except Exception as e:
        print(f"!!! Errore grave durante l'analisi del file {file_path}: {e}")
        return None

def main():
    # LA FUNZIONE main() NON CAMBIA
    all_recipes_data = []
    titles_map = {}
    os.makedirs(DUPLICATES_FOLDER, exist_ok=True)
    files_to_process = [os.path.join(r, f) for r, _, fs in os.walk(RECIPES_FOLDER) for f in fs if f.lower().endswith(('.html', '.htm'))]
    print(f"Trovati {len(files_to_process)} file. Inizio indicizzazione...")
    for file_path in tqdm(files_to_process, desc="Indicizzazione"):
        data = extract_recipe_data(file_path)
        if not data or not data['title'] or data['title'] == 'Senza Titolo': continue
        if data['title'] not in titles_map:
            titles_map[data['title']] = file_path
            all_recipes_data.append(data)
        else:
            try:
                destination_path = os.path.join(DUPLICATES_FOLDER, file_path)
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                shutil.move(file_path, destination_path)
            except Exception as e: print(f"ERRORE durante lo spostamento: {e}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_recipes_data, f, ensure_ascii=False, indent=4)
    print(f"\nIndicizzazione completata! {len(all_recipes_data)} ricette uniche salvate in '{OUTPUT_FILE}'")

if __name__ == '__main__':
    main()