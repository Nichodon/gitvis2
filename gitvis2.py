import git
import pprint
from Tkinter import *
import math
import time

repo = git.Repo('.')

commits = list(repo.iter_commits('master'))


def click(x):
    iText.config(text=x)
    print x


root = Tk()

info = LabelFrame(root, text='Info', width=500)
info.grid(row=0, column=0, sticky=NS)

iText = Message(info, text='hi', width=500)
iText.grid(row=0, column=0)

graph = LabelFrame(root, text='Graph')
graph.grid(row=0, column=1)

canvas = Canvas(graph, width=750, height=250, bg='white', scrollregion=(0, 0, 1000, 1000))
canvas.grid(row=0, column=0)

status = LabelFrame(root, text='Status')
status.grid(row=1, column=0, columnspan=2, sticky=EW)

sText = Message(status, text=repo.git.status())
sText.grid(row=0, column=0)

y = 20
for commit in commits:
    tag = canvas.create_rectangle(10, y - 10, 740, y + 10,
                                  fill='#eee' if (y / 20) % 2 == 1 else 'white', outline='', tags='tag')
    canvas.create_oval(15, y - 5, 25, y + 5, fill='red', tags='tag')
    canvas.create_text(50, y, text=commit.hexsha[:7], anchor=W, tags='tag')
    canvas.create_text(200, y, text=commit.message.split('\n')[0], anchor=W, tags='tag')
    canvas.create_text(400, y, text=commit.author.name, anchor=W, tags='tag')
    date = time.gmtime(commit.authored_date)
    mon = ('0' if date.tm_mon < 10 else '') + str(date.tm_mon)
    canvas.create_text(500, y, text=str(date.tm_year) + '-' + mon + '-' + str(date.tm_mday), anchor=W, tags='tag')
    canvas.tag_bind('tag', '<Button-1>', lambda x: click(commit))
    y += 20


def mousewheel(event):
    canvas.yview_scroll(int(-math.copysign(1, event.delta)), "units")


root.bind_all("<MouseWheel>", mousewheel)

mainloop()
