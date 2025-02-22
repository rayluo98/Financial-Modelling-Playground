#%%
# # for year in {2010..2025}; do ls -l /jpx/data/$year/*/*/* >> ~/ls_detailed.txt; done
with open('ls_detailed.txt', 'r') as f:
    s = f.readlines()

type_lists = {}
for f in s:
    split = f.split(' Feb')
    size = int(split[0].split(' ')[-1])
    date_file = split[-1].split('./')[-1]
    date = date_file[:10]
    name = date_file[11:-1]

    if date <= '2021/05/21': # this date and before is non-pcap
        filetype_extension = name.split('_')[0] + '.' + name.split('.')[-1]
    else:
        filetype_extension = name.split('_')[-1].split('.')[0] + '.' + name.split('_')[-2] + '.' + '.'.join(name.split('.')[-2:])

    if filetype_extension in type_lists:
        type_lists[filetype_extension][date] = size
    else:
        type_lists[filetype_extension] = {date: size}

#%%
import pandas as pd

df = []
for k, v in type_lists.items():
    df.append(pd.Series(v, name=k))

df = pd.DataFrame(df).T
zscore = (df - df.mean())/(df.std()+1e-4)

df.to_csv('file_size.csv')
zscore.to_csv('size_zscore.csv') # look for missing values and values smaller than -2.
# %%
