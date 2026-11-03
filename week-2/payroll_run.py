"UK monthly payroll run with payslip (2026/27 rates, England/Wales/NI).
Includes: PAYE on a cumulative basis, employee + employer NI (category A),
and workplace pension (auto-enrolment, net pay arrangement).
Simplified: no student loan, Scottish rates or K codes.
"""
import math

NI_PT, NI_UEL, NI_ST = 1048.00, 4189.00, 417.00      # monthly NI thresholds
PEN_LOWER, PEN_UPPER = 520.00, 4189.00               # monthly qualifying earnings band
PEN_EE, PEN_ER = 0.05, 0.03                          # minimum auto-enrolment rates
BANDS = [(37700 / 12, 0.20), (125140 / 12, 0.40), (math.inf, 0.45)]  # monthly band widths


def free_pay(code):
    """Monthly free pay from a tax code, e.g. 1257L -> 1048.25."""
    return round((int("".join(c for c in code if c.isdigit())) * 10 + 9) / 12, 2)


def tax_to_date(taxable_ytd, month_no):
    """Cumulative tax: band limits grow by one month's width each tax month."""
    tax, lower = 0.0, 0.0
    for width, rate in BANDS:
        upper = width * month_no
        if taxable_ytd > lower:
            tax += (min(taxable_ytd, upper) - lower) * rate
        lower = upper
    return round(tax, 2)


def pension(gross):
    qe = max(min(gross, PEN_UPPER) - PEN_LOWER, 0)
    return round(qe * PEN_EE, 2), round(qe * PEN_ER, 2)


def run_payroll(gross, code, month_no):
    ee_pen, er_pen = pension(gross)
    taxable_ytd = math.floor(max((gross - ee_pen) * month_no - free_pay(code) * month_no, 0))
    taxable_prev = math.floor(max((gross - ee_pen) * (month_no - 1) - free_pay(code) * (month_no - 1), 0))
    tax = round(tax_to_date(taxable_ytd, month_no) - tax_to_date(taxable_prev, month_no - 1), 2)
    ni = round(max(min(gross, NI_UEL) - NI_PT, 0) * 0.08 + max(gross - NI_UEL, 0) * 0.02, 2)
    er_ni = round(max(gross - NI_ST, 0) * 0.15, 2)
    return {"gross": gross, "ee_pension": ee_pen, "tax": tax, "ni": ni,
            "net": round(gross - ee_pen - tax - ni, 2),
            "er_ni": er_ni, "er_pension": er_pen,
            "employer_cost": round(gross + er_ni + er_pen, 2),
            "tax_ytd": tax_to_date(taxable_ytd, month_no), "taxable_ytd": taxable_ytd}


if _name_ == "_main_":
    r = run_payroll(3000, "1257L", 8)
    print("Gross pay           :", f"{r['gross']:9.2f}")
    print("Pension (employee)  :", f"{r['ee_pension']:9.2f}")
    print("Income Tax (PAYE)   :", f"{r['tax']:9.2f}")
    print("Employee NI (Cat A) :", f"{r['ni']:9.2f}")
    print("NET PAY             :", f"{r['net']:9.2f}")
    print("Employer NI         :", f"{r['er_ni']:9.2f}")
    print("Employer pension    :", f"{r['er_pension']:9.2f}")
    print("Total employer cost :", f"{r['employer_cost']:9.2f}")
