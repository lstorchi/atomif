""" psize class

    Get dimensions and other information from a PQR file.

    Originally written by Dave Sept
    Additional APBS-specific features added by Nathan Baker
    Ported to Python/Psize class by Todd Dolinsky and subsequently
    hacked by Nathan Baker

        ----------------------------
   
    PDB2PQR -- An automated pipeline for the setup, execution, and analysis of
    Poisson-Boltzmann electrostatics calculations

    Copyright (c) 2002-2011, Jens Erik Nielsen, University College Dublin; 
    Nathan A. Baker, Battelle Memorial Institute, Developed at the Pacific 
    Northwest National Laboratory, operated by Battelle Memorial Institute, 
    Pacific Northwest Division for the U.S. Department Energy.; 
    Paul Czodrowski & Gerhard Klebe, University of Marburg.

	All rights reserved.

	Redistribution and use in source and binary forms, with or without modification, 
	are permitted provided that the following conditions are met:

		* Redistributions of source code must retain the above copyright notice, 
		  this list of conditions and the following disclaimer.
		* Redistributions in binary form must reproduce the above copyright notice, 
		  this list of conditions and the following disclaimer in the documentation 
		  and/or other materials provided with the distribution.
        * Neither the names of University College Dublin, Battelle Memorial Institute,
          Pacific Northwest National Laboratory, US Department of Energy, or University
          of Marburg nor the names of its contributors may be used to endorse or promote
          products derived from this software without specific prior written permission.

	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
	ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
	WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
	IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
	INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
	BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
	DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
	LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
	OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED 
	OF THE POSSIBILITY OF SUCH DAMAGE.

    ----------------------------
"""

__date__ = "4 June 2008"
__author__ = "Dave Sept, Nathan Baker, Todd Dolinsky, Yong Huang"
"L. Storchi, Quick Port to python 3"

from posixpath import normpath
import string, sys, getopt
from sys import stdout, stderr
from math import log

class Psize:
    """Master class for parsing input files and suggesting settings"""
    def __init__(self):
        self.constants = {"cfac": 1.7, "fadd":20, "space": 0.50, "gmemfac": 200, "gmemceil": 400, "ofrac":0.1, "redfac": 0.25 }
        self.minlen = [None, None, None]
        self.maxlen = [None, None, None]
        self.q = 0.0
        self.gotatom = 0
        self.gothet = 0
        self.olen = [0.0, 0.0, 0.0]
        self.cen = [0.0, 0.0, 0.0]
        self.clen = [0.0, 0.0, 0.0]
        self.flen = [0.0, 0.0, 0.0]
        self.n = [0, 0, 0]
        self.np = [0.0, 0.0, 0.0]
        self.nsmall = [0,0,0]
        self.nfocus = 0

    def parseString(self, structure):
        """ Parse the input structure as a string in PDB or PQR format """
        lines = string.split(structure, "\n")
        self.parseLines(lines)

    def parseInput(self, filename):
        """ Parse input structure file in PDB or PQR format """
        with open(filename, 'rU') as f:
            self.parseLines(f.readlines())

    def parseLines(self, lines):
        """ Parse the lines """
        for line in lines:
            if line.find("ATOM") == 0:
                subline = line[30:].replace("-", " -")
                words = subline.split()
                if len(words) < 5:    
                    continue
                self.gotatom += 1
                self.q = self.q + float(words[3])
                rad = float(words[4])
                center = []
                for word in words[0:3]:
                    center.append(float(word))
                for i in range(3):
                    if self.minlen[i] == None or center[i]-rad < self.minlen[i]:
                        self.minlen[i] = center[i]-rad
                    if self.maxlen[i] == None or center[i]+rad > self.maxlen[i]:
                        self.maxlen[i] = center[i]+rad
            elif line.find("HETATM") == 0:
                self.gothet = self.gothet + 1
                # Special handling for no ATOM entries in the pqr file, only HETATM entries
                if self.gotatom == 0:
                    subline = string.replace(line[30:], "-", " -")
                    words = string.split(subline)
                    if len(words) < 5:    
                        continue
                    self.q = self.q + float(words[3])
                    rad = float(words[4])
                    center = []
                    for word in words[0:3]:
                        center.append(float(word))
                    for i in range(3):
                        if self.minlen[i] == None or center[i]-rad < self.minlen[i]:
                            self.minlen[i] = center[i]-rad
                        if self.maxlen[i] == None or center[i]+rad > self.maxlen[i]:
                            self.maxlen[i] = center[i]+rad
    
    def setConstant(self, name, value):
        """ Set a constant to a value; returns 0 if constant not found """
        try:
            self.constants[name] = value
            return 1
        except KeyError:
            return 0

    def getConstant(self, name):
        """ Get a constant value; raises KeyError if constant not found """
        return self.constants[name]

    def setLength(self, maxlen, minlen):
        """ Compute molecule dimensions """
        for i in range(3):
            self.olen[i] = maxlen[i] - minlen[i]
            if self.olen[i] < 0.1:
                self.olen[i] = 0.1
        return self.olen


    def setCoarseGridDims(self, olen):
        """ Compute coarse mesh dimensions """
        for i in range(3):
            self.clen[i] = self.constants["cfac"] * olen[i]
        return self.clen

    def setFineGridDims(self, olen, clen):
        """ Compute fine mesh dimensions """
        for i in range(3):
            self.flen[i] = olen[i] + self.constants["fadd"]
            if self.flen[i] > clen[i]:
                #str = "WARNING: Fine length (%.2f) cannot be larger than coarse length (%.2f)\n" % (self.flen[i], clen[i])
                #str = str + "         Setting fine grid length equal to coarse grid length\n"
                #stdout.write(str)
                self.flen[i] = clen[i]
        return self.flen

    def setCenter(self, maxlen, minlen):
        """ Compute molecule center """
        for i in range(3):
            self.cen[i] = (maxlen[i] + minlen[i]) / 2
        return self.cen


    def setFineGridPoints(self, flen):
        """ Compute mesh grid points, assuming 4 levels in MG hierarchy """
        tn = [0,0,0]
        for i in range(3):
            tn[i] = int(flen[i]/self.constants["space"] + 0.5)
            self.n[i] = 32*(int((tn[i] - 1) / 32.0 + 0.5)) + 1
            if self.n[i] < 33:
                self.n[i] = 33
        return self.n

    def setSmallest(self, n):
        """ Compute parallel division in case memory requirement above ceiling
        Find the smallest dimension and see if the number of grid points in
        that dimension will fit below the memory ceiling
        Reduce nsmall until an nsmall^3 domain will fit into memory """
        nsmall = []
        for i in range(3):
            nsmall.append(n[i])
        while 1:
            nsmem = 200.0 * nsmall[0] * nsmall[1] * nsmall[2] / 1024 / 1024
            if nsmem < self.constants["gmemceil"]: break
            else:
                i = nsmall.index(max(nsmall))
                nsmall[i] = 32 * ((nsmall[i] - 1)/32 - 1) + 1
                if nsmall[i] <= 0:
                    stdout.write("You picked a memory ceiling that is too small\n")
                    sys.exit(0)        

        self.nsmall = nsmall
        return nsmall

    def setProcGrid(self, n, nsmall):
        """ Calculate the number of processors required to span each 
        dimension """

        zofac = 1 + 2 * self.constants["ofrac"]
        for i in range(3):
            self.np[i] = n[i]/float(nsmall[i])
            if self.np[i] > 1: self.np[i] = int(zofac*n[1]/nsmall[i] + 1.0)
        return self.np
                                                
    def setFocus(self, flen, np, clen):
        """ Calculate the number of levels of focusing required for each
        processor subdomain """

        nfoc = [0,0,0]
        for i in range(3):
            nfoc[i] = int(log((flen[i]/np[i])/clen[i])/log(self.constants["redfac"]) + 1.0)
        nfocus = nfoc[0]
        if nfoc[1] > nfocus: nfocus = nfoc[1]
        if nfoc[2] > nfocus: nfocus = nfoc[2]
        if nfocus > 0: nfocus = nfocus + 1
        self.nfocus = nfocus

    def setAll(self):
        """ Set up all of the things calculated individually above """
        maxlen = self.getMax()
        minlen = self.getMin()
        self.setLength(maxlen, minlen)
        olen = self.getLength()
        
        self.setCoarseGridDims(olen)
        clen = self.getCoarseGridDims()        
        
        self.setFineGridDims(olen, clen)
        flen = self.getFineGridDims()
        
        self.setCenter(maxlen, minlen)
        cen = self.getCenter()
        
        self.setFineGridPoints(flen)
        n = self.getFineGridPoints()
        
        self.setSmallest(n)
        nsmall = self.getSmallest()
        
        self.setProcGrid(n, nsmall)
        np = self.getProcGrid()
        
        self.setFocus(flen, np, clen)
        nfocus = self.getFocus()
        
    def getMax(self): return self.maxlen
    def getMin(self): return self.minlen
    def getCharge(self): return self.q
    def getLength(self): return self.olen
    def getCoarseGridDims(self): return self.clen
    def getFineGridDims(self): return self.flen
    def getCenter(self): return self.cen
    def getFineGridPoints(self): return self.n
    def getSmallest(self): return self.nsmall
    def getProcGrid(self): return self.np
    def getFocus(self): return self.nfocus

    def runPsize(self, filename):
        """ Parse input PQR file and set parameters """
        self.parseInput(filename)
        self.setAll()
    
    def printResults(self):
        """ Return a string with the formatted results """

        str = "\n"
        
        if self.gotatom > 0:

            maxlen = self.getMax()
            minlen = self.getMin()
            q = self.getCharge()
            olen = self.getLength()
            clen = self.getCoarseGridDims()        
            flen = self.getFineGridDims()
            cen = self.getCenter()
            n = self.getFineGridPoints()
            nsmall = self.getSmallest()
            np = self.getProcGrid()
            nfocus = self.getFocus()

            # Compute memory requirements

            nsmem = 200.0 * nsmall[0] * nsmall[1] * nsmall[2] / 1024 / 1024
            gmem = 200.0 * n[0] * n[1] * n[2] / 1024 / 1024
            
            # Print the calculated entries
            str = str + "################# MOLECULE INFO ####################\n"
            str = str + "Number of ATOM entries = %i\n" % self.gotatom
            str = str + "Number of HETATM entries (ignored) = %i\n" % self.gothet
            str = str + "Total charge = %.3f e\n" % q
            str = str + "Dimensions = %.3f x %.3f x %.3f A\n" % (olen[0], olen[1], olen[2])
            str = str + "Center = %.3f x %.3f x %.3f A\n" % (cen[0], cen[1], cen[2])
            str = str + "Lower corner = %.3f x %.3f x %.3f A\n" % (minlen[0], minlen[1], minlen[2])
            str = str + "Upper corner = %.3f x %.3f x %.3f A\n" % (maxlen[0], maxlen[1], maxlen[2])

            str = str + "\n"
            str = str + "############## GENERAL CALCULATION INFO #############\n"
            str = str + "Coarse grid dims = %.3f x %.3f x %.3f A\n" % (clen[0], clen[1], clen[2])
            str = str + "Fine grid dims = %.3f x %.3f x %.3f A\n" % (flen[0], flen[1], flen[2])
            str = str + "Num. fine grid pts. = %i x %i x %i\n" % (n[0], n[1], n[2])

            if gmem > self.constants["gmemceil"]:
                str = str + "Parallel solve required (%.3f MB > %.3f MB)\n" % (gmem, self.constants["gmemceil"])
                str = str + "Total processors required = %i\n" % (np[0]*np[1]*np[2])
                str = str + "Proc. grid = %i x %i x %i\n" % (np[0], np[1], np[2])
                str = str + "Grid pts. on each proc. = %i x %i x %i\n" % (nsmall[0], nsmall[1], nsmall[2])
                xglob = np[0]*round(nsmall[0]/(1 + 2*self.constants["ofrac"]) - .001)
                yglob = np[1]*round(nsmall[1]/(1 + 2*self.constants["ofrac"]) - .001)
                zglob = np[2]*round(nsmall[2]/(1 + 2*self.constants["ofrac"]) - .001)
                if np[0] == 1: xglob = nsmall[0]
                if np[1] == 1: yglob = nsmall[1]
                if np[2] == 1: zglob = nsmall[2]
                str = str + "Fine mesh spacing = %g x %g x %g A\n" % (flen[0]/(xglob-1), flen[1]/(yglob-1), flen[2]/(zglob-1))
                str = str + "Estimated mem. required for parallel solve = %.3f MB/proc.\n" % nsmem
                ntot = nsmall[0]*nsmall[1]*nsmall[2]

            else:
                str = str + "Fine mesh spacing = %g x %g x %g A\n" % (flen[0]/(n[0]-1), flen[1]/(n[1]-1), flen[2]/(n[2]-1))
                str = str + "Estimated mem. required for sequential solve = %.3f MB\n" % gmem
                ntot = n[0]*n[1]*n[2]

            str = str + "Number of focusing operations = %i\n" % nfocus

            str = str + "\n"
            str = str + "################# ESTIMATED REQUIREMENTS ####################\n"
            str = str + "Memory per processor                   = %.3f MB\n" % (200.0*ntot/1024/1024)
            str = str + "Grid storage requirements (ASCII)      = %.3f MB\n" % (8.0*12*np[0]*np[1]*np[2]*ntot/1024/1024)
            str = str + "\n"

        else:
            str = str + "No ATOM entires in file!\n\n"

        return str