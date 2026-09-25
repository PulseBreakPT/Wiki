import {useState, useEffect, useRef} from 'react';
import {NavLink, Link, Outlet, useLocation} from 'react-router-dom';
import {Compass, Search, BookOpen, Radio, Bookmark, ArrowUpRight, Globe2, Menu, X, ShieldCheck, ArrowRight, PenLine, Asterisk} from 'lucide-react';
import {useSaved} from '../lib/saved';
import {Button} from './ui/button';
import {ArchiveSearch} from './ArchiveSearch';

const navigation = [
  {to: '/', label: 'Explorar', icon: Compass, tone: 'pink'},
  {to: '/encontrar', label: 'Encontrar', icon: Search, tone: 'cyan'},
  {to: '/resolver', label: 'Resolver', icon: BookOpen, tone: 'green'},
  {to: '/acompanhar', label: 'Acompanhar', icon: Radio, tone: 'amber'},
  {to: '/guardar', label: 'Guardar', icon: Bookmark, tone: 'lilac'},
];

export const Brand = () => (
  <Link to="/" className="brand" aria-label="VI Archive, início" data-testid="brand-home">
    <span className="brand-symbol" aria-hidden="true">VI<span>↗</span></span>
    <span className="brand-wordmark">ARCHIVE<span className="brand-caption">THE LEONIDA FILES</span></span>
  </Link>
);

export const ArchiveLayout = () => {
  const [menu, setMenu] = useState(false);
  const location = useLocation();
  const {saved} = useSaved();
  const menuButton = useRef<HTMLButtonElement>(null);
  const closeButton = useRef<HTMLButtonElement>(null);

  useEffect(() => {setMenu(false); window.scrollTo(0, 0);}, [location.pathname, location.search]);
  useEffect(() => {
    if (!menu) return;
    closeButton.current?.focus();
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const close = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {setMenu(false); menuButton.current?.focus();}
    };
    document.addEventListener('keydown', close);
    return () => {document.body.style.overflow = previous; document.removeEventListener('keydown', close);};
  }, [menu]);

  return (
    <div className="archive-shell">
      <a className="skip-link" href="#main-content" data-testid="skip-main">Saltar para o conteúdo</a>
      <aside id="archive-sidebar" className={`sidebar ${menu ? 'mobile-open' : ''}`} aria-label="O arquivo">
        <div className="sidebar-brand-row"><Brand/><button ref={closeButton} className="sidebar-close" aria-label="Fechar menu" data-testid="sidebar-close" onClick={() => setMenu(false)}><X size={20}/></button></div>
        <div className="sidebar-section-label"><span>O ARQUIVO</span><span>01 — 05</span></div>
        <nav aria-label="Navegação principal">
          {navigation.map(({to, label, icon: Icon, tone}, index) => (
            <NavLink key={to} to={to} end={to === '/'} data-testid={`nav-${label.toLowerCase()}`} className={({isActive}) => `nav-item tone-${tone} ${isActive || (to === '/' && location.pathname.startsWith('/entidade/')) ? 'active' : ''}`}>
              <span className="nav-icon"><Icon size={19} strokeWidth={1.7}/></span><span className="nav-label">{label}</span>
              {label === 'Guardar' && saved.length > 0 ? <span className="nav-count" data-testid="saved-count">{saved.length}</span> : <span className="nav-index">0{index + 1}</span>}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-divider"/>
        <div className="sidebar-section-label">DENTRO DE LEONIDA</div>
        <Link to="/encontrar?tipo=personagem" className="subnav" data-testid="sidebar-characters"><span className="tiny-square pink"/>Personagens<ArrowUpRight size={14}/></Link>
        <Link to="/encontrar?tipo=local" className="subnav" data-testid="sidebar-locations"><span className="tiny-square cyan"/>Locais e regiões<ArrowUpRight size={14}/></Link>
        <Link to="/acompanhar" className="subnav" data-testid="sidebar-timeline"><span className="tiny-square amber"/>Cronologia<ArrowUpRight size={14}/></Link>
        <div className="sidebar-bottom">
          <Link to="/metodologia" className="archive-note" data-testid="sidebar-method"><Asterisk size={25}/><strong>Menos ruído.<br/>Mais evidência.</strong><p>Cada descoberta começa numa fonte.</p><span>O nosso compromisso <ArrowRight size={14}/></span></Link>
          <Link to="/redacao" className="editor-link" data-testid="sidebar-editorial"><PenLine size={16}/> Redação <ArrowUpRight size={15}/></Link>
          <div className="sidebar-footer"><span className="status-dot"/> INDEPENDENTE <span>V.01 / PT</span></div>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <Button ref={menuButton} variant="ghost" size="icon" className="mobile-toggle" data-testid="mobile-menu-toggle" aria-label={menu ? 'Fechar menu' : 'Abrir menu'} aria-expanded={menu} aria-controls="archive-sidebar" onClick={() => setMenu(!menu)}>{menu ? <X/> : <Menu/>}</Button>
          <Link to="/" className="mobile-brand" aria-label="VI Archive, início" data-testid="mobile-brand-home">VI<span>↗</span></Link>
          <div className="breadcrumb" data-testid="current-section"><span className="header-cross" aria-hidden="true">+</span><span>O universo de</span><b>GRAND THEFT AUTO VI</b></div>
          <ArchiveSearch/>
          <span className="language" data-testid="interface-language"><Globe2 size={16}/> PT</span>
          <Link className="header-saved" to="/guardar" title="Os meus guardados" aria-label="Os meus guardados" data-testid="header-saved"><Bookmark size={19}/>{saved.length > 0 && <span className="header-saved-dot"/>}</Link>
        </header>
        <main id="main-content"><Outlet/></main>
        <footer className="page-footer"><div><span className="footer-logo">VI / ARCHIVE</span><span>Um mundo de informação. Uma fonte de cada vez.</span></div><Link to="/metodologia" data-testid="footer-rights">Independente. Não afiliado à Rockstar Games.<ArrowUpRight size={14}/></Link></footer>
      </div>
      <nav className="mobile-bottom-nav" aria-label="Navegação rápida">
        {navigation.map(({to, label, icon: Icon, tone}) => <NavLink key={to} to={to} end={to === '/'} data-testid={`mobile-nav-${label.toLowerCase()}`} className={({isActive}) => `tone-${tone} ${isActive || (to === '/' && location.pathname.startsWith('/entidade/')) ? 'active' : ''}`}><Icon size={21} strokeWidth={1.7}/><span>{label}</span></NavLink>)}
      </nav>
      {menu && <button className="mobile-backdrop" aria-label="Fechar navegação" data-testid="mobile-backdrop" onClick={() => setMenu(false)}/>}
    </div>
  );
};