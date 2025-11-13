from pathlib import Path

import ROOT
 
# Set up model
# ---------------------
 
# Create observables x,y
x = ROOT.RooRealVar("x", "x", -10, 10)
y = ROOT.RooRealVar("y", "y", -10, 10)
 
# Create pdf gaussx(x,-2,3), gaussy(y,2,2)
gx = ROOT.RooGaussian("gx", "gx", x, -2.0, 3.0)
gy = ROOT.RooGaussian("gy", "gy", y, +2.0, 2.0)
 
# gxy = gx(x)*gy(y)
gxy = ROOT.RooProdPdf("gxy", "gxy", [gx, gy])
 
# Retrieve raw & normalized values of RooFit pdfs
# --------------------------------------------------------------------------------------------------
 
# Return 'raw' unnormalized value of gx

# Return value of gxy normalized over x _and_ y in range [-10,10]
nset_xy = ROOT.RooArgSet(x, y)
 
# Create object representing integral over gx
# which is used to calculate  gx_Norm[x,y] == gx / gx_Int[x,y]
x_and_y = {x, y}
igxy = gxy.createIntegral(x_and_y)
 
# NB: it is also possible to do the following
 
# Return value of gxy normalized over x in range [-10,10] (i.e. treating y
# as parameter)
nset_x = ROOT.RooArgSet(x)
 
# Return value of gxy normalized over y in range [-10,10] (i.e. treating x
# as parameter)
nset_y = ROOT.RooArgSet(y)
 
# Integrate normalized pdf over subrange
# ----------------------------------------------------------------------------
 
# Define a range named "signal" in x from -5,5
x.setRange("signal", -5, 5)
y.setRange("signal", -3, 3)
 
# Create an integral of gxy_Norm[x,y] over x and y in range "signal"
# ROOT.This is the fraction of of pdf gxy_Norm[x,y] which is in the
# range named "signal"
 
igxy_sig = gxy.createIntegral(x_and_y, NormSet=x_and_y, Range="signal")
 
# Construct cumulative distribution function from pdf
# -----------------------------------------------------------------------------------------------------
 
# Create the cumulative distribution function of gx
# i.e. calculate Int[-10,x] gx(x') dx'
gxy_cdf = gxy.createCdf({x, y})

ws = ROOT.RooWorkspace()
ws.Import(gxy, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(igxy, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(igxy_sig, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(gxy_cdf, ROOT.RooFit.RecycleConflictNodes(True))

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
export_file = export_dir / "rf308_normintegration2d.json"
tool.exportJSON(str(export_file))
