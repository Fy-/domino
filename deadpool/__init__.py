# -*- coding: utf-8 -*-
"""
	deadpool.ext
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from domino.data import DominoData as domi
from deadpool.nickserv import nickserv_privmsg
from deadpool.operserv import operserv_privmsg
from deadpool.chanserv import DeadpoolChan, chanserv_privmsg, chanserv_on_create, botserv_privmsg

from deadpool.db import Base, Session

def deadpool(server):
	session = Session()
	print ('[Domino] [Deadpool] Loading Deadpool - I will shoot your f*cking cat!')

	domi.services.append(
		{
			'nick': 'NickServ',
			'realname': 'NickServ - Nick Service',
			'virthost': 'nickserv%s' % (server.config['host_mask']),
			'oper': True
		}
	)
	domi.services.append(
		{
			'nick': 'ChanServ',
			'realname': 'ChanServ - Chan service',
			'virthost': 'nickserv%s' % (server.config['host_mask']),
			'oper': True
		}
	)
	domi.services.append(
		{
			'nick': 'Deadpool',
			'realname': 'Wade <Deadpool><Ryan Reynolds> Wilson',
			'virthost': 'bad.deadpool.good.deadpool%s' % (server.config['host_mask']),
			'oper': True
		}
	)
	domi.services.append(
		{
			'nick': 'Loki',
			'realname': 'Loki Laufeyson - God of Mischief',
			'virthost': 'tom.hiddleston%s' % (server.config['host_mask']),
			'oper': True
		}
	)

	domi.add_callback('on_privmsg', nickserv_privmsg, key='nickserv')
	domi.add_callback('on_privmsg', operserv_privmsg, key='loki')
	domi.add_callback('on_privmsg', chanserv_privmsg, key='chanserv')

	try:
		channels = session.query(DeadpoolChan).all()
	except:
		channels = []

	for chan in channels:
		domi.add_callback('on_create_chan', chanserv_on_create, key=chan.id)
		if chan.bot != None:
			domi.add_callback('on_privmsg_chan', botserv_privmsg, key=chan.id)

	return server