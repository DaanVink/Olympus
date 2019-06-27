#TODO: find a way to minimize new object creation when calling updateTree()
#TODO: clean up functions and group related code using whitespace
#TODO: write a README.MD

from PyQt5 import QtGui, QtWidgets, QtCore, uic
import sys, json, sqlite3

from GUI import contentViews, dataEditor
import settingsHandler

db = sqlite3.connect("data/mainStore.sqlite")

settingsHolder = settingsHandler.Settings(db)
settingsHolder.load()

app = QtWidgets.QApplication(sys.argv)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        uic.loadUi("GUI/main.ui", self)

        self.db = db
        self.cursor = self.db.cursor()

        self.data = {}
        # This query gets all data to be shown in the tree from the DB
        for category in settingsHolder.settings["categories"]:
            query = f"SELECT name, content, type, id FROM data WHERE category == '{category}'"
            self.cursor.execute(query)
            self.data[str(category)] = self.cursor.fetchall()

        self.categoryFilter.addItem("") # Add an empty item to the start of the combobox, signifying no filter
        for item in settingsHolder.settings["categories"]:
            self.categoryFilter.addItem(item) # Add every category to the combobox
        self.categoryFilter.activated.connect(self.catFilterActivated) # Call a function to update the tree according to the new filters

        self.typeFilter.addItem("") # Add an empty item to the start of the combobox, signifying no filter
        for item in settingsHolder.settings["types"]:
            self.typeFilter.addItem(item) # Add every type to the combobox
        self.typeFilter.activated.connect(self.typeFilterActivated) # Call a function to update the tree according to the new filters

        self.searchBox.textChanged.connect(self.searchboxChange)
        self.filter = {"category": "", "type": "", "search": ""}

        self.treeView.setColumnWidth(0, 150) # This should be a settings when i get around to adding proper settings
        self.treeView.setAlternatingRowColors(False) # This too
        self.treeView.expandAll()
        self.treeView.doubleClicked.connect(self.treeDoubleClick)
        self.updateTree() # This function holds all code responsible for editing the data shown in the tree
        
        # Setting sup the menubar
        self.menu = self.menuBar()
        self.addNew = QtWidgets.QAction("New", self)
        self.addNew.triggered.connect(self.addContent)
        self.menu.addAction(self.addNew)

        self.dataMenu = QtWidgets.QMenu("Data", self)
        self.menu.addMenu(self.dataMenu)

        self.editTypes = QtWidgets.QAction("Types", self)
        self.editTypes.triggered.connect(self.editTypesFunc)
        self.dataMenu.addAction(self.editTypes)

        # For now, this is just a copy of the type editor
        self.editCategories = QtWidgets.QAction("Categories", self)
        self.editCategories.triggered.connect(self.editCategoriesFunc)
        self.dataMenu.addAction(self.editCategories)

        self.tmp = QtWidgets.QAction("Debug", self)
        self.tmp.triggered.connect(self.debugFunction)
        self.menu.addAction(self.tmp)

        # Final actions before showing the window

        self.setWindowTitle("Project Olympus")
        self.show()

    def updateTree(self):
        # First we build up a query to load data for the DB
        # This query is made up of three parts: the base, the category filter and the type filter
        # The type filter is stored in the addition variable before being added to the base query
        addition = ""
        if self.filter["category"] is not "": # Check if we need to filter
            filteredCategories = [ self.filter["category"] ]
        else:
            filteredCategories = settingsHolder.settings["categories"]
        
        filterType = self.filter["type"] if self.filter["type"] is not "" else "" # we need to create a new variable here because f-strings can only take pure variables, not list indices
        if filterType is not "":
            addition += f" AND type = '{filterType}'"
        if self.filter["search"] is not "":
            search = self.filter["search"]
            addition += f" AND (name LIKE '%{ search }%' or content LIKE '%{ search }%')"

        self.data = {}
        # For every category, create a query string and execute it. Then store the resulting data in a dictionary with as key the category
        for category in filteredCategories:
            query = f"SELECT name, content, type, id FROM data WHERE category = '{category}'" + addition
            self.cursor.execute(query)
            self.data[str(category)] = self.cursor.fetchall()

        # In Qt, a treeview requires a Model to store the data
        self.model = QtGui.QStandardItemModel()
        self.model.setColumnCount(4)
        self.model.setHorizontalHeaderLabels(["Title", "Notes", "Type", "ID"])

        self.rootNode = self.model.invisibleRootItem()

        # This part deals with adding the data to the newly created Model
        # Every category is represented by a new branch
        self.branches = []
        for x in range(0, len(filteredCategories)):
            category = filteredCategories[x]
            self.branches.append(QtGui.QStandardItem(str(category)))
            for node in range(0, len(self.data[str(category)])):
                currentData = self.data[str(category)][node]
                color = QtGui.QColor(settingsHolder.settings["typeColors"][currentData[2]])
                row = []
                for y in range(0, 4):
                    tmp = QtGui.QStandardItem(str(currentData[y]))
                    tmp.setForeground(color)
                    row.append(tmp)
                self.branches[x].appendRow(row)
        
        for branch in self.branches:
            self.rootNode.appendRow( [branch] )
        
        self.treeView.setModel(self.model)
        self.treeView.expandAll()
    
    def addContent(self):
        self.new = contentViews.AddContent(settingsHolder, db)
        self.new.exec() # block thread until dialog closes
        self.updateTree()
    
    def catFilterActivated(self, index):
        self.filter["category"] = self.categoryFilter.itemText(index)
        self.updateTree()

    def typeFilterActivated(self, index):
        self.filter["type"] = self.typeFilter.itemText(index)
        self.updateTree()
    
    def searchboxChange(self):
        search = self.searchBox.text()
        self.filter["search"] = search
        self.updateTree()

    def treeDoubleClick(self, index):
        id = self.treeView.selectedIndexes()[3].data()
        if id is None:
            pass
        else:
            self.detail = contentViews.ViewContent(settingsHolder, id, self.db)
            self.detail.exec() # block thread until dialog closes
        self.updateTree()
    
    def editTypesFunc(self):
        self.new = dataEditor.TypeEditor(self.db, settingsHolder.settings["types"])
        self.new.exec() # block thread until dialog closes
        settingsHolder.load() # reload settings
        self.updateTree()
    
    def editCategoriesFunc(self):
        self.new = dataEditor.CategoryEditor(self.db, settingsHolder.settings["categories"])
        self.new.exec() # block thread until dialog closes
        settingsHolder.load() # reload settings
        self.updateTree()
    
    def debugFunction(self):
        pass

main = MainWindow(db)
app.exec()
