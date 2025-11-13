from pathlib import Path

import ROOT
 
# Create observables, parameters
# -----------------------------------------------------------
 
# Create observables
x = ROOT.RooRealVar("x", "x", -5, 5)
y = ROOT.RooRealVar("y", "y", -5, 5)
 
# Create parameters
a0 = ROOT.RooRealVar("a0", "a0", -1.5, -5, 5)
a1 = ROOT.RooRealVar("a1", "a1", -0.5, -1, 1)
sigma = ROOT.RooRealVar("sigma", "width of gaussian", 0.5)
 
# Using RooFormulaVar to tailor pdf
# -----------------------------------------------------------------------
 
# Create interpreted function f(y) = a0 - a1*sqrt(10*abs(y))
fy_1 = ROOT.RooFormulaVar("fy_1", "a0-a1*sqrt(10*abs(y))", [y, a0, a1])
 
# Create gauss(x,f(y),s)
model_1 = ROOT.RooGaussian("model_1", "Gaussian with shifting mean", x, fy_1, sigma)
 
# Using RooPolyVar to tailor pdf
# -----------------------------------------------------------------------
 
# Create polynomial function f(y) = a0 + a1*y
fy_2 = ROOT.RooPolyVar("fy_2", "fy_2", y, [a0, a1])
 
# Create gauss(x,f(y),s)
model_2 = ROOT.RooGaussian("model_2", "Gaussian with shifting mean", x, fy_2, sigma)
 
# Using RooAddition to tailor pdf
# -----------------------------------------------------------------------
 
# Create sum function f(y) = a0 + y
fy_3 = ROOT.RooAddition("fy_3", "a0+y", [a0, y])
 
# Create gauss(x,f(y),s)
model_3 = ROOT.RooGaussian("model_3", "Gaussian with shifting mean", x, fy_3, sigma)
 
# Using RooProduct to tailor pdf
# -----------------------------------------------------------------------
 
# Create product function f(y) = a1*y
fy_4 = ROOT.RooProduct("fy_4", "a1*y", [a1, y])
 
# Create gauss(x,f(y),s)
model_4 = ROOT.RooGaussian("model_4", "Gaussian with shifting mean", x, fy_4, sigma)
 
ws = ROOT.RooWorkspace("ws")

ws.Import(model_1, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(model_2, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(model_3, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(model_4, ROOT.RooFit.RecycleConflictNodes(True))

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
export_file = export_dir / "rf302_utilfuncs.json"
tool.exportJSON(str(export_file))
