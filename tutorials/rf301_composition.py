from pathlib import Path

import ROOT
 
# Setup composed model gauss(x, m(y), s)
# -----------------------------------------------------------------------
 
# Create observables
x = ROOT.RooRealVar("x", "x", -5, 5)
y = ROOT.RooRealVar("y", "y", -5, 5)
 
# Create function f(y) = a0 + a1*y
a0 = ROOT.RooRealVar("a0", "a0", -0.5, -5, 5)
a1 = ROOT.RooRealVar("a1", "a1", -0.5, -1, 1)
fy = ROOT.RooPolyVar("fy", "fy", y, [a0, a1])

print("LOOK HERE: ", fy.x().GetName())
print(f)
# Creat gauss(x,f(y),s)
sigma = ROOT.RooRealVar("sigma", "width of gaussian", 0.5)
model = ROOT.RooGaussian("model", "Gaussian with shifting mean", x, fy, sigma)
 
# Sample data from x and y
# ---------------------------------------------------------------------------------
 
# Generate 10000 events in x and y from model
data = model.generate({x, y}, 10000)
 
ws = ROOT.RooWorkspace("ws")
ws.Import(model, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(data)

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
export_file = export_dir / "rf301_composition.json"
tool.exportJSON(str(export_file))
ws.writeToFile("rootFiles/rf301_composition.root")