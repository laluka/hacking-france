import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
# URL de la liste des serveurs Discord
discord_urls_file = 'https://raw.githubusercontent.com/Frozenka/hacking-france/main/src/assets/misc/liste_discord.txt'

# Définir le chemin du fichier de sortie
output_file_path = os.path.join('src', 'assets', 'misc', 'discord_servers_info.json')

# URL de l'image par défaut
default_image_url = 'https://logo-marque.com/wp-content/uploads/2020/12/Discord-Logo.png'

def fetch_discord_urls(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  # Forcer l'encodage UTF-8
    response.raise_for_status()
    return response.text.splitlines()

def is_valid_url(url):
    return url.startswith(('http://', 'https://'))

def extract_discord_info(url):
    if not is_valid_url(url):
        print(f"URL invalide : {url}")
        return None

    response = requests.get(url)
    response.encoding = 'utf-8'  # Forcer l'encodage UTF-8
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraction des informations à partir du code source HTML
    description_tag = soup.find('meta', {'name': 'description'})
    description = description_tag['content'] if description_tag else 'Description non disponible'

    # Extraction du nombre de membres dans la description
    members_match = re.search(r'Discord\s*(.*?)\s*autres\s*membres\s*et\s*profite\s*du\s*chat\s*vocal\s*et\s*textuel\s*gratuit', description, re.IGNORECASE)
    if members_match:
        members_text = members_match.group(1).strip()
        # Retirer le texte "- discute avec" s'il est présent
        members = re.sub(r'-\s*discute\s*avec\s*', '', members_text).strip() + ' membres'
    else:
        # Recherche d'une autre méthode pour extraire le nombre de membres
        members_match = re.search(r'\|\s*(\d+)\s*(membres|members)', description, re.IGNORECASE)
        if members_match:
            members = members_match.group(1).strip()
        else:
            members = 'Données non disponibles'
    
    # Traiter la description après avoir modifié la variable membres
    description = re.split(r'[|-]', description, 1)[0].strip()

    # Extraction du logo
    image_tag = soup.find('meta', {'property': 'og:image'})
    image_url = image_tag['content'] if image_tag else default_image_url

    # Extraction du nom
    title_tag = soup.find('meta', {'property': 'og:title'})
    title = title_tag['content'] if title_tag else 'Nom non disponible'

    return {
        'name': title.strip(),
        'description': description.strip(),
        'members': members,
        'image': image_url.strip(),
        'link': url.strip()
    }

def main():
    discord_urls = fetch_discord_urls(discord_urls_file)
    discord_channels = []
    
    for url in discord_urls:
        info = extract_discord_info(url)
        time.sleep(2)  # Attendre 2 secondes entre les requêtes
        if info is not None:  # Inclure seulement si info n'est pas None
            discord_channels.append(info)
            print(f"Infos récupérées pour {url}: {info}")

    # Écriture des résultats dans un fichier JSON
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(discord_channels, json_file, indent=2, ensure_ascii=False)

    print(f"Les informations des serveurs Discord ont été sauvegardées dans '{output_file_path}'.")

if __name__ == "__main__":
    main()
