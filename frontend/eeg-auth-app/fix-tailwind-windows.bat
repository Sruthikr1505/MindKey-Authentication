@echo off
echo ==========================================
echo Final Tailwind CSS Fix for Windows
echo ==========================================
echo.

REM Stop any running processes
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

REM Clear all caches
echo Clearing caches...
if exist "node_modules\.vite" rmdir /s /q "node_modules\.vite"
if exist "dist" rmdir /s /q "dist"
if exist ".cache" rmdir /s /q ".cache"

REM Reinstall Tailwind and PostCSS
echo Reinstalling Tailwind CSS...
call npm uninstall tailwindcss postcss autoprefixer
call npm install -D tailwindcss@latest postcss@latest autoprefixer@latest

REM Start dev server
echo.
echo Starting dev server...
call npm run dev
