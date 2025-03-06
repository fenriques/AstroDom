import sqlite3, sys, logging
import pandas as pd
from PyQt6.QtWidgets import QApplication, QTreeView,QHeaderView
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
        self.itemList = ["Target", "#", "Exposure", "Size", "Date", "Time","Filter","FWHM", "Eccentricity","SNR","ALT", "AZ", "Temp", "Frame",
                         "Bin","RA", "DEC", "Gain", "Offset", "Mean", "Median", "Site Lat", "Site Long", "Moon Phase", "Moon Separation","File"]
        self.setGeometry(100, 100, 800, 600)
        
        self.load_data()
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.setAlternatingRowColors(True)
        self.header().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self.dateDelegate = DateDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("Date"), self.dateDelegate)

        self.timeDelegate = TimeDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("Time"), self.timeDelegate)

        self.filterDelegate = FilterDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("Filter"), self.filterDelegate)

        self.fwhmDelegate = FWHMDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("FWHM"), self.fwhmDelegate)
        self.fwhmDelegate.setLimit(FWHM_LIMIT_DEFAULT)

        self.eccentricityDelegate = EccentricityDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("Eccentricity"), self.eccentricityDelegate)
        self.eccentricityDelegate.setLimit(ECCENTRICITY_LIMIT_DEFAULT)

        self.snrDelegate = SNRDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("SNR"), self.snrDelegate)
        self.snrDelegate.setLimit(SNR_LIMIT_DEFAULT)

        self.altDelegate = AltDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("ALT"), self.altDelegate)
        self.altDelegate.setLimit(ALT_LIMIT_DEFAULT)

        self.azDelegate = DmsDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("AZ"), self.azDelegate)

        self.frameDelegate = FrameDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("Frame"), self.frameDelegate)

        self.raDelegate = HmsDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("RA"), self.raDelegate)

        self.decDelegate = DmsDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("DEC"), self.decDelegate)
        
        self.siteLatDelegate = DmsDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("Site Lat"), self.siteLatDelegate)
        
        self.siteLongDelegate = DmsDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("Site Long"), self.siteLongDelegate)
        
        self.moonSeparationDelegate = DmsDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("Moon Separation"), self.moonSeparationDelegate)
                
        self.roundDelegate = RoundDelegate(self)
        self.setItemDelegateForColumn(self.itemList.index("Mean"), self.roundDelegate)
        self.setItemDelegateForColumn(self.itemList.index("Median"), self.roundDelegate)
        
        allAdditionalColumns = ["Temp", "Frame","Bin","RA", "DEC", "Gain", "Offset", "Mean", "Median", "Site Lat", "Site Long", "Moon Phase", "Moon Separation", "File"]
        hidden_columns = [col for col in allAdditionalColumns if col not in ADDITIONAL_COLUMNS]
        
        self.hide_columns(hidden_columns)


    def on_selection_changed(self, selected, deselected):
        return
        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            index = indexes[0]
            model_index = self.proxy_model.mapToSource(index)
            value = self.proxy_model.sourceModel().data(model_index.siblingAtColumn(self.itemList.index("File")), Qt.ItemDataRole.DisplayRole)
    
    def applyThreshold(self,fwhm, snr, alt, eccentricity):
        # setLimit is a method in the Delegate classes that formats the threshold values
        self.fwhmDelegate.setLimit(float(fwhm))
        self.eccentricityDelegate.setLimit(float(eccentricity))
        self.altDelegate.setLimit(float(alt))
        self.snrDelegate.setLimit(float(snr))
        expanded_items = self.save_expanded_state()
        
        # setThresholds sets the threshold values in the model
        self.model.setThresholds(fwhm, snr, alt, eccentricity)

        self.proxy_model.layoutChanged.emit()
        self.restore_expanded_state(expanded_items)

    def load_data(self):
        sqlString = ""
        selected_filter = self.parent.filterSelectComboBox.currentText()
        selected_target = self.parent.targetComboBox.currentText()

        if selected_filter != "--Filter--" and selected_filter != "":
            sqlString = f" AND FILTER = '{selected_filter}' "

        if selected_target != "--Target--" and selected_target != "":
            sqlString += f" AND OBJECT = '{selected_target}' "

        # Connect to the database
        db_path = str(self.parent.rsc_path.joinpath( DBNAME))
        conn = sqlite3.connect(db_path)

        if hasattr(self.parent, 'projectStatus') and self.parent.projectStatus != 'Active':
            self.parent.syncButton.setEnabled(False)

        if not self.project_id or self.project_id == 0:
            query = f"SELECT * FROM images ORDER BY PROJECT_ID DESC, DATE_OBS ASC"

        elif self.project_id > 0: 
            query = f"SELECT * FROM images WHERE PROJECT_ID = {self.project_id} {sqlString} ORDER BY  PROJECT_ID DESC,  DATE_OBS ASC"
            logging.debug(f"Loading data: {query}")   
        try:
            self.df = pd.read_sql_query(query, conn)
            conn.close()
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.close()
            return

        # Set the model
        self.model = CustomTreeModel(self.df, parent=self)
        self.proxy_model = CustomFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.setModel(self.proxy_model)
        
        # By default, expand the first item so the single filters are visible
        self.expand(self.proxy_model.index(0, 0))

    # The project_id is set automatically at startup and updated when a project is selected
    def setProjectID(self,project_id):
        self.project_id = project_id
        self.load_data()

    def update_contents(self,selected_project_id):
        self.proxy_model.setFilterString(str(selected_project_id))
        

    def hide_columns(self, columns_to_hide):
        for column_name in columns_to_hide:
            column_index = self.itemList.index(column_name)
            self.setColumnHidden(column_index, True)

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

