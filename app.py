import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import requests
import re
import json
import plotly.express as px

# ==========================================
# 1. INIZIALIZZAZIONE DATI E SESSIONI
# ==========================================
st.set_page_config(page_title="AI Resource Manager", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def genera_database():
    nomi_completi = [
        "Marco Rossi", "Giulia Bianchi", "Luca Neri", "Anna Verdi", "Matteo Colombo", "Sofia Ferrari",
        "Andrea Romano", "Martina Bruno", "Alessandro Gallo", "Chiara Conti", "Davide Costa", "Sara Giordano",
        "Lorenzo Rizzo", "Francesca Lombardi", "Simone Moretti", "Elena Barbieri", "Gabriele Fontana",
        "Valentina Santoro", "Emanuele Mariani", "Silvia Rinaldi", "Riccardo Ferrara", "Laura Galli",
        "Federico Martini", "Alessia Leone", "Stefano Longo", "Giorgia Gentile", "Daniele Martinelli",
        "Roberta Vitale", "Michele Lombardo", "Ilaria Coppola", "Tommaso De Luca", "Elisa Mancini",
        "Antonio Costa", "Paola Fiore", "Giovanni Marchetti", "Serena Parisi", "Roberto Villa",
        "Caterina Conte", "Francesco Ferri", "Marta Bianco"
    ]
    
    ruoli_skills = [
        ("Frontend Developer", ["React", "Vue", "TypeScript", "HTML/CSS"], "IT"),
        ("Backend Developer", ["Node.js", "Python", "Java", "Go", "C#"], "IT"),
        ("Fullstack Developer", ["React", "Node.js", "Python", "TypeScript", "SQL"], "IT"),
        ("DevOps Engineer", ["AWS", "Docker", "Kubernetes", "CI/CD", "Terraform"], "IT"),
        ("Data Scientist", ["Python", "Machine Learning", "SQL", "Pandas"], "Data Science"),
        ("Data Analyst", ["Excel", "Python", "SQL", "PowerBI"], "Data Science"),
        ("Business Analyst", ["Excel", "SQL", "BPMN"], "Risk/Management"),
        ("Project Manager", ["Agile", "Scrum", "Jira"], "Risk/Management")
    ]
    
    clienti_italiani = ["Enel", "TIM", "Poste Italiane", "Intesa Sanpaolo", "Unicredit", "Ferrari", "Eni", "Leonardo", "Ferrovie dello Stato", "Pirelli"]
    tipi_progetto = ["Piattaforma e-commerce", "App Mobile B2C", "Gestionale ERP", "Dashboard IoT", "Sistema Pagamenti", "Migrazione Cloud"]
    
    db = []
    for i, nome in enumerate(nomi_completi):
        ruolo, skills_possibili, macro_area = random.choice(ruoli_skills)
        skills = random.sample(skills_possibili, k=random.randint(2, len(skills_possibili)))
        seniority = random.choice(["Junior", "Mid", "Senior"])
        costo_base = {"Junior": 150, "Mid": 250, "Senior": 350}[seniority]
        occupazione = random.choice([0, 0, 50, 100])
        giorni_offset = random.randint(5, 30) if occupazione > 0 else 0
        disp_dal = (datetime.now() + timedelta(days=giorni_offset)).strftime("%Y-%m-%d")
        
        esperienze = []
        num_progetti = {"Junior": 1, "Mid": 2, "Senior": 3}[seniority]
        for _ in range(num_progetti):
            esperienze.append({
                "Cliente": random.choice(clienti_italiani),
                "Progetto": random.choice(tipi_progetto),
                "Tecnologie_Usate": random.sample(skills, k=random.randint(1, len(skills)))
            })
        
        db.append({
            "ID": f"RES-{1000+i}",
            "Nome": nome,
            "Macro_Area": macro_area,
            "Ruolo": f"{seniority} {ruolo}",
            "Seniority": seniority,
            "Skill": ", ".join(skills),
            "Esperienze": esperienze,
            "Costo_Giorno": costo_base,
            "Tariffa_Vendita": costo_base * 1.4, 
            "Occupazione_%": occupazione,
            "Disponibile_dal": disp_dal
        })
    return pd.DataFrame(db)

if "df_risorse" not in st.session_state:
    st.session_state.df_risorse = genera_database()
if "pending_approvals" not in st.session_state:
    st.session_state.pending_approvals = []
if "pending_allocations" not in st.session_state:
    st.session_state.pending_allocations = []

# Variabili Chatbot
if "chat_msgs" not in st.session_state:
    st.session_state.chat_msgs = [{"role": "assistant", "content": "Ciao! Sono il tuo Copilot AI. Scrivimi un comando, ad esempio:\n- *Alloca Marco Rossi su progetto TIM al 50%*\n- *Promuovi Giulia Bianchi a Senior*"}]
if "bot_action" not in st.session_state:
    st.session_state.bot_action = None

if "pm_logged_in" not in st.session_state: st.session_state.pm_logged_in = False
if "it_logged_in" not in st.session_state: st.session_state.it_logged_in = False
if "hr_logged_in" not in st.session_state: st.session_state.hr_logged_in = False
if "current_it_user" not in st.session_state: st.session_state.current_it_user = None
if "api_key_hf" not in st.session_state: st.session_state.api_key_hf = ""

# ==========================================
# 2. MOTORI SMART E VERO LLM (HUGGING FACE)
# ==========================================
def analizza_testo(testo):
    testo_lower = testo.lower()
    competenze_trovate = []
    regole = {
        "react": ("React", 15), "vue": ("Vue", 12), "angular": ("Angular", 15),
        "node": ("Node.js", 20), "python": ("Python", 18), "java ": ("Java", 25),
        "aws": ("AWS", 10), "docker": ("Docker", 5), "kubernetes": ("Kubernetes", 10),
        "machine learning": ("Machine Learning", 20), "sql": ("SQL", 8), "typescript": ("TypeScript", 10)
    }
    
    fasi = []
    for key, (skill, giorni) in regole.items():
        if key in testo_lower:
            competenze_trovate.append(skill)
            fasi.append({"Fase": f"Sviluppo {skill}", "Skill": skill, "Giorni": giorni})
            
    if not fasi:
        fasi = [{"Fase": "Analisi e Setup", "Skill": "Node.js", "Giorni": 10}]
        competenze_trovate = ["Node.js"]
        
    return fasi, competenze_trovate

def parse_chatbot_intent_llm(prompt, df, api_key):
    """
    Usa il VERO modello Mistral tramite chiamate API REST dirette ad Hugging Face (non serve installare la libreria!).
    """
    if not api_key:
        return fallback_simulatore_chatbot(prompt, df)
        
    # Prepariamo il contesto per l'AI
    lista_nomi = ", ".join(df['Nome'].tolist())
    
    system_prompt = f"""
    Sei l'assistente virtuale di un sistema HR/Project Management.
    Il tuo compito è estrarre l'intento dell'utente e restituire ESCLUSIVAMENTE un JSON valido.
    
    Dipendenti a sistema: {lista_nomi}
    
    Se l'utente chiede di ALLOCARE o ASSEGNARE un dipendente, restituisci questo JSON:
    {{
      "azione": "alloca",
      "nome": "Nome e Cognome trovato nel database",
      "percentuale": numero (es. 50, se non specificato usa 100),
      "cliente": "Nome del cliente o progetto (es. TIM, Progetto Alfa)",
      "messaggio_riepilogo": "Vado ad allocare [Nome] al [X]% sul progetto [Cliente]."
    }}
    
    Se l'utente chiede di PROMUOVERE o CAMBIARE LIVELLO, restituisci questo JSON:
    {{
      "azione": "promuovi",
      "nome": "Nome e Cognome trovato nel database",
      "nuova_seniority": "Junior, Mid o Senior",
      "messaggio_riepilogo": "Vado a promuovere [Nome] al livello [Seniority]."
    }}
    
    Se non capisci l'intento o la persona non esiste, restituisci:
    {{
      "azione": "errore",
      "messaggio_riepilogo": "Spiega cordialmente in italiano che non hai capito l'operazione o non trovi il dipendente."
    }}
    
    ATTENZIONE: Restituisci SOLO testo JSON pulito. Niente markdown. Niente backtick. Non scrivere altre frasi.
    """
    
    # Endpoint standard di Hugging Face per i modelli di chat
    url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 200
    }
    
    try:
        # Chiamata HTTP nativa (usa requests, preinstallato)
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 503:
            return None, "⚠️ Il modello su Hugging Face si sta svegliando (è gratuito e si iberna se non usato). Riprova tra 10 secondi!"
        elif response.status_code != 200:
            return None, f"⚠️ Errore API: Controlla che la chiave sia corretta. ({response.status_code})"
            
        risposta_raw = response.json()["choices"][0]["message"]["content"].strip()
        
        # Pulisce la risposta da eventuali formattazioni markdown non richieste
        if risposta_raw.startswith("```json"):
            risposta_raw = risposta_raw.replace("```json", "").replace("```", "").strip()
        elif risposta_raw.startswith("```"):
            risposta_raw = risposta_raw.replace("```", "").strip()
            
        dati_json = json.loads(risposta_raw)
        
        if dati_json.get("azione") == "errore":
            return None, dati_json.get("messaggio_riepilogo")
            
        if dati_json.get("azione") == "alloca":
            return {
                "type": "alloca",
                "nome": dati_json["nome"],
                "perc": dati_json["percentuale"],
                "cliente": dati_json["cliente"],
                "desc": dati_json["messaggio_riepilogo"]
            }, None
            
        if dati_json.get("azione") == "promuovi":
            return {
                "type": "promuovi",
                "nome": dati_json["nome"],
                "nuova_sen": dati_json["nuova_seniority"],
                "desc": dati_json["messaggio_riepilogo"]
            }, None
            
    except Exception as e:
        return None, f"⚠️ Errore di decodifica AI: {str(e)}\nRisposta ricevuta dall'AI: {risposta_raw if 'risposta_raw' in locals() else 'Nessuna'}"

def fallback_simulatore_chatbot(prompt, df):
    """Il mock usato se non hai messo l'API Key o se c'è un problema temporaneo di rete"""
    prompt_l = prompt.lower()
    nome_trovato = None
    for nome in df['Nome']:
        if nome.lower() in prompt_l:
            nome_trovato = nome
            break
            
    if not nome_trovato:
        return None, "Non sono riuscito a trovare il nome del consulente nel messaggio. (Modalità Simulatore attiva: inserisci la API Key HuggingFace per l'AI vera!)"
        
    if "alloca" in prompt_l or "assegna" in prompt_l:
        perc_match = re.search(r'(\d+)%', prompt_l)
        perc = int(perc_match.group(1)) if perc_match else 100
        cliente = "Progetto AI"
        match_cliente = re.search(r'(?:su|progetto|cliente)\s+(\w+)', prompt_l)
        if match_cliente: cliente = match_cliente.group(1).capitalize()
        desc = f"Vado ad allocare **{nome_trovato}** al **{perc}%** sul cliente **{cliente}**."
        return {"type": "alloca", "nome": nome_trovato, "perc": perc, "cliente": cliente, "desc": desc}, None

    if "promuovi" in prompt_l or "livello" in prompt_l:
        nuova_sen = "Senior" if "senior" in prompt_l else "Mid" if "mid" in prompt_l else "Junior"
        desc = f"Vado a promuovere **{nome_trovato}** al livello **{nuova_sen}**."
        return {"type": "promuovi", "nome": nome_trovato, "nuova_sen": nuova_sen, "desc": desc}, None
        
    return None, "Non ho capito l'operazione. Prova con 'Alloca' o 'Promuovi'. (Modalità Simulatore attiva)"

def esegui_azione_chatbot():
    action = st.session_state.bot_action
    df = st.session_state.df_risorse
    idx = df.index[df['Nome'] == action['nome']].tolist()[0]
    
    if action['type'] == 'alloca':
        df.at[idx, 'Occupazione_%'] = action['perc']
        disp_data = datetime.now() + timedelta(days=30)
        df.at[idx, 'Disponibile_dal'] = disp_data.strftime("%Y-%m-%d")
        df.at[idx, 'Esperienze'].append({"Cliente": action['cliente'], "Progetto": "Assegnazione da AI Copilot", "Tecnologie_Usate": []})
        msg = f"✅ Successo: **{action['nome']}** assegnato a **{action['cliente']}**."
        
    elif action['type'] == 'promuovi':
        ruolo_puro = df.at[idx, 'Ruolo'].replace('Senior ', '').replace('Mid ', '').replace('Junior ', '')
        df.at[idx, 'Seniority'] = action['nuova_sen']
        df.at[idx, 'Ruolo'] = f"{action['nuova_sen']} {ruolo_puro}"
        msg = f"✅ Successo: **{action['nome']}** è stato promosso a **{action['nuova_sen']}**."

    st.session_state.bot_action = None
    st.session_state.chat_msgs.append({"role": "assistant", "content": msg})

# ==========================================
# 3. SIDEBAR BASE E LOGOUT INCROCIATI
# ==========================================
st.sidebar.title("🔐 Accesso Sistema")
ruolo_utente = st.sidebar.radio("Scegli il tuo ruolo:", ["Project Manager", "HR (Risorse Umane)", "Consulente"])

if ruolo_utente != "Project Manager": st.session_state.pm_logged_in = False
if ruolo_utente != "Consulente": 
    st.session_state.it_logged_in = False
    st.session_state.current_it_user = None
if ruolo_utente != "HR (Risorse Umane)": st.session_state.hr_logged_in = False

df = st.session_state.df_risorse

# ---------------------------------------------------------
# IMPOSTAZIONI VERO LLM (HUGGING FACE)
# ---------------------------------------------------------
if ruolo_utente in ["Project Manager", "HR (Risorse Umane)"]:
    with st.sidebar.expander("⚙️ Impostazioni Vero LLM (Gratis)"):
        st.write("Usa l'intelligenza di **Mistral-7B** tramite Hugging Face API.")
        api_key = st.text_input("Inserisci Hugging Face Token (hf_...):", value=st.session_state.api_key_hf, type="password")
        if st.button("Salva Chiave"):
            st.session_state.api_key_hf = api_key
            st.success("Token salvato! Il Copilot è ora intelligente.")

# ---------------------------------------------------------
# CHATBOT WIDGET (Visibile per PM e HR)
# ---------------------------------------------------------
if (st.session_state.pm_logged_in or st.session_state.hr_logged_in):
    st.sidebar.markdown("---")
    with st.sidebar.popover("💬 Assistente AI (Copilot)", use_container_width=True):
        st.markdown("**Copilot Aziendale**")
        if st.session_state.api_key_hf:
            st.caption("🟢 *Modello: Mistral-7B (Hugging Face)*")
        else:
            st.caption("🟠 *Modello: Simulatore Base (Inserisci il Token HF per sbloccare l'AI vera)*")
        
        # Mostra messaggi precedenti
        for msg in st.session_state.chat_msgs:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # Mostra UI di Conferma Azione (se presente)
        if st.session_state.bot_action:
            st.info(st.session_state.bot_action['desc'])
            col_ok, col_ko = st.columns(2)
            if col_ok.button("✅ Esegui"):
                esegui_azione_chatbot()
                st.rerun()
            if col_ko.button("❌ Annulla"):
                st.session_state.bot_action = None
                st.session_state.chat_msgs.append({"role": "assistant", "content": "Operazione annullata. Posso aiutarti in altro?"})
                st.rerun()

        # Input utente
        if prompt := st.chat_input("Chiedi all'AI (es. Alloca Luca Neri su TIM al 50%)..."):
            st.session_state.chat_msgs.append({"role": "user", "content": prompt})
            
            with st.spinner("L'AI sta ragionando..."):
                action_dict, error_msg = parse_chatbot_intent_llm(prompt, st.session_state.df_risorse, st.session_state.api_key_hf)
            
            if error_msg:
                st.session_state.chat_msgs.append({"role": "assistant", "content": error_msg})
            else:
                st.session_state.bot_action = action_dict
                st.session_state.chat_msgs.append({"role": "assistant", "content": "Ecco cosa ho capito. Confermi l'esecuzione?"})
            st.rerun()

# ==========================================
# VISTA 1: CONSULENTE
# ==========================================
if ruolo_utente == "Consulente":
    if not st.session_state.it_logged_in:
        st.title("🔒 Accesso Area Personale")
        with st.form("login_it_form"):
            utente_selezionato = st.selectbox("Chi sei?", df['Nome'].tolist())
            password_it = st.text_input("Password", type="password", help="Password: dev123")
            if st.form_submit_button("Accedi"):
                if password_it == "dev123":
                    st.session_state.it_logged_in = True
                    st.session_state.current_it_user = utente_selezionato
                    st.rerun()
                else: st.error("Password errata.")
    else:
        st.title(f"👤 Dashboard Personale - {st.session_state.current_it_user}")
        if st.button("Esci (Logout)"):
            st.session_state.it_logged_in = False
            st.rerun()
            
        dati_utente = df[df['Nome'] == st.session_state.current_it_user].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Le tue Info")
            st.write(f"**Qualifica:** {dati_utente['Ruolo']}")
            st.write(f"**Skill Validate:** {dati_utente['Skill']}")
            st.write(f"**Stato:** Occupato al {dati_utente['Occupazione_%']}%")
            
            st.markdown("---")
            st.write("**Richiedi Validazione Skill**")
            nuova_skill = st.text_input("Aggiungi competenza (es. GraphQL):")
            if st.button("Invia Skill al PM"):
                if nuova_skill.strip():
                    st.session_state.pending_approvals.append({"ID": dati_utente['ID'], "Nome": dati_utente['Nome'], "Skill": nuova_skill.strip()})
                    st.success("Richiesta inviata!")
                    
        with c2:
            st.subheader("📅 Richiedi Allocazione / Slot")
            st.info("I consulenti non possono auto-allocarsi. Invia una richiesta al PM per occupare uno slot in agenda.")
            with st.form("richiesta_alloc"):
                progetto_req = st.text_input("Nome Progetto / Cliente")
                disp_req = st.slider("Percentuale di impegno richiesta (%)", 25, 100, 50, step=25)
                date_req = st.date_input("Periodo", value=(datetime.today(), datetime.today() + timedelta(days=30)))
                if st.form_submit_button("Invia Richiesta di Allocazione"):
                    if len(date_req) == 2:
                        st.session_state.pending_allocations.append({
                            "ID": dati_utente['ID'], "Nome": dati_utente['Nome'], 
                            "Progetto": progetto_req, "Occupazione": disp_req, 
                            "Dal": date_req[0], "Al": date_req[1]
                        })
                        st.success("Richiesta di allocazione inviata al manager!")
                    else:
                        st.error("Seleziona una data di inizio e fine.")

# ==========================================
# VISTA 2: PROJECT MANAGER
# ==========================================
elif ruolo_utente == "Project Manager":
    if not st.session_state.pm_logged_in:
        st.title("🔒 Accesso PM")
        with st.form("login_pm_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password", help="admin / admin123")
            if st.form_submit_button("Accedi"):
                if username == "admin" and password == "admin123":
                    st.session_state.pm_logged_in = True
                    st.rerun()
                else: st.error("Credenziali errate.")
    else:
        num_req_alloc = len(st.session_state.pending_allocations)
        tab_allocazioni = f"📅 Pianificazione & Allocazioni ({num_req_alloc})" if num_req_alloc > 0 else "📅 Pianificazione & Allocazioni"
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ Navigazione PM")
        pagina_pm = st.sidebar.radio("Vai a:", [
            "🏠 Homepage & Alert", 
            "🚀 Scoping & Staffing AI",
            tab_allocazioni,
            "👤 Analisi Profili & Assegnazioni", 
            "🗄️ Master Data (Database)"
        ])
        
        if st.sidebar.button("🚪 Esci (Logout)"):
            st.session_state.pm_logged_in = False
            st.rerun()

        # =====================================
        # PM 1: HOMEPAGE
        # =====================================
        if pagina_pm == "🏠 Homepage & Alert":
            st.title("Centro di Controllo Manageriale")
            
            if num_req_alloc > 0:
                st.warning(f"🔔 **ATTENZIONE:** Hai **{num_req_alloc}** nuove richieste di allocazione in attesa. Vai nella sezione Pianificazione & Allocazioni per gestirle.")
            
            st.markdown("""
            <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <h4>👤 Profilo Manager: Admin</h4>
                <p><b>Ruolo:</b> Senior IT Delivery Manager<br><b>Dipartimento:</b> Digital Transformation</p>
            </div>
            """, unsafe_allow_html=True)
            
            tot_risorse = len(df)
            occupate = len(df[df['Occupazione_%'] > 0])
            ferme = tot_risorse - occupate
            
            mancati_incassi_gg = df[df['Occupazione_%'] == 0]['Tariffa_Vendita'].sum()
            revenue_attiva_gg = (df['Tariffa_Vendita'] * (df['Occupazione_%']/100)).sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Risorse Totali", tot_risorse)
            c2.metric("Risorse Staffate", occupate)
            c3.metric("Mancati Incassi Bench (gg)", f"€ {mancati_incassi_gg:,.2f}", help="Ricavo perso giornalmente per le risorse ferme (costo opportunità).")
            c4.metric("Revenue Attesa (gg)", f"€ {revenue_attiva_gg:,.2f}")
            
            st.markdown("---")
            st.subheader("📊 Bilancio Portafoglio: Ricavi Attivi vs Mancati Ricavi")
            df_fin = pd.DataFrame({
                "Categoria": ["Mancati Ricavi (Bench)", "Ricavi Attivi (Staffati)"],
                "Valore Giornaliero": [mancati_incassi_gg, revenue_attiva_gg]
            })
            fig_fin = px.pie(df_fin, values='Valore Giornaliero', names='Categoria', hole=0.3,
                             color='Categoria', color_discrete_map={"Mancati Ricavi (Bench)": "#FF4B4B", "Ricavi Attivi (Staffati)": "#00CC96"})
            st.plotly_chart(fig_fin, use_container_width=True)

        # =====================================
        # PM 2: SCOPING & STAFFING AI
        # =====================================
        elif pagina_pm == "🚀 Scoping & Staffing AI":
            st.title("🤖 Scoping Dinamico & Scenario Analysis")
            st.info("💡 **Come usare questa sezione per la Demo:** Incolla il testo del progetto. Una volta generate le tabelle, **modifica i giorni o il margine in percentuale direttamente dentro la griglia**. Vedrai il *Breakdown Finanziario* in basso aggiornarsi in tempo reale!")
            
            testo_da_analizzare = st.text_area("Requisiti di progetto (Scrivi qui cosa serve al cliente):", height=100)

            if st.button("Genera WBS e Team", type="primary") or "wbs_data" in st.session_state:
                if testo_da_analizzare and "wbs_data" not in st.session_state:
                    fasi, skill_richieste = analizza_testo(testo_da_analizzare)
                    st.session_state.wbs_data = pd.DataFrame(fasi)
                    
                    team_proposto = []
                    for skill in skill_richieste:
                        candidati = df[df['Occupazione_%'] < 100]
                        match_trovato = False
                        for _, risorsa in candidati.iterrows():
                            if skill.lower() in risorsa['Skill'].lower():
                                team_proposto.append({
                                    "Skill": skill, "Nome": risorsa['Nome'], "Costo_gg": risorsa['Costo_Giorno'], "Margine_%": 30
                                })
                                match_trovato = True
                                break 
                        if not match_trovato:
                            team_proposto.append({"Skill": skill, "Nome": "DA ASSUMERE", "Costo_gg": 300, "Margine_%": 30})
                    st.session_state.team_data = pd.DataFrame(team_proposto)

                if "wbs_data" in st.session_state:
                    st.markdown("### 1. WBS & Stima Tempi (Tabella Interattiva)")
                    st.caption("Fai doppio clic sui giorni per modificarli e vedere l'impatto sui costi.")
                    edited_wbs = st.data_editor(st.session_state.wbs_data, num_rows="dynamic", key="wbs_editor", use_container_width=True)
                    
                    st.markdown("### 2. Team Consigliato e Marginalità (Tabella Interattiva)")
                    st.caption("Fai doppio clic sul margine per applicare uno scenario di vendita diverso.")
                    edited_team = st.data_editor(st.session_state.team_data, key="team_editor", use_container_width=True)
                    
                    costo_totale_progetto = 0
                    proposta_commerciale = 0
                    
                    for idx, row in edited_wbs.iterrows():
                        skill_fase = row['Skill']
                        giorni = row['Giorni']
                        
                        membro = edited_team[edited_team['Skill'] == skill_fase]
                        if not membro.empty:
                            c_gg = membro.iloc[0]['Costo_gg']
                            margine = membro.iloc[0]['Margine_%']
                            costo_fase = giorni * c_gg
                            ricavo_fase = costo_fase * (1 + (margine / 100))
                            
                            costo_totale_progetto += costo_fase
                            proposta_commerciale += ricavo_fase
                    
                    st.markdown("""
                    <div style='background-color: #e6f3ff; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 5px solid #0066cc;'>
                        <h3 style='margin-top: 0;'>💰 Breakdown Finanziario (Aggiornato in Tempo Reale)</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c_fin1, c_fin2, c_fin3 = st.columns(3)
                    c_fin1.metric("Costo Vivo Progetto", f"€ {costo_totale_progetto:,.2f}")
                    c_fin2.metric("Proposta Commerciale", f"€ {proposta_commerciale:,.2f}")
                    margine_assoluto = proposta_commerciale - costo_totale_progetto
                    c_fin3.metric("Margine Netto Finale", f"€ {margine_assoluto:,.2f}")

        # =====================================
        # PM 3: PIANIFICAZIONE & ALLOCAZIONI
        # =====================================
        elif pagina_pm == tab_allocazioni:
            st.title("Gestione Agende e Allocazioni")
            st.markdown("""
            **Come funziona questa pagina:**
            Qui decidi su quali progetti lavorano le tue persone. Puoi farlo in due modi:
            1. **Reagendo:** Accettando le richieste di slot che i consulenti hanno inserito dal loro portale.
            2. **Agendo (Manuale):** Allocando tu stesso un consulente specificando Cliente, Progetto e Periodo.
            """)
            st.divider()
            
            st.subheader("1. Richieste in attesa dal team")
            if len(st.session_state.pending_allocations) > 0:
                for i, req in enumerate(list(st.session_state.pending_allocations)):
                    with st.container():
                        st.info(f"👤 **{req['Nome']}** richiede il {req['Occupazione']}% per il progetto **{req['Progetto']}** ({req['Dal']} - {req['Al']})")
                        b1, b2 = st.columns(2)
                        if b1.button("✅ Approva Allocazione", key=f"alloc_ok_{i}"):
                            idx = df.index[df['ID'] == req['ID']].tolist()[0]
                            st.session_state.df_risorse.at[idx, 'Occupazione_%'] = req['Occupazione']
                            st.session_state.df_risorse.at[idx, 'Disponibile_dal'] = req['Al'].strftime("%Y-%m-%d")
                            st.session_state.df_risorse.at[idx, 'Esperienze'].append({
                                "Cliente": "Cliente/Progetto Interno", 
                                "Progetto": req['Progetto'], 
                                "Tecnologie_Usate": []
                            })
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
                        if b2.button("❌ Rifiuta", key=f"alloc_ko_{i}"):
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
            else:
                st.success("Nessuna richiesta in sospeso dai consulenti.")
                
            st.divider()
            st.subheader("2. Assegnazione Manuale Diretta (Top-Down)")
            
            col_filt1, col_filt2 = st.columns(2)
            seniority_alloc = col_filt1.selectbox("Filtra per Livello:", ["Tutti", "Senior", "Mid", "Junior"], key="sen_alloc")
            df_alloc_filt = df if seniority_alloc == "Tutti" else df[df['Seniority'] == seniority_alloc]
            
            with st.form("manual_alloc"):
                r_scelta = st.selectbox("Seleziona Consulente:", df_alloc_filt['Nome'].tolist())
                
                c_form1, c_form2 = st.columns(2)
                cliente_input = c_form1.text_input("Nome Cliente (Es: Enel, Poste)")
                progetto_input = c_form2.text_input("Tipo Progetto / Lavoro (Es: Sviluppo App, Manutenzione)")
                tech_input = st.text_input("Tecnologie che utilizzerà (Separate da virgola, es: React, AWS, Java)")
                
                c_form3, c_form4 = st.columns(2)
                oggi = datetime.today()
                date_range = c_form3.date_input("Periodo di Allocazione", value=(oggi, oggi + timedelta(days=60)))
                perc = c_form4.slider("Assegna Percentuale di Occupazione %", 0, 100, 100, step=25)
                
                submit_alloc = st.form_submit_button("Forza Allocazione a Calendario e Aggiorna CV")
                
                if submit_alloc:
                    if len(date_range) == 2 and cliente_input and progetto_input:
                        start_date, end_date = date_range
                        idx = df.index[df['Nome'] == r_scelta].tolist()[0]
                        
                        st.session_state.df_risorse.at[idx, 'Occupazione_%'] = perc
                        st.session_state.df_risorse.at[idx, 'Disponibile_dal'] = end_date.strftime("%Y-%m-%d")
                        
                        tech_list = [t.strip() for t in tech_input.split(",")] if tech_input else []
                        nuova_esperienza = {
                            "Cliente": cliente_input,
                            "Progetto": progetto_input,
                            "Tecnologie_Usate": tech_list
                        }
                        st.session_state.df_risorse.at[idx, 'Esperienze'].append(nuova_esperienza)
                        
                        st.success(f"✅ {r_scelta} è stato allocato al {perc}% dal {start_date} al {end_date} per il cliente {cliente_input}. Il suo profilo è stato aggiornato con queste nuove esperienze!")
                    else:
                        st.error("Per favore compila tutti i campi testuali e seleziona una data di inizio e fine valida.")

        # =====================================
        # PM 4: ANALISI PROFILI
        # =====================================
        elif pagina_pm == "👤 Analisi Profili & Assegnazioni":
            st.title("Indagine Risorse")
            c_filtro1, c_filtro2 = st.columns(2)
            seniority_scelta = c_filtro1.selectbox("1. Filtra per Livello (Seniority):", ["Tutti", "Senior", "Mid", "Junior"], key="sen_analisi")
            df_filtrato = df if seniority_scelta == "Tutti" else df[df['Seniority'] == seniority_scelta]
            
            nome_ricerca = c_filtro2.selectbox("2. Seleziona Consulente:", df_filtrato['Nome'].tolist())
            if nome_ricerca:
                dati_ricerca = df_filtrato[df_filtrato['Nome'] == nome_ricerca].iloc[0]
                
                c1, c2, c3 = st.columns(3)
                c1.info(f"**Qualifica:** {dati_ricerca['Ruolo']}")
                c2.success(f"**Hard Skills:** {dati_ricerca['Skill']}")
                c3.warning(f"**Stato Attuale:** Occupato {dati_ricerca['Occupazione_%']}%")
                
                st.markdown("---")
                col_grafico, col_dettagli = st.columns([1, 1])
                with col_grafico:
                    st.subheader("📅 Riassunto Occupazione")
                    oggi = datetime.today().date()
                    date_range = st.date_input("Analizza periodo:", value=(oggi, oggi + timedelta(days=30)))
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        data_libero = datetime.strptime(dati_ricerca['Disponibile_dal'], "%Y-%m-%d").date()
                        date_list = pd.date_range(start=start_date, end=end_date)
                        giorni_occupati = sum(1 for d in date_list if d.date() < data_libero)
                        giorni_liberi = len(date_list) - giorni_occupati
                        
                        df_pie = pd.DataFrame({"Stato": ["Staffato (Ricavo)", "Panchina (Costo)"], "Giorni": [giorni_occupati, giorni_liberi]})
                        fig = px.pie(df_pie, values='Giorni', names='Stato', hole=0.4, color='Stato', 
                                     color_discrete_map={"Staffato (Ricavo)": "#00CC96", "Panchina (Costo)": "#FF4B4B"})
                        st.plotly_chart(fig, use_container_width=True)
                
                with col_dettagli:
                    st.subheader("🗓️ Dettaglio Giornaliero")
                    if len(date_range) == 2:
                        vista_scelta = st.radio("Seleziona Vista:", ["Tabella Dettagliata", "Calendario Visivo"], horizontal=True)
                        
                        if vista_scelta == "Tabella Dettagliata":
                            dettaglio = [{"Data": d.strftime("%Y-%m-%d"), "Giorno": d.strftime("%A"), "Stato": f"Occupato al {dati_ricerca['Occupazione_%']}%" if d.date() < data_libero else "Libero 100%"} for d in date_list]
                            st.dataframe(pd.DataFrame(dettaglio), height=350)
                        
                        else:
                            st.markdown("""
                            <div style="display:flex; gap:15px; margin-bottom:15px;">
                                <div style="display:flex; align-items:center;"><div style="width:15px; height:15px; background:#FF4B4B; margin-right:5px;"></div> Libero (0%) - Costo</div>
                                <div style="display:flex; align-items:center;"><div style="width:15px; height:15px; background:#FFD700; margin-right:5px;"></div> Impegno Parziale (&lt;100%)</div>
                                <div style="display:flex; align-items:center;"><div style="width:15px; height:15px; background:#00CC96; margin-right:5px;"></div> Impegnato (100%) - Ricavo</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            html_cal = "<div style='display:flex; flex-wrap:wrap; gap:5px; margin-top:10px;'>"
                            for d in date_list:
                                occ = dati_ricerca['Occupazione_%'] if d.date() < data_libero else 0
                                if occ == 0:
                                    bg_color = "#FF4B4B" # Rosso (Bench)
                                elif occ < 100:
                                    bg_color = "#FFD700" # Giallo (Parziale)
                                else:
                                    bg_color = "#00CC96" # Verde (Staffato)
                                
                                html_cal += f"<div style='width:45px; height:45px; background-color:{bg_color}; display:flex; align-items:center; justify-content:center; border-radius:5px; color:#333; font-weight:bold; cursor:pointer;' title='{d.strftime('%Y-%m-%d')} | Occupazione: {occ}%'>{d.day}</div>"
                            html_cal += "</div>"
                            st.markdown(html_cal, unsafe_allow_html=True)

        # =====================================
        # PM 5: MASTER DATA
        # =====================================
        elif pagina_pm == "🗄️ Master Data (Database)":
            st.title("Vista Tabellare Completa")
            df_display = df.drop(columns=['Esperienze'])
            st.dataframe(df_display, use_container_width=True)

# ==========================================
# VISTA 3: HR (RISORSE UMANE)
# ==========================================
elif ruolo_utente == "HR (Risorse Umane)":
    if not st.session_state.hr_logged_in:
        st.title("🔒 Accesso HR")
        with st.form("login_hr_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password", help="Usa hr / hr123")
            if st.form_submit_button("Accedi"):
                if username == "hr" and password == "hr123":
                    st.session_state.hr_logged_in = True
                    st.rerun()
                else: st.error("Credenziali errate.")
    else:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ Navigazione HR")
        pagina_hr = st.sidebar.radio("Vai a:", [
            "🏠 Dashboard HR", 
            "➕ Onboarding Nuovo Assunto",
            "✏️ Gestione e Promozioni",
            "📥 Integrazione Zucchetti", 
            "🗄️ Master Data Dipendenti"
        ])
        if st.sidebar.button("🚪 Esci (Logout)"):
            st.session_state.hr_logged_in = False
            st.rerun()

        # =====================================
        # HR 1: DASHBOARD
        # =====================================
        if pagina_hr == "🏠 Dashboard HR":
            st.title("Dashboard Risorse Umane")
            st.info("Panoramica sulla composizione della forza lavoro aziendale.")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Totale Dipendenti (Headcount)", len(df))
            c2.metric("Età Media (Figurativa)", "32 Anni")
            c3.metric("Costo Medio GG", f"€ {df['Costo_Giorno'].mean():.0f}")
            
            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Distribuzione Seniority")
                df_sen = df['Seniority'].value_counts().reset_index()
                df_sen.columns = ['Seniority', 'Conteggio']
                fig1 = px.pie(df_sen, values='Conteggio', names='Seniority', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_chart2:
                st.subheader("Distribuzione per Ruolo")
                
                aree_disponibili = ["Tutte le Aree"] + sorted(list(df['Macro_Area'].unique()))
                area_selezionata = st.selectbox("Filtra per Macro Area:", aree_disponibili)
                
                df_ruoli = df if area_selezionata == "Tutte le Aree" else df[df['Macro_Area'] == area_selezionata]
                
                df_ruoli = df_ruoli['Ruolo'].str.replace('Senior ', '').str.replace('Mid ', '').str.replace('Junior ', '').value_counts().reset_index()
                df_ruoli.columns = ['Ruolo', 'Conteggio']
                fig2 = px.bar(df_ruoli, x='Ruolo', y='Conteggio', color='Ruolo')
                st.plotly_chart(fig2, use_container_width=True)

        # =====================================
        # HR 2: ONBOARDING NUOVO ASSUNTO
        # =====================================
        elif pagina_hr == "➕ Onboarding Nuovo Assunto":
            st.title("Assunzione Nuovo Dipendente")
            st.write("Aggiungi una nuova risorsa al Database aziendale. Sarà immediatamente visibile ai Project Manager.")
            
            with st.form("form_onboarding"):
                col1, col2 = st.columns(2)
                nuovo_nome = col1.text_input("Nome e Cognome")
                nuova_sen = col2.selectbox("Seniority", ["Junior", "Mid", "Senior"])
                
                nuovo_ruolo = col1.selectbox("Titolo Professionale", ["Frontend Developer", "Backend Developer", "Fullstack Developer", "DevOps Engineer", "Data Scientist", "Data Analyst", "Project Manager", "Business Analyst"])
                nuove_skill = col2.text_input("Competenze Iniziali (Separate da virgola, es: React, Node)")
                
                macro_area_auto = "IT" if "Developer" in nuovo_ruolo or "DevOps" in nuovo_ruolo else "Data Science" if "Data" in nuovo_ruolo else "Risk/Management"
                
                costo_gg = col1.number_input("Costo Giornaliero Base (€)", min_value=50, max_value=1000, value=200)
                
                if st.form_submit_button("✅ Conferma Assunzione e Salva a DB"):
                    if nuovo_nome and nuove_skill:
                        nuovo_dipendente = pd.DataFrame([{
                            "ID": f"RES-{len(df)+1000}",
                            "Nome": nuovo_nome,
                            "Macro_Area": macro_area_auto,
                            "Ruolo": f"{nuova_sen} {nuovo_ruolo}",
                            "Seniority": nuova_sen,
                            "Skill": nuove_skill,
                            "Esperienze": [],
                            "Costo_Giorno": costo_gg,
                            "Tariffa_Vendita": costo_gg * 1.4,
                            "Occupazione_%": 0, 
                            "Disponibile_dal": datetime.now().strftime("%Y-%m-%d")
                        }])
                        st.session_state.df_risorse = pd.concat([st.session_state.df_risorse, nuovo_dipendente], ignore_index=True)
                        st.success(f"Assunzione di {nuovo_nome} completata! Il dipendente è ora a sistema.")
                    else:
                        st.error("Per favore compila Nome e Competenze.")

        # =====================================
        # HR 3: GESTIONE E PROMOZIONI
        # =====================================
        elif pagina_hr == "✏️ Gestione e Promozioni":
            st.title("Gestione Dipendente e Promozioni")
            st.write("Aggiorna l'anagrafica, promuovi di livello o modifica il costo di una singola risorsa.")
            
            nome_ricerca = st.selectbox("Seleziona Dipendente da modificare:", df['Nome'].tolist())
            
            if nome_ricerca:
                idx = df.index[df['Nome'] == nome_ricerca].tolist()[0]
                dati_attuali = df.iloc[idx]
                
                with st.form("form_modifica_dipendente"):
                    st.subheader(f"Modifica Scheda: {dati_attuali['Nome']}")
                    c1, c2 = st.columns(2)
                    
                    nuovo_nome = c1.text_input("Nome e Cognome", value=dati_attuali['Nome'])
                    
                    ruolo_attuale_puro = dati_attuali['Ruolo'].replace('Senior ', '').replace('Mid ', '').replace('Junior ', '')
                    ruoli_disponibili = ["Frontend Developer", "Backend Developer", "Fullstack Developer", "DevOps Engineer", "Data Scientist", "Data Analyst", "Project Manager", "Business Analyst"]
                    if ruolo_attuale_puro not in ruoli_disponibili:
                        ruoli_disponibili.append(ruolo_attuale_puro)
                    
                    index_sen = ["Junior", "Mid", "Senior"].index(dati_attuali['Seniority'])
                    nuova_sen = c1.selectbox("Seniority", ["Junior", "Mid", "Senior"], index=index_sen)
                    
                    index_ruolo = ruoli_disponibili.index(ruolo_attuale_puro)
                    nuovo_ruolo = c2.selectbox("Titolo Professionale", ruoli_disponibili, index=index_ruolo)
                    
                    nuove_skill = st.text_input("Competenze (Separate da virgola)", value=dati_attuali['Skill'])
                    
                    c3, c4 = st.columns(2)
                    costo_gg = c3.number_input("Costo Giornaliero Base (€)", min_value=50, max_value=2000, value=int(dati_attuali['Costo_Giorno']))
                    tariffa_vendita = c4.number_input("Tariffa di Vendita (€)", min_value=50, max_value=3000, value=int(dati_attuali['Tariffa_Vendita']))
                    
                    if st.form_submit_button("💾 Salva Modifiche al Profilo"):
                        st.session_state.df_risorse.at[idx, 'Nome'] = nuovo_nome
                        st.session_state.df_risorse.at[idx, 'Seniority'] = nuova_sen
                        st.session_state.df_risorse.at[idx, 'Ruolo'] = f"{nuova_sen} {nuovo_ruolo}"
                        st.session_state.df_risorse.at[idx, 'Skill'] = nuove_skill
                        st.session_state.df_risorse.at[idx, 'Costo_Giorno'] = costo_gg
                        st.session_state.df_risorse.at[idx, 'Tariffa_Vendita'] = tariffa_vendita
                        st.success(f"I dati di {nuovo_nome} sono stati aggiornati con successo nel Master Data!")
                        st.rerun()

        # =====================================
        # HR 4: INTEGRAZIONE ZUCCHETTI
        # =====================================
        elif pagina_hr == "📥 Integrazione Zucchetti":
            st.title("Sincronizzazione Software Paghe / Zucchetti")
            st.info("Trattandosi di un modulo disaccoppiato, puoi scaricare il template o fare l'upload massivo per aggiornare le anagrafiche dei dipendenti.")
            
            st.subheader("1. Esporta dati attuali (Per Zucchetti)")
            df_export = df.drop(columns=['Esperienze', 'Macro_Area'], errors='ignore')
            csv_export = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica Export Zucchetti (CSV)", data=csv_export, file_name='export_hr_zucchetti.csv', mime='text/csv')
            
            st.markdown("---")
            st.subheader("2. Carica aggiornamenti da Zucchetti")
            uploaded_file = st.file_uploader("Upload file (.csv o .xlsx)", type=['csv', 'xlsx'])
            
            if uploaded_file is not None:
                with st.spinner("Sincronizzazione DB in corso..."):
                    if uploaded_file.name.endswith('.csv'):
                        new_df = pd.read_csv(uploaded_file)
                    else:
                        new_df = pd.read_excel(uploaded_file)
                    st.success("File letto correttamente! (In produzione andrebbe a sovrascrivere o fare un merge con il DB)")
                    st.dataframe(new_df.head(5))

        # =====================================
        # HR 5: MASTER DATA
        # =====================================
        elif pagina_hr == "🗄️ Master Data Dipendenti":
            st.title("Anagrafica Completa Dipendenti")
            st.write("Vista raw del database aziendale.")
            df_display = df.drop(columns=['Esperienze', 'Macro_Area'], errors='ignore')
            st.dataframe(df_display, use_container_width=True)
