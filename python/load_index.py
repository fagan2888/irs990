# Copyright 2017 Charity Navigator.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

FIRST_YEAR = 2011

from pyspark import SparkContext
from datetime import datetime
import os
import json
from cred import Credentials
from schema import Filing, RawXML
import boto
from boto.s3.key import Key

cred = Credentials()

def makeSession():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engineStr = cred.getEngineStr()
    engine = create_engine(engineStr)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    return session

def key_to_str(bucket, key):
    #start = time.time()
    ret = bucket.get_key(key) \
            .get_contents_as_string() \
            .replace("\r", "")
    #end = time.time()
    #print "Retrieved %s in %0.2fs." % (key,end-start)
    return ret

def get_na(record, key):
    if key in record:
        return record[key]
    return None
    
def submittedOn(raw):
    return datetime.strptime(raw, "%Y-%m-%d").date()

def taxPeriod(raw):
    return datetime.strptime(raw, "%Y%m").date()

def lastUpdated(raw):
    raw = raw.split(".")[0]
    return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S")

sc = SparkContext()
#sc.addPyFile("dependencies.zip")

def retrieveForYear(year):
    r = boto.connect_s3(host="s3.amazonaws.com") \
            .get_bucket("irs-form-990") \
            .get_key("index_%i.json" % year) \
            .get_contents_as_string() \
            .replace("\r", "")
    j = json.loads(r)
  
    # The index comes back as a single JSON key-value pair whose value is
    # a JSON array of length one. Inside _that_ is an array of filings.

    filings = j.values()[0]

    if cred.prod:
        return filings
    else:
        sample = filings[0:1000]
        return sample

def loadToDB(records):
    session = makeSession()

    for record in records:
        f = Filing()
        f.OrganizationName = get_na(record, "OrganizationName")
        f.ObjectId         = get_na(record, "ObjectId")
        f.SubmittedOn      = submittedOn(get_na(record, "SubmittedOn"))
        f.DLN              = get_na(record, "DLN")
        f.LastUpdated      = lastUpdated(get_na(record, "LastUpdated"))
        f.TaxPeriod        = taxPeriod(get_na(record, "TaxPeriod"))
        f.IsElectronic     = get_na(record, "IsElectronic")
        f.IsAvailable      = get_na(record, "IsAvailable")
        f.FormType         = get_na(record, "FormType")
        f.EIN              = get_na(record, "EIN")
        f.URL              = get_na(record, "URL")

        session.add(f)
        session.commit()

    session.close()

def getYears(first_year=FIRST_YEAR):
    year = first_year
    failed = False
    years = []

    bucket = boto.connect_s3(host="s3.amazonaws.com") \
            .get_bucket("irs-form-990")

    while not failed:
        failed = not bucket.get_key("index_%i.json" % year)
        if not failed:
            years.append(year)
        year += 1

    return years


if cred.prod:
    partitions = 200
else:
    partitions = 10

years = getYears()

sc.parallelize(years, len(years)) \
        .flatMap(lambda y : retrieveForYear(y)) \
        .repartition(partitions) \
        .foreachPartition(loadToDB)
