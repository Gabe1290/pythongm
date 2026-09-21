"""Guards for the one-page student download flyer (scripts/generate_student_download_flyer.py).

The flyer tells students which file to download; those names must be the ones the
release workflow really publishes, the links must be the README's, and each
language must stay on ONE A4 page.
"""
import importlib.util
import re
from pathlib import Path

import pytest

pytest.importorskip("fpdf")
pytest.importorskip("segno")

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "generate_student_download_flyer", REPO / "scripts" / "generate_student_download_flyer.py")
flyer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(flyer)


def _asset_names():
    text = (REPO / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
    app = re.search(r"APP_NAME:\s*(\S+)", text).group(1).strip("'\"")
    return {f"{app}.exe", f"{app}-macOS-ARM.zip", f"{app}-macOS-Intel.zip", f"{app}-Linux.tar.gz"}


@pytest.mark.parametrize("lang", ["en", "fr"])
def test_listed_files_are_the_ones_the_release_publishes(lang):
    listed = {fname for _, fname, _ in flyer.CONTENT[lang]["rows"]}
    assert listed == _asset_names()


def test_the_flyer_links_to_the_latest_release_page_the_readme_uses():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "https://github.com/Gabe1290/pythongm/releases/latest/download/PyGameMaker.exe" in readme
    assert flyer.RELEASES_URL == "https://github.com/Gabe1290/pythongm/releases/latest"
    assert flyer.RELEASES_SHORT in flyer.RELEASES_URL


@pytest.mark.parametrize("lang", ["en", "fr"])
def test_each_language_fits_one_a4_page(lang, tmp_path):
    out = tmp_path / f"{lang}.pdf"
    flyer.render(lang, str(out))          # raises SystemExit if the layout overflows
    fitz = pytest.importorskip("pymupdf")
    doc = fitz.open(str(out))
    assert len(doc) == 1 and abs(doc[0].rect.width - 595.28) < 1 and abs(doc[0].rect.height - 841.89) < 1


def test_french_text_keeps_its_accents():
    fr = flyer.CONTENT["fr"]
    text = " ".join([fr["subtitle"], fr["intro"], fr["warn"]] + [ln for _, ls in fr["cols"] for ln in ls] + fr["s3_lines"])
    for word in ("téléphone", "Télécharge", "sécurité", "Réglages Système", "Exécuter quand même"):
        assert word in text or word in fr["s1"] or word in fr["scan"]
    for stripped in ("telephone", "Telecharge", "securite", "Reglages", "Executer"):
        assert stripped not in text
