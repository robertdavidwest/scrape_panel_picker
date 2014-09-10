#!/usr/bin/env python
# encoding: utf-8

import pandas
import matplotlib.pyplot as plt
import numpy
import string
import pdb
import re
from unidecode import unidecode
from sqlalchemy import MetaData, VARCHAR, TEXT, Integer, Table, Column, ForeignKey
import sqlalchemy

####################################################
##                NLP Functions  
####################################################

def avg_fb_shares_per_top_ngram(df_top_ngrams, ngram_map, df_from_scrape):
	
	avg_shares = []
	for i in xrange(len(df_top_ngrams)):
		idx = ngram_map.index[ngram_map.id == i]
		avg = numpy.average(df_from_scrape.facebook_shares[idx])
		avg_shares.append(avg)
	
	df_top_ngrams['avg_fb_shares'] = avg_shares
	import pdb
	pdb.set_trace()
	return df_top_ngrams, ngram_map


def ngrams(input, n):
  '''takes a string of words and returns a list of ngrams where n in the number of words in the ngram'''  
  input = input.split(' ')
  output = []
  for i in range(len(input)-n+1):
	output.append(' '.join(input[i:i+n]))
  return output

def is_number(s):
	'''Returns True is the string 's' contains a number, false otherwise.'''
	try:
		float(s)
		return True
	except ValueError:
		return False

def clean_list_of_string(list_of_strings) : 
	
	# Convert Unicode to closest ascii representation 
	clean_list = [unidecode(x) for x in list_of_strings]
	
	# make all entries lower case
	clean_list = [x.lower() for x in clean_list]
	
	# remove punctuation except for dash
	exclude = set(string.punctuation)
	without_punc = []
	for s in clean_list:
		without_punc.append(''.join(ch for ch in s if ch not in exclude))
	clean_list = without_punc
	
	# Make all white space into a single space
	clean_list = [re.sub( '\s+', ' ', x ).strip() for x in clean_list]
	
	# remove numbers
	without_numbers = []
	for s in clean_list:
		without_numbers.append(''.join(ch for ch in s if not is_number(ch)))
	clean_list = without_numbers
	
	return clean_list

def top_N_ngrams(series, std_word_set, additional_stop_words,n,N):
	''' Takes as an argument a pandas Series of strings

	:param df: a pandas Series containing strings of words
	:type seach_key_words: pandas.Series

	:param std_word_set: a list of std stopwords
	:type seach_key_words: list

	:param additional_stop_words: a list of additional stopwords
	:type seach_key_words: list

	'''
	# Remove duplicate listings
	#all_words = series.unique()

	# Convert Unicode to closest ascii representation 
	all_words = [unidecode(x) for x in series]

	# make all entries lower case
	all_words = [x.lower() for x in all_words]

	# Make all white space into a single space
	all_words = [re.sub( '\s+', ' ', x ).strip() for x in all_words]

	# remove ' - ', rather than '-'. (dash VS hyphen)
	all_words = [x.replace(' - ',' ') for x in all_words]
	all_words = [x.replace('- ',' ') for x in all_words]
	all_words = [x.replace(' -',' ') for x in all_words]

	# remove punctuation except for dash
	exclude = set(string.punctuation.replace('-',''))
	without_punc = []
	for s in all_words:
		without_punc.append(''.join(ch for ch in s if ch not in exclude))
	all_words = without_punc

	# Make all white space into a single space
	all_words = [re.sub( '\s+', ' ', x ).strip() for x in all_words]

	# remove stand alone numbers (keep number/letter combinations)
	without_numbers = []
	for s in all_words:
		words = s.split(' ')
		words_without_numbers = [x for x in words if is_number(x) == False]
		without_numbers.append(' '.join(words for words in words_without_numbers))

	# Make all white space into a single space
	all_words = [re.sub( '\s+', ' ', x ).strip() for x in without_numbers]
	# split the string on each row into single ngrams
	split_ngrams = [ngrams(x, n) for x in all_words]

	# only 1 unique ngram per entry
	single_ngram_per_sentence = [set(x) for x in split_ngrams]

	# concatenate all words into single list
	full_list = [item for sublist in single_ngram_per_sentence for item in sublist]

	# Remove standard words using NLTK library
	for std_word in std_word_set:
		full_list = [x if std_word not in x.split(' ') else '' for x in full_list]                                   

	# remove additional_stop_words
	for std_word in additional_stop_words:
		full_list = [x if std_word not in x.split(' ') else '' for x in full_list]                                   

	## remove ''
	full_list = [x if x != '' else None for x in full_list]                                   

	# stores the unique entry results in a series
	unique_words_series = pandas.Series(full_list).value_counts()
	
	# Top N
	top_N = unique_words_series[:N]
	
	# Put results in dataframe
	df_top_N_ngrams = pandas.DataFrame({'Frequency' : top_N})
	df_top_N_ngrams.reset_index(inplace=True)
	cols = pandas.Series(df_top_N_ngrams.columns)
	cols[cols == 'index'] = 'ngram'
	df_top_N_ngrams.columns = cols
	df_top_N_ngrams.index.name = 'id'
	
	# Map the top N grams back to the original series
	series_idx = []
	top_ngram_idx = []
	assert len(series) == len(single_ngram_per_sentence)
	for i in xrange(N) : 
		for j in xrange(len(series)):
			if df_top_N_ngrams.ngram[i] in single_ngram_per_sentence[j] :
				series_idx.append(j)
				top_ngram_idx.append(i)
	
	ngram_series_mapping = pandas.DataFrame({'id' : top_ngram_idx},index=series_idx)
	ngram_series_mapping.index.name = series.index.name

	return df_top_N_ngrams, ngram_series_mapping

####################################################
##             PLotting functions 
####################################################

def autolabel(rects_freq,rects_percent,ax):
	# attach some text labels
	for rect_freq, rect_percent in zip(rects_freq,rects_percent):
		height_freq = rect_freq.get_height()
		height_percent = rect_percent.get_height() 

		ax.text(rect_freq.get_x()+rect_freq.get_width()/2., 1.05*height_freq, '%.2f%%' % (height_percent*100),
				ha='center', va='bottom')

def plot_topN_bar(N,my_series,name):
	"""
	N: Top N
	my_series: pandas.Series

	"""
	N = min(N, len(my_series.value_counts())) # ensure topN is less than # categories

	value_count_percent = my_series.value_counts(normalize=True)
	value_count_freq = my_series.value_counts()
	topN_percent = value_count_percent[:N]
	topN_freq = value_count_freq[:N]

	#######################

	ind = numpy.arange(N)
	width = 0.40   # the width of the bars

	#######################
	# Bars - Top 5        #
	fig, ax = plt.subplots()

	p_freq = ax.bar(ind, topN_freq   , color='#D1B9D4')  
	p_percent = ax.bar(ind, topN_percent   , color='#D1B9D4')  

	ax.set_ylabel('Qty of Entries')
	ax.set_xticks(ind+width)
	ax.set_xticklabels(topN_freq.index)
	plt.title('Top ' + str(N) + ' ' + name)
	plt.setp(ax.get_xticklabels(), rotation=7.5, fontsize=10) 

	autolabel(p_freq, p_percent,ax)             
	plt.savefig('plots/top5_' + name + '.jpg')
	plt.show()    
	plt.close()