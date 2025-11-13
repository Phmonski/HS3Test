from pathlib import Path

import ROOT
 
# B-physics pdf with truth resolution
# ---------------------------------------------------------------------
 
# Variables of decay pdf
dt = ROOT.RooRealVar("dt", "dt", -10, 10)
tau = ROOT.RooRealVar("tau", "tau", 1.548)
 
# Build a truth resolution model (delta function)
tm = ROOT.RooTruthModel("tm", "truth model", dt)
 
# Construct decay(t) (x) delta(t)
decay_tm = ROOT.RooDecay("decay_tm", "decay", dt, tau, tm, type=0)
 
# B-physics pdf with Gaussian resolution
# ----------------------------------------------------------------------------
 
# Build a gaussian resolution model
bias1 = ROOT.RooRealVar("bias1", "bias1", 0)
sigma1 = ROOT.RooRealVar("sigma1", "sigma1", 1)
gm1 = ROOT.RooGaussModel("gm1", "gauss model 1", dt, bias1, sigma1)
 
# Construct decay(t) (x) gauss1(t)
decay_gm1 = ROOT.RooDecay("decay_gm1", "decay", dt, tau, gm1, type=0)
 
# B-physics pdf with double Gaussian resolution
# ------------------------------------------------------------------------------------------
 
# Build another gaussian resolution model
bias2 = ROOT.RooRealVar("bias2", "bias2", 0)
sigma2 = ROOT.RooRealVar("sigma2", "sigma2", 5)
gm2 = ROOT.RooGaussModel("gm2", "gauss model 2", dt, bias2, sigma2)
 
# Build a composite resolution model f*gm1+(1-f)*gm2
gm1frac = ROOT.RooRealVar("gm1frac", "fraction of gm1", 0.5)
gmsum = ROOT.RooAddModel("gmsum", "sum of gm1 and gm2", [gm1, gm2], [gm1frac])
 
# Construct decay(t) (x) (f*gm1 + (1-f)*gm2)
decay_gmsum = ROOT.RooDecay("decay_gmsum", "decay", dt, tau, gmsum, type=0)
ws = ROOT.RooWorkspace()

ws.Import(decay_tm, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(decay_gm1, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(decay_gmsum, ROOT.RooFit.RecycleConflictNodes(True))

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
ws_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(ws_sanitized)
tool.allowExportInvalidNames = True
export_file = export_dir / "rf209_anaconv.json"
tool.exportJSON(str(export_file))
