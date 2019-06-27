from PyQt5 import QtGui, QtWidgets, QtCore, uic
from GUI import confirm 
from sqlite3 import IntegrityError

class TypeEditor(QtWidgets.QDialog):
    def __init__(self, db, types, parent=None):
        super().__init__(parent)
        uic.loadUi("GUI/typeEditor.ui", self)

        self.initialName = ""
        self.initialColor = ""
        self.newName = ""
        self.newColor = ""
        self.lastSelection = 0

        self.db = db
        self.cursor = self.db.cursor()

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
    
class CategoryEditor(QtWidgets.QDialog):
    def __init__(self, db, catgegories, parent=None):
        super().__init__(parent)
        uic.loadUi("GUI/categoryEditor.ui", self)

        self.initialNames = []
        self.newNames = []
        self.lastSelection = 0

        self.db = db
        self.cursor = self.db.cursor()

        for x in catgegories:
            self.listWidget.addItem(x)
            self.initialNames.append(x)
            self.newNames.append(x)

        self.listWidget.itemSelectionChanged.connect(self.update)
        self.listWidget.setCurrentRow(0)

        self.buttonDelete.clicked.connect(self.delete)
        self.buttonCancel.clicked.connect(self.cancel)
        self.buttonApply.clicked.connect(self.apply)
        self.buttonMerge.clicked.connect(self.merge)

        self.fieldName.textChanged.connect(self.onTextChanged)

        self.show()

    def merge(self):
        prompt = Merge(self.newNames, self.fieldName.text())
        try:
            response = prompt.response
        except AttributeError:
            return
        if len(response) == 1:
            selected = self.newNames[self.listWidget.currentRow()]
            self.cursor.execute(f"DELETE FROM categories WHERE name = '{selected}'")
            self.cursor.execute(f"UPDATE data SET category = '{response[0]}' WHERE category = '{selected}'")
            self.listWidget.takeItem(self.listWidget.currentRow())
            self.db.commit()

    def cancel(self):
        if self.initialNames != self.newNames:
            prompt = confirm.confirm(text="You have unsaved work. Are you sure you want to quit?", title=" ")
            if prompt.response:
                self.close()
            else:
                pass
        else:
            self.close()

    def apply(self):
        self.update()
        placeholdered = []
        for x in range(0, len(self.newNames)):
            if self.newNames[x] != self.initialNames[x]:
                try:
                    self.cursor.execute(f"UPDATE categories SET name = '{self.newNames[x]}' WHERE name = '{self.initialNames[x]}'")
                    self.cursor.execute(f"UPDATE data SET category = '{self.newNames[x]}' WHERE category = '{self.initialNames[x]}'")
                except IntegrityError:
                    placeholdered.append(x)
                    self.cursor.execute(f"UPDATE categories SET name = 'PLACEHOLDER{self.newNames[x]}' WHERE name = '{self.initialNames[x]}'")
                    self.cursor.execute(f"UPDATE data SET category = 'PLACEHOLDER{self.newNames[x]}' WHERE category = '{self.initialNames[x]}'")
        if len(placeholdered) != 0:
            for x in placeholdered:
                self.cursor.execute(f"UPDATE categories SET name = '{self.newNames[x]}' WHERE name = 'PLACEHOLDER{self.newNames[x]}'")
                self.cursor.execute(f"UPDATE data SET category = '{self.newNames[x]}' WHERE category = 'PLACEHOLDER{self.newNames[x]}'")
        self.db.commit()
        self.close()
    
    def delete(self):
        self.update()
        selected = self.fieldName.text()
        prompt = confirm.confirm("This will delete the selected category and its data.\nAre you sure you want to proceed?", title="Warning!")
        if prompt.response:
            self.cursor.execute(f"DELETE FROM categories WHERE name = '{selected}'")
            self.cursor.execute(f"DELETE FROM data WHERE category = '{selected}'")
            self.db.commit()
            self.listWidget.takeItem(self.listWidget.currentRow())
        else:
            pass
    
    def onTextChanged(self):
        self.newNames[self.listWidget.currentRow()] = self.fieldName.text()
        self.checkForDuplicates()
        self.update()

    def checkForDuplicates(self):
        x = 0
        suffix = ""
        print(self.newNames.count(self.fieldName.text() + suffix))
        print(self.fieldName.text() + suffix)
        while (self.newNames.count(self.fieldName.text() + suffix)) > 1:
            x += 1
            suffix = f" ({x})"
        self.fieldName.setText(self.fieldName.text() + suffix)
    
    def update(self):
        self.lastSelection = self.listWidget.currentRow()
        selected = self.listWidget.currentRow()

        name = self.newNames[selected]

        try:
            self.listWidget.selectedItems()[0].setText(name)
        except:
            pass
        self.fieldName.setText(name)

class Merge(QtWidgets.QDialog):
    def __init__(self, choices, original, parent=None):
        super().__init__(parent)
        uic.loadUi("GUI/merge.ui", self)

        self.setWindowTitle("Merging")

        self.buttonApply.clicked.connect(self.apply)
        self.buttonCancel.clicked.connect(self.cancel)
        
        self.box_selection.currentIndexChanged.connect(self.update)

        self.box_locked.addItem(original)
        self.box_selection.addItem("")

        for item in choices:
            if item != original:
                self.box_selection.addItem(item)

        self.exec()
        self.show()
    
    def update(self):
        if self.box_selection.currentText() == "":
            self.buttonApply.setEnabled(False)
        else:
            self.buttonApply.setEnabled(True)

    def apply(self):
        self.response = [self.box_selection.currentText()]
        self.close()     
    
    def cancel(self):
        self.response = []
        self.close() 
