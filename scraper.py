"""scraper.py - Scraping posts, comments and replies from public Facebook pages
Copyright (c) 2021 Utkarsh Patel
"""

import pickle as pkl
from copy import deepcopy
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from utils import (delay, parsePageScript, parsePostMetadata, parseComment, parseReply,
                   getLinks, getMoreCommentsLink, getMoreRepliesLink, getDivClass, getFilteredDivs)
from exceptions import (LoginError,
                        URLError,
                        BadPostError,
                        SourceError,
                        NoSuchElementException)
from constants import (BASE_URL,
                       MOBILE_URL,
                       MBASIC_URL,
                       ISSUE_URL)

class Session:
    def __init__(self,
                 credentials,
                 chromeDriverPath="chromedriver"):
        """object constructor
        ---------------------
        Input:
        :param credentials: (email, password) tuple for Facebook login
        :param chromeDriverPath: path to chromedriver
        """
        self._credentials = credentials
        self._data = dict()
        option = webdriver.ChromeOptions()
        # option.add_argument("--headless")
        option.add_argument("--no-sandbox")
        option.add_argument("--disable-dev-shm-usage")
        option.add_argument("--disable-gpu")
        option.add_argument("--disable-crash-reporter")
        option.add_argument("--disable-extensions")
        option.add_argument("--disable-in-process-stack-traces")
        option.add_argument("--disable-logging")
        option.add_argument("--log-level=3")
        self._browser = webdriver.Chrome(executable_path=chromeDriverPath, options=option)
        self._login()

    def __del__(self):
        """object destructor"""
        self._browser.close()

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
            delay()
            soup = bs(self._browser.page_source, "lxml")
            title = soup.find("title").text.lower().split()
            if "log" in title:
                raise LoginError("Login unsuccessful! Please check the credentials.")
        except NoSuchElementException:
            raise SourceError(f"Login page decoding is outdated!\nPlease create an issue at {ISSUE_URL}")

    def getPage(self,
                pageID):
        """routine to open a Facebook page
        ----------------------------------
        :param pageID: Facebook id of the page
        """
        pageURL = f"{MOBILE_URL}/{pageID}"
        self._browser.get(pageURL)

    def scroll(self,
               nScrolls):
        """routine to scroll through the Facebook page
        ----------------------------------------------
        Input:
        nScrolls: number of times to scroll
        """
        try:
            for i in tqdm(range(nScrolls), desc="Scrolling"):
                self._browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                delay()
        except Exception as e:
            print(f"Scrolling stopped! {e}")

    def getPostURLs(self):
        """routine to extract the post urls from a given page
        -----------------------------------------------------
        Output:
        returns a list containing the URLs
        """
        soup = bs(self._browser.page_source, "html.parser")
        links = getLinks(soup, filter="""/story.php?""")
        postURLs = list()
        for i in range(len(links) // 4):
            postURLs.append(f"{MBASIC_URL}{links[4 * i + 1]}")
        return postURLs

    def _getComments(self,
                     postURL):
        """routine to extract post comments recursively
        -----------------------------------------------
        Input:
        :param postURL: URL of the post
        """
        self._browser.get(postURL)
        delay()
        soup = bs(self._browser.page_source, "lxml")
        commentClass = getDivClass(soup)
        divs = getFilteredDivs(soup.findAll("div", class_=commentClass))
        batch = list()
        for div in divs:
            comment = parseComment(div, self._data["postID"])
            batch.append(comment)
        nCommentsRequired = self._data["nComments"] - len(self._data["post"]["comments"])
        nCommentsRequired = min(nCommentsRequired, len(batch))
        if nCommentsRequired == 0:
            return
        self._data["post"]["comments"].extend(batch[:nCommentsRequired])
        self._data["progressBar"].update(nCommentsRequired)
        nextLink = getMoreCommentsLink(soup, self._data["postID"])
        if nextLink is not None:
            try:
                self._getComments(nextLink)
            except:
                pass

    def _getReplies(self,
                    url):
        """routine to extract reples to the comments recursively
        --------------------------------------------------------
        Input:
        :param url: URL of the replies
        """
        self._browser.get(url)
        delay()
        soup = bs(self._browser.page_source, "lxml")
        replyClass = getDivClass(soup)
        divs = getFilteredDivs(soup.findAll("div", class_=replyClass))
        batch = list()
        for div in divs:
            reply = parseReply(div)
            batch.append(reply)
        nRepliesRequired = self._data["nReplies"] - len(self._data["current"])
        nRepliesRequired = min(nRepliesRequired, len(batch))
        if nRepliesRequired == 0:
            return
        self._data["current"].extend(batch[:nRepliesRequired])
        nextLink = getMoreRepliesLink(soup, self._data["commentID"])
        if nextLink is not None:
            try:
                self._getReplies(nextLink)
            except:
                pass

    def getPost(self,
                postURL,
                dumpAs,
                getReplies=False,
                nComments=10**10,
                nReplies=10**10):
        """routine to scrape a post
        ---------------------------
        Input:
        :param postURL: URL of the post
        :param dumpAs: pickled file to dump to
        :param nComments: upper bound on number of comment to a post
        :param getReplies: if True, replies to comments will also be scraped
        :param nReplies: upper bound on number of replies to a comment
        """
        if not postURL.startswith(MBASIC_URL):
            raise URLError(f"Post URL must start with {MBASIC_URL}")
        self._data["nComments"] = nComments
        self._browser.get(postURL)
        delay()
        soup = bs(self._browser.page_source, "lxml")
        try:
            metadata = parsePageScript(soup)
        except:
            raise BadPostError("Page source doesn't contain <script> element")
        self._data["post"] = parsePostMetadata(metadata)
        self._data["postID"] = self._data["post"]["identifier"].split(";")[1]
        self._data["nComments"] = min(self._data["nComments"], self._data["post"]["commentCount"])
        with tqdm(total=self._data["nComments"], desc="Comments") as self._data["progressBar"]:
            try:
                self._getComments(postURL)
            except:
                pass
        if getReplies:
            self._data["nReplies"] = nReplies
            for comment in tqdm(self._data["post"]["comments"], desc="Replies"):
                try:
                    self._data["current"] = list()
                    self._data["commentID"] = comment["identifier"]
                    self._getReplies(comment["repliesLink"])
                    comment["replies"] = deepcopy(self._data["current"])
                except:
                    comment["replies"] = []
        with open(dumpAs, "ab") as f:
            pkl.dump(self._data["post"], f)
