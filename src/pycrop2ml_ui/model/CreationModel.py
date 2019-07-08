import ipywidgets as wg
import os
import re

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.cpackage.CreationRepository import mkdirModel
from pycrop2ml_ui.browser.PathFetcher import FileBrowser
from pycrop2ml_ui.menus.creation import createmenu
from pycrop2ml_ui.menus.edition import editmenu
from pycrop2ml_ui.menus.display import displaymenu



class displayMainMenu:


    def __init__(self):

        #buttons
        self.create = wg.Button(value=False,description='Model creation',disabled=False)
        self.edit = wg.Button(value=False,description='Model edition',disabled=False)
        self.display = wg.Button(value=False,description='Model display',disabled=False)
        self.about = wg.Button(value=False,description='About',disabled=False)

        #global displayer
        self.displayer = wg.VBox([self.create, self.edit, self.display, self.about])

        #children nodes
        self.createWg = createmenu.createMenu()
        self.editWg = editmenu.editMenu()
        self.displayWg = displaymenu.displayMenu()

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()
    

    #on_click event for create button
    def eventCreate(self, b):
        self.out.clear_output()
        self.out2.clear_output()
        with self.out: 
            self.createWg.displayMenu()
            

    #on_click event for edit button
    def eventEdit(self, b):
        self.out.clear_output()
        self.out2.clear_output()
        with self.out:
            self.editWg.displayMenu()


    #on_click event for display button
    def eventDisplay(self, b):
        self.out2.clear_output()
        with self.out2:
            print("display !")


    #on_click event for about button
    def eventAbout(self, b):
        self.out2.clear_output()
        with self.out2:
            print("""
This widget provides a way to create a Crop2ML model including any needed parameter.\n
You may use it for model edition and model display aswell.\n
Both ipywidgets and qgrid are required for running this tool, they are enabled with the JupyterLab extension crop2ml.\n""")


    #displays the main menu
    def displayMenu(self):

        display(self.out)
        with self.out:
            display(self.displayer)
        display(self.out2)

        self.create.on_click(self.eventCreate)
        self.edit.on_click(self.eventEdit)
        self.display.on_click(self.eventDisplay)
        self.about.on_click(self.eventAbout)
        



def main():

    output = displayMainMenu()
    output.displayMenu()

