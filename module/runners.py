from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtWidgets

import os
import mifs
import carbo
import fields

TYPEOFRUNCOULOMB = 1
TYPEOFRUNAPBS = 2

class run_thread_mifinteraction(QThread):
    """
    Runs a counter thread.
    """
    count_changed = pyqtSignal(int)

    __runmif_done__ = False

    def mif_is_done (self):

        return self.__runmif_done__ 

    def get_results (self):
        return self.__values1__, self.__values2__

    def configure (self, \
        firstmolsset, firstmol2file, firstweightsset, \
        secondmolsset, secondmol2file, secondweightsset, \
        stepval, deltaval, probe, minimaselection, \
        workdir, progress, savekont, gridbin = "", fixpdbin = "", \
        apbsbin = "", obabelbin = ""): 

        self.__savekont__ = savekont

        self.__gridbin__ = gridbin
        self.__fixpdbin__ = fixpdbin
        self.__apbsbin__ = apbsbin
        self.__obabelbin__ = obabelbin

        self.__probe__ = probe

        self.__firstmolsset__ = firstmolsset
        self.__firstmol2file__ = firstmol2file
        self.__firstweightsset__ = firstweightsset

        self.__secondmolsset__ = secondmolsset
        self.__secondmol2file__ = secondmol2file
        self.__secondweightsset__ = secondweightsset

        self.__stepval__ = float(stepval)
        self.__deltaval__ = float(deltaval)
        self.__workdir__ = workdir

        self.__progress__ = progress

        self.__minimaselection__ = float(minimaselection)

        self.__values1__ = None
        self.__values2__ = None

    def run (self):

        verbose = False

        self.count_changed.emit(0)

        self.__progress__.set_label("Running first set of molecules")

        energy1, xmin1, ymin1, zmin1 = mifs.compute_grid_mean_field (self.__firstmolsset__ , \
          self.__firstweightsset__, self.__firstmol2file__, self.__stepval__ , \
          self.__deltaval__, self.__probe__, self.__fixpdbin__ , self.__gridbin__ , \
          self.__obabelbin__ , self.__workdir__,  self.count_changed, \
          self.__progress__ , 0, 45, verbose, self.__savekont__ )

        # TODO

        self.count_changed.emit(100)

        self.__runmif_done__ = True

class run_thread_mif(QThread):
    """
    Runs a counter thread.
    """
    count_changed = pyqtSignal(int)

    __runmif_done__ = False

    def mif_is_done (self):

        return self.__runmif_done__ 

    def get_results (self):
        return self.__values1__, self.__values2__

    def configure (self, \
        firstmolsset, firstmol2file, firstweightsset, \
        secondmolsset, secondmol2file, secondweightsset, \
        stepval, deltaval, axis, probe, minimaselection, \
        workdir, progress, savekont, gridbin = "", fixpdbin = "", \
        apbsbin = "", obabelbin = ""): 

        self.__savekont__ = savekont

        self.__gridbin__ = gridbin
        self.__fixpdbin__ = fixpdbin
        self.__apbsbin__ = apbsbin
        self.__obabelbin__ = obabelbin

        self.__axis__ = axis
        self.__probe__ = probe

        self.__firstmolsset__ = firstmolsset
        self.__firstmol2file__ = firstmol2file
        self.__firstweightsset__ = firstweightsset

        self.__secondmolsset__ = secondmolsset
        self.__secondmol2file__ = secondmol2file
        self.__secondweightsset__ = secondweightsset

        self.__stepval__ = float(stepval)
        self.__deltaval__ = float(deltaval)
        self.__workdir__ = workdir

        self.__progress__ = progress

        self.__minimaselection__ = float(minimaselection)

        self.__values1__ = None
        self.__values2__ = None

    def run (self):

        verbose = False

        self.count_changed.emit(0)

        self.__progress__.set_label("Running first set of molecules")

        energy1, xmin1, ymin1, zmin1 = mifs.compute_grid_mean_field (self.__firstmolsset__ , \
          self.__firstweightsset__, self.__firstmol2file__, self.__stepval__ , \
          self.__deltaval__, self.__probe__, self.__fixpdbin__ , self.__gridbin__ , \
          self.__obabelbin__ , self.__workdir__,  self.count_changed, \
          self.__progress__ , 0, 45, verbose, self.__savekont__ )

        if not self.__progress__.was_cancelled():
            self.__values1__ = mifs.get_points(energy1, self.__stepval__, xmin1, ymin1, zmin1, self.__axis__, \
                self.__minimaselection__, verbose)

        self.count_changed.emit(50)

        energy2, xmin2, ymin2, zmin2 = mifs.compute_grid_mean_field (self.__secondmolsset__ , \
          self.__secondweightsset__ , self.__secondmol2file__, self.__stepval__ , \
          self.__deltaval__, self.__probe__, self.__fixpdbin__ , self.__gridbin__ , \
          self.__obabelbin__ , self.__workdir__,  self.count_changed, \
          self.__progress__ , 50, 45, verbose, self.__savekont__ )

        if not self.__progress__.was_cancelled():
            self.__values2__ = mifs.get_points(energy2, self.__stepval__, xmin2, ymin2, zmin2, self.__axis__, \
                self.__minimaselection__, verbose)

        self.count_changed.emit(100)

        self.__runmif_done__ = True

class run_thread_ci(QThread):
    """
    Runs a counter thread.
    """
    count_changed = pyqtSignal(int)

    __carboidxs__ = None 
    __refpoints__ = None 
    __weights__ = None 
    __pweights__ = None
    __runcu_done__ = False
    __runapbs_done__ = False

    def cu_is_done (self):

        return self.__runcu_done__ 

    def apbs_is_done (self):

        return self.__runapbs_done__ 

    def get_carboidxs (self):

        if self.__runcu_done__  or self.__runapbs_done__:
            return self.__carboidxs__ , \
                self.__refpoints__ , \
                    self.__weights__ , \
                        self.__pweights__
        else:
            return None, None, None, None

    def configure (self, typeofrun, ddieletric, axis, \
        firstmolsset, firstmol2file, firstweightsset, \
        secondmolsset, secondmol2file, secondweightsset, \
        stepval, deltaval, exportdx, workdir, progress,
        gridbin = "", fixpdbin = "", apbsbin = "", obabelbin = ""): 

        self.__gridbin__ = gridbin
        self.__fixpdbin__ = fixpdbin
        self.__apbsbin__ = apbsbin
        self.__obabelbin__ = obabelbin

        self.__type_of_run__ = typeofrun

        self.__ddieletric__ = ddieletric
        self.__axis__ = axis

        self.__firstmolsset__ = firstmolsset
        self.__firstmol2file__ = firstmol2file
        self.__firstweightsset__ = firstweightsset

        self.__secondmolsset__ = secondmolsset
        self.__secondmol2file__ = secondmol2file
        self.__secondweightsset__ = secondweightsset

        self.__stepval__ = stepval
        self.__deltaval__ = deltaval
        self.__exportdx__ = exportdx
        self.__workdir__ = workdir

        self.__progress__ = progress

    def run (self):

        self.count_changed.emit(0)

        self.__progress__.set_label("Running first set of molecules")

        cfields1 = None
        allfields1 = None
        gmean1 = None 

        if self.__type_of_run__ == TYPEOFRUNCOULOMB:
            cfields1 = fields.get_cfields(self.__firstmolsset__, self.__stepval__, \
                self.__deltaval__ ,  1.0, False, self.__ddieletric__, \
                    self.count_changed, self.__progress__, 0, 45 )
           
            if (cfields1 != None):
                basename = os.path.splitext(self.__firstmol2file__)[0]
                basename  = basename.split("/")[-1]
           
                if self.__progress__.was_cancelled():
                    return 
           
                gmean1, allfields1 = fields.exporttodx (self.__workdir__ + "/" + basename, \
                         cfields1, self.__firstweightsset__ , self.__stepval__, self.__ddieletric__, \
                            self.__exportdx__, None)
           
            self.count_changed.emit(50)

        elif self.__type_of_run__ == TYPEOFRUNAPBS:
            gmean1, allfields1 = fields.get_apbsfields(self.__obabelbin__, self.__apbsbin__ , \
                self.__exportdx__ , self.__firstmol2file__ , self.__firstweightsset__, \
                    self.__stepval__, self.__deltaval__ , \
                    self.__workdir__ , False, self.count_changed, \
                        self.__progress__, 0, 45 )


        self.count_changed.emit(45)

        self.__progress__.set_label("Running second set of molecules")

        if (allfields1 != None):
           
            if (self.__progress__.was_cancelled()):
              return  

            allfields2 = None
            gmean2 = None 

            if self.__type_of_run__ == TYPEOFRUNCOULOMB:

                cfields2 = fields.get_cfields(self.__secondmolsset__, self.__stepval__, \
                    self.__deltaval__, 1.0, False, self.__ddieletric__, self.count_changed, \
                        self.__progress__, 50, 45 )
            
                if (cfields2 != None):
                    basename = os.path.splitext(self.__secondmol2file__)[0]
                    basename  = basename.split("/")[-1]
            
                    if self.__progress__.was_cancelled():
                        return 
            
                    gmean2, allfields2 = fields.exporttodx (self.__workdir__ + "/" + basename, \
                            cfields2, self.__secondweightsset__ , self.__stepval__, self.__ddieletric__, \
                                self.__exportdx__, \
                                    list(allfields1.values())[0][1]) # fit respect to the first one so we can compute carbo
                
                    self.count_changed.emit(100)
            elif self.__type_of_run__ == TYPEOFRUNAPBS:

                gmean2, allfields2 = fields.get_apbsfields(self.__obabelbin__, self.__apbsbin__ , \
                    self.__exportdx__ , self.__secondmol2file__ , self.__secondweightsset__, \
                        self.__stepval__, self.__deltaval__ , \
                        self.__workdir__ , False, self.count_changed, \
                            self.__progress__, 50, 45, list(allfields1.values())[0][1]) 

                self.count_changed.emit(100)

        if (allfields1 != None) and (allfields2 != None):
            # compute carbo
            self.__progress__.set_title("Compute Carbo index")

            self.__progress__.set_label("Computing Carbo index alog " +  \
                self.__axis__ + " axis")

            self.count_changed.emit(0)

            """
            for k in allfields1:
                print(k, allfields1[k][1].grid.shape)

            for k in allfields2:
                print(k, allfields2[k][1].grid.shape)
            """

            try:
                self.__carboidxs__, self.__refpoints__, self.__weights__, self.__pweights__ = \
                  carbo.returncarbodxs(allfields1, allfields2, False, self.__axis__, \
                      self.count_changed, self.__progress__)

                self.count_changed.emit(100)

                if self.__type_of_run__ == TYPEOFRUNCOULOMB:
                    self.__runcu_done__ = True
                elif self.__type_of_run__ == TYPEOFRUNAPBS:
                    self.__runapbs_done__ = True

                #print(self.__carboidxs__, self.__refpoints__, self.__weights__, self.__pweights__)

            except Exception as exp:
                self.__carboidxs__ = None 
                self.__refpoints__ = None 
                self.__weights__ = None 
                self.__pweights__ = None
                
                QtWidgets.QMessageBox.critical( self, \
                    "ERROR", exp) 