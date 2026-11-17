import { createInitialState, acquire, advanceMonth, firmFinancials, firmValuation, marketShares, hhi, portfolio, setPolicy, restructureOnePosition, serialize, deserialize, money, MONTHS } from './simulation.js';
import { HISTORICAL_FACTS, HISTORICAL_EVENTS } from './historical.js';
const $ = id => document.getElementById(id);
let state = createInitialState();
let selectedFirm = null;
const fmt = n => Math.round(n).toLocaleString('pl-PL');
const escapeHtml = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
function toast(message) { const el=$('toast'); el.textContent=message; el.classList.add('show'); setTimeout(()=>el.classList.remove('show'),2300); }
function render() {
  const p=portfolio(state), shares=marketShares(state);
  const totalSales=shares.reduce((a,x)=>a+x.sales,0);
  const ownedSales=p.positions.reduce((a,x)=>a+firmFinancials(state,x.firm).revenue*x.stake,0);
  $('date').textContent=`${MONTHS[state.month].toUpperCase()} ${state.year}`;
  $('currency').textContent=state.currency==='PLZ'?'STARE ZŁOTE · NOMINALNIE':'NOWE ZŁOTE · NOMINALNIE';
  $('cash').textContent=money(state.cash,state.currency); $('debt').textContent=money(state.debt,state.currency);
  $('profit').textContent=(p.net>=0?'+':'')+money(p.net,state.currency);
  $('profit').title=`Kapitał obrotowy netto portfela: ${money(p.netWorkingCapital,state.currency)}`;
  $('profit').style.color=p.net>=0?'var(--green)':'var(--red)';
  $('share').textContent=`${totalSales?Math.round(ownedSales/totalSales*100):0}%`;
  $('trust').textContent=`${Math.round(state.trust)} / 100`;
  $('jobs').textContent=fmt(p.jobs); $('income').textContent=Math.round(state.householdRealIncome);
  $('cpi').textContent=state.consumerPriceIndex.toLocaleString('pl-PL',{maximumFractionDigits:1}); $('hhi').textContent=Math.round(hhi(state));
  $('price').value=Math.round(state.pricePolicy*100); $('priceOut').textContent=`${Math.round(state.pricePolicy*100)}%`;
  $('wage').value=Math.round(state.wagePolicy*100); $('wageOut').textContent=`${Math.round(state.wagePolicy*100)}%`;
  $('investment').value=state.investmentBudget; $('investmentOut').textContent=fmt(state.investmentBudget);
  $('businesses').innerHTML=state.firms.map(f=>{
    const fin=firmFinancials(state,f), val=firmValuation(state,f), pos=state.owned[f.id];
    return `<article class="firm ${pos?'owned':''}"><div class="tag">${f.sector}</div><h3>${f.name}</h3><div class="seller">Sprzedający: ${f.seller}</div><div class="metrics"><span>Cena sprzedającego · 100%</span><b>${money(f.ask,state.currency)}</b><span>Szacunek kapitału · DCF</span><b>${money(val.equityValue,state.currency)}</b><span>Przychód / mies.</span><b>${money(fin.revenue,state.currency)}</b><span>Pracownicy</span><b>${f.workers}</b><span>Wynik operacyjny</span><b>${money(fin.operatingProfit,state.currency)}</b><span>Kapitał obrotowy netto</span><b>${money(fin.netWorkingCapital,state.currency)}</b><span>Cykl konwersji gotówki</span><b>${fin.cashConversionCycle} dni</b></div><div class="firm-actions">${pos?`<span class="owned-label">✓ ${Math.round(pos.stake*100)}% W PORTFELU</span>${pos.control?`<button class="danger" data-restructure="${f.id}">Restrukturyzuj zatrudnienie</button>`:'<span class="pill">Udział mniejszościowy · brak kontroli operacyjnej</span>'}`:`<button data-acquire="${f.id}">Negocjuj zakup udziałów</button>`}</div></article>`;
  }).join('');
  document.querySelectorAll('[data-acquire]').forEach(b=>b.addEventListener('click',()=>openDeal(b.dataset.acquire)));
  document.querySelectorAll('[data-restructure]').forEach(b=>b.addEventListener('click',()=>{const r=restructureOnePosition(state,b.dataset.restructure);toast(r.ok?'Zapisano restrukturyzację i jej koszty społeczne.':r.reason);render();}));
  $('ownership').innerHTML=p.positions.length?p.positions.map(({firm,stake,control})=>`<div class="metrics"><span>${firm.name}</span><b>${Math.round(stake*100)}% ${control?'· kontrola':'· mniejszość'}</b></div>`).join(''):'<span class="pill">Brak udziałów</span>';
  $('log').innerHTML=state.events.map(e=>`<div class="event"><b>${MONTHS[e.month].toUpperCase()} ${e.year} · ${e.kind.toUpperCase()}</b><br>${escapeHtml(e.text)}</div>`).join('')||'<div class="event">Styczeń 1990. Twoja historia właśnie się zaczyna.</div>';
  $('historicalAtlas').innerHTML=HISTORICAL_FACTS.map(f=>`<div class="case"><strong>${fmt(f.value)} ${escapeHtml(f.unitLabel)} · ${escapeHtml(f.title)}</strong><span>${escapeHtml(f.detail)}</span><div class="notice">${escapeHtml(f.caveat)}</div><span><a href="${escapeHtml(f.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(f.source)}</a></span></div>`).join('');
  $('historicalEvents').innerHTML=HISTORICAL_EVENTS.map(e=>`<div class="case"><strong>${escapeHtml(e.date)} · ${escapeHtml(e.title)}</strong><span><b>${escapeHtml(e.stake)}</b></span><span>Nabywca: ${escapeHtml(e.buyer)} · Sprzedający: ${escapeHtml(e.seller)}</span><div>${escapeHtml(e.detail)}</div><span><a href="${escapeHtml(e.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(e.source)}</a></span></div>`).join('');
}
function updateDealQuote() {
  if (!selectedFirm) return;
  const stake=Number($('stake').value), multiplier=Number($('offerMultiplier').value), debtShare=Number($('debtShare').value);
  const ask=selectedFirm.ask*stake, offer=ask*multiplier, loan=offer*debtShare, equity=offer-loan;
  const reserve=ask*(selectedFirm.sellerReserveRatio ?? 0.85), valuation=firmValuation(state,selectedFirm);
  $('dealQuote').innerHTML=`Cena sprzedającego za udział: <b>${money(ask,state.currency)}</b><br>Twoja oferta: <b>${money(offer,state.currency)}</b> (${Math.round(multiplier*100)}% ceny)<br>Cena rezerwowa: <b>${money(reserve,state.currency)}</b><br>Finansowanie: <b>${money(equity,state.currency)}</b> gotówki + <b>${money(loan,state.currency)}</b> długu<br>Szacowana wartość kapitału 100% (DCF): <b>${money(valuation.equityValue,state.currency)}</b><br>Założenia scenariusza: stopa dyskontowa ${Math.round(valuation.discountRate*1000)/10}%, wzrost ${Math.round(valuation.growthRate*1000)/10}%, wzrost terminalny ${Math.round(valuation.terminalGrowth*1000)/10}%, utrzymaniowy CAPEX ${Math.round(valuation.maintenanceCapexRate*100)}% rocznie.`;
}
function openDeal(id) {
  selectedFirm=state.firms.find(f=>f.id===id);
  $('dealTitle').textContent=`Nabycie: ${selectedFirm.name}`;
  const valuation=firmValuation(state,selectedFirm);
  $('dealDescription').textContent=`Cena sprzedającego: ${money(selectedFirm.ask,state.currency)} za 100%. Szacunek DCF: ${money(valuation.equityValue,state.currency)}. Wycena jest uproszczonym scenariuszem, nie historyczną ceną transakcyjną.`;
  $('dealModal').classList.add('show'); updateDealQuote();
}
function closeDeal() { $('dealModal').classList.remove('show'); selectedFirm=null; }
$('cancelDeal').onclick=closeDeal;
$('stake').onchange=updateDealQuote; $('offerMultiplier').onchange=updateDealQuote; $('debtShare').onchange=updateDealQuote;
$('confirmDeal').onclick=()=>{if(!selectedFirm)return;const result=acquire(state,selectedFirm.id,{stake:Number($('stake').value),debtShare:Number($('debtShare').value),offerMultiplier:Number($('offerMultiplier').value)});closeDeal();toast(result.ok?'Transakcja sfinalizowana.':result.counterOffer?`${result.reason} Cena rezerwowa: ${money(result.counterOffer,state.currency)}.`:result.reason);render();};
$('price').oninput=e=>{setPolicy(state,{pricePolicy:Number(e.target.value)/100});render();};
$('wage').oninput=e=>{setPolicy(state,{wagePolicy:Number(e.target.value)/100});render();};
$('investment').oninput=e=>{setPolicy(state,{investmentBudget:Number(e.target.value)});render();};
$('advance').onclick=()=>{advanceMonth(state);render();};
$('year').onclick=()=>{for(let i=0;i<12;i++)advanceMonth(state);render();};
$('save').onclick=()=>{localStorage.setItem('transformacja-save-v3',serialize(state));toast('Zapisano stan gry w tej przeglądarce.');};
$('load').onclick=()=>{try{const raw=localStorage.getItem('transformacja-save-v3')||localStorage.getItem('transformacja-save-v2');if(!raw)throw new Error('Brak zapisu.');state=deserialize(raw);render();toast('Wczytano zapis.');}catch(e){toast(e.message);}};
$('reset').onclick=()=>{if(confirm('Rozpocząć nową grę? Bieżący zapis pozostanie w pamięci przeglądarki.')){state=createInitialState();render();}};
render();
