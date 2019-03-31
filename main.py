# !python.exe
# !/usr/bin/python3
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
import json


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


class CheckSum:
    def __init__(self, parent):
        self._parent = parent

    def checksum(self):
        check_file = self._parent.para_strings[0]
        hash_type = self._parent.para_strings[1]
        to_check_sum = self._parent.para_strings[2]
        support_hash = ['md5', 'sha1', 'sha256']
        if len(check_file) == 0 or len(hash_type) == 0 or hash_type not in support_hash:
            self.out_checksum_help()
            return
        if not os.path.exists(check_file):
            notice = ['File Not Exist!']
            self._parent.update_outtext(notice)
            return
        hash_key = get_key(check_file, hash_type)
        outs = []
        outs.append(str(hash_key))
        if len(to_check_sum) > 0:
            if to_check_sum == hash_key:
                outs.append('Check passed!')
            else:
                outs.append('Check Failed!')
        self._parent.update_outtext(outs)

    def out_checksum_help(self):
        help = ['Please input paramater:',
                'para1:need check file',
                'para2:check algorithm(md5, sha1, sha256)',
                'para3:need checked sum']
        self._parent.update_outtext(help)


class CheckUnique:
    def __init__(self, parent):
        self._parent = parent

    def unique(self):
        out_file = self._parent.para_strings[4]
        need_check_dir = []
        for x in range(4):
            if len(self._parent.para_strings[x]) > 0:
                need_check_dir.append(self._parent.para_strings[x])

        if len(out_file) == 0 or len(need_check_dir) == 0:
            self.out_unique_help()
            return
        self.hash_key = dict()
        self.files = 0
        self.empty_files = []
        with open(out_file, 'w', encoding="utf-8") as self.out_f:
            for one in need_check_dir:
                self.process_unique(one)
            for one in self.empty_files:
                self.out_f.write('#empty File:%s\n' % one)
        notice = ['process success finished!']
        self._parent.update_outtext(notice)

    def process_unique(self, root):
        if len(root) == 0:
            return
        if os.path.isdir(root):
            for cur_path, dirs, files in os.walk(root):
                for file in files:
                    self.files += 1
                    if self.files % 1000 == 0:
                        ptr_str = ['\r processed files:%d' % self.files]
                        self._parent.update_outtext(ptr_str)
                    full_name = os.path.join(cur_path, file)
                    if os.path.getsize(full_name) == 0:
                        self.empty_files.append(full_name)
                        continue

                    f_key = get_key(full_name, 'sha1')
                    if f_key in self.hash_key:
                        self.record_equal(self.hash_key[f_key], full_name)
                    else:
                        self.hash_key[f_key] = full_name

    def out_unique_help(self):
        notice = ['Please input paramater:',
                'para1~para4:the dir to find equal files, High priority ahead',
                'para5:the file to out the equal files, can be run in command']
        self._parent.update_outtext(notice)

    def record_equal(self, ori, equal):
        outs = ['#Ori:%s\n' % ori,
                'del "%s"\n' % equal]
        for one in outs:
            self.out_f.write(one)


class HashDir:
    def __init__(self, parent):
        self._parent = parent

    def hashdir(self):
        out_file = self._parent.para_strings[4]
        need_hash_dir = []
        for x in range(4):
            if len(self._parent.para_strings[x]) > 0:
                need_hash_dir.append(self._parent.para_strings[x])
        if len(out_file) == 0 or len(need_hash_dir) == 0:
            self.out_hashdir_help()
            return

        self.record = dict()
        for one in need_hash_dir:
            self.process_hash(one)
        with open(out_file, 'w') as f:
            f.write(json.dumps(self.record, indent=4, ensure_ascii=False))

    def process_hash(self, root):
        skip_len = len(root)
        if skip_len == 0:
            return
        if os.path.isdir(root):
            for cur_path, dirs, files in os.walk(root):
                for file in files:
                    full_name = os.path.join(cur_path, file)
                    f_key = get_key(full_name, 'sha1')
                    self.record[f_key] = full_name[skip_len:]

    def out_hashdir_help(self):
        notice = ['Please input paramater:',
                'para1~para4:the dirs build hash key',
                'para5:the file to save all hash record, as json']
        self._parent.update_outtext(notice)


class Split:
    def __init__(self, parent):
        self._parent = parent

    def split(self):
        input_file = self._parent.para_strings[0]
        outs_files = []
        for x in range(4):
            if len(self._parent.para_strings[x+1]) > 0:
                outs_files.append(self._parent.para_strings[x+1])
        if len(input_file) == 0 or len(outs_files) == 0:
            self.out_split_help()
            return

        out_fs = []
        for outs_file in outs_files:
            out_fs.append(open(outs_file, 'wb'))

        with open(input_file, 'rb') as f:
            self.write2file(f, out_fs)

        for f in out_fs:
            f.close()

    def write2file(self, in_f, out_fs):
        while True:
            for f in out_fs:
                block = in_f.read(256)
                if not block:
                    return
                f.write(block)

    def out_split_help(self):
        notice = ['Please input paramater:',
                'para1:input file to split',
                'para2~para5:the files to save split data']
        self._parent.update_outtext(notice)


class Merge:
    def __init__(self, parent):
        self._parent = parent

    def merge(self):
            outs_file = self._parent.para_strings[4]
            input_files = []
            for x in range(4):
                if len(self._parent.para_strings[x]) > 0:
                    input_files.append(self._parent.para_strings[x])
            if len(outs_file) == 0 or len(input_files) == 0:
                self.out_merge_help()
                return

            in_fs = []
            for input_file in input_files:
                in_fs.append(open(input_file, 'rb'))

            with open(outs_file, 'wb') as f:
                self.write2file(in_fs, f)

            for f in in_fs:
                f.close()

    def write2file(self, in_fs, out_f):
        while True:
            for f in in_fs:
                block = f.read(256)
                if not block:
                    return
                out_f.write(block)

    def out_merge_help(self):
        notice = ['Please input paramater:',
                'para1~para4:input file to split, The order must be the same as input in split!',
                'para5:the files to save merged data']
        self._parent.update_outtext(notice)

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Lark')

        para = [None] * 5
        myfont = ('Lucida Console', 12)
        first_array_frame = tk.Frame(self.root, borderwidth=0)


        self.outText = tk.Text(first_array_frame, height=26, width=130, font=myfont, bg='#C7EDCC', fg='black', relief=tk.FLAT)
        scroll = tk.Scrollbar(first_array_frame, command=self.outText.yview)
        self.outText.configure(yscrollcommand=scroll.set)
        self.outText.pack(side=tk.LEFT)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)


        first_array_frame.pack()

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

        
        action_buttun = tk.Frame(self.root, borderwidth=0)
        self.SelectedFun = tk.IntVar()
        for text, value in [('checksum', 1), ('unique', 2), ('split', 3), ('merge', 4), ('hashdir', 5)]:
            tk.Radiobutton(action_buttun, text=text, value=value, variable=self.SelectedFun, command=lambda s=self, r=self.SelectedFun: s.SelectedAction(r)).pack(side=tk.LEFT, anchor=tk.W)
        self.SelectedFun.set(3)


        tk.Button(action_buttun, text='run',
                    borderwidth=1, relief=tk.RAISED, width=10,
                    command=lambda s=self, r=self.SelectedFun: s.action(r))\
                .pack(side=tk.LEFT, padx=1, pady=1)
        action_buttun.pack()

    def SelectedAction(self, action):
        if action.get() == 1:
            pass

    def action(self, action):
        self.para_strings = []
        for entry in self.para_entrys:
            self.para_strings.append(entry.get())
        if action.get() == 1:
            p = CheckSum(self)
            p.checksum()
        if action.get() == 2:
            p = CheckUnique(self)
            p.unique()
        if action.get() == 3:
            p = HashDir(self)
            p.hashdir()
        if action.get() == 4:
            p = Split(self)
            p.split()
        if action.get() == 5:
            p = Merge(self)
            p.merge()

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
