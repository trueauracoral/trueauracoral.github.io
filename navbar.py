#!/usr/bin/env python
import math
import pyperclip

PARTS = 7
sectionAdd = (2*math.pi)/PARTS
radius = 150

coordinates = []
navHTML = ""
content = ""

csscontent = ""
for i in list(range(PARTS)):
    x = radius*math.cos(sectionAdd*i)
    y = radius*math.sin(sectionAdd*i)
    coordinates.append({"x": x, "y": y})
    csscontent += (f"\n#navButton{i+1} {{left: calc({x}px + var(--radiusNumber)); top: calc({y}px + var(--radiusNumber))}}")
pyperclip.copy(csscontent)
#print(coordinates)

#with open("top.html", "r") as file:
#    navHTML += file.read()
#    navHTML = navHTML.replace("../index.css","index.css")

navHTML += content
with open("bottom.html", "r") as file:
    bottomHTML = file.read()

navHTML += bottomHTML
#print(navHTML)
#with open("index.html", "w") as file:
#    file.write(navHTML)