import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os

class ScrollableFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.canvas = tk.Canvas(self, height=400)  # 限制高度为400
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件
        self.scrollable_frame.bind("<Enter>", self._bind_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbind_mousewheel)

    def _on_mousewheel(self, event):
        # 兼容不同平台的滚动
        if event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

class StudentEntry:
    def __init__(self, parent, index, score_type):
        self.name_var = tk.StringVar()
        self.id_var = tk.StringVar(value=str(index + 1))  # 自动填充学号
        self.score_var = tk.StringVar(value='0')

        self.name_entry = tk.Entry(parent, textvariable=self.name_var)
        self.id_entry = tk.Entry(parent, textvariable=self.id_var, state='readonly')  # 学号不可编辑
        self.score_entry = tk.Entry(parent, textvariable=self.score_var, state='readonly')

        self.add_button = tk.Button(parent, text='加分', command=lambda: self.modify_score(1))
        self.sub_button = tk.Button(parent, text='减分', command=lambda: self.modify_score(-1))

        self.score_type = score_type  # 'regular' or 'chinese'
        self.index = index  # index from 0 to 49

    def grid(self, row):
        self.name_entry.grid(row=row, column=0)
        self.id_entry.grid(row=row, column=1)
        self.score_entry.grid(row=row, column=2)
        self.add_button.grid(row=row, column=3)
        self.sub_button.grid(row=row, column=4)

    def modify_score(self, delta):
        ModifyScoreWindow(self, delta)

class ModifyScoreWindow:
    def __init__(self, student_entry, delta):
        self.student_entry = student_entry
        self.delta = delta
        self.window = tk.Toplevel()
        if delta > 0:
            self.window.title('加分选项')
        else:
            self.window.title('减分选项')

        tk.Label(self.window, text='请输入分数:').grid(row=0, column=0)
        self.score_entry = tk.Entry(self.window)
        self.score_entry.grid(row=0, column=1)

        tk.Label(self.window, text='请输入密码:').grid(row=1, column=0)
        self.password_entry = tk.Entry(self.window, show='*')
        self.password_entry.grid(row=1, column=1)

        self.confirm_button = tk.Button(self.window, text='确定', command=self.confirm)
        self.confirm_button.grid(row=2, column=0, columnspan=2)

    def confirm(self):
        password = self.password_entry.get()
        if password != '11111':
            messagebox.showerror('错误', '密码错误')
            return
        try:
            score_change = float(self.score_entry.get())
            if self.delta < 0:
                score_change = -score_change
            current_score = float(self.student_entry.score_var.get())
            new_score = current_score + score_change
            if new_score < 0:
                new_score = 0
            self.student_entry.score_var.set(str(new_score))
            save_data()
            self.window.destroy()
        except ValueError:
            messagebox.showerror('错误', '请输入有效的分数')

def save_data():
    with open('data.txt', 'w', encoding='utf-8') as f:
        # Save Chinese scores
        for student in students_chinese:
            name = student.name_var.get()
            student_id = student.id_var.get()
            score = student.score_var.get()
            f.write(f'{name},{student_id},{score}\n')
        # Save Regular scores
        for student in students_regular:
            name = student.name_var.get()
            student_id = student.id_var.get()
            score = student.score_var.get()
            f.write(f'{name},{student_id},{score}\n')

def load_data():
    if not os.path.exists('data.txt'):
        return
    with open('data.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # Load Chinese scores
        for i in range(50):
            if i >= len(lines):
                break
            line = lines[i].strip()
            if line:
                data = line.split(',')
                if len(data) == 3:
                    name, student_id, score = data
                    student = students_chinese[i]
                    student.name_var.set(name)
                    # 不覆盖学号
                    student.score_var.set(score)
        # Load Regular scores
        for i in range(50):
            index = 50 + i
            if index >= len(lines):
                break
            line = lines[index].strip()
            if line:
                data = line.split(',')
                if len(data) == 3:
                    name, student_id, score = data
                    student = students_regular[i]
                    student.name_var.set(name)
                    # 不覆盖学号
                    student.score_var.set(score)

def import_file():
    filepath = filedialog.askopenfilename(title='导入文件', filetypes=[('Text Files', '*.txt')])
    if filepath:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Similar to load_data, but using lines from the selected file
        # Load Chinese scores
        for i in range(50):
            if i >= len(lines):
                break
            line = lines[i].strip()
            if line:
                data = line.split(',')
                if len(data) == 3:
                    name, student_id, score = data
                    student = students_chinese[i]
                    student.name_var.set(name)
                    # 不覆盖学号
                    student.score_var.set(score)
        # Load Regular scores
        for i in range(50):
            index = 50 + i
            if index >= len(lines):
                break
            line = lines[index].strip()
            if line:
                data = line.split(',')
                if len(data) == 3:
                    name, student_id, score = data
                    student = students_regular[i]
                    student.name_var.set(name)
                    # 不覆盖学号
                    student.score_var.set(score)
        save_data()

def show_statistics():
    window = tk.Toplevel()
    window.title('统计结果')

    # Get top 5 Chinese scores
    chinese_scores = []
    for student in students_chinese:
        try:
            score = float(student.score_var.get())
        except ValueError:
            score = 0
        chinese_scores.append((score, student.name_var.get(), student.id_var.get()))
    chinese_scores.sort(reverse=True)
    chinese_top5 = chinese_scores[:5]

    # Get top 5 Regular scores
    regular_scores = []
    for student in students_regular:
        try:
            score = float(student.score_var.get())
        except ValueError:
            score = 0
        regular_scores.append((score, student.name_var.get(), student.id_var.get()))
    regular_scores.sort(reverse=True)
    regular_top5 = regular_scores[:5]

    tk.Label(window, text='语文分前五名').grid(row=0, column=0)
    for i, (score, name, student_id) in enumerate(chinese_top5):
        tk.Label(window, text=f'{i+1}. {name} ({student_id}): {score}').grid(row=i+1, column=0, sticky='w')

    tk.Label(window, text='常规分前五名').grid(row=0, column=1)
    for i, (score, name, student_id) in enumerate(regular_top5):
        tk.Label(window, text=f'{i+1}. {name} ({student_id}): {score}').grid(row=i+1, column=1, sticky='w')

    confirm_button = tk.Button(window, text='确认奖励', command=lambda: confirm_reward(chinese_top5, regular_top5, window))
    confirm_button.grid(row=6, column=0, columnspan=2)

def confirm_reward(chinese_top5, regular_top5, window):
    # Reset Chinese scores of top 5 students
    for score, name, student_id in chinese_top5:
        for student in students_chinese:
            if student.name_var.get() == name and student.id_var.get() == student_id:
                student.score_var.set('0')
                break
    # Reset Regular scores of top 5 students
    for score, name, student_id in regular_top5:
        for student in students_regular:
            if student.name_var.get() == name and student.id_var.get() == student_id:
                student.score_var.set('0')
                break
    save_data()
    messagebox.showinfo('提示', '已清零语文分前五名和常规分前五名的分数')
    window.destroy()

# Main application
root = tk.Tk()
root.title("班级积分管理大师")

# Limit the window size
root.geometry('600x500')

# Menu bar
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="导入文件", command=import_file)
menu_bar.add_cascade(label="文件", menu=file_menu)
root.config(menu=menu_bar)

# Statistics button
statistics_button = tk.Button(root, text='统计', command=show_statistics)
statistics_button.pack()

# Notebook (Tabs)
notebook = ttk.Notebook(root)
tab_regular = ttk.Frame(notebook)
tab_chinese = ttk.Frame(notebook)
notebook.add(tab_regular, text='常规分')
notebook.add(tab_chinese, text='语文分')
notebook.pack(expand=1, fill='both')

# Create scrollable frames
scrollable_regular = ScrollableFrame(tab_regular)
scrollable_chinese = ScrollableFrame(tab_chinese)
scrollable_regular.pack(fill='both', expand=True)
scrollable_chinese.pack(fill='both', expand=True)

# Headers for Chinese tab
tk.Label(scrollable_chinese.scrollable_frame, text='姓名').grid(row=0, column=0)
tk.Label(scrollable_chinese.scrollable_frame, text='学号').grid(row=0, column=1)
tk.Label(scrollable_chinese.scrollable_frame, text='分数').grid(row=0, column=2)
tk.Label(scrollable_chinese.scrollable_frame, text='').grid(row=0, column=3)
tk.Label(scrollable_chinese.scrollable_frame, text='').grid(row=0, column=4)

# Headers for Regular tab
tk.Label(scrollable_regular.scrollable_frame, text='姓名').grid(row=0, column=0)
tk.Label(scrollable_regular.scrollable_frame, text='学号').grid(row=0, column=1)
tk.Label(scrollable_regular.scrollable_frame, text='分数').grid(row=0, column=2)
tk.Label(scrollable_regular.scrollable_frame, text='').grid(row=0, column=3)
tk.Label(scrollable_regular.scrollable_frame, text='').grid(row=0, column=4)

students_regular = []
students_chinese = []

for i in range(50):
    student_entry = StudentEntry(scrollable_regular.scrollable_frame, i, 'regular')
    student_entry.grid(row=i+1)
    students_regular.append(student_entry)

    student_entry = StudentEntry(scrollable_chinese.scrollable_frame, i, 'chinese')
    student_entry.grid(row=i+1)
    students_chinese.append(student_entry)

load_data()
root.mainloop()