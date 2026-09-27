import {BrowserRouter,Routes,Route,Link,useLocation} from 'react-router-dom';
import {useEffect} from 'react';
import {Toaster} from 'sonner';
import {ArchiveLayout} from './components/ArchiveLayout';
import {SavedProvider} from './lib/saved';
import Explore from './pages/CinemaExplore';
import Find from './pages/Find';
import EntityDetail from './pages/EntityDetail';
import Saved from './pages/Saved';
import Follow from './pages/Follow';
import Resolve from './pages/Resolve';
import Methodology from './pages/Methodology';
import Editorial from './pages/Editorial';
import EquipmentPage from './pages/EquipmentPage';
import OfflineEdition from './pages/OfflineEdition';
import CatalogPage from './pages/CatalogPage';
import {OFFLINE} from './lib/offline';
import './App.css';

const Metadata=()=>{const location=useLocation();useEffect(()=>{document.documentElement.lang='pt-PT';if(OFFLINE)return;if(!location.pathname.startsWith('/entidade/'))document.title=location.pathname==='/armas'?'Armas — VI Archive':location.pathname==='/veiculos'?'Veículos — VI Archive':'VI Archive — O arquivo independente de GTA VI';let canonical=document.querySelector('link[rel="canonical"]') as HTMLLinkElement;if(!canonical){canonical=document.createElement('link');canonical.rel='canonical';document.head.appendChild(canonical);}canonical.href=`${process.env.REACT_APP_BACKEND_URL}${location.pathname}`;let robots=document.querySelector('meta[name="robots"]') as HTMLMetaElement;if(!robots){robots=document.createElement('meta');robots.name='robots';document.head.appendChild(robots);}robots.content=location.search||['/redacao','/guardar'].includes(location.pathname)?'noindex, follow':'index, follow';},[location]);return null;};

const BASENAME = process.env.PUBLIC_URL || '/';

export default function App(){return <BrowserRouter basename={BASENAME}><SavedProvider><Metadata/><Routes><Route element={<ArchiveLayout/>}><Route index element={<Explore/>}/><Route path="encontrar" element={<Find/>}/><Route path="armas" element={<EquipmentPage kind="armas"/>}/><Route path="veiculos" element={<EquipmentPage kind="veiculos"/>}/>
<Route path="animais" element={<CatalogPage kind="animais"/>}/>
<Route path="atividades" element={<CatalogPage kind="atividades"/>}/>
<Route path="propriedades" element={<CatalogPage kind="propriedades"/>}/>
<Route path="faccoes" element={<CatalogPage kind="faccoes"/>}/>
<Route path="radio" element={<CatalogPage kind="radio"/>}/>
<Route path="missoes" element={<CatalogPage kind="missoes"/>}/>
<Route path="sistemas" element={<CatalogPage kind="sistemas"/>}/>
<Route path="media" element={<CatalogPage kind="media"/>}/>
<Route path="edicoes" element={<CatalogPage kind="edicoes"/>}/>
<Route path="equipamento" element={<CatalogPage kind="equipamento"/>}/>
<Route path="entidade/:slug" element={<EntityDetail/>}/><Route path="guardar" element={<Saved/>}/><Route path="acompanhar" element={<Follow/>}/><Route path="resolver" element={<Resolve/>}/><Route path="metodologia" element={<Methodology/>}/><Route path="redacao" element={OFFLINE ? <OfflineEdition/> : <Editorial/>}/><Route path="*" element={<div className="page-content empty-state"><h1 data-testid="not-found-title">Página não encontrada.</h1><Link to="/" data-testid="not-found-home">Voltar ao arquivo</Link></div>}/></Route></Routes><Toaster theme="dark" position="bottom-right" richColors closeButton/></SavedProvider></BrowserRouter>;}
