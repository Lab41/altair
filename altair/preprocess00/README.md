## Getting Data
The data we used for this challenge was *bigquery-public-data:github_repos*, publicly available on Google BigQuery and provided by GitHub. This dataset is all of the "contents from 2.9M public, open source licensed repositories on GitHub". The dataset is approximately 3+ TB in size, so to make things easier, we recommend that you sign up for a Google Cloud Free Trial, which provides you $300 of credit over a 60 day trial period.

Alternatively, Google also provides a "free" tier for low-volume queries (free first 1 TB per month). You may be able to use that free 1 TB to query the sample tables provided by Github on BigQuery. These sample tables are a random sample of their larger cousins, so they are useful to experiment against. 

### BigQuery
Specifically, we focused on downselecting to Python files (i.e. files ending in \*.py) from the *files* and *contents* table. Keep in mind that the *contents* table only contains the actual contents of files which are 1MB or less (any larger files are replaced by a string "null" in the *contents* column).

The specific queries that we ran are in the *data/queries* folder.

If you ran on the sample tables, the results may be small enough to download directly from the browser. However, if you ran on the full dataset, then you will need to export to Google Cloud Storage and use a tool like *gsutil* (https://cloud.google.com/storage/docs/gsutil_install) to download the data from object storage.