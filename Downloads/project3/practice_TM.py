import os
import re
import sqlite3

import pandas as pd
DB_FILENAME = 'DB_API.db'
DB_FILEPATH = os.path.join(os.getcwd(), DB_FILENAME)
con = sqlite3.connect(DB_FILENAME)
cur = con.cursor()
query = cur.execute("SELECT * From corona")
cols = [column[0] for column in query.description]
race_result = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
con.close()
import nltk
import pickle
from nltk.corpus import stopwords

print(race_result)