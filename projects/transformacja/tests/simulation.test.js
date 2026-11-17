import test from 'node:test';
import assert from 'node:assert/strict';
import {
  MODEL_VERSION, createInitialState, firmDemand, firmWorkingCapital,
  firmFinancials, firmValuation, marketShares, hhi, portfolio, acquire,
  setPolicy, restructureOnePosition, advanceMonth, serialize, deserialize
} from '../src/simulation.js';

test('starts in January 1990 with explicitly fictional firms', () => {
  const s=createInitialState();
  assert.equal(s.modelVersion,MODEL_VERSION);
  assert.equal(s.year,1990); assert.equal(s.month,0);
  assert.equal(s.firms.length,4);
  assert.ok(s.firms.every(f=>f.historical===false));
});
test('working capital uses receivables plus inventory less payables', () => {
  const w=firmWorkingCapital({receivableDays:30,inventoryDays:30,payableDays:15},3000);
  assert.equal(w.receivables,3000); assert.equal(w.inventory,3000); assert.equal(w.payables,1500);
  assert.equal(w.netWorkingCapital,4500); assert.equal(w.cashConversionCycle,45);
});
test('demand is bounded and responds to price policy only under control', () => {
  const s=createInitialState(), f=s.firms[0], before=firmDemand(s,f);
  setPolicy(s,{pricePolicy:1.2});
  assert.equal(firmDemand(s,f),before);
  s.owned[f.id]={stake:.51,control:true};
  assert.ok(firmDemand(s,f)<before);
});
test('DCF returns a transparent scenario valuation and rejects invalid discount rates', () => {
  const s=createInitialState(), v=firmValuation(s,s.firms[0]);
  assert.ok(v.enterpriseValue>0); assert.ok(v.equityValue>=0);
  assert.match(v.calibration,/not a historical Polish valuation series/);
  assert.throws(()=>firmValuation(s,s.firms[0],{discountRate:.01,terminalGrowth:.02}),RangeError);
});
test('unknown firms cannot be valued or acquired', () => {
  const s=createInitialState();
  assert.equal(firmValuation(s,'missing'),null);
  assert.equal(acquire(s,'missing').ok,false);
});
test('offer below seller reserve is rejected without mutating state', () => {
  const s=createInitialState(), cash=s.cash, debt=s.debt;
  const r=acquire(s,'kiosk',{stake:.51,offerMultiplier:.7});
  assert.equal(r.ok,false); assert.ok(r.counterOffer>0);
  assert.equal(s.cash,cash); assert.equal(s.debt,debt); assert.equal(Object.keys(s.owned).length,0);
});
test('accepted acquisition records DCF snapshot and control boundary', () => {
  const s=createInitialState();
  const r=acquire(s,'kiosk',{stake:.51,offerMultiplier:1,debtShare:.25});
  assert.equal(r.ok,true); assert.equal(s.owned.kiosk.control,true);
  assert.ok(s.owned.kiosk.valuationSnapshot.discountRate>0);
  assert.equal(s.cash,5_000_000-r.equity);
});
test('minority acquisition does not grant operational control', () => {
  const s=createInitialState(), r=acquire(s,'kiosk',{stake:.25,offerMultiplier:1});
  assert.equal(r.ok,true); assert.equal(s.owned.kiosk.control,false);
});
test('debt financing is capped at sixty percent', () => {
  const s=createInitialState();
  assert.equal(acquire(s,'kiosk',{debtShare:.61}).ok,false);
});
test('market shares sum to one hundred and HHI is bounded', () => {
  const s=createInitialState();
  const shares=marketShares(s);
  assert.ok(Math.abs(shares.reduce((a,x)=>a+x.share,0)-100)<1e-8);
  assert.ok(hhi(s)>=0&&hhi(s)<=10000);
});
test('restructuring requires control and imposes severance/social cost', () => {
  const s=createInitialState();
  assert.equal(restructureOnePosition(s,'kiosk').ok,false);
  acquire(s,'kiosk',{stake:.51});
  const trust=s.trust, workers=s.firms[0].workers;
  const r=restructureOnePosition(s,'kiosk');
  assert.equal(r.ok,true); assert.equal(s.firms[0].workers,workers-1); assert.ok(s.trust<trust);
});
test('monthly progression updates the calendar and macro variables', () => {
  const s=createInitialState(), cpi=s.consumerPriceIndex;
  advanceMonth(s);
  assert.equal(s.month,1); assert.ok(s.consumerPriceIndex>cpi);
});
test('1995 redenomination changes units by exactly 10,000', () => {
  const s=createInitialState(); s.year=1994; s.month=11;
  const cash=s.cash; advanceMonth(s);
  assert.equal(s.year,1995); assert.equal(s.month,0); assert.equal(s.currency,'PLN');
  assert.equal(s.cash,cash/10000);
});
test('serialization round-trips the current model', () => {
  const s=createInitialState(), restored=deserialize(serialize(s));
  assert.equal(restored.modelVersion,MODEL_VERSION);
  assert.deepEqual(restored.owned,s.owned);
});
test('portfolio is empty before acquisition and reflects controlled stake after', () => {
  const s=createInitialState(); assert.equal(portfolio(s).positions.length,0);
  acquire(s,'grocery',{stake:.51});
  assert.equal(portfolio(s).positions.length,1);
  assert.equal(portfolio(s).positions[0].control,true);
});
