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
import zipfile
import datetime


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
        self.gui.out_text.config(state='normal')
        self.gui.out_text.insert(tk.END, notice + '\n')
        self.gui.out_text.see(tk.END)
        self.gui.out_text.update()
        self.gui.out_text.config(state='disable')

    def outs(self, notices):
        self.gui.out_text.config(state='normal')
        for notice in notices:
            self.gui.out_text.insert(tk.END, notice + '\n')
        self.gui.out_text.see(tk.END)
        self.gui.out_text.update()
        self.gui.out_text.config(state='disable')

    def FlashOut(self, notice):
        self.gui.flash_text.config(state='normal')
        self.gui.flash_text.insert(tk.END, notice + '\n')
        self.gui.flash_text.see(tk.END)
        self.gui.flash_text.update()
        self.gui.flash_text.config(state='disable')

    def Act(self):
        ClassName = str(type(self))
        ClassName = ClassName[ClassName.find('.')+1:-2]
        td = datetime.datetime.today()
        begin_notice = "Start  [%s][%d-%02d-%02d %02d:%02d:%02d]" % (ClassName, td.year, td.month, td.day, td.hour, td.minute, td.second)
        self.out(begin_notice)
        self.RealAct()
        td = datetime.datetime.today()
        end_notice = "Finish [%s][%d-%02d-%02d %02d:%02d:%02d]" % (ClassName, td.year, td.month, td.day, td.hour, td.minute, td.second)
        self.out(end_notice)

class CheckSum(ActionBase):
    def __init__(self, parent):
        self._parent = parent
        notice_array = ['Need To Check File:', 'Alg(md5,sha1,sha256):', 'Need Check Sum(opt):','', '']
        ActionBase.__init__(self, notice_array, parent)

    def RealAct(self):
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

    def RealAct(self):
        out_file = self._parent.para_strings[4]
        need_check_dir = []
        for x in range(4):
            if len(self._parent.para_strings[x]) > 0:
                need_check_dir.append(self._parent.para_strings[x])

        if len(out_file) == 0 or len(need_check_dir) == 0:
            self.out('para error!')
            return

        self.hash_key = dict()
        self.empty_files = []
        with open(out_file, 'w', encoding="utf-8") as self.out_f:
            for one in need_check_dir:
                self.out('Process Dir:' + one)
                self.process_unique(one)
            for one in self.empty_files:
                self.out_f.write('rem empty_file:"%s"\n' % one)

    def process_unique(self, root):
        skip_len = len(root)
        if skip_len == 0:
            return
        if os.path.isdir(root):
            for cur_path, dirs, files in os.walk(root):
                for file in files:
                    full_name = os.path.join(cur_path, file)
                    self.FlashOut(full_name[skip_len:])
                    if os.path.getsize(full_name) == 0:
                        self.empty_files.append(full_name)
                        continue

                    f_key = get_key(full_name, 'sha1')
                    if f_key in self.hash_key:
                        self.record_equal(self.hash_key[f_key], full_name)
                    else:
                        self.hash_key[f_key] = full_name

    def record_equal(self, ori, equal):
        outs = ['\nrem "%s"\n' % ori,
                'del "%s"\n' % equal]
        for one in outs:
            self.out_f.write(one)


class HashDir(ActionBase):
    def __init__(self, parent):
        self._parent = parent
        notice_array = ['1st dir:', '2nd dir(opt):', '3rd dir(opt):','4th dir(opt):', 'File to Save:']
        ActionBase.__init__(self, notice_array, parent)

    def RealAct(self):
        out_file = self._parent.para_strings[4]
        need_hash_dir = []
        for x in range(4):
            if len(self._parent.para_strings[x]) > 0:
                need_hash_dir.append(self._parent.para_strings[x])
        if len(out_file) == 0 or len(need_hash_dir) == 0:
            self.out('para error!')
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
                    self.FlashOut(full_name[skip_len:])
                    f_key = get_key(full_name, 'sha1')
                    self.record[f_key] = full_name[skip_len:]


class Split(ActionBase):
    def __init__(self, parent):
        self._parent = parent
        notice_array = ['To Split File:', '1st Save File:', '2st Save File:','3st Save File(opt):', '4st Save File(opt):']
        ActionBase.__init__(self, notice_array, parent)

    def RealAct(self):
        input_file = self._parent.para_strings[0]
        outs_files = []
        for x in range(4):
            if len(self._parent.para_strings[x+1]) > 0:
                outs_files.append(self._parent.para_strings[x+1])
        if len(input_file) == 0 or len(outs_files) < 2:
            self.out('para error!')
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


class Merge(ActionBase):
    def __init__(self, parent):
        self._parent = parent
        notice_array = ['1st Merge File:', '2st Merge File:','3st Merge File(opt):', '4st Merge File(opt):','To Save File:', ]
        ActionBase.__init__(self, notice_array, parent)

    def RealAct(self):
        outs_file = self._parent.para_strings[4]
        input_files = []
        for x in range(4):
            if len(self._parent.para_strings[x]) > 0:
                input_files.append(self._parent.para_strings[x])
        if len(outs_file) == 0 or len(input_files) == 0:
            self.out('para error!')
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


class MyZip(ActionBase):
    def __init__(self, parent):
        self._parent = parent
        notice_array = ['To compress dir:', 'The Zip File:','', '', '', ]
        ActionBase.__init__(self, notice_array, parent)

    def RealAct(self):
        input_dir = self._parent.para_strings[0]
        outs_file = self._parent.para_strings[1]
        if len(outs_file) == 0 or len(input_dir) == 0 or not os.path.isdir(input_dir):
            self.out('para error!')
            return

        skip_len = len(input_dir)
        if skip_len == 0:
            return

        with zipfile.ZipFile(outs_file, 'a') as f:
            for cur_path, dirs, files in os.walk(input_dir):
                for file in files:
                    full_name = os.path.join(cur_path, file)
                    self.FlashOut(full_name[skip_len:])
                    f.write(full_name, arcname=full_name[skip_len:])


class MyUnZip(ActionBase):
    def __init__(self, parent):
        self._parent = parent
        notice_array = ['The Zip File:', 'To decompress dir:', '', '', '', ]
        ActionBase.__init__(self, notice_array, parent)

    def RealAct(self):
        input_file = self._parent.para_strings[0]
        outs_dir = self._parent.para_strings[1]
        if len(input_file) == 0 or len(outs_dir) == 0:
            self.out('para error!')
            return

        if not os.path.isdir(outs_dir):
            os.mkdir(outs_dir)

        with zipfile.ZipFile(input_file, 'r') as f:
            f.extractall(path=outs_dir)


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Lark 0.3')
        self.frame = []
        self.windows = []
        self.para_entrys = []
        self.label_var = []
        self.my_font = ('Lucida Console', 12)
        # [bg, fg]
        self.my_color = ['#C7EDCC', 'black']

        self.crt_outtext()
        self.crt_flashtext()
        self.crt_para()
        self.crt_sel_run()

        self.actions = [CheckSum(self), CheckUnique(self), Split(self), Merge(self), HashDir(self), MyZip(self), MyUnZip(self)]

    def crt_outtext(self):
        self.frame.append(tk.Frame(self.root, borderwidth=1))
        scroll_y = tk.Scrollbar(self.frame[-1])
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = tk.Scrollbar(self.frame[-1], orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.out_text = tk.Text(self.frame[-1],height=20, width=120, font=self.my_font, bg=self.my_color[0], fg=self.my_color[1], \
                            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set, wrap='none', relief=tk.FLAT)
        self.out_text.pack(side=tk.LEFT)
        scroll_y.config(command=self.out_text.yview)
        scroll_x.config(command=self.out_text.xview)

        self.frame[-1].pack(padx=1, pady=2)
        self.out_text.config(state='disable')

    def crt_flashtext(self):
        self.frame.append(tk.Frame(self.root, borderwidth=1))
        scroll_y = tk.Scrollbar(self.frame[-1])
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = tk.Scrollbar(self.frame[-1], orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.flash_text = tk.Text(self.frame[-1],height=6, width=120, font=self.my_font, bg=self.my_color[0], fg=self.my_color[1], \
                            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set, wrap='none', relief=tk.FLAT)
        self.flash_text.pack(side=tk.LEFT)
        scroll_y.config(command=self.flash_text.yview)
        scroll_x.config(command=self.flash_text.xview)

        self.frame[-1].pack(padx=1, pady=2)
        self.flash_text.config(state='disable')

    def crt_para(self):
        for line in range(5):
            self.label_var.append(tk.StringVar())
            self.frame.append(tk.Frame(self.root, borderwidth=0))
            in_label = tk.Label(self.frame[-1], width=30, font=self.my_font, textvariable=self.label_var[-1])
            in_label.pack(side=tk.LEFT)

            e = tk.StringVar()
            in_entry = tk.Entry(self.frame[-1], width=90, font=self.my_font, textvariable=e)
            in_entry.pack(side=tk.LEFT)
            e.set("")
            self.windows.append([in_label, in_entry])
            self.para_entrys.append(in_entry)
            self.frame[-1].pack()

    def crt_sel_run(self):
        self.frame.append(tk.Frame(self.root, borderwidth=0))
        self.SelectedFun = tk.IntVar()
        for text, value in [('checksum', 1), ('unique', 2), ('split', 3), ('merge', 4), ('hashdir', 5), ('zip', 6), ('unzip', 7)]:
            tk.Radiobutton(self.frame[-1], text=text, value=value, variable=self.SelectedFun, \
                command=lambda s=self, r=self.SelectedFun: s.SelectedAction(r)).pack(side=tk.LEFT, anchor=tk.W)

        tab_label = tk.Label(self.frame[-1], width=50, font=self.my_font)
        tab_label.pack(side=tk.LEFT)

        tk.Button(self.frame[-1], text='run',
                    borderwidth=1, relief=tk.RAISED, width=10,
                    command=lambda s=self, r=self.SelectedFun: s.RunAction(r))\
                .pack(side=tk.LEFT, padx=1, pady=1)
        self.frame[-1].pack()

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

    def mainloop(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = GUI()
    #app.master.title('Lark')
    app.mainloop()
