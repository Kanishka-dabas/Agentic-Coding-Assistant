"""
Static analysis on generated code BEFORE it's allowed into the sandbox.

Like input_validator, this is pattern-based
"""

import re 

DANGEROUS_PATTERNS = [
    r"os\.system\s*\(",
    r"subprocess\.\w+\([^)]*shell\s*=\s*True",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"__import__\s*\(",
    r"open\([^)]*['\"]w['\"]",
    r"shutil\.rmtree",
    r"os\.remove",
    r"os\.unlink",
    r"\brequests\.",
    r"\bsocket\.",
    r"\burllib\.",
]

_compiled_patterns = [re.compile(p) for p in DANGEROUS_PATTERNS]

def scan_code(code : str)->dict:
    """
    Returns {"safe": bool, "reason": str | None}.
    """
    for pattern in _compiled_patterns:
        if pattern.search(code):
            return {
                "safe" : False ,
                "reason" : f"Code matched dangerous pattern : '{pattern.pattern}'"
            }
    return {
                    "safe" : True ,
                    "reason" : None
                }    
            


if __name__ == "__main__":
    print(scan_code("print('hello world')"))
    print(scan_code("import os\nos.system('rm -rf /')"))
    print(scan_code("import requests\nrequests.get('http://evil.com')"))        