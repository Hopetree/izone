from django.test import TestCase
import datetime

# Create your tests here.

if __name__ == '__main__':
    site_date = datetime.datetime.strptime('2018-04-12', '%Y-%m-%d')
    print(site_date)
