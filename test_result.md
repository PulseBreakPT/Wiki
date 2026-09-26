#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Criar APK Android offline do VI Archive preservando o visual, corpus público, pesquisa, favoritos e checklist; utilizador escolheu A offline sem URL e B assinatura permanente. GitHub CI deve gerar APK a cada push. Login/redação indisponíveis por decisão explícita."
backend:
  - task: "Offline preview startup without backend configuration"
    implemented: true
    working: "NA"
    file: "frontend/scripts/start-preview.cjs, frontend/package.json"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: false
        agent: "user"
        comment: "Preview crashes: REACT_APP_BACKEND_URL não configurado at api.ts import (bundle.js:5623:62), https://android-release-auto.preview.emergentagent.com. User paused APK task to report this."
      - working: "NA"
        agent: "main"
        comment: "RCA: build:offline injects flag but supervisor start was craco start with no OFFLINE/backend config. Added pre-CRA startup wrapper reading existing CRA env precedence, choosing offline only if explicit true or no configured backend; generates actual corpus at startup and spawns CRACO directly. Explicit online without URL fails early; configured online preserved. No .env modified. Restart via supervisor logs offline+corpus+Compiled successfully. Lint passes; verify served bundle and standalone mode/data contracts before UI permission."
  - task: "Offline corpus export and local public query contracts"
    implemented: true
    working: "NA"
    file: "scripts/export_offline.py, frontend/src/lib/offline.ts"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Read-only exporter reads official corpus declarations from backend/seed.py without DB imports or writes. 12 entities/20 claims/3 source records, source excerpts, relations, initial history, two timeline entries. Local query engine retains public API data contracts, fuzzy/accent search, filters/cursors/ids, abort/version handling; rejects auth/editorial/writes. No backend code or .env modified. Test standalone data/contracts, NOT live server which has missing inherited env."
  - task: "Android offline build and permanent signing CI"
    implemented: true
    working: "NA"
    file: "android/, .github/workflows/android-apk.yml, frontend/scripts/build-offline.cjs, docs/ANDROID.md"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Frontend offline build, TS and lint pass. Generated wrapper8.11.1 with SHA256, AGP8.9.1/JDK17/SDK35/WebKit1.12.1. Android local build blocked by ARM64 Debian aapt2 too old (--source-path); source not yet compiled. SDK/Gradle under persistent /app/.cache (outside /app disappears). CI uses official x86 ubuntu24, four permanent signing secrets, no ephemeral key, version counter and artifacts; GitHub not executed and no real signing key configured. Docs and safe user-run one-time key script added."
  - task: "Restored preview environment and public API smoke"
    implemented: true
    working: true
    file: "backend/.env, frontend/.env"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Initial fork lacked both env files and any application database; RCA confirmed missing MONGO_URL, DB_NAME, REACT_APP_BACKEND_URL. Created missing config per troubleshoot agent, no existing env value or backend logic changed. Existing official corpus seed runs on startup. Public API smoke requested, no writes or auth guessing."
      - working: true
        agent: "testing"
        comment: "Comprehensive backend API smoke test completed successfully. All 14 tests passed: ✅ /api/health (status ok), ✅ /api/v1/stats (12 entities, 3 sources, 20 assertions), ✅ /api/v1/featured (4 entities including jason-duval and lucia-caminos), ✅ /api/v1/entities list (12 total), ✅ /api/v1/entities search (q=jason found 6), ✅ /api/v1/entities filter by type (type=person), ✅ /api/v1/entities pagination with cursor, ✅ /api/v1/entities/jason-duval detail (3 assertions with sources), ✅ /api/v1/entities/lucia-caminos detail (3 assertions with sources), ✅ /api/v1/entities/jason-duval/history (1 version), ✅ /api/v1/entities/lucia-caminos/history (1 version), ✅ /api/v1/sources (2 sources), ✅ /api/v1/timeline (2 entries), ✅ /api/v1/auth/me correctly rejects unauthenticated requests (401). Source data returns correctly, image routes and names verified. No data mutations performed. Public API fully functional for entire-site redesign."
frontend:
  - task: "Offline archive UI parity"
    implemented: true
    working: "NA"
    file: "frontend/src/lib/api.ts, offline.ts, App.tsx, pages/OfflineEdition.tsx, Saved.tsx, EntityDetail.tsx, index.css"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "OFFLINE build flag keeps existing online path. Identical fonts now local with licenses, all images local; native JSON export bridge hook and offline copy-reference. /redacao explains unavailable auth; labels reflect offline edition. Build-offline assets generated successfully with no backend URL. UI test permission will be asked after non-UI testing; do not start browser tests yet."
  - task: "Site-wide Leonida editorial redesign"
    implemented: true
    working: "NA"
    file: "frontend/src/styles/edition.css, edition-responsive.css, pages/Explore.tsx, components/ArchiveLayout.tsx, components/ui/button.jsx, index.css, App.css"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Full visual layer across home, search/list/grid/filters, entity detail/tabs/evidence/history, favorites/dialogs, timeline, checklist, methodology, editorial login/dashboard/forms/sources/reviews, sidebar/mobile/footer/autocomplete/toasts. New typographic system and official existing art only. Functional logic unchanged; new home dossier link and footer navigation use existing routes. Changed files lint pass. Build encountered preexisting incompatible @types/node 26 with TS4.9; pinned Node20 types per RCA. UI testing awaits permission after backend smoke."
      - working: false
        agent: "user"
        comment: "Reported preview Runtime error Cannot find module '/media/hero-city.webp' at css-loader edition.css, URL https://android-release-auto.preview.emergentagent.com. Explicitly requires testing-agent verification after fix."
      - working: "NA"
        agent: "main"
        comment: "RCA confirmed CRA css-loader attempts public asset as module. Removed CSS url(), rendered public hero-city image in JSX with isolated gradient/absolute layers. TypeScript now passes with compatible Node20 types. Verify exact runtime error is gone plus asset visible and navigation functional at both the user alias and configured UUID preview. Public UI verification authorized by user's explicit testing instruction; private account creation not authorized."
metadata:
  created_by: "main_agent"
  version: "3.0"
  test_sequence: 3
  run_ui: false
test_plan:
  current_focus:
    - "Offline preview startup without backend configuration"
    - "Offline corpus export and local public query contracts"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"
agent_communication:
  - agent: "main"
    message: "USER INTERRUPTION: fix preview REACT_APP_BACKEND_URL crash now. Test NON-UI only: previewMode function no-env/explicit modes/configured backend, real corpus export+query contracts, supervisor serving new compiled OFFLINE=true bundle and local archive JSON at user preview. No live backend needed. No browser/UI tests yet; will ask user after your report. Do not touch APK toolchain in this run, no secrets/DB/env changes. Parallel crawl overlapped restart and captured old overlay (valid bug reproduction); do not assume UI fixed solely from compilation."
  - agent: "main"
    message: "CURRENT TASK TESTING: non-UI standalone corpus/query contract tests and Android/CI validation only. Read memory/test_credentials.md (no auth needed; do not create accounts). Do not mutate backend/env or start servers/browser tests. TypeScript+lint+offline build already pass. Test real corpus integrity, query edge cases, release no-secrets fail-closed, workflow syntax. Android SDK and Gradle in /app/.cache persist; native Debian ARM64 aapt2 incompatible --source-path. Troubleshooter suggests current ARM64 aapt2 from lzhiyong/android-sdk-tools v35.0.2 for validation only, or defer build to CI. Native UI/device verification not yet claimed. No actual GitHub secrets/private key configured. Return honest limits, tests count, and critical defects only; no unsolicited code fixes."
  - agent: "main"
    message: "BACKEND ONLY: use configured preview from frontend/.env. Read credentials file: no known password, don't create/reset accounts. Verify health, stats, featured, entities/search/filters, entity Jason slug, sources, history, timeline; auth/me should reject unauthenticated. Do not mutate/publish fixtures. No backend logic changed. Report counts and any issues."
  - agent: "testing"
    message: "Backend API smoke test complete: ALL 14 TESTS PASSED ✅. Public API fully operational. Verified: health check, stats (12 entities, 3 sources, 20 assertions), featured entities (jason-duval, lucia-caminos present), entity list/search/filter/pagination, entity details with sources for jason-duval and lucia-caminos, entity history, sources list, timeline, and auth/me rejection. No mutations performed. Backend ready for entire-site redesign. Recommend main agent to summarize and finish."
