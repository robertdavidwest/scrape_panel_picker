import pandas
df = pandas.io.json.read_json('panel_picker_data_all.json')


# 5310 entries

# remove "Test"

idx = (df.idea_descriptions == "Test") | (df.idea_descriptions == "test") | (df.titles == "Test") | (df.titles == "test")
df = df[~idx] # (41 dropped)

# remove entries with no description
df = df[df.idea_descriptions != ""] # 4986 entries (304 dropped)



bad_descriptions = ['a','TBD','eterdgrf',
a= df[df.idea_descriptions.isin(bad_descriptions)]