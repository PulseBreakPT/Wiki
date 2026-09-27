import {useEffect, useState} from 'react';
import {Link, useNavigate} from 'react-router-dom';
import {Search, ArrowUpRight, ArrowRight, ShieldCheck, UsersRound, MapPin, Car, Layers3, Radio, ScanLine, Asterisk} from 'lucide-react';
import {motion, useReducedMotion} from 'framer-motion';
import {api} from '../lib/api';
import {assetUrl} from '../lib/assets';
import {Entity} from '../types';
import {EntityCard} from '../components/EntityCard';

type ArchiveStats = {entities: number; assertions: number; sources: number; types: Record<string, number>};
const categories = [
  {id: 'personagem', name: 'Personagens', icon: UsersRound, color: 'pink'},
  {id: 'local', name: 'Locais e regiões', icon: MapPin, color: 'cyan'},
  {id: 'veiculo', name: 'Veículos', icon: Car, color: 'amber'},
  {id: 'sistema', name: 'Sistemas de jogo', icon: Layers3, color: 'green'},
];

export default function Explore() {
  const [featured, setFeatured] = useState<Entity[]>([]);
  const [stats, setStats] = useState<ArchiveStats | null>(null);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    let active = true;
    Promise.all([api<Entity[]>('/featured'), api<ArchiveStats>('/stats')])
      .then(([items, counts]) => {if (active) {setFeatured(items); setStats(counts);}})
      .catch(error => active && setError(error.message));
    return () => {active = false;};
  }, []);

  return (
    <div className="explore-page">
      <section className="explore-hero" aria-labelledby="explore-title">
        <img className="hero-image" src={assetUrl('/media/hero-keyart.webp')} alt="Arte oficial de Jason e Lucia em Leonida, Grand Theft Auto VI" fetchPriority="high"/>
        <div className="hero-shade"/>
        <div className="hero-topline"><span data-testid="hero-edition"><span className="status-dot"/> THE LEONIDA FILES</span><span className="hero-index" data-testid="hero-game-label">GRAND THEFT AUTO VI</span></div>
        <motion.div className="hero-content" initial={reducedMotion ? false : {opacity: 0, y: 16}} animate={{opacity: 1, y: 0}} transition={{duration: 0.65, ease: 'easeOut'}}>
          <span className="eyebrow" data-testid="hero-eyebrow"><span className="hero-label-line"/> UM ARQUIVO INDEPENDENTE. UM UNIVERSO INTEIRO.</span>
          <h1 id="explore-title" data-testid="explore-title">LEONIDA.<br/><span>EM ARQUIVO.</span></h1>
          <p data-testid="explore-intro">Por trás de cada nome, uma história.<br/>Por trás de cada detalhe, uma fonte.</p>
          <form className="hero-search" role="search" onSubmit={event => {event.preventDefault(); navigate(`/encontrar?q=${encodeURIComponent(query)}`);}}>
            <Search size={21}/><input data-testid="hero-search-input" maxLength={100} aria-label="O que procura em Leonida?" placeholder="O que procura em Leonida?" value={query} onChange={event => setQuery(event.target.value)}/>
            <button type="submit" data-testid="hero-search-submit" aria-label="Pesquisar"><ArrowRight size={22}/></button>
          </form>
          <div className="quick-searches"><span>COMECE POR</span>{['Lucia Caminos', 'Vice City', 'Leonida Keys'].map(name => <Link key={name} to={`/encontrar?q=${encodeURIComponent(name)}`} data-testid={`quick-${name.toLowerCase().replaceAll(' ', '-')}`}>{name}<ArrowUpRight size={12}/></Link>)}</div>
        </motion.div>
        <Link to="/entidade/jason-duval" className="hero-dossier" data-testid="hero-featured-dossier"><span className="hero-dossier-index">01 / EM DESTAQUE</span><span className="hero-dossier-title">O homem por trás<br/>do nome.</span><span className="hero-dossier-link">Conhecer Jason Duval <ArrowUpRight size={18}/></span></Link>
        <div className="hero-caption"><span className="hero-caption-cross" aria-hidden="true">+</span><div><span data-testid="hero-artwork-name">JASON & LUCIA</span><span className="image-credit" data-testid="hero-artwork-credit">ARTE OFICIAL / ROCKSTAR GAMES</span></div></div>
      </section>

      <div className="knowledge-strip">
        <Link to="/metodologia" data-testid="trust-method"><ShieldCheck size={18}/><span>Conhecimento com origem.</span><span className="trust-description">Não confunda factos com suposições.</span><ArrowUpRight size={14}/></Link>
        <span data-testid="archive-count"><span className="status-dot"/>{stats ? <><b>{stats.entities}</b> entidades <span className="strip-divider">/</span> <b>{stats.assertions}</b> afirmações documentadas</> : 'A consultar o arquivo…'}</span>
      </div>

      <div className="explore-body">
        <section className="categories-section" aria-labelledby="categories-title">
          <div className="section-heading category-heading"><h2 id="categories-title" data-testid="categories-title">Escolha o seu ponto de partida.</h2><Link to="/encontrar" data-testid="all-categories-link">Todo o arquivo<ArrowUpRight size={16}/></Link></div>
          <div className="category-grid">
            {categories.map(({id, name, icon: Icon, color}) => (
              <Link to={id === 'veiculo' ? '/veiculos' : `/encontrar?tipo=${id}`} className={`category-item tone-${color}`} key={id} data-testid={`category-${id}`}>
                <span className="category-icon"><Icon size={25} strokeWidth={1.5}/></span>
                <div><h3>{name}</h3><span data-testid={`category-count-${id}`}>{!stats ? 'A consultar o arquivo…' : typeof stats.types[id] === 'number' ? `${String(stats.types[id]).padStart(2, '0')} entidades documentadas` : 'A aguardar evidência'}</span></div>
                <ArrowUpRight size={18}/>
              </Link>
            ))}
          </div>
        </section>

        <section className="featured-section" aria-labelledby="featured-title">
          <div className="section-heading"><div><span className="section-kicker"><span className="section-number">01</span> O ESSENCIAL, PARA COMEÇAR</span><h2 id="featured-title" data-testid="featured-title">Os nomes. Os lugares. As ligações.</h2></div><Link to="/encontrar" data-testid="see-all-entities">Explorar todos os dossiês<ArrowUpRight size={16}/></Link></div>
          {error ? <div role="alert" className="error-state" data-testid="home-error">{error}<button onClick={() => window.location.reload()} data-testid="home-retry">Tentar novamente</button></div> : <div className="entity-grid">{featured.length ? featured.map((item, index) => <motion.div key={item.id} className="entity-motion-wrap" initial={reducedMotion ? false : {y: 12}} whileInView={{y: 0}} viewport={{once: true, amount: 0.01}} transition={{duration: 0.4, delay: index * 0.06}}><EntityCard entity={item}/></motion.div>) : Array.from({length: 4}, (_, index) => <div key={index} className="skeleton entity-skeleton"/>)}</div>}
        </section>

        <section className="world-section" aria-labelledby="world-title">
          <div className="section-heading"><div><span className="section-kicker"><span className="section-number cyan-number">02</span> PARA LÁ DAS LUZES DA CIDADE</span><h2 id="world-title" data-testid="world-title">Há mais mundo lá fora.</h2></div><Link to="/encontrar?tipo=local" data-testid="world-all-locations">Locais e regiões<ArrowUpRight size={16}/></Link></div>
          <div className="world-panorama">
            <img src={assetUrl('/media/keys.webp')} loading="lazy" alt="Ilhas e pontes de Leonida Keys, imagem oficial da Rockstar Games"/>
            <div className="world-panorama-shade"/>
            <div className="world-panorama-content"><span className="eyebrow"><MapPin size={15}/> LEONIDA KEYS</span><p data-testid="world-feature-heading">O outro lado<br/>do paraíso.</p><Link to="/entidade/leonida-keys" data-testid="world-open-keys">Abrir o dossiê<ArrowUpRight size={19}/></Link></div>
            <span className="world-credit">IMAGEM OFICIAL / ROCKSTAR GAMES</span>
          </div>
          <div className="world-index">{[{slug:'vice-city', name:'Vice City', image:'vice-city'}, {slug:'grassrivers', name:'Grassrivers', image:'grassrivers'}, {slug:'port-gellhorn', name:'Port Gellhorn', image:'port'}].map((place, index) => <Link key={place.slug} to={`/entidade/${place.slug}`} data-testid={`world-location-${place.slug}`}><span className="world-index-number">0{index + 1}</span><img src={assetUrl(`/media/${place.image}.webp`)} alt="" loading="lazy"/><span>{place.name}</span><ArrowUpRight size={18}/></Link>)}</div>
        </section>

        <section className="bottom-editorial">
          <div className="editorial-spotlight"><img src={assetUrl('/media/hero-city.webp')} alt="" loading="lazy"/><span className="section-kicker"><Radio size={15}/> A HISTÓRIA, EM TEMPO REAL</span><h2>A caminho de Leonida.</h2><p>Os trailers e os anúncios que construíram a história de Grand Theft Auto VI.</p><Link to="/acompanhar" className="text-link" data-testid="explore-timeline">Percorrer a cronologia<ArrowRight size={16}/></Link></div>
          <div className="editorial-principle"><ScanLine size={34} strokeWidth={1.3}/><div><span className="section-kicker">O NOSSO COMPROMISSO</span><h3>Uma afirmação.<br/>A sua evidência.</h3><p>A origem e a verificação são coisas diferentes. Aqui, essa diferença fica à vista.</p><Link to="/metodologia" data-testid="explore-evidence-method">Conhecer os critérios editoriais<ArrowUpRight size={16}/></Link></div><Asterisk className="principle-asterisk" size={45} strokeWidth={1}/></div>
        </section>
      </div>
    </div>
  );
}