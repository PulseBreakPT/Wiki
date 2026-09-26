import {Link} from 'react-router-dom';
import {BookOpen, HardDrive, ArrowRight} from 'lucide-react';
import {Button} from '../components/ui/button';

export default function OfflineEdition() {
  return <div className="page-content methodology page-enter" data-testid="offline-edition">
    <header className="page-heading"><span className="eyebrow">VI ARCHIVE / EDIÇÃO OFFLINE</span><h1>O arquivo vai consigo.</h1><p>Sem conta. Sem servidor. Disponível mesmo sem ligação à Internet.</p></header>
    <div className="method-grid">
      <section><HardDrive size={26}/><h2>Incluído nesta edição</h2><p>Personagens, locais, evidências, relações e cronologia do conteúdo versionado do arquivo. Pesquisa, favoritos e checklist funcionam no dispositivo.</p><p>O conteúdo é atualizado ao instalar um novo APK. As datas do corpus não representam uma nova verificação das fontes. Favoritos e progresso são conservados nas atualizações assinadas com a mesma chave, sem desinstalar.</p></section>
      <section><BookOpen size={26}/><h2>A redação fica no site</h2><p data-testid="offline-editorial-notice">O login, a edição e a publicação editorial não estão disponíveis neste APK. Nenhum pedido de autenticação é enviado.</p><p>Ligações para fontes e vídeos abrem no navegador externo e precisam de Internet. O arquivo incluído na aplicação continua disponível offline.</p></section>
    </div>
    <Button asChild className="primary-button"><Link to="/encontrar" data-testid="offline-explore">Explorar o arquivo <ArrowRight size={16}/></Link></Button>
  </div>;
}
