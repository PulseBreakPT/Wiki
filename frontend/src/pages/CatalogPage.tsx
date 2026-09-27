import {useEffect, useState} from 'react';
import {Link} from 'react-router-dom';
import {ArrowLeft, ArrowUpRight, PawPrint, Trophy, House, Radio, UsersRound, ListChecks, Layers3, Film, PackageOpen, Backpack, ShieldCheck} from 'lucide-react';
import {fetchAllEntities} from '../lib/catalog';
import {SearchResult} from '../types';
import {EntityCard} from '../components/EntityCard';
import '../styles/equipment.css';

export type CatalogKind = 'animais'|'atividades'|'propriedades'|'faccoes'|'radio'|'missoes'|'sistemas'|'media'|'edicoes'|'equipamento';

const catalogs = {
  animais:{type:'animal',title:'Animais',label:'VIDA SELVAGEM',description:'Espécies documentadas em Leonida, separando material oficial, desenvolvimento e possibilidades ainda não confirmadas.',icon:PawPrint},
  atividades:{type:'atividade',title:'Atividades',label:'MUNDO ABERTO',description:'Desportos, mini-jogos, atividades secundárias e sistemas de progressão identificados no material pré-lançamento.',icon:Trophy},
  propriedades:{type:'propriedade',title:'Propriedades',label:'CASAS E GARAGENS',description:'Safehouses, motéis e garagens documentados, com acesso, capacidade e estado de confirmação preservados.',icon:House},
  faccoes:{type:'organizacao',title:'Facções e organizações',label:'GRUPOS',description:'Gangues, clubes e outras organizações registadas no arquivo.',icon:UsersRound},
  radio:{type:'radio',title:'Rádio e música',label:'SOM DE LEONIDA',description:'Estações, música de trailers e faixas atualmente associadas, sem tratar a lista como soundtrack final.',icon:Radio},
  missoes:{type:'missao',title:'Missões',label:'HISTÓRIA',description:'Missões individualmente documentadas e o estado atual da estrutura narrativa.',icon:ListChecks},
  sistemas:{type:'sistema',title:'Sistemas',label:'GAMEPLAY',description:'Polícia, furtos, combustível, Focus, roubos, economia, conclusão e outros sistemas documentados.',icon:Layers3},
  media:{type:'media',title:'Media oficial',label:'ARQUIVO VISUAL',description:'Trailers, screenshots, artwork e marcos de media documentados no pacote editorial.',icon:Film},
  edicoes:{type:'edicao',title:'Edições',label:'LANÇAMENTO',description:'Standard, Ultimate e conteúdos de pré-encomenda, mantendo o estado pré-lançamento dos detalhes.',icon:PackageOpen},
  equipamento:{type:'equipamento',title:'Equipamento',label:'FERRAMENTAS',description:'Ferramentas e equipamento não classificados como armas, preservados separadamente no arquivo.',icon:Backpack},
} as const;

export default function CatalogPage({kind}:{kind:CatalogKind}) {
  const section=catalogs[kind], Icon=section.icon;
  const [data,setData]=useState<SearchResult|null>(null),[error,setError]=useState('');
  useEffect(()=>{let active=true;setData(null);setError('');fetchAllEntities(section.type).then(result=>active&&setData(result)).catch(err=>active&&setError(err.message));return()=>{active=false;};},[section.type]);
  return <div className="page-content equipment-page page-enter" data-testid={`catalog-${kind}`}>
    <Link to="/" className="equipment-back"><ArrowLeft size={14}/> Voltar a explorar</Link>
    <header className="page-heading equipment-heading"><div><span className="eyebrow">O ARQUIVO / {section.label}</span><h1>{section.title}<span className="equipment-title-dot">.</span></h1><p>{section.description}</p></div><div className="equipment-heading-mark" aria-hidden="true"><Icon size={35} strokeWidth={1.1}/><span>CATÁLOGO SSS</span></div></header>
    <div className="equipment-toolbar"><span className="equipment-status"><span/>{data?`${data.total} REGISTOS PUBLICADOS`:'A CONSULTAR O ARQUIVO'}</span><Link to="/encontrar" className="text-link">Pesquisa global <ArrowUpRight size={15}/></Link></div>
    {error?<div className="error-state" role="alert">{error}</div>:!data?<div className="skeleton detail-skeleton"/>:<section className="equipment-catalog"><div className="equipment-catalog-note"><ShieldCheck size={18}/><p><strong>Estado editorial preservado.</strong> Official, Development, Unknown e Reported são categorias diferentes; dados em falta não são preenchidos por inferência.</p></div><div className="entity-grid">{data.items.map(entity=><EntityCard entity={entity} key={entity.id}/>)}</div></section>}
  </div>;
}
