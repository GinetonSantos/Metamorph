@echo off
REM Metamorph Trading Bot - Inicializador Windows
REM Este arquivo inicia o bot sem mostrar console

cd /d "%~dp0"

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Python não encontrado! Instale Python 3.8+ primeiro.
    echo Baixe em: https://python.org
    pause
    exit /b 1
)

REM Verificar se dependências estão instaladas
if not exist "requirements.txt" (
    echo Arquivo requirements.txt não encontrado!
    pause
    exit /b 1
)

REM Instalar dependências se necessário
pip show python-binance >nul 2>&1
if errorlevel 1 (
    echo Instalando dependências...
    pip install -r requirements.txt
)

REM Iniciar aplicação sem console
start "" pythonw start_gui_improved.pyw

REM Fechar este batch
exit