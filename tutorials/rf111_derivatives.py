from pathlib import Path

import ROOT
 
# Set up model
# ---------------------
 
# Declare variables x,mean, with associated name, title, value and allowed
# range
x = ROOT.RooRealVar("x", "x", -10, 10)
mean = ROOT.RooRealVar("mean", "mean of gaussian", 1, -10, 10)
sigma = ROOT.RooRealVar("sigma", "width of gaussian", 1, 0.1, 10)
 
# Build gaussian pdf in terms of x, and sigma
gauss = ROOT.RooGaussian("gauss", "gaussian PDF", x, mean, sigma)
 
# Create derivatives w.r.t. x
# ----------------------------------------------------------------------
 
# Derivative of normalized gauss(x) w.r.t. observable x
dgdx = gauss.derivative(x, 1)
 
# Second and third derivative of normalized gauss(x) w.r.t. observable x
d2gdx2 = gauss.derivative(x, 2)
d3gdx3 = gauss.derivative(x, 3)
 
# Create derivatives w.r.t. sigma
# ------------------------------------------------------------------------------
 
# Derivative of normalized gauss(x) w.r.t. parameter sigma
dgds = gauss.derivative(sigma, 1)
 
# Second and third derivative of normalized gauss(x) w.r.t. parameter sigma
d2gds2 = gauss.derivative(sigma, 2)
d3gds3 = gauss.derivative(sigma, 3)

ws = ROOT.RooWorkspace()
ws.Import(gauss, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(d3gdx3, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(d2gdx2, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(dgdx, ROOT.RooFit.RecycleConflictNodes(True))

ws.Import(dgds, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(d2gds2, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(d3gds3, ROOT.RooFit.RecycleConflictNodes(True))

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
export_file = export_dir / "rf111_derivatives.json"
tool.exportJSON(str(export_file))
