@echo off
echo ==========================================
echo Fixing Tailwind CSS for Windows
echo ==========================================
echo.

REM Stop any running dev server
echo Step 1: Stopping any running processes...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

REM Remove duplicate config files
echo Step 2: Removing duplicate config files...
if exist "postcss.config.cjs" (
    del postcss.config.cjs
    echo Removed postcss.config.cjs
)
if exist "tailwind.config.cjs" (
    del tailwind.config.cjs
    echo Removed tailwind.config.cjs
)

REM Clear Vite cache
echo Step 3: Clearing Vite cache...
if exist "node_modules\.vite" (
    rmdir /s /q "node_modules\.vite"
    echo Cleared Vite cache
)

REM Clear dist folder
echo Step 4: Clearing dist folder...
if exist "dist" (
    rmdir /s /q "dist"
    echo Cleared dist folder
)

REM Reinstall dependencies
echo Step 5: Reinstalling dependencies...
echo This may take a few minutes...
call npm install

echo.
echo ==========================================
echo Fix Complete!
echo ==========================================
echo.
echo Starting dev server...
echo.
call npm run dev
