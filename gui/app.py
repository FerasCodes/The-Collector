"""The Collector studio GUI — white & blue layout."""

from __future__ import annotations

import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    import customtkinter as ctk

    CTK = True
except ImportError:
    ctk = None
    CTK = False

from collector.catalog import (
    build_catalog,
    catalog_stats,
    category_counts,
    filter_commands,
    shell_counts,
    toggle_favorite,
)
from collector.profiles import list_profiles, resolve_profile
from collector.constants import APP_CREDIT, APP_NAME, APP_SUBTITLE, SIDEBAR_CATEGORIES
from collector.models import CollectorCommand
from collector.script_builder import BuildOptions, ScriptBuildResult, build_script
from gui.branding import apply_window_icon, load_header_logo
from gui.theme import COLORS, CTK_THEME, FONTS


class CollectorStudio(ctk.CTk if CTK else tk.Tk):  # type: ignore[misc]
    def __init__(self) -> None:
        if CTK:
            super().__init__()
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
        else:
            super().__init__()
        self.title(f"{APP_NAME} — {APP_SUBTITLE}")
        self.geometry("1440x900")
        self.minsize(1200, 720)
        if CTK:
            self.configure(fg_color=COLORS["bg"])
        apply_window_icon(self)

        build_catalog(force_rebuild=False)

        self.platform = tk.StringVar(value="windows")
        self.os_version = tk.StringVar(value="11")
        self.linux_distro = tk.StringVar(value="generic")
        self.shell_filter = tk.StringVar(value="all")
        self.category_filter = tk.StringVar(value="All")
        self.search_var = tk.StringVar(value="")
        self.output_format = tk.StringVar(value="auto")
        self._last_build: ScriptBuildResult | None = None
        self.add_error_handling = tk.BooleanVar(value=True)
        self.add_header = tk.BooleanVar(value=True)
        self.include_comments = tk.BooleanVar(value=True)

        self.selected_command: CollectorCommand | None = None
        self.builder_queue: list[CollectorCommand] = []
        self._run_process: subprocess.Popen[str] | None = None
        self.favorites_only_mode = False
        self._profile_display_to_id: dict[str, str] = {}

        self._build_ui()
        self._update_repo_stats()
        self._refresh_command_list()
        self._update_preview()

    def _frame(self, parent, **kw):
        if CTK:
            kw.setdefault("fg_color", COLORS["bg_panel"])
            kw.setdefault("border_color", COLORS["border"])
            kw.setdefault("corner_radius", 12)
            return ctk.CTkFrame(parent, **kw)
        f = tk.Frame(parent, bg=COLORS["bg_panel"], **kw)
        return f

    def _label(self, parent, text, *, bold=False, muted=False, mono=False):
        color = COLORS["text_muted"] if muted else COLORS["text"]
        font = FONTS["mono"] if mono else (FONTS["ui_bold"] if bold else FONTS["ui"])
        if CTK:
            return ctk.CTkLabel(parent, text=text, text_color=color, font=font)
        return tk.Label(parent, text=text, fg=color, bg=COLORS["bg_panel"], font=font)

    def _button(self, parent, text, command, *, primary=False, width=100):
        if CTK:
            return ctk.CTkButton(
                parent,
                text=text,
                command=command,
                width=width,
                fg_color=COLORS["accent"] if primary else COLORS["bg_panel"],
                hover_color=COLORS["accent_hover"] if primary else COLORS["accent_light"],
                text_color=COLORS["text_on_accent"] if primary else COLORS["text"],
                border_color=COLORS["border"],
                border_width=1 if not primary else 0,
            )
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=COLORS["accent"] if primary else COLORS["bg_panel"],
            fg=COLORS["text_on_accent"] if primary else COLORS["text"],
            activebackground=COLORS["accent_hover"],
            relief=tk.FLAT,
            padx=8,
            pady=4,
        )
        return btn

    def _entry(self, parent, textvariable, placeholder=""):
        if CTK:
            return ctk.CTkEntry(
                parent,
                textvariable=textvariable,
                placeholder_text=placeholder,
                fg_color=COLORS["bg_input"],
                border_color=COLORS["border"],
            )
        e = tk.Entry(parent, textvariable=textvariable, bg=COLORS["bg_input"], fg=COLORS["text"], insertbackground=COLORS["text"])
        return e

    def _text(self, parent, height=10, mono=True):
        if CTK:
            return ctk.CTkTextbox(
                parent,
                height=height * 20,
                font=FONTS["mono"] if mono else FONTS["ui"],
                fg_color=COLORS["bg_input"],
                text_color=COLORS["text"],
                border_color=COLORS["border"],
            )
        t = tk.Text(
            parent,
            height=height,
            bg=COLORS["bg_input"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            font=FONTS["mono"] if mono else FONTS["ui"],
            relief=tk.FLAT,
            wrap=tk.WORD,
        )
        return t

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_top_bar()
        self._build_sidebar()
        self._build_main_panes()
        self._build_status_bar()

    def _build_top_bar(self) -> None:
        bar = self._frame(self)
        bar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=8, pady=(8, 4))
        bar.grid_columnconfigure(1, weight=1)

        brand = self._frame(bar)
        brand.grid(row=0, column=0, padx=12, pady=8, sticky="w")
        self._logo_img = load_header_logo(40)
        if self._logo_img:
            tk.Label(brand, image=self._logo_img, bg=COLORS["bg_panel"]).pack(side="left", padx=(0, 10))
        title_col = self._frame(brand)
        title_col.pack(side="left")
        self._label(title_col, APP_NAME, bold=True).pack(anchor="w")
        self._label(title_col, APP_SUBTITLE, muted=True).pack(anchor="w")
        self.repo_stats_label = self._label(title_col, "", muted=False)
        self.repo_stats_label.pack(anchor="w", pady=(2, 0))
        self._label(title_col, APP_CREDIT, muted=True).pack(anchor="w")
        search = self._entry(bar, self.search_var, "Type to search commands...")
        search.grid(row=0, column=1, sticky="ew", padx=8, pady=8)
        self.search_var.trace_add("write", lambda *_: self._refresh_command_list())

        plat = ctk.CTkSegmentedButton if CTK else None
        if CTK:
            seg = ctk.CTkSegmentedButton(
                bar,
                values=["windows", "linux"],
                command=self._on_platform_change,
                variable=self.platform,
                fg_color=CTK_THEME["CTkSegmentedButton"]["fg_color"],
                selected_color=CTK_THEME["CTkSegmentedButton"]["selected_color"],
                unselected_color=CTK_THEME["CTkSegmentedButton"]["unselected_color"],
                text_color=CTK_THEME["CTkSegmentedButton"]["text_color"],
            )
            seg.grid(row=0, column=2, padx=4)
        else:
            for i, p in enumerate(("windows", "linux")):
                tk.Radiobutton(
                    bar,
                    text=p.title(),
                    variable=self.platform,
                    value=p,
                    command=self._on_platform_change,
                    bg=COLORS["bg_panel"],
                    fg=COLORS["text"],
                    selectcolor=COLORS["bg_card"],
                ).grid(row=0, column=2 + i)

        self._button(bar, "Run script", self._run_script, primary=True, width=95).grid(row=0, column=4, padx=4)
        self._button(bar, "Save", self._save_script, width=80).grid(row=0, column=5, padx=4)
        self._button(bar, "Export", self._export_script, width=80).grid(row=0, column=6, padx=(4, 12))

    def _build_sidebar(self) -> None:
        side = self._frame(self, width=220)
        side.grid(row=1, column=0, sticky="nsw", padx=(8, 4), pady=4)
        side.grid_propagate(False)

        self._label(side, "Menu", bold=True).pack(anchor="w", padx=12, pady=(12, 4))

        stats_frame = tk.Frame(side, bg=COLORS["accent"], padx=10, pady=8)
        stats_frame.pack(fill="x", padx=12, pady=(0, 8))
        self.sidebar_repo_label = tk.Label(
            stats_frame,
            text="",
            fg=COLORS["text_on_accent"],
            bg=COLORS["accent"],
            font=FONTS["ui_bold"],
            justify="left",
            wraplength=180,
        )
        self.sidebar_repo_label.pack(anchor="w")

        for label, handler in [
            ("Browse all commands", self._show_all_commands),
            ("My favorites", self._show_favorites),
        ]:
            btn = self._button(side, label, handler, width=180)
            btn.pack(fill="x", padx=12, pady=2)

        self._label(side, "Quick start", bold=True).pack(anchor="w", padx=12, pady=(16, 4))
        self._label(side, "Pick a ready-made collection", muted=True).pack(anchor="w", padx=12, pady=(0, 4))
        self.profile_choice = tk.StringVar(value="")
        self._refresh_profile_menu()
        if CTK:
            self.profile_menu = ctk.CTkOptionMenu(
                side,
                variable=self.profile_choice,
                values=list(self._profile_display_to_id.keys()) or ["(none)"],
                command=lambda _: None,
                width=180,
            )
            self.profile_menu.pack(fill="x", padx=12, pady=4)
        else:
            self.profile_menu = ttk.Combobox(
                side,
                textvariable=self.profile_choice,
                values=list(self._profile_display_to_id.keys()),
                state="readonly",
                width=22,
            )
            self.profile_menu.pack(fill="x", padx=12, pady=4)
        prof_row = tk.Frame(side, bg=COLORS["bg_panel"])
        prof_row.pack(fill="x", padx=12, pady=4)
        self._button(prof_row, "Use this profile", self._load_selected_profile, primary=True, width=100).pack(
            side="left", padx=(0, 4)
        )
        self._button(prof_row, "Clear script", self._clear_builder, width=85).pack(side="left")

        self._label(side, "Browse by topic", bold=True).pack(anchor="w", padx=12, pady=(16, 4))
        self.category_list = tk.Listbox(
            side,
            bg=COLORS["bg_input"],
            fg=COLORS["text"],
            selectbackground=COLORS["accent"],
            selectforeground=COLORS["text_on_accent"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            borderwidth=0,
            height=12,
            font=FONTS["ui"],
        )
        self.category_list.pack(fill="x", padx=12, pady=4)
        self.category_list.insert(0, "All")
        for cat in SIDEBAR_CATEGORIES:
            self.category_list.insert(tk.END, cat)
        self.category_list.bind("<<ListboxSelect>>", self._on_category_select)

        self._label(side, "Command type", bold=True).pack(anchor="w", padx=12, pady=(12, 4))
        for shell in ("all", "cmd", "powershell", "bash"):
            if CTK:
                ctk.CTkRadioButton(
                    side,
                    text=shell.upper() if shell != "all" else "All",
                    variable=self.shell_filter,
                    value=shell,
                    command=self._refresh_command_list,
                ).pack(anchor="w", padx=16, pady=2)
            else:
                tk.Radiobutton(
                    side,
                    text=shell.upper() if shell != "all" else "All",
                    variable=self.shell_filter,
                    value=shell,
                    command=self._refresh_command_list,
                    bg=COLORS["bg_panel"],
                    fg=COLORS["text"],
                    selectcolor=COLORS["bg_card"],
                ).pack(anchor="w", padx=16)

        self._label(side, "OS / Distro", bold=True).pack(anchor="w", padx=12, pady=(12, 4))
        if CTK:
            ctk.CTkOptionMenu(
                side,
                values=["xp", "vista", "7", "8", "8.1", "10", "11"],
                variable=self.os_version,
                command=lambda _: self._refresh_command_list(),
            ).pack(fill="x", padx=12, pady=2)
            ctk.CTkOptionMenu(
                side,
                values=["generic", "rhel", "ubuntu"],
                variable=self.linux_distro,
                command=lambda _: self._refresh_command_list(),
            ).pack(fill="x", padx=12, pady=2)

        self.shell_count_label = self._label(side, "", muted=True)
        self.shell_count_label.pack(anchor="w", padx=12, pady=8)

    def _build_main_panes(self) -> None:
        center = self._frame(self)
        center.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        center.grid_rowconfigure(1, weight=1)
        center.grid_columnconfigure(0, weight=1)

        # Command list
        list_frame = self._frame(center)
        list_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        list_hdr = self._frame(list_frame)
        list_hdr.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        self._label(list_hdr, "Commands", bold=True).pack(side="left")
        self.list_filter_count = self._label(list_hdr, "", muted=True)
        self.list_filter_count.pack(side="right")

        cols = ("fav", "name", "description")
        self.cmd_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=COLORS["bg_input"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["bg_input"],
            borderwidth=0,
            rowheight=26,
        )
        style.configure("Treeview.Heading", background=COLORS["bg_card"], foreground=COLORS["text_muted"])
        style.map(
            "Treeview",
            background=[("selected", COLORS["accent_light"])],
            foreground=[("selected", COLORS["text"])],
        )
        col_widths = {"fav": 40, "name": 240, "description": 380}
        headings = {"fav": "★", "name": "Command name", "description": "What it does"}
        for col in cols:
            self.cmd_tree.heading(col, text=headings[col])
            self.cmd_tree.column(col, width=col_widths[col], anchor="center" if col == "fav" else "w")
        self.cmd_tree.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 4))
        self.cmd_tree.bind("<<TreeviewSelect>>", self._on_command_select)
        self.cmd_tree.bind("<Double-1>", self._add_selected_to_builder)
        self.cmd_tree.bind("<space>", lambda _e: self._toggle_favorite_selected())
        self._cmd_menu = tk.Menu(self, tearoff=0, bg=COLORS["bg_card"], fg=COLORS["text"])
        self._cmd_menu.add_command(label="Add to builder", command=self._add_selected_to_builder)
        self._cmd_menu.add_command(label="Toggle favorite", command=self._toggle_favorite_selected)
        self.cmd_tree.bind("<Button-3>", self._show_command_context_menu)

        list_actions = self._frame(list_frame)
        list_actions.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        self._button(list_actions, "Add to favorites", self._toggle_favorite_selected, width=120).pack(
            side="left", padx=(0, 6)
        )
        self._button(list_actions, "Add to my script", self._add_selected_to_builder, primary=True, width=130).pack(
            side="right"
        )

        # Details
        detail_frame = self._frame(center)
        detail_frame.grid(row=1, column=0, sticky="nsew")
        detail_frame.grid_columnconfigure(0, weight=1)
        self._label(detail_frame, "About this command", bold=True).grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.detail_text = self._text(detail_frame, height=8)
        self.detail_text.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        # Right column: builder + preview + output
        right = self._frame(self)
        right.grid(row=1, column=2, sticky="nsew", padx=(4, 8), pady=4)
        right.grid_rowconfigure(1, weight=1)
        right.grid_rowconfigure(3, weight=1)
        right.grid_columnconfigure(0, weight=1)

        builder_header = self._frame(right)
        builder_header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        self.builder_title = self._label(builder_header, "Your script", bold=True)
        self.builder_title.pack(side="left")
        self._button(builder_header, "Start over", self._clear_builder, width=90).pack(side="right")

        self.builder_frame = self._frame(right)
        self.builder_frame.grid(row=1, column=0, sticky="nsew", padx=8)
        self.builder_frame.grid_rowconfigure(0, weight=1)
        self.builder_frame.grid_columnconfigure(0, weight=1)
        self._setup_builder_scroll()

        opts = self._frame(right)
        opts.grid(row=2, column=0, sticky="ew", padx=8, pady=4)
        self._label(opts, "Save as:").pack(side="left", padx=4)
        fmt_choices = (
            ("auto", "Automatic"),
            ("bat", "Batch file"),
            ("ps1", "PowerShell"),
            ("sh", "Linux shell"),
        )
        for fmt, label in fmt_choices:
            if CTK:
                ctk.CTkRadioButton(
                    opts,
                    text=label,
                    variable=self.output_format,
                    value=fmt,
                    command=self._update_preview,
                    fg_color=COLORS["accent"],
                    hover_color=COLORS["accent_hover"],
                    text_color=COLORS["text"],
                ).pack(side="left", padx=6)
            else:
                tk.Radiobutton(
                    opts,
                    text=label,
                    variable=self.output_format,
                    value=fmt,
                    command=self._update_preview,
                    bg=COLORS["bg_panel"],
                    fg=COLORS["text"],
                    selectcolor=COLORS["bg_input"],
                    activebackground=COLORS["bg_panel"],
                ).pack(side="left", padx=6)
        self.format_hint = self._label(opts, "", muted=True)
        self.format_hint.pack(side="left", padx=8)
        if CTK:
            ctk.CTkCheckBox(opts, text="Show errors", variable=self.add_error_handling, command=self._update_preview).pack(
                side="left", padx=8
            )
            ctk.CTkCheckBox(opts, text="Title lines", variable=self.add_header, command=self._update_preview).pack(side="left")
            ctk.CTkCheckBox(opts, text="Notes in script", variable=self.include_comments, command=self._update_preview).pack(
                side="left"
            )

        self._label(right, "Preview", bold=True).grid(row=3, column=0, sticky="nw", padx=8, pady=(8, 0))
        self.preview_text = self._text(right, height=12)
        self.preview_text.grid(row=4, column=0, sticky="nsew", padx=8, pady=4)

        out_bar = self._frame(right)
        out_bar.grid(row=5, column=0, sticky="ew", padx=8)
        self._label(out_bar, "Results", bold=True).pack(side="left", padx=8, pady=8)
        self._button(out_bar, "Run now", self._run_script, primary=True).pack(side="right", padx=4, pady=4)
        self._button(out_bar, "Stop", self._stop_script).pack(side="right", padx=4, pady=4)
        self._button(out_bar, "Clear", self._clear_output).pack(side="right", padx=4, pady=4)

        self.output_text = self._text(right, height=10)
        self.output_text.grid(row=6, column=0, sticky="nsew", padx=8, pady=(0, 8))

        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=2)

    def _build_status_bar(self) -> None:
        bar = self._frame(self)
        bar.grid(row=2, column=0, columnspan=3, sticky="ew", padx=8, pady=(0, 8))
        self.status_label = self._label(bar, "Ready", muted=True)
        self.status_label.pack(side="left", padx=12, pady=6)
        self.count_label = self._label(bar, "", muted=True)
        self.count_label.pack(side="right", padx=12)
        self._label(bar, APP_CREDIT, muted=True).pack(side="right", padx=8, pady=6)

    def _setup_builder_scroll(self) -> None:
        """Scrollable script-builder queue (CTkScrollableFrame or Canvas fallback)."""
        if CTK:
            self.builder_scroll = ctk.CTkScrollableFrame(
                self.builder_frame,
                fg_color=COLORS["bg_panel"],
                scrollbar_button_color=COLORS["accent"],
                scrollbar_button_hover_color=COLORS["accent_hover"],
            )
            self.builder_scroll.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
            self.builder_inner = self.builder_scroll
            return

        container = tk.Frame(self.builder_frame, bg=COLORS["bg_panel"], highlightbackground=COLORS["border"], highlightthickness=1)
        container.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._builder_canvas = tk.Canvas(
            container,
            bg=COLORS["bg_panel"],
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self._builder_canvas.yview)
        self._builder_canvas.configure(yscrollcommand=scrollbar.set)
        self._builder_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.builder_inner = tk.Frame(self._builder_canvas, bg=COLORS["bg_panel"])
        self._builder_window = self._builder_canvas.create_window((0, 0), window=self.builder_inner, anchor="nw")

        def _on_configure(_event=None) -> None:
            self._builder_canvas.configure(scrollregion=self._builder_canvas.bbox("all"))
            self._builder_canvas.itemconfig(self._builder_window, width=self._builder_canvas.winfo_width())

        self.builder_inner.bind("<Configure>", _on_configure)
        self._builder_canvas.bind("<Configure>", _on_configure)

        def _scroll_builder(event) -> None:
            self._builder_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_wheel(_event=None) -> None:
            self._builder_canvas.bind_all("<MouseWheel>", _scroll_builder)

        def _unbind_wheel(_event=None) -> None:
            self._builder_canvas.unbind_all("<MouseWheel>")

        self._builder_canvas.bind("<Enter>", _bind_wheel)
        self._builder_canvas.bind("<Leave>", _unbind_wheel)

    def _show_command_context_menu(self, event) -> None:
        row = self.cmd_tree.identify_row(event.y)
        if row:
            self.cmd_tree.selection_set(row)
            self._cmd_menu.tk_popup(event.x_root, event.y_root)

    def _toggle_favorite_selected(self) -> None:
        sel = self.cmd_tree.selection()
        if not sel:
            self._set_status("Select a command to favorite")
            return
        from collector.catalog import get_command_by_id

        cmd = get_command_by_id(sel[0])
        if not cmd:
            return
        is_fav = toggle_favorite(cmd.id)
        cmd.favorite = is_fav
        self._refresh_command_list()
        self._set_status(f"{'Added to' if is_fav else 'Removed from'} favorites: {cmd.name}")

    def _set_text(self, widget, content: str) -> None:
        if CTK and hasattr(widget, "delete"):
            widget.delete("1.0", "end")
            widget.insert("1.0", content)
        else:
            widget.delete("1.0", tk.END)
            widget.insert(tk.END, content)

    def _get_text(self, widget) -> str:
        if CTK and hasattr(widget, "get"):
            return widget.get("1.0", "end").strip()
        return widget.get("1.0", tk.END).strip()

    def _update_repo_stats(self) -> None:
        stats = catalog_stats()
        total, win, lin = stats["total"], stats["windows"], stats["linux"]
        repo_text = f"{total} commands available ({win} Windows, {lin} Linux)"
        sidebar_text = f"{total} commands\n{win} Windows\n{lin} Linux"
        if hasattr(self, "repo_stats_label"):
            self.repo_stats_label.configure(text=repo_text)
            if CTK:
                self.repo_stats_label.configure(text_color=COLORS["accent"], font=FONTS["ui_bold"])
            else:
                self.repo_stats_label.configure(fg=COLORS["accent"], font=FONTS["ui_bold"])
        if hasattr(self, "sidebar_repo_label"):
            self.sidebar_repo_label.configure(text=sidebar_text)

    def _on_platform_change(self, _value: str | None = None) -> None:
        self._refresh_profile_menu()
        self._refresh_command_list()
        if self.platform.get() == "linux":
            self.output_format.set("sh")
        else:
            self.output_format.set("auto")
        self._update_preview()

    def _refresh_profile_menu(self) -> None:
        profiles = list_profiles(self.platform.get())
        self._profile_display_to_id = {p.name: p.id for p in profiles}
        names = list(self._profile_display_to_id.keys())
        if CTK and hasattr(self, "profile_menu"):
            self.profile_menu.configure(values=names or ["(none)"])
        elif hasattr(self, "profile_menu"):
            self.profile_menu["values"] = names
        if names:
            self.profile_choice.set(names[0])

    def _load_selected_profile(self) -> None:
        pid = self._profile_display_to_id.get(self.profile_choice.get())
        if not pid:
            messagebox.showwarning(APP_NAME, "Select a triage profile first.")
            return
        try:
            self.builder_queue = resolve_profile(pid, build_catalog())
        except KeyError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        self._render_builder()
        self._update_preview()
        self._set_status(f"Loaded profile: {self.profile_choice.get()} ({len(self.builder_queue)} steps)")

    def _clear_builder(self) -> None:
        if self.builder_queue and not messagebox.askyesno(APP_NAME, "Clear all commands from the builder?"):
            return
        self.builder_queue = []
        self._render_builder()
        self._update_preview()
        self._set_status("Builder cleared")

    def _show_all_commands(self) -> None:
        self.category_filter.set("All")
        self.favorites_only_mode = False
        self._refresh_command_list()

    def _show_favorites(self) -> None:
        self.category_filter.set("All")
        self.favorites_only_mode = True
        self._refresh_command_list()

    def _on_category_select(self, _event=None) -> None:
        sel = self.category_list.curselection()
        if sel:
            val = self.category_list.get(sel[0])
            self.category_filter.set(val)
            self._refresh_command_list()

    def _refresh_command_list(self) -> None:
        fav_only = self.favorites_only_mode

        plat = self.platform.get()
        os_ver = self.os_version.get() if plat == "windows" else None
        distro = self.linux_distro.get() if plat == "linux" else None

        cmds = filter_commands(
            platform=plat,
            shell=self.shell_filter.get(),
            category=self.category_filter.get(),
            search=self.search_var.get(),
            favorites_only=fav_only,
            os_version=os_ver,
            linux_distro=distro,
        )

        for item in self.cmd_tree.get_children():
            self.cmd_tree.delete(item)
        for cmd in cmds:
            fav_mark = "★" if cmd.favorite else "☆"
            self.cmd_tree.insert(
                "",
                tk.END,
                iid=cmd.id,
                values=(fav_mark, cmd.name, cmd.description[:100]),
            )

        counts = shell_counts(plat)
        parts = [f"{k}: {v}" for k, v in sorted(counts.items())]
        self.shell_count_label.configure(text=" · ".join(parts))
        stats = catalog_stats()
        self.count_label.configure(
            text=f"Showing {len(cmds)} of {stats['total']} · {plat.title()}"
        )
        if hasattr(self, "list_filter_count"):
            self.list_filter_count.configure(text=f"{len(cmds)} shown")

        cats = category_counts(plat)
        # update category counts in sidebar (optional display in status)
        self._set_status(f"Loaded {len(cmds)} commands")

    def _on_command_select(self, _event=None) -> None:
        sel = self.cmd_tree.selection()
        if not sel:
            return
        from collector.catalog import get_command_by_id

        cmd = get_command_by_id(sel[0])
        if not cmd:
            return
        self.selected_command = cmd
        self._render_details(cmd)

    def _render_details(self, cmd: CollectorCommand) -> None:
        params = "\n".join(
            f"  {p.name} ({p.type}) required={p.required} — {p.description}" for p in cmd.parameters
        ) or "  (none)"
        examples = "\n".join(f"  {e}" for e in cmd.examples) or "  (see syntax)"
        text = (
            f"{cmd.name}\n"
            f"{'=' * len(cmd.name)}\n\n"
            f"Description:\n  {cmd.description}\n\n"
            f"Syntax:\n  {cmd.syntax}\n\n"
            f"Shell: {cmd.shell}  |  Output: {cmd.output_type}\n"
            f"OS: {cmd.os_min or 'any'} – {cmd.os_max or 'any'}  |  Platform: {cmd.platform}\n"
            f"Distros: {', '.join(cmd.distros) if cmd.distros else 'all'}\n\n"
            f"Parameters:\n{params}\n\n"
            f"Examples:\n{examples}\n"
        )
        self._set_text(self.detail_text, text)

    def _add_selected_to_builder(self, _event=None) -> None:
        sel = self.cmd_tree.selection()
        if not sel:
            return
        from collector.catalog import get_command_by_id

        cmd = get_command_by_id(sel[0])
        if cmd and cmd not in self.builder_queue:
            self.builder_queue.append(cmd)
            self._render_builder()
            self._update_preview()

    def _render_builder(self) -> None:
        for w in self.builder_inner.winfo_children():
            w.destroy()

        n = len(self.builder_queue)
        if hasattr(self, "builder_title"):
            self.builder_title.configure(text=f"Your script ({n} step{'s' if n != 1 else ''})")

        if not self.builder_queue:
            empty = tk.Label(
                self.builder_inner,
                text="Your script is empty.\n\n1. Pick a command from the list and click “Add to my script”\n   — or —\n2. Use a Quick start profile on the left.",
                fg=COLORS["text_muted"],
                bg=COLORS["bg_panel"],
                font=FONTS["ui"],
                justify="center",
            )
            empty.pack(pady=40, padx=12)
            return

        for cmd in self.builder_queue:
            card = tk.Frame(self.builder_inner, bg=COLORS["bg_card"], padx=10, pady=8)
            card.pack(fill="x", pady=4, padx=4)
            top = tk.Frame(card, bg=COLORS["bg_card"])
            top.pack(fill="x")
            tk.Label(top, text=cmd.name, fg=COLORS["text"], bg=COLORS["bg_card"], font=FONTS["ui_bold"]).pack(
                side="left", anchor="w"
            )
            tk.Label(
                top,
                text=cmd.shell.upper(),
                fg=COLORS["ps_badge"] if cmd.shell == "powershell" else COLORS["cmd_badge"],
                bg=COLORS["bg_card"],
                font=FONTS["mono_sm"],
            ).pack(side="right")
            tk.Label(
                card,
                text=cmd.description[:120],
                fg=COLORS["text_muted"],
                bg=COLORS["bg_card"],
                font=FONTS["ui"],
                wraplength=340,
                justify="left",
            ).pack(anchor="w", pady=(4, 0))
            row = tk.Frame(card, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=(6, 0))
            fav_label = "★ Saved to favorites" if cmd.favorite else "☆ Save to favorites"
            tk.Button(
                row,
                text=fav_label,
                command=lambda c=cmd: self._toggle_fav(c),
                bg=COLORS["accent"] if cmd.favorite else COLORS["accent_light"],
                fg=COLORS["text_on_accent"] if cmd.favorite else COLORS["text"],
                relief=tk.FLAT,
                padx=8,
            ).pack(side="left")
            tk.Button(
                row,
                text="Remove",
                command=lambda c=cmd: self._remove_from_builder(c),
                bg=COLORS["danger"],
                fg=COLORS["text"],
                relief=tk.FLAT,
                padx=10,
            ).pack(side="right")

    def _remove_from_builder(self, cmd: CollectorCommand) -> None:
        self.builder_queue = [c for c in self.builder_queue if c.id != cmd.id]
        self._render_builder()
        self._update_preview()

    def _toggle_fav(self, cmd: CollectorCommand) -> None:
        cmd.favorite = toggle_favorite(cmd.id)
        self._render_builder()
        self._refresh_command_list()
        self._set_status(f"{'Favorited' if cmd.favorite else 'Unfavorited'}: {cmd.name}")

    def _build_options(self) -> BuildOptions:
        fmt = self.output_format.get()
        if self.platform.get() == "linux":
            fmt = "sh"
        return BuildOptions(
            output_format=fmt,
            add_error_handling=self.add_error_handling.get(),
            add_header=self.add_header.get(),
            include_comments=self.include_comments.get(),
            platform=self.platform.get(),
        )

    def _update_preview(self) -> None:
        if self.builder_queue:
            ordered = self.builder_queue
        else:
            required = [c for c in build_catalog() if c.required_step and c.platform == self.platform.get()]
            ids = {c.id for c in required}
            ordered = required + [c for c in self.builder_queue if c.id not in ids]
        if not ordered:
            self._last_build = None
            self._set_text(self.preview_text, "# Add commands from the list to build your collection script.\n")
            if hasattr(self, "format_hint"):
                self.format_hint.configure(text="")
            return
        result = build_script(ordered, self._build_options())
        self._last_build = result
        header = f"# Format: {result.format_label} → {result.path_hint}\n"
        if result.companion_path_hint:
            header += f"# Companion: {result.companion_path_hint}\n"
        header += "# ---\n\n"
        self._set_text(self.preview_text, header + result.content)
        if hasattr(self, "format_hint"):
            hint = result.format_label
            if result.companion_path_hint:
                hint += f" + {result.companion_path_hint}"
            self.format_hint.configure(text=hint)

    def _save_script(self) -> None:
        if not self._last_build:
            messagebox.showwarning(APP_NAME, "Build a script first.")
            return
        ext = self._last_build.extension
        path = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=self._last_build.path_hint,
            filetypes=[("Scripts", "*.bat *.ps1 *.sh"), ("All", "*.*")],
        )
        if path:
            Path(path).write_text(self._last_build.content, encoding="utf-8")
            saved = [path]
            if self._last_build.companion_content and self._last_build.companion_path_hint:
                companion = Path(path).parent / self._last_build.companion_path_hint
                companion.write_text(self._last_build.companion_content, encoding="utf-8")
                saved.append(str(companion))
            self._set_status(f"Saved {', '.join(saved)}")

    def _export_script(self) -> None:
        self._save_script()

    def _run_script(self) -> None:
        if not self._last_build or not self._last_build.content.strip():
            messagebox.showwarning(APP_NAME, "Build a script first.")
            return
        run_dir = Path.home() / ".the-collector" / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        tmp = run_dir / self._last_build.path_hint
        tmp.write_text(self._last_build.content, encoding="utf-8")
        if self._last_build.companion_content and self._last_build.companion_path_hint:
            comp = run_dir / self._last_build.companion_path_hint
            comp.write_text(self._last_build.companion_content, encoding="utf-8")
        self._append_output(f"=== Running {tmp} ===\n")
        ext = self._last_build.extension.lower()
        if ext == ".bat":
            cmd = ["cmd", "/c", str(tmp)]
        elif ext == ".ps1":
            cmd = [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(tmp),
            ]
        else:
            messagebox.showinfo(APP_NAME, "Linux .sh scripts must be run on a Linux host.")
            return

        def worker() -> None:
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
                )
                self._run_process = proc
                out, _ = proc.communicate(timeout=600)
                self.after(0, lambda: self._append_output(out or ""))
                self.after(0, lambda: self._set_status(f"Exit code {proc.returncode}"))
            except subprocess.TimeoutExpired:
                self.after(0, lambda: self._append_output("\n[Timed out]\n"))
            except Exception as exc:
                self.after(0, lambda: self._append_output(f"\n[Error] {exc}\n"))
            finally:
                self._run_process = None

        threading.Thread(target=worker, daemon=True).start()

    def _stop_script(self) -> None:
        if self._run_process and self._run_process.poll() is None:
            self._run_process.terminate()
            self._append_output("\n[Stopped]\n")

    def _clear_output(self) -> None:
        self._set_text(self.output_text, "")

    def _append_output(self, text: str) -> None:
        current = self._get_text(self.output_text)
        self._set_text(self.output_text, current + text)

    def _set_status(self, msg: str) -> None:
        self.status_label.configure(text=msg)


def run_gui() -> None:
    """Desktop GUI replaced by web studio — opens your browser."""
    from web.server import run_server

    run_server(open_browser=True)


if __name__ == "__main__":
    run_gui()
