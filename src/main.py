#!/usr/bin/python
from src.openfda import *
from src.reporter import Report

openfda = OpenFDA()

# fetch some data from openFDA, and save it locally for use
# events = openfda.load_from_api_counts(get_event_drug_characterization(2, "../data/drugcharacterization:2.json"))
# events = openfda.load_from_api_counts(get_event_count_by_medicinalproduct(2), "../data/count:medicinalproduct.json")
# events = openfda.load_from_api_counts(get_event_count_by_occurcountry(), "../data/count:occurcountry.json")
# events = openfda.load_from_api_counts(get_event_count_by_reactionmeddrapt(), "../data/count:reactionmeddrapt.json")

print("reading stored data...")
countries = openfda.load_from_file("../data/count:occurcountry.json")
reactions = openfda.load_from_file("../data/count:reactionmeddrapt.json")
medicines = openfda.load_from_file("../data/count:medicinalproduct.json")

reporter = Report(countries, reactions, medicines)
print("starting report...")
reporter.report_reactionmeddrapt_by_occurcountry(cached_data=True, debug=True)