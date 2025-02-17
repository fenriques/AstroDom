import sqlite3, sys, logging
import pandas as pd
from PyQt6.QtWidgets import QApplication, QTreeView
from PyQt6.QtCore import Qt
from astrodom.customTreeModel import CustomTreeModel, CustomFilterProxyModel
from astrodom.viewDelegates import *
from astrodom.settings import *
from astrodom.loadSettings import *  # Import the constants


class Dashboard(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_id = None
        self.parent = parent

        self.setGeometry(100, 100, 800, 600)

        self.setAlternatingRowColors(True)
        self.setColumnWidth(0, 350)
        self.header().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setColumnWidth(5, 250)

        self.dateDelegate = DateDelegate(self)
        self.setItemDelegateForColumn(4, self.dateDelegate)

        self.timeDelegate = TimeDelegate(self)
        self.setItemDelegateForColumn(5, self.timeDelegate)

        self.filterDelegate = FilterDelegate(self)
        self.setItemDelegateForColumn(6, self.filterDelegate)

        self.fwhmDelegate = FWHMDelegate(self)
        self.setItemDelegateForColumn(7, self.fwhmDelegate)
        self.fwhmDelegate.setLimit(FWHM_LIMIT_DEFAULT)

        self.eccentricityDelegate = EccentricityDelegate(self)
        self.setItemDelegateForColumn(8, self.eccentricityDelegate)
        self.eccentricityDelegate.setLimit(ECCENTRICITY_LIMIT_DEFAULT)

        self.snrDelegate = SNRDelegate(self)
        self.setItemDelegateForColumn(9, self.snrDelegate)
        self.snrDelegate.setLimit(SNR_LIMIT_DEFAULT)

        self.altDelegate = AltDelegate(self)
        self.setItemDelegateForColumn(10, self.altDelegate)
        self.altDelegate.setLimit(ALT_LIMIT_DEFAULT)

        self.azDelegate = DmsDelegate(self)
        self.setItemDelegateForColumn(11, self.azDelegate)

        self.frameDelegate = FrameDelegate(self)
        self.setItemDelegateForColumn(13, self.frameDelegate)

        self.raDelegate = HmsDelegate(self)
        self.setItemDelegateForColumn(15, self.raDelegate)

        self.decDelegate = DmsDelegate(self)
        self.setItemDelegateForColumn(16, self.decDelegate)
        
        self.roundDelegate = RoundDelegate(self)
        self.setItemDelegateForColumn(19, self.roundDelegate)
        self.setItemDelegateForColumn(20, self.roundDelegate)


        self.load_data()
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)
    
    def on_selection_changed(self, selected, deselected):
        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            index = indexes[0]
            model_index = self.proxy_model.mapToSource(index)
            value = self.proxy_model.sourceModel().data(model_index.siblingAtColumn(21), Qt.ItemDataRole.DisplayRole)
            print(f"Value at column 10: {value}")

    def applyThreshold(self,fwhm, snr, alt, eccentricity):
        self.fwhmDelegate.setLimit(float(fwhm))
        self.eccentricityDelegate.setLimit(float(eccentricity))
        self.altDelegate.setLimit(float(alt))
        self.snrDelegate.setLimit(float(snr))
        expanded_items = self.save_expanded_state()
        self.proxy_model.layoutChanged.emit()
        self.restore_expanded_state(expanded_items)

    def load_data(self):
        # Connect to the database
        db_path = str(self.parent.rsc_path.joinpath( DBNAME))
        conn = sqlite3.connect(db_path)

        if hasattr(self.parent, 'projectStatus') and self.parent.projectStatus != 'Active':
            self.parent.syncButton.setEnabled(False)

        if not self.project_id or self.project_id == 0:
            query = f"SELECT * FROM images ORDER BY PROJECT_ID DESC, DATE_OBS ASC"

        elif self.project_id > 0: 
            query = f"SELECT * FROM images WHERE PROJECT_ID = {self.project_id} ORDER BY  PROJECT_ID DESC,  DATE_OBS ASC"
        
        try:
            self.df = pd.read_sql_query(query, conn)
            conn.close()
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.close()
            return
        
        # Set the model
        self.model = CustomTreeModel(self.df)
        self.proxy_model = CustomFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.setModel(self.proxy_model)
  
    
    def setProjectID(self,project_id):
        self.project_id = project_id
        self.load_data()

    def update_contents(self,selected_project_id):
        self.proxy_model.setFilterString(str(selected_project_id))

    def save_expanded_state(self):
        expanded_items = []
        root_index = self.proxy_model.index(0, 0)
        self._save_expanded_state_recursive(root_index, expanded_items)
        return expanded_items

    def _save_expanded_state_recursive(self, index, expanded_items):
        if not index.isValid():
            return
        if self.isExpanded(index):
            expanded_items.append(self.proxy_model.data(index, Qt.ItemDataRole.DisplayRole))
        for row in range(self.proxy_model.rowCount(index)):
            child_index = self.proxy_model.index(row, 0, index)
            self._save_expanded_state_recursive(child_index, expanded_items)

    def restore_expanded_state(self, expanded_items):
        root_index = self.proxy_model.index(0, 0)
        self._restore_expanded_state_recursive(root_index, expanded_items)

    def _restore_expanded_state_recursive(self, index, expanded_items):
        if not index.isValid():
            return
        if self.proxy_model.data(index, Qt.ItemDataRole.DisplayRole) in expanded_items:
            self.setExpanded(index, True)
        for row in range(self.proxy_model.rowCount(index)):
            child_index = self.proxy_model.index(row, 0, index)
            self._restore_expanded_state_recursive(child_index, expanded_items)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = Dashboard()
    viewer.show()
    sys.exit(app.exec())
