from pathlib import Path
import ROOT

x = ROOT.RooRealVar("x", "x", -10, 10)
mean = ROOT.RooRealVar("mean", "mean of gaussian", 1, -10, 10)
sigma = ROOT.RooRealVar("sigma", "width of gaussian", 1, 0.1, 10)

gauss = ROOT.RooGaussian("gauss", "gaussian PDF", x, mean, sigma)

sigma.setVal(3)

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

