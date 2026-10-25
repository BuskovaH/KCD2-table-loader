"""Localization: loads key -> text entries from an Excel-style XML file.
Expected shape (the <Table> may be wrapped in <Workbook>/<Worksheet>, and
cells may contain a <Data> element; both are handled):

    <Table>
      <Row><Cell>some_key</Cell><Cell>first text</Cell><Cell>second text</Cell></Row>
      ...
    </Table>
"""

import xml.etree.ElementTree as ET

try:
    from .table import Table          # when used as part of a package
except ImportError:
    from table import Table           # when table.py sits next to this file


def _local(tag):
    """'{namespace}Row' -> 'Row'"""
    return tag.rsplit("}", 1)[-1]


class Localization:
    """Localization entries: the first cell of each row is the key, the
    remaining cells are its texts.

        loc = Localization().load(root + "Localization/English_xml.pak/text_ui_soul.xml")
        loc["alch_aesop_step_1"]            # ('text in column 2', 'text in column 3')
        loc.get("alch_aesop_step_1", 1)     # column 3 only (0 = first text after the key)

    `entries` is a dict {key: tuple_of_texts}, in file order. If a key occurs
    more than once (within a file, or across files via append()), the later
    one wins. Texts are kept exactly as written in the file. Rows without a
    key (no cells, or an empty first cell) are skipped.
    """

    def __init__(self):
        self.entries = {}    # key -> tuple of texts
        self.sources = []    # every path loaded or appended, in order

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def load(self, path):
        """Load entries from `path` (plain file, or through .pak archives,
        same path rules as Table.load). Replaces whatever was loaded before.
        Returns self."""
        pairs = self._parse(path)          # parse first, so a bad file leaves us untouched
        self.entries = dict(pairs)
        self.sources = [str(path)]
        return self

    def append(self, path):
        """Add the entries of another file. Keys that already exist are
        overwritten by the new file. Returns self, so calls can be chained."""
        pairs = self._parse(path)
        self.entries.update(pairs)
        self.sources.append(str(path))
        return self

    @staticmethod
    def _parse(path):
        data = Table._read_bytes(path)

        if data.startswith(b"CryXmlB"):
            raise ValueError(f"{path}: binary CryXml is not supported, it needs converting to text XML first")

        root = ET.fromstring(data)
        pairs = []
        for el in root.iter():
            if _local(el.tag) != "Row":
                continue
            cells = ["".join(c.itertext()) for c in el if _local(c.tag) == "Cell"]
            if cells and cells[0]:
                pairs.append((cells[0], tuple(cells[1:])))
        return pairs

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------
    def get(self, key, column=None, default=None):
        """Texts for `key` as a tuple, or just one text if `column` is given
        (0 = first text after the key). Returns `default` if the key or the
        column doesn't exist."""
        texts = self.entries.get(key)
        if texts is None:
            return default
        if column is None:
            return texts
        try:
            return texts[column]
        except IndexError:
            return default

    def keys(self):
        return self.entries.keys()

    def items(self):
        return self.entries.items()

    def __getitem__(self, key):
        return self.entries[key]

    def __contains__(self, key):
        return key in self.entries

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)

    # ------------------------------------------------------------------
    # Removing
    # ------------------------------------------------------------------
    def drop(self, *keys):
        """Remove the given keys (keys that aren't present are ignored).
        Returns how many were removed.

            loc.drop("alch_aesop_step_1", "alch_aesop_step_2")
        """
        removed = 0
        for key in keys:
            if self.entries.pop(key, None) is not None:
                removed += 1
        return removed

    def drop_where(self, predicate):
        """Remove every entry for which predicate(key, texts) is True.
        Returns how many were removed.

            loc.drop_where(lambda key, texts: key.startswith("alch_"))
        """
        doomed = [k for k, t in self.entries.items() if predicate(k, t)]
        for k in doomed:
            del self.entries[k]
        return len(doomed)

    def __repr__(self):
        return f"<Localization entries={len(self.entries)} sources={len(self.sources)}>"


if __name__ == "__main__":
    import sys

    loc = Localization().load(sys.argv[1])
    print(loc)
    for key, texts in list(loc.items())[:10]:
        print(key, texts)
