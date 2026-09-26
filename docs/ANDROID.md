# VI Archive — APK Android offline e CI

## O que esta versão faz

- Empacota o site existente, as imagens, as fontes e o corpus editorial incluído no repositório. Não é um atalho para um site nem precisa de um URL público.
- Pesquisa, filtros, fichas, evidências, relações, histórico incluído, favoritos e checklist funcionam sem rede.
- `pt.viarchive.app`, nome **VI Archive**, Android **8.0+ (API 26)**.
- Login, redação, publicação e sincronização com um servidor **não estão disponíveis**, por escolha do utilizador. A rota Redação explica essa limitação.
- Os vídeos e as páginas originais das fontes não são descarregados: abrem no navegador, após confirmação, e precisam de Internet.
- Não há permissão Android `INTERNET`, permissões de armazenamento geral, analytics ou API remota no APK.

## Conteúdo e atualizações

`scripts/export_offline.py` lê apenas as declarações do corpus oficial já existente em `backend/seed.py`, sem importar `core.py`, ligar ao MongoDB ou executar operações do seed. Gera `frontend/public/data/archive.json` com 12 entidades, 20 afirmações, três registos de fonte e a cronologia incluída. Isto é conteúdo real do repositório, **não dados simulados** nem uma exportação de uma base de dados alojada.

Cada build volta a gerar o corpus. Para acrescentar ou corrigir conteúdo nesta modalidade, atualizar o corpus versionado e enviar a atualização ao repositório. Alterações feitas apenas numa base de dados externa não entram no APK. O exportador interrompe a compilação se faltarem imagens ou relações. Se a estrutura do seed mudar, atualizar também o exportador.

As datas indicam a revisão do corpus no repositório (ou `SOURCE_DATE_EPOCH`, se definido); não afirmam que houve nova consulta ou verificação das fontes. A revisão humana continua identificada como pendente.

O APK usa uma origem virtual reservada do Android, `appassets.androidplatform.net`, servida exclusivamente pelos ficheiros empacotados. Não corresponde a um servidor na Internet. A navegação React tem fallback local; as chamadas do modo offline consultam o JSON local e nunca a API.

## Primeira configuração da assinatura permanente

Não é necessário nenhum serviço pago, conta Google Play ou chave de API. O proprietário precisa de acesso ao repositório GitHub e de criar **uma única chave de assinatura**, para manter a identidade de todas as atualizações.

1. Num computador de confiança com JDK 17, executar, indicando uma pasta privada fora do repositório:
   ```bash
   bash scripts/create-android-keystore.sh /caminho/privado/backup-vi-archive
   ```
   O `keytool` pede uma palavra-passe; guardá-la num gestor de palavras-passe. O script recusa substituir uma chave existente. O formato PKCS12 usa a mesma palavra-passe para a chave e o ficheiro.
2. Guardar uma cópia cifrada do `.jks` e a palavra-passe num local seguro. **Não enviar estes ficheiros para o código nem para o chat.** Perder ou trocar esta chave impede atualizar uma instalação existente.
3. No GitHub, abrir **Settings → Secrets and variables → Actions → New repository secret** e adicionar:

   | Secret | Valor |
   |---|---|
   | `ANDROID_KEYSTORE_B64` | Conteúdo completo do ficheiro privado `viarchive-release.jks.b64` |
   | `ANDROID_STORE_PASSWORD` | Palavra-passe escolhida |
   | `ANDROID_KEY_ALIAS` | `viarchive` |
   | `ANDROID_KEY_PASSWORD` | A mesma palavra-passe do PKCS12 |

4. Enviar os ficheiros deste projeto usando **Save to Github**, na interface do Emergent. O agente não faz push nem configura os segredos por si.
5. Abrir **Actions → Android Offline APK → Run workflow** para a primeira geração. Depois, cada push em qualquer branch gera automaticamente outro APK. Os segredos só devem estar disponíveis a colaboradores de confiança; proteger as branches de distribuição.

**Sem os quatro segredos, o workflow termina com uma mensagem explícita. Não cria uma chave temporária e não disfarça um APK debug de release.** A configuração dos segredos e a primeira execução real do GitHub ficam a cargo do proprietário.

## Onde descarregar o APK

Em **Actions → Android Offline APK → execução concluída → Artifacts**, descarregar `vi-archive-offline-N`. O ZIP contém:

- `vi-archive-1.0.N.apk`, assinado com a chave permanente;
- `SHA256SUMS.txt`, integridade do APK;
- `signature.txt`, resultado de verificação e impressão digital pública do certificado;
- `version.txt`, versão, versionCode e commit correspondente.

Os artefactos ficam disponíveis durante 30 dias. Não é feita publicação na Play Store, não é criado um GitHub Release e não é atualizado automaticamente nenhum telemóvel.

Para atualizar, instalar o novo APK por cima do anterior, autorizando a instalação pela aplicação de origem quando o Android pedir. Não desinstalar: os favoritos/checklist são locais à aplicação. A assinatura e o identificador têm de permanecer iguais. O `versionCode` é `100000 + GITHUB_RUN_NUMBER` e cresce **por este workflow**; reexecutar a mesma execução conserva a versão. Se migrar de repositório ou recriar o workflow, aumentar `VERSION_OFFSET` para superar a última versão distribuída. Usar as versões da branch de distribuição, evitando instalar builds de branches antigas como atualização.

## Compilar localmente

Requisitos: Node indicado em `.nvmrc`, Yarn 1.22.22, Python 3.11 (biblioteca padrão), JDK 17, Android SDK 35 e Build Tools 35.0.0.

```bash
cd frontend
yarn install --frozen-lockfile
yarn tsc --noEmit
yarn build:offline
cd ../android
bash gradlew --no-daemon assembleDebug
```

O build offline não precisa de `.env`, `REACT_APP_BACKEND_URL`, MongoDB nem FastAPI. Usa `build-offline/` e copia os ficheiros para `android/app/src/main/assets/www/`; esses diretórios são gerados e ignorados. A versão normal do site continua a usar a configuração existente de backend e `yarn build`.

Para a pré-visualização, `yarn start` prepara automaticamente o corpus e ativa o modo offline quando não existe backend configurado. Se já existir `REACT_APP_BACKEND_URL`, mantém o modo online. `REACT_APP_OFFLINE=true` permite escolher offline explicitamente; `false` exige backend. O arranque lê a configuração existente antes do CRA, sem alterar qualquer `.env`.

O APK de teste fica em `android/app/build/outputs/apk/debug/app-debug.apk`, com identificador separado `pt.viarchive.app.debug`. **Não é a versão de distribuição permanente** e os dados do debug não passam automaticamente para release.

Para release local, configurar `ANDROID_KEYSTORE` (caminho absoluto), `ANDROID_STORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`, `VERSION_CODE` e `VERSION_NAME` no ambiente privado e executar `bash gradlew assembleRelease`. Não passar palavras-passe no código. O Gradle recusa gerar release sem assinatura.

Matriz fixada: AGP 8.9.1, Gradle 8.11.1 com checksum de distribuição, AndroidX WebKit 1.12.1, JDK 17, SDK 35. O workflow usa o runner Linux x86-64 oficial. Ferramentas Android x86-64 podem exigir uma alternativa nativa em ambientes ARM; isso não altera o projeto de CI.

## Verificação num dispositivo

1. Instalar, ativar modo avião antes da primeira abertura, consultar início, pesquisa e fichas.
2. Procurar por nomes e acentos, usar filtros, abrir evidências e relações.
3. Guardar entidades e marcar checklist; fechar e reabrir para verificar persistência.
4. Exportar favoritos pelo seletor de documentos e confirmar o JSON (cancelar também deve funcionar).
5. Confirmar que Redação mostra indisponibilidade, sem formulário de login.
6. Testar voltar, rotação, teclado, barras do sistema e ligação externa (cancelar/abrir navegador).
7. Instalar duas releases consecutivas assinadas com a mesma chave; confirmar a conservação dos favoritos.

Compilação e testes de dados não substituem esta verificação de Android real. Não considerar a assinatura permanente nem o CI como executados antes de configurar os segredos e obter uma execução bem-sucedida.
