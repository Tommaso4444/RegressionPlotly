import plotly.graph_objects as go
from qgis.PyQt.QtWidgets import QDockWidget,QGridLayout ,QTabWidget, QVBoxLayout, QHBoxLayout,QWidget, QComboBox, QPushButton, QLabel, QFileDialog,QSizePolicy,QScrollArea
from qgis.core import QgsProject, QgsVectorLayer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt
import pandas as pd
import geopandas as gpd
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene
from PyQt5.QtWebKitWidgets import QWebPage, QGraphicsWebView
import plotly.graph_objects as go
import sys
from .statistical_tools import StatisticalTools
import numpy as np
import statsmodels.api as sm
from .regression_analysis_tab import RegressionAnalysisTab
from PyQt5.QtWidgets import *


class ScatterPlotDock(QDockWidget):
    
         
    
    def __init__(self, iface):
        super().__init__("RegressionPlotly")
        self.iface = iface
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.regression_tab = None
        
        # Lista dei tab
        self.tabs = QTabWidget()
        self.setWidget(self.tabs)
        
        # Tab 1
        self.scatter_tab = QWidget()
        self.setup_scatter_tab()
        self.tabs.addTab(self.scatter_tab, "Scatter Plot")

        
        # Tab 2
        self.csv_to_shp_tool_tab = QWidget()
        self.setup_csv_to_shp_tab()
        self.tabs.addTab(self.csv_to_shp_tool_tab, "Csv to GeoPackage File Tool")
        
        self.regression_tab = None
        
        
        
        
    def setup_scatter_tab(self):

        self.scatter_tab = QWidget()
        self.main_layout = QVBoxLayout(self.scatter_tab)
        self.main_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)  # Evita vincoli di layout
        
        self.string_fields = None
        
        # Dropdown per scegliere tra i layer presenti
        self.layer_dropdown = QComboBox()
        self.refresh_layers_button = QPushButton("Refresh Layers")
        
        # Bottone per importare lo shapefile
        self.select_shp_button = QPushButton("Import Shapefile")
        
        # Dropdown per la scelta delle variabili
        self.x_field_dropdown = QComboBox()
        self.y_field_dropdown = QComboBox()
        self.refresh_button = QPushButton("Draw Scatter Plot")
        
        self.regression_button = QPushButton("To Regression Analysis")
        self.regression_button.setEnabled(False)
        
        # Matplotlib Fig
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
    
        # Contenitore per i controlli
        container_widget = QWidget()
        container_widget.setObjectName("controlPanel")
    
        container_layout = QVBoxLayout(container_widget)
        container_layout.setAlignment(Qt.AlignTop)
        container_layout.setContentsMargins(10, 10, 10, 10)
    
        grid_layout = QGridLayout()
    
        grid_layout.addWidget(QLabel("Select Layer:"), 0, 0)
        grid_layout.addWidget(self.layer_dropdown, 0, 1)
        grid_layout.addWidget(self.refresh_layers_button, 0, 2)
    
        grid_layout.addWidget(QLabel("Or:"), 1, 0)
        grid_layout.addWidget(self.select_shp_button, 1, 1)
    
        grid_layout.addWidget(QLabel("X-Axis Field:"), 2, 0)
        grid_layout.addWidget(self.x_field_dropdown, 2, 1)
    
        grid_layout.addWidget(QLabel("Y-Axis Field:"), 3, 0)
        grid_layout.addWidget(self.y_field_dropdown, 3, 1)
    
        # Aggiunta di uno spacer per evitare che i pulsanti vincolino la larghezza
        grid_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum), 4, 0, 1, 3)
    
        button_row_layout = QHBoxLayout()
        self.refresh_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.regression_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
        # Impedisce ai bottoni di vincolare il layout orizzontale
        self.refresh_button.setMinimumWidth(0)
        self.regression_button.setMinimumWidth(0)
    
        button_row_layout.addWidget(self.refresh_button)
        button_row_layout.addWidget(self.regression_button)
    
        container_layout.addLayout(grid_layout)
        container_layout.addLayout(button_row_layout)
    
        container_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    
        self.main_layout.addWidget(container_widget)
    
        dynamicScatterPlot = True
    
        if not dynamicScatterPlot:
            self.main_layout.addWidget(self.canvas)
    
        # Connessioni dei pulsanti
        self.refresh_layers_button.clicked.connect(self.populate_layers)
        self.select_shp_button.clicked.connect(self.select_shapefile)
        self.layer_dropdown.currentIndexChanged.connect(self.populate_fields)
    
        # Crea interactive scatter plot viewer
        self.web_page = QWebPage()
        self.web_view = QGraphicsWebView()
        self.web_view.setPage(self.web_page)
    
        self.scene = QGraphicsScene()
        self.scene.addItem(self.web_view)
        
        self.graphics_view = QGraphicsView(self.scene)
    
        if dynamicScatterPlot:
            self.main_layout.addWidget(self.graphics_view)
            self.refresh_button.clicked.connect(self.load_interactive_scatter_plot)
        else:
            self.refresh_button.clicked.connect(self.load_scatter_plot)
    
        self.regression_button.clicked.connect(self.open_regression_analysis)
    
        # Applica QSS
        self.setStyleSheet("""
            #controlPanel {
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 10px;
            }
        """)
    
        # Imposta la politica di espansione corretta
        self.x_field_dropdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.y_field_dropdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layer_dropdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
        # Inizializza i dropdown
        self.populate_layers()


        
    
        

    def select_shapefile(self):
        """Open file dialog to select a shapefile and load it into QGIS."""
        shp_path, _ = QFileDialog.getOpenFileName(None, "Select Shapefile", "", "Shapefiles (*.shp)")
        if not shp_path:
            return  

        # Carica shapefile in QGIS
        layer = QgsVectorLayer(shp_path, f"{shp_path}", "ogr")
        if not layer.isValid():
            print("Invalid shapefile")
            return

        # Aggiungi layer al progetto QGIS 
        QgsProject.instance().addMapLayer(layer)

        # Fa un refresh dei layer disponibili
        self.populate_layers()

        # Seleziona automaticamente il nuovo layer
        index = self.layer_dropdown.findText(layer.name())
        if index >= 0:
            self.layer_dropdown.setCurrentIndex(index)

    def populate_layers(self):
        
        self.layer_dropdown.clear()
        layers = [layer for layer in QgsProject.instance().mapLayers().values() if isinstance(layer, QgsVectorLayer)]
        
        if not layers:
            self.layer_dropdown.addItem("No layers available")
            return
        
        for layer in layers:
            self.layer_dropdown.addItem(layer.name(), layer)

        # Aggiorna i campi se un layer è selezionato
        if layers:
            self.populate_fields()
            self.disable_regression_tab()

    def populate_fields(self):
        
        layer = self.get_selected_layer()
        if not layer or layer.geometryType() != 0:  
            self.x_field_dropdown.clear()
            self.y_field_dropdown.clear()
            return
        
        # Ottieni i campi numerici
        numeric_fields = [field.name() for field in layer.fields() if field.typeName() in ["Integer", "Real"]]
        
        
        if not numeric_fields:
            self.x_field_dropdown.clear()
            self.y_field_dropdown.clear()
            return
        
        # Popola dropdowns con le variabili numeriche
        self.x_field_dropdown.clear()
        self.y_field_dropdown.clear()
        self.x_field_dropdown.addItems(numeric_fields)
        self.y_field_dropdown.addItems(numeric_fields)
        
        # Seleziona la seconda variabili come dipendente di default
        if len(numeric_fields) > 1:
            self.y_field_dropdown.setCurrentIndex(1)
        
        
        self.string_fields = [field.name() for field in layer.fields() if field.typeName() == "String"]
        self.disable_regression_tab()

    def get_selected_layer(self):
        
        index = self.layer_dropdown.currentIndex()
        if index < 0:
            return None
        return self.layer_dropdown.itemData(index)
    
    def get_x_data_y_data(self):
        self.selected_layer = self.get_selected_layer()
        if not self.selected_layer:
            return
        
        x_field = self.x_field_dropdown.currentText()
        y_field = self.y_field_dropdown.currentText()
    
        self.x_data, self.y_data = [], []
        for feature in self.selected_layer.getFeatures():
           
            try:
                self.x_data.append(feature[x_field])
                self.y_data.append(feature[y_field])
                
            except:
                continue  # Skip features with missing values
        print("x_data,y_data in get_x_data_y_data")
        print(self.x_data,self.y_data)
        self.regression_button.setEnabled(True)
        return self.x_data, self.y_data,x_field,y_field
        

    def load_scatter_plot(self):
        """Loads scatter plot data based on selected fields"""
        x_data, y_data,x_field,y_field=self.get_x_data_y_data()
        print("x_data,y_data in load_scatter_plot")
        print(x_data, y_data,x_field,y_field)           
        
        self.ax.clear()
        self.ax.scatter(x_data, y_data, color="blue", alpha=0.6)
        self.ax.set_xlabel(x_field)
        self.ax.set_ylabel(y_field)
        self.ax.set_title(f"Scatter Plot of {x_field} vs {y_field}")
        self.canvas.draw()
        
    def load_interactive_scatter_plot(self):
        # Genera scatter plot usando plotly.graph_objects
        fig = go.Figure()
        x_data, y_data,x_field,y_field=self.get_x_data_y_data()
        regression_data=self.get_regression_data(x_data, y_data,x_field,y_field)
        y_pred=regression_data["y_pred"]
        
        fig.add_trace(go.Scatter(x=x_data, y=y_data, 
                                 mode='markers', marker=dict(size=6, color='red'),name="Data Point"))
        fig.add_trace(go.Scatter(x=x_data, y=y_pred, mode='lines', line=dict(color='blue', width=1.5), name="Regression Line"))
        fig.update_layout(title="Interactive Scatter Plot",xaxis_title=f"{x_field}",
        yaxis_title=f"{y_field}",template="plotly_white")
        fig.update_layout(
            width=675,  
            height=450,  
        )

        # rappresentazione HTML 
        html = fig.to_html(full_html=False, include_plotlyjs='cdn')

        # Caricamento HTML in una QWebPage
        self.web_page.mainFrame().setHtml(html)
        
    def get_regression_data(self,x_data, y_data,x_field,y_field):

    
        x_with_const = sm.add_constant(x_data)  
        model = sm.OLS(y_data, x_with_const).fit()  # Fit Ordinary Least Squares model
        y_pred = model.predict(x_with_const) 
        print(y_pred)
        print(model.summary())
        rse = model.mse_resid ** 0.5
        return {"y_pred":y_pred,"rse":rse}
    
    def open_regression_analysis(self):
        
        
        x_field_selected_value = self.x_field_dropdown.currentText()
        x_field_items_list = [self.x_field_dropdown.itemText(i) for i in range(self.x_field_dropdown.count())]
        y_field_selected_value = self.y_field_dropdown.currentText()
        y_field_items_list = [self.y_field_dropdown.itemText(i) for i in range(self.y_field_dropdown.count())]

        if not self.regression_tab:  # Create only if it doesn't exist
            self.regression_tab = RegressionAnalysisTab(self.x_data, self.y_data,
                                                        x_field_selected_value,x_field_items_list,
                                                        y_field_selected_value,y_field_items_list,self.string_fields,
                                                        self.selected_layer
                                                        )
            self.tabs.addTab(self.regression_tab, "Regression Analysis")
        
        self.tabs.setCurrentWidget(self.regression_tab)  # Switch to the new tab
    
    
    
    
    
    
    
    
    
        
    def setup_csv_to_shp_tab(self):
        """Set up the second tab with vertical alignment at the start."""

        # Main layout (Vertical Box) with top alignment
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)  # Align all widgets to the top
    
        
        self.import_csv_button = QPushButton("Import CSV")
    
        
        container_widget = QWidget()
        container_widget.setObjectName("controlPanel")  
    
        container_layout = QVBoxLayout(container_widget)
        container_layout.setAlignment(Qt.AlignTop)  
        container_layout.setContentsMargins(10, 10, 10, 10)  
    
        container_layout.addWidget(self.import_csv_button)
    
        self.grid_layout = QGridLayout()
    
        # Crea dropdowns 
        self.lat_field_dropdown = QComboBox()
        self.lon_field_dropdown = QComboBox()
        self.lat_field_dropdown.setEnabled(False)
        self.lon_field_dropdown.setEnabled(False)
    
        # Aggiungi dropdowns al grid layout
        self.grid_layout.addWidget(QLabel("Latitude Field:"), 0, 0)
        self.grid_layout.addWidget(self.lat_field_dropdown, 0, 1)
        self.grid_layout.addWidget(QLabel("Longitude Field:"), 1, 0)
        self.grid_layout.addWidget(self.lon_field_dropdown, 1, 1)
    
        
        container_layout.addLayout(self.grid_layout)
    
        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setFixedHeight(200)  
        container_layout.addWidget(self.table_widget)
    
        # Crea bottone create SHP 
        self.create_shp_button = QPushButton("Create GPKG File")
        self.create_shp_button.setEnabled(False)
        container_layout.addWidget(self.create_shp_button)
    
        # Connectti i bottoni ai rispettivi metodi
        self.import_csv_button.clicked.connect(self.select_csv)
        self.lat_field_dropdown.currentIndexChanged.connect(self.check_dropdowns)
        self.lon_field_dropdown.currentIndexChanged.connect(self.check_dropdowns)
        self.create_shp_button.clicked.connect(self.create_shp)
        
        container_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
    
        
        self.layout.addWidget(container_widget, alignment=Qt.AlignTop)
    
        
        self.csv_to_shp_tool_tab.setLayout(self.layout)

        
    def check_dropdowns(self):
        """Abilità Create SHP button solo se entrambi i dropdowns sono selezionati."""
        lat_selected = self.lat_field_dropdown.currentText() != ""
        lon_selected = self.lon_field_dropdown.currentText() != ""
        self.create_shp_button.setEnabled(lat_selected and lon_selected)

    def populate_csv_fields(self):
        """Popola i dropdowns con i nomi dei campi del CSV selezionato."""
        if not hasattr(self, 'fields_csv') or not self.fields_csv:
            print("No fields available to populate")
            return
    
        self.lon_field_dropdown.clear()
        self.lat_field_dropdown.clear()
    
        self.lon_field_dropdown.addItems(self.fields_csv)
        self.lat_field_dropdown.addItems(self.fields_csv)
        
        # Prova a selezionare automaticamente, come items latitudine e longitudine dei dropdowns, eventuali campi contenenti "lat" e "lon" 
        self.lon_index = next((i for i, field in enumerate(self.fields_csv) if "lon" in field.lower()), -1)
        self.lat_index = next((i for i, field in enumerate(self.fields_csv) if "lat" in field.lower()), -1)
        print(f"lon_index ${self.lon_index}")
    

        if self.lon_index != -1:
            self.lon_field_dropdown.setCurrentIndex(self.lon_index)
        if self.lat_index != -1:
            self.lat_field_dropdown.setCurrentIndex(self.lat_index)
    
    def select_csv(self):
        """Seleziona un CSV mostrando il fragment con il relativo datafram"""
        csv_path, _ = QFileDialog.getOpenFileName(None, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if not csv_path:
            return  
    
        self.filename = csv_path.split("/")[-1].split(".")[0]
        
        # Carica il CSV con Pandas e sostituisce , con . come separatore dei decimali
        self.df = pd.read_csv(csv_path)
        print("dataframe");print(self.df)
        self.df = self.df.applymap(lambda x: float(str(x).replace(',', '.')) if isinstance(x, str) and x.replace(',', '').replace('.', '').isdigit() else x)
        self.fields_csv = self.df.columns.tolist()
        print(self.fields_csv)
        
       
        self.populate_csv_fields()
        self.lat_field_dropdown.setEnabled(True)
        self.lon_field_dropdown.setEnabled(True)
        
        self.display_dataframe_fragment(self.df.head())  # Show only first 5 rows
        
    def display_dataframe_fragment(self,df):
        self.table_widget.clear()
        self.table_widget.setRowCount(df.shape[0]) 
        self.table_widget.setColumnCount(df.shape[1])
        self.table_widget.setHorizontalHeaderLabels(df.columns)
        
        for i in range(df.shape[0]):  
            for j in range(df.shape[1]): 
                print(f"riga {i}, colonna {j}")
                self.table_widget.setItem(i,j,QTableWidgetItem(str(df.iloc[i,j])))
        self.table_widget.resizeColumnsToContents() 
        
    
    def create_shp(self):
            
        df=self.df
        print("df")
        print(df)
        lon_field=self.fields_csv[self.lon_index]
        lat_field=self.fields_csv[self.lat_index]
        # Converti il CSV in GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon_field], df[lat_field]))
        gdf.set_crs(epsg=4326, inplace=True)  # WGS 84
        
        filename=self.filename
    
        # Salva come Shapefile
        shp_path = rf"C:\Users\tomma\shp_prova\{filename}.shp"
        gdf.to_file(shp_path, driver="ESRI Shapefile")
    
        # Carica il Shapefile come layer in QGIS
        layer = QgsVectorLayer(shp_path, filename, "ogr")
        if not layer.isValid():
            print("Invalid shapefile")
            return
        
        # Salva in GeoPackage invece di Shapefile
        gpkg_path = rf"C:\Users\tomma\shp_prova\{filename}.gpkg"
        gdf.to_file(gpkg_path, driver="GPKG")
    
        # Carica il GeoPackage come layer in QGIS
        layer = QgsVectorLayer(gpkg_path, filename, "ogr")
        if not layer.isValid():
            print("Invalid GeoPackage")
            return
    
        QgsProject.instance().addMapLayer(layer)
        
        
    def disable_regression_tab(self):
        
        if not hasattr(self, 'regression_tab'):
            self.regression_tab = None
        
        self.regression_button.setEnabled(False)
    
        if self.regression_tab:
            index = self.tabs.indexOf(self.regression_tab)
            if index != -1:
                self.tabs.removeTab(index)
            self.regression_tab = None

    
        
        
    
    
    

    
            

        
        
    
    
    
