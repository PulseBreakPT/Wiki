import {BrowserRouter,Routes,Route,Link,useLocation} from 'react-router-dom';
import {useEffect} from 'react';
import {Toaster} from 'sonner';
import {ArchiveLayout} from './components/ArchiveLayout';
import {SavedProvider} from './lib/saved';
import Explore from './pages/Explore';
import Find from './pages/Find';
import EntityDetail from './pages/EntityDetail';
import Saved from './pages/Saved';
import Follow from './pages/Follow';
import Resolve from './pages/Resolve';
import Methodology from './pages/Methodology';
import Editorial from './pages/Editorial';
import './App.css';
import './refinements.css';
const Metadata=()=>{const location=useLocation();useEffect(()=>{document.documentElement.lang='pt-PT';if(!location.pathname.startsWith('/entidade/'))document.title='VI Archive — O arquivo independente de GTA VI';let canonical=document.querySelector('link[rel="canonical"]') as HTMLLinkElement;if(!canonical){canonical=document.createElement('link');canonical.rel='canonical';document.head.appendChild(canonical);}canonical.href=`${process.env.REACT_APP_BACKEND_URL}${location.pathname}`;let robots=document.querySelector('meta[name="robots"]') as HTMLMetaElement;if(!robots){robots=document.createElement('meta');robots.name='robots';document.head.appendChild(robots);}robots.content=location.search||['/redacao','/guardar'].includes(location.pathname)?'noindex, follow':'index, follow';},[location]);return null;};
export default function App(){return <BrowserRouter><SavedProvider><Metadata/><Routes><Route element={<ArchiveLayout/>}><Route index element={<Explore/>}/><Route path="encontrar" element={<Find/>}/><Route path="entidade/:slug" element={<EntityDetail/>}/><Route path="guardar" element={<Saved/>}/><Route path="acompanhar" element={<Follow/>}/><Route path="resolver" element={<Resolve/>}/><Route path="metodologia" element={<Methodology/>}/><Route path="redacao" element={<Editorial/>}/><Route path="*" element={<div className="page-content empty-state"><h1 data-testid="not-found-title">Página não encontrada.</h1><Link to="/" data-testid="not-found-home">Voltar ao arquivo</Link></div>}/></Route></Routes><Toaster theme="dark" position="bottom-right" richColors closeButton/></SavedProvider></BrowserRouter>;}