import {createContext, useContext, useEffect, useState, ReactNode} from 'react';
import {toast} from 'sonner';
type SavedContext = {saved: string[]; toggle: (id: string) => void; clear: () => void};
const Context = createContext<SavedContext>({saved: [], toggle: () => {}, clear: () => {}});
export const SavedProvider = ({children}: {children: ReactNode}) => {
  const [saved, setSaved] = useState<string[]>(() => {
    try { const value = JSON.parse(localStorage.getItem('vi-archive-saved') || '[]'); return Array.isArray(value) ? value.filter(i => typeof i === 'string') : []; } catch {return [];}
  });
  useEffect(() => {try {localStorage.setItem('vi-archive-saved', JSON.stringify(saved));} catch {toast.error('O navegador não permite guardar favoritos.');}}, [saved]);
  const toggle = (id: string) => {
    const exists = saved.includes(id);
    setSaved(v => exists ? v.filter(x => x !== id) : [...v, id]);
    toast.success(exists ? 'Removido dos guardados.' : 'Adicionado aos guardados.');
  };
  return <Context.Provider value={{saved, toggle, clear: () => setSaved([])}}>{children}</Context.Provider>;
};
export const useSaved = () => useContext(Context);