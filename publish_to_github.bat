@echo off
chcp 65001 >nul
echo ===============================================
echo Публикация проекта на GitHub
echo ===============================================
echo.

REM Проверка наличия git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Git не установлен
    echo Установите Git с https://git-scm.com/downloads
    pause
    exit /b 1
)

echo Текущий статус:
git status --short
echo.

echo ===============================================
echo ИНСТРУКЦИЯ:
echo ===============================================
echo.
echo 1. Создайте новый репозиторий на GitHub:
echo    https://github.com/new
echo.
echo 2. Название репозитория (например): telegram-booking-bot
echo.
echo 3. НЕ добавляйте README, .gitignore или лицензию
echo    (они уже есть в проекте)
echo.
echo 4. После создания репозитория введите его название:
echo.
set /p REPO_NAME="Название репозитория: "

if "%REPO_NAME%"=="" (
    echo ОШИБКА: Название репозитория не может быть пустым
    pause
    exit /b 1
)

echo.
echo Добавление remote...
git remote add origin https://github.com/Igor1803/%REPO_NAME%.git 2>nul
if %errorlevel% neq 0 (
    echo Предупреждение: Remote уже существует, обновляю...
    git remote set-url origin https://github.com/Igor1803/%REPO_NAME%.git
)

echo.
echo Отправка кода на GitHub...
echo (Вам может потребоваться ввести логин и пароль)
echo.
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ===============================================
    echo ✅ Проект успешно опубликован!
    echo ===============================================
    echo.
    echo URL репозитория: https://github.com/Igor1803/%REPO_NAME%
) else (
    echo.
    echo ===============================================
    echo ❌ Ошибка при публикации
    echo ===============================================
    echo.
    echo Возможные причины:
    echo - Репозиторий еще не создан на GitHub
    echo - Неверное имя пользователя или репозитория
    echo - Проблемы с авторизацией
    echo.
    echo Попробуйте выполнить команды вручную:
    echo git remote add origin https://github.com/Igor1803/%REPO_NAME%.git
    echo git push -u origin main
)

echo.
pause

