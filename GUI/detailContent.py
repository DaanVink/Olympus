from PyQt5 import QtGui, QtWidgets, QtCore, uic
from GUI import confirm, editContent

class LinkDialog(QtWidgets.QDialog):
    def __init__(self, settingsObj, id, db, cursor, parent=None):
        super().__init__(parent)
        self.settingsObj = settingsObj
        self.id = id
        self.db = db
        self.cursor = cursor

        self.cursor.execute(f"SELECT name, content, category, type FROM data WHERE id == '{self.id}'")
        x = self.cursor.fetchall()

        uic.loadUi("GUI/content.ui", self)
        self.show()

        self.buttonEdit.clicked.connect(self.edit)
        self.buttonDelete.clicked.connect(self.delete)
        self.buttonClose.clicked.connect(self.close)

        for item in settingsObj.settings["types"]:
            self.typeBox.addItem(item)
        
        for item in settingsObj.settings["categories"]:
            self.categoryBox.addItem(item)

        self.linkURL.setText(x[0][0])
        self.linkNotes.setText(x[0][1])
        self.categoryBox.setCurrentIndex(self.categoryBox.findText(x[0][2]))
        self.typeBox.setCurrentIndex(self.typeBox.findText(x[0][3]))

    def delete(self):
        prompt = confirm.confirm(text="Are you sure you want to delete this note?", title="")
        if prompt.response:
            self.cursor.execute(f"DELETE FROM data WHERE id == '{self.id}'")
            self.db.commit()
            self.close()
        else:
            pass
    
    def edit(self):
        self.close()
        widget = editContent.editWidget(self.settingsObj, self.id, self.db, self.cursor)
        