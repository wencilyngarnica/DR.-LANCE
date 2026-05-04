@echo off
echo Stopping any existing Ollama processes...
taskkill /F /IM ollama.exe 2>nul
taskkill /F /IM ollama-app.exe 2>nul

echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo Starting Ollama with CORS enabled...
set OLLAMA_ORIGINS=*
ollama serve

pause