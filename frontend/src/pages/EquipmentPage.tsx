import {Link, NavLink} from 'react-router-dom';
import {ArrowLeft, ArrowUpRight, CarFront, Crosshair, FolderOpen, ShieldCheck} from 'lucide-react';
import {Button} from '../components/ui/button';
import '../styles/equipment.css';

type EquipmentKind = 'armas' | 'veiculos';

const sections = {
  armas: {
    title: 'Armas',
    label: 'EQUIPAMENTO',
    description: 'O espaço dedicado às armas de Grand Theft Auto VI.',
    emptyTitle: 'O arsenal ainda está por documentar.',
    emptyDescription: 'Ainda não há armas publicadas nesta página. Este espaço fica preparado para receber os primeiros registos.',
    icon: Crosshair,
    index: '01',
  },
  veiculos: {
    title: 'Veículos',
    label: 'MOBILIDADE',
    description: 'O espaço dedicado aos veículos de Grand Theft Auto VI.',
    emptyTitle: 'A garagem ainda está vazia.',
    emptyDescription: 'Ainda não há veículos publicados nesta página. Este espaço fica preparado para receber os primeiros registos.',
    icon: CarFront,
    index: '02',
  },
};

export default function EquipmentPage({kind}: {kind: EquipmentKind}) {
  const section = sections[kind];
  const Icon = section.icon;

  return (
    <div className="page-content equipment-page page-enter" data-catalog-kind={kind} data-testid={`${kind}-page`}>
      <Link to="/" className="equipment-back" data-testid={`${kind}-back`}><ArrowLeft size={14}/> Voltar a explorar</Link>
      <header className="page-heading equipment-heading">
        <div>
          <span className="eyebrow">O ARQUIVO / {section.label}</span>
          <h1 data-testid={`${kind}-title`}>{section.title}<span className="equipment-title-dot">.</span></h1>
          <p>{section.description}</p>
        </div>
        <div className="equipment-heading-mark" aria-hidden="true"><Icon size={35} strokeWidth={1.1}/><span>CATÁLOGO / {section.index}</span></div>
      </header>

      <div className="equipment-toolbar">
        <nav className="equipment-navigation" aria-label="Catálogos do arquivo">
          <NavLink to="/armas" className={({isActive}) => isActive ? 'active' : ''} data-testid="catalog-nav-armas"><Crosshair size={15}/>Armas</NavLink>
          <NavLink to="/veiculos" className={({isActive}) => isActive ? 'active' : ''} data-testid="catalog-nav-veiculos"><CarFront size={16}/>Veículos</NavLink>
        </nav>
        <span className="equipment-status" data-testid={`${kind}-status`}><span/>SEM REGISTOS PUBLICADOS</span>
      </div>

      <section className="equipment-empty" aria-labelledby={`${kind}-empty-title`} data-testid={`${kind}-empty`}>
        <span className="equipment-corner corner-top" aria-hidden="true"/>
        <span className="equipment-corner corner-bottom" aria-hidden="true"/>
        <div className="equipment-emblem" aria-hidden="true"><Icon size={43} strokeWidth={1.1}/></div>
        <span className="section-kicker">UM NOVO CAPÍTULO DO ARQUIVO</span>
        <h2 id={`${kind}-empty-title`}>{section.emptyTitle}</h2>
        <p>{section.emptyDescription}</p>
        <Button asChild variant="outline" className="equipment-explore"><Link to="/encontrar" data-testid={`${kind}-explore`}><FolderOpen size={16}/>Explorar o arquivo<ArrowUpRight size={16}/></Link></Button>
        <span className="equipment-empty-footnote">Sem itens de exemplo. Sem estatísticas inventadas.</span>
      </section>

      <aside className="equipment-principle">
        <span className="equipment-principle-icon"><ShieldCheck size={22} strokeWidth={1.4}/></span>
        <div><h2>Primeiro a fonte. Depois o registo.</h2><p>As futuras entradas seguem os mesmos critérios de evidência do resto do arquivo.</p></div>
        <Link to="/metodologia" data-testid={`${kind}-method`}>Conhecer os critérios<ArrowUpRight size={15}/></Link>
      </aside>
    </div>
  );
}
