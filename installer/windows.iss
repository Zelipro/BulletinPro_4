#define MyAppName "BulletinPro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Ecole"
#define MyAppExeName "BulletinPro.exe"

[Setup]
AppId={{8F9A3B2C-1D4E-5F6A-7B8C-9D0E1F2A3B4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=dist\installers
OutputBaseFilename=BulletinPro_Setup_{#MyAppVersion}
SetupIconFile=dist\BulletinPro_Package\app_icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Creer raccourci bureau"

[Files]
Source: "dist\BulletinPro_Package\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Flags: nowait postinstall skipifsilent
