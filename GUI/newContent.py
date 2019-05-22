from PyQt5 import QtGui, QtWidgets, QtCore, uic
from GUI import confirm
        

class LinkDialog(QtWidgets.QDialog):
    def __init__(self, settingsObj, parent=None):
        super().__init__(parent)
        uic.loadUi("GUI/newContent.ui", self)
        self.show()

        self.buttonCancel.clicked.connect(self.cancel)
        self.buttonApply.clicked.connect(self.apply)

        for item in settingsObj.settings["types"]:
            self.typeBox.addItem(item)
        
        for item in settingsObj.settings["categories"]:
            self.categoryBox.addItem(item)

        self.link = ""
        self.notes = ""
        self.type = settingsObj.settings["types"][0]
        self.cat = settingsObj.settings["categories"][0]

        self.typeBox.activated.connect(self.typeBoxFunc)
        self.categoryBox.activated.connect(self.catBoxFunc)

    def cancel(self):
        if self.linkURL.text() != "" or self.linkNotes.toPlainText() != "":
            prompt = confirm.confirm(text="You have unsaved work. Are you sure you want to quit?", title="")
            if prompt.response:
                self.close()
            else:
                pass
        else:
            self.close()

    def typeBoxFunc(self, index):
        self.type = self.typeBox.itemText(index)
    
    def catBoxFunc(self, index):
        self.cat = self.categoryBox.itemText(index)

    def apply(self):
        self.link = self.linkURL.text()
        self.notes = self.linkNotes.toPlainText()
        self.obj = {"title": self.link, "notes": self.notes, "category": self.cat, "type": self.type}
        self.close()
