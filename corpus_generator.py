import json
import os
import re
import random
import requests
import pandas as pd
from datetime import datetime

# Configuration
SOURCES_FILE = 'sources.json'
OUTPUT_DIR = 'output'
DATA_DIR = 'data'
TARGET_TOTAL = 20000
TARGET_PER_ELEMENT = 5000
TARGET_PHRASES = 12000
TARGET_PARAGRAPHS = 8000
TARGET_PHRASES_PER_ELEMENT = 3000
TARGET_PARAGRAPHS_PER_ELEMENT = 2000

# Keywords for elements (Portuguese)
KEYWORDS = {
    'água': [
        'água', 'rio', 'mar', 'oceano', 'chuva', 'lago', 'lagoa', 'fonte', 'nascente',
        'onda', 'espuma', 'orvalho', 'umidade', 'molhado', 'inundação', 'correnteza',
        'fluir', 'beber', 'sede', 'aquático', 'submerso', 'mergulhar', 'nadar', 'barco',
        'navio', 'poço', 'cachoeira', 'tempestade', 'garoa', 'aguaceiro', 'dilúvio',
        'gota', 'lágrima', 'suor', 'vapor', 'gelo', 'neve', 'granizo', 'bruma', 'neblina'
    ],
    'terra': [
        'terra', 'solo', 'chão', 'poeira', 'areia', 'pedra', 'rocha', 'montanha', 'monte',
        'colina', 'vale', 'campo', 'floresta', 'mata', 'árvore', 'raiz', 'folha', 'flor',
        'fruto', 'semente', 'plantar', 'colher', 'jardim', 'horta', 'fazenda', 'sítio',
        'caminho', 'estrada', 'trilha', 'lama', 'barro', 'argila', 'mineral', 'mina',
        'caverna', 'gruta', 'terreno', 'território', 'mundo', 'planeta', 'seco', 'árido'
    ],
    'ar': [
        'ar', 'vento', 'brisa', 'sopro', 'respirar', 'fôlego', 'céu', 'nuvem', 'atmosfera',
        'voar', 'pássaro', 'ave', 'asa', 'pena', 'etéreo', 'invisível', 'espaço', 'vazio',
        'altura', 'alto', 'elevar', 'subir', 'flutuar', 'pairar', 'suspiro', 'grito',
        'voz', 'som', 'eco', 'canção', 'música', 'melodia', 'ruído', 'silêncio', 'furacão',
        'vendaval', 'ciclone', 'tornado', 'aéreo', 'gasoso'
    ],
    'fogo': [
        'fogo', 'chama', 'labareda', 'incêndio', 'queimar', 'arder', 'quente', 'calor',
        'sol', 'luz', 'brilho', 'raio', 'relâmpago', 'faísca', 'centelha', 'brasa',
        'cinza', 'fumaça', 'ferver', 'cozinhar', 'assar', 'fritar', 'derreter', 'fundir',
        'vulcão', 'lava', 'magma', 'inferno', 'diabo', 'demônio', 'paixão', 'amor',
        'ódio', 'raiva', 'fúria', 'cólera', 'sangue', 'vermelho', 'laranja', 'amarelo'
    ]
}

def download_text(url, filename):
    if os.path.exists(filename):
        return True
    try:
        response = requests.get(url)
        response.raise_for_status()
        # Try to detect encoding, default to utf-8
        response.encoding = 'utf-8' 
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def clean_text(text):
    # Remove Gutenberg headers/footers (simple heuristic)
    # Look for "*** START OF THE PROJECT GUTENBERG EBOOK" and "*** END OF THE PROJECT GUTENBERG EBOOK"
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
    
    start_idx = text.find(start_marker)
    if start_idx != -1:
        text = text[start_idx + len(start_marker):]
        # Skip the title/author lines usually following
        text = text.split('\n', 20)[-1] # Skip first 20 lines after marker roughly
        
    end_idx = text.find(end_marker)
    if end_idx != -1:
        text = text[:end_idx]
        
    return text

def count_words(text):
    return len(re.findall(r'\b\w+\b', text))

def classify_element(text):
    text_lower = text.lower()
    scores = {el: 0 for el in KEYWORDS}
    
    for element, words in KEYWORDS.items():
        for word in words:
            # Simple word matching, could be improved with regex for boundaries
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                scores[element] += 1
                
    # Get max score
    if not scores:
        return None
        
    max_element = max(scores, key=scores.get)
    if scores[max_element] > 0:
        return max_element
    return None

def process_corpus():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
        sources = json.load(f)
        
    all_phrases = []
    all_paragraphs = []
    
    for source in sources:
        print(f"Processing {source['title']}...")
        filename = os.path.join(DATA_DIR, f"{source['author']}_{source['title']}.txt".replace(' ', '_'))
        if download_text(source['url'], filename):
            with open(filename, 'r', encoding='utf-8') as f:
                raw_text = f.read()
                
            text = clean_text(raw_text)
            
            # Split into paragraphs first
            paragraphs = re.split(r'\n\s*\n', text)
            
            for p in paragraphs:
                p = p.strip()
                if not p:
                    continue
                    
                word_count = count_words(p)
                
                # Check if it's a valid paragraph
                if 50 <= word_count <= 100:
                    element = classify_element(p)
                    if element:
                        all_paragraphs.append({
                            'elemento': element,
                            'autor': source['author'],
                            'obra': source['title'],
                            'titulo do texto': f"Trecho de {source['title']}",
                            'trecho': p,
                            'tipo': 'parágrafo'
                        })
                
                # Split paragraph into sentences (phrases)
                # Simple regex split by . ! ?
                sentences = re.split(r'(?<=[.!?])\s+', p)
                for s in sentences:
                    s = s.strip()
                    s_word_count = count_words(s)
                    if 10 <= s_word_count <= 30:
                        element = classify_element(s)
                        if element:
                            all_phrases.append({
                                'elemento': element,
                                'autor': source['author'],
                                'obra': source['title'],
                                'titulo do texto': f"Trecho de {source['title']}",
                                'trecho': s,
                                'tipo': 'frase'
                            })

    # Balancing
    final_data = []
    
    # Phrases
    phrases_by_element = {el: [] for el in KEYWORDS}
    for p in all_phrases:
        phrases_by_element[p['elemento']].append(p)
        
    for el in KEYWORDS:
        available = phrases_by_element[el]
        count = len(available)
        print(f"Phrases for {el}: {count}")
        if count >= TARGET_PHRASES_PER_ELEMENT:
            selected = random.sample(available, TARGET_PHRASES_PER_ELEMENT)
        else:
            selected = available # Take all if not enough
            # Note: In a real scenario we might need to duplicate or find more sources
        final_data.extend(selected)

    # Paragraphs
    paragraphs_by_element = {el: [] for el in KEYWORDS}
    for p in all_paragraphs:
        paragraphs_by_element[p['elemento']].append(p)
        
    for el in KEYWORDS:
        available = paragraphs_by_element[el]
        count = len(available)
        print(f"Paragraphs for {el}: {count}")
        if count >= TARGET_PARAGRAPHS_PER_ELEMENT:
            selected = random.sample(available, TARGET_PARAGRAPHS_PER_ELEMENT)
        else:
            selected = available
        final_data.extend(selected)
        
    # Create DataFrame
    df = pd.DataFrame(final_data)
    
    # Export
    date_str = datetime.now().strftime("%d-%m-%Y")
    output_filename = f"corpus-elementos-v.0-{date_str}.ods"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    print(f"Saving to {output_path} with {len(df)} records...")
    try:
        df.to_excel(output_path, engine='odf', index=False)
        print("Done!")
    except Exception as e:
        print(f"Error saving ODS: {e}")
        # Fallback to CSV if ODS fails
        csv_path = output_path.replace('.ods', '.csv')
        df.to_csv(csv_path, index=False)
        print(f"Saved as CSV instead: {csv_path}")

if __name__ == "__main__":
    process_corpus()
