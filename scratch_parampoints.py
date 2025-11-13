import ROOT

y = ROOT.RooRealVar("y", "y", 1, -5, 5)

a = ROOT.RooRealVar("a", "a", 2, -5, 5)
b = ROOT.RooRealVar("b", "b", 3, -5, 5)

func = ROOT.RooPolyVar("myFunc", "myFunc", y, [a, b])
func.Print("t")
print("Function Variable:", func.x().GetName())

print(ROOT.__version__)

pdf = ROOT.RooPolynomial("myPdf", "myPdf", y, [a, b])
pdf.Print("t")
print("Pdf Variable:", pdf.x().GetName())