# Інструкції запуску proxy_finder для Docker

## 1. Запуск лише proxy_finder через Docker
Для Linux додайте `sudo`:  
```shell
docker run -it --rm --pull always ghcr.io/porthole-ascend-cinnamon/proxy_finder:latest --threads 5000
```

де 5000 можна замінити на будь-яке значення від 1 до 10000, але **ми рекомендуємо саме 2500, які стоять за замовчуванням**  
Зупинити скрипт можна натиснувши Ctrl+C (бажано пару разів), або якщо не спрацює - закрити вікно терміналу  

# Спосіб все-в-одному - mhddos_proxy та proxy_finder в одному скрипті через Docker
```shell
docker run -it --rm --pull always --name alexnestua ghcr.io/alexnest-ua/auto_mhddos_alexnest:latest 1 1500 1000 --debug
```
Більш детально про всі параметри тут: https://github.com/alexnest-ua/auto_mhddos_alexnest/tree/docker
