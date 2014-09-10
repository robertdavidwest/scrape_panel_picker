import pandas
import numpy 
import sqlalchemy
from unidecode import unidecode
from sqlalchemy import MetaData, VARCHAR, TEXT, Integer, Table, Column, ForeignKey
import spp_analysis

f = open('mysql_pword.txt','r')
pword = f.read()
f.close()
engine = sqlalchemy.create_engine("mysql+mysqldb://root:"+pword+"@localhost/sxsw_panel_picker")

## Drop sql tables if they already exist
meta = MetaData(bind=engine)

title_words_map = Table('title_words_map',meta)
description_words_map = Table('description_words_map',meta)
title_2gram_map = Table('title_2gram_map',meta)
description_2gram_map = Table('description_2gram_map',meta)

title_words = Table('title_words',meta)
description_words = Table('description_words',meta)
title_2grams = Table('title_2grams',meta)
description_2grams = Table('description_2grams',meta)

panel_employee = Table('panel_employee',meta)
employee_website = Table('employee_website',meta)
employee = Table('employee',meta)
company = Table('company',meta)
tags = Table('tags',meta)
questions = Table('questions',meta)
panel_description = Table('panel_description',meta)
panel = Table('panel',meta)

title_words_map.drop(engine,checkfirst=True)
description_words_map.drop(engine,checkfirst=True)
title_2gram_map.drop(engine,checkfirst=True)
description_2gram_map.drop(engine,checkfirst=True)

title_words.drop(engine,checkfirst=True)
description_words.drop(engine,checkfirst=True)
title_2grams.drop(engine,checkfirst=True)
description_2grams.drop(engine,checkfirst=True)

panel_employee.drop(engine,checkfirst=True)
title_words.drop(engine,checkfirst=True)
description_words.drop(engine,checkfirst=True)
employee_website.drop(engine,checkfirst=True)
employee.drop(engine,checkfirst=True)
company.drop(engine,checkfirst=True)
tags.drop(engine,checkfirst=True)
questions.drop(engine,checkfirst=True)
panel_description.drop(engine,checkfirst=True)
panel.drop(engine,checkfirst=True)

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
### SET META ENVIRONMENT FOR DATABASE

meta = MetaData(bind=engine)
import pdb
pdb.set_trace()
## PANEL ###
table_panel = Table('panel', meta,
	Column('panel_id', Integer, primary_key=True, autoincrement=False),
	Column('category', TEXT, nullable=True),
	Column('event', TEXT, nullable=True),
	Column('level', TEXT, nullable=True),
	Column('panel_url', TEXT, nullable=True),
	Column('title', TEXT, nullable=True),
	Column('theme', TEXT, nullable=True),
	Column('facebook_shares', Integer, nullable=True)
)

## PANEL_DESCRIPTION ###
table_panel_description = Table('panel_description', meta,
	Column('idea_description', TEXT, nullable=True),
	Column('panel_id', Integer, ForeignKey('panel.panel_id'))
)

## QUESTIONS TABLE
table_question = Table('questions', meta,
	Column('question', TEXT, nullable=True),
	Column('panel_id', Integer, ForeignKey('panel.panel_id'))
)

## TAGS TABLE
table_tags = Table('tags', meta,
	Column('tag', TEXT, nullable=True),
	Column('panel_id', Integer, ForeignKey('panel.panel_id'))
)

## COMPANY TABLE
table_company = Table('company', meta,
	Column('company_id', Integer, primary_key=True, autoincrement=False),
	Column('company_name', TEXT, nullable=True)
)

## EMPLOYEE TABLE
table_employee = Table('employee', meta,
	Column('employee_id', Integer, primary_key=True, autoincrement=False),
	Column('name', TEXT, nullable=True),
	Column('company_id', Integer, ForeignKey('company.company_id'))
)

## EMPLOYEE_WEBSITE TABLE
table_employee_websites = Table('employee_website', meta,
	Column('website', TEXT, nullable=True),
	Column('employee_id', Integer, ForeignKey('employee.employee_id'))
)

# panel_employee TABLE
table_panel_employee = Table('panel_employee', meta,
	Column('employee_id', Integer, ForeignKey('employee.employee_id')),
	Column('panel_id', Integer, ForeignKey('panel.panel_id'))
)

#######################
### ANALYSIS TABLES
#######################
# title_words TABLE
table_title_words = Table('title_words', meta,
	Column('id', Integer, primary_key=True, autoincrement=False),
	Column('ngram', TEXT, nullable=False),
	Column('Frequency', Integer, nullable=False),	
	Column('avg_fb_shares', Integer, nullable=False)	
)

# title_words_map TABLE
table_title_words_map = Table('title_words_map', meta,
	Column('id', Integer, ForeignKey('title_words.id')),
	Column('panel_id', Integer, ForeignKey('panel.panel_id'))
)

# table_description_words TABLE
table_description_words = Table('description_words', meta,
	Column('id', Integer, primary_key=True, autoincrement=False),
	Column('ngram', TEXT, nullable=False),
	Column('Frequency', Integer, nullable=False),
	Column('avg_fb_shares', Integer, nullable=False)
)

# table_description_words_map TABLE
table_description_words_map = Table('description_words_map', meta,
	Column('id', Integer, ForeignKey('description_words.id')),
	Column('panel_id', Integer, ForeignKey('panel.panel_id'))
)

# title_words TABLE
table_title_2grams = Table('title_2grams', meta,
	Column('id', Integer, primary_key=True, autoincrement=False),
	Column('ngram', TEXT, nullable=False),
	Column('Frequency', Integer, nullable=False),
	Column('avg_fb_shares', Integer, nullable=False)
)

# title_words_map TABLE
table_title_2gram_map = Table('title_2gram_map', meta,
	Column('id', Integer, ForeignKey('title_words.id')),
	Column('panel_id', Integer, ForeignKey('panel.panel_id'))
)

# table_description_words TABLE
table_description_2grams = Table('description_2grams', meta,
	Column('id', Integer, primary_key=True, autoincrement=False),
	Column('ngram', TEXT, nullable=False),
	Column('Frequency', Integer, nullable=False),
	Column('avg_fb_shares', Integer, nullable=False)
)

# table_description_words_map TABLE
table_description_2gram_map = Table('description_2gram_map', meta,
	Column('id', Integer, ForeignKey('description_words.id')),
	Column('panel_id', Integer, ForeignKey('panel.panel_id'))
)

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
### Create all tables 

meta.create_all(engine)

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
### Reformat data for mySQL relations tables

## Create dataframes that will be used as SQL tables: 
df = pandas.io.json.read_json('panel_picker_data_v3.json')
import pdb
pdb.set_trace()

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

#######################
### Panel Table
panel_df = df[['category','event','idea_description','level','panel_url', 'title','theme','facebook_shares']]
# need to remove 'idea_descriptions' for now due to size
panel_df = panel_df.drop('idea_description',axis=1)

#######################
### Panel Description Table
panel_description_df = df[['idea_description']] 

#######################
### Questions Table ###
all_questions = []
panel_id = []
for i in xrange(len(df.questions)) :
	for item in df.questions[i]:
		all_questions.append(item)
		panel_id.append(panel_df.index[i])

question_df = pandas.DataFrame({'panel_id' : panel_id, 'question' : all_questions})


#######################
### Tags Table      ###
all_tags = []
panel_id = []
for i in xrange(len(df.tag)) :
	for item in df.tag[i]:
		all_tags.append(item)
		panel_id.append(df.index[i])

tag_df = pandas.DataFrame({'panel_id' : panel_id, 'tag' : all_tags})


###########################
### Company Table       ###
all_company_names = pandas.Series([item for sublist in df.company_name for item in sublist])    
company_df = pandas.DataFrame({'company_name' : all_company_names})
company_df.drop_duplicates(inplace=True)
company_df.reset_index(inplace=True)
company_df.drop('index',inplace=True,axis=1)
company_df.index.name = 'company_id'


#######################
### employee Table  ###

all_names = []
all_company_names = []
all_websites = []
for i in xrange(len(df.name)) :
	for j in xrange(len(df.name[i])): 
		assert len(df.name[i]) == len(df.company_name[i]) 
		assert len(df.name[i]) == len(df.website[i]) 
		all_names.append(df.name[i][j])
		all_company_names.append(df.company_name[i][j])
		all_websites.append(df.website[i][j].lower())
		
		
employee_df = pandas.DataFrame({'name' : all_names, 'company_name' : all_company_names})
employee_df.set_index('company_name',inplace=True)
company_df_temp = company_df.copy()
company_df_temp.reset_index(inplace=True)
company_df_temp.set_index('company_name',inplace=True)
employee_df = employee_df.join(company_df_temp,how='left')
employee_df.drop_duplicates(inplace=True)
employee_df.reset_index(inplace=True)
employee_df.drop('company_name',inplace=True,axis=1)
employee_df.index.name = 'employee_id'


##########################
### employee Website  ###	

employee_df_temp = employee_df.copy()
employee_df_temp.reset_index(inplace=True)
employee_df_temp.set_index('name',inplace=True)
employee_df_temp.drop('company_id',inplace=True,axis=1)
employee_website_df = pandas.DataFrame({'name' : all_names, 'website' : all_websites})
employee_website_df.set_index('name',inplace=True)
employee_website_df = employee_website_df.join(employee_df_temp,how='left')
employee_website_df.drop_duplicates(inplace=True)
employee_website_df.reset_index(inplace=True)
employee_website_df.drop('name',inplace=True,axis=1)

##########################
### Panel Employee     ###
panel_ids = []
all_names = []
for i in xrange(len(df.name)) :
	for j in xrange(len(df.name[i])): 
		all_names.append(df.name[i][j])
		panel_ids.append(df.index[i])
		
panel_employee_df = pandas.DataFrame({'name' : all_names, 'panel_id' : panel_ids})
panel_employee_df.set_index('name',inplace=True)

employee_df_temp = employee_df.copy()
employee_df_temp.reset_index(inplace=True)
employee_df_temp.set_index('name',inplace=True)
employee_df_temp.drop('company_id',inplace=True,axis=1)

panel_employee_df = panel_employee_df.join(employee_df_temp,how='outer')
panel_employee_df.drop_duplicates(inplace=True)

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
### Send data to mySQL DATABASE
panel_df.to_sql('panel',engine,flavor='mysql', if_exists='append',index=True)
panel_description_df.to_sql('panel_description',engine,flavor='mysql', if_exists='append',index=True)
question_df.to_sql('questions',engine,flavor='mysql',if_exists='append',index=False)
tag_df.to_sql('tags',engine,flavor='mysql',if_exists='append',index=False)
company_df.to_sql('company',engine,flavor='mysql',if_exists='append',index=True)
employee_df.to_sql('employee',engine,flavor='mysql',if_exists='append',index=True)
employee_website_df.to_sql('employee_website',engine,flavor='mysql',if_exists='append',index=False)
panel_employee_df.to_sql('panel_employee',engine,flavor='mysql',if_exists='append',index=False)

### Run analysis and put into mysql database
nlp_results = pandas.HDFStore('nlp_results.h5')

### Top Words - titles #################### 
nlp_results.df_top_title_words.to_sql('title_words', engine,flavor='mysql',if_exists='append',index=True)
nlp_results.title_words_map.to_sql('title_words_map', engine,flavor='mysql',if_exists='append',index=True)

### Top Words - descriptions  
nlp_results.df_top_description_words.to_sql('description_words', engine,flavor='mysql',if_exists='append',index=True) 
nlp_results.description_words_map.to_sql('description_words_map', engine,flavor='mysql',if_exists='append',index=True)

### Top 2grams - titles #################### 
nlp_results.df_top_title_2grams.to_sql('title_2grams', engine,flavor='mysql',if_exists='append',index=True)
nlp_results.title_2gram_map.to_sql('title_2gram_map', engine,flavor='mysql',if_exists='append',index=True)

### Top 2grams - descriptions  
nlp_results.df_top_description_2grams.to_sql('description_2grams', engine,flavor='mysql',if_exists='append',index=True) 
nlp_results.description_2gram_map.to_sql('description_2gram_map', engine,flavor='mysql',if_exists='append',index=True)
