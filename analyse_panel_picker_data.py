import pandas
import matplotlib.pyplot as plt
import numpy
from nltk.corpus import stopwords
import string
import subprocess
import pdb


####################################################
##                NLP Functions  
####################################################

def is_number(s):
    '''Returns True is the string 's' contains a number, false otherwise.'''
    try:
        float(s)
        return True
    except ValueError:
        return False
 
def top_words(series, std_word_set, additional_stop_words):
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
 
    # make all entries lower case
    all_words = [x.lower() for x in all_words]
 
    # remove punctuation
    exclude = set(string.punctuation)
    without_punc = []
    for s in all_words:
        without_punc.append(''.join(ch for ch in s if ch not in exclude))
    all_words = without_punc
 
    # remove numbers
    without_numbers = []
    for s in all_words:
        without_numbers.append(''.join(ch for ch in s if not is_number(ch)))
    all_words = without_numbers
 
    # split the string on each row into single words
    split_words = [x.split() for x in all_words]

    # one word per entry
    single_word_per_sentence = [set(x) for x in split_words]
 
    # concatenate all words into single list
    full_list = [item for sublist in single_word_per_sentence for item in sublist]
 
    # Remove standard words using NLTK library
    full_list = [x if x not in std_word_set else None for x in full_list]                                   
    
    # remove additional_stop_words
    full_list = pandas.Series([x if x not in additional_stop_words else None for x in full_list])                                                                           

    # stores the unique entry results in a series
    unique_words_series = full_list.value_counts()
 
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
    std_word_set = set(stopwords.words('english'))
    additional_stop_words = ['also','get','way','use','well','way']
    
    top_title_words = top_words(df.titles,std_word_set,additional_stop_words)
    top_description_words = top_words(df.idea_descriptions,std_word_set,additional_stop_words)
    top_tags = all_tags.value_counts()    

    ###########################################
    ### Create Top Ns tables and add to html###
    ###########################################
    
    # Create html file from markdown file
    filename = 'SXSE_panel_picker_analysis'
    args = ['pandoc', filename+'.md' , '-o', filename+'.html']
    subprocess.check_call(args)


    # create html tables and add to html file
    f = open(filename+'.html', "r")
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
    
    df = pandas.DataFrame({'Frequency' : top_title_words[:N]})
    top_title_words_html = df.to_html()
    top_title_words_html = '<h3>Top 30 words in Proposal titles (limit 1 word per title):</h3> \n' + top_title_words_html 
    contents.append(top_title_words_html)       
  
    df = pandas.DataFrame({'Frequency' : top_description_words[:N]})  
    top_description_words_html = df.to_html()
    top_description_words_html = '<h3>Top 30 words in Proposal descriptions (limit 1 word per description):</h3> \n' + top_description_words_html      
    contents.append(top_description_words_html)


    contents.append('<h3>Stop words removed in NLP analysis</h3> \n')
    contents.append('<b>Standard Stopwords</b>: ' + ", ".join(std_word_set))
    contents.append('<h3></h3> ')    
    contents.append('<b>Additional Stopwords</b>: ' + ", ".join(additional_stop_words) + '\n')    

    contents.append('</body></html>')    
    f = open(filename+'.html', "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()
    

