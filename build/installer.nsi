; NSIS Installer Script for SheetsBot
; This creates a professional Windows installer for your application

!define APPNAME "SheetsBot"
!define COMPANYNAME "SheetsBot"
!define DESCRIPTION "Desktop application for Google Sheets automation"
!define VERSIONMAJOR "1"
!define VERSIONMINOR "0"
!define VERSIONBUILD "0"
!define HELPURL "https://github.com/baranozck/demoproject"
!define UPDATEURL "https://github.com/baranozck/demoproject/releases"
!define ABOUTURL "https://github.com/baranozck/demoproject"
!define INSTALLSIZE 150000  ; Estimate in KB

RequestExecutionLevel admin ; Required for installation in Program Files

; Include Modern UI
!include "MUI2.nsh"

; Define installer name and output
Name "${APPNAME}"
OutFile "SheetsBot-Setup.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"
InstallDirRegKey HKCU "Software\${APPNAME}" ""

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Default installation section
Section "${APPNAME} (required)" SecMain
    SectionIn RO
    
    ; Set output path to the installation directory
    SetOutPath $INSTDIR
    
    ; Copy all files from dist/SheetsBot/
    File /r "dist\SheetsBot\*.*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Store installation folder
    WriteRegStr HKCU "Software\${APPNAME}" "" $INSTDIR
    
    ; Create registry entries for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
SectionEnd

; Desktop shortcut section
Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\SheetsBot.exe" "" "$INSTDIR\SheetsBot.exe" 0
SectionEnd

; Start Menu shortcuts section
Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\SheetsBot.exe" "" "$INSTDIR\SheetsBot.exe" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
SectionEnd

; Component descriptions
LangString DESC_SecMain ${LANG_ENGLISH} "Main application files (required)"
LangString DESC_SecDesktop ${LANG_ENGLISH} "Create a desktop shortcut"
LangString DESC_SecStartMenu ${LANG_ENGLISH} "Create Start Menu shortcuts"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} $(DESC_SecStartMenu)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKCU "Software\${APPNAME}"
    
    ; Remove files and directories
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APPNAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APPNAME}"
SectionEnd 