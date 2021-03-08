#!/usr/bin/env python3

import os
import shutil
import sqlite3
import re
import html
from pathlib import Path


def generate_docset(docset_name, path, search_key):
    root_dir = "output" / Path("{}.docset".format(docset_name))
    content_dir = root_dir / "Contents"
    resource_dir = content_dir / "Resources"
    document_dir = resource_dir / "Documents"

    INSTRUCTION_REGEX = re.compile(r'<h2 class="instruction-section">(.*)<\/h2>')

    document_dir.mkdir(parents=True)

    shutil.copytree(path, document_dir, dirs_exist_ok=True)
    shutil.copy("icon.png", root_dir / "icon.png")

    (content_dir / "Info.plist").write_text(
        """
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
            <key>CFBundleIdentifier</key>
            <string>armv8-a</string>
            <key>CFBundleName</key>
            <string>{}</string>
            <key>DocSetPlatformFamily</key>
            <string>{}</string>
            <key>isDashDocset</key>
            <true/>
    </dict>
    </plist>""".format(docset_name, search_key)
    )

    conn = sqlite3.connect(resource_dir / "docSet.dsidx")
    c = conn.cursor()

    c.execute(
        "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);"
    )
    c.execute("CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);")


    path = Path(document_dir)
    for p in path.glob("*.html"):
        m = INSTRUCTION_REGEX.search(p.read_text())
        if m:
            name = html.unescape(m.group(1))
            entry_type = "Instruction"
            path = p.name

            c.execute(
                "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?);",
                (name, entry_type, path),
            )

    conn.commit()
    conn.close()

generate_docset("Armv8-A", "armv8-a", "arm64")
generate_docset("Armv7-A", "armv7-a", "arm32")
