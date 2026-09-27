import {Link} from 'react-router-dom';
import {BookOpen, Cloud, HardDrive, ArrowRight} from 'lucide-react';
import {Button} from '../components/ui/button';
import {LIVE_CHANNEL} from '../lib/offline';
export default function OfflineEdition() {
  return <div className="page-content methodology page-enter" data-testid="offline-edition">
    <header className="page-heading"><span className="eyebrow">VI ARCHIVE / {LIVE_CHANNEL?'CANAL LIVE':'EDIÇÃO OFFLINE'}</span><h1>{LIVE_CHANNEL?'O arquivo atualiza-se pelo GitHub.':'O arquivo vai consigo.'}</h1><p>{LIVE_CHANNEL?'As publicações do main entram no arquivo sem reinstalar o APK.':'Sem conta. Sem servidor. Disponível mesmo sem ligação à Internet.'}</p></header>
    <div className="method-grid">
      <section>{LIVE_CHANNEL?<Cloud size={26}/>:<HardDrive size={26}/>}<h2>{LIVE_CHANNEL?'Atualização automática':'Incluído nesta edição'}</h2><p>Personagens, locais, veículos, armas, animais, atividades, propriedades, sistemas, rádio, facções, media, edições, evidências e cronologia fazem parte do corpus versionado.</p><p>{LIVE_CHANNEL?'Quando uma alteração é publicada no GitHub Pages, o APK recebe a versão live na próxima abertura. Não é necessário reinstalar o APK por alterações de conteúdo ou interface web.':'A cópia empacotada é o fallback quando a versão live não está acessível.'}</p></section>
      <section><BookOpen size={26}/><h2>Estados editoriais separados</h2><p data-testid="offline-editorial-notice">Official, Development, Unknown e Reported permanecem distintos. O arquivo não transforma material de desenvolvimento em confirmação final e não inventa campos em falta.</p><p>Ligações externas precisam de Internet; o corpus local continua disponível como reserva no APK.</p></section>
    </div>
    <Button asChild className="primary-button"><Link to="/encontrar">Explorar o arquivo <ArrowRight size={16}/></Link></Button>
  </div>;
}
