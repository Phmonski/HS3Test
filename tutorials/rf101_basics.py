from pathlib import Path

import ROOT
 
# Set up model
# ---------------------
# Declare variables x,mean,sigma with associated name, title, initial
# value and allowed range
x = ROOT.RooRealVar("x", "x", -10, 10)
mean = ROOT.RooRealVar("mean", "mean of gaussian", 1, -10, 10)
sigma = ROOT.RooRealVar("sigma", "width of gaussian", 1, 0.1, 10)
 
# Build gaussian pdf in terms of x,mean and sigma
gauss = ROOT.RooGaussian("gauss", "gaussian PDF", x, mean, sigma)
 
# Plot model and change parameter values
# ---------------------------------------------------------------------------
# Change the value of sigma to 3
sigma.setVal(3)
 
# Generate events
# -----------------------------
# Generate a dataset of 1000 events in x from gauss
data = gauss.generate({x}, 10000)  # ROOT.RooDataSet
 
ws = ROOT.RooWorkspace()
ws.Import(gauss)
ws.Import(data)

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
exportFile = str(export_dir / "rf101_basics.json")
tool.exportJSON(exportFile)

# Fit model to data
# -----------------------------
# Fit pdf to data
gauss.fitTo(data, PrintLevel=-1)
 
# Print values of mean and sigma (that now reflect fitted values and
# errors)
mean.Print()
sigma.Print()
 
