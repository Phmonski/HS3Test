from pathlib import Path

import ROOT
 
 
# Create 3D pdf
# -------------------------
 
# Define observable (x,y,z)
x = ROOT.RooRealVar("x", "x", 0, 10)
y = ROOT.RooRealVar("y", "y", 0, 10)
z = ROOT.RooRealVar("z", "z", 0, 10)
 
# Define 3 dimensional pdf
z0 = ROOT.RooRealVar("z0", "z0", -0.1, 1)
px = ROOT.RooPolynomial("px", "px", x, [0.0])
py = ROOT.RooPolynomial("py", "py", y, [0.0])
pz = ROOT.RooPolynomial("pz", "pz", z, [z0])
pxyz = ROOT.RooProdPdf("pxyz", "pxyz", [px, py, pz])
 
# Defined non-rectangular region R in (x, y, z)
# -------------------------------------------------------------------------------------
 
#
# R = Z[0 - 0.1*Y^2] * Y[0.1*X - 0.9*X] * X[0 - 10]
#
 
# Construct range parameterized in "R" in y [ 0.1*x, 0.9*x ]
ylo = ROOT.RooFormulaVar("ylo", "0.1*x", [x])
yhi = ROOT.RooFormulaVar("yhi", "0.9*x", [x])
y.setRange("R", ylo, yhi)
 
# Construct parameterized ranged "R" in z [ 0, 0.1*y^2 ]
zlo = ROOT.RooFormulaVar("zlo", "0.0*y", [y])
zhi = ROOT.RooFormulaVar("zhi", "0.1*y*y", [y])
z.setRange("R", zlo, zhi)
 
# Calculate integral of normalized pdf in R
# ----------------------------------------------------------------------------------
 
# Create integral over normalized pdf model over x,y, in "R" region
intPdf = pxyz.createIntegral({x, y, z}, {x, y, z}, "R")

ws = ROOT.RooWorkspace("ws")
ws.Import(pxyz, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(intPdf, ROOT.RooFit.RecycleConflictNodes(True))

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
export_file = export_dir / "rf313_paramranges.json"
tool.exportJSON(str(export_file))
