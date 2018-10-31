from django.test import TestCase

# Create your tests here.

def table_url_cases():
   import os
   os.system("curl 'http://127.0.0.1:8000/tables?preceding=+left+%2C+right++&succeeding=&main=+amygdala%2C++hippo&fields=allfields'")

   os.system("curl 'http://127.0.0.1:8000/tables?preceding=+left+%2C+right++&succeeding=&main=amygdala+%2C+hippo&constraint=depression%2C+emotion&constraint=fmri+&constraint=&fields=allfields'")
   return

table_url_cases()