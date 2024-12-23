#%%
import xml.etree.ElementTree as ET
tree = ET.parse('GLOBAL.config')
root = tree.getroot()
root.get
print(root.get('CACHE_DIR'))
# %%
