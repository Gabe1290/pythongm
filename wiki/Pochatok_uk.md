# Початок Роботи

> [English](Getting-Started) | [Français](Demarrage_fr) | [Deutsch](Erste_Schritte_de) | [Italiano](Iniziare_it) | [Español](Empezar_es) | [Português](Comecar_pt) | [Slovenščina](Zacetek_sl) | [Українська](Pochatok_uk) | [Русский](Nachalo_ru)

---

[Повернутися на головну сторінку](Home_uk)

Цей посібник допоможе вам запустити PyGameMaker на своїй системі.

---

## Системні Вимоги

- **Python** 3.10 або новіший
- **Операційна Система:** Windows, Linux або macOS
- **Місце на Диску:** ~500 МБ для встановлення
- **RAM:** щонайменше 4 ГБ, рекомендовано 8 ГБ

---

## Встановлення

### Крок 1: Встановіть Python

Завантажте Python 3.10+ з [python.org](https://www.python.org/downloads/) та встановіть його. При встановленні на Windows переконайтеся, що позначили "Add Python to PATH".

### Крок 2: Клонуйте Репозиторій

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
```

Або завантажте ZIP-файл зі [сторінки Releases](https://github.com/Gabe1290/pythongm/releases).

### Крок 3: Створіть Віртуальне Середовище

Створення віртуального середовища ізолює залежності PyGameMaker:

```bash
python -m venv venv
```

Активуйте віртуальне середовище:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Крок 4: Встановіть Залежності

```bash
pip install -r requirements.txt
```

### Крок 5: Запустіть PyGameMaker

```bash
python main.py
```

---

## Перший Запуск

При першому запуску PyGameMaker ви побачите:

1. **Рядок Меню** — меню File, Edit, Assets, Build, Tools та Help
2. **Дерево Ресурсів** — ліва панель з ресурсами проєкту (Спрайти, Звуки, Фони, Об'єкти, Кімнати)
3. **Робочу Область** — центральна область для редагування ресурсів
4. **Панель Властивостей** — права панель для властивостей ресурсів

---

## Створіть Свій Перший Проєкт

1. Перейдіть до **File > New Project**
2. Виберіть розташування та назву для свого проєкту
3. Буде створено нову папку проєкту зі стандартною структурою

---

## Структура Проєкту

Кожен проєкт PyGameMaker містить:

```
my_project/
├── project.json      # Налаштування проєкту
├── sprites/          # Зображення спрайтів
├── sounds/           # Аудіофайли
├── backgrounds/      # Зображення фонів
├── objects/          # Визначення ігрових об'єктів
├── rooms/            # Макети рівнів
├── fonts/            # Файли шрифтів
├── scripts/          # Власні скрипти
└── data/             # Власні файли даних
```

---

## Зміна Мови

PyGameMaker підтримує кілька мов:

1. Перейдіть до **Tools > Language**
2. Виберіть потрібну мову з меню
3. Перезапустіть PyGameMaker, щоб застосувати зміну

Доступні мови: англійська, французька, німецька, італійська, іспанська, португальська, словенська, українська, російська

---

## Наступні Кроки

- [[Persha_Gra_uk]] — Побудуйте просту гру крок за кроком
- [[Redaktor_Obiektiv_uk]] — Навчіться створювати ігрові об'єкти
- [[Redaktor_Kimnat_uk]] — Спроєктуйте свої ігрові рівні
- [[Podii_ta_Dii_uk]] — Зрозумійте ігрову логіку

---

## Усунення Неполадок

### Python не знайдено
Переконайтеся, що Python встановлено і додано до PATH. Щоб перевірити, спробуйте запустити `python --version`.

### Відсутні залежності
Якщо виникають помилки імпорту, спробуйте перевстановити залежності:
```bash
pip install -r requirements.txt --force-reinstall
```

### Проблеми з відображенням
На Linux Qt (GUI-фреймворк, на якому побудовано PyGameMaker) потребує
кількох системних бібліотек, які `pip` не встановлює:
```bash
sudo apt-get install -y libegl1 libxkbcommon0 libxcb-cursor0 \
    libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libasound2-dev libgl1-mesa-dev
```

---

## Допомога

- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) — Повідомте про помилки або запропонуйте функції
- [[FAQ_uk]] — Часті запитання та відповіді
