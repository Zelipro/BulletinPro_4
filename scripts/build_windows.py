#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de build Windows pour BulletinPro
Prépare la structure pour l'installateur Inno Setup
Compatible encodage Windows
"""

import os
import shutil
from pathlib import Path
import sys

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

def create_windows_structure():
    """Prépare les fichiers pour Inno Setup"""
    
    try:
        project_root = Path(__file__).parent.parent
        dist_dir = project_root / "dist"
        installers_dir = dist_dir / "installers"
        
        print("[INFO] Preparation de la structure Windows...")
        
        # Créer le dossier installers
        installers_dir.mkdir(parents=True, exist_ok=True)
        
        # Vérifier que l'exécutable existe
        exe_path = dist_dir / "BulletinPro.exe"
        if not exe_path.exists():
            print("[ERROR] BulletinPro.exe introuvable dans dist/")
            print("[INFO] Lancez d'abord PyInstaller pour creer l'executable")
            return False
        
        print(f"[OK] Executable trouve : {exe_path}")
        print(f"[INFO] Taille : {exe_path.stat().st_size / (1024*1024):.2f} MB")
        
        # Vérifier l'icône
        icon_path = project_root / "assets" / "icons" / "app_icon.ico"
        if not icon_path.exists():
            print("[ERROR] app_icon.ico introuvable")
            print("[INFO] Lancez d'abord create_icons.py")
            return False
        
        print(f"[OK] Icone trouvee : {icon_path}")
        
        # Copier les fichiers nécessaires dans un dossier temporaire
        temp_dir = dist_dir / "BulletinPro_Package"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        # Copier l'exécutable
        shutil.copy2(exe_path, temp_dir / "BulletinPro.exe")
        print("[OK] Executable copie")
        
        # Copier l'icône
        icon_dest = temp_dir / "app_icon.ico"
        shutil.copy2(icon_path, icon_dest)
        print("[OK] Icone copiee")
        
        # Copier les fichiers de configuration (si présents)
        files_to_copy = ["config.py", ".env", "README.md", "LICENSE.txt"]
        for file in files_to_copy:
            src = project_root / file
            if src.exists():
                shutil.copy2(src, temp_dir / file)
                print(f"[OK] {file} copie")
        
        print("\n[SUCCESS] Structure Windows prete pour Inno Setup !")
        print(f"[INFO] Dossier : {temp_dir}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_iss_file():
    """Génère dynamiquement le fichier .iss si nécessaire"""
    
    try:
        project_root = Path(__file__).parent.parent
        iss_path = project_root / "installer" / "windows.iss"
        
        # Si le fichier existe déjà, ne rien faire
        if iss_path.exists():
            print("[INFO] Fichier windows.iss existant trouve")
            return True
        
        print("[INFO] Generation du fichier Inno Setup...")
        
        iss_content = """#define MyAppName "BulletinPro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Votre Etablissement"
#define MyAppExeName "BulletinPro.exe"

[Setup]
AppId={{8F9A3B2C-1D4E-5F6A-7B8C-9D0E1F2A3B4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist\\installers
OutputBaseFilename=BulletinPro_Setup_{#MyAppVersion}
SetupIconFile=assets\\icons\\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\\{#MyAppExeName}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Creer un raccourci sur le bureau"; GroupDescription: "Raccourcis:";

[Files]
Source: "dist\\BulletinPro_Package\\BulletinPro.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\\BulletinPro_Package\\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\\BulletinPro_Package\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; IconFilename: "{app}\\app_icon.ico"
Name: "{group}\\Desinstaller {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; IconFilename: "{app}\\app_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "Lancer {#MyAppName}"; Flags: nowait postinstall skipifsilent
"""
        
        # Créer le dossier installer
        iss_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Écrire le fichier
        with open(iss_path, 'w', encoding='utf-8') as f:
            f.write(iss_content)
        
        print(f"[OK] Fichier cree : {iss_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur generation .iss : {e}")
        return False

def create_license_file():
    """Crée un fichier LICENSE.txt par défaut si absent"""
    
    try:
        project_root = Path(__file__).parent.parent
        license_path = project_root / "LICENSE.txt"
        
        if license_path.exists():
            return True
        
        print("[INFO] Creation du fichier LICENSE.txt...")
        
        license_content = """LICENCE D'UTILISATION - BulletinPro

Copyright (c) 2024 Votre Nom / Etablissement

Permission est accordee d'utiliser ce logiciel a des fins educatives.

CE LOGICIEL EST FOURNI "TEL QUEL", SANS GARANTIE D'AUCUNE SORTE.

Pour toute question, contactez : votre@email.com
"""
        
        with open(license_path, 'w', encoding='utf-8') as f:
            f.write(license_content)
        
        print("[OK] LICENSE.txt cree")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur creation LICENSE : {e}")
        return False

def main():
    """Fonction principale"""
    
    print("=" * 60)
    print("BUILD WINDOWS - BulletinPro")
    print("=" * 60)
    print("")
    
    # 1. Créer les fichiers nécessaires
    if not create_license_file():
        print("\n[ERROR] Echec creation LICENSE")
        return 1
    
    if not generate_iss_file():
        print("\n[ERROR] Echec generation .iss")
        return 1
    
    # 2. Préparer la structure
    if not create_windows_structure():
        print("\n[ERROR] Build Windows echoue")
        return 1
    
    print("\n" + "=" * 60)
    print("[SUCCESS] PREPARATION WINDOWS TERMINEE")
    print("=" * 60)
    print("\n[INFO] Prochaines etapes :")
    print("   1. L'executable est pret dans : dist/BulletinPro_Package/")
    print("   2. Inno Setup compilera automatiquement l'installateur")
    print("   3. Resultat : dist/installers/BulletinPro_Setup_1.0.0.exe")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
