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
    search += '+AND+patient.drug.drugcharacterization:{}'.format(urllib2.quote(value))
    search += '&limit={}'
    search += '&skip={}'
    return search


def get_event_count_by_occurcountry():
    """define counts by country query"""
    search = '_exists_:serious'
    search += '+AND+serious:1'
    search += '+AND+_exists_:occurcountry'
    search += '&count=occurcountry.exact'
    search += '&limit=1000'
    return search


def get_event_count_by_medicinalproduct(value):
    """define counts by medicinalproduct query"""
    search = '_exists_:serious'
    search += '+AND+serious:1'
    search += '+AND+_exists_:patient.drug.medicinalproduct'
    search += '+AND+_exists_:patient.drug.drugcharacterization'
    search += '+AND+patient.drug.drugcharacterization:{}'.format(value)
    search += '&count=patient.drug.medicinalproduct.exact'
    search += '&limit=1000'
    return search


def get_event_count_by_reactionmeddrapt():
    """define counts by reactionmeddrapt query"""
    search = '_exists_:serious'
    search += '+AND+serious:1'
    search += '+AND+_exists_:patient.reaction.reactionmeddrapt'
    search += '&count=patient.reaction.reactionmeddrapt.exact'
    search += '&limit=1000'
    return search


def get_reactionmeddrapt_event_count_by_occurcountry(value):
    """define the drug characterization query"""
    search = '_exists_:serious'
    search += '+AND+serious:1'
    search += '+AND+_exists_:occurcountry'
    search += '+AND+_exists_:patient.reaction.reactionmeddrapt'
    search += '+AND+patient.reaction.reactionmeddrapt.exact:"{}"'.format(value)
    search += '&count=occurcountry.exact'
    search += '&limit=1000'
    return search


class OpenFDA:

    def __init__(self, debug=False):
        """read in the configuration API Key"""
        # w/o API Key:  40 requests/minute/IP Address: 1,000 requests/day/IP Address
        # with API Key: 240 requests/minute/key:       120,000 requests/day/key
        self.api_key = API_KEY
        self.debug = debug

    def api_request(self, query, limit=0, skip=0):
        """perform an OpenFDA Restful API Request"""
        if query.strip() == '':
            query = get_event_drug_characterization(2)
        request = 'https://api.fda.gov/drug/event.json?api_key={0}&search={1}'.format(self.api_key,
                                                                                      query.format(limit, skip))
        if self.debug:
            print "Send Query as:\n{0}".format(request)
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError:
            print("Bad query for {}".format(request))
            return {"results": []}, 0

        fda_data = json.load(response)
        records_received = len(fda_data["results"])
        if self.debug:
            print "Result Count: {0}".format(records_received)
        return fda_data, records_received

    def load_from_api_full_events(self, search="", outfile="../data/results.json"):
        """request the data from the OpenFDA API, requests are limited to 100 records at a time"""
        results = []
        max_records = 100  # get only 10K events, about 600Mb in size
        record_count = 100
        offset = 0
        # limited by OpenFDA, maximum records at a time is 100 via search filters, use pagination
        for i in range(max_records / record_count):
            records, records_received = self.api_request(search, record_count, offset)
            offset += records_received
            results += records['results']
            if self.debug:
                print "Records Retrieved Count: {0}".format(len(results))

        with codecs.open(outfile, 'w', 'utf-8') as fout:
            if self.debug:
                print "file api: results type", type(results)
            json.dump(results, fout, indent=4, ensure_ascii=False)

        return results

    def load_from_api_counts(self, search="", outfile="../data/counts.json"):
        """request count data from the OpenFDA API"""
        results = []
        # limited by OpenFDA, maximum records at a time is 100 via search filters, use pagination
        records, records_received = self.api_request(search)
        results += records['results']
        if self.debug:
            print "Records Retrieved Count: {0}".format(len(results))

        with codecs.open(outfile, 'w', 'utf-8') as fout:
            if self.debug:
                print "file api: results type", type(results)
            json.dump(results, fout, indent=4, ensure_ascii=False)

        return results

    def load_from_file(self, filename):
        with codecs.open(filename, 'r', 'utf-8') as fin:
            return json.load(fin)
        return []
