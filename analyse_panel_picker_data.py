import pandas
import numpy
from nltk.corpus import stopwords
from spp_analysis import plot_topN_bar, top_N_ngrams
import spp_analysis
import time
import datetime
import subprocess

def main(df_from_scrape , create_html_report):
    
    ### Tag and Company full lists        
    # get all_tags
    all_tags = pandas.Series([item for sublist in df_from_scrape.tag for item in sublist])    
    # get all companies
    all_companies = pandas.Series([item for sublist in df_from_scrape.company_name for item in sublist])    
    
    ####################
    ### Top Ns plots ###
    ####################
    makeCharts = False
    
    if makeCharts:
        N = 5
        
        plot_topN_bar(N,df_from_scrape.themes,'Themes') # Top 5 Themes
        plot_topN_bar(N,df_from_scrape.event_types,'Events') # Top 5 event types
        plot_topN_bar(N,df_from_scrape.categories,'Categories') # Top 5 categories
        plot_topN_bar(N,df_from_scrape.levels,'Levels') # Top 5 levels  
        plot_topN_bar(N,all_tags,'Tags') # Top 5 tags  

    ####################
    ###  NLP - Top N ###
    ####################
    
    std_word_set = numpy.sort(list(stopwords.words('english')))
    additional_stop_words =  numpy.sort(['also','get','way','use','well','new','session','panel','discuss','us','one','work','make','take','using','need','many','making','content','around','even','ways','years','best','better','good'])
    
    N = 30   
    # tags
    top_tags = all_tags.value_counts() 
    df_tags = pandas.DataFrame({'Frequency' : top_tags[:N]})    
    
    # words
    df_top_title_words, title_words_map = top_N_ngrams(df_from_scrape.title,std_word_set,additional_stop_words,1,N) # titles
    df_top_title_words, title_words_map = spp_analysis.avg_fb_shares_per_top_ngram(df_top_title_words, title_words_map,df_from_scrape)
    
    df_top_description_words, description_words_map = top_N_ngrams(df_from_scrape.idea_description,std_word_set,additional_stop_words,1,N) # description
    df_top_description_words, description_words_map = spp_analysis.avg_fb_shares_per_top_ngram(df_top_description_words, description_words_map,df_from_scrape)
    
    # 2grams
    df_top_title_2grams, title_2gram_map = top_N_ngrams(df_from_scrape.title,std_word_set,[],2,N)  # titles
    df_top_title_2grams, title_2gram_map = spp_analysis.avg_fb_shares_per_top_ngram(df_top_title_2grams, title_2gram_map,df_from_scrape)
    
    df_top_description_2grams, description_2gram_map = top_N_ngrams(df_from_scrape.idea_description,std_word_set,[],2,N) # description
    df_top_description_2grams, description_2gram_map = spp_analysis.avg_fb_shares_per_top_ngram(df_top_description_2grams, description_2gram_map,df_from_scrape)
  
    ### Top Companies
    N = 10
    value_count_percent = all_companies.value_counts(normalize=True)
    value_count_freq = all_companies.value_counts()
    topN_percent = value_count_percent[:N]
    topN_percent = topN_percent.apply(lambda x: str(round(x*100,2)) + '%')
    topN_freq = value_count_freq[:N]
    df_top_10_companies = pandas.DataFrame({'Frequency' :topN_freq}).join(pandas.DataFrame({'Percent' :topN_percent}))
    
    
    ###########################################
    ###          Store in hdf5              ###
    ###########################################
    
    nlp_results = pandas.HDFStore('nlp_results.h5')
 
    # words
    df_top_title_words.to_hdf('nlp_results.h5','df_top_title_words')
    title_words_map.to_hdf('nlp_results.h5','title_words_map') 
    df_top_description_words.to_hdf('nlp_results.h5','df_top_description_words')
    description_words_map.to_hdf('nlp_results.h5','description_words_map')
    # 2grams
    df_top_title_2grams.to_hdf('nlp_results.h5','df_top_title_2grams')
    title_2gram_map.to_hdf('nlp_results.h5','title_2gram_map')
    df_top_description_2grams.to_hdf('nlp_results.h5','df_top_description_2grams')
    description_2gram_map.to_hdf('nlp_results.h5','description_2gram_map') 
    
    ###########################################
    ###        Create html report           ###
    ###########################################
    if create_html_report :
        
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
        
        # Add css
        cssfile = open("markdown_style.css",'r')
        contents.insert(0,'<!DOCTYPE HTML><html><head><style>')  
        contents.insert(1,cssfile.read())
        contents.insert(2,'</head></style>')  
        contents.insert(3,'<body>')      
        cssfile.close()
      
        # distribution of Meta data
        contents.append('<h2>Meta Data distributions</h2> \n')
        for my_series in [df_from_scrape.theme, df_from_scrape.event, df_from_scrape.category, df_from_scrape.level]:
            N = len(my_series.value_counts()) # ensure topN is less than # categories
            value_count_percent = my_series.value_counts(normalize=True)
            value_count_freq = my_series.value_counts()
            topN_percent = value_count_percent[:N]
            topN_percent = topN_percent.apply(lambda x: str(round(x*100,2)) + '%')
            topN_freq = value_count_freq[:N]
    
            df_temp = pandas.DataFrame({'Frequency' :topN_freq}).join(pandas.DataFrame({'Percent' :topN_percent}))
            html_table = df_temp.to_html()
            contents.append('<h3>Distribution of ' + my_series.name +': \n</h3>')
            contents.append(html_table)     
    
        ################################################################
        ### Print top N results from NLP to html                     ###
        ################################################################
        
        ### Top Companies ######################### 
        html_table = df_top_10_companies.to_html()
        contents.append('<h3>Top 10 Companies:</h3>')
        contents.append(html_table)
          
        ###########################################
        ### Top Tags ##############################
        top_tags_html = df_tags.to_html()
        top_tags_html = '<h3>Top 30 Proposal Tags:</h3> \n' + top_tags_html
        contents.append(top_tags_html)
        
        contents.append('<h2>NLP Results:</h2> \n')
    
        ###########################################
        ### Top Words - titles
        df_top_title_words.reset_index(drop=True,inplace=True)
        top_title_words_html = df_top_title_words.to_html(index=False,index_names=False)
        top_title_words_html = '<h3>Top 30 words in Proposal titles (limit 1 word per title):</h3> \n' + top_title_words_html 
        contents.append(top_title_words_html)       
      
        ###########################################
        ### Top Words - descriptions   
        df_top_description_words.reset_index(drop=True,inplace=True)
        top_description_words_html = df_top_description_words.to_html(index=False,index_names=False)
        top_description_words_html = '<h3>Top 30 words in Proposal descriptions (limit 1 word per description):</h3> \n' + top_description_words_html      
        contents.append(top_description_words_html)
    
        ### Top 2grams - titles
        df_top_title_2grams.reset_index(drop=True,inplace=True)
        top_title_2grams_html = df_top_title_2grams.to_html(index=False,index_names=False)
        top_title_2grams_html = '<h3>Top 30 2grams in Proposal titles (limit 1 2gram per title):</h3> \n' + top_title_2grams_html 
        contents.append(top_title_2grams_html)
    
        ### Top 2grams - descriptions
        df_top_description_2grams.reset_index(drop=True,inplace=True)
        top_description_2grams_html = df_top_description_2grams.to_html(index=False,index_names=False)
        top_description_2grams_html = '<h3>Top 30 2grams in Proposal descriptions (limit 1 2gram per title):</h3> \n' + top_description_2grams_html 
        contents.append(top_description_2grams_html)
        
        ### Stop Words
        contents.append('<h3>Stop words removed in NLP analysis</h3> \n')
        contents.append('<b>Standard Stopwords</b>: ' + ", ".join(std_word_set))
        contents.append('<h3></h3> ')    
        contents.append('<b>Additional Stopwords</b>: ' + ", ".join(additional_stop_words) + '\n')    
         
        ##############
        ### Close file
        contents.append('</body></html>')    
        f = open(output_filename + '.html', "w") 
        contents = "".join(contents)        
        f.write(contents)
        f.close()
    
if __name__ == "__main__" :     
    
    ## 
    df = pandas.io.json.read_json('panel_picker_data_v3.json')
    ### Clean company data
    new_company_list = []
    for company_list in df.companies :
        company_list = spp_analysis.clean_list_of_string(company_list)
        new_company_list.append(company_list)
    df.companies = new_company_list
    
    ### Clean speaker data
    new_speaker_list = []
    for speaker_list in df.speakers :
        speaker_list = spp_analysis.clean_list_of_string(speaker_list)
        new_speaker_list.append(speaker_list)
    df.speakers = new_speaker_list

    ## reset index
    df.reset_index(inplace=True)
    df.drop('index',inplace=True,axis=1)
    df.index.name = 'panel_id'
    
    # Rename variables
    new_columns =  df.columns.to_series()
    new_columns[new_columns == 'categories'] = 'category'
    new_columns[new_columns == 'companies'] = 'company_name'
    new_columns[new_columns == 'company_websites'] = 'website'
    new_columns[new_columns == 'speakers'] = 'name'
    new_columns[new_columns == 'urls'] = 'panel_url'
    new_columns[new_columns == 'levels'] = 'level'
    new_columns[new_columns == 'idea_descriptions'] = 'idea_description'
    new_columns[new_columns == 'titles'] = 'title'
    new_columns[new_columns == 'themes'] = 'theme'
    new_columns[new_columns == 'tags'] = 'tag'
    new_columns[new_columns == 'event_types'] = 'event'
    df.columns = new_columns
    
    # Create html report and send data to hdf5 storage
    main(df,True)