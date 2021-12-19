"""main.py - Scraping Facebook Data
Author: Utkarsh Patel

Run this file as
$ python main.py -e EMAIL -p PASSWORD -x chromeDriverPath -i DonaldTrump -s 100 -d posts.pkl -g true
                 [-c 1000] [-r 1000] [-j false]
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                      optional arguments
"""

from scraper import Session
from utils import PKLtoJSON
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email", type=str, required=True, help="email address/phone number for login")
    parser.add_argument("-p", "--password", type=str, required=True, help="password for login")
    parser.add_argument("-x", "--chromeDriver", type=str, required=True, help="path to chromedriver")
    parser.add_argument("-i", "--pageID", type=str, required=True, help="page ID to be scraped")
    parser.add_argument("-s", "--nScrolls", type=int, required=True, help="number of scrolls required")
    parser.add_argument("-d", "--dump", type=str, required=True, help="file to dump the data")
    parser.add_argument("-g", "--getReplies", type=bool, default=False, help="replies to be scraped?")
    parser.add_argument("-c", "--nComments", type=int, default=10**10, help="number of comments to be scraped")
    parser.add_argument("-r", "--nReplies", type=int, default=10**10, help="number of replies to be scraped")
    parser.add_argument("-j", "--json", type=bool, default=False, help="want dataset in JSON?")
    args = parser.parse_args()

    sess = Session(
        credentials=(args.email, args.password),
        chromeDriverPath=args.chromeDriver
    )
    postURLs = sess.getPostURLs(
        pageID=args.pageID,
        nScrolls=args.nScrolls
    )
    for i, postURL in enumerate(postURLs):
        print(f"Scraping post {i + 1} of {len(postURLs)}")
        try:
            sess.getPost(
                postURL=postURL,
                dumpAs=args.dump,
                nComments=args.nComments,
                getReplies=args.getReplies,
                nReplies=args.nReplies
            )
        except Exception as e:
            print(f"Error: {e}")
    sess.close()
    if args.json:
        PKLtoJSON(args.dump, args.dump.replace("pkl", "json"))

if __name__ == "__main__":
    main()
