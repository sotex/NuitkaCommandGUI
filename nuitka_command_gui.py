import os
import sys

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ttkthemes import ThemedTk


class NuitkaCommandGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nuitka Command GUI")
        # self.root.geometry("1000x950")
        self.root.resizable(False, False)

        # 核心变量库
        self.vars = {
            "script": tk.StringVar(), "out_dir": tk.StringVar(), "out_file": tk.StringVar(),
            "build_mode": tk.StringVar(value="exe_no_console"),
            "standalone": tk.BooleanVar(value=True), "onefile": tk.BooleanVar(value=False),
            "remove_build": tk.BooleanVar(value=True), "uac_admin": tk.BooleanVar(value=False),

            # Windows 资源
            "icon": tk.StringVar(), "splash": tk.StringVar(),
            "company_name": tk.StringVar(), "product_name": tk.StringVar(),
            "copyright": tk.StringVar(), "trademarks": tk.StringVar(),
            "file_version": tk.StringVar(value="1.0.0.0"), "prod_version": tk.StringVar(value="1.0.0.0"),
            "file_desc": tk.StringVar(),

            # 编译器控制
            "use_jobs": tk.BooleanVar(value=False),  # 线程数勾选开关
            "jobs": tk.StringVar(value=str(os.cpu_count())), "lto": tk.StringVar(value="yes"),
            "clang": tk.BooleanVar(), "mingw64": tk.BooleanVar(), "static_lib": tk.BooleanVar(),
            "console_mode": tk.StringVar(value="force"),
            "stdout_spec": tk.StringVar(), "stderr_spec": tk.StringVar(),

            # 控制导入的模块
            "follow_imports": tk.StringVar(),  # "nofollow_import": tk.StringVar(),
            "follow_import_to": tk.StringVar(), "nofollow_import_to": tk.StringVar(),
            "follow_stdlib": tk.BooleanVar(),

            # 插件系统 (细分 Qt 且支持自定义)
            "p_pyqt5": tk.BooleanVar(), "p_pyqt6": tk.BooleanVar(), "p_pyside2": tk.BooleanVar(), "p_pyside6": tk.BooleanVar(),
            "p_numpy": tk.BooleanVar(), "p_torch": tk.BooleanVar(), "p_mpl": tk.BooleanVar(),
            "p_tk": tk.BooleanVar(), "p_gevent": tk.BooleanVar(),
            "custom_plugins": tk.StringVar(),  # 用户手动输入插件名
            "dis_plugins": tk.StringVar(), "user_plugin": tk.StringVar(), "mod_param": tk.StringVar(),

            # 数据与依赖
            "inc_pkg": tk.StringVar(), "inc_pkg_data": tk.StringVar(),
            "inc_files": tk.StringVar(), "inc_dir": tk.StringVar(), "noinc_files": tk.StringVar()
        }

        self._create_widgets()
        self._update_ui_state()

        # 绑定联动逻辑
        self.vars["build_mode"].trace_add("write", self._update_ui_state)
        self.vars["use_jobs"].trace_add("write", self._update_jobs_state)

    def _update_ui_state(self, *args):
        mode = self.vars["build_mode"].get()
        is_exe = mode.startswith("exe")
        state = "normal" if is_exe else "disabled"
        for w in self.exe_widgets:
            w.configure(state=state)

    def _update_jobs_state(self, *args):
        """联动：勾选复选框后才允许输入线程数"""
        if self.vars["use_jobs"].get():
            self.entry_jobs.configure(state="normal")
        else:
            self.entry_jobs.configure(state="disabled")

    def _row(self, master, lbl, var, cmd=None, r=0, width=72):
        ttk.Label(master, text=lbl).grid(row=r, column=0, sticky="w", padx=5)
        ent = ttk.Entry(master, textvariable=var, width=width)
        ent.grid(row=r, column=1, padx=10, pady=3, sticky="w")
        if cmd:
            btn = ttk.Button(master, text="...", width=5, command=cmd)
            btn.grid(row=r, column=2)
            return ent, btn
        return ent

    def _create_widgets(self):
        # 顶部路径
        top = ttk.LabelFrame(self.root, text=" 核心输出路径 ", padding=10)
        top.pack(fill="x", padx=15, pady=5)
        self._row(top, "入口脚本:", self.vars["script"], lambda: self._sel_file(self.vars["script"]), 0)
        self._row(top, "输出目录:", self.vars["out_dir"], lambda: self._sel_dir(self.vars["out_dir"]), 1)
        self._row(top, "输出文件名:", self.vars["out_file"], None, 2, 35)

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=15, pady=5)

        # Tab 1: 模式与 IO
        t1 = ttk.Frame(nb)
        nb.add(t1, text=" 📦 编译模式/IO ")
        self._build_tab_mode(t1)

        # Tab 2: Windows 特定
        t2 = ttk.Frame(nb)
        nb.add(t2, text=" 🖼️ Windows 资源/版权 ")
        self._build_tab_win(t2)

        # Tab 3: 优化与编译器
        t3 = ttk.Frame(nb)
        nb.add(t3, text=" ⚙️ 编译优化/编译器 ")
        self._build_tab_opt(t3)

        # Tab 4: 插件与数据
        t4 = ttk.Frame(nb)
        nb.add(t4, text=" 🔌 插件/数据管理 ")
        self._build_tab_plugin(t4)

        # 底部区域
        bot = ttk.Frame(self.root, padding=10)
        bot.pack(fill="x")
        self.cmd_box = tk.Text(bot, height=10, bg="#1e1e1e", fg="#DCDCAA", font=("Consolas", 10))
        self.cmd_box.pack(fill="x", padx=5)

        btn_f = ttk.Frame(bot)
        btn_f.pack(pady=10)
        ttk.Button(btn_f, text="🚀 生成 Nuitka 命令", width=25, command=self.generate).pack(side="left", padx=10)
        ttk.Button(btn_f, text="📋 复制到剪贴板", width=15, command=self.copy_cmd).pack(side="left", padx=10)

    def _build_tab_mode(self, f):
        inner = ttk.Frame(f, padding=15)
        inner.pack(fill="both")

        self.exe_widgets = []
        m_f = ttk.LabelFrame(inner, text=" 程序输出模式 ", padding=10)
        m_f.pack(fill="x")
        ttk.Radiobutton(m_f, text="窗口程序 (Hide Console)",
                        variable=self.vars["build_mode"], value="exe_no_console").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(m_f, text="命令行程序 (Show Console)",
                        variable=self.vars["build_mode"], value="exe_console").grid(row=0, column=1, padx=10)
        ttk.Radiobutton(m_f, text="模块 (PYD/DLL)",
                        variable=self.vars["build_mode"], value="module_pyd").grid(row=0, column=2, padx=10)

        opt_f = ttk.LabelFrame(inner, text=" 核心行为开关 ", padding=10)
        opt_f.pack(fill="x", pady=10)
        c1 = ttk.Checkbutton(opt_f, text="独立分发 (--standalone)", variable=self.vars["standalone"])
        c1.grid(row=0, column=0, padx=10)
        self.exe_widgets.append(c1)
        c2 = ttk.Checkbutton(opt_f, text="单文件模式 (--onefile)", variable=self.vars["onefile"])
        c2.grid(row=0, column=1, padx=10)
        self.exe_widgets.append(c2)
        c3 = ttk.Checkbutton(opt_f, text="管理员权限 (UAC)", variable=self.vars["uac_admin"])
        c3.grid(row=0, column=2, padx=10)
        self.exe_widgets.append(c3)
        ttk.Checkbutton(opt_f, text="编译后清理临时目录", variable=self.vars["remove_build"]).grid(
            row=1, column=0, padx=10, pady=5)

        io_f = ttk.LabelFrame(inner, text=" 标准流定向与控制台 ", padding=10)
        io_f.pack(fill="x")
        ttk.Label(io_f, text="控制台模式:").grid(row=0, column=0)
        ttk.Combobox(io_f, textvariable=self.vars["console_mode"], values=[
                     "attach", "force", "hide"], width=10).grid(row=0, column=1, sticky="w", padx=10)
        self._row(io_f, "标准输出文件:", self.vars["stdout_spec"], None, 1, 50)
        self._row(io_f, "标准错误文件:", self.vars["stderr_spec"], None, 2, 50)

    def _build_tab_win(self, f):
        inner = ttk.Frame(f, padding=15)
        inner.pack(fill="both")
        self._row(inner, "程序图标 (.ico):", self.vars["icon"],
                  lambda: self._sel_file(self.vars["icon"], [("ICO", "*.ico")]), 0, 65)
        self._row(inner, "启动画面 (.png):", self.vars["splash"],
                  lambda: self._sel_file(self.vars["splash"], [("PNG", "*.png")]), 1, 65)
        meta = [("公司名称:", "company_name"), ("产品名称:", "product_name"), ("版权信息:", "copyright"), ("注册商标:", "trademarks"),
                ("程序描述:", "file_desc"), ("文件版本:", "file_version"), ("产品版本:", "prod_version")]
        for i, (l, v) in enumerate(meta):
            self._row(inner, l, self.vars[v], None, i+2, 65)

    def _build_tab_opt(self, f):
        inner = ttk.Frame(f, padding=15)
        inner.pack(fill="both")
        c_f = ttk.LabelFrame(inner, text=" 编译器选择与链接 ", padding=10)
        c_f.pack(fill="x")
        ttk.Checkbutton(c_f, text="强制使用 Clang", variable=self.vars["clang"]).grid(row=0, column=0, padx=10)
        ttk.Checkbutton(c_f, text="强制使用 MinGW64", variable=self.vars["mingw64"]).grid(row=0, column=1, padx=10)
        ttk.Checkbutton(c_f, text="静态链接 C++ 库", variable=self.vars["static_lib"]).grid(row=0, column=2, padx=10)

        # 强制使用 Clang 和 强制使用 MinGW64 不能同时启用
        def check_clang(cc: str):
            clang = self.vars["clang"].get()
            mingw64 = self.vars["mingw64"].get()
            if cc == "clang" and (clang and mingw64):
                self.vars["mingw64"].set(False)
            elif cc == "mingw64" and (clang and mingw64):
                self.vars["clang"].set(False)

        self.vars["clang"].trace_add("write", lambda *args:   check_clang("clang"))
        self.vars["mingw64"].trace_add("write", lambda *args: check_clang("mingw64"))

        p_f = ttk.LabelFrame(inner, text=" 性能参数 ", padding=10)
        p_f.pack(fill="x", pady=10)
        ttk.Checkbutton(p_f, text="指定编译线程:", variable=self.vars["use_jobs"]).grid(row=0, column=0)
        self.entry_jobs = ttk.Entry(p_f, textvariable=self.vars["jobs"], width=8, state="disabled")
        self.entry_jobs.grid(row=0, column=1, padx=5)
        ttk.Label(p_f, text="LTO 优化等级:").grid(row=0, column=2, padx=10)
        ttk.Combobox(p_f, textvariable=self.vars["lto"], values=["yes", "no", "auto"], width=8).grid(row=0, column=3)

        p_f = ttk.LabelFrame(inner, text=" 导入模块控制 ", padding=10)
        p_f.pack(fill="x", pady=10)
        ttk.Checkbutton(p_f, text="跟随导入(--follow-imports)",
                        variable=self.vars["follow_imports"]).grid(row=0, column=0, padx=10)
        ttk.Checkbutton(p_f, text="跟随导入标准库(--follow-stdlib)",
                        variable=self.vars["follow_stdlib"]).grid(row=0, column=1, padx=10)
        self._row(p_f, "指定包跟随导入:", self.vars["follow_import_to"], None, 1, 50)
        self._row(p_f, "指定包不跟随导入:", self.vars["nofollow_import_to"], None, 2, 50)

    def _build_tab_plugin(self, f):
        inner = ttk.Frame(f, padding=15)
        inner.pack(fill="both")
        p_f = ttk.LabelFrame(inner, text=" 插件启用 (--enable-plugins) ", padding=10)
        p_f.pack(fill="x")

        # Qt 细分选项
        qts = [("PyQt5", "p_pyqt5"), ("PyQt6", "p_pyqt6"), ("PySide2", "p_pyside2"), ("PySide6", "p_pyside6")]
        qt_f = ttk.LabelFrame(p_f, text=" Qt 框架选择 ", padding=5)
        qt_f.grid(row=0, column=0, rowspan=4, columnspan=1, sticky="ew", pady=5)
        for i, (t, v) in enumerate(qts):
            ttk.Checkbutton(qt_f, text=t, variable=self.vars[v]).grid(row=i//2, column=i % 2, sticky="ew", padx=5)

        # 其他内置插件勾选
        pls = [("Numpy", "p_numpy"), ("PyTorch", "p_torch"),
               ("Matplotlib", "p_mpl"), ("Tkinter", "p_tk"), ("Gevent", "p_gevent")]
        for i, (t, v) in enumerate(pls):
            ttk.Checkbutton(p_f, text=t, variable=self.vars[v]).grid(
                row=i//2, column=1+i % 2, padx=15, pady=5, sticky="w")

        # 用户自定义插件输入
        ttk.Label(p_f, text="其他自定义插件 (逗号隔开):").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(p_f, textvariable=self.vars["custom_plugins"], width=55).grid(
            row=4, column=1, columnspan=2, sticky="w", padx=5)

        data_f = ttk.LabelFrame(inner, text=" 数据与自定义扩展 ", padding=10)
        data_f.pack(fill="x", pady=10)
        opts = [("包含包数据:", "inc_pkg_data"), ("包含文件 (S=D):", "inc_files"), ("包含目录 (S=D):", "inc_dir"),
                ("强制包含包:", "inc_pkg"), ("禁用插件:", "dis_plugins"), ("用户插件路径:", "user_plugin")]
        for i, (l, v) in enumerate(opts):
            self._row(data_f, l, self.vars[v], None, i, 66)

    def _sel_file(self, var, ft=None):
        p = filedialog.askopenfilename(filetypes=ft or [("Python", "*.py")])
        if p:
            var.set(os.path.normpath(p))

    def _sel_dir(self, var):
        p = filedialog.askdirectory()
        if p:
            var.set(os.path.normpath(p))

    def generate(self):
        v = self.vars
        if not v["script"].get():
            return messagebox.showerror("错误", "入口脚本缺失")
        cmd = [f'"{sys.executable}"', "-m", "nuitka"]
        mode = v["build_mode"].get()

        # 1. 基础模式
        if mode == "module_pyd":
            cmd.append("--module")
        else:
            if v["standalone"].get():
                cmd.append("--standalone")
            if v["onefile"].get():
                cmd.append("--onefile")
            if mode == "exe_no_console":
                cmd.append("--windows-disable-console")
            if v["uac_admin"].get():
                cmd.append("--windows-uac-admin")
            cmd.append(f'--windows-console-mode={v["console_mode"].get()}')
            if v["icon"].get():
                cmd.append(f'--windows-icon-from-ico="{v["icon"].get()}"')
            if v["splash"].get():
                cmd.append(f'--onefile-windows-splash-screen-image="{v["splash"].get()}"')

        # 2. 版本与版权
        meta = {"--windows-company-name": "company_name", "--windows-product-name": "product_name",
                "--copyright": "copyright", "--trademarks": "trademarks",
                "--windows-file-description": "file_desc", "--windows-file-version": "file_version",
                "--windows-product-version": "prod_version"}
        for flag, key in meta.items():
            if v[key].get():
                cmd.append(f'{flag}="{v[key].get()}"')

        # 3. 性能优化与编译器
        if v["use_jobs"].get():
            cmd.append(f'--jobs={v["jobs"].get()}')
        cmd.append(f'--lto={v["lto"].get()}')
        if v["remove_build"].get():
            cmd.append("--remove-output")
        if v["clang"].get():
            cmd.append("--clang")
        if v["mingw64"].get():
            cmd.append("--mingw64")
        if v["static_lib"].get():
            cmd.append("--static-libpython=no")

        if v["follow_import"].get():
            cmd.append("--follow-imports")
        if v["follow_stdlib"].get():
            cmd.append("--follow-stdlib")
        if v["follow_import_to"].get():
            cmd.append(f"--follow-import-to=\"{v["follow_import_to"].get()}\"")
        if v["nofollow_import_to"].get():
            cmd.append(f"--nofollow-import-to=\"{v["nofollow_import_to"].get()}\"")

        # 4. 流重定向
        if v["stdout_spec"].get():
            cmd.append(f'--force-stdout-spec="{v["stdout_spec"].get()}"')
        if v["stderr_spec"].get():
            cmd.append(f'--force-stderr-spec="{v["stderr_spec"].get()}"')

        # 5. 插件处理 (核心更新)
        pls_map = {"p_pyqt5": "pyqt5", "p_pyqt6": "pyqt6", "p_pyside2": "pyside2", "p_pyside6": "pyside6",
                   "p_numpy": "numpy", "p_torch": "torch", "p_mpl": "matplotlib", "p_tk": "tk-inter", "p_gevent": "gevent"}
        for vk, pk in pls_map.items():
            if v[vk].get():
                cmd.append(f"--enable-plugin={pk}")
        if v["custom_plugins"].get():
            for p in v["custom_plugins"].get().split(","):
                if p.strip():
                    cmd.append(f"--enable-plugin={p.strip()}")

        # 6. 数据文件
        for flag, key in [("--include-package-data", "inc_pkg_data"), ("--include-data-files", "inc_files"),
                          ("--include-data-dir", "inc_dir"), ("--include-package", "inc_pkg")]:
            if v[key].get():
                for item in v[key].get().split(","):
                    cmd.append(f'{flag}={item.strip()}')

        if v["out_dir"].get():
            cmd.append(f'--output-dir="{v["out_dir"].get()}"')
        if v["out_file"].get():
            cmd.append(f'--output-filename="{v["out_file"].get()}"')
        cmd.append(f'"{v["script"].get()}"')

        self.cmd_box.delete(1.0, tk.END)
        self.cmd_box.insert(tk.END, " ".join(cmd))

    def copy_cmd(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.cmd_box.get(1.0, tk.END).strip())
        messagebox.showinfo("成功", "命令已复制")


if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = NuitkaCommandGUI(root)
    root.mainloop()
