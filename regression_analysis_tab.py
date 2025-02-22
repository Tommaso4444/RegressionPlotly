from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtWidgets import (
    QWidget, QTextEdit, QDialog, QDialogButtonBox, QComboBox, 
    QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QSizePolicy, 
    QTableWidget, QTableWidgetItem, QLabel, QGraphicsView, QGraphicsScene, 
    QPushButton, QListWidget, QListWidgetItem, QFileDialog
)
from PyQt5.QtWebKitWidgets import QGraphicsWebView, QWebPage

import plotly.graph_objects as go
import statsmodels.api as sm
from array import array
import numpy as np
import pandas as pd

from qgis.core import (
    QgsVectorLayer, QgsFeature, QgsFields, QgsField, QgsGeometry, QgsProject, 
    QgsVectorFileWriter, QgsWkbTypes, QgsGraduatedSymbolRenderer, 
    QgsRendererRange, QgsSymbol, QgsColorRampShader, QgsRuleBasedRenderer, 
    QgsMarkerSymbol, QgsRasterShader, QgsSingleSymbolRenderer, QgsProperty, 
    QgsSymbolLayer, QgsClassificationRange, QgsGradientColorRamp
)
from qgis.core import QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling
from qgis.PyQt.QtGui import QColor


class RegressionAnalysisTab(QWidget):
    
    def __init__(self, x_data, y_data,
                  x_field_selected_value, x_field_items_list,
                  y_field_selected_value, y_field_items_list, string_fields, selected_layer):
        super().__init__()
        self.x_data = x_data
        self.y_data = y_data
        self.selected_layer = selected_layer
        self.x_field_items_list=x_field_items_list
        self.string_fields=string_fields
        
        print("x_field_selected_value");
        print(x_field_selected_value);
        print("y_field_selected_value");
        print(y_field_selected_value);
        
        
        self.selected_covariate_fields_multiselector=None
        
        
        self.attribute_table=[]
        self.model_variables=[]
        self.dependent_variable_name=None
        self.regression_data=None

        # Crea dropdowns
        self.model_dropdown = QComboBox()
        self.x_single_field_dropdown = QComboBox()
        self.y_field_dropdown = QComboBox()
        self.geo_label_dropdown = QComboBox()
        
        self.model_dropdown.addItems(["Simple Linear Regression", "Multiple Linear Regression"])
        self.x_single_field_dropdown.addItems(x_field_items_list)
        self.y_field_dropdown.addItems(y_field_items_list)
        self.geo_label_dropdown.addItems(string_fields)

        # Multi-selection lista per le variabili X 
        self.x_list_widget = QListWidget()
        self.x_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.x_list_widget.setFixedSize(350, 95)
        
        # Crea QWebPage e QGraphicsWebView per il grafico sottostante
        self.web_page = QWebPage()
        self.web_view = QGraphicsWebView()
        self.web_view.setPage(self.web_page)

        
        self.scene = QGraphicsScene()
        self.scene.addItem(self.web_view)
        
        self.graphics_view = QGraphicsView(self.scene)

        # Aggiungi "Select All" al selettore multiplo
        select_all_item = QListWidgetItem("Select All")
        self.x_list_widget.addItem(select_all_item)
        
        # Aggiungi le label delle covariate al selettore multiplo
        for x_var in x_field_items_list:
            self.x_list_widget.addItem(QListWidgetItem(x_var))

        
        self.x_list_widget.itemClicked.connect(self.handle_covariate_selection)
        
        self.y_field_dropdown.currentIndexChanged.connect(self.handle_covariate_selection_when_dep_variable_changes)
        
        
        # Clear selection bottone per deselezionare le covariate
        self.clear_covariates_button = QPushButton("Clear")
        self.clear_covariates_button.clicked.connect(self.clear_covariates_selection)
        

        

        button_row_layout = QHBoxLayout()
        # Start regression button
        self.start_regression_analysis_button = QPushButton("Start Regression Analysis")
        self.start_regression_analysis_button.clicked.connect(self.load_interactive_scatter_plot)
        self.start_regression_analysis_button.clicked.connect(self.show_regression_results_dialog)
        
        
        self.show_fitted_values_button = QPushButton("Show fit and residuals values table")
        self.export_button = QPushButton("Export GPKG file with Fit Statistics")
        self.show_fitted_values_button.setEnabled(False);self.export_button.setEnabled(False)
        
        # Crea un layout orizzonatale per i bottoni
        button_row_layout.addWidget(self.start_regression_analysis_button)
        button_row_layout.addWidget(self.show_fitted_values_button)
        button_row_layout.addWidget(self.export_button)
        
        self.show_fitted_values_button.clicked.connect(self.show_attribute_table)
        self.export_button.clicked.connect(self.export_shp_with_attribute_table)
        
        
        
        
        
        
        
        
        
        
        
        self.model_dropdown.currentIndexChanged.connect(self.toggle_x_list_widget_visibility)

        
        container_widget = QWidget()
        container_widget.setObjectName("controlPanel")  
        
        container_layout = QVBoxLayout(container_widget)
        container_layout.setAlignment(Qt.AlignTop) 
        container_layout.setContentsMargins(10, 10, 10, 10)  
        grid_layout = QGridLayout()
        
      
        
        
        self.label_single_x_field=QLabel("Var. X Field:")
        self.label_multiple_x_fields=QLabel("Var. X Fields (Covariates):")
        
        self.inner_grid_layout_covariates = QGridLayout()
        self.inner_grid_layout_covariates.addWidget(self.x_list_widget, 0, 0)
        self.inner_grid_layout_covariates.addWidget(self.clear_covariates_button, 0, 1)
    

        grid_layout.addWidget(QLabel("Model Type:"), 0, 0)
        grid_layout.addWidget(self.model_dropdown, 0, 1)
        grid_layout.addWidget(self.label_single_x_field, 1, 0)
        grid_layout.addWidget(self.x_single_field_dropdown, 1, 1)
        grid_layout.addWidget(self.label_multiple_x_fields, 2, 0)
        grid_layout.addLayout(self.inner_grid_layout_covariates, 2, 1)
        grid_layout.addWidget(QLabel("Var. Y Field:"), 3, 0)
        grid_layout.addWidget(self.y_field_dropdown, 3, 1)
        grid_layout.addWidget(QLabel("Geographic label:"), 4, 0)
        grid_layout.addWidget(self.geo_label_dropdown, 4, 1)
        
        
        self.x_single_field_related_objs=[self.label_single_x_field,self.x_single_field_dropdown]
        self.x_multiple_field_related_objs=[self.label_multiple_x_fields,self.inner_grid_layout_covariates]

        container_layout.addLayout(grid_layout)
        container_layout.addLayout(button_row_layout)

        # Scrollable area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(container_widget)
        
        # Applica larghezza fissa e altezza dinamica
        self.scroll_area.setMinimumHeight(0)
        self.scroll_area.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)

        
        main_layout = QVBoxLayout()
        
        main_layout.addWidget(self.scroll_area)  
        main_layout.addWidget(self.graphics_view)  # QGraphicsView (Plotly plot) at the top
        self.setLayout(main_layout)
        
        self.initialize_dropdowns_values(x_field_selected_value,y_field_selected_value,x_field_items_list)
        self.toggle_x_list_widget_visibility()
        
        
        
        self.setStyleSheet("""
            #controlPanel {
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 10px;
            }
            QScrollArea {
                border: none;
            }
        """)
        
    def initialize_dropdowns_values(self,x_field_selected_value,y_field_selected_value,x_field_items_list):
        print("x_field_items_list");print(x_field_items_list)
        x_field_index=0;y_field_index=1
        print("initialize_dropdowns_values(self)")
        if x_field_selected_value in x_field_items_list:
            x_field_index=x_field_items_list.index(x_field_selected_value)
        if y_field_selected_value in x_field_items_list:
            y_field_index=x_field_items_list.index(y_field_selected_value)
        self.x_single_field_dropdown.setCurrentIndex(x_field_index);
        self.y_field_dropdown.setCurrentIndex(y_field_index);
        
    def load_interactive_scatter_plot(self):
        
        print("self.x_data");
        print(self.x_data);
        fig = go.Figure()
        fig.update_layout(autosize=True, margin=dict(l=50, r=50, t=50, b=50))
        fig.update_layout(
            width=675,  
            height=450, 
        )
        
        x_data, y_data, x_field, y_field = self.get_x_data_y_data()
        print("x_data in load_interactive_scatter_plot");print(x_data);print("y_data in load_interactive_scatter_plot");print(y_data)
        
        self.regression_data = self.get_regression_data(x_data, y_data, x_field, y_field)
        print("x_field load_interactive_scatter_plot");print(x_field)
        
        if self.model_dropdown.currentText() == "Simple Linear Regression":
            y_pred = self.regression_data["y_pred"]
            x_data=[x[0] for x in x_data]
    
            fig.add_trace(go.Scatter(x=x_data, y=y_data, 
                                     mode='markers', marker=dict(size=6, color='red'),name="Data Point"))
            fig.add_trace(go.Scatter(x=x_data, y=y_pred, mode='lines', line=dict(color='blue', width=1.5), name="Regression Line"))
            fig.update_layout(title="Interactive Scatter Plot",xaxis_title=f"{x_field[0]}",
            yaxis_title=f"{y_field}",
            template="plotly_white")
    
            
            html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
            
            self.web_page.mainFrame().setHtml(html)
        
        else :
            y_pred = self.regression_data["y_pred"]

            
            residuals = [y_obs - y_hat for y_obs, y_hat in zip(y_data, y_pred)]
            
            
            x_data = [x[0] for x in x_data]
            
            # Crea Plotly Figure
            fig = go.Figure()
            
            # Aggiungi coppie (valore reale, valore stimato)
            fig.add_trace(go.Scatter(
                x=y_data, 
                y=y_pred, 
                mode='markers', 
                marker=dict(size=6, color='red'),
                name="Data Point"
            ))
            
            
            min_val, max_val = min(y_data), max(y_data)
            fig.add_trace(go.Scatter(x=[min_val, max_val], y=[min_val, max_val], 
                         mode='lines', line=dict(color='blue', dash='dot', width=1), 
                         name="Perfect Fit (y=x)"))
            
            
            
            fig.update_layout(
                title=f"Observed - Predicted Plot: {y_field}",
                xaxis_title=f"Observed {y_field}",
                yaxis_title="Predicted",
                template="plotly_white"
            )
            fig.update_layout(autosize=True, margin=dict(l=50, r=50, t=50, b=50))
            fig.update_layout(
                width=675,  
                height=450,  
            )
            
            
            html = fig.to_html(full_html=False, include_plotlyjs='cdn')
            
    
            self.web_page.mainFrame().setHtml(html)
        
    def get_x_data_y_data(self):
        layer = self.selected_layer
        if not layer:
            return
        
        x_field=None;x_fields=None; x_fields=[]
        if self.model_dropdown.currentText() == "Simple Linear Regression":
            x_fields.append(self.x_single_field_dropdown.currentText())
        else:
            x_fields = self.selected_covariate_fields_multiselector
            
        y_field = self.y_field_dropdown.currentText()
        self.dependent_variable_name = y_field
    
        self.x_data, self.y_data = [], []
        if self.model_dropdown.currentText() == "Simple Linear Regression":
           
            for feature in layer.getFeatures():
                try:
                    x_values = [feature[field] for field in x_fields]
                    self.x_data.append(x_values)
                    self.y_data.append(feature[y_field])
                    self.attribute_table.append(feature.attributes())
                except KeyError:
                    continue  # Salta le features con valori mancanti

            
        
        elif self.model_dropdown.currentText() == "Multiple Linear Regression":
            for feature in layer.getFeatures():
                try:
                    x_values = [feature[field] for field in x_fields]
                    self.x_data.append(x_values)
                    self.y_data.append(feature[y_field])
                    self.attribute_table.append(feature.attributes())
                except KeyError:
                    continue  # Salta le features con valori mancanti

        
            
        
        return self.x_data, self.y_data, x_fields, y_field
        
    def get_regression_data(self, x_data, y_data, x_fields, y_field):
       
        x_df = pd.DataFrame()        
        for i in range(len(x_fields)):
            series = pd.Series([row[i] for row in x_data], name=x_fields[i])
            x_df[x_fields[i]] = series
        
        x_with_const = sm.add_constant(x_df)
        
        
        model = sm.OLS(y_data, x_with_const).fit()  
        y_pred = model.predict(x_with_const) 
        summary = model.summary().as_text()
        rse = model.mse_resid ** 0.5
        r_squared = model.rsquared
        coefficients = model.params
        p_values = model.pvalues
        t_values = model.tvalues  
        std_errors = model.bse
        covariate_names = model.model.exog_names

        return {"y_pred": y_pred, "rse": rse,"summary": summary ,"r^2":r_squared,"coefficients":model.params,
                "p_values":p_values,"t_stats":t_values,"std_errors":std_errors,"dependent_variable":y_field,"model_variables":covariate_names}
    
    def handle_covariate_selection(self, item):
        
        y_field=self.y_field_dropdown.currentText()
        if item.text() == "Select All":
            select_all = item.isSelected()
            for i in range(1, self.x_list_widget.count()): 
                if self.x_list_widget.item(i).text()!=y_field:
                    
                    self.x_list_widget.item(i).setSelected(select_all)

        selected_items = self.x_list_widget.selectedItems()
        self.selected_covariate_fields_multiselector = [item.text() for item in selected_items
                                                        if item.text() != "Select All"]
        
        
        
    def handle_covariate_selection_when_dep_variable_changes(self):
    
        y_field=self.y_field_dropdown.currentText()
        
        selected_items = self.x_list_widget.selectedItems()

        # Controlla se l'opzione "Select All" è selezionata, in questo caso si deseleziona la variabile mostrata come dipendente da y_field_dropdown
        if any(item.text() == "Select All" for item in selected_items) and self.model_dropdown.currentText() == "Multiple Linear Regression":
            print("Select All is selected")
        
            for i in range(0, self.x_list_widget.count()):  
                select_all = self.x_list_widget.item(i).isSelected()
                if self.x_list_widget.item(i).text()!=y_field:
                    
                    self.x_list_widget.item(i).setSelected(select_all)
    
            selected_items = self.x_list_widget.selectedItems()
            self.selected_covariate_fields_multiselector = [item.text() for item in selected_items
                                                            if item.text() != "Select All"]
            
        
    
                
    
    def clear_covariates_selection(self):
        for index in range(self.x_list_widget.count()):
            item = self.x_list_widget.item(index)
            item.setSelected(False)  # Deseleziona ogni item
        
        
    def toggle_x_list_widget_visibility(self):
        is_multiple = self.model_dropdown.currentText() == "Multiple Linear Regression"

        # Toggle la visibilità of singolo X dropdown e del selettore multiplo delle covariate X 
        self.set_widgets_visibility(self.x_multiple_field_related_objs, is_multiple)
        self.set_widgets_visibility(self.x_single_field_related_objs, not is_multiple)
        
        
        if is_multiple:
            new_height = 230  
        else:
            new_height = 155  
    
        self.scroll_area.setFixedHeight(new_height) 
        self.scroll_area.adjustSize()  
            
    def set_widgets_visibility(self, widgets, visible):
       
        for widget in widgets:
            if isinstance(widget, QGridLayout):
                
                for i in range(widget.count()):
                    item = widget.itemAt(i)
                    if item and item.widget():
                        item.widget().setVisible(visible)
            else:
                widget.setVisible(visible)
                
    def show_regression_results_dialog(self):
        """Show a dialog with the regression summary results."""
        x_data, y_data, x_field, y_field = self.get_x_data_y_data()
        self.regression_data = self.get_regression_data(x_data, y_data, x_field, y_field)

        # Ottieni il regression model summary
        model_summary = self.regression_data["summary"]  # This is the summary as a string
        dependent_variable=self.regression_data["dependent_variable"]
    
        # Crea un dialog per mostrare il summary
        dialog = QDialog(self)
        dialog.setModal(False)
        dialog.setWindowTitle("Regression Results")
        dialog.resize(520, 300) 
        dialog_layout = QVBoxLayout(dialog)
    
        # Crea un QTableWidget per mostrare i risultati
        regr_covariates_table_widget = QTableWidget(dialog)
       
        
        # numero di righe (una per ogni variabile)
        num_rows = len(self.regression_data["coefficients"])
        regr_covariates_table_widget.setRowCount(num_rows)
        
        model_variables=self.regression_data["model_variables"]
        self.model_variables = model_variables
        t_stats=self.regression_data["t_stats"]
       
      
        
        # numero di colonne (nome variabile, coefficiente, standard error, t-value ,p-value)
        regr_covariates_table_widget.setColumnCount(5)
    
        regr_covariates_table_widget.setHorizontalHeaderLabels(["Variable", "Coefficient", "Standard Error","T-value" ,"P-value"])
        
       
        row = 0
       
        
        
        
        for param, coef in enumerate(self.regression_data["coefficients"]):
            regr_covariates_table_widget.setItem(row, 0, QTableWidgetItem(model_variables[row]))
            regr_covariates_table_widget.setItem(row, 1, QTableWidgetItem(f"{coef:.4f}"))
            regr_covariates_table_widget.setItem(row, 2, QTableWidgetItem(f"{self.regression_data['std_errors'][param]:.4f}"))
            regr_covariates_table_widget.setItem(row, 3, QTableWidgetItem(f"{t_stats[param]:.4f}"))
            regr_covariates_table_widget.setItem(row, 4, QTableWidgetItem(f"{self.regression_data['p_values'][param]:.4f}"))

            row += 1
        
        
        
        # Aggiungi la table al dialog
        dialog_layout.addWidget(QLabel(f"<b>Dependent variable:</b> {dependent_variable}"))
        dialog_layout.addWidget(regr_covariates_table_widget)
        dialog_layout.addWidget(QLabel(f"<b>R-squared:</b> {self.regression_data['r^2']:.4f}         <b>Residual Std. Error:</b> {self.regression_data['rse']:.4f}"))
        
    
        #  Aggiungi OK button
        buttons = QDialogButtonBox(QDialogButtonBox.Ok, Qt.Horizontal)
        buttons.accepted.connect(dialog.accept)
        dialog_layout.addWidget(buttons)
        
        self.show_fitted_values_button.setEnabled(True);self.export_button.setEnabled(True)
    
        dialog.show()
        
    
        
    def show_attribute_table(self):
        if not self.selected_layer:
            print("No active layer selected.")
            return
        
        
        covariates_involved = [var for var in self.model_variables if var != 'const']
     
        dependent_variable_name=self.y_field_dropdown.currentText()
        fitted_values=self.regression_data["y_pred"]
        geo_label=self.geo_label_dropdown.currentText()
        covariates_involved.insert(0,geo_label)
        covariates_involved.insert(1,dependent_variable_name)
        
        
    
       
        attribute_table = [feature.attributes() for feature in self.selected_layer.getFeatures()]
        
        attribute_table_fields = [field.name() for field in self.selected_layer.fields()]
        
        
        
        df_attribute_table = pd.DataFrame(attribute_table, columns=attribute_table_fields)
        
    
        # Scegli solo le variabili covariate selezionate
        df_attribute_table_cols_invol = df_attribute_table[covariates_involved]
        
        
        df_attribute_table_cols_invol.insert(1, f'Fitted Values {dependent_variable_name}', fitted_values)
        
        residuals=self.y_data-fitted_values
        df_attribute_table_cols_invol.insert(3, f'Residuals {dependent_variable_name}', residuals)
        
        
   
        
        # Crea un QDialog per la table
        dialog = QDialog(self)
        dialog.setWindowTitle("Attribute Table")
        
    
        table_widget = QTableWidget(dialog)
        num_rows, num_cols = df_attribute_table_cols_invol.shape
        table_widget.setRowCount(num_rows)
        table_widget.setColumnCount(num_cols)
        table_widget.setHorizontalHeaderLabels(df_attribute_table_cols_invol.columns)
    
        for index, row in df_attribute_table_cols_invol.iterrows():
            
            for col_index, col_name in enumerate(df_attribute_table_cols_invol.columns):
                value = row[col_name]
                item = QTableWidgetItem(str(value))  # Converti valori in string
                table_widget.setItem(index, col_index, item)
    
        layout = QVBoxLayout(dialog)
        layout.addWidget(table_widget)
        

        dialog.setGeometry(100, 100, 600, 400)
        dialog.show()
        
    def export_shp_with_attribute_table(self):
        if not self.selected_layer:
            print("No active layer selected.")
            return
        
        
        covariates_involved = [var for var in self.model_variables if var != 'const']
     
        dependent_variable_name=self.y_field_dropdown.currentText()
        fitted_values=self.regression_data["y_pred"]
        geo_label=self.geo_label_dropdown.currentText()
        covariates_involved.insert(0,geo_label)
        covariates_involved.insert(1,dependent_variable_name)
        
        
    
     
        attribute_table = [feature.attributes() for feature in self.selected_layer.getFeatures()]
        
        attribute_table_fields = [field.name() for field in self.selected_layer.fields()]
        
        
        
        
     
        df_attribute_table = pd.DataFrame(attribute_table, columns=attribute_table_fields)
        
    
       
        df_attribute_table_cols_invol = df_attribute_table[covariates_involved]
        
       
        df_attribute_table_cols_invol.insert(1, f'Fitted Values {dependent_variable_name}', fitted_values)
        
        residuals=self.y_data-fitted_values
        df_attribute_table_cols_invol.insert(3, f'Residuals {dependent_variable_name}', residuals)
        
        cloned_layer=self.clone_selected_vector_layer(fitted_values,residuals,dependent_variable_name)
        self.style_and_save_cloned_layer(cloned_layer)
   
        
        
        
    def clone_selected_vector_layer(self, fitted_values, residuals,dependent_variable_name):
        if not self.selected_layer or not isinstance(self.selected_layer, QgsVectorLayer):
            print("No vector layer selected")
            return
    
        # Ottieni le varie proprietà dell'original layer
        layer_crs = self.selected_layer.crs().authid()  # Get CRS
        layer_geometry = QgsWkbTypes.displayString(self.selected_layer.wkbType())  # Get geometry type
        layer_fields = self.selected_layer.fields()  # Get existing fields
    
        # Crea un nuovo vector layer clonando l'originale
        layer_uri = f"{layer_geometry}?crs={layer_crs}"
        cloned_layer = QgsVectorLayer(layer_uri, self.selected_layer.name() + f"_Fitted Values_{dependent_variable_name}", "memory")
        provider = cloned_layer.dataProvider()
    
        # Aggiungi original fields
        provider.addAttributes(layer_fields)
        
        # Aggiungi altri campi per Fitted Values e Residuals
        provider.addAttributes([
            QgsField(f"Fitted Values {self.y_field_dropdown.currentText()}", QVariant.Double),
            QgsField(f"Residuals {self.y_field_dropdown.currentText()}", QVariant.Double)
        ])
        
        cloned_layer.updateFields()
    
        
        features = list(self.selected_layer.getFeatures())
        print("features in clone_selected_vector_layer");print(features)
        cloned_layer.startEditing()
        
        for i, feature in enumerate(features):
            new_feature = QgsFeature()
            new_feature.setGeometry(feature.geometry())  # Copy geometry
    
            # Copia attributi originali
            new_attributes = feature.attributes()
    
            # Aggiungi Fitted Values e Residuals 
            fitted_value = fitted_values[i] if i < len(fitted_values) else None
            residual_value = residuals[i] if i < len(residuals) else None
            new_attributes.extend([fitted_value, residual_value])
    
            new_feature.setAttributes(new_attributes)
            cloned_layer.addFeature(new_feature)
    
        cloned_layer.commitChanges()
    
        # Aggiungi il cloned layer al progetto
        QgsProject.instance().addMapLayer(cloned_layer)
        
    
        return cloned_layer
    
    




    
    
    
    
    def style_and_save_cloned_layer(self, cloned_layer):
        """Applica simbologia graduata (grandezza e colore dei punti, aggiungi il layer alla mappa e permetti il salvataggio)."""
        field_name = f"Fitted Values {self.y_field_dropdown.currentText()}"
        
        if not cloned_layer or cloned_layer.fields().indexFromName(field_name) < 0:
            print("Cloned layer or field not found.")
            return
    
        # Color ramp 
        color_ramp = QgsGradientColorRamp(QColor(255, 236, 161), QColor(255, 0, 0))
        
      
    
        # min/max valori per la normalizzazione
        min_value = cloned_layer.minimumValue(cloned_layer.fields().indexFromName(field_name))
        max_value = cloned_layer.maximumValue(cloned_layer.fields().indexFromName(field_name))
    
        if min_value == max_value:
            print("No variation in fitted values; thematization skipped.")
            return
    
        
        ranges = []
        num_classes = 15
        step = (max_value - min_value) / num_classes
    
        for i in range(num_classes):
            lower = min_value + i * step
            upper = min_value + (i + 1) * step
            symbol = QgsSymbol.defaultSymbol(cloned_layer.geometryType())
            
            # Assegna dimensione in base alla classe (tra 1.5 e 4)
            size = 1.5 + ((i / (num_classes - 1)) * 2.5)
            symbol.setSize(size)
            
            # Assegna colore in base alla classe
            ratio = i / (num_classes - 1)  # normalizzazione indice di classe
            
            symbol.setColor(color_ramp.color(ratio))
          

    
            # Crea range label e aggiungilo alla lista
            range_label = f"{lower:.2f} - {upper:.2f}"
            renderer_range = QgsRendererRange(lower, upper, symbol, range_label)
            ranges.append(renderer_range)
    
        # inizializza il renderer
        renderer = QgsGraduatedSymbolRenderer(field_name, ranges)

        
        renderer.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
        renderer.setSourceColorRamp(color_ramp)
        
       
    
    
    
        # Applica il renderer
        cloned_layer.setRenderer(renderer)
        
  
        
        cloned_layer.triggerRepaint()
    
        # Salva il layer con un dialog
        default_name = f"{cloned_layer.name()}.shp"
        save_path, _ = QFileDialog.getSaveFileName(None, "Save Layer", default_name, "Shapefile (*.shp)")
    
        if save_path:
            QgsVectorFileWriter.writeAsVectorFormat(cloned_layer, save_path, "UTF-8", cloned_layer.crs(), "ESRI Shapefile")
            print(f"Layer saved successfully: {save_path}")
        else:
            print("Save operation cancelled.")
    
    
    
    
        
                
        
        
