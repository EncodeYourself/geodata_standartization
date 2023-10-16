import utls
import pandas as pd
import os
import numpy as np

pd.set_option('display.max_colwidth', 80)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


#%%
data = os.getcwd() + '/geoutf8.csv'
df = pd.read_csv(data, names=['old', 'new'], skiprows=1)
df.dropna(inplace=True)
df.head()
#%%
mutations = {
    'C': ['россия'],
    'R1': ['область','обл'],
    'R2': ['республика', 'респ'],
    'R3': ['край'],
    'R4': ['автономный округ'],
    'D': ['район', 'р-н'],
    'D2': ['городской округ'],
    'G': ['город ', 'г'],
    'V1': ['деревня'],
    'V2': ['село', 'с'],
    'V3': ['станица', 'ст-ца'],
    'V4': ['пгт', 'пос[её]лок городского типа'],
    'V5': ['рабочий пос[её]лок', 'рп'],
    'V6': ['пос[её]лок', 'п'],
    'V7': ['аул'],
    'V8': ['починок', 'поч'],
    'V9': ['хутор', 'х'],
    'VV': ['слобода', 'сл'],
    'S1': ['проспект', 'пр-кт'],
    'S2' : ['улица', 'ул', 'у'],
    'S3': ['переулок', 'пер', 'пр'],
    'S4': ['площадь', 'пл'],
    'S5': ['бульвар', 'б'],
    'B': ['дом', 'стр'],
    'X': ['д'],
    'Z': ['квартира', 'кв','кабинет', 'каб']
}

all_values = sum(mutations.values(), [])
reversed_mutations = utls.reverse(mutations)
#%%
df['raw'] = df['old'].apply(lambda string: utls.preprocess(string, all_values, reversed_mutations))

x = utls.GA(df, pop_size=4)
for i in range(10):
    x.forward()
    x.get_scores()
    print(x.results)
    x.select_parents()
    print(x.df[['result0']].head(100))
    #print(x.population[0], '\n', x.population[1])
x.df[['old','new', 'result0']].to_csv('result.csv')