# -*- coding: utf-8 -*-
import os

from domino import Domino
def main():
    config = {
        'host': '0.0.0.0',
        'port': 6667,
        'name': 'ircd.fy.to',
        'ipv6': True,
        'motd': os.path.join(os.path.dirname(__file__), 'motd.txt'),
        'opers': {
            'fy': 'stay',
        },
        'auto_join' : ['#domino'],
        'hostmask' : '.fy.to',
        'exts' : ['avengers']
    }
    srv = Domino(config)

    srv.run()

if __name__ == '__main__':
    main()