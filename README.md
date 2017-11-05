# pharmaceutical-website-scraping

Scraping illness and related drug details from a pharmaceutical website.

Handles multi-level record collection by nesting Http requests and passing columns as intermediate meta parameters.

Custom middleware and spider settings are used to bypass captcha and IP blocks. Append respective code to each file. 

Second example deals with scraping ASP.NET pages where navigation uses HTTP POST form submission.


Setup code as:

$sudo su 

#scrapy startproject pharma2

#cd pharma2

#vi pharma2/spiders/pharma2_spider.py

#vi middlewares.py

#vi settings.py

Run in EC2 terminal as:

#scrapy crawl pharma2

#scrapy crawl pharma2 --set FEED_URI=output.csv --set FEED_FORMAT=csv	
