from xml.dom import minidom
import datetime
from urllib.parse import urljoin
from config import *
from orgpython import to_html

def rss_generator(blogData, currentDate):
    rss = minidom.Document()
    # print(rss.getElementsByTagName("xml"))
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
    imageUrl.appendChild(rss.createTextNode(urljoin(websiteUrl, "/img/icons/chadoku.ico")))
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
        guid.appendChild(rss.createTextNode(urljoin(websiteUrl, article['url'])))
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

    # print(blogData)

    