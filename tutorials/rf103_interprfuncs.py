from pathlib import Path

import ROOT
 
# Generic interpreted pdf
# ------------------------------
 
# Declare observable x
x = ROOT.RooRealVar("x", "x", -20, 20)
 
# Construct generic pdf from interpreted expression
# ------------------------------------------------------
 
# ROOT.To construct a proper pdf, the formula expression is explicitly normalized internally by dividing
# it by a numeric integral of the expression over x in the range [-20,20]
#
alpha = ROOT.RooRealVar("alpha", "alpha", 5, 0.1, 10)
genpdf = ROOT.RooGenericPdf("genpdf", "genpdf", "(1+0.1*abs(x)+sin(sqrt(abs(x*alpha+0.1))))", [x, alpha])
 
# Sample, fit and plot generic pdf
# ---------------------------------------------------------------
 
# Generate a toy dataset from the interpreted pdf
data = genpdf.generate({x}, 10000)
 
# Fit the interpreted pdf to the generated data
r = genpdf.fitTo(data, Save=True, PrintLevel=-1)
# Make a plot of the data and the pdf overlaid
 
# Standard pdf adjust with interpreted helper function
# ------------------------------------------------------------------------------------------------------------
# Make a gauss(x,sqrt(mean2),sigma) from a standard ROOT.RooGaussian                                               #
#
# Construct standard pdf with formula replacing parameter
# ------------------------------------------------------------------------------------------------------------
 
# Construct parameter mean2 and sigma
mean2 = ROOT.RooRealVar("mean2", "mean^2", 10, 0, 200)
sigma = ROOT.RooRealVar("sigma", "sigma", 3, 0.1, 10)
 
# Construct interpreted function mean = sqrt(mean^2)
mean = ROOT.RooFormulaVar("mean", "mean", "sqrt(mean2)", [mean2])
 
# Construct a gaussian g2(x,sqrt(mean2),sigma)
g2 = ROOT.RooGaussian("g2", "h2", x, mean, sigma)
 
# Generate toy data
# ---------------------------------
 
# Construct a separate gaussian g1(x,10,3) to generate a toy Gaussian
# dataset with mean 10 and width 3
g1 = ROOT.RooGaussian("g1", "g1", x, 10, 3)
data2 = g1.generate({x}, 1000)


ws = ROOT.RooWorkspace()
ws.Import(genpdf)
ws.Import(data)
ws.Import(g2)
ws.Import(data2)

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
exportFile = str(export_dir / "rf103_interprfuncs.json")
tool.exportJSON(exportFile)



# Fit and plot tailored standard pdf
# -------------------------------------------------------------------
 
# Fit g2 to data from g1
r = g2.fitTo(data2, Save=True, PrintLevel=-1)  # ROOT.RooFitResult
 

