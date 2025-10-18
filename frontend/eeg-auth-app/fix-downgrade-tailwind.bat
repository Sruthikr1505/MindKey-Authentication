@echo off
echo ==========================================
echo Downgrading to Tailwind CSS v3 (Stable)
echo ==========================================
echo.

REM Stop any running processes
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

REM Uninstall Tailwind v4
echo Uninstalling Tailwind v4...
call npm uninstall tailwindcss @tailwindcss/postcss @tailwindcss/node

REM Install Tailwind v3 (stable)
echo Installing Tailwind CSS v3...
call npm install -D tailwindcss@3.3.0 postcss@8.4.31 autoprefixer@10.4.16

echo.
echo Clearing caches...
if exist "node_modules\.vite" rmdir /s /q "node_modules\.vite"
if exist "dist" rmdir /s /q "dist"

echo.
echo Starting dev server...
call npm run dev
