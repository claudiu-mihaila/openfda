#!/usr/bin/python
import codecs
import json
import urllib2

from keys import API_KEY


def get_event_drug_characterization(value):
    """define the drug characterization query"""
    search = '_exists_:serious'
    search += '+AND+serious:1'
    search += '+AND+_exists_:patient.drug.drugcharacterization'
    search += '+AND+patient.drug.drugcharacterization:{}'.format(value)
    return search


class OpenFDA:

    def __init__(self):
        """read in the configuration API Key"""
        # w/o API Key:  40 requests/minute/IP Address: 1,000 requests/day/IP Address
        # with API Key: 240 requests/minute/key:       120,000 requests/day/key
        self.api_key = API_KEY

    def api_request(self, query, limit=100, skip=0):
        """perform an OpenFDA Restful API Request"""
        if query.strip() == '':
            query = get_event_drug_characterization(2)
            count = "patient.drug.drugindication.exact"
        request_string = 'https://api.fda.gov/drug/event.json?api_key={0}&search={1}&limit={2}&skip={3}'
        request = request_string.format(self.api_key, query, limit, skip)
        print "Send Query as:\n{0}".format(request)
        response = urllib2.urlopen(request)
        fda_data = json.load(response)
        records_received = len(fda_data["results"])
        print "Result Count: {0}".format(records_received)
        return fda_data, records_received

    def load_from_api(self, search=""):
        """request the data from the OpenFDA API, requests are limited in 100 records at a time"""
        results = []
        max_records = 10000 # get only 10K events, about 600Mb in size
        record_count = 100
        offset = 0
        # limited by OpenFDA, maximum records at a time is 100 via search filters, use pagination
        for i in range(max_records / record_count):
            records, records_received = self.api_request(search, record_count, offset)
            offset += records_received
            results += records['results']
            print "Records Retrieved Count: {0}".format(len(results))

        with codecs.open("./../data/openfda_data.json", 'w', 'utf-8') as f:
            print "file api: results type", type(results)
            json.dump(results, f, indent=4, ensure_ascii=False)

        return results
