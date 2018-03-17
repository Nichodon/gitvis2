import git
import pprint
from Tkinter import *
import math
import time
import colorsys
import tkFileDialog


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


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
    for higher in c.parents:
        thing += higher.hexsha + '\n'
    i_text.config(text='Commit SHA1:\n' + c.hexsha + '\n\nMessage:\n' + c.message + '\n\nAuthor:\n' + c.author.name +
                       '\n' + c.author.email + '\n\nDate: ' + year(c.authored_date) + '\nTime: ' + hour(c.authored_date)
                       + '\n\nParents:\n' + thing)


def connect(p1, p2, q1, q2, h):
    color = '#%02X%02X%02X' % tuple([q * 255 for q in colorsys.hsv_to_rgb(h, 0.8, 0.8)])
    a1 = q1
    b1 = p1
    a2 = q2
    b2 = p2
    if p1 < q1:
        a1 = p1
        b1 = q1
        a2 = p2
        b2 = q2
    if a1 == b1:
        canvas.create_line(a1, a2 + 4, b1, b2 - 3, fill=color)
    elif a2 < b2:
        canvas.create_line(a1 + 4, a2, b1 - 6, a2, fill=color)
        canvas.create_line(b1 - 6, a2, b1 - 4, a2 + 2, fill=color)
        canvas.create_line(b1 - 4, a2 + 2, b1 - 4, b2 - 7, fill=color)
        canvas.create_line(b1 - 4, b2 - 7, b1, b2 - 3, fill=color)
    else:
        canvas.create_line(a1 + 4, a2, b1 - 6, a2, fill=color)
        canvas.create_line(b1 - 6, a2, b1 - 4, a2 - 2, fill=color)
        canvas.create_line(b1 - 4, a2 - 2, b1 - 4, b2 + 7, fill=color)
        canvas.create_line(b1 - 4, b2 + 7, b1, b2 + 3, fill=color)


def follow():
    n = 0
    while True:
        if n not in big or len(big[n]) == 0:
            return n
        n += 1


def mousewheel(event):
    canvas.yview_scroll(int(-math.copysign(1, event.delta)), 'units')


big = {}
commits = []


def new():
    directory = tkFileDialog.askdirectory()
    if directory != '':
        update(directory)


def update(name):
    global commits, big

    repo = git.Repo(name)
    canvas.delete("all")
    s_text.config(text=repo.git.status())
    i_text.config(text='GitVis 2 BETA')

    commits = list(repo.iter_commits())
    lanes = {}
    positions = {}
    children = {}

    e = 20
    hue = 0
    big = {}

    for i in range(len(commits)):
        commit = commits[i]
        lane = lanes[commit.hexsha] if commit.hexsha in lanes else 0
        if lane in big:
            big[lane].remove(commit.hexsha)
        parents = list(commit.parents)
        parents.sort(key=lambda x: commits.index(x))
        for parent in parents:
            if parent.hexsha not in lanes:
                overflow = follow()
                lanes[parent.hexsha] = overflow
                if overflow in big:
                    big[overflow].append(parent.hexsha)
                else:
                    big[overflow] = [parent.hexsha]
            if parent.hexsha in children:
                children[parent.hexsha].append(commit.hexsha)
            else:
                children[parent.hexsha] = [commit.hexsha]
        lane *= 10
        canvas.create_rectangle(10, e - 10, 890, e + 10, fill='#eee' if (e / 20) % 2 == 1 else 'white', outline='',
                                tags='t' + str(i))
        positions[commit.hexsha] = Point(lane + 20, e)
        canvas.create_oval(lane + 17, e - 3, lane + 23, e + 3, fill='white', tags='t' + str(i))
        if commit.hexsha in children:
            for child in children[commit.hexsha]:
                hue += 0.275
                connect(lane + 20, e, positions[child].x, positions[child].y, hue)
        canvas.create_text(200, e, text=commit.hexsha[:7], anchor=W, tags='t' + str(i))
        line = commit.message.split('\n')[0]
        canvas.create_text(300, e, text=line[:50] + ' ...' if len(line) > 50 else line, anchor=W, tags='t' + str(i))
        canvas.create_text(700, e, text=commit.author.name, anchor=W, tags='t' + str(i))
        canvas.create_text(800, e, text=year(commit.authored_date), anchor=W, tags='t' + str(i))
        canvas.tag_bind('t' + str(i), '<Button-1>', click)
        e += 20

    canvas.config(scrollregion=(0, 0, 1000, e))


root = Tk()
root.bind_all('<MouseWheel>', mousewheel)
root.wm_title('GitVis2 1.0 Beta')

info = LabelFrame(root, text='Info', width=100000)
info.grid(row=0, column=0, sticky=NS)
i_text = Message(info)
i_text.grid(row=0, column=0)

graph = LabelFrame(root, text='Graph')
graph.grid(row=0, column=1)
canvas = Canvas(graph, width=900, height=500, bg='white')
canvas.grid(row=0, column=0)

status = LabelFrame(root, text='Status')
status.grid(row=1, column=0, columnspan=2, sticky=EW)
s_text = Message(status)
s_text.grid(row=0, column=0)

menu = Menu(root)
files = Menu(menu, tearoff=0)
files.add_command(label="Open", command=new)
menu.add_cascade(label="File", menu=files)
root.config(menu=menu)

update('.')

root.mainloop()
