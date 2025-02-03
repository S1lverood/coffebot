# Инструкция по развертыванию бота BIBITI на Ubuntu

## 1. Подготовка системы

```bash
# Обновление системы
sudo apt update
sudo apt upgrade -y

# Установка Python и необходимых инструментов
sudo apt install python3 python3-pip python3-venv git -y
```

## 2. Настройка проекта

```bash
# Создание директории для бота
mkdir -p ~/bibiti_bot
cd ~/bibiti_bot

# Копирование файлов проекта
# Скопируйте все файлы из этой папки в директорию ~/bibiti_bot

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

## 3. Настройка автозапуска через systemd

```bash
# Создание файла службы systemd
sudo nano /etc/systemd/system/bibiti_bot.service
```

Вставьте следующее содержимое:
```ini
[Unit]
Description=BIBITI Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/bibiti_bot
Environment=PATH=/home/YOUR_USERNAME/bibiti_bot/venv/bin
ExecStart=/home/YOUR_USERNAME/bibiti_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Замените YOUR_USERNAME на имя вашего пользователя в Ubuntu.

## 4. Запуск бота

```bash
# Перезагрузка демона systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable bibiti_bot

# Запуск бота
sudo systemctl start bibiti_bot

# Проверка статуса
sudo systemctl status bibiti_bot
```

## 5. Управление ботом

```bash
# Остановка бота
sudo systemctl stop bibiti_bot

# Перезапуск бота
sudo systemctl restart bibiti_bot

# Просмотр логов
sudo journalctl -u bibiti_bot -f
```

## 6. Обновление бота

Для обновления бота:
1. Остановите службу: `sudo systemctl stop bibiti_bot`
2. Замените необходимые файлы в директории ~/bibiti_bot
3. Запустите службу: `sudo systemctl start bibiti_bot`

## Важные замечания

1. Убедитесь, что файл .env содержит правильный токен бота и ID администратора
2. Проверьте права доступа к файлам меню (menu1.jpg, menu2.jpg, menu3.jpg)
3. Для просмотра ошибок используйте команду: `sudo journalctl -u bibiti_bot -f`
4. Рекомендуется делать резервные копии перед обновлением

## Требования к системе

- Ubuntu 20.04 или новее
- Python 3.8 или новее
- Минимум 512MB RAM
- Минимум 1GB свободного места на диске
