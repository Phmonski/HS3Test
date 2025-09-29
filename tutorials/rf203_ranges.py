from pathlib import Path

import ROOT
 
# Set up model
# ---------------------
 
# Construct observables x
x = ROOT.RooRealVar("x", "x", -10, 10)
 
# Construct gaussx(x,mx,1)
mx = ROOT.RooRealVar("mx", "mx", 0, -10, 10)
gx = ROOT.RooGaussian("gx", "gx", x, mx, 1.0)


# px = ax + 1 (flat in x)
a = ROOT.RooRealVar("a", "a", 0.1, -0.1, 0.1)
px = ROOT.RooPolynomial("px", "px", x, [a])
 
# model = f*gx + (1-f)px
f = ROOT.RooRealVar("f", "f", 0.0, 1.0)
model = ROOT.RooAddPdf("model", "model", [gx, px], [f])
 
# Generated 10000 events in (x,y) from pdf model
modelData = model.generate({x}, 10000)
 
# Fit full range
# ---------------------------
 
# Fit pdf to all data
r_full = model.fitTo(modelData, Save=True, PrintLevel=-1)
 
# Fit partial range
# ----------------------------------
 
# Define "signal" range in x as [-3,3]
x.setRange("signal", -3, 3)

# Fit pdf only to data in "signal" range
r_sig = model.fitTo(modelData, Save=True, Range="signal", PrintLevel=-1)
 
ws = ROOT.RooWorkspace()

ws.Import(model, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(modelData, ROOT.RooFit.RecycleConflictNodes(True))

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
exportFile = str(export_dir / "rf203_ranges.json")
tool.exportJSON(exportFile)

# Plot/print results
# ---------------------------------------
 
# Make plot frame in x and add data and fitted model
frame = x.frame(Title="Fitting a sub range")
modelData.plotOn(frame)
model.plotOn(frame, Range="Full", LineColor="r", LineStyle="--")  # Add shape in full ranged dashed
model.plotOn(frame)  # By default only fitted range is shown
 
# Print fit results
print("result of fit on all data ")
r_full.Print()
print("result of fit in in signal region (note increased error on signal fraction)")
r_sig.Print()
 
# Draw frame on canvas
c = ROOT.TCanvas("rf203_ranges", "rf203_ranges", 600, 600)
ROOT.gPad.SetLeftMargin(0.15)
frame.GetYaxis().SetTitleOffset(1.4)
frame.Draw()
