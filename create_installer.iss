[Setup]
AppName=File Version Saver
AppVersion=1.0
DefaultDirName={autopf}\FileVersionSaver
DefaultGroupName=File Version Saver
OutputDir=dist
OutputBaseFilename=FileVersionSaver_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\version_saver.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "install_context_menu.reg"; DestDir: "{app}"; Flags: ignoreversion
Source: "uninstall_context_menu.reg"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\File Version Saver"; Filename: "{app}\version_saver.exe"
Name: "{group}\Uninstall File Version Saver"; Filename: "{uninstallexe}"

[Registry]
Root: HKCR; Subkey: "*\shell\SaveVersion"; ValueType: string; ValueName: ""; ValueData: "Save Version"; Flags: uninsdeletekey
Root: HKCR; Subkey: "*\shell\SaveVersion\command"; ValueType: string; ValueName: ""; ValueData: """{app}\version_saver.exe"" save ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "*\shell\ViewVersions"; ValueType: string; ValueName: ""; ValueData: "View Versions"; Flags: uninsdeletekey
Root: HKCR; Subkey: "*\shell\ViewVersions\command"; ValueType: string; ValueName: ""; ValueData: """{app}\version_saver.exe"" view ""%1"""; Flags: uninsdeletekey

[Run]
Filename: "{app}\version_saver.exe"; Description: "Launch File Version Saver"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ErrorCode: Integer;
  RegFile: String;
begin
  if CurStep = ssPostInstall then
  begin
    RegFile := ExpandConstant('{app}\\install_context_menu.reg');
    if FileExists(RegFile) then
    begin
      Exec(ExpandConstant('{sys}\\reg.exe'), 'import "' + RegFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
    end;
  end;
end; 