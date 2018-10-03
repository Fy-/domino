# -*- coding: utf-8 -*-
"""
	domino.handle.helpers
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import asyncio

#: >> :ircd.fy.to 001 un_geek :Welcome to ircd.fy.to un_geek
def send_numeric(code, args, txt, user):
	args = [str(x) for x in args]

	response = ':%s %s %s %s' % (user.server.name, str(code).rjust(3, '0'), ' '.join(args), txt)
	response = response.replace('  ', ' ')
	user.send(response)

def split_string_512(str):
	i = 0
	tmp = str.split(' ')
	result = []
	result.append('')

	for word in tmp:
		if (len(result[i] + word) > 512):
			result[i] = result[i].strip()
			i += 1
			result.append('')

		result[i] += word + ' '

	return result