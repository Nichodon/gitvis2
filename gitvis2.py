import git
import pprint
from Tkinter import *
import math
import time


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


repo = git.Repo('../anematode.github.io')

commits = list(repo.iter_commits())
lanes = {}
positions = {}
children = {}


def leading(x):
    return '0' + str(x) if x < 10 else str(x)


def year(x):
    sec = time.gmtime(x)
    return str(sec.tm_year) + '-' + leading(sec.tm_mon) + '-' + leading(sec.tm_mday)


def hour(x):
    sec = time.gmtime(x)
    return leading(sec.tm_hour) + ':' + leading(sec.tm_min) + ':' + leading(sec.tm_sec)


def click(event):
    c = commits[int(canvas.itemcget(event.widget.find_withtag('current'), 'tags').split(' ')[0][1:])]
    thing = ''
    for parent in c.parents:
        thing += parent.hexsha[:7] + '\n'
    iText.config(text='Commit SHA1:\n' + c.hexsha + '\n\nMessage:\n' + c.message + '\n\nAuthor:\n' + c.author.name +
                      '\n' + c.author.email + '\n\nDate: ' + year(c.authored_date) + '\nTime: ' +
                      hour(c.authored_date) + '\n\n\nparents' + thing)


root = Tk()

info = LabelFrame(root, text='Info', width=100000)
info.grid(row=0, column=0)

iText = Message(info, text='hi', width=500)
iText.grid(row=0, column=0, sticky=EW)

graph = LabelFrame(root, text='Graph')
graph.grid(row=0, column=1)

canvas = Canvas(graph, width=800, height=500, bg='white', scrollregion=(0, 0, 1000, 10000))
canvas.grid(row=0, column=0)

status = LabelFrame(root, text='Status')
status.grid(row=1, column=0, columnspan=2, sticky=EW)

sText = Message(status, text=repo.git.status())
sText.grid(row=0, column=0)


def connect(p1, p2, q1, q2):
    if p1 < q1:
        canvas.create_line(p1, p2, q1, p2)
        canvas.create_line(q1, p2, q1, q2)
    else:
        canvas.create_line(p1, p2, p1, q2)
        canvas.create_line(p1, q2, q1, q2)


def follow():
    n = 0
    while True:
        if n not in used or used[n] <= 0:
            used[n] = 0
            return n
        n += 1


e = 20
used = {}
lane = 0
for i in range(len(commits)):
    commit = commits[i]
    print commit.hexsha
    lane = lanes[commit.hexsha] if commit.hexsha in lanes else 0
    used[lane] = used[lane] - 1 if lane in used else 0
    for parent in commit.parents:
        overflow = follow()
        lanes[parent.hexsha] = min(lanes[parent.hexsha], overflow) if parent.hexsha in lanes else overflow
        used[overflow] += 1
        if parent.hexsha in children:
            children[parent.hexsha].append(commit.hexsha)
        else:
            children[parent.hexsha] = [commit.hexsha]
    lane *= 10
    tag = canvas.create_rectangle(10, e - 10, 790, e + 10,
                                  fill='#eee' if (e / 20) % 2 == 1 else 'white', outline='', tags='t' + str(i))
    positions[commit.hexsha] = Point(lane + 20, e)
    if commit.hexsha in children:
        for child in children[commit.hexsha]:
            connect(lane + 20, e, positions[child].x, positions[child].y)
    canvas.create_oval(15 + lane, e - 5, 25 + lane, e + 5, fill='red', tags='t' + str(i))
    canvas.create_text(200, e, text=commit.hexsha[:7], anchor=W, tags='t' + str(i))
    line = commit.message.split('\n')[0]
    canvas.create_text(250, e, text=line[:50] + ' ...' if len(line) > 50 else line, anchor=W, tags='t' + str(i))
    canvas.create_text(600, e, text=commit.author.name, anchor=W, tags='t' + str(i))
    canvas.create_text(700, e, text=year(commit.authored_date), anchor=W, tags='t' + str(i))
    canvas.tag_bind('t' + str(i), '<Button-1>', click)
    e += 20


def mousewheel(event):
    canvas.yview_scroll(int(-math.copysign(1, event.delta)), 'units')


root.bind_all('<MouseWheel>', mousewheel)

mainloop()
