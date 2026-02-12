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

KEYWORDS = {
    'água': [
        'água', 'rio', 'mar', 'oceano', 'chuva', 'lago', 'lagoa', 'fonte', 'nascente',
        'onda', 'espuma', 'orvalho', 'umidade', 'molhado', 'inundação', 'correnteza',
        'fluir', 'beber', 'sede', 'aquático', 'submerso', 'mergulhar', 'nadar', 'barco',
        'navio', 'poço', 'cachoeira', 'tempestade', 'garoa', 'aguaceiro', 'dilúvio',
        'gota', 'lágrima', 'suor', 'vapor', 'gelo', 'neve', 'granizo', 'bruma', 'neblina',
        # Expansão
        'vaga', 'vagalhão', 'estuário', 'ribeiro', 'arroio', 'torrente', 'preamar', 
        'maré', 'sereia', 'ninfas', 'líquido', 'cristalino', 'espelhar', 'vazar', 
        'naufrágio', 'galé', 'caravela', 'salitre', 'borrifo', 'Poção', 'estio'
    ],
    'terra': [
        'terra', 'solo', 'chão', 'poeira', 'areia', 'pedra', 'rocha', 'montanha', 'monte',
        'colina', 'vale', 'campo', 'floresta', 'mata', 'árvore', 'raiz', 'folha', 'flor',
        'fruto', 'semente', 'plantar', 'colher', 'jardim', 'horta', 'fazenda', 'sítio',
        'caminho', 'estrada', 'trilha', 'lama', 'barro', 'argila', 'mineral', 'mina',
        'caverna', 'gruta', 'terreno', 'território', 'mundo', 'planeta', 'seco', 'árido',
        # Expansão
        'pântano', 'lodo', 'gleba', 'penhasco', 'rochedo', 'outeiro', 'selva', 'bosque',
        'arbusto', 'folhagem', 'tronco', 'sepulcro', 'tumba', 'pó', 'pedregulho', 
        'planície', 'sertão', 'ermidada', 'pátria', 'chácara', 'quintal', 'cortiço'
    ],
    'ar': [
        'ar', 'vento', 'brisa', 'sopro', 'respirar', 'fôlego', 'céu', 'nuvem', 'atmosfera',
        'voar', 'pássaro', 'ave', 'asa', 'pena', 'etéreo', 'invisível', 'espaço', 'vazio',
        'altura', 'alto', 'elevar', 'subir', 'flutuar', 'pairar', 'suspiro', 'grito',
        'voz', 'som', 'eco', 'canção', 'música', 'melodia', 'ruído', 'silêncio', 'furacão',
        'vendaval', 'ciclone', 'tornado', 'aéreo', 'gasoso',
        # Expansão
        'zéfiro', 'aura', 'bafo', 'exalação', 'firmamento', 'astros', 'vôo', 'plumagem',
        'aragem', 'borrasca', 'tormenta', 'fragor', 'estrepito', 'harmonia', 'canto',
        'vaguear', 'ascender', 'nefelibata', 'éter', 'hálito', 'psique'
    ],
    'fogo': [
        'fogo', 'chama', 'labareda', 'incêndio', 'queimar', 'arder', 'quente', 'calor',
        'sol', 'luz', 'brilho', 'raio', 'relâmpago', 'faísca', 'centelha', 'brasa',
        'cinza', 'fumaça', 'ferver', 'cozinhar', 'assar', 'fritar', 'derreter', 'fundir',
        'vulcão', 'lava', 'magma', 'inferno', 'diabo', 'demônio', 'paixão', 'amor',
        'ódio', 'raiva', 'fúria', 'cólera', 'sangue', 'vermelho', 'laranja', 'amarelo',
        # Expansão (Machado/Barreto/Gregório):
        'fogueira', 'lume', 'clarão', 'incandescência', 'abrasar', 'crepitar', 'cinzas',
        'tição', 'pira', 'feveraço', 'estio', 'febre', 'ímpeto', 'entusiasmo', 'desejo',
        'luxúria', 'suplício', 'purga', 'candente', 'fulgor', 'resplendor', 'astro-rei'
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
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
    
    start_idx = text.find(start_marker)
    if start_idx != -1:
        text = text[start_idx + len(start_marker):]
        text = text.split('\n', 20)[-1] 
        
        
    end_idx = text.find(end_marker)
    if end_idx != -1:
        text = text[:end_idx]

    # FIX: Merge lines that do NOT end with sentence punctuation.
    # This handles "double spacing" and sentences split across lines (including proper nouns like Rio de\nJaneiro)
    # Terminators: . ? ! : " ” … (and anything else that ends a paragraph?)
    # We capture the last char and restore it, replacing newline(s) with space.
    text = re.sub(r'([^.\?!\:\"\”\…\n])\n+', r'\1 ', text)

    # FIX 2: Normalize single newlines ensuring remaining single newlines (after punctuation) are also space
    # (unless they are double newlines which mean paragraph break).
    # If a line ended with '.', we KEPT the newline above.
    # Now we must ensure that if it was just a line wrap (single \n), it breaks.
    # But wait, if text was "End.\nStart", and we kept \n.
    # The next regex (?<!\n)\n(?!\n) will see single \n and turn it to space.
    # Result: "End. Start". Correct.
    # If text was "End.\n\nStart", and we kept \n\n.
    # The next regex will see double \n and KEEP it.
    # Result: "End.\n\nStart". Correct (Paragraph break).
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        
    return text

def count_words(text):
    return len(re.findall(r'\b\w+\b', text))

def is_valid_context(text, keyword, start_index):
    """
    Check if the keyword usage is valid (not part of a proper noun entity like 'Rio de Janeiro').
    """
    # 1. Check for "Rio de Janeiro", "Rio Grande", etc.
    if keyword.lower() == 'rio':
        # Look ahead for " de " or " Grande"
        # Extract a window around the word
        window = text[start_index:start_index+20] # "Rio de Janeiro..."
        if re.match(r'rio\s+de\s+[A-Z]', window, re.IGNORECASE):
            return False
        if re.match(r'rio\s+grande', window, re.IGNORECASE):
            return False
            
    # NEW: Generic Proper Noun Filtering
    # If the found keyword is Capitalized in the text, and it's not the start of the sentence
    # (Checking start of sentence is hard without reliable split, but we can check if previous char is .!?)
    # For now, let's trust the "Rio" specific filter as it's the most common false positive for 'água'.
    
    return True

def classify_element(text):
    text_lower = text.lower()
    scores = {el: 0 for el in KEYWORDS}
    
    for element, words in KEYWORDS.items():
        for word in words:
            # Iterate over all matches to check context
            for match in re.finditer(r'\b' + re.escape(word) + r'\b', text_lower):
                if is_valid_context(text, word, match.start()):
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
        
    all_paragraphs = []
    
    for source in sources:
        print(f"Processing {source['title']}...")
        filename = os.path.join(DATA_DIR, f"{source['author']}_{source['title']}.txt".replace(' ', '_'))
        if download_text(source['url'], filename):
            with open(filename, 'r', encoding='utf-8') as f:
                raw_text = f.read()
                
            text = clean_text(raw_text)
            
            # Split into paragraphs 
            paragraphs = re.split(r'\n\s*\n', text)
            
            for i, p in enumerate(paragraphs):
                p = p.strip()
                if not p:
                    continue
                    
                word_count = count_words(p)
                
                
                # Check if it's a valid paragraph
                # Adjusted range: 5 to 600 words to capture poetry lines/stanzas and long prose
                if 5 <= word_count <= 600: 
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

    # Balancing
    final_data = []
    
    # Paragraphs Only
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
    output_filename = f"corpus-elementos-v.1-{date_str}.ods" # Bumped version
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
