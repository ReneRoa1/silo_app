[Setup]
AppName=SiloApp
AppVersion=0.1
DefaultDirName={autopf}\SiloApp
DefaultGroupName=SiloApp
OutputDir=output
OutputBaseFilename=SiloApp_Installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "portuguesebrazil"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Opções adicionais:"

[Files]
Source: "..\dist\SiloApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SiloApp"; Filename: "{app}\SiloApp.exe"
Name: "{autodesktop}\SiloApp"; Filename: "{app}\SiloApp.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SiloApp.exe"; Description: "Executar SiloApp"; Flags: nowait postinstall skipifsilent