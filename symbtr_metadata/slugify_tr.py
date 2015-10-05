import unicodedata
import re

def slugify_tr(value):  
    value_slug = value.replace(u'\u0131', 'i')
    value_slug = unicodedata.normalize('NFKD', 
        value_slug).encode('ascii', 'ignore').decode('ascii')
    value_slug = re.sub('[^\w\s-]', '', value_slug).strip()
    
    return re.sub('[-\s]+', '-', value_slug)