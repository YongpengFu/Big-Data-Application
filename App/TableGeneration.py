from DBConnection import Database
from datetime import datetime
import pandas as pd

def readDataFromFile():
    productReviewData = pd.read_parquet('AmazonReviews.parquet', engine='fastparquet')

    reviewSummaryData = pd.read_parquet('AmazonReviewsSummarize.parquet', engine='fastparquet')
    reviewSummaryData=reviewSummaryData.drop(columns=['Review Body'])

    productPriceData = pd.read_csv('AmazonProductPrice.csv')

    productName = productReviewData[['ASIN', 'product Name']].drop_duplicates() #.groupby(['ASIN', 'product Name']).nunique()

    dfTemp = pd.merge(productPriceData, reviewSummaryData, how='left', on = 'ASIN')
    productData = pd.merge(dfTemp, productName, how='left', on = 'ASIN')

    productData[['Price', '#Ratings']] = productData[['Price', '#Ratings']].fillna(0)
    productData[['product Name', 'top 5']] = productData[['product Name', 'top 5']].fillna('')

    productReviewData[['Review Rating']] = productReviewData[['Review Rating']].fillna(0)
    productReviewData[['product Name', 'Review Title', 'Review Body', 'Review Date']] = productReviewData[['product Name', 'Review Title', 'Review Body', 'Review Date']].fillna('')

    return productData.drop_duplicates(subset=["ASIN"], keep='first'), productReviewData.drop_duplicates()

def createDBTables():
    with Database() as db:
        sql = "CREATE TABLE Product ( ASIN VARCHAR(50) PRIMARY KEY, Name VARCHAR(150), Summary VARCHAR(255), Url VARCHAR(255), Price DECIMAL(5,2),  NumOfRating INT)"
        db.execute(sql)

        sql = "CREATE TABLE Review (ReviewID CHAR(38) PRIMARY KEY DEFAULT (UUID()), ASIN VARCHAR(50), Title VARCHAR(150), Rating INT, Detail TEXT, Date Date, Location VARCHAR(100), FOREIGN KEY (ASIN) REFERENCES Product(ASIN))"
        db.execute(sql)

def insertDataIntoProductDB(dataFrame):
    with Database() as db:

        for index, row in dataFrame.iterrows():
            
            print(index)

            val = (row['ASIN'], row['product Name'], row['top 5'], row['URLs'], row['Price'], row['#Ratings']) 
            sql = "INSERT INTO Product (ASIN, Name, Summary, Url, Price, NumOfRating) VALUES (%s, %s, %s, %s, %s, %s)"   

            db.execute(sql, val)

def insertDataIntoReviewDB(dataFrame):

    with Database() as db:

        for index, row in dataFrame.iterrows():

            print(index)

            if len(row['ASIN']) != 10:
                continue

            reviewDate, reviewLocation = extracDateAndLocation(row['Review Date'])

            val = (row['ASIN'], row['Review Title'], row['Review Rating'], row['Review Body'], reviewDate, reviewLocation) 
            sql = "INSERT INTO Review (ASIN, Title, Rating, Detail, Date, Location) VALUES (%s, %s, %s, %s, %s, %s)"        

            db.execute(sql, val)

def extracDateAndLocation(dateString):

    locationStartString = "in the "
    locationEndString = " on "

    locationStartIndex = dateString.find(locationStartString) + len(locationStartString)
    locationEndIndex = dateString.find(locationEndString)

    if locationStartIndex ==  len(locationStartString) - 1:
        location = ""
    else:
        location = ''.join(x for x in dateString[locationStartIndex:locationEndIndex] if (x.isalpha() or x == ' '))

    dateStartIndex = locationEndIndex + len(locationEndString)

    dateText = dateString[dateStartIndex:]

    while dateText[-1].isalpha(): 
        dateText = dateText[:-1]

    if locationEndIndex == -1:
        date = datetime(1900, 1, 1)
    else:
        date = datetime.strptime(dateText, '%d %B %Y').date()

    return date, location

if __name__ == '__main__':
    productDF, productReviewDF = readDataFromFile()    
    
    # createDBTables()
    # insertDataIntoProductDB(productDF)
    # insertDataIntoReviewDB(productReviewDF)