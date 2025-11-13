from pathlib import Path

import ROOT
 
 
def makeFakeDataXY():
 
    trnd = ROOT.TRandom3()
 
    x = ROOT.RooRealVar("x", "x", -10, 10)
    y = ROOT.RooRealVar("y", "y", -10, 10)
    coord = {x, y}
 
    d = ROOT.RooDataSet("d", "d", coord)
 
    for i in range(10000):
        tmpy = trnd.Gaus(0, 10)
        tmpx = trnd.Gaus(0.5 * tmpy, 1)
        if (abs(tmpy) < 10) and (abs(tmpx) < 10):
            x.setVal(tmpx)
            y.setVal(tmpy)
            d.add(coord)
 
    return d
 
 
# Set up composed model gauss(x, m(y), s)
# -----------------------------------------------------------------------
 
# Create observables
x = ROOT.RooRealVar("x", "x", -10, 10)
y = ROOT.RooRealVar("y", "y", -10, 10)
 
# Create function f(y) = a0 + a1*y
a0 = ROOT.RooRealVar("a0", "a0", -0.5, -5, 5)
a1 = ROOT.RooRealVar("a1", "a1", -0.5, -1, 1)
fy = ROOT.RooPolyVar("fy", "fy", y, [a0, a1])
 
# Creat gauss(x,f(y),s)
sigma = ROOT.RooRealVar("sigma", "width of gaussian", 0.5, 0.1, 2.0)
model = ROOT.RooGaussian("model", "Gaussian with shifting mean", x, fy, sigma)
 
# Obtain fake external experimental dataset with values for x and y
expDataXY = makeFakeDataXY()
 
# Generate data from conditional p.d.f. model(x|y)
# ---------------------------------------------------------------------------------------------
 
# Make subset of experimental data with only y values
expDataY = expDataXY.reduce({y})
 
# Generate 10000 events in x obtained from _conditional_ model(x|y) with y
# values taken from experimental data
data = model.generate({x}, ProtoData=expDataY)
 
# Fit conditional p.d.f model(x|y) to data
# ---------------------------------------------------------------------------------------------
 
r1 = model.fitTo(expDataXY, ConditionalObservables={y}, Save=True, PrintLevel=-1)

ws = ROOT.RooWorkspace()

ws.Import(model, ROOT.RooFit.RecycleConflictNodes(True))
ws.Import(data)
ws.Import(expDataXY)

export_dir = Path(__file__).resolve().parents[1] / "exportedJSON"
export_dir.mkdir(exist_ok=True)
w_sanitized = ROOT.RooJSONFactoryWSTool.sanitizeWS(ws)
tool = ROOT.RooJSONFactoryWSTool(w_sanitized)
tool.allowExportInvalidNames = False
export_file = export_dir / "rf303_conditional.json"
tool.exportJSON(str(export_file))
