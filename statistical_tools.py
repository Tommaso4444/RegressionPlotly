# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 22:02:42 2025

@author: tomma
"""

import sys
import numpy as np
import statsmodels.api as sm
# import plotly.graph_objects as go
# from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QGraphicsView, QGraphicsScene
# from PyQt5.QtWebKitWidgets import QWebPage, QGraphicsWebView


class StatisticalTools():

    def get_simple_regression_data(x_data, y_data,x_field,y_field):
            # Sample scatter plot data
            x_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            y_data = np.array([10, 15, 7, 12, 5, 14, 18, 19, 22, 25])
    
            # Perform linear regression using statsmodels
            x_with_const = sm.add_constant(x_data)  # Add intercept (constant term)
            model = sm.OLS(y_data, x_with_const).fit()  # Fit Ordinary Least Squares model
            y_pred = model.predict(x_with_const) 
            print(model)
            return model