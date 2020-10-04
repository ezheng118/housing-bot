import requests
import bs4
#import selenium

#temp
import json

if __name__ == "__main__":
    # only searches through one site atm
    url = "https://raleigh.craigslist.org/search/hhh?query=<qqq>&availabilityMode=0&sale_date=all+dates"
    swap = "<qqq>"
    space = "+"

    # get the search queries that you want to use
    queries = {}
    with open('./defaults.json') as param_file:
        json_string_data = param_file.read()
        params = json.loads(json_string_data)

        queries = list(params['queries'].values())
        for i in range(len(queries)):
            queries[i] = queries[i].replace('<location>', params['location'])
            queries[i] = queries[i].replace(' ', space)

    print(queries)

    for query in queries:
        # retrieve the webpage
        search = url.replace(swap, query)

        res = requests.get(search)
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as err:
            # TODO: implement actual exception handling
            print(f'Issue: {err}')
        
        # use bs4 to parse the retrieved html
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        # for craigslist look through section class=page-container ->
        # form id=searchform -> div class=content -> ul class=rows -> li class=result-row
        search_results = soup.select('body > section > form > div > ul > li')

        # inside of the li tag is:
        # an a tag href=*the url we want*
        # data-pid values, will let us easily check for duplicates
        # data-pid method might only be valid for craigslist

        # avoid parsing duplicate listings by tracking listings already parsed
        checked_results = set() # only need to test for membership

        # want to iterate through the search results and get the urls for each listing
        for res in search_results:
            if res.get('data-pid') in checked_results:
                continue

            listing = requests.get(res.a.get('href'))
            try:
                listing.raise_for_status()
            except requests.exceptions.HTTPError as err:
                #TODO: more exception handling
                print(f'Issue: {err}')
            
            
            checked_results.add(res.get('data-pid'))