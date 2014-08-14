import pandas
import matplotlib.pyplot as plt
import numpy
from nltk.corpus import stopwords
import string
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
 
def top_words(series):
    ''' Takes as an argument a pandas Series of strings
 
    :param df: a pandas Series containing strings of words
    :type seach_key_words: pandas.Series
 
    
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

    single_word_per_sentence = [set(x) for x in split_words]
 
    # concatenate all words
    full_list2 = [item for sublist in single_word_per_sentence for item in sublist]
 
    full_list = []
    for x in split_words:
        full_list = full_list + x
    
    # Remove standard words using NLTK library
    std_word_set=set(stopwords.words('english'))
    full_list = [x if x not in std_word_set else None for x in full_list]                  
    full_list2 = [x if x not in std_word_set else None for x in full_list2]                  
    # remove non activity entries
    non_actitivity_words = ['']
    
    full_list = pandas.Series([x if x not in non_actitivity_words else None for x in full_list])                                                                           
    full_list2 = pandas.Series([x if x not in non_actitivity_words else None for x in full_list2])
    # find the list of unique words   
    unique_list = []
    for x in full_list:
        if x not in unique_list:
            unique_list.append(x)
 
    # count the occurence of each word, 1 per row of the dataset
    count_entries = []
    for y in unique_list :
        count = 0
        for x in split_words:
            if y in x:
                count = count + 1
 
        count_entries.append(count)
 
    test_count = full_list2.value_counts()
 
    # stores the unique entry results in a dataframe 
    unique_words_df = pandas.DataFrame({"Unique Words" : unique_list, "frequency" : count_entries})
 
    # drop null values 
    unique_words_df = unique_words_df[~unique_words_df['Unique Words'].isnull()]
 
    # sort dataframe
    unique_words_df = unique_words_df.sort('frequency',ascending=False)
 
    return unique_words_df, test_count
 
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
    
    # 5310 entries
    # remove "Test"
    #idx = (df.idea_descriptions == "Test") | (df.idea_descriptions == "test") | (df.titles == "Test") | (df.titles == "test")
    #df = df[~idx] # (41 dropped)
    
    # remove entries with no description
    #df = df[df.idea_descriptions != ""] # 4986 entries (304 dropped)
    
    ####################
    ### Top 5s plots ###
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

    top_title_words, test  = top_words(df.titles)
    #top_description_words = top_words(df.idea_descriptions)
    