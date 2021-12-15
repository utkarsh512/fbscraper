# FacebookScraper
Scraping posts and comments from Facebook using selenium and beautifulsoup.
## How to use
First of all, create a `Session` object for scraping:
```python3
from fbscraper import Session
sess = Session(
    credentials=(EMAIL, 
                 PASSWORD), 
    chromeDriverPath="chromedriver"
)
```
where `(EMAIL, PASSWORD)` are your facebook credentials and `chromeDriverPath` is the path to the chromedriver.

Then, you can extract recent post URLs of a public pages as
```python3
postURLs = sess.getPostURLs(
    pageID="nytimes", 
    nScrolls=10
)
```
where `pageID` is the unique Facebook ID of the page and `nScrolls` is number of scrolls (as viewed in FB mobile app) upto which posts are to be extracted. The above function will return a list of URLs `postURLs`.

As you now have the list of URLs for the required posts, post data (including comments) can be scraped as
```python3
sess.getPost(
    postURL="https://mbasic.facebook.com/story.php?...",
    dumpAs="posts.pkl",
    nComments=1000
)
```
where `postURL` is URL of the post we are interested in, `dumpAs` is the name of binary file to which we are __appending__ this post and `nComments` is the upper-bound on number of comments. Just make sure postURL starts with `https://mbasic.facebook.com` instead of `https://www.facebook.com`, `https://mobile.facebook.com`, etc.

## TO-DO
* Extracting replies along with comments
