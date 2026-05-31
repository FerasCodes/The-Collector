"""Extended command packs — KAPE-style artifacts, WEF queries, pentest, triage."""

from __future__ import annotations

from collector.models import CollectorCommand
from collector.packs.config_remote import config_and_remote_commands
from collector.packs.linux_extended import linux_pack_commands
from collector.packs.windows_kape import kape_pack_commands
from collector.packs.windows_misc import misc_windows_pack_commands
from collector.packs.windows_wef import wef_pack_commands


def all_pack_commands() -> list[CollectorCommand]:
    return (
        kape_pack_commands()
        + wef_pack_commands()
        + misc_windows_pack_commands()
        + linux_pack_commands()
        + config_and_remote_commands()
    )
