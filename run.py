# -*- coding: utf-8 -*-
import os

from domino import Domino
from deadpool import Deadpool
from smileys import ServerSideSmiley

def main():
    #: Config sample
    config = {
        'host': '0.0.0.0',
        'port': 6667,
        'name': 'irc.2kay.net',
        'ipv6': True,
        'motd': os.path.join(os.path.dirname(__file__), 'motd.txt'),
        'hosts_txt': os.path.join(os.path.dirname(__file__), 'hosts.txt'),
        'opers': {
            'fy': 'pbkdf2:sha256:50000$Y7SgxwCz$109cbf31479bec70d151e40129d1f73e6abd91eadd159b227da9c2b49d18a44f',
        },
        'auto_join' : ['#domino'],
        'host_mask' : '.2kay.net',
        'back_list' : ['184.73.55.46']
    }


    srv = Domino(config) #: Prepare Server

    dp = Deadpool() #: services
    dp.init(srv)

    sm = ServerSideSmiley() #: Server side smiley (stupid concept ^_^)
    sm.init(srv)

    srv.init()
    srv.run() #: Run

if __name__ == '__main__':
    main()