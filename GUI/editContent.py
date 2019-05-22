from PyQt5 import QtGui, QtWidgets, QtCore, uic
from GUI import confirm

class editWidget(QtWidgets.QDialog):
    def __init__(self, settingsObj, id, db, cursor, parent=None):
        super().__init__(parent)
        self.id = id
        self.db = db
        self.cursor = cursor

        self.cursor.execute(f"SELECT name, content, category, type FROM data WHERE id == '{self.id}'")
        x = self.cursor.fetchall()
        
        uic.loadUi("GUI/newContent.ui", self)
        self.show()

        self.buttonCancel.clicked.connect(self.cancel)
        self.buttonApply.clicked.connect(self.apply)

        for item in settingsObj.settings["types"]:
            self.typeBox.addItem(item)
        
        for item in settingsObj.settings["categories"]:
            self.categoryBox.addItem(item)

        self.linkURL.setText(x[0][0])
        self.linkNotes.setText(x[0][1])
        self.categoryBox.setCurrentIndex(self.categoryBox.findText(x[0][2]))
        self.typeBox.setCurrentIndex(self.typeBox.findText(x[0][3]))


        self.link = x[0][0]
        self.notes = x[0][1]
        self.cat = x[0][2]
        self.type = x[0][3]

        self.typeBox.activated.connect(self.typeBoxFunc)
        self.categoryBox.activated.connect(self.catBoxFunc)

        self.exec()

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
        self.cursor.execute(f"UPDATE data SET name = '{self.link}', content = '{self.notes}', category = '{self.cat}', type = '{self.type}' WHERE id == '{self.id}'")
        self.db.commit()
        self.close()
