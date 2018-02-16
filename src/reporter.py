#!/usr/bin/python

import matplotlib.pyplot as plt
import pandas

from src.openfda import get_reactionmeddrapt_event_count_by_occurcountry, OpenFDA


class Report:

    def __init__(self, country_json, reaction_json, medicine_json):
        self.country_counts = pandas.DataFrame(country_json)
        self.reaction_counts = pandas.DataFrame(reaction_json)
        self.medicine_counts = pandas.DataFrame(medicine_json)

    def get_reactionmeddrapt_by_occurcountry(self):
        openfda = OpenFDA()
        df_append = []
        missing_terms = []
        for r in self.reaction_counts.term[90:100]:
            term = "+".join(r.split(" "))
            term = "+".join(term.split("^"))
            term = "+".join(term.split("'"))
            term = "+".join(term.split(","))
            print(term)
            results = openfda.load_from_api_counts(get_reactionmeddrapt_event_count_by_occurcountry(term))
            if len(results) > 0:
                df = pandas.DataFrame(results)
                df.set_index("term", drop=True, inplace=True)
                df_append.append(df)
            else:
                # terms for which no results are returned need to be removed
                missing_terms.append(r)
        final_df = pandas.concat(df_append, axis = 1)
        final_df.columns = [x for x in self.reaction_counts.term[90:100] if x not in missing_terms]
        print(final_df.shape)
        return final_df

    def report_reactionmeddrapt_by_occurcountry(self):
        df = self.get_reactionmeddrapt_by_occurcountry()

