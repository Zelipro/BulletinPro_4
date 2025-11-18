#!/usr/bin/env python3
"""
Script de build Windows pour BulletinPro
Prépare la structure pour l'installateur Inno Setup
"""

import os
import shutil
from pathlib import Path

def create_windows_structure():
    """Prépare les fichiers pour Inno Setup"""
    
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    installers_dir = dist_dir / "installers"
    
    print("🪟 Préparation de la structure Windows...")
    
    # Créer le dossier installers
    installers_dir.mkdir(parents=True, exist_ok=True)
    
    # Vérifier que l'exécutable existe
    exe_path = dist_dir / "BulletinPro.exe"
    if not exe_path.exists():
        print("❌ Erreur : BulletinPro.exe introuvable dans dist/")
        print("💡 Lancez d'abord PyInstaller pour créer l'exécutable")
        return False
    
    print(f"  ✅ Exécutable trouvé : {exe_path}")
    
    # Vérifier l'icône
    icon_path = project_root / "assets" / "icons" / "app_icon.ico"
    if not icon_path.exists():
        print("❌ Erreur : app_icon.ico introuvable")
        print("💡 Lancez d'abord create_icons.py")
        return False
    
    print(f"  ✅ Icône trouvée : {icon_path}")
    
    # Copier les fichiers nécessaires dans un dossier temporaire
    temp_dir = dist_dir / "BulletinPro_Package"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Copier l'exécutable
    shutil.copy2(exe_path, temp_dir / "BulletinPro.exe")
    print("  ✅ Exécutable copié")
    
    # Copier l'icône
    icon_dest = temp_dir / "app_icon.ico"
    shutil.copy2(icon_path, icon_dest)
    print("  ✅ Icône copiée")
    
    # Copier les fichiers de configuration (si présents)
    for file in ["config.py", ".env", "README.md", "LICENSE.txt"]:
        src = project_root / file
        if src.exists():
            shutil.copy2(src, temp_dir / file)
            print(f"  ✅ {file} copié")
    
    print("\n✅ Structure Windows prête pour Inno Setup !")
    print(f"📁 Dossier : {temp_dir}")
    
    return True

def generate_iss_file():
    """Génère dynamiquement le fichier .iss si nécessaire"""
    
    project_root = Path(__file__).parent.parent
    iss_path = project_root / "installer" / "windows.iss"
    
    # Si le fichier existe déjà, ne rien faire
    if iss_path.exists():
        print("ℹ️  Fichier windows.iss existant trouvé")
        return
    
    print("📝 Génération du fichier Inno Setup...")
    
    iss_content = """#define MyAppName "BulletinPro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Votre Établissement"
#define MyAppExeName "BulletinPro.exe"
#define MyAppURL "https://github.com/votre-username/BulletinPro"

[Setup]
; Identifiant unique de l'application (NE PAS MODIFIER après publication)
AppId={{8F9A3B2C-1D4E-5F6A-7B8C-9D0E1F2A3B4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
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
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";
Name: "quicklaunchicon"; Description: "Créer une icône dans la barre des tâches"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\BulletinPro_Package\\BulletinPro.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\\BulletinPro_Package\\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\\BulletinPro_Package\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Menu Démarrer
Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; IconFilename: "{app}\\app_icon.ico"
Name: "{group}\\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Bureau
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; IconFilename: "{app}\\app_icon.ico"; Tasks: desktopicon

; Barre des tâches (Windows 7+)
Name: "{userappdata}\\Microsoft\\Internet Explorer\\Quick Launch\\User Pinned\\TaskBar\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; IconFilename: "{app}\\app_icon.ico"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Ajouter au PATH (optionnel)
Root: HKLM; Subkey: "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath('{app}')

[Code]
// Vérifie si le dossier est déjà dans le PATH
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

// Message de bienvenue personnalisé
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption := 
    'Cet assistant vous guidera dans l''installation de BulletinPro.' + #13#10 + #13#10 +
    'BulletinPro est une application complète pour gérer les bulletins scolaires, ' +
    'les notes des élèves et les statistiques de votre établissement.' + #13#10 + #13#10 +
    'Cliquez sur Suivant pour continuer.';
end;

// Vérification de la version Windows
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  Result := True;
  GetWindowsVersionEx(Version);
  
  // Windows 10 minimum (build 10240)
  if (Version.Major < 10) then
  begin
    MsgBox('BulletinPro nécessite Windows 10 ou supérieur.' + #13#10 + 
           'Votre version de Windows n''est pas supportée.', 
           mbError, MB_OK);
    Result := False;
  end;
end;
"""
    
    # Créer le dossier installer
    iss_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Écrire le fichier
    with open(iss_path, 'w', encoding='utf-8') as f:
        f.write(iss_content)
    
    print(f"  ✅ Fichier créé : {iss_path}")

def create_license_file():
    """Crée un fichier LICENSE.txt par défaut si absent"""
    
    project_root = Path(__file__).parent.parent
    license_path = project_root / "LICENSE.txt"
    
    if license_path.exists():
        return
    
    print("📄 Création du fichier LICENSE.txt...")
    
    license_content = """LICENCE D'UTILISATION - BulletinPro

Copyright (c) 2024 Votre Nom / Établissement

Permission est accordée d'utiliser ce logiciel à des fins éducatives.

CE LOGICIEL EST FOURNI "TEL QUEL", SANS GARANTIE D'AUCUNE SORTE.

Pour toute question, contactez : votre@email.com
"""
    
    with open(license_path, 'w', encoding='utf-8') as f:
        f.write(license_content)
    
    print(f"  ✅ LICENSE.txt créé")

def main():
    """Fonction principale"""
    
    print("=" * 60)
    print("🪟 BUILD WINDOWS - BulletinPro")
    print("=" * 60 + "\n")
    
    # 1. Créer les fichiers nécessaires
    create_license_file()
    generate_iss_file()
    
    # 2. Préparer la structure
    if not create_windows_structure():
        print("\n❌ Build Windows échoué")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ PRÉPARATION WINDOWS TERMINÉE")
    print("=" * 60)
    print("\n📋 Prochaines étapes :")
    print("   1. L'exécutable est prêt dans : dist/BulletinPro_Package/")
    print("   2. Inno Setup compilera automatiquement l'installateur")
    print("   3. Résultat : dist/installers/BulletinPro_Setup_1.0.0.exe")
    
    return 0

if __name__ == "__main__":
    exit(main())
