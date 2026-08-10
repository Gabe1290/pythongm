# Начало Работы

> [English](Getting-Started) | [Français](Demarrage_fr) | [Deutsch](Erste_Schritte_de) | [Italiano](Iniziare_it) | [Español](Empezar_es) | [Português](Comecar_pt) | [Slovenščina](Zacetek_sl) | [Українська](Pochatok_uk) | [Русский](Nachalo_ru)

---

[Вернуться на главную страницу](Home_ru)

Это руководство поможет вам запустить PyGameMaker на своей системе.

---

## Системные Требования

- **Python** 3.10 или новее
- **Операционная Система:** Windows, Linux или macOS
- **Место на Диске:** ~500 МБ для установки
- **RAM:** минимум 4 ГБ, рекомендуется 8 ГБ

---

## Установка

### Шаг 1: Установите Python

Скачайте Python 3.10+ с [python.org](https://www.python.org/downloads/) и установите его. При установке на Windows убедитесь, что отметили "Add Python to PATH".

### Шаг 2: Клонируйте Репозиторий

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
```

Или скачайте ZIP-файл со [страницы Releases](https://github.com/Gabe1290/pythongm/releases).

### Шаг 3: Создайте Виртуальное Окружение

Создание виртуального окружения изолирует зависимости PyGameMaker:

```bash
python -m venv venv
```

Активируйте виртуальное окружение:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Шаг 4: Установите Зависимости

```bash
pip install -r requirements.txt
```

### Шаг 5: Запустите PyGameMaker

```bash
python main.py
```

---

## Первый Запуск

При первом запуске PyGameMaker вы увидите:

1. **Строку Меню** — меню File, Edit, Assets, Build, Tools и Help
2. **Дерево Ресурсов** — левая панель с ресурсами проекта (Спрайты, Звуки, Фоны, Объекты, Комнаты)
3. **Рабочую Область** — центральная область для редактирования ресурсов
4. **Панель Свойств** — правая панель для свойств ресурсов

![Вкладка приветствия при первом запуске, без открытого проекта](images/ide-welcome.png)

---

## Создайте Свой Первый Проект

1. Перейдите к **File > New Project**
2. Выберите расположение и название для своего проекта
3. Будет создана новая папка проекта со стандартной структурой

---

## Структура Проекта

Каждый проект PyGameMaker содержит:

```
my_project/
├── project.json      # Настройки проекта
├── sprites/          # Изображения спрайтов
├── sounds/           # Аудиофайлы
├── backgrounds/      # Изображения фонов
├── objects/          # Определения игровых объектов
├── rooms/            # Макеты уровней
├── fonts/            # Файлы шрифтов
├── scripts/          # Собственные скрипты
└── data/             # Собственные файлы данных
```

---

## Смена Языка

PyGameMaker поддерживает несколько языков:

1. Перейдите к **Tools > Language**
2. Выберите нужный язык из меню
3. Перезапустите PyGameMaker, чтобы применить изменение

Доступные языки: английский, французский, немецкий, итальянский, испанский, португальский, словенский, украинский, русский

---

## Следующие Шаги

- [[Pervaya_Igra_ru]] — Постройте простую игру шаг за шагом
- [[Redaktor_Obektov_ru]] — Научитесь создавать игровые объекты
- [[Redaktor_Komnat_ru]] — Спроектируйте свои игровые уровни
- [[Sobytiya_i_Deystviya_ru]] — Разберитесь в игровой логике

---

## Устранение Неполадок

### Python не найден
Убедитесь, что Python установлен и добавлен в PATH. Чтобы проверить, попробуйте запустить `python --version`.

### Отсутствующие зависимости
Если возникают ошибки импорта, попробуйте переустановить зависимости:
```bash
pip install -r requirements.txt --force-reinstall
```

### Проблемы с отображением
На Linux Qt (GUI-фреймворк, на котором построен PyGameMaker) требует
несколько системных библиотек, которые `pip` не устанавливает:
```bash
sudo apt-get install -y libegl1 libxkbcommon0 libxcb-cursor0 \
    libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libasound2-dev libgl1-mesa-dev
```

---

## Помощь

- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) — Сообщите об ошибках или предложите функции
- [[FAQ_ru]] — Часто задаваемые вопросы и ответы
