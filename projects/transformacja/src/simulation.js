/**
 * TRANSFORMACJA — deterministic monthly simulation kernel.
 * All initial local-market businesses and numeric parameters are fictional/stylized.
 * Historical companies are deliberately not tradable in this sandbox slice.
 */
export const MODEL_VERSION = '0.4.0';
export const MONTHS = ['Sty', 'Lut', 'Mar', 'Kwi', 'Maj', 'Cze', 'Lip', 'Sie', 'Wrz', 'Paź', 'Lis', 'Gru'];

const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));
const round2 = x => Math.round((x + Number.EPSILON) * 100) / 100;

export function createInitialState() {
  return {
    modelVersion: MODEL_VERSION, year: 1990, month: 0, currency: 'PLZ',
    cash: 5_000_000, debt: 0, trust: 62, householdRealIncome: 100,
    consumerPriceIndex: 100, monthlyInflation: 0.08,
    baseRate: 0.12, taxRate: 0.19, pricePolicy: 1, wagePolicy: 1,
    investmentBudget: 50_000, owned: {}, events: [],
    firms: [
      { id:'kiosk', name:'Kiosk przy dworcu', sector:'retail', seller:'Prywatny przedsiębiorca', ask:450_000, revenue:90_000, variableCost:25_000, payroll:18_000, fixedCost:8_000, workers:2, capacity:1, productivity:1, quality:0.58, elasticity:0.72, necessity:0.88, price:1, wage:1, assets:320_000, debt:0, owner:'Polski właściciel', region:'Miasto', historical:false, sellerReserveRatio:0.85 },
      { id:'grocery', name:'Sklep Spożywczy', sector:'food', seller:'Rodzina właścicieli', ask:1_250_000, revenue:230_000, variableCost:105_000, payroll:34_000, fixedCost:25_000, workers:7, capacity:1, productivity:1, quality:0.64, elasticity:0.48, necessity:1, price:1, wage:1, assets:900_000, debt:0, owner:'Polski właściciel', region:'Miasto', historical:false, sellerReserveRatio:0.85 },
      { id:'workshop', name:'Warsztat Mechaniczny', sector:'services', seller:'Spółka pracownicza', ask:780_000, revenue:145_000, variableCost:54_000, payroll:29_000, fixedCost:13_000, workers:5, capacity:1, productivity:1, quality:0.70, elasticity:0.58, necessity:0.55, price:1, wage:1, assets:540_000, debt:0, owner:'Spółka pracownicza', region:'Miasto', historical:false, sellerReserveRatio:0.85 },
      { id:'bazaar', name:'Targowisko Centralne', sector:'wholesale', seller:'Zrzeszenie kupców', ask:980_000, revenue:190_000, variableCost:92_000, payroll:26_000, fixedCost:19_000, workers:9, capacity:1, productivity:1, quality:0.55, elasticity:0.92, necessity:0.42, price:1, wage:1, assets:650_000, debt:0, owner:'Niezależni kupcy', region:'Miasto', historical:false, sellerReserveRatio:0.85 }
    ].map(f => ({ ...f, receivableDays:f.sector==='wholesale'?35:f.sector==='services'?18:12, inventoryDays:f.sector==='wholesale'?42:f.sector==='food'?24:f.sector==='retail'?28:8, payableDays:f.sector==='wholesale'?30:f.sector==='food'?18:15 }))
  };
}

export function addEvent(state, text, kind='info') {
  state.events.unshift({ year:state.year, month:state.month, text, kind });
  state.events = state.events.slice(0, 40);
}
export function firmDemand(state, firm) {
  const hasControl = Boolean(state.owned[firm.id]?.control);
  const realPrice = firm.price * (hasControl ? state.pricePolicy : 1);
  const incomeFactor = Math.pow(Math.max(0.2, state.householdRealIncome / 100), 0.35);
  const priceFactor = Math.pow(Math.max(0.2, realPrice), -firm.elasticity);
  const qualityFactor = 0.8 + firm.quality * 0.35;
  return clamp(firm.revenue * priceFactor * incomeFactor * qualityFactor, 0, firm.revenue * 3);
}
export function firmWorkingCapital(firm, revenue=firm.revenue) {
  const dailyRevenue = Math.max(0, revenue) / 30;
  const receivables = dailyRevenue * (firm.receivableDays ?? 15);
  const inventory = dailyRevenue * (firm.inventoryDays ?? 20);
  const payables = dailyRevenue * (firm.payableDays ?? 15);
  return { receivables, inventory, payables, netWorkingCapital:Math.max(0,receivables+inventory-payables), cashConversionCycle:(firm.receivableDays??15)+(firm.inventoryDays??20)-(firm.payableDays??15) };
}
export function firmFinancials(state, firm) {
  const demandRevenue = firmDemand(state, firm);
  const capacityRevenue = firm.revenue * firm.capacity * firm.productivity * 1.5;
  const revenue = Math.min(demandRevenue, capacityRevenue);
  const utilization = clamp(revenue / Math.max(1, firm.revenue), 0, 1.5);
  const variableCost = firm.variableCost * utilization;
  const payroll = firm.payroll * firm.wage * (state.owned[firm.id]?.control ? state.wagePolicy : 1);
  const operatingProfit = revenue - variableCost - payroll - firm.fixedCost;
  const workingCapital = firmWorkingCapital(firm, revenue);
  const interest = firm.debt * state.baseRate / 12;
  const taxable = Math.max(0, operatingProfit - interest);
  const tax = taxable * state.taxRate;
  return { revenue, variableCost, payroll, fixedCost:firm.fixedCost, operatingProfit, interest, tax, ...workingCapital, netOperatingCash:operatingProfit-interest-tax };
}

/** Transparent DCF estimate; a game valuation aid, not a calibrated historical valuation. */
export function firmValuation(state, firmOrId, assumptions={}) {
  const firm = typeof firmOrId === 'string' ? state.firms.find(f=>f.id===firmOrId) : firmOrId;
  if (!firm) return null;
  const sectorRisk = { retail:0.08, food:0.09, services:0.10, wholesale:0.11 };
  const forecastYears = assumptions.forecastYears ?? 5;
  const growthRate = assumptions.growthRate ?? 0.03;
  const terminalGrowth = assumptions.terminalGrowth ?? 0.02;
  const maintenanceCapexRate = assumptions.maintenanceCapexRate ?? 0.04;
  const riskPremium = assumptions.riskPremium ?? sectorRisk[firm.sector] ?? 0.10;
  const discountRate = assumptions.discountRate ?? state.baseRate + riskPremium;
  if (!Number.isInteger(forecastYears)||forecastYears<1||forecastYears>20) throw new RangeError('Forecast horizon must be 1–20 years.');
  if (!(growthRate>-1&&growthRate<1)||!(terminalGrowth>=0&&terminalGrowth<1)) throw new RangeError('Invalid growth assumptions.');
  if (!(maintenanceCapexRate>=0&&maintenanceCapexRate<=1)) throw new RangeError('Invalid maintenance capex assumption.');
  if (!(discountRate>terminalGrowth&&discountRate<2)) throw new RangeError('Discount rate must exceed terminal growth.');
  const financials = firmFinancials(state, firm);
  const unleveredTax = Math.max(0,financials.operatingProfit)*state.taxRate;
  const monthlyMaintenanceCapex = Math.max(0,firm.assets)*maintenanceCapexRate/12;
  const baseAnnualFcf = (financials.operatingProfit-unleveredTax-monthlyMaintenanceCapex)*12;
  const baseNwc = financials.netWorkingCapital;
  const forecast=[]; let presentValue=0; let previousNwc=baseNwc;
  for(let year=1;year<=forecastYears;year++){
    const revenueScale=Math.pow(1+growthRate,year);
    const projectedNwc=baseNwc*revenueScale;
    const changeInWorkingCapital=projectedNwc-previousNwc;
    const cashFlow=baseAnnualFcf*revenueScale-changeInWorkingCapital*12;
    previousNwc=projectedNwc;
    const discounted=cashFlow/Math.pow(1+discountRate,year);
    forecast.push({year,cashFlow,discounted,changeInWorkingCapital}); presentValue+=discounted;
  }
  const finalCashFlow=forecast[forecast.length-1].cashFlow;
  const terminalValue=finalCashFlow*(1+terminalGrowth)/(discountRate-terminalGrowth);
  const discountedTerminalValue=terminalValue/Math.pow(1+discountRate,forecastYears);
  const enterpriseValue=presentValue+discountedTerminalValue;
  const equityValue=Math.max(0,enterpriseValue-Math.max(0,firm.debt||0));
  return { enterpriseValue,equityValue,annualFcf:forecast[0].cashFlow,baseAnnualFcf,baseNwc,monthlyMaintenanceCapex,discountRate,growthRate,terminalGrowth,maintenanceCapexRate,riskPremium,forecastYears,forecast,terminalValue,discountedTerminalValue,method:'five-year DCF using unlevered operating cash flow, maintenance capex and incremental working capital',calibration:'scenario-only; not a historical Polish valuation series' };
}
export function marketShares(state, sector=null) {
  const firms=state.firms.filter(f=>!sector||f.sector===sector);
  const sales=firms.map(f=>({id:f.id,sales:firmFinancials(state,f).revenue}));
  const total=sales.reduce((a,x)=>a+x.sales,0);
  return sales.map(x=>({...x,share:total?x.sales/total*100:0}));
}
export function hhi(state, sector=null) {
  return round2(marketShares(state,sector).reduce((sum,x)=>sum+x.share**2,0));
}
export function portfolio(state) {
  const positions=Object.entries(state.owned).map(([id,p])=>{
    const firm=state.firms.find(f=>f.id===id);
    return firm?{firm,stake:p.stake,control:p.control}:null;
  }).filter(Boolean);
  const financials=positions.map(({firm,stake})=>({firm,stake,...firmFinancials(state,firm)}));
  const revenue=financials.reduce((a,x)=>a+x.revenue*x.stake,0);
  const net=financials.reduce((a,x)=>a+x.netOperatingCash*x.stake,0);
  const jobs=positions.reduce((a,x)=>a+Math.round(x.firm.workers*x.stake),0);
  const netWorkingCapital=financials.reduce((a,x)=>a+x.netWorkingCapital*x.stake,0);
  return {positions,financials,revenue,net,jobs,netWorkingCapital};
}
export function acquire(state, firmId, {stake=1,debtShare=0,offerMultiplier=1}={}) {
  const firm=state.firms.find(f=>f.id===firmId);
  if(!firm)return{ok:false,reason:'Nie znaleziono przedsiębiorstwa.'};
  if(state.owned[firmId])return{ok:false,reason:'Masz już udział w tym przedsiębiorstwie.'};
  if(firm.historical)return{ok:false,reason:'Historyczne transakcje są tylko materiałem badawczym.'};
  if(!(stake>0&&stake<=1))return{ok:false,reason:'Udział musi mieścić się w zakresie 1–100%.'};
  if(!(debtShare>=0&&debtShare<=0.6))return{ok:false,reason:'Finansowanie dłużne w prototypie jest ograniczone do 60% ceny.'};
  if(!(Number.isFinite(offerMultiplier)&&offerMultiplier>=0.7&&offerMultiplier<=1.5))return{ok:false,reason:'Oferta musi mieścić się w zakresie 70–150% ceny wywoławczej.'};
  const sellerAsk=firm.ask*stake, price=sellerAsk*offerMultiplier, reserve=sellerAsk*(firm.sellerReserveRatio??0.85);
  if(price+1e-8<reserve)return{ok:false,reason:'Sprzedający odrzuca ofertę. Zaproponuj co najmniej cenę rezerwową.',counterOffer:reserve,sellerAsk};
  const valuation=firmValuation(state,firm), loan=price*debtShare, equity=price-loan;
  if(equity>state.cash)return{ok:false,reason:'Za mało gotówki na wkład własny.'};
  state.cash-=equity; state.debt+=loan;
  state.owned[firmId]={stake,control:stake>=0.5,acquiredYear:state.year,acquiredMonth:state.month,purchasePrice:price,sellerAsk,offerMultiplier,valuationEquityValue:valuation.equityValue,valuationStakeValue:valuation.equityValue*stake,valuationSnapshot:{enterpriseValue:valuation.enterpriseValue,equityValue:valuation.equityValue,discountRate:valuation.discountRate,growthRate:valuation.growthRate,terminalGrowth:valuation.terminalGrowth,maintenanceCapexRate:valuation.maintenanceCapexRate,riskPremium:valuation.riskPremium,forecastYears:valuation.forecastYears,annualFcf:valuation.annualFcf,method:valuation.method}};
  addEvent(state, `Nabyto ${(stake*100).toFixed(0)}% udziałów w ${firm.name}. Cena: ${money(price,state.currency)} (${(offerMultiplier*100).toFixed(0)}% ceny sprzedającego); szacunek DCF 100% kapitału: ${money(valuation.equityValue,state.currency)}; dług transakcyjny: ${money(loan,state.currency)}. Wartość DCF jest parametrem scenariusza, nie historyczną wyceną. Firma jest fikcyjna.`,'deal');
  return {ok:true,price,loan,equity,sellerAsk,reserve,offerMultiplier,valuation};
}
export function setPolicy(state,{pricePolicy=state.pricePolicy,wagePolicy=state.wagePolicy,investmentBudget=state.investmentBudget}={}) {
  state.pricePolicy=clamp(pricePolicy,0.7,1.8); state.wagePolicy=clamp(wagePolicy,0.65,1.5); state.investmentBudget=clamp(investmentBudget,0,500_000);
}
export function restructureOnePosition(state,firmId) {
  const firm=state.firms.find(f=>f.id===firmId);
  if(!firm||!state.owned[firmId]?.control)return{ok:false,reason:'Nie masz kontroli operacyjnej nad tym przedsiębiorstwem.'};
  if(firm.workers<=1)return{ok:false,reason:'Nie można zmniejszyć zatrudnienia poniżej jednej osoby.'};
  const severance=firm.payroll/Math.max(1,firm.workers)*2;
  if(state.cash<severance)return{ok:false,reason:'Brak gotówki na odprawę.'};
  state.cash-=severance; const previousWorkers=firm.workers;
  firm.workers-=1; firm.payroll*=firm.workers/previousWorkers; firm.capacity*=firm.workers/previousWorkers;
  firm.quality=clamp(firm.quality-0.035,0.1,1); state.trust=clamp(state.trust-3.5,0,100);
  state.householdRealIncome=clamp(state.householdRealIncome-0.8,20,130);
  addEvent(state,`Restrukturyzacja ${firm.name}: redukcja jednego etatu, odprawa ${money(severance,state.currency)}. Spadły zaufanie i lokalny dochód gospodarstw domowych.`,'labour');
  return{ok:true,severance};
}
export function advanceMonth(state) {
  const before=portfolio(state), openingWorkingCapital=before.netWorkingCapital;
  state.cash+=before.net-state.debt*state.baseRate/12;
  const controlledPositions=before.positions.filter(x=>x.control);
  const investmentPerFirm=controlledPositions.length?state.investmentBudget/controlledPositions.length:0;
  for(const {firm} of controlledPositions){
    const invest=Math.min(investmentPerFirm,Math.max(0,state.cash)); state.cash-=invest;
    firm.productivity=clamp(firm.productivity+invest/Math.max(100_000,firm.assets)*0.015,0.5,2.5);
    firm.quality=clamp(firm.quality+invest/Math.max(100_000,firm.assets)*0.008,0.1,1);
    firm.revenue*=1+(firm.productivity-1)*0.002;
  }
  for(const firm of state.firms){
    firm.ask*=1+state.monthlyInflation*0.12; firm.revenue*=1+state.monthlyInflation*0.08;
    firm.variableCost*=1+state.monthlyInflation*0.1; firm.payroll*=1+state.monthlyInflation*0.06;
  }
  state.consumerPriceIndex*=1+state.monthlyInflation;
  const closingWorkingCapital=portfolio(state).netWorkingCapital;
  const workingCapitalInvestment=closingWorkingCapital-openingWorkingCapital;
  state.cash-=workingCapitalInvestment;
  state.householdRealIncome=clamp(state.householdRealIncome+(state.wagePolicy-1)*0.25-(state.pricePolicy-1)*0.55,20,140);
  state.trust=clamp(state.trust-Math.max(0,state.pricePolicy-1)*1.8+Math.max(0,state.wagePolicy-1)*0.7,0,100);
  state.month+=1;
  if(state.month===12){state.month=0;state.year+=1;state.monthlyInflation=Math.max(0.015,state.monthlyInflation*0.82);addEvent(state,'Roczny przegląd: scenariuszowa presja inflacyjna spada. Wartości pozostają nominalne; model nie jest jeszcze skalibrowany do historycznych szeregów GUS/NBP.','macro');}
  if(state.year===1995&&state.month===0&&state.currency==='PLZ'){
    state.cash/=10_000; state.debt/=10_000;
    for(const f of state.firms){f.ask/=10_000;f.revenue/=10_000;f.variableCost/=10_000;f.payroll/=10_000;f.fixedCost/=10_000;f.assets/=10_000;f.debt/=10_000;}
    state.currency='PLN'; addEvent(state,'Denominacja: 10 000 starych złotych = 1 nowy złoty. Przeliczono nominały bez zmiany realnego majątku.','history');
  }
  return {...portfolio(state),workingCapitalInvestment,hhiOverall:hhi(state),monthLabel:MONTHS[state.month],year:state.year};
}
export function money(value,currency='PLZ'){return `${Math.round(value).toLocaleString('pl-PL')} ${currency}`;}
export function serialize(state){return JSON.stringify(state);}
export function deserialize(raw){
  const parsed=JSON.parse(raw);
  if(!Array.isArray(parsed.firms)||typeof parsed.owned!=='object')throw new Error('Nieobsługiwana lub uszkodzona wersja zapisu.');
  if(parsed.modelVersion==='0.2.0'){parsed.migrations??=[];for(const firm of parsed.firms)firm.sellerReserveRatio??=0.85;parsed.modelVersion='0.3.0';parsed.migrations.push('0.2.0-to-0.3.0: seller reserve ratio and DCF negotiation fields');}
  if(parsed.modelVersion==='0.3.0'){parsed.migrations??=[];for(const firm of parsed.firms){firm.receivableDays??=firm.sector==='wholesale'?35:firm.sector==='services'?18:12;firm.inventoryDays??=firm.sector==='wholesale'?42:firm.sector==='food'?24:firm.sector==='retail'?28:8;firm.payableDays??=firm.sector==='wholesale'?30:firm.sector==='food'?18:15;}parsed.modelVersion=MODEL_VERSION;parsed.migrations.push('0.3.0-to-0.4.0: sector working-capital operating assumptions');}
  if(parsed.modelVersion!==MODEL_VERSION)throw new Error('Nieobsługiwana lub uszkodzona wersja zapisu.');
  return parsed;
}
