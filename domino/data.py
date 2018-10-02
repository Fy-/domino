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