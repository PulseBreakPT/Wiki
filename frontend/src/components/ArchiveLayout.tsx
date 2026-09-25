import {useState, useEffect} from 'react';
import {NavLink, Link, Outlet, useLocation, useNavigate} from 'react-router-dom';
import {Compass, Search, BookOpen, Radio, Bookmark, ArrowUpRight, Globe2, Menu, X, ShieldCheck, ArrowRight, PenLine, EyeOff} from 'lucide-react';
import {useSaved} from '../lib/saved';
import {Button} from './ui/button';
import {ArchiveSearch} from './ArchiveSearch';
const navigation = [
  {to:'/', label:'Explorar', icon:Compass}, {to:'/encontrar', label:'Encontrar', icon:Search},
  {to:'/resolver', label:'Resolver', icon:BookOpen}, {to:'/acompanhar', label:'Acompanhar', icon:Radio},
  {to:'/guardar', label:'Guardar', icon:Bookmark}
];
export const Brand = () => <Link to="/" className="brand" aria-label="VI Archive, início" data-testid="brand-home"><span className="brand-symbol">VI<span>↗</span></span><span>ARCHIVE<span className="brand-caption">THE LEONIDA FILES</span></span></Link>;
export const ArchiveLayout = () => {
  const [menu, setMenu] = useState(false);
  const [term, setTerm] = useState('');
  const location = useLocation();
  const navigate = useNavigate();
  const {saved} = useSaved();
  useEffect(() => {setMenu(false); window.scrollTo(0, 0);}, [location.pathname]);
  return <div className="archive-shell">
    <a className="skip-link" href="#main-content" data-testid="skip-main">Saltar para o conteúdo</a>
    <aside className={`sidebar ${menu ? 'mobile-open' : ''}`}>
      <Brand/>
      <div className="sidebar-section-label">O ARQUIVO</div>
      <nav aria-label="Navegação principal">{navigation.map(({to,label,icon:Icon}) => <NavLink key={to} to={to} end={to==='/'} data-testid={`nav-${label.toLowerCase()}`} className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}><Icon size={19}/><span>{label}</span>{label==='Guardar' && saved.length>0 ? <span className="nav-count" data-testid="saved-count">{saved.length}</span> : null}{label==='Explorar' && <span className="nav-dot"/>}</NavLink>)}</nav>
      <div className="sidebar-divider"/>
      <div className="sidebar-section-label">DENTRO DE LEONIDA</div>
      <Link to="/encontrar?tipo=personagem" className="subnav" data-testid="sidebar-characters"><span className="tiny-square pink"/>Personagens<ArrowUpRight size={14}/></Link>
      <Link to="/encontrar?tipo=local" className="subnav" data-testid="sidebar-locations"><span className="tiny-square cyan"/>Locais e regiões<ArrowUpRight size={14}/></Link>
      <Link to="/acompanhar" className="subnav" data-testid="sidebar-timeline"><span className="tiny-square amber"/>Cronologia<ArrowUpRight size={14}/></Link>
      <div className="sidebar-bottom">
        <Link to="/metodologia" className="archive-note" data-testid="sidebar-method"><ShieldCheck size={20}/><strong>Informação, não especulação.</strong><p>Cada descoberta começa numa fonte.</p><span>O nosso compromisso <ArrowRight size={14}/></span></Link>
        <Link to="/redacao" className="editor-link" data-testid="sidebar-editorial"><PenLine size={16}/> Redação <ArrowUpRight size={15}/></Link>
        <div className="sidebar-footer"><span className="status-dot"/> ARQUIVO INDEPENDENTE <span>V.01</span></div>
      </div>
    </aside>
    <div className="workspace">
      <header className="topbar">
        <Button variant="ghost" size="icon" className="mobile-toggle" data-testid="mobile-menu-toggle" aria-label={menu?'Fechar menu':'Abrir menu'} onClick={()=>setMenu(!menu)}>{menu?<X/>:<Menu/>}</Button>
        <div className="breadcrumb" data-testid="current-section"><span>O universo de</span> <b>GRAND THEFT AUTO VI</b></div>
        <ArchiveSearch/>
        <span className="language" data-testid="interface-language"><Globe2 size={15}/> PT</span>
        <Link className="header-saved" to="/guardar" title="Os meus guardados" aria-label="Os meus guardados" data-testid="header-saved"><Bookmark size={18}/></Link>
      </header>
      <main id="main-content"><Outlet/></main>
      <footer className="page-footer"><span>VI ARCHIVE <span className="footer-sep">/</span> Um mundo de informação. Uma fonte de cada vez.</span><Link to="/metodologia" data-testid="footer-rights">Independente. Não afiliado à Rockstar Games. <ArrowUpRight size={13}/></Link></footer>
    </div>
    {menu&&<button className="mobile-backdrop" aria-label="Fechar navegação" data-testid="mobile-backdrop" onClick={()=>setMenu(false)}/>}
  </div>;
};