"""Friendly white & blue theme — Times New Roman."""

FONT_FAMILY = "Times New Roman"

COLORS = {
    "bg": "#f7fafc",
    "bg_panel": "#ffffff",
    "bg_card": "#eef5fc",
    "bg_input": "#ffffff",
    "bg_accent_bar": "#2e6eb5",
    "border": "#c5d9ed",
    "accent": "#2e6eb5",
    "accent_hover": "#245a94",
    "accent_dim": "#d4e6f7",
    "accent_light": "#f0f6fc",
    "text": "#1a2e44",
    "text_muted": "#5c7289",
    "text_on_accent": "#ffffff",
    "success": "#2e7d32",
    "warning": "#e65100",
    "danger": "#c62828",
    "cmd_badge": "#245a94",
    "ps_badge": "#5e35b1",
    "bash_badge": "#2e7d32",
}

FONTS = {
    "ui": (FONT_FAMILY, 12),
    "ui_bold": (FONT_FAMILY, 12, "bold"),
    "title": (FONT_FAMILY, 16, "bold"),
    "mono": (FONT_FAMILY, 11),
    "mono_sm": (FONT_FAMILY, 10),
}

CTK_THEME = {
    "CTk": {"fg_color": COLORS["bg"]},
    "CTkFrame": {"fg_color": COLORS["bg_panel"], "border_color": COLORS["border"]},
    "CTkButton": {
        "fg_color": COLORS["accent"],
        "hover_color": COLORS["accent_hover"],
        "text_color": COLORS["text_on_accent"],
        "border_color": COLORS["border"],
    },
    "CTkEntry": {
        "fg_color": COLORS["bg_input"],
        "border_color": COLORS["border"],
        "text_color": COLORS["text"],
        "placeholder_text_color": COLORS["text_muted"],
    },
    "CTkTextbox": {
        "fg_color": COLORS["bg_input"],
        "border_color": COLORS["border"],
        "text_color": COLORS["text"],
    },
    "CTkOptionMenu": {
        "fg_color": COLORS["bg_panel"],
        "button_color": COLORS["accent"],
        "button_hover_color": COLORS["accent_hover"],
        "dropdown_fg_color": COLORS["bg_panel"],
        "text_color": COLORS["text"],
    },
    "CTkSegmentedButton": {
        "fg_color": COLORS["accent_light"],
        "selected_color": COLORS["accent"],
        "selected_hover_color": COLORS["accent_hover"],
        "unselected_color": COLORS["bg_panel"],
        "unselected_hover_color": COLORS["border"],
        "text_color": COLORS["text"],
    },
}
