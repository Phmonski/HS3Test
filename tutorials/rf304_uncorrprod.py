from pathlib import Path

import ROOT
 
 
# Create component pdfs in x and y
# ----------------------------------------------------------------
 
# Create two pdfs gaussx(x,meanx,sigmax) gaussy(y,meany,sigmay) and its
# variables
x = ROOT.RooRealVar("x", "x", -5, 5)
y = ROOT.RooRealVar("y", "y", -5, 5)
 
meanx = ROOT.RooRealVar("mean1", "mean of gaussian x", 2)
meany = ROOT.RooRealVar("mean2", "mean of gaussian y", -2)
sigmax = ROOT.RooRealVar("sigmax", "width of gaussian x", 1)
sigmay = ROOT.RooRealVar("sigmay", "width of gaussian y", 5)
 
gaussx = ROOT.RooGaussian("gaussx", "gaussian PDF", x, meanx, sigmax)
gaussy = ROOT.RooGaussian("gaussy", "gaussian PDF", y, meany, sigmay)
 
# Construct uncorrelated product pdf
# -------------------------------------------------------------------
 
# Multiply gaussx and gaussy into a two-dimensional pdf gaussxy
gaussxy = ROOT.RooProdPdf("gaussxy", "gaussx*gaussy", [gaussx, gaussy])
 
# Sample pdf
# ---------------------------------------------------------------------------
 
# Generate 10000 events in x and y from gaussxy
data = gaussxy.generate({x, y}, 10000)
 
ws = ROOT.RooWorkspace()
ws.Import(gaussxy, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(data)

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
export_file = export_dir / "rf304_uncorrprod.json"
tool.exportJSON(str(export_file))
