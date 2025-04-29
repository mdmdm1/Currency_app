[Setup]
AppName=Currency Manager
AppVersion=1.0
DefaultDirName={pf}\CurrencyManager
DefaultGroupName=Currency Manager
UninstallDisplayIcon={app}\app.exe
OutputBaseFilename=CurrencyManagerInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Currency Manager"; Filename: "{app}\scripts\launcher.bat"
Name: "{group}\Uninstall Currency Manager"; Filename: "{uninstallexe}"
