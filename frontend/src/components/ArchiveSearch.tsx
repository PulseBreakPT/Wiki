import {useEffect, useRef, useState} from 'react';
import type {KeyboardEvent} from 'react';
import {Link, useNavigate, useLocation} from 'react-router-dom';
import {Search, ArrowRight, ArrowUpRight, LoaderCircle} from 'lucide-react';
import {api} from '../lib/api';
import {Entity, SearchResult, typeNames} from '../types';

export const ArchiveSearch = () => {
  const [term, setTerm] = useState('');
  const [items, setItems] = useState<Entity[]>([]);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [active, setActive] = useState(-1);
  const navigate = useNavigate();
  const location = useLocation();
  const ref = useRef<HTMLDivElement>(null);
  const showSuggestions = open && term.trim().length >= 2;

  useEffect(() => {
    setOpen(false);
    setTerm('');
  }, [location.pathname]);

  useEffect(() => {
    const controller = new AbortController();
    setActive(-1);
    setItems([]);
    if (term.trim().length < 2) {
      setBusy(false);
      return;
    }
    setBusy(true);
    const timer = setTimeout(() => {
      api<SearchResult>(`/entities?q=${encodeURIComponent(term)}&limit=5`, {
        signal: controller.signal,
      })
        .then(result => setItems(result.items))
        .catch(error => {
          if (error.name !== 'AbortError') setItems([]);
        })
        .finally(() => {
          if (!controller.signal.aborted) setBusy(false);
        });
    }, 230);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [term]);

  useEffect(() => {
    const close = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, []);

  const submit = () => {
    const selected = showSuggestions && !busy && active >= 0 ? items[active] : undefined;
    setOpen(false);
    navigate(selected ? `/entidade/${selected.slug}` : `/encontrar?q=${encodeURIComponent(term)}`);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Escape') {
      setOpen(false);
      setActive(-1);
    }
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setOpen(true);
      if (!busy) setActive(index => Math.min(index + 1, items.length - 1));
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (!busy) setActive(index => Math.max(-1, index - 1));
    }
  };

  return (
    <div className="header-search-wrap" ref={ref}>
      <form className="header-search" role="search" onSubmit={event => {event.preventDefault(); submit();}}>
        <Search size={16}/>
        <input
          value={term}
          maxLength={100}
          data-testid="header-search-input"
          aria-label="Pesquisar no arquivo"
          placeholder="Pesquisar no arquivo…"
          role="combobox"
          aria-autocomplete="list"
          aria-expanded={showSuggestions}
          aria-controls="archive-suggestions"
          aria-activedescendant={showSuggestions && !busy && active >= 0 ? `suggestion-${active}` : undefined}
          onChange={event => {setTerm(event.target.value); setOpen(true);}}
          onFocus={() => setOpen(true)}
          onKeyDown={handleKeyDown}
        />
        <button type="submit" aria-label="Pesquisar" data-testid="header-search-submit">
          <ArrowRight size={15}/>
        </button>
      </form>
      {showSuggestions && (
        <div className="search-suggestions" data-testid="search-autocomplete">
          <div className="suggestions-heading" data-testid="autocomplete-status">
            {busy ? 'A consultar o arquivo…' : 'ENTIDADES DO ARQUIVO'}
            {busy && <LoaderCircle size={13} className="search-spinner"/>}
          </div>
          <div role="listbox" id="archive-suggestions" aria-label="Sugestões de pesquisa">
            {!busy && items.map((item, index) => (
              <div role="option" aria-selected={active === index} id={`suggestion-${index}`} key={item.id} data-testid={`autocomplete-option-${item.slug}`}>
                <Link to={`/entidade/${item.slug}`} className={active === index ? 'active' : ''} onClick={() => setOpen(false)} onMouseEnter={() => setActive(index)} data-testid={`autocomplete-link-${item.slug}`}>
                  {item.image && <img src={item.image} alt=""/>}
                  <div>
                    <strong data-testid={`autocomplete-name-${item.slug}`}>{item.name}</strong>
                    <span data-testid={`autocomplete-type-${item.slug}`}>{typeNames[item.type]}</span>
                  </div>
                  <ArrowUpRight size={14}/>
                </Link>
              </div>
            ))}
          </div>
          {!busy && !items.length && <p className="autocomplete-empty" data-testid="autocomplete-empty">Ainda sem correspondências no arquivo.</p>}
          <Link to={`/encontrar?q=${encodeURIComponent(term)}`} onClick={() => setOpen(false)} className="all-search-results" data-testid="autocomplete-all-results">
            Ver todos os resultados <ArrowRight size={14}/>
          </Link>
        </div>
      )}
    </div>
  );
};