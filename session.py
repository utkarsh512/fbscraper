"""session.py - Creating a session for scraping posts, comments and replies from public Facebook pages
Copyright (c) 2021 Utkarsh Patel
"""

import time
import numpy as np
import json
import pickle as pkl
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs

BASE_URL = "https://facebook.com"
W3_BASE_URL = "https://www.facebook.com"
MOBILE_URL = "https://mobile.facebook.com"
MBASIC_URL = "https://mbasic.facebook.com"

def delay():
    """delay for 5-15 seconds"""
    time.sleep(np.random.randint(5, 15))

class LoginError(Exception):
    """raised when facebook login is unsuccessful"""
    pass

class URLError(Exception):
    """raised when an invalid URL is given to scrape"""
    pass

class Session:
    def __init__(self,
                 credentials,
                 chromeDriverPath="chromedriver"):
        """Routine to inititialize a session
        ------------------------------------
        Input:
        :param credentials: (email, password) tuple for Facebook login
        :param chromeDriverPath: path to chromedriver
        """
        self._credentials = credentials
        self._kwargs = dict()
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-dev-shm-usage')
        self._browser = webdriver.Chrome(executable_path=chromeDriverPath, options=option)
        self._login()

    def _login(self):
        """routine to login to Facebook using passed credentials
        --------------------------------------------------------
        raises LoginError in case login is unsuccessful
        """
        try:
            self._browser.get(BASE_URL)
            self._browser.maximize_window()
            self._browser.find_element(By.NAME, "email").send_keys(self._credentials[0])
            self._browser.find_element(By.NAME, "pass").send_keys(self._credentials[1])
            self._browser.find_element(By.NAME, "login").click()
            print("Successfully logged in!")
            delay()
        except:
            raise LoginError("Login unsuccessful")

    def _scroll(self,
                nScrolls):
        """routine to scroll through the Facebook page
        ----------------------------------------------
        Input:
        nScrolls: number of times to scroll
        """
        for i in tqdm(range(nScrolls), desc="Scrolling"):
            self._browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")
            delay()

    def getPostURLs(self,
                    pageID,
                    nScrolls):
        """routine to extract the post urls from a given page
        -----------------------------------------------------
        Input:
        :param pageID: unique ID of the page
        :param nPosts: number of post for which URL is required

        Output:
        returns a list containing the URLs
        """
        pageURL = f"{MOBILE_URL}/{pageID}"
        self._browser.get(pageURL)
        self._scroll(nScrolls)
        soup = bs(self._browser.page_source, "html.parser")
        linkElements = soup.findAll("a")
        rawLinks = list()
        for i in range(len(linkElements)):
            try:
                link = linkElements[i]["href"]
                rawLinks.append(link)
            except:
                pass
        linkFilter = """/story.php?"""
        filteredLinks = list()
        for link in rawLinks:
            if link.startswith(linkFilter):
                filteredLinks.append(link)
        postURLs = list()
        for i in range(len(filteredLinks) // 4):
            postURLs.append(f"{MBASIC_URL}{filteredLinks[4 * i + 1]}")
        return postURLs

    def _parsePage(self):
        """routine to parse the page metadata and return it as a dictionary"""
        soup = bs(self._browser.page_source, "lxml")
        metadata = str(soup.find("script"))
        idx = 0
        while metadata[idx] != "{":
            idx += 1
        metadata = metadata[idx:-9]
        return json.loads(metadata)

    def _parsePost(self,
                   metadata):
        """routine to parse metadata of a given post from the metadata dictionary
        -------------------------------------------------------------------------
        Input:
        :param metadata: dictionary as returned by self._parsePage() method
        """
        self._kwargs["post"]["time"] = metadata["dateCreated"]
        self._kwargs["post"]["text"] = metadata["articleBody"]
        self._kwargs["post"]["url"] = metadata["url"]
        stats = dict()
        stats["likeCount"] = metadata["interactionStatistic"][1]["userInteractionCount"]
        stats["commentCount"] = metadata["interactionStatistic"][0]["userInteractionCount"]
        stats["shareCount"] = metadata["interactionStatistic"][2]["userInteractionCount"]
        self._kwargs["post"]["userInteractionCount"] = stats
        self._kwargs["post"]["author"] = metadata["author"]
        self._kwargs["post"]["comments"] = list()
        self._kwargs["post"]["commentCount"] = metadata["commentCount"]
        self._kwargs["post"]["identifier"] = metadata["identifier"]

    def _getNext(self):
        """routine to extract the link to more comments"""
        soup = bs(self._browser.page_source, "lxml")
        element = soup.find("div", id=f"see_next_{self.posts[-1]['identifier'].split(';')[1]}")
        nextLink = None
        if element is not None:
            nextLink = f"{MBASIC_URL}{element.a['href']}"
        return nextLink

    def _extract(self,
                 postURL):
        """routine to iteratively extract post comments
        -----------------------------------------------
        Input:
        :param postURL: URL of the post
        """
        self._browser.get(postURL)
        delay()
        metadata = self._parsePage()
        nCommentsRequired = self._kwargs["nComments"] - len(self._kwargs["post"]["comments"])
        nCommentsRequired = min(nCommentsRequired, len(metadata["comment"]))
        self._kwargs["post"]["comments"].extend(metadata["comment"][:nCommentsRequired])
        self._kwargs["pbar"].update(nCommentsRequired)
        if self._kwargs["nComments"] == len(self._kwargs["post"]["comments"]):
            return
        nextLink = self._getNext()
        if nextLink is not None:
            self._extract(nextLink)
        
    def getPost(self,
                postURL,
                dumpAs,
                nComments=10**10):
        """routine to scrape a post
        ---------------------------
        Input:
        :param postURL: URL of the post
        :param dumpAs: pickled file to dump to
        :param nComments: upper bound on number of comments
        """
        if not postURL.startswith(MBASIC_URL):
            raise URLError(f"Post URL must start with {MBASIC_URL}")
        self._kwargs["nComments"] = nComments
        self._browser.get(postURL)
        delay()
        metadata = self._parsePage()
        self._kwargs["post"] = dict()
        self._parsePost(metadata)
        self._kwargs["nComments"] = min(self._kwargs["nComments"], self._kwargs["post"]["commentCount"])
        with tqdm(total=self._kwargs["nComments"], desc="Comments") as self._kwargs["pbar"]:
            self._extract(postURL)
        with open(dumpAs, "ab") as f:
            pkl.dump(self._kwargs["post"], f)

    def close(self):
        """Routine to close the session"""
        self._browser.close()
 
