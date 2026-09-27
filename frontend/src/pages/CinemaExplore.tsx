import {useEffect, useRef, useState} from 'react';
import {Link, useNavigate} from 'react-router-dom';
import {ArrowRight, ArrowUpRight, Bookmark, Compass, Fingerprint, MapPin, Radio, Search, ShieldCheck, UsersRound, CarFront, Layers3} from 'lucide-react';
import {motion, useReducedMotion} from 'framer-motion';
import {api} from '../lib/api';
import {assetUrl} from '../lib/assets';
import {OFFLINE} from '../lib/offline';
import {Entity} from '../types';
import {EntityCard} from '../components/EntityCard';

type ArchiveStats = {entities: number; assertions: number; sources: number; types: Record<string, number>};
const categories = [
  {id: 'personagem', name: 'Personagens', icon: UsersRound, tone: 'pink', to: '/encontrar?tipo=personagem'},
  {id: 'local', name: 'Locais', icon: MapPin, tone: 'cyan', to: '/encontrar?tipo=local'},
  {id: 'veiculo', name: 'Veículos', icon: CarFront, tone: 'amber', to: '/veiculos'},
  {id: 'sistema', name: 'Sistemas', icon: Layers3, tone: 'lilac', to: '/encontrar?tipo=sistema'},
];

export default function CinemaExplore() {
  const [featured, setFeatured] = useState<Entity[]>([]);
  const [stats, setStats] = useState<ArchiveStats | null>(null);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const reducedMotion = useReducedMotion();
  const posterTrack = useRef<HTMLDivElement>(null);
  const [posterIndex, setPosterIndex] = useState(0);
  const movePoster = (direction: number) => {
    const track = posterTrack.current;
    const target = track?.children[Math.max(0, Math.min(featured.length - 1, posterIndex + direction))] as HTMLElement | undefined;
    if (track && target) track.scrollTo({left: track.scrollLeft + target.getBoundingClientRect().left - track.getBoundingClientRect().left - 1, behavior: reducedMotion ? 'auto' : 'smooth'});
  };

  useEffect(() => {
    let active = true;
    Promise.all([api<Entity[]>('/featured'), api<ArchiveStats>('/stats')])
      .then(([items, counts]) => {if (active) {setFeatured(items); setStats(counts);}})
      .catch(error => active && setError(error.message));
    return () => {active = false;};
  }, []);

  return <div className="cinema-home">
    <div className="cinema-masthead"><span><Compass size={14}/> UM UNIVERSO PARA DESCOBRIR</span><span>INDEPENDENTE. POR PRINCÍPIO.</span></div>
    <section className="cinema-cover" aria-labelledby="explore-title">
      <img className="cinema-cover-art" src={assetUrl('/media/hero-keyart.webp')} alt="Arte oficial de Jason e Lucia em Leonida, Grand Theft Auto VI" fetchPriority="high"/>
      <div className="cinema-cover-shade"/>
      <div className="cinema-cover-top"><span className="cinema-edition" data-testid="hero-edition"><span/> THE LEONIDA FILES</span><span data-testid="hero-game-label">GRAND THEFT AUTO VI</span></div>
      <motion.div className="cinema-cover-copy" initial={reducedMotion ? false : {opacity: 0, y: 12}} animate={{opacity: 1, y: 0}} transition={{duration: 0.5, ease: 'easeOut'}}>
        <p className="cinema-overline" data-testid="hero-eyebrow">O ARQUIVO INDEPENDENTE DE GTA VI</p>
        <h1 id="explore-title" data-testid="explore-title">LEONIDA.<br/><span>MAIS DE PERTO.</span></h1>
        <p className="cinema-cover-description" data-testid="explore-intro">Por trás de cada nome, uma história.<br/>Por trás de cada detalhe, uma fonte.</p>
        <Link to="/encontrar" className="cinema-primary" data-testid="hero-explore">Descobrir o arquivo <span><ArrowUpRight size={19}/></span></Link>
      </motion.div>
      <Link to="/entidade/jason-duval" className="cinema-focus-card" data-testid="hero-featured-dossier">
        <img src={assetUrl('/media/jason.webp')} alt=""/><div><span>DOSSIÊ EM FOCO</span><strong>Jason Duval</strong></div><ArrowUpRight size={20}/>
      </Link>
      <span className="cinema-art-credit" data-testid="hero-artwork-credit">ARTE OFICIAL · ROCKSTAR GAMES</span>
    </section>

    <section className="discovery-console" aria-label="Pesquisar e explorar o arquivo">
      <form className="discovery-search" role="search" onSubmit={event => {event.preventDefault(); navigate(`/encontrar?q=${encodeURIComponent(query)}`);}}>
        <Search size={22} aria-hidden="true"/><div><label htmlFor="discovery-query">A SUA PRÓXIMA DESCOBERTA</label><input id="discovery-query" data-testid="hero-search-input" maxLength={100} placeholder="O que procura em Leonida?" value={query} onChange={event => setQuery(event.target.value)}/></div>
        <button type="submit" data-testid="hero-search-submit" aria-label="Pesquisar no arquivo"><ArrowRight size={22}/></button>
      </form>
      <div className="discovery-suggestions"><span>COMECE POR</span>{['Lucia Caminos', 'Vice City', 'Leonida Keys'].map(name => <Link key={name} to={`/encontrar?q=${encodeURIComponent(name)}`} data-testid={`quick-${name.toLowerCase().replaceAll(' ', '-')}`}>{name}<ArrowUpRight size={12}/></Link>)}</div>
    </section>

    <div className="cinema-proof-strip">
      <Link to="/metodologia" data-testid="trust-method"><ShieldCheck size={17}/><span>Menos ruído. <strong>Mais evidência.</strong></span><ArrowUpRight size={13}/></Link>
      <span data-testid="archive-count">{stats ? <><b>{stats.entities}</b> dossiês<span className="cinema-dot"/><b>{stats.assertions}</b> afirmações documentadas</> : 'A abrir o arquivo…'}</span>
    </div>

    <section className="cinema-categories" aria-labelledby="categories-title">
      <div className="cinema-section-heading"><div><span className="cinema-overline">ESCOLHA UMA DIREÇÃO</span><h2 id="categories-title" data-testid="categories-title">Siga a sua curiosidade.</h2></div><Link to="/encontrar" className="cinema-round-link" aria-label="Ver todas as categorias" data-testid="all-categories-link"><ArrowUpRight size={21}/></Link></div>
      <div className="cinema-category-grid">{categories.map(({id, name, icon: Icon, tone, to}) => <Link key={id} to={to} className={`cinema-category tone-${tone}`} data-testid={`category-${id}`}>
        <span className="cinema-category-icon"><Icon size={23} strokeWidth={1.5}/></span><div><h3>{name}</h3><span data-testid={`category-count-${id}`}>{!stats ? 'A consultar…' : typeof stats.types[id] === 'number' ? `${String(stats.types[id]).padStart(2, '0')} dossiês` : 'Por documentar'}</span></div><ArrowUpRight size={16}/>
      </Link>)}</div>
    </section>

    <section className="cinema-featured" aria-labelledby="featured-title">
      <div className="cinema-section-heading"><div><span className="cinema-overline"><span className="cinema-section-index">01</span> A PORTA DE ENTRADA</span><h2 id="featured-title" data-testid="featured-title">Tudo começa com uma história.</h2></div><Link to="/encontrar" className="cinema-text-link" data-testid="see-all-entities">Todos os dossiês <ArrowUpRight size={17}/></Link></div>
      {error ? <div role="alert" className="error-state" data-testid="home-error">{error}<button onClick={() => window.location.reload()} data-testid="home-retry">Tentar novamente</button></div> : <div className="cinema-poster-track" id="featured-dossiers" ref={posterTrack} role="region" aria-label="Dossiês em destaque" onScroll={() => {const track = posterTrack.current; const first = track?.firstElementChild as HTMLElement | null; if (track && first) setPosterIndex(Math.min(featured.length - 1, Math.max(0, Math.round(track.scrollLeft / (first.offsetWidth + parseFloat(getComputedStyle(track).columnGap || '0'))))));}}>{featured.length ? featured.map((entity, index) => <div className="cinema-poster-slot" key={entity.id}><EntityCard entity={entity} poster/><span className="cinema-poster-index"><span>0{index + 1}</span><span>{entity.type === 'personagem' ? 'AS PESSOAS DE LEONIDA' : 'OS LUGARES DE LEONIDA'}</span></span></div>) : Array.from({length: 4}, (_, i) => <div key={i} className="skeleton cinema-poster-skeleton"/>)}</div>}
      {!!featured.length && <div className="cinema-carousel-controls"><span aria-live="polite" aria-atomic="true"><b>{String(posterIndex + 1).padStart(2, '0')}</b> / {String(featured.length).padStart(2, '0')}</span><div><button type="button" aria-label="Dossiê anterior" aria-controls="featured-dossiers" data-testid="poster-previous" disabled={posterIndex === 0} onClick={() => movePoster(-1)}><ArrowRight size={17} className="previous-arrow"/></button><button type="button" aria-label="Dossiê seguinte" aria-controls="featured-dossiers" data-testid="poster-next" disabled={posterIndex >= featured.length - 1} onClick={() => movePoster(1)}><ArrowRight size={17}/></button></div></div>}
    </section>

    <section className="cinema-world" aria-labelledby="world-title">
      <div className="cinema-section-heading"><div><span className="cinema-overline"><span className="cinema-section-index">02</span> PARA LÁ DO HORIZONTE</span><h2 id="world-title" data-testid="world-title">Nem tudo acontece na cidade.</h2></div><Link to="/encontrar?tipo=local" className="cinema-text-link" data-testid="world-all-locations">Explorar locais <ArrowUpRight size={17}/></Link></div>
      <Link className="cinema-landscape" to="/entidade/leonida-keys" data-testid="world-open-keys">
        <img src={assetUrl('/media/keys.webp')} loading="lazy" alt="Ilhas e pontes de Leonida Keys, imagem oficial da Rockstar Games"/>
        <div className="cinema-landscape-shade"/><span className="cinema-place-tag"><MapPin size={14}/> LEONIDA KEYS</span>
        <div className="cinema-landscape-copy"><p data-testid="world-feature-heading">O OUTRO LADO<br/><span>DO PARAÍSO.</span></p><span>Abrir o dossiê <ArrowUpRight size={19}/></span></div><span className="cinema-landscape-note">NENHUM LUGAR É SÓ UM CENÁRIO.</span>
      </Link>
      <div className="cinema-location-list">{[{slug:'vice-city', name:'Vice City', image:'vice-city', label:'AS LUZES DA CIDADE'}, {slug:'grassrivers', name:'Grassrivers', image:'grassrivers', label:'PARA LÁ DO ASFALTO'}, {slug:'port-gellhorn', name:'Port Gellhorn', image:'port', label:'OUTRO LADO DE LEONIDA'}].map((place, index) => <Link key={place.slug} to={`/entidade/${place.slug}`} data-testid={`world-location-${place.slug}`}><img src={assetUrl(`/media/${place.image}.webp`)} alt="" loading="lazy"/><div><span>{place.label}</span><h3>{place.name}</h3></div><span className="cinema-location-number">0{index + 1}</span><ArrowUpRight size={20}/></Link>)}</div>
    </section>

    <section className="cinema-closing" aria-label="Continue a descobrir">
      <Link to="/acompanhar" className="cinema-timeline-card" data-testid="explore-timeline"><img src={assetUrl('/media/hero-duo.webp')} alt="" loading="lazy"/><div><span className="cinema-overline"><Radio size={14}/> OS MARCOS DO ARQUIVO</span><h2>A HISTÓRIA<br/>ATÉ AQUI.</h2><span className="cinema-closing-link">Percorrer a cronologia <ArrowUpRight size={18}/></span></div></Link>
      <div className="cinema-manifesto"><Fingerprint size={42} strokeWidth={1}/><span className="cinema-overline">A NOSSA ASSINATURA</span><h2>O detalhe importa.<br/><span>A origem também.</span></h2><p>Uma fonte oficial não é uma verificação independente. Aqui, essa diferença nunca fica nas entrelinhas.</p><Link to="/metodologia" className="cinema-text-link" data-testid="explore-evidence-method">O nosso compromisso <ArrowUpRight size={17}/></Link></div>
    </section>
    <Link to={OFFLINE ? '/redacao' : '/guardar'} className="cinema-pocket-note" data-testid="home-pocket-note"><Bookmark size={18}/><span>{OFFLINE ? 'O seu arquivo. Mesmo longe da rede.' : 'As suas descobertas merecem ficar guardadas.'}</span><ArrowUpRight size={16}/></Link>
  </div>;
}
