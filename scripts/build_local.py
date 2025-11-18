#!/usr/bin/env python3
"""
Script de build local pour BulletinPro
Teste le build avant de pusher sur GitHub
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def build_windows():
    """Build Windows avec PyInstaller"""
    print("🔨 Building Windows executable...")
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--name", "BulletinPro",
        "--windowed",
        "--onefile",
        "--icon", "assets/icons/app_icon.ico",
        "--add-data", "config.py;.",
        "--add-data", "assets/icons;assets/icons",
        "--hidden-import", "flet",
        "--hidden-import", "flet.core",
        "--hidden-import", "flet_core",
        "--hidden-import", "flet_runtime",
        "--hidden-import", "fpdf",
        "--hidden-import", "supabase",
        "--hidden-import", "PIL",
        "--hidden-import", "sqlite3",
        "--collect-all", "flet",
        "--collect-all", "flet_core",
        "--collect-all", "flet_runtime",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        exe_path = Path("dist/BulletinPro.exe")
        if exe_path.exists():
            size = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ Build Windows terminé : {size:.2f} MB")
            return True
        else:
            print("❌ Fichier .exe non trouvé")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur build : {e}")
        return False

def build_linux():
    """Build Linux avec PyInstaller + StaticX"""
    print("🔨 Building Linux executable...")
    
    # 1. PyInstaller
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--name", "bulletinpro",
        "--windowed",
        "--onefile",
        "--icon", "assets/icons/app_icon.png",
        "--add-data", "config.py:.",
        "--add-data", "assets/icons:assets/icons",
        "--hidden-import", "flet",
        "--hidden-import", "flet.core",
        "--hidden-import", "flet_core",
        "--hidden-import", "flet_runtime",
        "--hidden-import", "fpdf",
        "--hidden-import", "supabase",
        "--hidden-import", "PIL",
        "--hidden-import", "sqlite3",
        "--collect-all", "flet",
        "--collect-all", "flet_core",
        "--collect-all", "flet_runtime",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        # 2. StaticX (optionnel, nécessite installation: pip install staticx)
        exe_path = Path("dist/bulletinpro")
        
        if exe_path.exists():
            print("✅ PyInstaller terminé")
            
            # Essayer StaticX si disponible
            try:
                subprocess.run(
                    ["staticx", "dist/bulletinpro", "dist/bulletinpro-static"],
                    check=True
                )
                os.replace("dist/bulletinpro-static", "dist/bulletinpro")
                os.chmod("dist/bulletinpro", 0o755)
                print("✅ StaticX appliqué (binaire statique)")
            except FileNotFoundError:
                print("⚠️ StaticX non installé (binaire dynamique)")
                os.chmod("dist/bulletinpro", 0o755)
            
            size = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ Build Linux terminé : {size:.2f} MB")
            return True
        else:
            print("❌ Fichier binaire non trouvé")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur build : {e}")
        return False

def main():
    """Point d'entrée"""
    print("=" * 60)
    print("BUILD LOCAL - BulletinPro")
    print("=" * 60)
    
    # Détection OS
    system = platform.system()
    print(f"🖥️  Plateforme : {system}")
    print(f"🐍 Python : {sys.version}")
    
    # Vérifications préalables
    if not Path("main.py").exists():
        print("❌ main.py introuvable")
        return 1
    
    if not Path("assets/icons").exists():
        print("⚠️ Génération des icônes...")
        subprocess.run([sys.executable, "scripts/create_icons.py"])
    
    # Build selon l'OS
    if system == "Windows":
        success = build_windows()
    elif system == "Linux":
        success = build_linux()
    else:
        print(f"❌ OS non supporté : {system}")
        return 1
    
    if success:
        print("\n" + "=" * 60)
        print("✅ BUILD TERMINÉ AVEC SUCCÈS")
        print("=" * 60)
        print(f"\n📁 Fichier : dist/{('BulletinPro.exe' if system == 'Windows' else 'bulletinpro')}")
        return 0
    else:
        print("\n❌ BUILD ÉCHOUÉ")
        return 1

if __name__ == "__main__":
    sys.exit(main())
