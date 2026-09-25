import {useEffect, useState} from 'react';
import {Link, useSearchParams} from 'react-router-dom';
import {Search, SlidersHorizontal, X, ArrowUpRight, LayoutGrid, List, ChevronDown, SearchX} from 'lucide-react';
import {api} from '../lib/api';
import {Entity, SearchResult, typeNames} from '../types';
import {EntityCard} from '../components/EntityCard';
import {Button} from '../components/ui/button';
export default function Find(){
  const [params,setParams]=useSearchParams();
  const q=params.get('q')||'', type=params.get('tipo')||'', label=params.get('origem')||'';
  const [text,setText]=useState(q);
  const [data,setData]=useState<SearchResult|null>(null);
  const [busy,setBusy]=useState(true), [error,setError]=useState(''), [list,setList]=useState(false);
  const update=(key:string,value:string)=>{const next=new URLSearchParams(params);value?next.set(key,value):next.delete(key);setParams(next);};
  useEffect(()=>{setText(q);setBusy(true);setError('');let alive=true;api<SearchResult>(`/entities?q=${encodeURIComponent(q)}&type=${type}&label=${label}&limit=12`).then(v=>{if(alive)setData(v);}).catch(e=>alive&&setError(e.message)).finally(()=>alive&&setBusy(false));return()=>{alive=false;};},[q,type,label]);
  const more=async()=>{try{setBusy(true);const next=await api<SearchResult>(`/entities?q=${encodeURIComponent(q)}&type=${type}&label=${label}&cursor=${data?.next_cursor}&limit=12`);setData(v=>({...next,items:[...(v?.items||[]),...next.items]}));}catch(e:any){setError(e.message);}finally{setBusy(false);}};
  return <div className="page-content page-enter">
    <header className="page-heading"><span className="eyebrow">ENCONTRAR / BASE DE CONHECIMENTO</span><h1 data-testid="find-title">A resposta começa aqui.</h1><p>Um arquivo de pessoas, lugares e ligações. Sempre com uma fonte.</p></header>
    <form className="large-search" onSubmit={e=>{e.preventDefault();update('q',text);}}><Search size={23}/><input data-testid="find-search-input" placeholder="Pesquisar nomes, locais ou palavras-chave…" value={text} onChange={e=>setText(e.target.value)} aria-label="Pesquisar entidades"/>{text&&<button type="button" data-testid="clear-search" aria-label="Limpar pesquisa" onClick={()=>{setText('');update('q','');}}><X size={18}/></button>}<Button data-testid="find-search-submit" type="submit" className="primary-button">Pesquisar <ArrowUpRight size={16}/></Button></form>
    <div className="filter-bar"><div className="filter-tabs" aria-label="Tipo de entidade"><button className={!type?'selected':''} data-testid="filter-all" onClick={()=>update('tipo','')}>Todas</button>{Object.entries(typeNames).map(([id,name])=><button key={id} className={type===id?'selected':''} data-testid={`filter-${id}`} onClick={()=>update('tipo',id)}>{name}</button>)}</div><label className="origin-filter"><SlidersHorizontal size={15}/><select value={label} onChange={e=>update('origem',e.target.value)} data-testid="origin-filter" aria-label="Filtrar por origem"><option value="">Todas as origens</option><option value="Official">Oficial</option><option value="Datamined">Datamining</option><option value="Rumour">Rumor</option><option value="Reported">Reportado</option></select></label></div>
    <div className="result-toolbar"><span data-testid="search-result-count" aria-live="polite">{busy&&!data?'A pesquisar…':`${data?.total||0} entidades`}{q&&<> para <b>“{q}”</b></>}</span><div className="view-toggle"><button aria-label="Vista de grelha" aria-pressed={!list} data-testid="grid-view" className={!list?'selected':''} onClick={()=>setList(false)}><LayoutGrid size={17}/></button><button aria-label="Vista de lista" aria-pressed={list} data-testid="list-view" className={list?'selected':''} onClick={()=>setList(true)}><List size={18}/></button></div></div>
    {data?.suggestion&&<p className="suggestion" data-testid="search-suggestion">Resultados aproximados para <strong>{data.suggestion}</strong>.</p>}
    {error&&<p className="error-state" role="alert" data-testid="find-error">{error}</p>}
    {busy&&!data?<div className="entity-grid">{[0,1,2,3].map(i=><div className="skeleton entity-skeleton" key={i}/>)}</div>:data?.items.length?<div className={`entity-grid search-grid ${list?'list-view':''}`}>{data.items.map(entity=><EntityCard entity={entity} key={entity.id}/>)}</div>:<div className="empty-state" data-testid="search-empty"><SearchX size={40}/><h2>{type==='veiculo'||type==='sistema'?'Ainda sem registos publicados.':'Nenhuma entidade encontrada.'}</h2><p>{type==='veiculo'||type==='sistema'?'Esta categoria só recebe dados acompanhados de evidência. Não preenchemos o desconhecido com suposições.':'Experimente outro nome ou retire os filtros da pesquisa.'}</p><Button variant="outline" data-testid="reset-filters" onClick={()=>setParams({})}>Ver todo o arquivo <ArrowUpRight size={16}/></Button></div>}
    {data?.next_cursor&&<div className="load-more"><Button variant="outline" data-testid="load-more" onClick={more} disabled={busy}>{busy?'A carregar…':'Carregar mais'}<ChevronDown size={15}/></Button></div>}
  </div>;
}