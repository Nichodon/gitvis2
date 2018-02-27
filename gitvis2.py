import git
import pprint
from Tkinter import *
import math
import time


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


repo = git.Repo('../nichodon.github.io')

commits = list(repo.iter_commits())
lanes = {}
positions = {}
children = {}


def leading(x):
    return '0' + str(x) if x < 10 else str(x)


def year(x):
    sec = time.gmtime(x)
    return str(sec.tm_year) + '-' + leading(sec.tm_mon) + '-' + str(sec.tm_mday)


def hour(x):
    sec = time.gmtime(x)
    return leading(sec.tm_hour) + ':' + leading(sec.tm_min) + ':' + leading(sec.tm_sec)


def click(event):
    c = commits[int(canvas.itemcget(event.widget.find_withtag('current'), 'tags').split(' ')[0][1:])]
    iText.config(text='Commit SHA1:\n' + c.hexsha + '\n\nMessage:\n' + c.message + '\n\nAuthor:\n' + c.author.name +
                      '\n' + c.author.email + '\n\nDate: ' + year(c.authored_date) + '\nTime: ' + hour(c.authored_date))


root = Tk()

info = LabelFrame(root, text='Info', width=100000)
info.grid(row=0, column=0)

iText = Message(info, text='hi', width=500)
iText.grid(row=0, column=0, sticky=EW)

graph = LabelFrame(root, text='Graph')
graph.grid(row=0, column=1)

canvas = Canvas(graph, width=750, height=250, bg='white', scrollregion=(0, 0, 1000, 10000))
canvas.grid(row=0, column=0)

status = LabelFrame(root, text='Status')
status.grid(row=1, column=0, columnspan=2, sticky=EW)

sText = Message(status, text=repo.git.status())
sText.grid(row=0, column=0)


def follow():
    n = 0
    while True:
        if n not in used:
            used.append(n)
            return n
        n += 1


def replace(a, b):
    lanes[a] = min(lanes[a], b) if a in lanes else b


e = 20
used = []
for i in range(len(commits)):
    commit = commits[i]
    d = lanes[commit.hexsha] if commit.hexsha in lanes else follow()
    lanes[commit.hexsha] = d
    d *= 10
    first = 0
    for parent in commit.parents:
        if parent.hexsha in children:
            children[parent.hexsha].append(commit.hexsha)
        else:
            children[parent.hexsha] = [commit.hexsha]
        replace(parent.hexsha, lanes[commit.hexsha] if first == 0 else follow())
        first += 1
    tag = canvas.create_rectangle(10, e - 10, 740, e + 10,
                                  fill='#eee' if (e / 20) % 2 == 1 else 'white', outline='', tags='t' + str(i))
    positions[commit.hexsha] = Point(d + 20, e)
    if commit.hexsha in children:
        for child in children[commit.hexsha]:
            canvas.create_line(d + 20, e, positions[child].x, positions[child].y)
    canvas.create_oval(15 + d, e - 5, 25 + d, e + 5, fill='red', tags='t' + str(i))
    canvas.create_text(200, e, text=commit.hexsha[:7], anchor=W, tags='t' + str(i))
    canvas.create_text(300, e, text=commit.message.split('\n')[0], anchor=W, tags='t' + str(i))
    canvas.create_text(550, e, text=commit.author.name, anchor=W, tags='t' + str(i))
    canvas.create_text(650, e, text=year(commit.authored_date), anchor=W, tags='t' + str(i))
    canvas.tag_bind('t' + str(i), '<Button-1>', click)
    e += 20


def mousewheel(event):
    canvas.yview_scroll(int(-math.copysign(1, event.delta)), 'units')


root.bind_all('<MouseWheel>', mousewheel)

mainloop()
