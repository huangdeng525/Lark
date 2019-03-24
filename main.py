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
import hashlib
import os


def get_key(full_name, hash_type):
    my_hash = None
    if hash_type == 'sha1':
        my_hash = hashlib.sha1()
    elif hash_type == 'md5':
        my_hash = hashlib.md5()
    elif hash_type == 'sha256':
        my_hash = hashlib.sha256()
    else:
        return 0

    block_size = 100 * 1024 * 1024
    if os.path.getsize(full_name) < block_size:
        with open(full_name, 'rb') as f:
            b = f.read()
            my_hash.update(b)
    else:
        with open(full_name, 'rb') as f:
            while True:
                b = f.read(block_size)
                if not b:
                    break
                my_hash.update(b)
    return my_hash.hexdigest()

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Lark')

        para = [None] * 5
        myfont = ('Lucida Console', 12)
        self.outMessageFrame = tk.Frame(self.root, borderwidth=0)
        self.outText = tk.Text(self.outMessageFrame,height=26, width=130, font=myfont, bg='black', fg='ivory', relief=tk.FLAT)
        scroll = tk.Scrollbar(self.outMessageFrame, command=self.outText.yview)
        self.outText.configure(yscrollcommand=scroll.set)

        self.outText.pack(side=tk.LEFT)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.outMessageFrame.pack()

        self.para_entrys = []
        for ofline in range(5):
            para[ofline] = tk.Frame(self.root, borderwidth=0)
            para[ofline]
            tk.Label(para[ofline], text='para[%d]:' % (ofline+1), font=myfont).pack(side=tk.LEFT)
            e = tk.StringVar()
            para_ety = tk.Entry(para[ofline], width=128, font=myfont, textvariable=e)
            para_ety.pack(side=tk.LEFT)
            self.para_entrys.append(para_ety)
            e.set("")
            para[ofline].pack()

        buttuns = {'checksum', 'unique', 'split', 'merge'}
        action_buttun = tk.Frame(self.root, borderwidth=0)
        for buttun in buttuns:
            tk.Button(action_buttun, text=buttun,
                        borderwidth=1, relief=tk.RAISED, width=10,
                        command=lambda s=self, r=buttun: s.action(r))\
                    .pack(side=tk.LEFT, padx=0, pady=0)
        action_buttun.pack()

    def action(self, action):
        self.para_strings = []
        for entry in self.para_entrys:
            self.para_strings.append(entry.get())
        if action == 'checksum':
            self.checksum()

    def checksum(self):
        check_file = self.para_strings[0]
        hash_type = self.para_strings[1]
        to_check_sum = self.para_strings[2]
        support_hash = ['md5', 'sha1', 'sha256']
        if len(check_file) == 0 or len(hash_type) == 0 or hash_type not in support_hash:
            self.out_checksum_help()
            return
        if not os.path.exists(check_file):
            notice = ['File Not Exist!']
            self.update_outtext(notice)
            return
        hash_key = get_key(check_file, hash_type)
        outs = []
        outs.append(str(hash_key))
        if len(to_check_sum) > 0:
            if to_check_sum == hash_key:
                outs.append('Check passed!')
            else:
                outs.append('Check Failed!')
        self.update_outtext(outs)

    def out_checksum_help(self):
        help = ['Please input paramater:',
                'para1:need check file',
                'para2:check algorithm(md5, sha1, sha256)',
                'para3:need checked sum']
        self.update_outtext(help)

    def update_outtext(self, strings):
        for string in strings:
            self.outText.insert(tk.END, string + '\n')
        self.outText.see(tk.END)
        self.outText.update()

    def mainloop(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = GUI()
    #app.master.title('Lark')
    app.mainloop()
