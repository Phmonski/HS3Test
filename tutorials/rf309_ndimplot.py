from pathlib import Path

import ROOT
 
# Create 2D model and dataset
# -----------------------------------------------------
 
# Create observables
x = ROOT.RooRealVar("x", "x", -5, 5)
y = ROOT.RooRealVar("y", "y", -5, 5)
 
# Create parameters
a0 = ROOT.RooRealVar("a0", "a0", -3.5, -5, 5)
a1 = ROOT.RooRealVar("a1", "a1", -1.5, -1, 1)
sigma = ROOT.RooRealVar("sigma", "width of gaussian", 1.5)
 
# Create interpreted function f(y) = a0 - a1*sqrt(10*abs(y))
fy = ROOT.RooFormulaVar("fy", "a0-a1*sqrt(10*abs(y))", [y, a0, a1])
 
# Create gauss(x,f(y),s)
model = ROOT.RooGaussian("model", "Gaussian with shifting mean", x, fy, sigma)
 
# Sample dataset from gauss(x,y)
data = model.generate({x, y}, 10000)
 
# Create 3D model and dataset
# -----------------------------------------------------
 
# Create observables
z = ROOT.RooRealVar("z", "z", -5, 5)
 
gz = ROOT.RooGaussian("gz", "gz", z, 0.0, 2.0)
model3 = ROOT.RooProdPdf("model3", "model3", [model, gz])
 
data3 = model3.generate({x, y, z}, 10000)

ws = ROOT.RooWorkspace()

ws.Import(model, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(model3, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(data, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(data3, ROOT.RooFit.RecycleConflictNodes(True))

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
export_file = export_dir / "rf309_ndimplot.json"
tool.exportJSON(str(export_file))
