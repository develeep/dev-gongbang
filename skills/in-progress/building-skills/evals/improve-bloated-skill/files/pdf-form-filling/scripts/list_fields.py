import sys
from pypdf import PdfReader
r = PdfReader(sys.argv[1])
for k, v in (r.get_fields() or {}).items():
    print(k, v.get("/FT"))
