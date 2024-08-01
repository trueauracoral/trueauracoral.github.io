#!/usr/bin/env python
import os
import time
from urllib.parse import urljoin
import datetime
from dateutil.relativedelta import relativedelta
from orgpython import to_html
import json
from bs4 import BeautifulSoup
from rssGenerator import rss_generator
from config import *
import re

currentDate = datetime.datetime.now()

def fileGetDate(filename):
    return "-".join(filename.split("-")[:3])
def strToDatetime(articleDate):
    return datetime.datetime.strptime(articleDate, dateformat).timestamp()

#https://stackoverflow.com/a/168580/24903843
def getfiles(dirpath):
    a = [s for s in os.listdir(dirpath)
         if os.path.isfile(os.path.join(dirpath, s))]
    a.sort(key=lambda s: strToDatetime(fileGetDate(s)))
    return a

articles = getfiles(articlesDir)
blogData = []

topHTML = ""
with open("top.html", "r", encoding="utf-8") as file:
    topHTMLread = str(file.read())
topHTML = topHTMLread

with open("bottom.html", "r") as file:
    bottomHTML = "\n" + file.read()
    soup = BeautifulSoup(bottomHTML, "html.parser")

    genDateHTML = soup.find("p", {"id": "genDate"})
    genDateHTML.replace_with(f"Last generated: {currentDate}")

    copyrightHTML = soup.find("p", {"id": "copyright"})
    newCopyright = BeautifulSoup(f"© ZortaZert 2021-{currentDate.year}")
    copyrightHTML.replace_with(newCopyright.p)
    bottomHTML = soup.prettify()
    print(bottomHTML)

def htmlify(middleStuff):
    data = ""
    data += topHTML
    data += middleStuff
    data += bottomHTML
    return data

def main():
    global topHTML
    #BLOG!!
    # Gather info from files
    for article in articles:
        path = os.path.join(articlesDir, article)
        date = fileGetDate(article)
        with open(path, "r") as file:
            articleText = file.read()
            title = re.findall("(?<=\#\+TITLE: ).*", articleText)[0]
            tags = list(filter(None, re.findall("(?<=\#\+TAGS: ).*", articleText)[0].split(" ")))

        blogData.append({
            "file": path,
            "title": title,
            "url": urljoin("./blog", article.replace(date+'-','').replace("org", "html")),
            "date": datetime.datetime.fromtimestamp(strToDatetime(date)),
            "dateStr": date,
            "tags": tags
        })

    # Export the Org documents with org-python
    def exporter(file, export, write=False):
        #command = f'pandoc -s -c {os.path.join(articlesDir, "index.css")} {file} -o {export}.html --highlight-style=tango'
        #print(command)
        #os.system(command)
        with open(file, "r", encoding="utf8") as f:
            articleText = str(f.read())
        orgToHTML = to_html(articleText, toc=False, offset=0, highlight=True)
        if (write):
            return orgToHTML
        else:
            with open(export, "w", encoding="utf8") as f:
                f.write(htmlify(orgToHTML))

        print(f"Exported: {file}")

    def blogIndex(blogData):
        print(blogData)
        blogHTML = "<ul>\n"

        for i, article in enumerate(blogData):
            blogHTML += f"""\n<li><a href='{blogData[i]['url']}'>{blogData[i]['title']}</a> ({blogData[i]['date'].strftime("%B %d")})</li>"""
        blogHTML += "\n</ul>"
        return htmlify(blogHTML)

    for i, file in enumerate(blogData):
        file = blogData[i]["file"]
        date = blogData[i]["dateStr"]
        export = str(file).replace(f".{markup}",".html").replace(f"{markup}\\","").replace(f"{markup}/","").replace(date+'-',"")
        fileDate = datetime.datetime.fromtimestamp(os.path.getmtime(file))
        lastModified = (currentDate - fileDate).days
        if exportAll:
            exporter(file, export)
        elif lastModified < 30:
            exporter(file, export)
    
    # Blog homepage to access all the blogs
    blogHTML = ""
    blogData.reverse()

    count = 0
    lastYear = currentDate.year
    for i, article in enumerate(blogData):
        #print(currentDate)
        #print(article["date"])
        yearsAgo = int(relativedelta(currentDate, article["date"]).years)
        year = currentDate.year - yearsAgo
        if count == 0:
            blogHTML += f"\n<h2>{year}</h2>"
            blogHTML += "\n<ul>"
            lastYear = year
        if year != lastYear:
            blogHTML += "\n</ul>"
            blogHTML += f"\n<h2>{year}</h2>"
            blogHTML += "\n<ul>"
            lastYear = year
            count = 0
        count = count + 1
        blogHTML += f"""\n<li><a href='{blogData[i]['url']}'>{blogData[i]['title']}</a> ({blogData[i]['date'].strftime("%B %d")})</li>"""
    blogHTML += "\n</ul>"

    blogPage = os.path.join(blogDir, "index.html")
    
    ## Create RSS for blog
    rss_generator(blogData, currentDate)

    ## Create Tags for blog
    blogData.reverse()
    tags = []
    for article in blogData:
        tags += article['tags']
    tags = list(set(tags))
    print(tags)
    tags += ["all"]
    tagsDir = os.path.join(os.getcwd(), "tags")
    tagsHTML = "<div id='tagsList'>"
    for tag in tags:
        if tag == "all":
            tagURL = "/blog/index.html"
        else:
            tagURL = f"/tags/{tag}/index.html"
        tagsHTML += f"  <a href={tagURL}>{tag.title()}</a>"
    topHTML += tagsHTML + " </div>"
    for tag in tags:
        tagDir = os.path.join(tagsDir, tag)
        if os.path.isdir(tagDir) == False:
            os.mkdir(tagDir)
        tagArticles = []
        for i, article in enumerate(blogData):
            articleTags = article['tags']
            if tag in articleTags:
                tagArticles.append(blogData[i])
        with open(os.path.join(os.path.join(tagsDir, tag), "index.html"), "w", encoding="utf-8") as file:
            file.write(blogIndex(tagArticles))
    
    with open(blogPage, "w", encoding="utf-8") as file:
        file.write(htmlify(blogHTML))

if __name__ == "__main__":
    main()