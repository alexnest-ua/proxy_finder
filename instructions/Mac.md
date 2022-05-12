# Інструкції встановлення proxy_finder на Mac


❗️Треба встановити супер-швидкий та стабільний VPN, щоб ваш провайдер не різав трафік через підключення до багатьох ІР(проксі):
https://auto-ddos.notion.site/VPN-5e45e0aadccc449e83fea45d56385b54

Якщо ви будете без ВПН, то у вас взагалі може попасти інтернет на роутері, як було у мене, бо провайдери не полюбляють коли з їх ІР йде трафік на велику кількість інших ІР(проксі)

Інші ВПН теж можуть не підійти, бо вони можуть відключатися 

1. [**Запуск за допомогою авто-оновлюваного bash-скрипта, який сам завантажить усі необхідні файли, та самостійно буде завантажувати оновлення**](https://github.com/porthole-ascend-cinnamon/proxy_finder/edit/main/instructions/Mac.md#1-%D0%B7%D0%B0%D0%BF%D1%83%D1%81%D0%BA-%D0%B7%D0%B0-%D0%B4%D0%BE%D0%BF%D0%BE%D0%BC%D0%BE%D0%B3%D0%BE%D1%8E-%D0%B0%D0%B2%D1%82%D0%BE-%D0%BE%D0%BD%D0%BE%D0%B2%D0%BB%D1%8E%D0%B2%D0%B0%D0%BD%D0%BE%D0%B3%D0%BE-bash-%D1%81%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%B0-%D1%8F%D0%BA%D0%B8%D0%B9-%D1%81%D0%B0%D0%BC-%D0%B7%D0%B0%D0%B2%D0%B0%D0%BD%D1%82%D0%B0%D0%B6%D0%B8%D1%82%D1%8C-%D1%83%D1%81%D1%96-%D0%BD%D0%B5%D0%BE%D0%B1%D1%85%D1%96%D0%B4%D0%BD%D1%96-%D1%84%D0%B0%D0%B9%D0%BB%D0%B8-%D1%82%D0%B0-%D1%81%D0%B0%D0%BC%D0%BE%D1%81%D1%82%D1%96%D0%B9%D0%BD%D0%BE-%D0%B1%D1%83%D0%B4%D0%B5-%D0%B7%D0%B0%D0%B2%D0%B0%D0%BD%D1%82%D0%B0%D0%B6%D1%83%D0%B2%D0%B0%D1%82%D0%B8-%D0%BE%D0%BD%D0%BE%D0%B2%D0%BB%D0%B5%D0%BD%D0%BD%D1%8F)  
2. [**Спосіб все-в-одному - авто-оновлювані mhddos_proxy та proxy_finder в одному скрипті**](https://github.com/porthole-ascend-cinnamon/proxy_finder/blob/main/instructions/Mac.md#2-%D1%81%D0%BF%D0%BE%D1%81%D1%96%D0%B1-%D0%B2%D1%81%D0%B5-%D0%B2-%D0%BE%D0%B4%D0%BD%D0%BE%D0%BC%D1%83---%D0%B0%D0%B2%D1%82%D0%BE-%D0%BE%D0%BD%D0%BE%D0%B2%D0%BB%D1%8E%D0%B2%D0%B0%D0%BD%D1%96-mhddos_proxy-%D1%82%D0%B0-proxy_finder-%D0%B2-%D0%BE%D0%B4%D0%BD%D0%BE%D0%BC%D1%83-%D1%81%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D1%96)    

Якщо виникли будь-які проблеми на будь-якому етапі пишіть в телеграм: @brainqdead

# 1. Запуск за допомогою авто-оновлюваного bash-скрипта, який сам завантажить усі необхідні файли, та самостійно буде завантажувати оновлення
1) Заходимо в Launchpad, щоб відкрити термінал:  
![image](https://user-images.githubusercontent.com/74729549/167870744-564a23ad-966d-430c-8fe1-5557b22df9ff.png)  
2) Шукаємо terminal
![image](https://user-images.githubusercontent.com/74729549/167871196-714ccf87-42a0-458a-acb9-fb1cddf0d0da.png)
3) Запускаємо Термінал
![image](https://user-images.githubusercontent.com/74729549/167871258-0a24e1fd-0c87-42c3-ace1-2d32d8120b75.png)
4) Запускаємо скрипт, який сам встановить необхідні програми: Brew, Python, Git, доп. засоби Баш'у (можливо попросить ввести пароль для установки, 10 Гб вільного  місця на диску та натиснути ENTER, щоб продовжити завантаження - тому слідкуйте уважно за виконанням скрипта при першому запуску), та запустить proxy_finder:  
```shell
curl -LO https://raw.githubusercontent.com/porthole-ascend-cinnamon/proxy_finder/main/auto_runner_mac.sh && bash auto_runner_mac.sh 2500
```
де 2500 можна замінити на будь-яке значення від 1 до 10000, але **ми рекомендуємо саме 2500, які стоять за замовчуванням**  
Зупинити скрипт можна натиснувши Ctrl+C (бажано пару разів), або якщо не спрацює - закрити вікно терміналу  


### 2. Спосіб все-в-одному - авто-оновлювані mhddos_proxy та proxy_finder в одному скрипті
1) Відкрити Термінал, як у пункту вище  
2) Та запустити скрипт, який сам встановить необхідні програми: Brew, Python, Git, доп. засоби Баш'у (можливо попросить ввести пароль для установки, 10 Гб вільного  місця на диску та натиснути ENTER, щоб продовжити завантаження - тому слідкуйте уважно за виконанням скрипта при першому запуску) та запустить mhddos_proxy та proxy_finder:    
```shell
curl -LO https://raw.githubusercontent.com/alexnest-ua/auto_mhddos_mac/main/runner.sh && bash runner.sh 2000 2000 -d
```
Більш детально про всі параметри можна почитати тут: https://github.com/alexnest-ua/auto_mhddos_mac - цей скрипт дозволяє запустити одночасно mhddos_proxy та  proxy_finder, який ще й автоматично оновлює не лише себе, а й mhddos_proxy та proxy_finder, та бере актуальні цілі звідси: https://t.me/ddos_separ  
Тому можете запускати його та йти займатися своїми справами, а скрипт зробить все за вас
