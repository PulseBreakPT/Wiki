import {useState} from 'react';
import {api} from '../../lib/api';
import {toast} from 'sonner';
import {Button} from '../ui/button';
export const SourceForm=({onDone}:{onDone:()=>void})=>{
 const [data,setData]=useState({title:'',url:'',publisher:'',rights:''}),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 const submit=async(e:React.FormEvent)=>{e.preventDefault();setBusy(true);try{await api('/editorial/sources',{method:'POST',body:JSON.stringify(data)});toast.success('Fonte registada.');onDone();}catch(e:any){setError(e.message);}finally{setBusy(false);}};
 return <form onSubmit={submit} className="source-form" data-testid="source-form"><h2>Registar fonte</h2><div className="form-grid">{[['title','Título'],['url','URL original'],['publisher','Autoria / publicação'],['rights','Direitos e condições de utilização']].map(([key,label])=><label key={key}>{label}<input required minLength={key==='rights'?5:3} type={key==='url'?'url':'text'} value={(data as any)[key]} data-testid={`source-${key}`} onChange={e=>setData({...data,[key]:e.target.value})}/></label>)}</div>{error&&<p role="alert" data-testid="source-error">{error}</p>}<Button type="submit" className="primary-button" disabled={busy} data-testid="source-save">{busy?'A guardar…':'Guardar fonte'}</Button></form>;
};