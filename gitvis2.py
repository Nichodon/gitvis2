import git
import pprint
from Tkinter import *

repo = git.Repo('.')

commits = list(repo.iter_commits('master'))
names = map(lambda l1: [l1.hexsha, map(lambda l2: l2.hexsha, l1.parents),
                        l1.message.rstrip(), l1.author.name, l1.authored_date], commits)

pprint.pprint(names)

tk = Tk()

canvas = Canvas(tk, width=800, height=800, background='white')
canvas.configure(scrollregion=(0, 0, 1000, 1000))
canvas.grid(row=0, column=0)

y = 20
for name in names:
    canvas.create_oval(15, y - 5, 25, y + 5, fill='red')
    canvas.create_text(35, y, text=name[0][:7], anchor=W)
    canvas.create_text(100, y, text=name[2], anchor=W)
    canvas.create_text(400, y, text=name[3], anchor=W)
    canvas.create_text(500, y, text=name[4], anchor=W)
    y += 20


def scroll_start(event):
    canvas.scan_mark(0, event.y)


def scroll_move(event):
    canvas.scan_dragto(0, event.y, gain=1)


canvas.bind("<ButtonPress-1>", scroll_start)
canvas.bind("<B1-Motion>", scroll_move)

mainloop()
