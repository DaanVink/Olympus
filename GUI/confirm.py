from PyQt5 import QtWidgets, uic

class confirm(QtWidgets.QDialog):
    def __init__(self, text=None, title=None, parent=None):
        super().__init__(parent)
        uic.loadUi("GUI/confirm.ui", self)

        self.label.setText(str(text))
        self.setWindowTitle(str(title))

        self.exec()
        self.show()

    def acceptAction(self):
        self.response = True
        self.close()     
    
    def cancelAction(self):
        self.response = False
        self.close() 
