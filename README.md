# fbscraper
Scraping posts, comments and replies from Facebook using selenium and beautifulsoup.
## Requirements
* `bs4`
* `selenium`
* `cssutils`
## How to use
First of all, create a `Session` object for scraping:
```python3
from scraper import Session
sess = Session(
    credentials=(EMAIL, 
                 PASSWORD), 
    chromeDriverPath="chromedriver"
)
```
where `(EMAIL, PASSWORD)` are your facebook credentials and `chromeDriverPath` is the path to the chromedriver.

Then, you can extract recent post URLs of a public pages as
```python3
sess.getPage("nytimes")
sess.scroll(10)
postURLs = sess.getPostURLs()
```

As you now have the list of URLs for the required posts, post data (including comments) can be scraped as
```python3
sess.getPost(
    postURL="https://mbasic.facebook.com/story.php?...",
    dumpAs="posts.pkl",
    getComments=True,
    getReplies=True,
    nComments=1000,
    nReplies=10
)
```
where 
* `postURL` is the URL of the post
* `dumpAs` is the name of binary file used for appending the post
* `nComments` is the upper-bound on number of comments per post
* `getReplies` should be `True` if you want to scrape replies as well
* `nReplies` is the upper-bound on number of replies per comment

Just make sure postURL starts with `https://mbasic.facebook.com` instead of `https://www.facebook.com`, `https://mobile.facebook.com`, etc.

## Sample Output
Following data was scraped from The New York's Time (`nytimes`) Facebook page.
```json
[
    {
        "time": "2021-12-15T05:40:05-0800",
        "text": "The economic situation in Afghanistan is dire, prompting the UN to warn that the country is at risk of a \u201ctotal breakdown.\u201d\n\nWhat does the crisis look like on the ground? Listen to today\u2019s episode of The Daily.",
        "url": "https://www.facebook.com/story.php?story_fbid=10152837809989999&id=5281959998",
        "likeCount": 25,
        "commentCount": 13,
        "shareCount": 3,
        "author": {
            "@type": "Organization",
            "name": "The New York Times",
            "identifier": 5281959998,
            "url": "https://www.facebook.com/nytimes/",
            "image": null,
            "sameAs": "nytimes.com/chat",
            "foundingDate": "2007-10-29T16:03:34-0700"
        },
        "identifier": "5281959998;10152837809989999;;9",
        "comments": [
            {
                "author": {
                    "name": "Dembele Ndaou",
                    "url": "https://www.facebook.com/dembele.ndaou?rc=p&refid=52&__tn__=R"
                },
                "text": "And US is accountable of what s going on there these days.Taliban inherit a country already destroyed.That's bad.",
                "identifier": "10152837809989999_10152837816429999",
                "replies": [],
                "repliesLink": null
            },
            {
                "author": {
                    "name": "Carlos Alberto Lobe",
                    "url": "https://www.facebook.com/carlos.a.lobe?rc=p&refid=52&__tn__=R"
                },
                "text": "America's success is dependent on the evil it imposes on the world.",
                "identifier": "10152837809989999_10152837817634999",
                "replies": [],
                "repliesLink": null
            },
            {
                "author": {
                    "name": "Dany Nelthomasson",
                    "url": "https://www.facebook.com/profile.php?id=100072333914191&rc=p&refid=52&__tn__=R"
                },
                "text": "Honor is a word that is out of fashion nowadays.",
                "identifier": "10152837809989999_10152837811559999",
                "replies": [],
                "repliesLink": null
            },
            {
                "author": {
                    "name": "Jayson Southmayd",
                    "url": "https://www.facebook.com/jayson.southmayd?rc=p&refid=52&__tn__=R"
                },
                "text": "Don\u2019t worry Brandon will save you!! He loves the Taliban \ud83d\ude4a\ud83d\ude49\ud83d\ude48",
                "identifier": "10152837809989999_10152837811554999",
                "replies": [],
                "repliesLink": null
            },
            {
                "author": {
                    "name": "Chris Peacock",
                    "url": "https://www.facebook.com/hiredhand?rc=p&refid=52&__tn__=R"
                },
                "text": "Why should they care, god is merciful he will provide.",
                "identifier": "10152837809989999_10152837811234999",
                "replies": [
                    {
                        "author": {
                            "name": "Abigail Mensah",
                            "url": "https://www.facebook.com/abigastyhauston.jacksonsmith?rc=p&__tn__=R"
                        },
                        "text": "Chris Peacock pity em huh"
                    },
                    {
                        "author": {
                            "name": "Pererro Velatus",
                            "url": "https://www.facebook.com/profile.php?id=100076258682710&rc=p&__tn__=R"
                        },
                        "text": "Chris Peacock  - I\u2019m confused if god provides then why didn\u2019t he provide during all the other genocides ?"
                    },
                    {
                        "author": {
                            "name": "Matthew Pinto",
                            "url": "https://www.facebook.com/matthew.pinto.75?rc=p&__tn__=R"
                        },
                        "text": "Chris Peacock God has no hands but ours!"
                    }
                ],
                "repliesLink": "https://mbasic.facebook.com/comment/replies/?ctoken=10152837809989999_10152837811234999&count=3&curr&pc=1&ft_ent_identifier=10152837809989999&gfid=AQD3PaoDMcDk82ErDXk&refid=52&__tn__=R"
            }
        ]
    }
]
```
