; Ping Monitor - Inno Setup
#define MyAppName "Ping Monitor"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Ping Monitor"
#define MyAppExeName "Ping Monitor.exe"

[Setup]
AppId={{A7B5E9E5-4C19-4F0E-9A6A-8E1C0F5E8C21}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Ping Monitor
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=PingMonitor_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=PingMonitor.ico
UninstallDisplayIcon={app}\Ping Monitor.exe
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Files]
Source: "dist\Ping Monitor.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Ping Monitor"; Filename: "{app}\Ping Monitor.exe"; IconFilename: "{app}\Ping Monitor.exe"
Name: "{autodesktop}\Ping Monitor"; Filename: "{app}\Ping Monitor.exe"; IconFilename: "{app}\Ping Monitor.exe"

[Run]
Filename: "{app}\Ping Monitor.exe"; Description: "Launch Ping Monitor"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
