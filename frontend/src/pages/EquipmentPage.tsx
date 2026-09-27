import {useEffect, useState} from 'react';
import {Link, NavLink} from 'react-router-dom';
import {ArrowLeft, ArrowUpRight, CarFront, Crosshair, FolderOpen, ShieldCheck} from 'lucide-react';
import {fetchAllEntities} from '../lib/catalog';
import {SearchResult} from '../types';
import {EntityCard} from '../components/EntityCard';
import {Button} from '../components/ui/button';
import '../styles/equipment.css';

type EquipmentKind = 'armas' | 'veiculos';
const sections = {
  armas:{title:'Armas',label:'EQUIPAMENTO',description:'Armas documentadas no pacote pré-lançamento, com confirmação, desenvolvimento e incerteza editorial sempre separados.',emptyTitle:'O arsenal ainda está por documentar.',emptyDescription:'Ainda não há armas publicadas nesta página.',icon:Crosshair,index:'01',entityType:'arma'},
  veiculos:{title:'Veículos',label:'MOBILIDADE',description:'Base de veículos pré-lançamento, incluindo classes, referências de design e campos técnicos apenas quando o dossiê os fornece.',emptyTitle:'A garagem ainda está vazia.',emptyDescription:'Ainda não há veículos publicados nesta página.',icon:CarFront,index:'02',entityType:'veiculo'},
};
export default function EquipmentPage({kind}:{kind:EquipmentKind}) {
  const section=sections[kind], Icon=section.icon;
  const [data,setData]=useState<SearchResult|null>(null),[error,setError]=useState('');
  useEffect(()=>{let active=true;setData(null);setError('');fetchAllEntities(section.entityType).then(result=>active&&setData(result)).catch(err=>active&&setError(err.message));return()=>{active=false;};},[section.entityType]);
  return <div className="page-content equipment-page page-enter" data-catalog-kind={kind} data-testid={`${kind}-page`}>
    <Link to="/" className="equipment-back"><ArrowLeft size={14}/> Voltar a explorar</Link>
    <header className="page-heading equipment-heading"><div><span className="eyebrow">O ARQUIVO / {section.label}</span><h1>{section.title}<span className="equipment-title-dot">.</span></h1><p>{section.description}</p></div><div className="equipment-heading-mark" aria-hidden="true"><Icon size={35} strokeWidth={1.1}/><span>CATÁLOGO / {section.index}</span></div></header>
    <div className="equipment-toolbar"><nav className="equipment-navigation" aria-label="Catálogos do arquivo"><NavLink to="/armas" className={({isActive})=>isActive?'active':''}><Crosshair size={15}/>Armas</NavLink><NavLink to="/veiculos" className={({isActive})=>isActive?'active':''}><CarFront size={16}/>Veículos</NavLink></nav><span className="equipment-status"><span/>{data?`${data.total} REGISTOS PUBLICADOS`:'A CONSULTAR O ARQUIVO'}</span></div>
    {error?<div className="error-state" role="alert">{error}</div>:!data?<div className="skeleton detail-skeleton"/>:data.items.length?<section className="equipment-catalog"><div className="equipment-catalog-note"><ShieldCheck size={18}/><p><strong>Proveniência primeiro.</strong> O estado editorial de cada entrada é preservado; Development e Unknown nunca são apresentados como confirmação final.</p></div><div className="entity-grid">{data.items.map(entity=><EntityCard entity={entity} key={entity.id}/>)}</div></section>:<section className="equipment-empty"><div className="equipment-emblem"><Icon size={43}/></div><h2>{section.emptyTitle}</h2><p>{section.emptyDescription}</p><Button asChild variant="outline"><Link to="/encontrar"><FolderOpen size={16}/>Explorar o arquivo<ArrowUpRight size={16}/></Link></Button></section>}
  </div>;
}
