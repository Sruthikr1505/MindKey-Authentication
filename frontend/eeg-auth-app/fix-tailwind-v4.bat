@echo off
echo ==========================================
echo Installing Tailwind CSS v4 PostCSS Plugin
echo ==========================================
echo.

REM Stop any running processes
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

REM Install the new PostCSS plugin
echo Installing @tailwindcss/postcss...
call npm install -D @tailwindcss/postcss

echo.
echo Starting dev server...
call npm run dev
