import {Link} from 'react-router-dom';
import {ArrowUpRight, Bookmark, Check, ShieldCheck, FileText, MapPin, UserRound, Building2, Car, Layers3} from 'lucide-react';
import {Entity} from '../types';
import {useSaved} from '../lib/saved';

const types = {
  personagem: {label: 'Personagem', icon: UserRound, tone: 'pink'},
  local: {label: 'Local', icon: MapPin, tone: 'cyan'},
  organizacao: {label: 'Organização', icon: Building2, tone: 'lilac'},
  veiculo: {label: 'Veículo', icon: Car, tone: 'amber'},
  sistema: {label: 'Sistema', icon: Layers3, tone: 'green'},
};

export const EntityCard = ({entity, compact = false}: {entity: Entity; compact?: boolean}) => {
  const {saved, toggle} = useSaved();
  const marked = saved.includes(entity.id);
  const type = types[entity.type as keyof typeof types] || types.sistema;
  const Icon = type.icon;

  return (
    <article className={`entity-card tone-${type.tone} ${compact ? 'compact' : ''}`} data-testid={`entity-card-${entity.slug}`}>
      <Link to={`/entidade/${entity.slug}`} className="entity-image-link" data-testid={`entity-open-${entity.slug}`}>
        {entity.image ? <img src={entity.image} alt={entity.name} loading="lazy" style={{objectPosition: entity.image_position}}/> : <div className="image-empty"><FileText size={36}/></div>}
        <span className="image-tint"/>
        <span className="entity-type" data-testid={`entity-type-${entity.slug}`}><Icon size={12}/>{type.label}</span>
        <span className="card-open-arrow" aria-hidden="true"><ArrowUpRight size={20}/></span>
      </Link>
      <button className={`save-card ${marked ? 'is-saved' : ''}`} title={marked ? 'Remover dos guardados' : 'Guardar entidade'} aria-label={`${marked ? 'Remover' : 'Guardar'} ${entity.name}`} aria-pressed={marked} data-testid={`save-${entity.slug}`} onClick={() => toggle(entity.id)}>{marked ? <Check size={17}/> : <Bookmark size={17}/>}</button>
      <div className="entity-card-content">
        <Link to={`/entidade/${entity.slug}`} data-testid={`entity-title-${entity.slug}`}><h3>{entity.name}</h3></Link>
        <p data-testid={`entity-summary-${entity.slug}`}>{entity.summary}</p>
        <div className="entity-card-footer"><span className="official-tag" data-testid={`entity-label-${entity.slug}`}><ShieldCheck size={13}/>{entity.label}</span><span data-testid={`entity-claim-count-${entity.slug}`}><FileText size={13}/>{entity.assertion_count} afirmações</span></div>
      </div>
    </article>
  );
};