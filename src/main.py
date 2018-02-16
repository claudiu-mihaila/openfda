#!/usr/bin/python
from src.openfda import OpenFDA


openfda = OpenFDA()
results = openfda.load_from_api() # load default search query