# -*- coding:utf-8 -*-
import random, os
import regex as re
from unidecode import unidecode


_punct_re = re.compile(r'[\t !":\!#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def create_chain(file_paths):
	markov_chain = {}
	word1 = "\n"
	word2 = "\n"
	for path in file_paths:
		with open(path) as file:
			for line in file:
				for current_word in line.split():
					if current_word != "":
						markov_chain.setdefault((word1, word2), []).append(current_word)
						word1 = word2
						word2 = current_word
	return markov_chain

def construct_sentence(markov_chain, word_count=5, slug=False):
	generated_sentence = ""
	word_tuple = random.choice(list(markov_chain.keys()))
	w1 = word_tuple[0]	
	w2 = word_tuple[1]
	
	for i in range(word_count):
		newword = random.choice(markov_chain[(w1, w2)])
		generated_sentence = generated_sentence + " " + newword
		w1 = w2
		w2 = newword
		
	if slug:
		return slugify(generated_sentence)

	return generated_sentence

def specials(s):
	s = s.replace(':', '')
	s = s.replace(';', '')
	s = s.replace('!', '')
	s = s.replace('?', '')

	return s

def slugify(text, delim=u'.'):
	result = []
	for word in _punct_re.split(text.lower()):
		result.extend(unidecode(word).split())
	return str(delim.join(result))