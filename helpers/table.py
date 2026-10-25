"""Table: loads an XML table from a plain path or from inside .pak (zip) archives."""

import io
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


class Table:
    """A table loaded from an XML file shaped like:

        <database name="...">
          <weapon_presets version="1">                      <- the table
            <weapon_preset id="..." name="...">             <- a row
              <weapon_preset_item item_class_id="..."/>     <- a sub-item of the row
            </weapon_preset>
          </weapon_presets>
        </database>

    Every row is a dict: its XML attributes become keys (whatever they are
    called, and rows may have different sets of them). Child elements are
    grouped by tag into lists of dicts, e.g.

        {"weapon_preset_id": "...", "weapon_preset_name": "longsword_5_01",
         "weapon_preset_item": [{"item_class_id": "..."}]}

    All values are strings, exactly as in the file.
    """

    def __init__(self):
        self.source = None   # the path string passed to load()
        self.sources = []    # every path loaded or appended, in order
        self.root = None     # the <database> element
        self.element = None  # the table element (e.g. <weapon_presets>)
        self.name = None     # tag of the table element
        self.version = None  # its "version" attribute, if any
        self.rows = []       # list[dict]

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def load(self, path, table=None):
        """Load a table from `path`.

        `path` may be a normal file, or may pass through one or more .pak
        archives, e.g. "Data/Tables.pak/Libs/Tables/Item/weapon_preset.xml".
        Archives are read in memory; nothing is extracted to disk.

        `table` picks the table element by tag if the file holds several;
        by default the first one is used.

        Returns self, so you can write: t = Table().load(path)
        """
        root, element, rows = self._parse(path, table)
        self.source = str(path)
        self.sources = [str(path)]
        self.root = root
        self.element = element
        self.name = element.tag
        self.version = element.get("version")
        self.rows = rows
        return self

    def append(self, path, table=None, strict=True):
        """Add the rows of another file to this table, keeping the existing ones.

        Takes the same kind of `path` as load() (plain file or through .pak
        archives). Returns self, so calls can be chained:

            t = Table().load(a).append(b).append(c)

        If nothing is loaded yet, this behaves like load(). With strict=True
        (the default) the other file's table element must have the same tag
        as the loaded one (e.g. both <soul>), which catches mixing up
        different tables; pass strict=False to append regardless.

        `root`, `element`, `name` and `version` keep describing the first
        file; `sources` lists every file that contributed rows.
        """
        if self.element is None:
            return self.load(path, table)

        _, element, rows = self._parse(path, table)
        if strict and element.tag != self.name:
            raise ValueError(
                f"{path}: table <{element.tag}> doesn't match the loaded table "
                f"<{self.name}> (pass strict=False to append anyway)"
            )
        self.rows.extend(rows)
        self.sources.append(str(path))
        return self

    @classmethod
    def _parse(cls, path, table):
        """Read and parse one file; returns (root, table_element, rows)."""
        data = cls._read_bytes(path)

        if data.startswith(b"CryXmlB"):
            raise ValueError(f"{path}: binary CryXml is not supported, it needs converting to text XML first")

        root = ET.fromstring(data)

        if table is not None:
            element = root.find(table)
            if element is None:
                raise KeyError(f"{path}: no <{table}> element (found: {[c.tag for c in root]})")
        else:
            element = next(iter(root), root)   # first child of <database>

        rows = [cls._row_from_element(el) for el in element] if element is not root else []
        return root, element, rows

    @classmethod
    def _row_from_element(cls, el):
        row = dict(el.attrib)
        text = (el.text or "").strip()
        if text:
            row["_text"] = text
        for child in el:
            row.setdefault(child.tag, []).append(cls._row_from_element(child))
        return row

    @property
    def columns(self):
        """Attribute names used by any row, in order of first appearance."""
        seen = {}
        for row in self.rows:
            for key in row:
                seen.setdefault(key, None)
        return list(seen)

    # ------------------------------------------------------------------
    # Path resolution (real folders -> .pak archive -> folders inside it)
    # ------------------------------------------------------------------
    @classmethod
    def _read_bytes(cls, path):
        parts = Path(str(path).replace("\\", "/")).parts

        # Walk down the real filesystem until we hit a file.
        current = Path()
        for i, part in enumerate(parts):
            current = current / part
            if current.is_file():
                rest = parts[i + 1:]
                if not rest:
                    return current.read_bytes()      # plain file, no archive involved
                with zipfile.ZipFile(current) as zf:
                    return cls._read_from_zip(zf, rest, current)
            if not current.exists():
                break
        raise FileNotFoundError(f"Could not resolve path: {path}")

    @classmethod
    def _read_from_zip(cls, zf, parts, where):
        """Find `parts` inside the open archive `zf`, descending into nested paks."""
        # Case-insensitive lookup, since game paks are often inconsistent.
        names = {n.lower(): n for n in zf.namelist()}

        for j in range(len(parts)):
            prefix = "/".join(parts[: j + 1]).lower()
            if prefix not in names:
                continue                              # still inside a directory
            member = names[prefix]
            if j == len(parts) - 1:
                return zf.read(member)                # found the target file
            # A file in the middle of the path: it's a nested archive.
            inner = zipfile.ZipFile(io.BytesIO(zf.read(member)))
            with inner:
                return cls._read_from_zip(inner, parts[j + 1:], f"{where}/{member}")

        raise FileNotFoundError(f"{'/'.join(parts)} not found inside {where}")

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------
    def where(self, **conditions):
        """Rows whose columns equal all given values: t.where(social_class_id="1")"""
        return [r for r in self.rows if all(r.get(k) == v for k, v in conditions.items())]

    def drop(self, predicate=None, /, **conditions):
        """Remove rows in place and return how many were removed.

        Match by column values, like where():

            t.drop(social_class_id="1")
            t.drop(weapon_preset_name="longsword_5_01", Quality="2")   # both must match

        or with a function that gets each row dict and returns True to drop it:

            t.drop(lambda row: row.get("weapon_preset_name", "").startswith("UC_"))

        If both are given, a row is dropped only when it satisfies both.
        With no condition at all this raises ValueError instead of emptying the
        table by accident; use t.rows.clear() for that.
        """
        if predicate is None and not conditions:
            raise ValueError("drop() needs a condition; use t.rows.clear() to remove every row")

        def matches(row):
            return all(row.get(k) == v for k, v in conditions.items()) and (
                predicate is None or predicate(row)
            )

        kept = [r for r in self.rows if not matches(r)]
        removed = len(self.rows) - len(kept)
        self.rows[:] = kept          # same list object, so outside references stay valid
        return removed

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, index):
        return self.rows[index]

    def __repr__(self):
        return f"<Table {self.name!r} from {self.source!r} rows={len(self.rows)}>"


if __name__ == "__main__":
    import sys

    t = Table().load(sys.argv[1])
    print(t)
    print("columns:", t.columns)
    for row in t.rows[:10]:
        print(row)
