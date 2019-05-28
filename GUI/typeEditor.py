from PyQt5 import QtGui, QtWidgets, QtCore, uic
from GUI import confirm 

class Editor(QtWidgets.QDialog):
    def __init__(self, db, cursor, types, parent=None):
        super().__init__(parent)
        uic.loadUi("GUI/typeEditor.ui", self)

        self.initialName = ""
        self.initialColor = ""
        self.newName = ""
        self.newColor = ""
        self.lastSelection = 0

        self.db = db
        self.cursor = cursor

        for x in types:
            self.listWidget.addItem(x)

        self.listWidget.itemSelectionChanged.connect(self.update)
        self.listWidget.setCurrentRow(0)

        self.buttonCancel.clicked.connect(self.cancel)
        self.buttonApply.clicked.connect(self.apply)
        self.buttonConfirm.clicked.connect(self.confirm)
        self.buttonColor.clicked.connect(self.openColorDialog)
        self.fieldName.textChanged.connect(self.onTextChanged)

        self.show()

    def cancel(self):
        if self.initialColor != self.newColor or self.initialName != self.newName:
            prompt = confirm.confirm(text="You have unsaved work. Are you sure you want to quit?", title=" ")
            if prompt.response:
                self.close()
            else:
                pass
        else:
            self.close()

    def apply(self):
        self.initialName = self.newName
        self.initialColor = self.newColor
        self.cursor.execute(f"UPDATE types SET color = '{self.newColor}', name = '{self.newName}' WHERE name = '{self.initialName}'")
        if (self.initialName != self.newName):
            self.cursor.execute(f"UPDATE data SET type = '{self.newName}' WHERE type = '{self.initialName}'")
        self.db.commit()
    
    def confirm(self):
        self.cursor.execute(f"UPDATE types SET color = '{self.newColor}', name = '{self.newName}' WHERE name = '{self.initialName}'")
        if (self.initialName != self.newName):
            self.cursor.execute(f"UPDATE data SET type = '{self.newName}' WHERE type = '{self.initialName}'")
        self.db.commit()
        self.close()
    
    def openColorDialog(self):
        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            self.newColor = color.name()
            self.buttonColor.setStyleSheet(f"background-color: {self.newColor}" )
    
    def onTextChanged(self):
        self.newName = self.fieldName.text()
    
    def update(self):
        if self.initialColor != self.newColor or self.initialName != self.newName:
            prompt = confirm.confirm(text="You have unsaved work. Are you sure you want to quit?", title=" ")
            if not prompt.response:
                self.listWidget.blockSignals(True)
                self.listWidget.setCurrentRow(self.lastSelection)
                self.listWidget.blockSignals(False)
                return
        self.lastSelection = self.listWidget.currentRow()
        selected = self.listWidget.currentItem()

        name = selected.data(0)
        self.cursor.execute(f"SELECT color FROM types WHERE name = '{name}'")
        color = self.cursor.fetchall()

        self.initialName = str(name)
        self.initialColor = str(color[0][0])

        self.newName = self.initialName
        self.newColor = self.initialColor

        self.fieldName.setText(name)
        self.buttonColor.setStyleSheet(f"background-color: {self.initialColor}" )