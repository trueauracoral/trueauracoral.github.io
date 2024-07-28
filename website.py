#!/usr/bin/env python
import os
import time
from urllib.parse import urljoin
import datetime
from dateutil.relativedelta import relativedelta
from orgpython import to_html
import json
from bs4 import BeautifulSoup
from xml.dom import minidom 

websiteTitle = "ZortaZert"
websiteUrl = "https://trueauracoral.github.io"
articlesDir = os.path.join(os.getcwd(), "blog/org")
articlesWebDir = "./blog/org/"
blogDir = os.path.join(os.getcwd(), "blog")
markup = "org"
exportAll = True
dateformat = "%y-%m-%d"

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

with open("top.html", "r") as file:
    topHTML = file.read()

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
    #BLOG!!
    # Gather info from files
    for article in articles:
        path = os.path.join(articlesDir, article)
        date = fileGetDate(article)
        with open(path, "r") as file:
            articleText = file.read()
            title = ' '.join(articleText.splitlines()[0].split(" ")[1:])

        blogData.append({
            "file": path,
            "title": title,
            "url": urljoin("./blog", article.replace(date+'-','').replace("org", "html")),
            "date": datetime.datetime.fromtimestamp(strToDatetime(date)),
            "dateStr": date
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
    with open(blogPage, "w", encoding="utf-8") as file:
        file.write(htmlify(blogHTML))
    
    ## Create RSS for blog
    rss = minidom.Document()
    print(rss.getElementsByTagName("xml"))
    rssElement = rss.createElement('rss')
    rssElement.setAttribute('version', '2.0')
    rss.appendChild(rssElement)
    channel = rss.createElement('channel')
    rssElement.appendChild(channel)
    title = rss.createElement('title')
    title.appendChild(rss.createTextNode(websiteTitle))
    channel.appendChild(title)
    language = rss.createElement('language')
    language.appendChild(rss.createTextNode("en-us"))
    channel.appendChild(language)
    link = rss.createElement('link')
    link.appendChild(rss.createTextNode(urljoin(websiteUrl, "rss.xml")))
    channel.appendChild(link)
    
    #atomLink = rss.createElement('atom:link')
    #atomLink.setAttribute('href', 'https://monstro1.com/rss.xml')
    #atomLink.setAttribute('rel', 'self')
    #atomLink.setAttribute('type', 'application/rss+xml')
    #channel.appendChild(atomLink)
    
    image = rss.createElement('image')
    channel.appendChild(image)
    imageTitle = rss.createElement('title')
    imageTitle.appendChild(rss.createTextNode(f"{websiteTitle}'s Title"))
    image.appendChild(imageTitle)    
    imageUrl = rss.createElement('url')
    imageUrl.appendChild(rss.createTextNode(urljoin(websiteTitle, "/img/icons/chadoku.ico")))
    image.appendChild(imageUrl)    
    imageLink = rss.createElement('link')
    imageLink.appendChild(rss.createTextNode(urljoin(websiteUrl, "rss.xml")))
    image.appendChild(imageLink)

    for article in blogData:
        item = rss.createElement('item')
        channel.appendChild(item)
        itemTitle = rss.createElement('title')
        itemTitle.appendChild(rss.createTextNode(article['title']))
        item.appendChild(itemTitle)
        guid = rss.createElement('guid')
        guid.appendChild(rss.createTextNode(article['url']))
        item.appendChild(guid)
        itemLink = rss.createElement('link')
        itemLink.appendChild(rss.createTextNode(urljoin(websiteUrl, f"/blog/{article['url']}")))
        item.appendChild(itemLink)
        pubDate = rss.createElement('pubDate')
        pubDate.appendChild(rss.createTextNode(article['date'].strftime("%a, %d %b %Y %H:%M:%S %z")))
        item.appendChild(pubDate)
        author = rss.createElement('author')
        author.appendChild(rss.createTextNode(websiteTitle))
        item.appendChild(author)
        
        with open(article['file'], 'r', encoding="utf-8") as file:
            articleText = file.read()
            articleText = to_html(articleText, toc=False, offset=0, highlight=True).replace('\n','')

        description = rss.createElement('description')
        description.appendChild(rss.createTextNode(articleText))
        item.appendChild(description)
    
    xml_str = rss.toprettyxml(indent ="  ")  
    #print(xml_str)

    with open("rss.xml", "w", encoding="utf-8") as f: 
        f.write(xml_str) 
        print("Exported: rss.xml")

    print(blogData)
    
if __name__ == "__main__":
    main()