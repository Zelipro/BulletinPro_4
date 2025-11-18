; Script Inno Setup pour BulletinPro
; Compatible GitHub Actions

#define MyAppName "BulletinPro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "AZeli"
#define MyAppExeName "BulletinPro.exe"

[Setup]
; Identifiant unique (ne pas changer apres publication)
AppId={{8F9A3B2C-1D4E-5F6A-7B8C-9D0E1F2A3B4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Pas de fichier licence pour l'instant
; LicenseFile=LICENSE.txt
OutputDir=dist\installers
OutputBaseFilename=BulletinPro_Setup_{#MyAppVersion}
; Icone depuis le package temporaire
SetupIconFile=dist\BulletinPro_Package\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Creer un raccourci sur le bureau"; GroupDescription: "Raccourcis:"

[Files]
; Tous les fichiers du package temporaire
Source: "dist\BulletinPro_Package\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Menu Demarrer
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"
Name: "{group}\Desinstaller {#MyAppName}"; Filename: "{uninstallexe}"

; Bureau
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer {#MyAppName}"; Flags: nowait postinstall skipifsilent
