import ROOT
from pathlib import Path
 
# Define observables and decay pdf
# ---------------------------------------------------------------
 
# Declare observables
t = ROOT.RooRealVar("t", "t", 0, 5)
 
# Make pdf
tau = ROOT.RooRealVar("tau", "tau", -1.54, -4, -0.1)
model = ROOT.RooExponential("model", "model", t, tau)
 
# Define efficiency function
# ---------------------------------------------------
 
# Use error function to simulate turn-on slope
eff = ROOT.RooFormulaVar("eff", "0.5*(TMath::Erf((t-1)/0.5)+1)", [t])
 
# Define decay pdf with efficiency
# ---------------------------------------------------------------
 
# Multiply pdf(t) with efficiency in t
modelEff = ROOT.RooEffProd("modelEff", "model with efficiency", model, eff)
copyEff = ROOT.RooEffProd(modelEff, "copyEff")
copyEff.Print("t")
# Generate events. If the input pdf has an internal generator, internal generator
# is used and an accept/reject sampling on the efficiency is applied.
data = modelEff.generate({t}, 10000)

 
ws = ROOT.RooWorkspace("ws")

ws.Import(modelEff, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(data, ROOT.RooFit.RecycleConflictNodes(True))

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
export_file = export_dir / "rf703_effpdfprod.json"
tool.exportJSON(str(export_file))