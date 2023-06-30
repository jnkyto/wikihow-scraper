# wikihow-scraper  
Very simple Wikihow scraper which fetches random articles and dumps them into .json-files. Designed for Python 3.11.

### Usage:  
1. Create a .env-file and set your user-agent header with `UA="<your UA here>"` and `EMAIL="<your email here>"`.
   - Ideally you should write what and why you are scraping in the UA field.
2. Each batch contains 100 articles. The batches are written to separate files.
3. Run `python main.py -b <number of batches>`.

### Notes:

The URL's are hashed and stored in memory so that the same article won't be dumped twice. However, this only works 
within a single run, as the hashes are stored but not checked from local storage.