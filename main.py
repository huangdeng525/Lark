#!/usr/bin/python3
# coding=utf-8
# main.py
#
#  python gui tools
#
#  Copyright (C) 2019-2019 huangdeng @ chengdu
#
#  This program is free sparatware; you can redistribute it and/or modify
#  it under the terms para the GNU General Public License version 3 as
#  published by the Free Sparatware Foundation.
#  2019.03.22 init

import tkinter as tk


class GUITest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Lark')

        para = [None] * 5
        for bdw in range(5):
            para[bdw] = tk.Frame(self.root, borderwidth=0)
            tk.Label(para[bdw], text='borderwidth = %d' % bdw).pack(side=tk.LEFT)
            for relief in [tk.RAISED, tk.SUNKEN, tk.FLAT, tk.RIDGE, tk.GROOVE, tk.SOLID]:
                tk.Button(para[bdw], text=relief,
                        borderwidth=bdw, relief=relief, width=10,
                        command=lambda s=self, r=relief, b=bdw: s.prt(r, b))\
                    .pack(side=tk.LEFT, padx=7-bdw, pady=7-bdw)
            para[bdw].pack()

    def prt(self, relief, border):
        print('%s:%d' % (relief, border))

    def mainloop(self):
        self.root.mainloop()

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Lark')

        para = [None] * 5

        self.outMessage = tk.Frame(self.root, borderwidth=0)
        tk.Message(self.outMessage,text="Init.", bg='black', fg='ivory',
            relief=tk.GROOVE).pack(padx=0, pady=0)
        self.outMessage.pack()

        for ofline in range(5):
            para[ofline] = tk.Frame(self.root, borderwidth=0)
            para[ofline]
            tk.Label(para[ofline], text='para[%d]:' % (ofline+1)).pack(side=tk.LEFT)
            e = tk.StringVar()
            tk.Entry(para[ofline], width=128, textvariable=e).pack(side=tk.LEFT)
            e.set("")
            para[ofline].pack()

        buttuns = {'checksum', 'unique', 'split', 'merge'}
        action_buttun = tk.Frame(self.root, borderwidth=0)
        for buttun in buttuns:
            tk.Button(action_buttun, text=buttun,
                        borderwidth=1, relief=tk.RAISED, width=10,
                        command=lambda s=self, r=buttun: s.action(r))\
                    .pack(side=tk.LEFT, padx=1, pady=1)
        action_buttun.pack()


    def action(self, action):
        print('%s' % action)

    def mainloop(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = GUI()
    #app.master.title('Lark')
    app.mainloop()
