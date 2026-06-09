"""Regression tests: the Open Roberta importer hardens its XML parse.

Roberta program XML is web-sourced (lab.open-roberta.org), so it's untrusted.
The importer parses via defusedxml, which rejects entity-expansion ("billion
laughs") and external-entity/DTD constructs. These tests pin that a malicious
file is rejected as a clean RobertaImportError rather than being expanded
(DoS) or quietly parsed.
"""

import pytest

from importers.roberta_importer import (
    import_roberta,
    import_roberta_detailed,
    RobertaImportError,
)


BILLION_LAUGHS = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
]>
<export xmlns="http://de.fhg.iais.roberta.blockly">&lol3;</export>
"""

EXTERNAL_ENTITY = """<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<export xmlns="http://de.fhg.iais.roberta.blockly">&xxe;</export>
"""


def _write(tmp_path, payload):
    p = tmp_path / "program.xml"
    p.write_text(payload, encoding="utf-8")
    return p


def test_billion_laughs_rejected_detailed(tmp_path):
    """An entity-expansion bomb is rejected, not expanded."""
    xml = _write(tmp_path, BILLION_LAUGHS)
    with pytest.raises(RobertaImportError):
        import_roberta_detailed(str(xml), str(tmp_path / "out"))


def test_external_entity_rejected_detailed(tmp_path):
    """An external-entity (classic XXE) DOCTYPE is rejected."""
    xml = _write(tmp_path, EXTERNAL_ENTITY)
    with pytest.raises(RobertaImportError):
        import_roberta_detailed(str(xml), str(tmp_path / "out"))


def test_malicious_file_returns_false_not_crash(tmp_path):
    """The simple wrapper degrades to False rather than raising/expanding."""
    xml = _write(tmp_path, BILLION_LAUGHS)
    assert import_roberta(str(xml), str(tmp_path / "out")) is False


def test_no_passwd_leak(tmp_path):
    """The external-entity payload must not pull /etc/passwd into the parse."""
    xml = _write(tmp_path, EXTERNAL_ENTITY)
    with pytest.raises(RobertaImportError) as exc:
        import_roberta_detailed(str(xml), str(tmp_path / "out"))
    assert "root:" not in str(exc.value)
