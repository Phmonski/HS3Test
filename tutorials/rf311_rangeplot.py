from pathlib import Path

import ROOT
 
# Create 3D pdf and data
# -------------------------------------------
 
# Create observables
x = ROOT.RooRealVar("x", "x", -5, 5)
y = ROOT.RooRealVar("y", "y", -5, 5)
z = ROOT.RooRealVar("z", "z", -5, 5)
 
# Create signal pdf gauss(x)*gauss(y)*gauss(z)
gx = ROOT.RooGaussian("gx", "gx", x, 0.0, 1.0)
gy = ROOT.RooGaussian("gy", "gy", y, 0.0, 1.0)
gz = ROOT.RooGaussian("gz", "gz", z, 0.0, 1.0)
sig = ROOT.RooProdPdf("sig", "sig", [gx, gy, gz])
 
# Create background pdf poly(x)*poly(y)*poly(z)
px = ROOT.RooPolynomial("px", "px", x, [-0.1, 0.004])
py = ROOT.RooPolynomial("py", "py", y, [0.1, -0.004])
pz = ROOT.RooPolynomial("pz", "pz", z)
bkg = ROOT.RooProdPdf("bkg", "bkg", [px, py, pz])
 
# Create composite pdf sig+bkg
fsig = ROOT.RooRealVar("fsig", "signal fraction", 0.1, 0.0, 1.0)
model = ROOT.RooAddPdf("model", "model", [sig, bkg], [fsig])
 
data = model.generate({x, y, z}, 20000)
 
# Define signal region in y and z observables
y.setRange("sigRegion", -1, 1)
z.setRange("sigRegion", -1, 1)

ws = ROOT.RooWorkspace("ws")
ws.Import(model, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(data)

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
export_file = export_dir / "rf311_rangeplot.json"
tool.exportJSON(str(export_file))
