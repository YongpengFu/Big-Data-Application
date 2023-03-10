import requests  # send request to website
from bs4 import BeautifulSoup as bs  # convert the web content to bs object
from bs4 import Comment  # search if we are caught by Amazon as a robot
# create fake user agent from different browser
from fake_useragent import UserAgent
import re  # regular expression
import pandas as pd  # output dataframe
import numpy as np  # fast data manipulation
import random  # randomly use agent header for sending request
import time  # If access is denied, sleep 5s and then request again
from collections import defaultdict  # Used to declare a dictionary with emply
import os
import csv
from string import punctuation

# Create a class to deal with web request and convert it to beautiful soup


class get_soup:
    header = None
    # When the class is initiated, a list of user agent will be generated
    '''
    There is a pretty useful third-party package called fake-useragent 
    that provides a nice abstraction layer over user agents: https://pypi.org/project/fake-useragent/

    If you don't want to use the local data, you can use the external data source to retrieve the user-agents. 
    #Set use_external_data to True:
    '''

    def __init__(self, total_user_agent=1000):
        ua = UserAgent(
            browsers=["chrome", "edge", "internet explorer", "firefox", "safari", "opera"])
        # I will generate a lsit of fake agent string with total number of total_user_agent
        self.user_agent_set = set()
        # Set a cap for user_agent_set to prevent endless loop
        while(len(self.user_agent_set) < total_user_agent and len(self.user_agent_set) < 4500):
            self.user_agent_set.add(ua.random)
    '''
    Define the function to get contents from each page. 
    Each header_attempts will use the same header until it is caught by the weg server.
    In each header_attempts, we will try request_attempts times to request contents until we get the right contents
    '''

    def get_individual_soup(self, url, header_attempts=10, request_attempts=10):
        self.soup = 'No Data Returned'
        for _ in range(header_attempts):
            request_count = 0
            page = ''
            notDenied = True
            # We want to keep using the same header if that one particular header is working
            # We change it unless it is recognized and banned by Web server
            if get_soup.header is None:
                user_agent = random.choice(list(self.user_agent_set))
                get_soup.header = {'content-type': 'text/html;charset=UTF-8',
                                   'Accept-Encoding': 'gzip, deflate, sdch',
                                   'Accept-Language': 'en-US,en;q=0.8',
                                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                   "User-Agent": user_agent}

            while page == '' and request_count < request_attempts and notDenied:
                try:
                    request_count += 1
                    page = requests.get(
                        url, headers=get_soup.header, timeout=10)
                    self.soup = bs(page.content, "lxml")
                    '''If the page returns a message like To discuss automated access 
                        to Amazon data please contact api-services-support@amazon.com.
                        We know we are denied access to the web page.
                        Or,
                        Amazon page blocks you by returning a login page
                        In either case, lets try again using different header
                    '''
                    comments = self.soup.find_all(
                        string=lambda text: isinstance(text, Comment))
                    login_page = self.soup.find(
                        'a', id='createAccountSubmit', class_='a-button-text')
                    for comment in comments:
                        if ("api-services-support@amazon.com" in comment) or login_page:
                            notDenied = False
                            get_soup.header = None
                            self.soup = 'No Data Returned'
                            break

                    if (notDenied):
                        return self.soup
                    # We are caught by Web server as a bot, break this while and try a new header
                    break
                except:
                    get_soup.header = None
                    print("Connection refused by the server..")
                    print("Let me sleep for 5 seconds")
                    time.sleep(5)
                    print("Now I will use a different header to request data...")
                    # The server does not respond to our request, break this while and try a new header
                    break
        return self.soup
    '''
    Customer Reviews, including Product Star Ratings, 
    help customers to learn more about the product and decide whether it is the right product for them.
    To calculate the overall star rating and percentage breakdown by star, we don’t use a simple average. 
    Instead, our system considers things like how recent a review is and if the reviewer bought the item on Amazon. 
    It also analyses reviews to verify trustworthiness.
    Learn more from
    https://www.amazon.co.uk/gp/help/customer/display.html/ref=cm_cr_arp_d_omni_lm_btn?nodeId=G8UYX7LALQC8V9KA'''
    # Define a function to get the review of a product on one page only

    def get_page_reviews(self, ASIN, soup=None):
        reviewlist = []
        if soup is not None:
            for item in soup.find_all('div', {'data-hook': 'review'}):
                try:
                    # This is domenstic review
                    review = {
                        'ASIN': ASIN,
                        'product Name': soup.title.text.replace('Amazon.co.uk:Customer reviews:', '').strip(),
                        'Review Title': item.find('a', {'data-hook': 'review-title'}).get_text().strip(),
                        'Review Rating':  float(item.find('i', {'data-hook': 'review-star-rating'}).get_text().replace('out of 5 stars', '').strip()),
                        'Review Body': item.find('span', {'data-hook': 'review-body'}).get_text().strip(),
                        'Review Date': item.find('span', {'data-hook': 'review-date'}).get_text().strip(),
                    }
                except AttributeError:
                    # This is international review
                    try:
                        review = {
                            'ASIN': ASIN,
                            'product Name': soup.title.text.replace('Amazon.co.uk:Customer reviews:', '').strip(),
                            'Review Title': item.find('span', {'data-hook': 'review-title'}).get_text().strip(),
                            'Review Rating':  float(item.find('i', {'data-hook': 'cmps-review-star-rating'}).get_text().replace('out of 5 stars', '').strip()),
                            'Review Body': item.find('span', {'data-hook': 'review-body'}).get_text().strip(),
                            'Review Date': item.find('span', {'data-hook': 'review-date'}).get_text().strip(),
                        }
                    except:
                        # If there is still error, return None
                        review = {
                            'ASIN': None,
                            'product Name': None,
                            'Review Title': None,
                            'Review Rating': None,
                            'Review Body': None,
                            'Review Date': None,
                        }
                reviewlist.append(review)
        return reviewlist

# Create a class to handle all the file I/O


class Review_file_io:
    '''
    This method is to get the root link for each product
    '''
    @classmethod
    def get_review_link(cls, file_loc):
        # Get the review entrance link for all the product items
        review_links = {}
        with open(file_loc, mode="r") as f:
            for link in f:
                entry_link = link.strip().split(",")[0]
                if (not re.search("product-reviews/.*/ref", entry_link)):
                    continue
                ASIN = re.search("product-reviews/.*/ref",
                                 entry_link).group(0).split("/")[1]
                '''Need to think this again, this is mainly for empty page loc'''
                if re.search(r'&pageNumber=\d+$', entry_link):
                    review_links[ASIN] = entry_link
                else:
                    review_links[ASIN] = entry_link + "&pageNumber="
        return review_links
    '''
    This method is to get all the reviews on every page of a product
    '''

    def get_product_reviews(self, file_loc, reviews_loc, empty_page_loc, total_page=999, header_attempts=3, request_attempts=1):
        review_links = Review_file_io.get_review_link(file_loc)
        mySoup = get_soup()
        empty_page = defaultdict(list)
        reviews = []
        # loop through each page and get reviews on each page
        for ASIN, review_link in review_links.items():
            for page_number in range(1, total_page):
                print(f"You are on product {ASIN} page {page_number}")
                page_url = f"{review_link}{page_number}"
                page_soup = mySoup.get_individual_soup(
                    page_url, header_attempts=header_attempts, request_attempts=request_attempts)
                '''
                There are 3 cases page_soup equals 'No Data Returned'.
                1st is when you get caught by Amazon as a bot;
                2nd is Amazon returns you a login page
                3rd is when our scrapper has tried header_attempts*request_attempts times to reach the page,
                    but still got nothing, either rejected or caught by the server;

                There are case that you do get the page content from our web scrapper,
                but there are no reviews on that page. For example, 
                1. You get the page, but the page 
                2. you hit the last review page;
                3. the product item just does not have any reviews at all.
                '''
                if page_soup != 'No Data Returned':
                    review = mySoup.get_page_reviews(ASIN, page_soup)
                    # There are simply no reviews for this product item, there are 2 things can happen:
                    # 1st: the review page is just some random page returned by Amazon
                    # 2nd: the review page is a normal review page but
                    # because the page number has gone out of bound, there is simply no review at all
                    if not review:
                        # this is is to check if the page is a normal review page but the page number is out of boundary
                        # The first find is to check if the page still has product title
                        # The second find is to check if there is no Previous Page or Next Page button, that means this is it, there is no more reviews to look, break it
                        # what is inside this tag is: '←Previous pageNext page→'
                        if page_soup.find("a", attrs={"data-hook": "product-link"}) and not page_soup.find("ul", {'class': 'a-pagination'}):
                            break
                        continue

                    reviews.extend(review)

                    # if not page_soup.find("ul", {'class': 'a-pagination'}):
                    # break
                    # Last page is hit, we break the for loop
                    if page_soup.find('li', {'class': 'a-disabled a-last'}):
                        break
                    else:
                        continue
                # When we failed to get the content for this page, record this page, and go to the next page
                else:
                    empty_page[ASIN].append(page_url)
                    continue
        # Save the reviews and empty page link
        try:
            with open(reviews_loc, mode="a") as f:
                csv_columns = ['ASIN', 'product Name', 'Review Title',
                               'Review Rating', 'Review Body', 'Review Date']
                writer = csv.DictWriter(f, fieldnames=csv_columns)
                writer.writeheader()
                for prod_info in reviews:
                    writer.writerow(prod_info)

            with open(empty_page_loc, mode="a") as f:
                writer = csv.writer(f)
                writer.writerow(['URLs', 'ASIN'])
                for key, page in empty_page.items():
                    for link in page:
                        writer.writerow([link, key])
        except:
            print("I/O error")


if __name__ == '__main__':
    '''
    ./Dataset/Sample_link.csv: the file location contains the entrance link for product item review;
    ./Dataset/review.csv: the file location that will output all the reviews for a particular product item;
    ./Dataset/empty_link.csv: the file location that will output all the page information if we cannot reach them
    '''

    '''
    Chnage the ./Dataset/Sample_link.csv, ./Dataset/review.csv and ./Dataset/empty_link.csv to your own file directory
    The follwing is just an example.
    '''
    # total_page=10:
    # header_attempts=3: the total number of fake-IP attempts to reach for a page
    # request_attempts=1: the total number of request if got denied from the web server for each header_attempts
    # Therefore, in total there are maximm header_attempts * request_attempts to retrieve contents
    # There is a dramatic performance impact when you try larger header_attempts or request_attempts
    my_review = Review_file_io()
    my_review.get_product_reviews(
        './Dataset/Sneha/xab', './Dataset/Yong/review_Sheha.csv', './Dataset/Yong/empty_link_Shena.csv',
        total_page=999, header_attempts=3, request_attempts=1)
