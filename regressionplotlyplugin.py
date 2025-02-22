# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MyPlugin
                                 A QGIS plugin
 Plugin demo con due schermate
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2025-01-26
        git sha              : $Format:%H$
        copyright            : (C) 2025 by Tommaso Barbiero
        email                : tommasobarbiero@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from PyQt5.QtWidgets import QAction, QToolButton, QMenu, QDockWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtWidgets import QDialog, QApplication

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog

import os.path
from .myscatterplot import ScatterPlotDock


class RegressionPlotlyPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.iface = iface
        self.window1 = None
        self.window2 = None
        self.actions = []
        self.first_start = True  
        
        self.plugin_dir = os.path.dirname(__file__)
        self.icon_path = os.path.join(self.plugin_dir, "icon.png")

    
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        
        return QCoreApplication.translate('MyPlugin', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
       
        icon = QIcon(self.icon_path)
        
        
        self.action = QAction(icon, "RegressionPlotly", self.iface.mainWindow())

        # Connetti self.action al metodo per aprire lo scatter_dock
        self.action.triggered.connect(self.show_scatter_dock)

        # Aggiungi il bottone del plugin alla toolbar
        self.iface.addToolBarIcon(self.action)

        # Aggiungi il plugin al menu
        self.iface.addPluginToMenu("RegressionPlotly", self.action)

        # Crea lo ScatterPlotDock
        self.scatter_dock = ScatterPlotDock(self.iface)
        self.scatter_dock.setObjectName("MyPluginDock")

        # Aggiungi il ScatterPlotDock widget a QGIS
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.scatter_dock)

    def unload(self):
        
        self.iface.removePluginMenu("RegressionPlotly", self.action)
        self.iface.removeToolBarIcon(self.action)
        if self.scatter_dock:
            self.iface.removeDockWidget(self.scatter_dock)
            self.scatter_dock = None
        
    def show_scatter_dock(self):
        self.scatter_dock.setVisible(not self.scatter_dock.isVisible())

    def run(self):
        
        if self.first_start == True:
            self.first_start = False
            

        
        self.dlg.show()
        
        result = self.dlg.exec_()
       
        if result:
            
            pass




        


