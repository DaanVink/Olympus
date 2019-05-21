from PyQt5 import QtGui, QtWidgets, QtCore, uic
import sys
import settingsHandler

settingsHolder = settingsHandler.Settings()

app = QtWidgets.QApplication(sys.argv)

class confirmExit(QtWidgets.QDialog):
    def setupUI(self):
        uic.loadUi("confirmExit.ui", self)
        self.exec_()
        self.show()

    def acceptAction(self):
        self.response = True
        self.close()
        
    
    def cancelAction(self):
        self.response = False
        self.close()
        

class NewLinkWidget(QtWidgets.QDialog):
    def setupUI(self, settingsObj):
        uic.loadUi("dialog.ui", self)
        dialog.show()

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
            prompt = confirmExit()
            prompt.setupUI()
            print(prompt.response)
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
        obj = [self.link, self.notes, self.cat, self.type]
        print(obj)
        self.close()
    
dialog = NewLinkWidget()
dialog.setupUI(settingsHolder)
app.exec()