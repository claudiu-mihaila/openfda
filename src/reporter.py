#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy
import pandas
from matplotlib.ticker import FuncFormatter, IndexLocator
from scipy.spatial.distance import euclidean, pdist, squareform

from src.openfda import get_reactionmeddrapt_event_count_by_occurcountry, OpenFDA


class Report:

    def __init__(self, country_json, reaction_json, medicine_json):
        self.country_counts = pandas.DataFrame(country_json)
        self.reaction_counts = pandas.DataFrame(reaction_json)
        self.medicine_counts = pandas.DataFrame(medicine_json)

    def get_reactionmeddrapt_by_occurcountry(self, debug=False):
        openfda = OpenFDA(debug=debug)
        df_append = []
        missing_terms = []
        for r in self.reaction_counts.term:
            term = "+".join(r.split(" "))
            # some characters break the API, either raw or encoded/quoted by urllib2
            term = "+".join(term.split("^"))
            term = "+".join(term.split("'"))
            term = "+".join(term.split(","))
            if debug:
                print(term)
            results = openfda.load_from_api_counts(get_reactionmeddrapt_event_count_by_occurcountry(term))
            if len(results) > 0:
                df = pandas.DataFrame(results)
                df.set_index("term", drop=True, inplace=True)
                df_append.append(df)
            else:
                # terms for which no results are returned need to be removed
                missing_terms.append(r)
        final_df = pandas.concat(df_append, axis=1)
        final_df.columns = [x for x in self.reaction_counts.term if x not in missing_terms]
        return final_df.fillna(0)

    def report_reactionmeddrapt_by_occurcountry(self, cached_data=False, debug=False):
        if cached_data:
            if debug:
                print("fetching cached data for report...")
            df = pandas.read_pickle("../data/cached_reactionmeddrapt_by_occurcountry.pkl")
        else:
            if debug:
                print("fetching data for report from API...")
            df = self.get_reactionmeddrapt_by_occurcountry()
            df.to_pickle("../data/cached_reactionmeddrapt_by_occurcountry.pkl")

        if debug:
            print(df.shape)
            print("reporting")

        plt.figure()
        df.sum(axis=1).plot(kind="bar", figsize=(30, 6), fontsize=11)
        plt.title("Number of adverse events reported by country")
        plt.gcf().savefig("../output/reactions_by_country.png", dpi=100)

        plt.figure()
        df.transpose().describe().loc["count"].sort_values().plot(kind="bar", figsize=(32, 12), fontsize=11)
        plt.title("Number of distinct adverse events reported by country")
        plt.gcf().savefig("../output/distinct_reactions_by_country.png", dpi=100)

        plt.figure()
        df.transpose().describe().loc["count"].plot(kind="hist", figsize=(15, 3), fontsize=11)
        plt.title("Histogram of number of distinct adverse events reported by country")
        plt.gcf().savefig("../output/hist_distinct_reactions_by_country.png", dpi=100)

        normalised_df = df.divide(df.sum(axis=1), axis=0)
        plt.figure()
        normalised_df.plot(kind="bar", figsize=(32, 12), fontsize=11, stacked=True)
        plt.title("Normalised adverse events reported by country")
        plt.gcf().savefig("../output/normalised_reactions_by_country.png", dpi=100)

        dists = pdist(normalised_df, euclidean)
        similarity_df = pandas.DataFrame(squareform(dists), columns=df.index, index=df.index)
        plt.figure()
        fig, ax = plt.subplots()
        fig.set_size_inches(40, 40)
        ax.xaxis.tick_top()
        plt.xticks(rotation=70)

        def format_fn(tick_val, tick_pos):
            if tick_val >= 0 and int(tick_val) in range(len(similarity_df.index)):
                return similarity_df.index[int(tick_val)]
            else:
                return ''

        ax.xaxis.set_ticks(numpy.arange(0, len(similarity_df.index), 1))
        ax.xaxis.set_major_formatter(FuncFormatter(format_fn))
        ax.xaxis.set_major_locator(IndexLocator(1, 0))
        ax.yaxis.set_major_formatter(FuncFormatter(format_fn))
        ax.yaxis.set_major_locator(IndexLocator(1, 0))
        plt.imshow(similarity_df, cmap='hot', interpolation='nearest')
        plt.colorbar()
        plt.gcf().savefig("../output/similar_countries_heatmap.png", dpi=200)
