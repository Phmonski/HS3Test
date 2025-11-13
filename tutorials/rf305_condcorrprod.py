from pathlib import Path

import ROOT
 
# Create conditional pdf gx(x|y)
# -----------------------------------------------------------
 
# Create observables
x = ROOT.RooRealVar("x", "x", -5, 5)
y = ROOT.RooRealVar("y", "y", -5, 5)
 
# Create function f(y) = a0 + a1*y
a0 = ROOT.RooRealVar("a0", "a0", -0.5, -5, 5)
a1 = ROOT.RooRealVar("a1", "a1", -0.5, -1, 1)
fy = ROOT.RooPolyVar("fy", "fy", y, [a0, a1])
 
# Create gaussx(x,f(y),sx)
sigmax = ROOT.RooRealVar("sigma", "width of gaussian", 0.5)
gaussx = ROOT.RooGaussian("gaussx", "Gaussian in x with shifting mean in y", x, fy, sigmax)
 
# Create pdf gy(y)
# -----------------------------------------------------------
 
# Create gaussy(y,0,5)
gaussy = ROOT.RooGaussian("gaussy", "Gaussian in y", y, 0.0, 3.0)
 
# Create product gx(x|y)*gy(y)
# -------------------------------------------------------
 
# Create gaussx(x,sx|y) * gaussy(y)
model = ROOT.RooProdPdf("model", "gaussx(x|y)*gaussy(y)", {gaussy}, Conditional=({gaussx}, {x}))
 
# Sample and fit product pdf
# ---------------------------------------------------------------
 
# Generate 1000 events in x and y from model
data = model.generate({x, y}, 10000)

ws = ROOT.RooWorkspace()

ws.Import(model, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(data)

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
export_file = export_dir / "rf305_condcorrprod.json"
tool.exportJSON(str(export_file))
