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
  
numPages = 40599
for id_ in xrange(0,numPages) :
    # construct search url from specified criteria    
    url = 'http://panelpicker.sxsw.com/vote/' + unicode(id_)

    # Open url and use beautiful soup to find search results   
    # 404 error then skip id
    try: 
        response = urllib2.urlopen(url)   
    except:
        print "404 for id = " + unicode(id_)
        break

    soup = bs4.BeautifulSoup(response)
    
    # If the entry in competition is no longer open then skip it
    flash_notice = soup.find('div', {'class':'flash notice'})              
    if  flash_notice != None :
        assert 'Voting period for this idea type has passed' in flash_notice.text, 'alternate reason for flash notice for id= ' + unicode(id_) + ', check source.'
 
    else :
    
        ids.append(id_)
        urls.append(urls)
                                
        # title 
        article = soup.find('article')
        title = article.find('h1').text.encode('utf-8', 'replace')
        titles.append(title)
        
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
        question = soup.find('ol', id='questions_answered').text.encode('utf-8', 'replace')
        questions.append(question)    
            
# store results in pandas dataframe
d = {'id' : ids, 'title' : titles, 'idea_descriptions' : idea_descriptions, 'questions' : questions, 'url' : url }
df = pandas.DataFrame(d)


print df.head()
print len(df)
#df.to_hdf('panel_picker_data.h5','df')
df.to_csv('panel_picker_data.csv')