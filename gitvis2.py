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


class Blank:
    def __init__(self):
        self.widget = 0


def leading(x):
    return '0' + str(x) if x < 10 else str(x)


def year(x):
    sec = time.gmtime(x)
    return str(sec.tm_year) + '-' + leading(sec.tm_mon) + '-' + leading(sec.tm_mday)


def hour(x):
    sec = time.gmtime(x)
    return leading(sec.tm_hour) + ':' + leading(sec.tm_min) + ':' + leading(sec.tm_sec)


current = [None, '']


def click(event):
    global current
    canvas.itemconfig(canvas.find_withtag('t0'), fill='#eee')
    if event.widget != 0:
        if current[0]:
            canvas.itemconfig(current[0], fill=current[1])

        number = int(canvas.itemcget(event.widget.find_withtag('current'), 'tags').split(' ')[0][1:])
        color = '#fff' if number % 2 == 1 else '#eee'
        current = [event.widget.find_withtag('current'), color]

        canvas.itemconfig(event.widget.find_withtag('current'), fill='#ccc')

        c = commits[number]
    else:
        c = commits[0]
        canvas.itemconfig(canvas.find_withtag('t0'), fill='#ccc')

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
        canvas.create_line(a1, a2 + 3, b1, b2 - 2, fill=color)
    elif a2 < b2:
        canvas.create_line(a1 + 3, a2, b1 - 7, a2, fill=color)
        canvas.create_line(b1 - 7, a2, b1 - 5, a2 + 2, fill=color)
        canvas.create_line(b1 - 5, a2 + 2, b1 - 5, b2 - 5, fill=color)
        canvas.create_line(b1 - 5, b2 - 5, b1 - 2, b2 - 2, fill=color)
    else:
        canvas.create_line(a1 + 3, a2, b1 - 7, a2, fill=color)
        canvas.create_line(b1 - 7, a2, b1 - 5, a2 - 2, fill=color)
        canvas.create_line(b1 - 5, a2 - 2, b1 - 5, b2 + 5, fill=color)
        canvas.create_line(b1 - 5, b2 + 5, b1 - 2, b2 + 2, fill=color)


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
    t_text.config(state=NORMAL)
    t_text.delete(1.0, END)
    t_text.insert(END, repo.git.diff())
    t_text.config(state=DISABLED)

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
        canvas.create_rectangle(10, e - 10, 890, e + 10, fill='#eee' if (e / 20) % 2 == 1 else '#fff',
                                outline='', tags='t' + str(i))
        positions[commit.hexsha] = Point(lane + 20, e)
        canvas.create_rectangle(lane + 18, e - 2, lane + 23, e + 3, fill='#999', outline='')
        canvas.create_rectangle(lane + 19, e - 1, lane + 22, e + 2, fill='#fff', outline='')
        if commit.hexsha in children:
            for child in children[commit.hexsha]:
                hue += 0.275
                connect(lane + 20, e, positions[child].x, positions[child].y, hue)
        canvas.create_text(200, e, text=commit.hexsha[:7], anchor=W)
        line = commit.message.split('\n')[0]
        canvas.create_text(300, e, text=line[:40] + ' ...' if len(line) > 40 else line, anchor=W)
        canvas.create_text(600, e, text=commit.author.name, anchor=W)
        canvas.create_text(700, e, text=year(commit.authored_date), anchor=W)
        canvas.tag_bind('t' + str(i), '<Button-1>', click)
        e += 20

    canvas.config(scrollregion=(0, 0, 0, e))
    click(Blank())


root = Tk()
root.bind_all('<MouseWheel>', mousewheel)
root.wm_title('GitVis2 1.0 Beta')

info = LabelFrame(root, text='Info', width=100000)
info.grid(row=0, column=0, sticky=NS)
i_text = Message(info)
i_text.grid(row=0, column=0)

graph = LabelFrame(root, text='Graph')
graph.grid(row=0, column=1)
canvas = Canvas(graph, width=800, height=400, bg='white')
canvas.grid(row=0, column=0)

status = LabelFrame(root, text='Status')
status.grid(row=1, column=0, columnspan=2, sticky=EW)
s_text = Message(status)
s_text.grid(row=0, column=0)
t_text = Text(status, relief='flat', borderwidth=0, height=20, bg=s_text.cget('bg'), font=s_text.cget('font'))
t_text.grid(row=0, column=1)
t_scroll = Scrollbar(status, command=t_text.yview)
t_scroll.grid(row=0, column=2, sticky=NS)

menu = Menu(root)
files = Menu(menu, tearoff=0)
files.add_command(label="Open", command=new)
menu.add_cascade(label="File", menu=files)
root.config(menu=menu)

update('.')

mainloop()
