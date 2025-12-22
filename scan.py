import os
import json
import re

# Configuration
EXTENSIONS_IMAGES = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
DOSSIER_CHAPITRES = "." # Le dossier où sont vos dossiers de chapitres

def extraire_numero_chapitre(nom_dossier):
    """Extrait le numéro du chapitre pour un tri correct"""
    match = re.search(r'(\d+)', nom_dossier.lower())
    return int(match.group(1)) if match else 0

def generer_donnees():
    chapters = []
    
    # Liste TOUS les dossiers (pas seulement ceux avec "chapitre")
    try:
        tous_les_elements = os.listdir(DOSSIER_CHAPITRES)
    except Exception as e:
        print(f"Erreur lors de la lecture du dossier : {e}")
        return
    
    # Filtre pour ne garder que les vrais dossiers
    dossiers = []
    for element in tous_les_elements:
        chemin_complet = os.path.join(DOSSIER_CHAPITRES, element)
        # Vérifier que c'est un dossier et qu'il contient "chapitre" (insensible à la casse)
        if os.path.isdir(chemin_complet) and "chapitre" in element.lower():
            dossiers.append(element)
    
    print(f"Dossiers détectés : {dossiers}")
    
    # Tri numérique basé sur le numéro dans le nom
    dossiers.sort(key=extraire_numero_chapitre)

    for index, dossier in enumerate(dossiers):
        chemin_complet = os.path.join(DOSSIER_CHAPITRES, dossier)
        
        try:
            # On récupère toutes les images du dossier
            fichiers = os.listdir(chemin_complet)
            images = [f for f in fichiers if f.lower().endswith(EXTENSIONS_IMAGES)]
            
            if not images:
                print(f"Attention : aucune image trouvée dans {dossier}")
                continue
            
            # Identifier la miniature (celle qui ne commence pas par un chiffre)
            thumbnail_candidates = [f for f in images if not f[0].isdigit()]
            if thumbnail_candidates:
                thumbnail = thumbnail_candidates[0]
            else:
                thumbnail = images[0] if images else None
            
            # Les autres images, triées numériquement
            other_images = [f for f in images if f != thumbnail]
            
            # Tri numérique amélioré
            def extraire_numero(nom_fichier):
                match = re.search(r'(\d+)', nom_fichier)
                return int(match.group(1)) if match else 0
            
            other_images.sort(key=extraire_numero)
            
            # Liste complète : miniature en premier, puis les autres triées
            images_list = [thumbnail] + other_images if thumbnail else other_images

            chapters.append({
                "id": index + 1,
                "title": dossier,
                "folder": f"./{dossier}/",
                "thumbnail": thumbnail,
                "images": images_list,
                "date": "Ajouté récemment"
            })
            
            print(f"✓ {dossier} : {len(images)} images")
            
        except Exception as e:
            print(f"Erreur avec le dossier {dossier} : {e}")
            continue

    # Écriture dans le fichier JavaScript
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write("const chapters = " + json.dumps(chapters, indent=4, ensure_ascii=False) + ";")
    
    print(f"\n✓ Succès ! {len(chapters)} chapitres détectés et exportés dans data.js")

if __name__ == "__main__":
    generer_donnees()
