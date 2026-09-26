import {useState, useEffect, useRef} from 'react';
import {NavLink, Link, Outlet, useLocation} from 'react-router-dom';
import {Compass, Search, BookOpen, Radio, Bookmark, ArrowUpRight, Globe2, Menu, X, ShieldCheck, ArrowRight, PenLine, Asterisk} from 'lucide-react';
import {useSaved} from '../lib/saved';
import {Button} from './ui/button';
import {ArchiveSearch} from './ArchiveSearch';
import {OFFLINE} from '../lib/offline';

const equipmentNavigation = [
  {to: '/armas', label: 'Armas', tone: 'pink'},
  {to: '/veiculos', label: 'Veículos', tone: 'amber'},
];

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
  const activeTitle = location.pathname.startsWith('/entidade/') ? 'Dossiê' : ({'/':'Explorar', '/encontrar':'Encontrar', '/guardar':'Guardados', '/resolver':'Guias', '/acompanhar':'Cronologia', '/metodologia':'O compromisso', '/redacao':OFFLINE ? 'Edição offline' : 'Redação', '/armas':'Armas', '/veiculos':'Veículos'}[location.pathname] || 'Arquivo');
  const sidebar = useRef<HTMLElement>(null);
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
      if (event.key === 'Tab') {
        const controls = Array.from(sidebar.current?.querySelectorAll<HTMLElement>('a[href],button:not([disabled])') || []).filter(element => element.getClientRects().length);
        const first = controls[0], last = controls[controls.length - 1];
        if (event.shiftKey && document.activeElement === first) {event.preventDefault(); last?.focus();}
        else if (!event.shiftKey && document.activeElement === last) {event.preventDefault(); first?.focus();}
      }
    };
    const wideScreen = window.matchMedia('(min-width: 901px)');
    const restoreDesktop = () => {if (wideScreen.matches) setMenu(false);};
    wideScreen.addEventListener('change', restoreDesktop);
    document.addEventListener('keydown', close);
    return () => {document.body.style.overflow = previous; document.removeEventListener('keydown', close); wideScreen.removeEventListener('change', restoreDesktop);};
  }, [menu]);

  return (
    <div className="archive-shell cinema-shell" data-area={location.pathname.split('/')[1] || 'explorar'}>
      <a className="skip-link" href="#main-content" data-testid="skip-main">Saltar para o conteúdo</a>
      <aside ref={sidebar} id="archive-sidebar" className={`sidebar ${menu ? 'mobile-open' : ''}`} role={menu ? 'dialog' : undefined} aria-modal={menu || undefined} aria-label="O arquivo">
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
        {equipmentNavigation.map(({to, label, tone}) => <NavLink key={to} to={to} className={({isActive}) => `subnav tone-${tone} ${isActive ? 'active' : ''}`} data-testid={`sidebar-${to.slice(1)}`}><span className={`tiny-square ${tone}`}/>{label}<ArrowUpRight size={14}/></NavLink>)}
        <Link to="/acompanhar" className="subnav" data-testid="sidebar-timeline"><span className="tiny-square amber"/>Cronologia<ArrowUpRight size={14}/></Link>
        <div className="sidebar-bottom">
          <Link to="/metodologia" className="archive-note" data-testid="sidebar-method"><Asterisk size={25}/><strong>Menos ruído.<br/>Mais evidência.</strong><p>Cada descoberta começa numa fonte.</p><span>O nosso compromisso <ArrowRight size={14}/></span></Link>
          <Link to="/redacao" className="editor-link" data-testid="sidebar-editorial"><PenLine size={16}/> {OFFLINE ? 'Sobre esta edição offline' : 'Redação'} <ArrowUpRight size={15}/></Link>
          <div className="sidebar-footer"><span className="status-dot"/> INDEPENDENTE <span>V.01 / PT</span></div>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <Button ref={menuButton} variant="ghost" size="icon" className="mobile-toggle" data-testid="mobile-menu-toggle" aria-label={menu ? 'Fechar menu' : 'Abrir menu'} aria-expanded={menu} aria-controls="archive-sidebar" onClick={() => setMenu(!menu)}>{menu ? <X/> : <Menu/>}</Button>
          <Link to="/" className="mobile-brand" aria-label="VI Archive, início" data-testid="mobile-brand-home"><span className="mobile-logo-mark">VI<small>↗</small></span><span className="mobile-wordmark">ARCHIVE<small>THE LEONIDA FILES</small></span></Link>
          <div className="breadcrumb" data-testid="current-section"><span>LEONIDA FILES</span><span className="breadcrumb-divider" aria-hidden="true">/</span><b>{activeTitle}</b></div>
          <ArchiveSearch/>
          <span className="language" data-testid="interface-language">{OFFLINE ? <span className="status-dot"/> : <Globe2 size={14}/>} {OFFLINE ? 'OFFLINE' : 'PT'}</span>
          <Link className="header-saved" to="/guardar" title="Os meus guardados" aria-label="Os meus guardados" data-testid="header-saved"><Bookmark size={19}/>{saved.length > 0 && <span className="header-saved-dot"/>}</Link>
        </header>
        <main id="main-content"><Outlet/></main>
        <footer className="page-footer">
          <div className="footer-top"><Link to="/" className="footer-statement" aria-label="VI Archive, voltar ao início">UM MUNDO.<br/><span>UMA FONTE DE CADA VEZ.</span></Link><div className="footer-directory"><span className="section-kicker">CONTINUE A DESCOBRIR</span><div>{[...navigation, ...equipmentNavigation].map(({to, label}) => <Link key={to} to={to}>{label}<ArrowUpRight size={14}/></Link>)}</div></div></div>
          <div className="footer-bottom"><span className="footer-logo">VI / ARCHIVE</span><span className="footer-edition">THE LEONIDA FILES — ARQUIVO INDEPENDENTE</span><Link to="/metodologia" data-testid="footer-rights">Não afiliado à Rockstar Games.<ArrowUpRight size={14}/></Link></div>
        </footer>
      </div>
      <nav className="mobile-bottom-nav" aria-label="Navegação rápida">
        {navigation.map(({to, label, icon: Icon, tone}) => <NavLink key={to} to={to} end={to === '/'} data-testid={`mobile-nav-${label.toLowerCase()}`} className={({isActive}) => `tone-${tone} ${isActive || (to === '/' && location.pathname.startsWith('/entidade/')) ? 'active' : ''}`}><span className="dock-icon"><Icon size={21} strokeWidth={1.7}/></span><span className="dock-label">{label}</span>{to === '/guardar' && saved.length > 0 && <span className="dock-saved-dot" aria-hidden="true"/>}</NavLink>)}
      </nav>
      {menu && <button className="mobile-backdrop" aria-label="Fechar navegação" data-testid="mobile-backdrop" onClick={() => setMenu(false)}/>}
    </div>
  );
};