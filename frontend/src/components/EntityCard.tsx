import {Link} from 'react-router-dom';
import {ArrowUpRight, Bookmark, Check, ShieldCheck, FileText, MapPin, UserRound} from 'lucide-react';
import {Entity} from '../types';
import {useSaved} from '../lib/saved';
export const EntityCard = ({entity, compact=false}: {entity: Entity; compact?: boolean}) => {
  const {saved,toggle} = useSaved();
  const marked = saved.includes(entity.id);
  return <article className={`entity-card ${compact?'compact':''}`} data-testid={`entity-card-${entity.slug}`}>
    <Link to={`/entidade/${entity.slug}`} className="entity-image-link" data-testid={`entity-open-${entity.slug}`}>
      {entity.image ? <img src={entity.image} alt={entity.name} loading="lazy" style={{objectPosition:entity.image_position}}/> : <div className="image-empty"><FileText size={36}/></div>}
      <span className="image-tint"/><span className="entity-type">{entity.type==='local'?<MapPin size={12}/>:<UserRound size={12}/>} {entity.type==='local'?'LOCAL':'PERSONAGEM'}</span>
      <span className="card-open-arrow"><ArrowUpRight size={18}/></span>
    </Link>
    <button className={`save-card ${marked?'is-saved':''}`} title={marked?'Remover dos guardados':'Guardar entidade'} aria-label={`${marked?'Remover':'Guardar'} ${entity.name}`} aria-pressed={marked} data-testid={`save-${entity.slug}`} onClick={()=>toggle(entity.id)}>{marked?<Check size={16}/>:<Bookmark size={16}/>}</button>
    <div className="entity-card-content"><Link to={`/entidade/${entity.slug}`} data-testid={`entity-title-${entity.slug}`}><h3>{entity.name}</h3></Link><p data-testid={`entity-summary-${entity.slug}`}>{entity.summary}</p><div className="entity-card-footer"><span className="official-tag" data-testid={`entity-label-${entity.slug}`}><ShieldCheck size={12}/>{entity.label}</span><span><FileText size={12}/> {entity.assertion_count} afirmações</span></div></div>
  </article>;
};