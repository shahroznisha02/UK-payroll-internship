"""UK monthly payroll calculator (2026/27 rates, England/Wales/NI).
Handles tax codes (e.g. 1257L, BR, 0T) and NI categories (A, B, C, H, J, M, Z).
Simplified: no student loan, pension, Scottish rates or K codes.
"""
import math

NI_PT, NI_UEL, NI_ST = 1048.00, 4189.00, 417.00        # monthly thresholds
NI_RATES = {"A": (0.08, 0.02), "B": (0.0185, 0.02), "C": (0, 0),
            "H": (0.08, 0.02), "M": (0.08, 0.02), "J": (0.02, 0.02), "Z": (0.02, 0.02)}
BANDS = [(37700 / 12, 0.20), (125140 / 12, 0.40), (math.inf, 0.45)]  # monthly


def free_pay(code):
    """Monthly tax-free pay from a tax code (HMRC rule: number*10+9, /12)."""
    code = code.upper()
    if code in ("BR", "D0", "D1", "0T"):
        return 0.0
    number = int("".join(ch for ch in code if ch.isdigit()))
    return round((number * 10 + 9) / 12, 2)


def income_tax(gross, code):
    code = code.upper()
    if code in ("BR", "D0", "D1"):
        rate = {"BR": 0.20, "D0": 0.40, "D1": 0.45}[code]
        return round(math.floor(gross) * rate, 2)
    taxable = math.floor(max(gross - free_pay(code), 0))   # round down to £
    tax, lower = 0.0, 0.0
    for upper, rate in BANDS:
        if taxable > lower:
            tax += (min(taxable, upper) - lower) * rate
        lower = upper
    return round(tax, 2)


def employee_ni(gross, cat):
    main, upper = NI_RATES[cat.upper()]
    ni = max(min(gross, NI_UEL) - NI_PT, 0) * main + max(gross - NI_UEL, 0) * upper
    return round(ni, 2)


def employer_ni(gross):
    return round(max(gross - NI_ST, 0) * 0.15, 2)


def payslip(gross, code, cat):
    tax, ni = income_tax(gross, code), employee_ni(gross, cat)
    return {"gross": gross, "tax": tax, "ni": ni,
            "net": round(gross - tax - ni, 2), "employer_ni": employer_ni(gross)} 


if _name_ == "_main_":
    for code, cat in [("1257L", "A"), ("BR", "A"), ("1257L", "C")]:
        p = payslip(2500, code, cat)
        print(f"{code:6} Cat {cat} | tax {p['tax']:7.2f} | NI {p['ni']:6.2f} | net {p['net']:8.2f}")
