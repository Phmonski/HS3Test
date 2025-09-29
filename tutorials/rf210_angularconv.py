from pathlib import Path

import ROOT
 
# Set up component pdfs
# ---------------------------------------
 
# Define angle psi
psi = ROOT.RooRealVar("psi", "psi", 0, 3.14159268)
 
# Define physics p.d.f T(psi)
Tpsi = ROOT.RooGenericPdf("Tpsi", "1+sin(2*@0)", [psi])
 
# Define resolution R(psi)
gbias = ROOT.RooRealVar("gbias", "gbias", 0.2, 0.0, 1)
greso = ROOT.RooRealVar("greso", "greso", 0.3, 0.1, 1.0)
Rpsi = ROOT.RooGaussian("Rpsi", "Rpsi", psi, gbias, greso)
 
# Define cos(psi) and function psif that calculates psi from cos(psi)
cpsi = ROOT.RooRealVar("cpsi", "cos(psi)", -1, 1)
psif = ROOT.RooFormulaVar("psif", "acos(cpsi)", [cpsi])
 
# Define physics p.d.f. also as function of cos(psi): T(psif(cpsi)) = T(cpsi)
Tcpsi = ROOT.RooGenericPdf("T", "1+sin(2*@0)", [psif])
 
# Construct convolution pdf in psi
# --------------------------------------------------------------
 
# Define convoluted p.d.f. as function of psi: M=[T(x)R](psi) = M(psi)
Mpsi = ROOT.RooFFTConvPdf("Mf", "Mf", psi, Tpsi, Rpsi)
 
# Set the buffer fraction to zero to obtain a ROOT.True cyclical
# convolution
Mpsi.setBufferFraction(0)
 
# Sample, fit and plot convoluted pdf (psi)
# --------------------------------------------------------------------------------
 
# Generate some events in observable psi
data_psi = Mpsi.generate({psi}, 10000)
 
# Fit convoluted model as function of angle psi
Mpsi.fitTo(data_psi, PrintLevel=-1)
 
 
# Construct convolution pdf in cos(psi)
# --------------------------------------------------------------------------
 
# Define convoluted p.d.f. as function of cos(psi): M=[T(x)R](psif cpsi)) = M(cpsi:
#
# Need to give both observable psi here (for definition of convolution)
# and function psif here (for definition of observables, in cpsi)
Mcpsi = ROOT.RooFFTConvPdf("Mcf", "Mcf", psif, psi, Tpsi, Rpsi)
 
# Set the buffer fraction to zero to obtain a ROOT.True cyclical
# convolution
Mcpsi.setBufferFraction(0)
 
# Sample, fit and plot convoluted pdf (cospsi)
# --------------------------------------------------------------------------------
 
# Generate some events
data_cpsi = Mcpsi.generate({cpsi}, 10000)
 
# set psi constant to exclude to be a parameter of the fit
psi.setConstant(True)
 
# Fit convoluted model as function of cos(psi)
Mcpsi.fitTo(data_cpsi, PrintLevel=-1)

ws = ROOT.RooWorkspace("ws")
ws.Import(Mpsi, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(Mcpsi, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(data_psi)
ws.Import(data_cpsi)

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
exportFile = str(export_dir / "rf210_angularconv.json")
tool.exportJSON(exportFile)

 
