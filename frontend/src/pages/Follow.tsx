import {useEffect, useState} from 'react';
import {ArrowUpRight, CalendarDays, History, ShieldCheck, ExternalLink} from 'lucide-react';
import {api} from '../lib/api';
import {dateLabel} from '../types';

type TimelineEntry = {id: string; date: string; title: string; summary: string; source_url: string; type: string};

export default function Follow() {
  const [items, setItems] = useState<TimelineEntry[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    api<TimelineEntry[]>('/timeline')
      .then(data => active && setItems(data))
      .catch(error => active && setError(error.message))
      .finally(() => active && setLoading(false));
    return () => {active = false;};
  }, []);

  return (
    <div className="page-content page-enter">
      <header className="page-heading"><span className="eyebrow">ACOMPANHAR / CRONOLOGIA REAL</span><h1 data-testid="follow-title">A história até aqui.</h1><p>Os anúncios e as publicações que nos aproximam de Leonida.</p></header>
      <div className="timeline-banner">
        <img src="/media/keys.webp" alt="Leonida Keys na galeria oficial de GTA VI"/>
        <div/>
        <span className="eyebrow">DOS PRIMEIROS TRAILERS AO ARQUIVO</span>
        <h2>O próximo capítulo<br/>tem uma história.</h2>
        <a href="https://www.rockstargames.com/VI" target="_blank" rel="noreferrer" data-testid="official-announcements">Últimos anúncios da Rockstar<ArrowUpRight size={16}/></a>
      </div>
      <div className="section-heading timeline-heading"><h2><History size={18}/>Marcos documentados</h2><span>História do desenvolvimento · Não é a cronologia do universo</span></div>
      {error ? <p className="error-state" role="alert" data-testid="timeline-error">{error}</p> : loading ? <div className="skeleton" style={{height: 180}} role="status" aria-label="A carregar a cronologia" data-testid="timeline-loading"/> : items.length ? (
        <div className="timeline">
          {items.map(item => (
            <article key={item.id} className="timeline-item" data-testid={`timeline-${item.id}`}>
              <div className="timeline-date"><CalendarDays size={15}/><time dateTime={item.date}>{dateLabel(item.date)}</time><span>{item.type.toUpperCase()}</span></div>
              <div className="timeline-node"/>
              <div className="timeline-text"><span className="official-tag"><ShieldCheck size={12}/>Official</span><h3>{item.title}</h3><p>{item.summary}</p><a href={item.source_url} target="_blank" rel="noreferrer" data-testid={`timeline-source-${item.id}`}>Ver publicação original<ExternalLink size={14}/></a></div>
            </article>
          ))}
        </div>
      ) : <div className="empty-state" data-testid="timeline-empty"><History size={35}/><h2>Ainda sem marcos publicados.</h2><p>A cronologia recebe apenas acontecimentos documentados com uma fonte.</p></div>}
      <div className="info-note"><ShieldCheck size={17}/><p>Datas de publicação não são datas de acontecimentos no jogo. Este registo reúne marcos selecionados, não todos os anúncios.</p></div>
    </div>
  );
}