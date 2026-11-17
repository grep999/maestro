import test from 'node:test';
import assert from 'node:assert/strict';
import { HISTORICAL_FACTS, HISTORICAL_EVENTS } from '../src/historical.js';

test('historical aggregate facts are sourced and caveated', () => {
  assert.equal(HISTORICAL_FACTS.length,6);
  for(const fact of HISTORICAL_FACTS){
    assert.ok(fact.id&&fact.source&&fact.url);
    assert.ok(fact.caveat.length>10);
  }
  const foreign=HISTORICAL_FACTS.find(x=>x.id==='GUS-2009-T4-FOREIGN');
  assert.equal(foreign.value,59);
  assert.match(foreign.caveat,/not the total|całkowita/i);
});
test('company casebook keeps the five verified events separate', () => {
  assert.equal(HISTORICAL_EVENTS.length,5);
  const pzu=HISTORICAL_EVENTS.find(x=>x.id.startsWith('PZU-'));
  assert.match(pzu.buyer,/20%/);
  assert.match(pzu.buyer,/10%/);
  assert.match(pzu.detail,/Nie jest to 30% kapitału zagranicznego/);
});
test('Bank Pekao consideration is explicitly arithmetically derived', () => {
  const pekao=HISTORICAL_EVENTS.find(x=>x.id.startsWith('PEKAO-'));
  assert.match(pekao.stake,/52,09%/);
  assert.match(pekao.detail,/75 707 500 akcji po 56 zł/);
});
test('historical transaction records include source links and dates', () => {
  for(const event of HISTORICAL_EVENTS){
    assert.ok(event.date&&event.title&&event.buyer&&event.seller&&event.stake);
    assert.ok(event.url.startsWith('https://'));
  }
});
