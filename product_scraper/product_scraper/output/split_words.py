
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


products = pd.read_csv('Product.csv')


# In[3]:


products.head()


# In[9]:


products = products.sort_values(by='wp_product_type')


# In[55]:


total = len(products)

batch = 25000


# In[1]:


all_dfs = []
start = 0
end = batch
sum = 0
while start < total:
    df = pd.DataFrame(products[start:end])
    all_dfs.append(df)
    sum = sum + len(df)
    start = end
    end = start + batch

    if end > total:
        end = total


# In[57]:


for index, d in enumerate(all_dfs):
    d.to_csv('product_'+str(index+1))
