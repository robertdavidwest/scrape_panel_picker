#!/usr/bin/env python
# encoding: utf-8
"""
.. module:: connect_to_craigslist.py
    :synopsis: search craiglist and filter results by description, price, and category. Then send html formatted results in an email to your friends, or to yourself.
.. moduleauthor:: Robert D. West <robert.david.west@gmail.com>
"""
import pdb
import urllib2
import bs4
import pandas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import __search_results_template__
  

# construct search url from specified criteria    
search_key_words = search_key_words.replace(' ','+')
url = 'http://' + city + '.craigslist.org/search/' + get_category(category) + '?query=' + search_key_words 
if pandas.isnull(min_value) is not None:
    url = url + '&minAsk=' + str(min_value)

if pandas.isnull(max_value) is not None:
    url = url + '&maxAsk=' + str(max_value)
    
url = url + '&sort=rel'

# Open url and use beautiful soup to find search results    
response = urllib2.urlopen(url)
soup = bs4.BeautifulSoup(response)
   
# initialise lists that will hold results of the search
results = []
urls = []
price = []
dates = []
location = []

# Check to see if multiple pages have been returned from the search
# if so, loop through each page and append the results

idea_description_id = soup.find('p', id='idea_description')
all_siblings = idea_description_id.findNextSiblings()
idea_description = '' 
our_kid = all_siblings.pop(0)
while our_kid.name == 'p'    
    idea_description = idea_description + our_kid.text
    
    

multi_page_info = multi_page_info.find('span', {'class':'button pagenum'})


# craigslist results are broken into blocks of 100, loop through each set of 100 and append the results
for i in range(num_loops):        
    
    if idx1 == -1:
        current_url = url
    else :
        idx2 = url.find("?")
        current_url = url[:idx2+1] + "s=" + str(i*100) +  url[:idx2+1]

    # Open url and use beautiful soup to find search results    
    response = urllib2.urlopen(current_url)
    soup = bs4.BeautifulSoup(response)

    # All data returned from the query is stored in <div class="content">
    search_content = soup.find_all('div', {'class':'content'})
    assert(len(search_content)==1) # There should only be one div class="content", if more than one returned, stop program
    search_content = search_content.pop()
      
    for row in search_content.find_all('p',{'class':'row'}):    
        # text and url data
        class_pl_info = row.find('span',{'class':'pl'}) 
        # there is an href stored in 'class_pl_info' with a single 'a' tag
        #    - the method 'getText' will return unicode containing the search entry title
        #    - the method 'attrs' will return a dict, and the key 'href' will then return the respective url
        results.append(class_pl_info.find('a').getText())
        urls.append(class_pl_info.find('a').attrs['href'])
        
        # price data
        class_price_info = row.find('span',{'class':'price'}) 
        # class_price_info contains the respective price if one is specified
        if class_price_info == None:
            price.append(None)   
        else :
            price.append(class_price_info.getText())        
        
        # date of craigslist post
        date_info = row.find('span',{'class','date'})
        dates.append(date_info.getText())
    
        # Location
        location_info = row.find('span',{'class':'pnr'})
        location_info = location_info.find('small')
        # class_price_info contains the respective price if one is specified
       
        if location_info == None:
            location.append(None)   
        else :
            location.append(location_info.getText()) 
       
# store results in pandas dataframe
d = {'Results' : results, 'urls' : urls, 'Price' : price, 'Date' : dates, 'Location' : location }
df = pandas.DataFrame(d)
    
# Remove rows that contain words from the string 'words_not_included'
words = words_not_included.split()
for word in words:
    idx = [x.find(word) ==-1 for x in df.Results] # idx shows which rows do not contain excluded words
    df = df[idx] # only keep rows that do not contain excluded words


  	
  	
  	
