## Getting Training Data
The training data we used for this challenge was *bigquery-public-data:github_repos*, publicly available on Google BigQuery and provided by GitHub. This dataset is all of the "contents from 2.9M public, open source licensed repositories on GitHub". The dataset is approximately 3+ TB in size, so to make things easier, we recommend that you sign up for a Google Cloud Free Trial, which provides you $300 of credit over a 60 day trial period.

Alternatively, Google also provides a "free" tier for low-volume queries (free first 1 TB per month). You may be able to use that free 1 TB to query the sample tables provided by Github on BigQuery. These sample tables are a random sample of their larger cousins, so they are useful to experiment against. 

### BigQuery
Specifically, we focused on downselecting to Python files (i.e. files ending in \*.py) from the *files* and *contents* table. Keep in mind that the *contents* table only contains the actual contents of files which are 1MB or less (any larger files are replaced by a string "null" in the *contents* column).

The specific SQL queries that we ran are in the *queries* folder.

If you ran on the sample tables, the results may be small enough to download directly from the browser. However, if you ran on the full dataset, then you will need to export to Google Cloud Storage and use a tool like *gsutil* (https://cloud.google.com/storage/docs/gsutil_install) to download the data from object storage.

## Getting Testing Data
The testing data we used for this challenge was *Meta Kaggle*, publicly available at https://www.kaggle.com/kaggle/meta-kaggle. This dataset is Kaggle's public data on competitions, users, submission scores, and kernels. As of version 7 in early February 2017, the dataset is approximately 459 MB in size (compressed). The zipped archive contains a series of csv files as well as a sqlite database (approximately 1.1 GB) for relational queries.

### Meta Kaggle
We focused on downselecting to Python files (i.e. ScriptLanguageId=2) from the *ScriptVersions* table with several joins to associated tables to obtain unique identifiers for the Competition and Author. Spot checks revealed that some R files were incorrectly labeled as Python files in the Meta Kaggle dataset.

The specific SQL queries that we ran are in the *queries* folder.

### sqlite
Installing sqlite can be accomplished on Ubuntu via:

*sudo apt-get install sqlite*

Opening the Meta Kaggle sqlite database is done via:

*sqlite3 database.sqlite*

Changing the output mode from stdout to csv is done through the following commands:

*sqlite> .mode csv*

*sqlite> .output test.csv*

*sqlite> select * from tbl1;*

*sqlite> .output stdout*

After obtaining the csv output file from sqlite, we converted the csv to json via a Python script and did some light preprocessing. The json conversion script is located in the *preprocess00* folder.