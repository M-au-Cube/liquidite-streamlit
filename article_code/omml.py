"""LaTeX -> OMML (Office Math) via latex2mathml + Microsoft MML2OMML.XSL."""
import re
from lxml import etree
import latex2mathml.converter as l2m

XSL = r"C:/Program Files/Microsoft Office/root/Office16/MML2OMML.XSL"
_xslt = etree.XSLT(etree.parse(XSL))
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

def latex_to_omml(tex, display=False):
    mml = l2m.convert(tex, display="block" if display else "inline")
    mml = mml.replace('<math ', '<math xmlns:mml="http://www.w3.org/1998/Math/MathML" ', 1) if 'xmlns=' not in mml else mml
    tree = etree.fromstring(mml)
    om = _xslt(tree).getroot()
    return om  # <m:oMath> element
