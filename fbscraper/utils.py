"""
utils.py - Parsers for fbscraper
"""

import re
import time
import numpy as np
import urllib.parse
from tqdm import tqdm
import json
import cssutils
import pickle as pkl
from .constants import (W3_BASE_URL, MBASIC_URL)
import logging

cssutils.log.setLevel(logging.CRITICAL)

CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

def delay():
    """randomized delay"""
    time.sleep(np.random.randint(5, 15))

def PKLtoJSON(old,
              new):
    """routine to convert the pickled dataset (as used in scraper) to JSON
    ---------------------------------------------------------------------
    Input:
    :param old: path to PKL dataset
    :param new: path to JSON dataset
    """
    posts = list()
    with open(old, "rb") as reader:
        try:
            while True:
                posts.append(pkl.load(reader))
        except EOFError:
            pass
    with open(new, "w", encoding="utf-8") as writer:
        writer.write(json.dumps(posts, indent=4))

def getLinks(soup,
             filter=None):
    """routine to extract all hyperlinks from the given soup element with filtering"""
    linkElements = soup.findAll("a")
    rawLinks = list()
    for i in tqdm(range(len(linkElements)), desc='Extracting links'):
        try:
            link = linkElements[i]["href"]
            rawLinks.append(link)
        except:
            pass
    if filter is None:
        return rawLinks
    filteredLinks = list()
    for link in tqdm(rawLinks, desc='Filtering'):
        if link.startswith(filter):
            filteredLinks.append(link)
    return filteredLinks

def getMoreCommentsLink(soup,
                        postID):
    """routine to extract the 'more comments' link in the page
    returns None if it doesn't exists"""
    element = soup.find("div", id=f"see_next_{postID}")
    nextLink = None
    if element is not None:
        nextLink = f"{MBASIC_URL}{element.a['href']}"
    return nextLink

def getMoreRepliesLink(soup,
                       commentID):
    """routine to extract the 'more replies' link in the page
    return None if it doesn't exists"""
    element = soup.find("div", id=f"comment_replies_more_1:{commentID}")
    nextLink = None
    if element is not None:
        nextLink = f"{MBASIC_URL}{element.a['href']}"
    return nextLink

def getDivClass(soup):
    """routine to find the div class for comments/replies"""
    css = soup.find('style').text[32:-22]
    dct = parseCSS(css)
    candidates = list()
    for k, v in dct.items():
        if v == "padding: 4px":
            candidates.append(k)
    return candidates[-1][-2:]

def getFilteredDivs(divs):
    """routine to filter elements corresponding to a comment/reply"""
    filtered = list()
    for div in divs:
        if len(div.get("class")) == 1:
            filtered.append(div)
    return filtered

def getRepliesLink(div,
                   divID):
    """routine to get reply link a comment"""
    element = div.find("div", id=f"comment_replies_more_1:{divID}")
    repliesLink = None
    if element is not None:
        try:
            repliesLink = f"{MBASIC_URL}{element.div.a['href']}"
        except:
            pass
    return repliesLink

def parseLinks(links):
    """routine to extract unique post URLs"""
    postURLsDict = dict()
    for link in tqdm(links, desc="Parsing links"):
        params = urllib.parse.parse_qs(link[11:]) # removing /story.php?
        postURLsDict[(params["story_fbid"][0], params["id"][0])] = True
    postURLs = list()
    for key in tqdm(postURLsDict.keys(), desc="Preparing links"):
        postURLs.append(f"{MBASIC_URL}/story.php?story_fbid={key[0]}&id={key[1]}")
    return postURLs

def parsePageScript(soup):
    """routine to parse content of <script> tag"""
    metadata = str(soup.find("script"))
    idx = 0
    while metadata[idx] != "{":
        idx += 1
    metadata = metadata[idx:-9]
    return json.loads(metadata)

def parsePostMetadata(metadata):
    """routine to parse the metadata of the post"""
    return dict(
        time=metadata["dateCreated"],
        text=metadata["articleBody"],
        url=metadata["url"],
        likeCount=metadata["interactionStatistic"][1]["userInteractionCount"],
        commentCount=metadata["commentCount"],
        shareCount=metadata["interactionStatistic"][2]["userInteractionCount"],
        author=metadata["author"],
        identifier=metadata["identifier"],
        comments=[]
    )

def parseCSS(css):
    """routine to convert a CSS script to a dictionary"""
    dct = {}
    sheet = cssutils.parseString(css)
    for rule in sheet:
        try:
            selector = rule.selectorText
            styles = rule.style.cssText
            dct[selector] = styles
        except:
            pass
    return dct

def parseComment(div,
                 postID):
    """routine to parse a comment div
    ---------------------------------
    :param div: comment div
    :param postID: ID of the post of which div is a part
    """
    identifier = f"{postID}_{div.get('id')}"
    return dict(
        author=dict(
            name=re.sub(CLEANR, "", div.div.h3.text),
            url=f"{W3_BASE_URL}{div.div.h3.a['href']}"
        ),
        text=div.div.div.text,
        identifier=identifier,
        replies=[],
        repliesLink=getRepliesLink(div, identifier)
    )

def parseReply(div):
    """routine to parse a reply div
    -------------------------------
    :param div: reply div
    """
    return dict(
        author=dict(
            name=re.sub(CLEANR, "", div.div.h3.text),
            url=f"{W3_BASE_URL}{div.div.h3.a['href']}"
        ),
        text=div.div.div.text
    )
