"""Fallback translations for Qt's own standard dialog strings.

Qt ships ``qtbase_<lang>.qm`` catalogs that translate the standard buttons
(Save / Discard / Cancel / Yes / No ...) and the non-native file dialog.  Those
catalogs are missing or incomplete for some of our languages:

* ``qtbase_sl`` does not exist, ``qtbase_pt`` / ``qtbase_zh`` exist only as
  ``pt_BR`` / ``zh_CN`` (the loader looked for the bare code);
* ``qtbase_fr`` has no entries for most buttons (``Save``, ``Discard``, ``Yes``...).

``QtStandardStringsTranslator`` is consulted only when nothing else translated a
string (it is installed *before* Qt's own translator, and Qt asks the most
recently installed translator first), so a complete Qt catalog always wins.
"""

from PySide6.QtCore import QTranslator

# Contexts Qt uses for the strings below.
CONTEXTS = frozenset({
    "QPlatformTheme", "QDialogButtonBox", "QMessageBox",
    "QFileDialog", "QColorDialog", "QFontDialog", "QWizard",
})

# source -> {language: translation}
_STRINGS = {
    "OK": {"fr": "OK", "sl": "V redu", "pt": "OK", "zh": "确定"},
    "&OK": {"fr": "&OK", "sl": "&V redu", "pt": "&OK", "zh": "确定(&O)"},
    "Save": {"fr": "Enregistrer", "sl": "Shrani", "pt": "Guardar", "zh": "保存"},
    "&Save": {"fr": "&Enregistrer", "sl": "&Shrani", "pt": "&Guardar", "zh": "保存(&S)"},
    "Save All": {"fr": "Tout enregistrer", "sl": "Shrani vse", "pt": "Guardar tudo", "zh": "全部保存"},
    "Open": {"fr": "Ouvrir", "sl": "Odpri", "pt": "Abrir", "zh": "打开"},
    "&Open": {"fr": "&Ouvrir", "sl": "&Odpri", "pt": "&Abrir", "zh": "打开(&O)"},
    "&Yes": {"fr": "&Oui", "sl": "&Da", "pt": "&Sim", "zh": "是(&Y)"},
    "Yes": {"fr": "Oui", "sl": "Da", "pt": "Sim", "zh": "是"},
    "Yes to &All": {"fr": "Oui à &tout", "sl": "Da za &vse", "pt": "Sim para &todos", "zh": "全部是(&A)"},
    "&No": {"fr": "&Non", "sl": "&Ne", "pt": "&Não", "zh": "否(&N)"},
    "No": {"fr": "Non", "sl": "Ne", "pt": "Não", "zh": "否"},
    "N&o to All": {"fr": "N&on à tout", "sl": "N&e za vse", "pt": "N&ão para todos", "zh": "全部否(&O)"},
    "Abort": {"fr": "Abandonner", "sl": "Prekini", "pt": "Abortar", "zh": "中止"},
    "Retry": {"fr": "Réessayer", "sl": "Poskusi znova", "pt": "Repetir", "zh": "重试"},
    "Ignore": {"fr": "Ignorer", "sl": "Prezri", "pt": "Ignorar", "zh": "忽略"},
    "Close": {"fr": "Fermer", "sl": "Zapri", "pt": "Fechar", "zh": "关闭"},
    "&Close": {"fr": "&Fermer", "sl": "&Zapri", "pt": "&Fechar", "zh": "关闭(&C)"},
    "Cancel": {"fr": "Annuler", "sl": "Prekliči", "pt": "Cancelar", "zh": "取消"},
    "&Cancel": {"fr": "&Annuler", "sl": "&Prekliči", "pt": "&Cancelar", "zh": "取消(&C)"},
    "Discard": {"fr": "Ne pas enregistrer", "sl": "Zavrzi", "pt": "Descartar", "zh": "放弃"},
    "Don't Save": {"fr": "Ne pas enregistrer", "sl": "Ne shrani", "pt": "Não guardar", "zh": "不保存"},
    "Help": {"fr": "Aide", "sl": "Pomoč", "pt": "Ajuda", "zh": "帮助"},
    "&Help": {"fr": "&Aide", "sl": "&Pomoč", "pt": "&Ajuda", "zh": "帮助(&H)"},
    "Apply": {"fr": "Appliquer", "sl": "Uporabi", "pt": "Aplicar", "zh": "应用"},
    "Reset": {"fr": "Réinitialiser", "sl": "Ponastavi", "pt": "Repor", "zh": "重置"},
    "Restore Defaults": {"fr": "Rétablir les valeurs par défaut", "sl": "Obnovi privzeto",
                         "pt": "Repor predefinições", "zh": "恢复默认值"},
    "Show Details...": {"fr": "Afficher les détails...", "sl": "Pokaži podrobnosti...",
                        "pt": "Mostrar detalhes...", "zh": "显示详细信息..."},
    "Hide Details...": {"fr": "Masquer les détails...", "sl": "Skrij podrobnosti...",
                        "pt": "Ocultar detalhes...", "zh": "隐藏详细信息..."},
    "&Choose": {"fr": "&Choisir", "sl": "&Izberi", "pt": "&Escolher", "zh": "选择(&C)"},
    "Select All": {"fr": "Tout sélectionner", "sl": "Izberi vse", "pt": "Selecionar tudo", "zh": "全选"},
    # File dialog
    "Look in:": {"fr": "Regarder dans :", "sl": "Poglej v:", "pt": "Procurar em:", "zh": "查找范围:"},
    "File &name:": {"fr": "&Nom du fichier :", "sl": "&Ime datoteke:", "pt": "&Nome do ficheiro:", "zh": "文件名(&N):"},
    "Files of type:": {"fr": "Fichiers de type :", "sl": "Datoteke vrste:", "pt": "Ficheiros do tipo:", "zh": "文件类型:"},
    "Directory:": {"fr": "Dossier :", "sl": "Mapa:", "pt": "Pasta:", "zh": "目录:"},
    "Back": {"fr": "Précédent", "sl": "Nazaj", "pt": "Anterior", "zh": "后退"},
    "Forward": {"fr": "Suivant", "sl": "Naprej", "pt": "Seguinte", "zh": "前进"},
    "Parent Directory": {"fr": "Dossier parent", "sl": "Nadrejena mapa", "pt": "Pasta superior", "zh": "上级目录"},
    "Create New Folder": {"fr": "Créer un nouveau dossier", "sl": "Ustvari novo mapo",
                          "pt": "Criar nova pasta", "zh": "新建文件夹"},
    "List View": {"fr": "Vue en liste", "sl": "Seznam", "pt": "Vista de lista", "zh": "列表视图"},
    "Detail View": {"fr": "Vue détaillée", "sl": "Podrobnosti", "pt": "Vista de detalhes", "zh": "详细视图"},
    "All Files (*)": {"fr": "Tous les fichiers (*)", "sl": "Vse datoteke (*)",
                      "pt": "Todos os ficheiros (*)", "zh": "所有文件 (*)"},
    "Recent Places": {"fr": "Emplacements récents", "sl": "Nedavna mesta", "pt": "Locais recentes", "zh": "最近的位置"},
    "Computer": {"fr": "Ordinateur", "sl": "Računalnik", "pt": "Computador", "zh": "计算机"},
    "New Folder": {"fr": "Nouveau dossier", "sl": "Nova mapa", "pt": "Nova pasta", "zh": "新建文件夹"},
    "Delete": {"fr": "Supprimer", "sl": "Izbriši", "pt": "Eliminar", "zh": "删除"},
    "Rename": {"fr": "Renommer", "sl": "Preimenuj", "pt": "Mudar o nome", "zh": "重命名"},
    "Show hidden files": {"fr": "Afficher les fichiers cachés", "sl": "Pokaži skrite datoteke",
                          "pt": "Mostrar ficheiros ocultos", "zh": "显示隐藏文件"},
    "Sidebar": {"fr": "Barre latérale", "sl": "Stranska vrstica", "pt": "Barra lateral", "zh": "侧边栏"},
    "Drive": {"fr": "Lecteur", "sl": "Pogon", "pt": "Unidade", "zh": "驱动器"},
    "File": {"fr": "Fichier", "sl": "Datoteka", "pt": "Ficheiro", "zh": "文件"},
    "Folder": {"fr": "Dossier", "sl": "Mapa", "pt": "Pasta", "zh": "文件夹"},
    "Name": {"fr": "Nom", "sl": "Ime", "pt": "Nome", "zh": "名称"},
    "Size": {"fr": "Taille", "sl": "Velikost", "pt": "Tamanho", "zh": "大小"},
    "Type": {"fr": "Type", "sl": "Vrsta", "pt": "Tipo", "zh": "类型"},
    "Date Modified": {"fr": "Date de modification", "sl": "Datum spremembe",
                      "pt": "Data de modificação", "zh": "修改日期"},
}


def _normalise(language_code: str) -> str:
    return (language_code or "").replace("-", "_").split("_")[0].lower()


class QtStandardStringsTranslator(QTranslator):
    """Supplies standard-dialog strings Qt's own catalogs lack (see module docstring)."""

    def __init__(self, language_code: str, parent=None):
        super().__init__(parent)
        self._lang = _normalise(language_code)

    def isEmpty(self):
        return not any(self._lang in t for t in _STRINGS.values())

    def translate(self, context, source_text, disambiguation=None, n=-1):
        if context in CONTEXTS:
            entry = _STRINGS.get(source_text)
            if entry:
                found = entry.get(self._lang)
                if found:
                    return found
        # A NULL string ("not mine, ask the next translator"). Returning ""
        # from a PySide6 override is a non-null empty QString, which Qt takes
        # as "translated to nothing" and stops there -- every menu and label
        # in the IDE rendered blank (2026-11-19).
        return None
