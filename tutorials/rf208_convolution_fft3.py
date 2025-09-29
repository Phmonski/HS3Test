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

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
exportFile = str(export_dir / "rf208_convolution_fft3.json")
tool.exportJSON(exportFile)

# Plot data, pdf, landau (X) gauss pdf
frame = t.frame(Title="landau (x) gauss convolution")
data.plotOn(frame)
lxg.plotOn(frame)
landau.plotOn(frame, LineStyle="--")
 
