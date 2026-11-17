# Economic model — version 0.4.0

## Purpose and status

The model is a deterministic monthly sandbox for exploring corporate ownership, operating decisions, financing, labour, consumers and local concentration. It is a mechanics prototype, not an econometrically or historically calibrated reconstruction of Poland's macroeconomy.

## Accounting and operating loop

Each stylized firm has revenue, variable costs, payroll, fixed costs, assets, productivity, quality, capacity, and sector-specific receivable, inventory and payable days. The monthly loop calculates demand, capacity-constrained revenue, operating profit, interest and illustrative tax. Portfolio cash flow is ownership-share weighted.

Working capital is represented as receivables plus inventory less payables, using day-based approximations. Changes in portfolio working capital affect cash. The model does not yet contain full balance sheets, explicit cash conversion at firm level, inventory stock accounting, depreciation schedules or detailed tax law.

## Ownership and acquisitions

The sandbox begins with fictional local firms. Historical companies in the casebook are evidence records only and are not purchasable. Acquisitions support 25%, 51% and 100% stakes. A 50% threshold is used as a simplified operational-control heuristic; real corporate control depends on voting arrangements, governance, dispersed ownership, board appointment rights and other factors.

The seller reserve ratio (85% of ask) and offer bounds (70–150% of ask) are deterministic game mechanics, not claims about historical Polish privatization practice. Acquisition financing is capped at 60% debt in this prototype.

## Valuation

The five-year DCF is an indicative scenario tool. It uses an unlevered operating cash-flow proxy, maintenance-capex allowance based on book assets, incremental day-based working capital, a sector risk premium and a terminal growth assumption. Discount rate must exceed terminal growth.

It omits full capex plans, depreciation and amortization schedules, working-capital seasonality, detailed taxes, pension liabilities, contingent liabilities, control premiums, minority discounts, transaction costs and stochastic sensitivity. It must not be presented as an observed or historically calibrated transaction valuation.

## Macro and welfare

Inflation, interest and tax settings are scenario parameters. They are not historical GUS/NBP time series. Household real income and social trust are deliberately simplified indicators. The 1995 denomination converts nominal values at 10,000 old złoty to one new złoty; it is a unit conversion, not a real wealth shock.

## Concentration and employment

Market shares and HHI are calculated from modeled sales. Restructuring one worker creates a severance cost and reduces quality, household income and trust. These are explicit game assumptions, not empirical causal estimates of privatization effects.

## Next calibration requirements

Before claiming historical realism, add primary-source macro series, firm-level balance-sheet and employment observations, transaction-level price/obligation data, institutional rules by privatization route, and a documented parameter-estimation process. Include uncertainty and scenario ranges rather than point estimates where the evidence is weak.
