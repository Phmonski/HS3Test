from pathlib import Path

import ROOT
 
# Set up component pdfs
# ---------------------------------------
 
# Construct observable
t = ROOT.RooRealVar("t", "t", -10, 30)
 
# Construct landau(t,ml,sl)
ml = ROOT.RooRealVar("ml", "mean landau", 5.0, -20, 20)
sl = ROOT.RooRealVar("sl", "sigma landau", 1, 0.1, 10)
landau = ROOT.RooLandau("lx", "lx", t, ml, sl)
 
# Construct gauss(t,mg,sg)
mg = ROOT.RooRealVar("mg", "mg", 0)
sg = ROOT.RooRealVar("sg", "sg", 2, 0.1, 10)
gauss = ROOT.RooGaussian("gauss", "gauss", t, mg, sg)
 
# Construct convolution pdf
# ---------------------------------------
 
# Set #bins to be used for FFT sampling to 10000
t.setBins(10000, "cache")
 
# Construct landau (x) gauss
lxg = ROOT.RooFFTConvPdf("lxg", "landau (X) gauss", t, landau, gauss)
 
# Sample, fit and plot convoluted pdf
# ----------------------------------------------------------------------
 
# Sample 1000 events in x from gxlx
data = lxg.generate({t}, 10000)
 
# Fit gxlx to data
lxg.fitTo(data, PrintLevel=-1)

ws = ROOT.RooWorkspace("ws")
ws.Import(lxg, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(data)

tool = ROOT.RooJSONFactoryWSTool(ws)
export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
tool.exportJSON(str(export_dir / "rf208_convolution_fft3.json"))

# Plot data, pdf, landau (X) gauss pdf
frame = t.frame(Title="landau (x) gauss convolution")
data.plotOn(frame)
lxg.plotOn(frame)
landau.plotOn(frame, LineStyle="--")
 
# Draw frame on canvas
c = ROOT.TCanvas("rf208_convolution", "rf208_convolution", 600, 600)
ROOT.gPad.SetLeftMargin(0.15)
frame.GetYaxis().SetTitleOffset(1.4)
frame.Draw()
