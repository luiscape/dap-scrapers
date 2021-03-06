import json
import requests
import datetime
import orm
"""Value: dsID, region, indID, period, value, source, is_number
   DataSet: dsID, last_updated, last_scraped, name
   Indicator: indID, name, units
"""


def yeartotimestamp(year):
    d = datetime.datetime(year=year, month=1, day=1)
    return int(d.strftime('%s'))


def getcountrylist():
    for value in orm.session.query(orm.Value).filter(orm.Value.indID == "CG060").all():
        yield value.region

dsID = "reliefweb-api"

dataset = {'dsID': dsID,
           'last_updated': orm.now(),
           'last_scraped': orm.now(),
           'name': "ReliefWeb API"}

orm.DataSet(**dataset).save()

ocha_products = """Situation Report
Humanitarian Bulletin
Humanitarian Dashboard
Humanitarian Snapshot
Key Messages
Press Release
Press Review
Statement/Speech
Other
Thematic Map
Reference Map
Infographic""".split('\n')

#baseurl = "http://api.rwlabs.org/v0/report/list?limit=1&query[value]={country}&query[fields][0]=country&filter[field]=date.created&filter[value][from]={from}000&filter[value][to]={to}000"


def get_product_query(FROM, TO, COUNTRY, PRODUCT):
    return json.dumps({#"limit": 0,
                       "filter":
                          {"operator": "and",
                           "conditions":
                              [
                                  {'field': 'date.original',
                                   'value': {'from': FROM, 'to': TO}
                                  },
                                  {'field': 'country',
                                   'value': COUNTRY
                                  },
#                                 {'field': 'title',
#                                  'value': TITLE},
                                  {'field': 'ocha_product',
                                   'value': PRODUCT},
                              ]
                          }
                      })

def get_job_query(COUNTRY):
    return json.dumps({"limit": 0,
                       "filter":
                          {"operator": "and",
                           "conditions":
                              [
                                  {'field': 'country',
                                   'value': COUNTRY
                                  },
                                  {'field': 'date.closed',
                                   'value': {'from': FROM, 'to': TO}
                                  }
                              ]
                          }
                      })


countries = list(getcountrylist())

def do_products():
    for product in ocha_products:
        print product
        niceproduct = product.replace(" ", "_")
        indID = "reliefweb_" + niceproduct
        indicator = {'indID': indID,
                     'name': "Number of ReliefWeb reports flagged with ocha_product: %s" % product,
                     'units': 'uno'}
        orm.Indicator(**indicator).save()

        for country in countries:
            for year in range(1990, 2014):
                params = dict()
                params['PRODUCT'] = product
                params['COUNTRY'] = country
                params['FROM'] = 1000 * yeartotimestamp(year)
                params['TO'] = 1000 * yeartotimestamp(year + 1) - 1
                url = "http://api.rwlabs.org/v0/report/list"
                r = requests.get(url, data=get_product_query(**params))
                if 'data' not in r.json():
                    print r.json()
                    print country
                    continue
                value = {'region': country,
                         'period': str(year),
                         'value': r.json()['data']['total'],
                         'dsID': dsID,
                         'indID': indID,
                         'source': url,
                         'is_number': True}
                orm.Value(**value).save()

def do_jobs():
    print "jobs"
    indID = "reliefweb_jobs"
    indicator = {'indID': indID,
                 'name': "Number of jobs on ReliefWeb at specified time",
                 'units': 'uno'}
    orm.Indicator(**indicator).save()
    for country in countries:
        url = "http://api.rwlabs.org/v0/job/list"
        r = requests.get(url, data=get_job_query(country))
        if 'data' not in r.json():
            print r.json()
            print country
            continue
        value = {'region': country,
                 'period': orm.now()[:10],  # we don't need sub-day precision.
                 'value': r.json()['data']['total'],
                 'dsID': dsID,
                 'indID': indID,
                 'source': url,
                 'is_number': True}
        orm.Value(**value).save()

# do_jobs()
do_products()
