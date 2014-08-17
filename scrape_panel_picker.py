#!/usr/bin/env python
# encoding: utf-8
"""
.. module:: scrape_panel_picker.py
    :synopsis: Pull down data from Panel Picker
.. moduleauthor:: Robert D. West <robert.david.west@gmail.com>
"""
import pdb
import urllib2
import bs4
import pandas


# initialise lists that will hold results of the search
ids = []
urls = []
titles = []
idea_descriptions = []
questions = [] 
speakers = []
companies = []
company_websites = []
event_types = []
categories = []
themes = []
levels = []
tags = [] 

good_pages = 0
id_df =pandas.read_csv('panel_ids.csv')
for id_ in id_df.id :
    print 'id= ' + str(id_) + ', good_pages=' + str(good_pages) 
    
    # construct search url from specified criteria    
    url = 'http://panelpicker.sxsw.com/vote/' + unicode(id_)
  
    # Open url and use beautiful soup to find search results   
    # 404 error then skip id
    try: 
        response = urllib2.urlopen(url) 
        
    except:
        #print "404 for id = " + unicode(id_)
        continue

    soup = bs4.BeautifulSoup(response)
    
    # If the entry in competition is no longer open then skip it
    flash_notice = soup.find('div', {'class':'flash notice'})              
    if  flash_notice != None :
        assert 'Voting period for this idea type has passed' in flash_notice.text, 'alternate reason for flash notice for id= ' + unicode(id_) + ', check source.'
 
    else :                             
        # title - if no h1 object, or title is empty string, skip id 
        article = soup.find('article')
        
        try:
            title = article.find('h1').text.encode('utf-8', 'replace')
        except: 
            continue
            
        if title == '':
            continue
        
        good_pages = good_pages + 1
            
        titles.append(title)
             
        # id and url
        ids.append(id_)
        urls.append(url)
         
        # idea description
        idea_description_id = soup.find('p', id='idea_description')
        all_siblings = idea_description_id.findNextSiblings()
        idea_description = '' 
        our_kid = all_siblings.pop(0)
        while our_kid.name == 'p' :   
            idea_description = idea_description + our_kid.text.encode('utf-8', 'replace')
            our_kid = all_siblings.pop(0)
        
        idea_descriptions.append(idea_description)
        
        # questions     
        question_soup = soup.find('ol', id='questions_answered').findAll('li')
        this_set_of_questions = []
        for q in question_soup:
            this_set_of_questions.append(q.text.encode('utf-8', 'replace'))
              
        questions.append(this_set_of_questions)    
        
        # Speaker, company and company website
        assert len(article.findAll('ul')) == 1 
        speaker_soup = article.find('ul').findAll('li')
        this_set_of_speakers = []
        this_set_of_companies = []
        this_set_of_company_websites = []
        for sp in speaker_soup:
            
            this_speaker = sp.renderContents().rsplit('\n')[1]
            this_company = sp.find('a').text
            this_company_website = sp.find('a')['href']
            
            this_set_of_speakers.append(this_speaker)
            this_set_of_companies.append(this_company)
            this_set_of_company_websites.append(this_company_website)
            
        speakers.append(this_set_of_speakers)    
        companies.append(this_set_of_companies)    
        company_websites.append(this_set_of_company_websites)    
               
        # tags     
        tag_soup = soup.findAll('p')
        tag_data = [x for x in tag_soup if 'Tags' in x.text]
        assert len(tag_data) == 1
        this_set_of_tags = [x.text for x in tag_data.pop().findAll('a')]
        tags.append(this_set_of_tags)
                                                                                                                 
        # Meta data
        meta_data = soup.find('dl', {'class' :'meta'})
        meta_data2 = meta_data.findAll('dd')
        meta_labels = meta_data.findAll('dt')   
        
        # events
        idx = ['Event' in x.text for x in meta_labels]
        event_type = pandas.Series(list(meta_data2))[idx].values[0].text
        event_types.append(event_type)
       
        # categories
        idx = ['Category' in x.text for x in meta_labels]
        category = pandas.Series(list(meta_data2))[idx].values[0].text
        categories.append(category)
    
        # themes
        idx = ['Theme' in x.text for x in meta_labels]
        theme = pandas.Series(list(meta_data2))[idx].values[0].text
        themes.append(theme)
        
        # levels
        idx = ['Level' in x.text for x in meta_labels]
        level = pandas.Series(list(meta_data2))[idx].values[0].text                                          
        levels.append(level)
                                    
# store results in pandas dataframe
d = {'titles' : titles, 'idea_descriptions' : idea_descriptions, 'questions' : questions, 'urls' : urls, 'speakers' : speakers, 'event_types' : event_types, 'categories' : categories, 'themes' : themes, 'levels' : levels,'tags' :tags, 'companies' : companies, 'company_websites' : company_websites}
df = pandas.DataFrame(d,index= ids)

print 'size =' + str(len(df))
#df.to_hdf('panel_picker_data.h5','df')
#df.to_csv('panel_picker_data.csv')
df.to_json('panel_picker_data.json')