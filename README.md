# fbscraper
Scraping posts, comments and replies from Facebook.
## Installing
```bash
$ git clone https://github.com/utkarsh512/fbscraper.git
$ cd fbscraper
$ pip install . -r requirements.txt
```
## How to use

### Creating a session

Create a `Session` object for scraping:
```python3
from fbscraper import Session
sess = Session(
    credentials=(EMAIL, 
                 PASSWORD), 
    chromeDriverPath="chromedriver"
)
```
where `(EMAIL, PASSWORD)` are your facebook credentials and `chromeDriverPath` is the path to the chromedriver.

### Fetching post URLs from the public pages

Then, you can extract recent post URLs of a public pages as
```python3
sess.getPage("nytimes")
sess.scroll(10)
postURLs = sess.getPostURLs()
```

### Scraping posts using the fetched URLs

As you now have the list of URLs for the required posts, post data (including comments) can be scraped as
```python3
sess.getPost(
    postURL="https://mbasic.facebook.com/story.php?...",
    dump="posts.pkl",
    getComments=True,
    getReplies=True,
    nComments=1000,
    nReplies=10
)
```
where 
* `postURL` is the URL of the post
* `dump` is the name of binary file used for dumping the post data
* `getComments` should be `True` if you want to scrape comments to the post as well
* `getReplies` should be `True` if you want to scrape replies to the comments as well
* `nComments` is the upper-bound on number of comments per post
* `nReplies` is the upper-bound on number of replies per comment

__Note__: Just make sure `postURL` starts with `https://mbasic.facebook.com` instead of `https://www.facebook.com`, `https://mobile.facebook.com`, etc.
