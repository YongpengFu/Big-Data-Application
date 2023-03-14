import multiprocessing
from multiprocessing import Pool
from get_review import get_single_product_reviews
import re

if __name__ == '__main__':
    # define a funciton to get all the links from the link.csv file
    def get_review_link(file_loc):
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
    review_links = get_review_link("../../Dataset/links2.csv")
    # print(review_links)
    # Set up multiprocessing pool as follows.
    # I am using multi-processing technique to do the following tasks.
    # The reason is because each process is independent, we dont need to share same memory locaiton for each process.
    pool = Pool(processes=multiprocessing.cpu_count())
    # NOTE, I am using starmap because I need to pass multiple arguments https://superfastpython.com/multiprocessing-pool-map-multiple-arguments/
    args = [(link, "../../Dataset/Yong/review2.csv", "../../Dataset/Yong/empty_link2.csv")
            for link in review_links.values()]
    results = pool.starmap(get_single_product_reviews, args)
    pool.close()

    '''
    ./Dataset/Sample_link.csv: the file location contains the entrance link for product item review;
    ./Dataset/review.csv: the file location that will output all the reviews for a particular product item;
    ./Dataset/empty_link.csv: the file location that will output all the page information if we cannot reach them
    '''

    '''
    Chnage the ./Dataset/Sample_link.csv, ./Dataset/review.csv and ./Dataset/empty_link.csv to your own file directory
    The follwing is just an example.
    '''
    # total_page=200: this is total pages it will look for reviews
    # header_attempts=3: the total number of fake-IP attempts to reach for a page
    # request_attempts=1: the total number of request if got denied from the web server for each header_attempts
    # Therefore, in total there are maximm header_attempts * request_attempts to retrieve contents
    # There is a dramatic performance impact when you try larger header_attempts or request_attempts
    # args = ['./Dataset/links2.csv', './Dataset/Yong/review2.csv',
    #         './Dataset/Yong/empty_link2.csv', 200, 3, 1]
    # my_review = Review_file_io()
    # my_review.get_product_reviews(
    #     './Dataset/Sample_link.csv', './Dataset/Yong/review_Yong.csv', './Dataset/Yong/empty_link_Yong.csv',
    #     total_page=200, header_attempts=3, request_attempts=1)
    # print("web search start")
    # results = pool.starmap(my_review.get_product_reviews, args)
    # pool.close()
    # print("web search end")
