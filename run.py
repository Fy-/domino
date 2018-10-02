# -*- coding: utf-8 -*-
import os

from domino import Domino
def main():
    config = {
        'port': 6667,
        'name': 'ircd.fy.to',
        'ipv6': True,
        'motd': os.path.join(os.path.dirname(__file__), 'motd.txt'),
        'hosts_txt': os.path.join(os.path.dirname(__file__), 'hosts.txt'),
        'opers': {
            'fy': 'pbkdf2:sha256:50000$Y7SgxwCz$109cbf31479bec70d151e40129d1f73e6abd91eadd159b227da9c2b49d18a44f',
        },
        'auto_join' : ['#domino'],
        'host_mask' : '.fy.to',
        'exts' : ['avengers']
    }
    srv = Domino(config)

    srv.run()

if __name__ == '__main__':
    main()