"""Regression tests for the Aseba (.aesl) exporter (M32, M33).

M32: exported .aesl files were raw Aseba source, but Aseba Studio opens .aesl
as an XML document (<!DOCTYPE aesl-source><network><node>...). File -> Open
failed for every export. Output is now wrapped in the XML envelope.

M33: every onevent handler was terminated with a stray 'end', which is invalid
AESL ('end' only closes if/when/while/for) and failed compilation.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from export.Aseba.aseba_exporter import AsebaExporter


def _project_with_thymio():
    return {
        "name": "TestBot",
        "assets": {
            "objects": {
                "thymio_robot": {
                    "is_thymio": True,
                    "events": {
                        "thymio_button_forward": {
                            "actions": [
                                {"action": "thymio_move_forward",
                                 "parameters": {"speed": 200}}
                            ]
                        }
                    },
                }
            }
        },
    }


@pytest.fixture
def exported(tmp_path):
    proj = tmp_path / "project.json"
    proj.write_text(json.dumps(_project_with_thymio()), encoding="utf-8")
    out = tmp_path / "out"
    exporter = AsebaExporter()
    assert exporter.export(str(proj), str(out)) is True
    aesl = out / "thymio_robot.aesl"
    assert aesl.exists()
    return aesl.read_text(encoding="utf-8")


class TestAeslXmlEnvelope:
    def test_has_doctype(self, exported):
        assert exported.lstrip().startswith("<!DOCTYPE aesl-source>")

    def test_is_parseable_xml(self, exported):
        # Strip the DOCTYPE line (ET doesn't accept custom DOCTYPEs) then parse.
        body = "\n".join(
            l for l in exported.splitlines() if not l.strip().startswith("<!DOCTYPE"))
        root = ET.fromstring(body)
        assert root.tag == "network"
        node = root.find("node")
        assert node is not None
        assert node.get("name") == "thymio-II"
        # The Aseba source lives inside the node (CDATA).
        assert "onevent button.forward" in (node.text or "")


class TestNoStrayEnd:
    def test_event_handler_has_no_trailing_end(self, exported):
        # The only "end" tokens allowed are those closing if/when/while/for.
        # This simple handler opens no block, so it must contain no bare "end".
        lines = [l.strip() for l in exported.splitlines()]
        assert "end" not in lines
