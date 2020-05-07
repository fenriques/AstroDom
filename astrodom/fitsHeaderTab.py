
import sys
import os
import ntpath
import logging

from pathlib import Path
from astropy.io import fits
from PyQt5 import QtWidgets
from PyQt5 import QtGui, QtCore


'''
FITS Header parser 
'''
class FitsHeaderTab():
    logger = logging.getLogger(__name__)

    def __init__(self, mainW, app):
        super().__init__()
        self.mainW = mainW
        self.app = app

    def readHeaders(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.mainW,
            'Select a FITS file to open…',
            QtCore.QDir.homePath(),
            'FITS Files (*.fits *.fit *.FIT *.FITS) ;; All Files (*)'
        )
        if filename:
            with open(filename) as fh:
                self.mainW.ui.plainTextEditFitsHeader.clear()
                self.mainW.ui.plainTextEditMsg.clear()
                self.mainW.ui.lineEditFitsHeader.setText(filename)
                self.logger.info(f"Opened {filename}")
               
                hdu = fits.open(filename)
                hdu.verify('silentfix')
                hdr = hdu[0].header
                for i,key in enumerate(hdr):
                    sval = str(hdr[key])[0:70]
                    if key  in self.app.filterDictToList('fitsHeader'):
                        color = "green"
                        if not hdr[key]:
                            sval= "<font color=\"#48f\">Empty value: set a default value in Settings before importing</font>"
                    else:
                        color = "#ccc"
                    s = "<pre><font color="+color+">"+str(key)+"\t"+sval+"</font></pre>"
                    self.mainW.ui.plainTextEditFitsHeader.appendHtml(s)
                
                l = ('FILE', 'HASH', 'ALT', 'AZ')
                requestedH = set(self.app.filterDictToList('fitsHeader')) - set(l)
                missingH = set(requestedH) - set(hdr)- set(self.app.filterDictToList('fitsDefault', 'fitsHeader'))
                matchedH =  set(requestedH).intersection(set(hdr))
                defaultedH = set(self.app.filterDictToList('fitsDefault', 'fitsHeader')) -set(hdr)
                msg=""
                if len(matchedH)> 0:
                    msg +="<font color=\"green\">Matched keywords: "+','.join(matchedH)+ "</font><br>"
                if len(defaultedH)> 0:
                    msg +="<font color=\"#48f\">Keywords with a default: "+','.join(defaultedH)+ "</font><br>"
                if len(missingH)> 0:
                    msg +="<font color=\"red\">Missing keywords: "+','.join(missingH)+ "</font>"
                else:
                    msg +="This file can be imported in Astrodom."
                    
                self.mainW.ui.plainTextEditMsg.appendHtml(msg)
                    
