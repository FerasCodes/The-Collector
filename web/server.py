"""Flask web server — opens in your default browser."""

from __future__ import annotations

import socket
import threading
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from collector.catalog import (
    build_catalog,
    catalog_stats,
    filter_commands,
    get_command_by_id,
    toggle_favorite,
)
from collector.constants import APP_CREDIT, APP_NAME, APP_SUBTITLE, SIDEBAR_CATEGORIES
from collector.paths import resource_path
from collector.profiles import list_profiles, resolve_profile
from collector.script_builder import BuildOptions, build_script

WEB_ROOT = resource_path("web")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def create_app() -> Flask:
    build_catalog(force_rebuild=False)
    app = Flask(
        __name__,
        template_folder=str(WEB_ROOT / "templates"),
        static_folder=str(WEB_ROOT / "static"),
    )

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            app_name=APP_NAME,
            app_subtitle=APP_SUBTITLE,
            app_credit=APP_CREDIT,
        )

    @app.get("/api/stats")
    def api_stats():
        return jsonify(catalog_stats())

    @app.get("/api/categories")
    def api_categories():
        return jsonify(SIDEBAR_CATEGORIES)

    @app.get("/api/commands")
    def api_commands():
        platform = request.args.get("platform", "windows")
        cmds = filter_commands(
            platform=platform,
            shell=request.args.get("shell") or None,
            category=request.args.get("category") or None,
            search=request.args.get("search", ""),
            favorites_only=request.args.get("favorites") == "1",
            os_version=request.args.get("os_version") or None,
            linux_distro=request.args.get("linux_distro") or None,
        )
        return jsonify([c.to_dict() for c in cmds])

    @app.get("/api/commands/<cmd_id>")
    def api_command(cmd_id: str):
        cmd = get_command_by_id(cmd_id)
        if not cmd:
            return jsonify({"error": "not found"}), 404
        return jsonify(cmd.to_dict())

    @app.post("/api/favorites/<cmd_id>")
    def api_toggle_favorite(cmd_id: str):
        state = toggle_favorite(cmd_id)
        return jsonify({"id": cmd_id, "favorite": state})

    @app.get("/api/profiles")
    def api_profiles():
        platform = request.args.get("platform")
        items = [
            {"id": p.id, "name": p.name, "description": p.description, "platform": p.platform}
            for p in list_profiles(platform)
        ]
        return jsonify(items)

    @app.post("/api/profiles/<profile_id>/resolve")
    def api_resolve_profile(profile_id: str):
        try:
            cmds = resolve_profile(profile_id, build_catalog())
        except KeyError as exc:
            return jsonify({"error": str(exc)}), 404
        return jsonify([c.to_dict() for c in cmds])

    @app.post("/api/build")
    def api_build():
        data = request.get_json(force=True) or {}
        ids = data.get("command_ids") or []
        catalog = {c.id: c for c in build_catalog()}
        commands = [catalog[i] for i in ids if i in catalog]
        if not commands:
            return jsonify({"error": "no commands selected"}), 400
        platform = data.get("platform", "windows")
        fmt = data.get("format", "auto")
        if platform == "linux":
            fmt = "sh"
        opts = BuildOptions(
            output_format=fmt,
            platform=platform,
            add_error_handling=bool(data.get("add_error_handling", True)),
            add_header=bool(data.get("add_header", True)),
            include_comments=bool(data.get("include_comments", True)),
        )
        result = build_script(commands, opts)
        return jsonify(
            {
                "content": result.content,
                "extension": result.extension,
                "path_hint": result.path_hint,
                "format_label": result.format_label,
                "companion_content": result.companion_content,
                "companion_path_hint": result.companion_path_hint,
            }
        )

    return app


def run_server(open_browser: bool = True, port: int | None = None) -> None:
    app = create_app()
    port = port or _free_port()
    url = f"http://127.0.0.1:{port}"

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    print(f"{APP_NAME} — {APP_SUBTITLE}")
    print(f"Open in browser: {url}")
    print("Press Ctrl+C to stop.")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    run_server()
