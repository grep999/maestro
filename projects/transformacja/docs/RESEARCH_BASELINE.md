# Historical research baseline

## Evidence architecture

The project keeps three evidence layers separate:

1. **Official aggregates** — Statistics Poland (GUS) and IMF series with exact table locators, period definitions and limitations.
2. **Company transaction events** — only closed events with named parties, event date and precision, stake, source IDs, locator, confidence and explicit uncertainty.
3. **Research leads** — candidate cases that are not yet sufficiently verified and must not be treated as facts in game logic.

## GUS aggregates (1990–2008)

The 2009 Statistical Yearbook records 7,463 state-owned enterprises included in ownership transformation; 2,105 enterprises in direct privatization; 1,317 direct privatizations by paid lease; 1,560 employee companies in a narrower group of 1,825; 59 companies with foreign-capital participation among 265 companies with State Treasury participation in that group; and 512 companies in the National Investment Fund programme.

These are distinct statistical categories. In particular, 59 is not the total number of foreign acquisitions in Poland. Programme participation, paid leasing, direct privatization and a share sale are not interchangeable events.

## IMF route series

The IMF table provides annual cumulative totals and annual flows from 1990 through 1995, plus a Jan–Sep 1996 column. The last period is nine months and must not be relabelled as a full year. The CSV keeps cumulative and flow measures in separate columns.

## Company-level casebook

The current ledger contains five closed cases:

- Telekomunikacja Polska: October 2000 consortium purchase of 35% (France Telecom 25%, Kulczyk Holding 10%); consortium investment is not treated as Treasury sale consideration.
- PZU: November 1999 transfer of 30%, split between Eureko (20%) and domestic BIG Bank Gdański (10%); it is not 30% foreign ownership.
- Bank Pekao: August 1999 sale of 52.09%; 75,707,500 shares at PLN 56, yielding PLN 4,239,620,000 arithmetically and approximately PLN 4.24bn in the parliamentary record.
- Polskie Huty Stali: March 2004 completion; LNM 60%, State Treasury 25%, employees 15%; consideration and detailed obligations remain unknown.
- Śląska Spółka Cukrowa: April 2003 transfer of 95% to Saint Louis Sucre International; State Treasury retained 2.57%; consideration and remaining cap table are not inferred.

## Research leads and caveats

Eleven leads include Bank Zachodni, Bank Handlowy, Biedronka, E. Wedel, FSM/Fiat Auto Poland and STOEN. A lead is not a verified event. Follow-on ownership tranches, investment obligations, employment guarantees, legal control and later acquisitions require separate records.

## Non-negotiable research rules

- Preserve unknown values as null; never fill gaps with plausible estimates.
- Distinguish buyer consortium composition from ultimate parent and nationality.
- Distinguish share sale, asset sale, lease, liquidation, greenfield FDI and indirect control.
- Separate signing, closing, announcement and later ownership dates.
- Do not infer employment or productivity effects from ownership changes without credible identification.
- Keep all source locators and uncertainty notes with the claim they support.
