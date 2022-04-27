import socket

from yarl import URL


JUDGES = [
    URL(judge).with_host(
        socket.gethostbyname(
            URL(judge).host
        )
    )
    for judge in [
        'http://www.proxy-listen.de/azenv.php',
        'http://www.wfuchs.de/azenv.php',
        'http://users.ugent.be/~bfdwever/start/env.cgi',
        'http://mojeip.net.pl/asdfa/azenv.php',
        'http://www.meow.org.uk/cgi-bin/env.pl',
        'http://httpheader.net',
        'tcp://1.1.1.1:53',
        'tcp://8.8.8.8:53',
        'http://google.ru/',
    ]
]
