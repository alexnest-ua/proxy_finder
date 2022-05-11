# Опис proxy_finder

Цей скрипт призначений для повністю автоматичного пошуку нових проксі для [mhddos_proxy](https://github.com/porthole-ascend-cinnamon/mhddos_proxy), 
від вас потрібно лише запустити його(бажано з під [ВПН](https://auto-ddos.notion.site/VPN-5e45e0aadccc449e83fea45d56385b54)), а пошук проксі та відправлення їх у нашу базу буде відбуватися повністю автоматично 24/7.  
  
Статистика пошуку оновлюється кожні 30 секунд - нормальна статистика це 1 знайдений проксі за 10 000 000.  
  
Так він знаходить менше, але 100% робочі проксі для mhddos_proxy, на відміну від unfx, який збирає купу шлаку, бо там виявився кривий алгоритм, насправді він кривий майже у всіх подібних програмах, бо вони ваажають за проксі будь-який IP:PORT, який віддає Status code: 200, але це може бути будь-що, а не проксі, і тому на нього запити йдуть, а на ціль - ні.  
  
Цей алгоритм proxy_finder зроблено так, що проксі перевіряється на конкретному судді, який має віддавати конкретну відповідь - тому це буде 100% проксі, а не шлак.  
  
Також алгоритм має асинхронну реалізацію, що значно пришвидшує пошук проксі (перевіряється ~50 000 проксі за 1 хвилину, але залежить від кількості потоків), та зменшує навантаження на процесор.  
  
Тому про unfx можете забути.

# Встановлення та запуск

[**Windows**](https://github.com/porthole-ascend-cinnamon/proxy_finder/blob/main/instructions/Windows.md)  
  
[**Linux**](https://github.com/porthole-ascend-cinnamon/proxy_finder/blob/main/instructions/Linux.md)  
  
[**Mac**](https://github.com/porthole-ascend-cinnamon/proxy_finder/blob/main/instructions/Mac.md)  
  
[**Android**](https://github.com/porthole-ascend-cinnamon/proxy_finder/blob/main/instructions/Android.md)  
  
[**Docker**](https://github.com/porthole-ascend-cinnamon/proxy_finder/blob/main/instructions/Docker.md)

Якщо виникли будь-які проблеми на будь-якому етапі пишіть в телеграм: @brainqdead
