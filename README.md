# Telegram Feedback Bot - Инструкция по деплою на Ubuntu

## Подготовка сервера

1. Обновите пакеты:
```bash
sudo apt update
sudo apt upgrade -y
```

2. Установите Python и pip:
```bash
sudo apt install python3 python3-pip -y
```

3. Установите git:
```bash
sudo apt install git -y
```

## Установка бота

1. Создайте папку для бота:
```bash
mkdir -p /home/ubuntu/cofebot
cd /home/ubuntu/cofebot
```

2. Скопируйте файлы бота в эту папку:
```bash
# Скопируйте все файлы из этой папки на сервер
# Можно использовать scp или просто создать файлы вручную
```

3. Установите зависимости:
```bash
pip3 install -r requirements.txt
```

4. Создайте и настройте файл .env:
```bash
nano .env
# Вставьте следующие строки, заменив значения на свои:
BOT_TOKEN=ваш_токен_бота
ADMIN_ID=ваш_id_админа
```

## Настройка автозапуска через systemd

1. Создайте файл службы:
```bash
sudo nano /etc/systemd/system/cofebot.service
```

2. Вставьте следующее содержимое:
```ini
[Unit]
Description=Telegram Feedback Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/cofebot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Включите и запустите службу:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cofebot
sudo systemctl start cofebot
```

## Проверка работы

1. Проверьте статус бота:
```bash
sudo systemctl status cofebot
```

2. Посмотреть логи:
```bash
sudo journalctl -u cofebot -f
```

## Управление ботом

- Остановить бота: `sudo systemctl stop cofebot`
- Запустить бота: `sudo systemctl start cofebot`
- Перезапустить бота: `sudo systemctl restart cofebot`

## Обновление бота

1. Остановите бота:
```bash
sudo systemctl stop cofebot
```

2. Обновите файлы
3. Запустите бота:
```bash
sudo systemctl start cofebot
```

## Безопасность

1. Настройте firewall:
```bash
sudo ufw allow ssh
sudo ufw enable
```

2. Регулярно обновляйте систему:
```bash
sudo apt update
sudo apt upgrade -y
```

## Бэкап

Регулярно делайте бэкап файлов бота:
```bash
# Создание архива с ботом
tar -czf cofebot_backup.tar.gz /home/ubuntu/cofebot
```

## Решение проблем

1. Если бот не запускается:
   - Проверьте логи: `sudo journalctl -u cofebot -f`
   - Проверьте права на файлы: `ls -la /home/ubuntu/cofebot`
   - Проверьте настройки в .env файле

2. Если бот падает:
   - Проверьте подключение к интернету
   - Проверьте токен бота
   - Проверьте свободное место на диске: `df -h`

## Контакты

По всем вопросам обращайтесь к администратору системы.
