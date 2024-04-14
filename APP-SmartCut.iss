; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "APP-SmartCut"
#define MyAppVersion "0.8"
#define MyAppPublisher "kMarflow-Software"
#define MyAppURL "https://dev.kMarflow.com"


[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{35939202-6F77-40BD-9B2E-B068BFB704A4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName=C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\SmartCut
DisableDirPage=yes
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputBaseFilename=APP-SmartCut-Setup
Compression=lzma2 
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "D:\OneDrive\Documents\MarflowSoftware\SmartCut\extensionFiles\SmartCut\*"; Excludes: "\Output\, \.vscode\, \.git\ *.md, *.iss, .gitignore, *.backup"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
;Source: "D:\OneDrive\Documents\MarflowSoftware\SmartCut\ProgramDataFiles\SmartCut\*"; DestDir: "C:\ProgramData\Adobe\CEP\extensions\SmartCut\"; Flags: ignoreversion recursesubdirs createallsubdirs

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

