# -*- coding: utf-8 -*-
"""
	domino.data
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import regex as re

class DominoData(object):
	re_nick = re.compile(r"^[][\`_^\|\-{|}A-Za-z][][\`_^\|\-{|}A-Za-z0-9]{0,50}$")
	re_chan = re.compile(r"^[&#+!][^\x00\x07\x0a\x0d ,:]{0,50}$")

	users = {}
	chans = {}
	hosts = {}
	masked_hosts = {}

	services = []

	callback = {
		'on_join_chan' : {},
		'on_create_chan' : {},
		'on_privmsg' : {},
		'on_privmsg_chan' : {},
		'server_ready' : []
	}

	@staticmethod
	def add_callback(action, cb, key=False):
		has_key = ['on_join_chan', 'on_create_chan', 'on_privmsg', 'on_privmsg_chan']

		if action.lower() in DominoData.callback:
			if isinstance(DominoData.callback[action.lower()], list):
				DominoData.callback[action.lower()].append(cb)
			elif isinstance(DominoData.callback[action.lower()], dict):
				if key:
					if key.lower() not in DominoData.callback[action.lower()]:
						DominoData.callback[action.lower()][key.lower()] = []

					DominoData.callback[action.lower()][key.lower()].append(cb)
