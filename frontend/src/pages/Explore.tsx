import {useEffect, useState} from 'react';
import {Link, useNavigate} from 'react-router-dom';
import {Search, ArrowUpRight, ArrowRight, ShieldCheck, UsersRound, MapPin, Car, Crosshair, Layers3, ChevronRight, Radio, FileText} from 'lucide-react';
import {api} from '../lib/api';
import {Entity} from '../types';
import {EntityCard} from '../components/EntityCard';
const categories = [{id:'personagem',name:'Personagens',icon:UsersRound,color:'pink'},{id:'local',name:'Locais e regiões',icon:MapPin,color:'cyan'},{id:'veiculo',name:'Veículos',icon:Car,color:'amber'},{id:'sistema',name:'Sistemas de jogo',icon:Layers3,color:'green'}];
export default function Explore(){
  const [featured,setFeatured]=useState<Entity[]>([]);
  const [stats,setStats]=useState<any>(null);
  const [error,setError]=useState('');
  const [query,setQuery]=useState('');
  const navigate=useNavigate();
  useEffect(()=>{Promise.all([api<Entity[]>('/featured'),api('/stats')]).then(([items,counts])=>{setFeatured(items);setStats(counts);}).catch(e=>setError(e.message));},[]);
  return <div className="explore-page page-enter">
    <section className="explore-hero" aria-labelledby="explore-title">
      <img className="hero-image" src="/media/hero-city.webp" alt="Vista oficial de Vice City em Grand Theft Auto VI" fetchPriority="high"/>
      <div className="hero-shade"/>
      <div className="hero-content"><span className="eyebrow"><span className="status-dot"/> O ARQUIVO INDEPENDENTE DE GTA VI</span>
        <h1 id="explore-title" data-testid="explore-title">Todo um mundo.<br/><span>Cada detalhe conta.</span></h1>
        <p data-testid="explore-intro">Pessoas, lugares e histórias de Leonida.<br/>O que sabemos. De onde sabemos.</p>
        <form className="hero-search" onSubmit={e=>{e.preventDefault();navigate(`/encontrar?q=${encodeURIComponent(query)}`);}}>
          <Search size={21}/><input data-testid="hero-search-input" aria-label="O que procura em Leonida?" placeholder="O que procura em Leonida?" value={query} onChange={e=>setQuery(e.target.value)}/><button type="submit" data-testid="hero-search-submit" aria-label="Pesquisar"><ArrowRight size={21}/></button>
        </form>
        <div className="quick-searches"><span>COMECE POR</span>{['Lucia Caminos','Vice City','Leonida Keys'].map(name=><Link key={name} to={`/encontrar?q=${encodeURIComponent(name)}`} data-testid={`quick-${name.toLowerCase().replaceAll(' ','-')}`}>{name}<ArrowUpRight size={11}/></Link>)}</div>
      </div>
      <div className="hero-location"><MapPin size={14}/><span>VICE CITY, LEONIDA</span><span className="image-credit">IMAGEM OFICIAL · ROCKSTAR GAMES</span></div>
      <span className="hero-index">01 / THE LEONIDA FILES</span>
    </section>
    <div className="knowledge-strip"><div><ShieldCheck size={17}/><span>Conhecimento com origem.</span><Link to="/metodologia" data-testid="trust-method">Factos com fontes, não suposições.<ArrowUpRight size={13}/></Link></div><span data-testid="archive-count">{stats?`${stats.entities} entidades · ${stats.assertions} afirmações documentadas`:'A consultar o arquivo…'}</span></div>
    <div className="explore-body">
      <section className="categories-section"><div className="section-heading"><div><span className="section-kicker">UM ESTADO. MUITAS HISTÓRIAS.</span><h2 data-testid="categories-title">Entre no universo de Leonida</h2></div><Link to="/encontrar" data-testid="all-categories-link">Explorar o arquivo <ArrowUpRight size={16}/></Link></div>
        <div className="category-grid">{categories.map(({id,name,icon:Icon,color})=><Link to={`/encontrar?tipo=${id}`} className={`category-item ${color}`} key={id} data-testid={`category-${id}`}><span className="category-icon"><Icon size={24} strokeWidth={1.5}/></span><div><h3>{name}</h3><span>{stats?.types?.[id]?`${stats.types[id]} entidades no arquivo`:'À espera de evidência'}</span></div><ChevronRight size={17}/></Link>)}</div>
      </section>
      <section className="featured-section"><div className="section-heading"><div><span className="section-kicker"><span className="pink-dash"/> O ESSENCIAL, PARA COMEÇAR</span><h2 data-testid="featured-title">Em destaque no arquivo</h2></div><Link to="/encontrar" data-testid="see-all-entities">Ver todas as entidades <ArrowUpRight size={16}/></Link></div>
        {error?<div role="alert" className="error-state" data-testid="home-error">{error}<button onClick={()=>window.location.reload()} data-testid="home-retry">Tentar novamente</button></div>:<div className="entity-grid">{featured.length?featured.map(item=><EntityCard key={item.id} entity={item}/>):Array.from({length:4},(_,i)=><div key={i} className="skeleton entity-skeleton"/>)}</div>}
      </section>
      <section className="bottom-editorial"><div className="editorial-spotlight"><span className="section-kicker"><Radio size={13}/> HISTÓRIA REAL, SEM CONFUNDIR UNIVERSOS</span><h2>A caminho de Leonida.</h2><p>Os trailers e os anúncios que construíram a história de Grand Theft Auto VI.</p><Link to="/acompanhar" className="text-link" data-testid="explore-timeline">Percorrer a cronologia <ArrowRight size={16}/></Link></div><div className="editorial-principle"><FileText size={27}/><div><h3>Uma afirmação. A sua evidência.</h3><p>Oficial não significa imutável. A origem e a verificação são coisas diferentes.</p><Link to="/metodologia" data-testid="explore-evidence-method">Conhecer os critérios editoriais <ArrowUpRight size={14}/></Link></div></div></section>
    </div>
  </div>;
}