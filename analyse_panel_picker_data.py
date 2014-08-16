import pandas
import matplotlib.pyplot as plt
import numpy
from nltk.corpus import stopwords
import string
import subprocess
import pdb
import time
import datetime
import re
from unidecode import unidecode

####################################################
##                NLP Functions  
####################################################

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
 
def top_ngrams(series, std_word_set, additional_stop_words,n):
    ''' Takes as an argument a pandas Series of strings
 
    :param df: a pandas Series containing strings of words
    :type seach_key_words: pandas.Series
    
    :param std_word_set: a list of std stopwords
    :type seach_key_words: list

    :param additional_stop_words: a list of additional stopwords
    :type seach_key_words: list
  
    
    '''
    # Remove duplicate listings
    all_words = series.unique()
   
    # Convert Unicode to closest ascii representation 
    all_words = [unidecode(x) for x in all_words]
    
    # make all entries lower case
    all_words = [x.lower() for x in all_words]
 
    # remove numbers
    without_numbers = []
    for s in all_words:
        without_numbers.append(''.join(ch for ch in s if not is_number(ch)))
    all_words = without_numbers
    
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
    
    return unique_words_series
 
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
    plt.savefig('top5_' + name + '.jpg')
    plt.show()    
    plt.close()
                     
if __name__ == "__main__" :     
    
    df = pandas.io.json.read_json('panel_picker_data_all.json')
   
    # get all_tags
    all_tags = pandas.Series([item for sublist in df.tags for item in sublist])    
    
    ####################
    ### Top Ns plots ###
    ####################
    makeCharts = False
    
    if makeCharts:
        N = 5
        
        plot_topN_bar(N,df.themes,'Themes') # Top 5 Themes
        plot_topN_bar(N,df.event_types,'Events') # Top 5 event types
        plot_topN_bar(N,df.categories,'Categories') # Top 5 categories
        plot_topN_bar(N,df.levels,'Levels') # Top 5 levels  
        all_tags = pandas.Series([item for sublist in df.tags for item in sublist])
        plot_topN_bar(N,all_tags,'Tags') # Top 5 tags  

    ####################
    ###     NLP      ###
    ####################
    std_word_set = numpy.sort(list(stopwords.words('english')))
    additional_stop_words =  numpy.sort(['also','get','way','use','well','new','session','panel','discuss','us','one','work','make','take','using','need','many','making','content','around','even','ways','years','best','better',])
       
    # tags
    top_tags = all_tags.value_counts() 
    
    # words
    top_title_words = top_ngrams(df.titles,std_word_set,additional_stop_words,1)
    top_description_words = top_ngrams(df.idea_descriptions,std_word_set,additional_stop_words,1)   

    # 2grams
    top_title_2grams = top_ngrams(df.titles,std_word_set,[],2)
    top_description_2grams = top_ngrams(df.idea_descriptions,std_word_set,[],2)

    # 3grams
    top_title_3grams = top_ngrams(df.titles,std_word_set,[],3)
    top_description_3grams = top_ngrams(df.idea_descriptions,std_word_set,[],3)

    ###########################################
    ### Create Top Ns tables and add to html###
    ###########################################
    
    # Create html file from markdown file
    ts = time.time()
    time_stamp = '_' + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H.%M')
    
    initial_filename = 'SXSE_panel_picker_analysis'
    output_filename = initial_filename + time_stamp
    args = ['pandoc', initial_filename+'.md' , '-o', output_filename+ '.html']
    subprocess.check_call(args)

    # create html tables and add to html file
    f = open(output_filename+'.html', "r")
    contents = f.readlines()
    f.close()
    
    # add css
    cssfile = open("markdown_style.css",'r')
    contents.insert(0,'<!DOCTYPE HTML><html><head><style>')  
    contents.insert(1,cssfile.read())
    contents.insert(2,'</head></style>')  
    contents.insert(3,'<body>')      
    cssfile.close()
  
    contents.append('<h2>Meta Data distributions</h2> \n')
    for my_series in [df.themes, df.event_types, df.categories, df.levels]:
        N = len(my_series.value_counts()) # ensure topN is less than # categories
        value_count_percent = my_series.value_counts(normalize=True)
        value_count_freq = my_series.value_counts()
        topN_percent = value_count_percent[:N]
        topN_percent = topN_percent.apply(lambda x: str(round(x*100,2)) + '%')
        topN_freq = value_count_freq[:N]
      
        html_table = (pandas.DataFrame({'Frequency' :topN_freq}).join(pandas.DataFrame({'Percent' :topN_percent}))).to_html()
        contents.append('<h3>Distribution of ' + my_series.name +': \n</h3>')
        contents.append(html_table)

    ############################################
    ### Print top N results from NLP to html ###
    ############################################
      
    N = 30
    
    df = pandas.DataFrame({'Frequency' : top_tags[:N]})    
    top_tags_html =df.to_html()
    top_tags_html = '<h3>Top 30 Proposal Tags:</h3> \n' + top_tags_html
    contents.append(top_tags_html)
    
    contents.append('<h2>NLP Results:</h2> \n')
    
    ### Top Words - titles
    df = pandas.DataFrame({'Frequency' : top_title_words[:N]})
    top_title_words_html = df.to_html()
    top_title_words_html = '<h3>Top 30 words in Proposal titles (limit 1 word per title):</h3> \n' + top_title_words_html 
    contents.append(top_title_words_html)       
  
    ### Top Words - descriptions
    df = pandas.DataFrame({'Frequency' : top_description_words[:N]})  
    top_description_words_html = df.to_html()
    top_description_words_html = '<h3>Top 30 words in Proposal descriptions (limit 1 word per description):</h3> \n' + top_description_words_html      
    contents.append(top_description_words_html)
    
    ### Stop Words
    contents.append('<h3>Stop words removed in NLP analysis</h3> \n')
    contents.append('<b>Standard Stopwords</b>: ' + ", ".join(std_word_set))
    contents.append('<h3></h3> ')    
    contents.append('<b>Additional Stopwords</b>: ' + ", ".join(additional_stop_words) + '\n')    

    ### Top 2grams - titles
    df = pandas.DataFrame({'Frequency' : top_title_2grams[:N]})
    top_title_2grams_html = df.to_html()
    top_title_2grams_html = '<h3>Top 30 2grams in Proposal titles (limit 1 2gram per title):</h3> \n' + top_title_2grams_html 
    contents.append(top_title_2grams_html)

    ### Top 2grams - descriptions
    df = pandas.DataFrame({'Frequency' : top_description_2grams[:N]})
    top_description_2grams_html = df.to_html()
    top_description_2grams_html = '<h3>Top 30 2grams in Proposal descriptions (limit 1 2gram per title):</h3> \n' + top_description_2grams_html 
    contents.append(top_description_2grams_html)

    ##############
    ### Close file
    contents.append('</body></html>')    
    f = open(output_filename + '.html', "w")
    
    
    ccc = []
    for line in contents:
        if u'\u2013' in line :
            line = line.replace(u'\u2013', "MASSIVE_DONKEY")
        ccc.append(line)
    
    ccc = "".join(ccc)        
    f.write(ccc)
    f.close()
    

