import os
import json
import re

# Configuration
EXTENSIONS_IMAGES = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
DOSSIER_RACINE = "."  # Dossier racine contenant les dossiers de scans

def extraire_numero_chapitre(nom_dossier):
    """Extrait le numéro du chapitre pour un tri correct"""
    match = re.search(r'(\d+)', nom_dossier.lower())
    return int(match.group(1)) if match else 0

def extraire_numero(nom_fichier):
    """Extrait le numéro d'une image"""
    match = re.search(r'(\d+)', nom_fichier)
    return int(match.group(1)) if match else 0

def dedupliquer_images(images):
    """Élimine les doublons en gardant de préférence .webp, sinon .jpg"""
    images_uniques = {}
    
    for img in images:
        numero = extraire_numero(img)
        nom_base = img.rsplit('.', 1)[0].strip()
        
        if not img[0].isdigit():
            images_uniques[nom_base] = img
            continue
        
        if numero not in images_uniques:
            images_uniques[numero] = img
        else:
            img_existante = images_uniques[numero]
            if img.lower().endswith('.webp') and not img_existante.lower().endswith('.webp'):
                images_uniques[numero] = img
    
    return list(images_uniques.values())

def traiter_scan(dossier_scan):
    """Traite un dossier de scan et retourne la liste des chapitres"""
    chapters = []
    
    try:
        tous_les_elements = os.listdir(dossier_scan)
    except Exception as e:
        print(f"Erreur lors de la lecture du dossier {dossier_scan} : {e}")
        return chapters
    
    # Filtre pour ne garder que les dossiers de chapitres
    dossiers = []
    for element in tous_les_elements:
        chemin_complet = os.path.join(dossier_scan, element)
        if os.path.isdir(chemin_complet) and "chapitre" in element.lower():
            dossiers.append(element)
    
    print(f"\n  Dossiers détectés dans {os.path.basename(dossier_scan)} : {dossiers}")
    
    # Tri numérique
    dossiers.sort(key=extraire_numero_chapitre)

    for index, dossier in enumerate(dossiers):
        chemin_complet = os.path.join(dossier_scan, dossier)
        
        try:
            fichiers = os.listdir(chemin_complet)
            images = [f for f in fichiers if f.lower().endswith(EXTENSIONS_IMAGES)]
            
            if not images:
                print(f"  ⚠ Aucune image trouvée dans {dossier}")
                continue
            
            # Déduplication
            images = dedupliquer_images(images)
            
            # Identifier la miniature
            thumbnail_candidates = [f for f in images if not f[0].isdigit()]
            if thumbnail_candidates:
                thumbnail = thumbnail_candidates[0]
            else:
                thumbnail = images[0] if images else None
            
            # Les autres images, triées numériquement
            other_images = [f for f in images if f != thumbnail]
            other_images.sort(key=extraire_numero)
            
            images_list = [thumbnail] + other_images if thumbnail else other_images

            chapters.append({
                "id": index + 1,
                "title": dossier,
                "folder": f"./{os.path.basename(dossier_scan)}/{dossier}/",
                "thumbnail": thumbnail,
                "images": images_list,
                "date": "Ajouté récemment"
            })
            
            print(f"  ✓ {dossier} : {len(images_list)} images")
            
        except Exception as e:
            print(f"  ✗ Erreur avec {dossier} : {e}")
            continue

    return chapters

def generer_donnees():
    """Génère les données pour tous les scans"""
    data = {}
    
    # Parcourir tous les dossiers dans le répertoire racine
    try:
        tous_les_elements = os.listdir(DOSSIER_RACINE)
    except Exception as e:
        print(f"Erreur lors de la lecture du dossier racine : {e}")
        return
    
    # Identifier les dossiers de scans (ignorer fichiers et dossiers système)
    dossiers_scans = []
    for element in tous_les_elements:
        chemin_complet = os.path.join(DOSSIER_RACINE, element)
        if os.path.isdir(chemin_complet) and not element.startswith('.') and element not in ['__pycache__']:
            # Vérifier s'il contient des dossiers "Chapitre"
            try:
                sous_elements = os.listdir(chemin_complet)
                if any("chapitre" in se.lower() for se in sous_elements):
                    dossiers_scans.append(element)
            except:
                pass
    
    print(f"═══════════════════════════════════════")
    print(f"Dossiers de scans détectés : {dossiers_scans}")
    print(f"═══════════════════════════════════════")
    
    # Traiter chaque scan
    for dossier_scan in dossiers_scans:
        chemin_scan = os.path.join(DOSSIER_RACINE, dossier_scan)
        print(f"\n📚 Traitement de : {dossier_scan}")
        chapters = traiter_scan(chemin_scan)
        
        if chapters:
            # Normaliser le nom pour l'utiliser comme clé
            cle_scan = dossier_scan.lower().replace(' ', '_').replace('-', '_')
            data[cle_scan] = {
                "name": dossier_scan,
                "chapters": chapters
            }
            print(f"  ✓ {len(chapters)} chapitres ajoutés")
    
    # Écriture dans le fichier JavaScript
    if data:
        with open('data.js', 'w', encoding='utf-8') as f:
            f.write("const scansData = " + json.dumps(data, indent=4, ensure_ascii=False) + ";")
        
        print(f"\n═══════════════════════════════════════")
        print(f"✓ Succès ! {len(data)} scans exportés dans data.js")
        print(f"═══════════════════════════════════════")
    else:
        print("\n⚠ Aucun scan détecté. Vérifiez votre structure de dossiers.")

if __name__ == "__main__":
    generer_donnees()