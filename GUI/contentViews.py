from PyQt5 import QtGui, QtWidgets, QtCore, uic
from GUI import confirm

class AddContent(QtWidgets.QMainWindow):
    def __init__(self, settingsObj, parent=None):
        super().__init__(parent)
        uic.loadUi("GUI/newContent.ui", self)

        self.buttonCancel.clicked.connect(self.cancel)
        self.buttonApply.clicked.connect(self.apply)
        self.typeBox.activated.connect(self.typeBoxFunc)
        self.categoryBox.activated.connect(self.catBoxFunc)

        for item in settingsObj.settings["types"]:
            self.typeBox.addItem(item)        
        for item in settingsObj.settings["categories"]:
            self.categoryBox.addItem(item)

        self.link = ""
        self.notes = ""
        self.type = settingsObj.settings["types"][0]
        self.cat = settingsObj.settings["categories"][0]

        self.show()

    def cancel(self):
        if self.linkURL.text() != "" or self.linkNotes.toPlainText() != "":
            prompt = confirm.confirm(text="You have unsaved work. Are you sure you want to quit?", title=" ")
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

class ViewContent(QtWidgets.QMainWindow):
    def __init__(self, settingsObj, id, db, cursor, parent=None):
        super().__init__(parent)
        uic.loadUi("GUI/content.ui", self)
        self.settingsObj = settingsObj
        self.id = id
        self.db = db
        self.cursor = cursor

        self.cursor.execute(f"SELECT name, content, category, type FROM data WHERE id == '{self.id}'")
        x = self.cursor.fetchall()

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

        self.show()

    def delete(self):
        prompt = confirm.confirm(text="Are you sure you want to delete this note?", title=" ")
        if prompt.response:
            self.cursor.execute(f"DELETE FROM data WHERE id == '{self.id}'")
            self.db.commit()
            self.close()
        else:
            pass
    
    def edit(self):
        self.close()
        widget = EditContent(self.settingsObj, self.id, self.db, self.cursor)

class EditContent(QtWidgets.QMainWindow):
    def __init__(self, settingsObj, id, db, cursor, parent=None):
        super().__init__(parent)
        uic.loadUi("GUI/newContent.ui", self)

        self.id = id
        self.db = db
        self.cursor = cursor

        self.cursor.execute(f"SELECT name, content, category, type FROM data WHERE id == '{self.id}'")
        x = self.cursor.fetchall()

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

        self.show()

    def cancel(self):
        if self.linkURL.text() != "" or self.linkNotes.toPlainText() != "":
            prompt = confirm.confirm(text="You have unsaved work. Are you sure you want to quit?", title=" ")
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