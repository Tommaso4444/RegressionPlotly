from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QScrollArea, QListWidget, QListWidgetItem,
    QComboBox, QLabel, QGridLayout, QToolButton
)
from PyQt5.QtCore import Qt

class RegressionAnalysisTab(QWidget):

    def __init__(self, x_data, y_data,
                  x_field_selected_value,x_field_items_list,
    y_field_selected_value,y_field_items_list,selected_layer):
        super().__init__()
        self.x_data = x_data
        self.y_data = y_data
        self.selected_layer = selected_layer

        # Create dropdowns
        self.model_dropdown = QComboBox()
        self.x_single_field_dropdown = QComboBox()
        self.y_field_dropdown = QComboBox()
        
        self.model_dropdown.addItems(["Simple Linear Regression", "Multiple Linear Regression"])
        self.x_single_field_dropdown.addItems(x_field_items_list)
        self.y_field_dropdown.addItems(y_field_items_list)

        # Multi-selection list for X variables
        self.x_list_widget = QListWidget()
        self.x_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.x_list_widget.setFixedSize(200, 160)


        # Add "Select All" option
        select_all_item = QListWidgetItem("Select All")
        self.x_list_widget.addItem(select_all_item)
        
        # Add covariate options
        for x_var in x_field_items_list:
            self.x_list_widget.addItem(QListWidgetItem(x_var))

        # Connect selection logic
        self.x_list_widget.itemClicked.connect(self.handle_covariate_selection)

        # Clear selection button
        self.clear_covariates_button = QPushButton("Clear")
        self.clear_covariates_button.clicked.connect(self.clear_covariates_selection)

        # Start regression button
        self.start_regression_analysis_button = QPushButton("Start Regression Analysis")
        self.start_regression_analysis_button.clicked.connect(self.load_interactive_scatter_plot)

        # Layout setup
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        grid_layout = QGridLayout()
        
        self.inner_grid_layout_covariates = QGridLayout()
        self.inner_grid_layout_covariates.addWidget(self.x_list_widget, 0, 0)
        self.inner_grid_layout_covariates.addWidget(self.clear_covariates_button, 0, 1)

        grid_layout.addWidget(QLabel("Model Type:"), 0, 0)
        grid_layout.addWidget(self.model_dropdown, 0, 1)
        grid_layout.addWidget(QLabel("Var. X Field:"), 1, 0)
        grid_layout.addWidget(self.x_single_field_dropdown, 1, 1)
        grid_layout.addWidget(QLabel("Var. X Fields (Covariates):"), 2, 0)
        grid_layout.addLayout(self.inner_grid_layout_covariates, 2, 1)
        grid_layout.addWidget(QLabel("Var. Y Field:"), 3, 0)
        grid_layout.addWidget(self.y_field_dropdown, 3, 1)
        grid_layout.addWidget(self.start_regression_analysis_button, 4, 0)

        container_layout.addLayout(grid_layout)

        # Scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def handle_covariate_selection(self, item):
        """Handles selection of covariates, including 'Select All' logic."""
        if item.text() == "Select All":
            # Toggle all selections
            select_all = item.isSelected()
            for i in range(1, self.x_list_widget.count()):  # Skip "Select All" item
                self.x_list_widget.item(i).setSelected(select_all)

    def clear_covariates_selection(self):
        """Clears all selected covariates."""
        self.x_list_widget.clearSelection()

    def load_interactive_scatter_plot(self):
        """Placeholder for regression analysis logic."""
        selected_x_vars = [self.x_list_widget.item(i).text() for i in range(1, self.x_list_widget.count()) if self.x_list_widget.item(i).isSelected()]
        print(f"Selected Covariates: {selected_x_vars}")
