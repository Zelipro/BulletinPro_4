#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génération des icônes pour BulletinPro
Compatible Windows/Linux/macOS
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
import sys

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

def create_app_icons():
    """Génère les icônes dans tous les formats nécessaires"""
    
    try:
        project_root = Path(__file__).parent.parent
        logo_path = project_root / "assets" / "icons" / "logo.png"
        icons_dir = project_root / "assets" / "icons"
        
        # Créer le dossier icons s'il n'existe pas
        icons_dir.mkdir(parents=True, exist_ok=True)
        
        # Vérifier si le logo existe
        if not logo_path.exists():
            print("[WARN] Logo manquant, creation d'un logo par defaut...")
            # Créer un logo par défaut bleu
            img = Image.new('RGB', (512, 512), color='#2196F3')
            draw = ImageDraw.Draw(img)
            
            # Dessiner "BP" au centre
            try:
                font = ImageFont.truetype("arial.ttf", 200)
            except:
                font = ImageFont.load_default()
            
            # Centrer le texte
            text = "BP"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (512 - text_width) // 2
            y = (512 - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font)
            img.save(logo_path)
            print("[INFO] Logo par defaut cree avec succes")
        else:
            img = Image.open(logo_path)
            print("[INFO] Logo charge depuis logo.png")
        
        print("[INFO] Generation des icones...")
        
        # 1. Icône Windows (.ico) - Multiples résolutions
        print("[INFO] Creation de l'icone Windows (.ico)...")
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(icons_dir / "app_icon.ico", format='ICO', sizes=icon_sizes)
        print("[OK] app_icon.ico cree")
        
        # 2. Icônes Linux (.png) - Plusieurs tailles
        print("[INFO] Creation des icones Linux (.png)...")
        linux_sizes = [16, 32, 48, 64, 128, 256, 512]
        for size in linux_sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(icons_dir / f"app_icon_{size}x{size}.png")
            print(f"[OK] app_icon_{size}x{size}.png cree")
        
        # 3. Icône principale (pour l'application)
        print("[INFO] Creation de l'icone principale...")
        img.resize((512, 512), Image.Resampling.LANCZOS).save(icons_dir / "app_icon.png")
        print("[OK] app_icon.png cree")
        
        print("\n[SUCCESS] Toutes les icones ont ete generees avec succes !")
        print(f"[INFO] Dossier: {icons_dir}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la generation des icones: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_app_icons()
    sys.exit(0 if success else 1)
