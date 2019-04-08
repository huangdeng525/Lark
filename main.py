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


class ActionBase:
    def __init__(self, notice_array, gui_base):
        self.gui = gui_base
        self.notice_array = notice_array
        self.label_array = gui_base.label_var
        self.entrys = gui_base.para_entrys

    def update_notice(self):
        for notice, label in zip(self.notice_array, self.label_array):
            label.set(notice)
        for entry in self.entrys:
            entry.delete(0, tk.END)

    def out(self, notice):
        self.gui.windows[0][0].insert(tk.END, notice + '\n')
        self.gui.windows[0][0].see(tk.END)
        self.gui.windows[0][0].update()

    def FlashOut(self, notice):
        self.gui.windows[0][1].insert(tk.END, notice + '\n')
        self.gui.windows[0][1].see(tk.END)
        self.gui.windows[0][1].update()
    
class CheckSum(ActionBase):
    def __init__(self, parent):
        self._parent = parent
        notice_array = ['Need To Check File:', 'Alg(md5,sha1,sha256):', 'Need Check Sum(opt):','', '']
        ActionBase.__init__(self, notice_array, parent)

    def Act(self):
        check_file = self._parent.para_strings[0]
        hash_type = self._parent.para_strings[1]
        to_check_sum = self._parent.para_strings[2]
        support_hash = ['md5', 'sha1', 'sha256']
        if len(check_file) == 0 or len(hash_type) == 0 or hash_type not in support_hash:
            self.out('para error:')
            return
        if not os.path.exists(check_file):
            self.out('File Not Exist!')
            return
        hash_key = get_key(check_file, hash_type)
        self.out(check_file)
        self.out('[%s]%s' % (hash_type, str(hash_key)))
        if len(to_check_sum) > 0:
            if to_check_sum == hash_key:
                self.out('Check Passed!')
            else:
                self.out('Check Failed!')


class CheckUnique(ActionBase):
    def __init__(self, parent):
        self._parent = parent
        notice_array = ['1st dir(H):', '2nd dir(opt):', '3rd dir(opt):','4th dir(L)(opt):', 'File to Save:']
        ActionBase.__init__(self, notice_array, parent)

    def Act(self):
        out_file = self._parent.para_strings[4]
        need_check_dir = []
        for x in range(4):
            if len(self._parent.para_strings[x]) > 0:
                need_check_dir.append(self._parent.para_strings[x])

        if len(out_file) == 0 or len(need_check_dir) == 0:
            self.out('para error!')
            return
        self.hash_key = dict()
        self.files = 0
        self.empty_files = []
        with open(out_file, 'w', encoding="utf-8") as self.out_f:
            for one in need_check_dir:
                self.out('Process Dir:' + one)
                self.process_unique(one)
            for one in self.empty_files:
                self.out_f.write('#empty File:%s\n' % one)
        self.out('Process success finished!')

    def process_unique(self, root):
        if len(root) == 0:
            return
        if os.path.isdir(root):
            for cur_path, dirs, files in os.walk(root):
                for file in files:
                    self.files += 1
                    if self.files % 1000 == 0:
                        self.out('\rProcessed files:%d' % self.files)
                    full_name = os.path.join(cur_path, file)
                    if os.path.getsize(full_name) == 0:
                        self.empty_files.append(full_name)
                        continue

                    f_key = get_key(full_name, 'sha1')
                    if f_key in self.hash_key:
                        self.record_equal(self.hash_key[f_key], full_name)
                    else:
                        self.hash_key[f_key] = full_name

    def record_equal(self, ori, equal):
        outs = ['#Ori:%s\n' % ori,
                'del "%s"\n' % equal]
        for one in outs:
            self.out_f.write(one)


class HashDir(ActionBase):
    def __init__(self, parent):
        self._parent = parent
        notice_array = ['1st dir:', '2nd dir(opt):', '3rd dir(opt):','4th dir(opt):', 'File to Save:']
        ActionBase.__init__(self, notice_array, parent)

    def Act(self):
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


class Split(ActionBase):
    def __init__(self, parent):
        self._parent = parent
        notice_array = ['To Split File:', '1st Save File:', '2st Save File:','3st Save File(opt):', '4st Save File(opt):']
        ActionBase.__init__(self, notice_array, parent)

    def Act(self):
        input_file = self._parent.para_strings[0]
        outs_files = []
        for x in range(4):
            if len(self._parent.para_strings[x+1]) > 0:
                outs_files.append(self._parent.para_strings[x+1])
        if len(input_file) == 0 or len(outs_files) < 2:
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


class Merge(ActionBase):
    def __init__(self, parent):
        self._parent = parent
        notice_array = ['1st Merge File:', '2st Merge File:','3st Merge File(opt):', '4st Merge File(opt):','To Save File:', ]
        ActionBase.__init__(self, notice_array, parent)

    def Act(self):
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
        self.frame = []
        self.windows = []
        self.para_entrys = []
        self.label_var = []
        self.my_font = ('Lucida Console', 12)
        self.my_color = ['#C7EDCC', 'black']

        self.frame.append(tk.Frame(self.root, borderwidth=0)) 
        outText = tk.Text(self.frame[0], height=20, width=120, font=self.my_font, bg='#C7EDCC', fg='black', relief=tk.FLAT)
        scroll = tk.Scrollbar(self.frame[0], command=outText.yview)
        outText.configure(yscrollcommand=scroll.set)
        outText.pack(side=tk.TOP)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        FlashText = tk.Text(self.frame[0], height=6, width=120, font=self.my_font, bg='#C7EDCC', fg='black', relief=tk.FLAT)
        FlashText.pack(side=tk.BOTTOM)

        self.windows.append([outText, FlashText])
        self.frame[0].pack()

        col = 0
        for line in range(5):
            col += 1
            label_var = tk.StringVar()
            self.frame.append(tk.Frame(self.root, borderwidth=0))
            in_label = tk.Label(self.frame[col], width=30, font=self.my_font, textvariable=label_var)
            self.label_var.append(label_var)
            in_label.pack(side=tk.LEFT)
            e = tk.StringVar()
            in_entry = tk.Entry(self.frame[col], width=90, font=self.my_font, textvariable=e)
            in_entry.pack(side=tk.LEFT)
            e.set("")
            self.windows.append([in_label, in_entry])
            self.para_entrys.append(in_entry)
            self.frame[col].pack()

        self.frame.append(tk.Frame(self.root, borderwidth=0))
        self.SelectedFun = tk.IntVar()
        for text, value in [('checksum', 1), ('unique', 2), ('split', 3), ('merge', 4), ('hashdir', 5)]:
            tk.Radiobutton(self.frame[-1], text=text, value=value, variable=self.SelectedFun, \
                command=lambda s=self, r=self.SelectedFun: s.SelectedAction(r)).pack(side=tk.LEFT, anchor=tk.W)

        tab_label = tk.Label(self.frame[-1], width=50, font=my_font)
        tab_label.pack(side=tk.LEFT)

        tk.Button(self.frame[-1], text='run',
                    borderwidth=1, relief=tk.RAISED, width=10,
                    command=lambda s=self, r=self.SelectedFun: s.RunAction(r))\
                .pack(side=tk.LEFT, padx=1, pady=1)
        self.frame[-1].pack()

        self.actions = [CheckSum(self), CheckUnique(self), Split(self), Merge(self), HashDir(self), ]

    def crt_outtext(self):
                self.out_text_frame = tk.Frame(self.root, borderwidth=1)
        scroll_y = tk.Scrollbar(self.out_text_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = tk.Scrollbar(self.out_text_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.out_text = tk.Text(self.out_text_frame,height=22, width=120, font=self.my_font, bg='#C7EDCC', fg='black', \
                            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set, wrap='none', relief=tk.FLAT)
        self.out_text.pack(side=tk.LEFT)
        scroll_y.config(command=self.out_text.yview)
        scroll_x.config(command=self.out_text.xview)

        self.out_text_frame.pack(padx=1, pady=2)
        self.out_text.config(state='disable')

    def SelectedAction(self, para):
        if para.get() > 0:
            index = para.get() - 1
            self.actions[index].update_notice()

    def RunAction(self, para):
        self.para_strings = []
        for entry in self.para_entrys:
            self.para_strings.append(entry.get())
        if para.get() > 0:
            index = para.get() - 1
            self.actions[index].Act()

    def update_outtext(self, strings):
        for string in strings:
            self.windows[0][0].insert(tk.END, string + '\n')
        self.windows[0][0].see(tk.END)
        self.windows[0][0].update()

    def mainloop(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = GUI()
    #app.master.title('Lark')
    app.mainloop()
