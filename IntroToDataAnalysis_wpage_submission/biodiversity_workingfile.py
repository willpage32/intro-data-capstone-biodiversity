#!/usr/bin/env python
# coding: utf-8

# # Capstone 2: Biodiversity Project

# # Introduction
# You are a biodiversity analyst working for the National Parks Service.  You're going to help them analyze some data about species at various national parks.
# 
# Note: The data that you'll be working with for this project is *inspired* by real data, but is mostly fictional.

# # Step 1
# Import the modules that you'll be using in this assignment:
# - `from matplotlib import pyplot as plt`
# - `import pandas as pd`

# In[116]:


from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency


# # Step 2
# You have been given two CSV files. `species_info.csv` with data about different species in our National Parks, including:
# - The scientific name of each species
# - The common names of each species
# - The species conservation status
# 
# Load the dataset and inspect it:
# - Load `species_info.csv` into a DataFrame called `species`

# In[117]:


species = pd.read_csv('species_info.csv')


# Inspect each DataFrame using `.head()`.

# In[118]:


species.head(15)


# In[119]:


species.dtypes


# # Step 3
# Let's start by learning a bit more about our data.  Answer each of the following questions.

# How many different species are in the `species` DataFrame?

# In[120]:


uniq_species = np.unique(species.category)
num_species = np.size(uniq_species)
print num_species


# What are the different values of `category` in `species`?

# In[121]:


print uniq_species


# What are the different values of `conservation_status`?

# In[122]:


uniq_conservation_stat = np.unique(species.conservation_status)
print type( uniq_conservation_stat[6] )


# # Step 4
# Let's start doing some analysis!
# 
# The column `conservation_status` has several possible values:
# - `Species of Concern`: declining or appear to be in need of conservation
# - `Threatened`: vulnerable to endangerment in the near future
# - `Endangered`: seriously at risk of extinction
# - `In Recovery`: formerly `Endangered`, but currnetly neither in danger of extinction throughout all or a significant portion of its range
# 
# We'd like to count up how many species meet each of these criteria.  Use `groupby` to count how many `scientific_name` meet each of these criteria.

# In[123]:


grouped_species = species.groupby('conservation_status').scientific_name.nunique().reset_index()
grouped_species.head(10)


# As we saw before, there are far more than 200 species in the `species` table.  Clearly, only a small number of them are categorized as needing some sort of protection.  The rest have `conservation_status` equal to `None`.  Because `groupby` does not include `None`, we will need to fill in the null values.  We can do this using `.fillna`.  We pass in however we want to fill in our `None` values as an argument.
# 
# Paste the following code and run it to see replace `None` with `No Intervention`:
# ```python
# species.fillna('No Intervention', inplace=True)
# ```

# In[124]:


species.fillna('No Intervention', inplace=True)


# Great! Now run the same `groupby` as before to see how many species require `No Intervention`.

# In[125]:


group2_species = species.groupby('conservation_status').scientific_name.nunique().reset_index()
group2_species_sorted = group2_species.sort_values(by='scientific_name')
group2_species_sorted.head(10)


# Let's use `plt.bar` to create a bar chart.  First, let's sort the columns by how many species are in each categories.  We can do this using `.sort_values`.  We use the the keyword `by` to indicate which column we want to sort by.
# 
# Paste the following code and run it to create a new DataFrame called `protection_counts`, which is sorted by `scientific_name`:
# ```python
# protection_counts = species.groupby('conservation_status')\
#     .scientific_name.count().reset_index()\
#     .sort_values(by='scientific_name')
# ```

# In[126]:


protection_counts = species.groupby('conservation_status')    .scientific_name.count().reset_index()    .sort_values(by='scientific_name')


# Now let's create a bar chart!
# 1. Start by creating a wide figure with `figsize=(10, 4)`
# 1. Start by creating an axes object called `ax` using `plt.subplot`.
# 2. Create a bar chart whose heights are equal to `scientific_name` column of `protection_counts`.
# 3. Create an x-tick for each of the bars.
# 4. Label each x-tick with the label from `conservation_status` in `protection_counts`
# 5. Label the y-axis `Number of Species`
# 6. Title the graph `Conservation Status by Species`
# 7. Plot the grap using `plt.show()`

# In[127]:


plt.figure(figsize = (10,4))
ax = plt.subplot
plt.bar(group2_species_sorted.conservation_status,group2_species_sorted.scientific_name)
plt.title('Conservation Status by Species')
plt.ylabel('Number of Species')
plt.xlabel('Species')
plt.show()


# # Step 4
# Are certain types of species more likely to be endangered?

# Let's create a new column in `species` called `is_protected`, which is `True` if `conservation_status` is not equal to `No Intervention`, and `False` otherwise.

# In[128]:


species['is_protected'] = species.conservation_status!='No Intervention'
species.head(10)


# Let's group by *both* `category` and `is_protected`.  Save your results to `category_counts`.

# In[129]:


category_counts = species.groupby(['category','is_protected']).scientific_name.nunique().reset_index()


# Examine `category_counts` using `head()`.

# In[130]:


category_counts.head(10)


# It's going to be easier to view this data if we pivot it.  Using `pivot`, rearange `category_counts` so that:
# - `columns` is `is_protected`
# - `index` is `category`
# - `values` is `scientific_name`
# 
# Save your pivoted data to `category_pivot`. Remember to `reset_index()` at the end.

# In[131]:


category_pivot = category_counts.pivot_table('scientific_name',index='category',columns = 'is_protected').reset_index()


# Examine `category_pivot`.

# In[132]:


print category_pivot


# Use the `.columns` property to  rename the categories `True` and `False` to something more description:
# - Leave `category` as `category`
# - Rename `False` to `not_protected`
# - Rename `True` to `protected`

# In[133]:


category_pivot.columns=['category','not_protected','protected']


# Let's create a new column of `category_pivot` called `percent_protected`, which is equal to `protected` (the number of species that are protected) divided by `protected` plus `not_protected` (the total number of species).

# In[134]:


category_pivot['percent_protected'] = category_pivot.protected/(category_pivot.protected+category_pivot.not_protected)


# Examine `category_pivot`.

# In[156]:


# Rank order all protection percentages
# Calculate each chi_square contingency

cat_pivot_sigf = category_pivot.sort_values(by='percent_protected').reset_index(drop=True)
print cat_pivot_sigf
for i in range(0,6):
    tmp_contingency = cat_pivot_sigf.iloc[[i,i+1],[2,1]]
    print chi2_contingency(tmp_contingency)[1]


# It looks like species in category `Mammal` are more likely to be endangered than species in `Bird`.  We're going to do a significance test to see if this statement is true.  Before you do the significance test, consider the following questions:
# - Is the data numerical or categorical?
# - How many pieces of data are you comparing?

# Based on those answers, you should choose to do a *chi squared test*.  In order to run a chi squared test, we'll need to create a contingency table.  Our contingency table should look like this:
# 
# ||protected|not protected|
# |-|-|-|
# |Mammal|?|?|
# |Bird|?|?|
# 
# Create a table called `contingency` and fill it in with the correct numbers

# In[158]:


# Calculate all the permutations of chi square significance

print chi2_contingency( [[46,4216],[5,73]]   )[1]
print chi2_contingency( [[46,4216],[11,115]] )[1]
print chi2_contingency( [[46,4216],[7,72]]   )[1]
print chi2_contingency( [[46,4216],[75,413]] )[1]
print chi2_contingency( [[46,4216],[30,146]] )[1]
print '\n'
print chi2_contingency( [[5,328],[11,115]] )[1]
print chi2_contingency( [[5,328],[7,72]] )[1]
print chi2_contingency( [[5,328],[75,413]] )[1]
print chi2_contingency( [[5,328],[30,146]] )[1]
print '\n'
print chi2_contingency( [[5,73],[7,72]] )[1]
print chi2_contingency( [[5,73],[75,413]] )[1]
print chi2_contingency( [[5,73],[30,146]] )[1]
print '\n'
print chi2_contingency( [[11,115],[75,413]] )[1]
print chi2_contingency( [[11,115],[30,146]] )[1]
print '\n'
print chi2_contingency( [[7,72],[30,146]] )[1]


# In[137]:


bird_vs_mam_cont = category_pivot.iloc[[3,1],[2,1]]
print bird_vs_mam_cont


# In order to perform our chi square test, we'll need to import the correct function from scipy.  Past the following code and run it:
# ```py
# from scipy.stats import chi2_contingency
# ```

# Now run `chi2_contingency` with `contingency`.

# In[138]:


bird_vs_mam_chi2 = chi2_contingency(bird_vs_mam_cont)
print bird_vs_mam_chi2[1]


# It looks like this difference isn't significant!
# 
# Let's test another.  Is the difference between `Reptile` and `Mammal` significant?

# In[139]:


rep_vs_mam_cont = category_pivot.iloc[[5,3],[2,1]]
rep_vs_mam_chi2 = chi2_contingency(rep_vs_mam_cont)
print rep_vs_mam_chi2[1]


# Yes! It looks like there is a significant difference between `Reptile` and `Mammal`!

# # Step 5

# Conservationists have been recording sightings of different species at several national parks for the past 7 days.  They've saved sent you their observations in a file called `observations.csv`.  Load `observations.csv` into a variable called `observations`, then use `head` to view the data.

# In[140]:


observations = pd.read_csv('observations.csv')
observations.head(10)


# Some scientists are studying the number of sheep sightings at different national parks.  There are several different scientific names for different types of sheep.  We'd like to know which rows of `species` are referring to sheep.  Notice that the following code will tell us whether or not a word occurs in a string:

# In[141]:


# Does "Sheep" occur in this string?
str1 = 'This string contains Sheep'
'Sheep' in str1


# In[142]:


# Does "Sheep" occur in this string?
str2 = 'This string contains Cows'
'Sheep' in str2
species.head(10)


# Use `apply` and a `lambda` function to create a new column in `species` called `is_sheep` which is `True` if the `common_names` contains `'Sheep'`, and `False` otherwise.

# In[143]:


species['is_sheep'] = species.common_names.apply(lambda x : 'Sheep' in x)
species.head(10)


# In[144]:


sheeps = species[species['is_sheep']==True]


# Select the rows of `species` where `is_sheep` is `True` and examine the results.

# In[145]:


sheeps.head(10)


# Many of the results are actually plants.  Select the rows of `species` where `is_sheep` is `True` and `category` is `Mammal`.  Save the results to the variable `sheep_species`.

# In[146]:


sheep_species = sheeps[sheeps['category']=='Mammal']
sheep_species.head(10)


# Now merge `sheep_species` with `observations` to get a DataFrame with observations of sheep.  Save this DataFrame as `sheep_observations`.

# In[147]:


sheep_observations = sheep_species.merge(observations,how='inner')
sheep_observations.head(20)


# How many total sheep observations (across all three species) were made at each national park?  Use `groupby` to get the `sum` of `observations` for each `park_name`.  Save your answer to `obs_by_park`.
# 
# This is the total number of sheep observed in each park over the past 7 days.

# In[148]:


obs_by_park = sheep_observations.groupby('park_name')['observations'].sum().reset_index()
obs_by_park.head(10)


# Create a bar chart showing the different number of observations per week at each park.
# 
# 1. Start by creating a wide figure with `figsize=(16, 4)`
# 1. Start by creating an axes object called `ax` using `plt.subplot`.
# 2. Create a bar chart whose heights are equal to `observations` column of `obs_by_park`.
# 3. Create an x-tick for each of the bars.
# 4. Label each x-tick with the label from `park_name` in `obs_by_park`
# 5. Label the y-axis `Number of Observations`
# 6. Title the graph `Observations of Sheep per Week`
# 7. Plot the grap using `plt.show()`

# In[153]:


plt.figure(figsize=(16,4))
ax = plt.subplot
plt.bar(obs_by_park.park_name,obs_by_park.observations)
plt.title('Observations of Sheep per Week')
plt.ylabel('Number of Observations')
plt.xlabel('National Park')
plt.show()


# Our scientists know that 15% of sheep at Bryce National Park have foot and mouth disease.  Park rangers at Yellowstone National Park have been running a program to reduce the rate of foot and mouth disease at that park.  The scientists want to test whether or not this program is working.  They want to be able to detect reductions of at least 5 percentage points.  For instance, if 10% of sheep in Yellowstone have foot and mouth disease, they'd like to be able to know this, with confidence.
# 
# Use <a href="https://s3.amazonaws.com/codecademy-content/courses/learn-hypothesis-testing/a_b_sample_size/index.html">Codecademy's sample size calculator</a> to calculate the number of sheep that they would need to observe from each park.  Use the default level of significance (90%).
# 
# Remember that "Minimum Detectable Effect" is a percent of the baseline.

# In[150]:


sample_size_req = 870


# How many weeks would you need to observe sheep at Bryce National Park in order to observe enough sheep?  How many weeks would you need to observe at Yellowstone National Park to observe enough sheep?

# In[151]:


import math
weeks_req_bryce = 1.0*sample_size_req / obs_by_park.iloc[0,1]
print weeks_req_bryce
print math.ceil(weeks_req_bryce)


# In[152]:


weeks_req_yellow = 1.0*sample_size_req / obs_by_park.iloc[2,1]
print weeks_req_yellow
print math.ceil(weeks_req_yellow)

