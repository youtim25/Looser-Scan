import os
import json

# Configuration
EXTENSIONS_IMAGES = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
DOSSIER_CHAPITRES = "." # Le dossier où sont vos dossiers de chapitres

def generer_donnees():
    chapters = []
    # On liste les dossiers qui commencent par "Chapitre"
    dossiers = [d for d in os.listdir(DOSSIER_CHAPITRES) if os.path.isdir(d) and "Chapitre" in d]
    # Tri alphabétique (pour avoir 71, 72, 73...)
    dossiers.sort()

    for index, dossier in enumerate(dossiers):
        chemin_complet = os.path.join(DOSSIER_CHAPITRES, dossier)
        # On récupère toutes les images du dossier
        images = [f for f in os.listdir(chemin_complet) if f.lower().endswith(EXTENSIONS_IMAGES)]
        images.sort() # Trie les images par nom (1.webp, 2.webp...)

        if images:
            chapters.append({
                "id": index + 1,
                "title": dossier,
                "folder": f"./{dossier}/",
                "thumbnail": images[0], # La première image sert de miniature
                "images": images,
                "date": "Ajouté récemment"
            })

    # Écriture dans le fichier JavaScript
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write("const chapters = " + json.dumps(chapters, indent=4, ensure_ascii=False) + ";")
    
    print(f"Succès ! {len(chapters)} chapitres détectés.")

if __name__ == "__main__":
    generer_donnees()