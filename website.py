#!/usr/bin/env python
import os
import time
from urllib.parse import urljoin
import datetime
from dateutil.relativedelta import relativedelta

articlesDir = os.path.join(os.getcwd(), "blog/org")
articlesWebDir = "./blog/org/"
blogDir = os.path.join(os.getcwd(), "blog")
markup = "org"
exportAll = False

currentDate = datetime.datetime.now()

#https://stackoverflow.com/a/168580/24903843
def getfiles(dirpath):
    a = [s for s in os.listdir(dirpath)
         if os.path.isfile(os.path.join(dirpath, s))]
    a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))
    return a

articles = getfiles(articlesDir)
blogData = []

with open("top.html", "r") as file:
    topHTML = file.read()

with open("bottom.html", "r") as file:
    bottomHTML = "\n" + file.read()

def htmlify(middleStuff):
    data = ""
    data += topHTML
    data += middleStuff
    data += bottomHTML
    return data

def main():
    # MAIN PAGE Circle Navigation Bar

    #BLOG!!

    # Gather info from files
    for article in articles:
        path = os.path.join(articlesDir, article)
        date = os.path.getmtime(path)

        blogData.append({
            "file": path,
            "title": article.title().replace(".Org", "").replace("-"," "),
            "url": urljoin("./blog", article.replace("org", "html")),
            "date": datetime.datetime.fromtimestamp(date)
        })

    # Export the Org documents with pandoc
    def exporter(file, export):
        command = f'pandoc -s -c {os.path.join(articlesDir, "index.css")} {file} -o {export}.html --highlight-style=tango'
        print(command)
        print(f"Exported: {file}")
        os.system(command)
    for i, file in enumerate(blogData):
        file = blogData[i]["file"]
        export = str(file).replace(f".{markup}","").replace(f"{markup}\\","").replace(f"{markup}/","")
        fileDate = datetime.datetime.fromtimestamp(os.path.getmtime(file))
        lastModified = (currentDate - fileDate).days
        if exportAll:
            exporter(file, export)
        elif lastModified < 30:
            exporter(file, export)
    
    # Blog.html
    blogHTML = "<ul>"
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
            lastYear = year
        if year != lastYear:
            blogHTML += f"\n<h2>{year}</h2>"
            lastYear = year
            count = 0
        count = count + 1
        blogHTML += f"\n<li><a href='{blogData[i]['url']}'>{blogData[i]['title']}</a></li>"
    blogHTML += "\n</ul>"

    blogPage = os.path.join(blogDir, "index.html")
    with open(blogPage, "w") as file:
        file.write(htmlify(blogHTML))

    print(blogData)
    
if __name__ == "__main__":
    main()