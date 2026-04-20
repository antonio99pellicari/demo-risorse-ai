import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import re
import plotly.express as px
import calendar
import requests
import json

# ==========================================
# 1. INIZIALIZZAZIONE DATI E SESSIONI
# ==========================================
st.set_page_config(page_title="AI Resource Manager", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# --- INIEZIONE CSS SAAS (MODERN DARK THEME) ---
st.markdown("""
<style>
    /* Sfondo e font di base */
    .stApp { font-family: 'Inter', sans-serif; }
    
    /* Stile per i bottoni primari */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    /* KPI Cards personalizzate */
    .kpi-card {
        background-color: #1E2127;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .kpi-card.green { border-left-color: #00CC96; }
    .kpi-card.red { border-left-color: #FF4B4B; }
    .kpi-card.orange { border-left-color: #FFD700; }
    .kpi-card h3 { margin-top: 0; font-size: 13px; color: #9BA1A6; text-transform: uppercase; letter-spacing: 1px;}
    .kpi-card h2 { margin: 0; font-size: 28px; color: #FFFFFF; font-weight: 700;}
    
    /* Stile per le Tabs di Streamlit */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-size: 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

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
    
    clienti_italiani = ["Enel", "TIM", "Poste", "Intesa", "Unicredit", "Ferrari", "Eni", "Leonardo", "Ferrovie", "Pirelli"]
    tipi_progetto = ["Piattaforma e-commerce", "App Mobile", "Gestionale", "Dashboard IoT", "Sistema Pagamenti", "Migrazione Cloud"]
    
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

def estrai_progetto_attuale(row):
    """Estrae il progetto corrente se la risorsa è occupata"""
    if row.get('Occupazione_%', 0) > 0 and isinstance(row.get('Esperienze', []), list) and len(row['Esperienze']) > 0:
        ult = row['Esperienze'][-1]
        return f"{ult.get('Cliente', 'N/D')} - {ult.get('Progetto', 'N/D')}"
    return "Disponibile (Bench)"

if "df_risorse" not in st.session_state: st.session_state.df_risorse = genera_database()
if "pending_approvals" not in st.session_state: st.session_state.pending_approvals = []
if "pending_allocations" not in st.session_state: st.session_state.pending_allocations = []
if "cal_month_idx" not in st.session_state: st.session_state.cal_month_idx = 0
if "team_cal_idx" not in st.session_state: st.session_state.team_cal_idx = 0

# Variabili Chatbot
if "chat_msgs" not in st.session_state:
    st.session_state.chat_msgs = [{"role": "assistant", "content": "Ciao! Sono il tuo Copilot AI. Scrivimi un comando, ad esempio:\n- *Alloca Marco Rossi su TIM al 50%*\n- *Promuovi Giulia Bianchi a Senior*"}]
if "bot_action" not in st.session_state: st.session_state.bot_action = None
if "groq_api_key" not in st.session_state: st.session_state.groq_api_key = "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"

if "pm_logged_in" not in st.session_state: st.session_state.pm_logged_in = False
if "it_logged_in" not in st.session_state: st.session_state.it_logged_in = False
if "hr_logged_in" not in st.session_state: st.session_state.hr_logged_in = False
if "current_it_user" not in st.session_state: st.session_state.current_it_user = None

# ==========================================
# 2. MOTORI AI E COPILOT
# ==========================================
def analizza_testo(testo):
    """Motore Deterministico (Rules Engine MVP) per lo Scoping"""
    testo_lower = testo.lower()
    competenze_trovate = []
    regole = {
        "react": ("React", 15), "vue": ("Vue", 12), "angular": ("Angular", 15),
        "node": ("Node.js", 20), "python": ("Python", 18), "java": ("Java", 25),
        "aws": ("AWS", 10), "docker": ("Docker", 5), "kubernetes": ("Kubernetes", 10),
        "machine learning": ("Machine Learning", 20), "sql": ("SQL", 8), "typescript": ("TypeScript", 10)
    }
    
    fasi = []
    for key, (skill, giorni) in regole.items():
        if key in testo_lower:
            competenze_trovate.append(skill)
            fasi.append({"Fase": f"Sviluppo {skill}", "Skill": skill, "Giorni": giorni})
            
    return fasi, competenze_trovate

def fallback_simulatore_chatbot(prompt, df):
    """Simulatore Regex se non c'è l'API Key Groq"""
    prompt_l = prompt.lower()
    nome_trovato = None
    for nome in df['Nome']:
        if nome.lower() in prompt_l:
            nome_trovato = nome
            break
    if not nome_trovato: return None, "Non ho trovato il dipendente. (Modalità Simulator)"
    if "alloca" in prompt_l or "assegna" in prompt_l:
        perc_match = re.search(r'(\d+)%', prompt_l)
        perc = int(perc_match.group(1)) if perc_match else 100
        cliente = "Nuovo Progetto"
        match_cliente = re.search(r'(?:su|sul|sulla)\s+([a-zA-Z0-9_\-]+)', prompt_l.replace("progetto ", ""))
        if match_cliente: cliente = match_cliente.group(1).capitalize()
        desc = f"**{nome_trovato}** pronto per l'allocazione (Simulazione)."
        return {"type": "alloca", "nome": nome_trovato, "perc": perc, "cliente": cliente, "desc": desc}, None
    if "promuovi" in prompt_l:
        sen = "Senior" if "senior" in prompt_l else "Mid" if "mid" in prompt_l else "Junior"
        return {"type": "promuovi", "nome": nome_trovato, "nuova_sen": sen, "desc": f"Promuovo **{nome_trovato}** a **{sen}**."}, None
    return None, "Comando non riconosciuto (Modalità Simulator)."

def parse_chatbot_intent_llm(prompt, df, api_key):
    """Vero LLM tramite Groq per il Copilot Chatbot (Versione Antiproiettile)"""
    if not api_key:
        return fallback_simulatore_chatbot(prompt, df)
        
    lista_nomi = ", ".join(df['Nome'].tolist())
    
    system_prompt = f"""
    Sei l'assistente virtuale di un sistema HR/Project Management.
    Rispondi SEMPRE E SOLO con un oggetto JSON valido. Non aggiungere altre frasi.
    Dipendenti a sistema: {lista_nomi}
    
    REGOLE:
    1. Se l'utente chiede di ALLOCARE/ASSEGNARE:
    {{"azione": "alloca", "nome": "Nome e Cognome", "percentuale": 50, "cliente": "Nome cliente", "messaggio_riepilogo": "Vado ad allocare..."}}
    
    2. Se l'utente chiede di PROMUOVERE:
    {{"azione": "promuovi", "nome": "Nome e Cognome", "nuova_seniority": "Junior/Mid/Senior", "messaggio_riepilogo": "Vado a promuovere..."}}
    
    3. Se l'utente ti saluta (es. "ciao come stai") o fa richieste non pertinenti:
    {{"azione": "errore", "messaggio_riepilogo": "Ciao! Sono il tuo AI Copilot. Posso aiutarti ad allocare risorse sui progetti o a promuovere i consulenti. Prova a chiedermi: 'Alloca Marco Rossi su TIM al 50%'."}}
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200: 
            return None, f"⚠️ Errore API Groq: {response.text}"
            
        testo_risposta = response.json()["choices"][0]["message"]["content"]
        
        try:
            match = re.search(r'\{.*\}', testo_risposta, re.DOTALL)
            dati = json.loads(match.group(0)) if match else json.loads(testo_risposta)
        except:
            return None, f"⚠️ Il modello non ha restituito JSON valido. Risposta ricevuta: {testo_risposta}"
        
        if dati.get("azione") == "errore": 
            return None, dati.get("messaggio_riepilogo")
            
        if dati.get("azione") == "alloca":
            return {
                "type": "alloca", 
                "nome": dati.get("nome"), 
                "perc": dati.get("percentuale", 100), 
                "cliente": dati.get("cliente", "N/D"), 
                "desc": dati.get("messaggio_riepilogo")
            }, None
            
        if dati.get("azione") == "promuovi":
            return {
                "type": "promuovi", 
                "nome": dati.get("nome"), 
                "nuova_sen": dati.get("nuova_seniority"), 
                "desc": dati.get("messaggio_riepilogo")
            }, None
            
        return None, "Non ho capito la richiesta. Riprova con parole diverse."
    except Exception as e:
        return None, f"⚠️ Errore di connessione AI: {str(e)}"

def esegui_azione_chatbot(dati_finali):
    df = st.session_state.df_risorse
    idx = df.index[df['Nome'] == dati_finali['nome']].tolist()[0]
    
    if dati_finali['type'] == 'alloca':
        df.at[idx, 'Occupazione_%'] = dati_finali['perc']
        if 'end_date' in dati_finali and dati_finali['end_date']:
            df.at[idx, 'Disponibile_dal'] = dati_finali['end_date'].strftime("%Y-%m-%d")
        else:
            df.at[idx, 'Disponibile_dal'] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        df.at[idx, 'Esperienze'].append({"Cliente": dati_finali['cliente'], "Progetto": "Assegnazione da AI Copilot", "Tecnologie_Usate": []})
        msg = f"✅ Successo: **{dati_finali['nome']}** assegnato a **{dati_finali['cliente']}** al {dati_finali['perc']}%."
        
    elif dati_finali['type'] == 'promuovi':
        ruolo_puro = df.at[idx, 'Ruolo'].replace('Senior ', '').replace('Mid ', '').replace('Junior ', '')
        df.at[idx, 'Seniority'] = dati_finali['nuova_sen']
        df.at[idx, 'Ruolo'] = f"{dati_finali['nuova_sen']} {ruolo_puro}"
        msg = f"✅ Successo: **{dati_finali['nome']}** promosso a **{dati_finali['nuova_sen']}**."

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
# IMPOSTAZIONI VERO LLM (GROQ) PER IL CHATBOT
# ---------------------------------------------------------
if ruolo_utente in ["Project Manager", "HR (Risorse Umane)"]:
    with st.sidebar.expander("⚙️ Impostazioni AI Copilot (Groq)"):
        st.write("Attiva il VERO LLM (Llama 3) per il Chatbot.")
        api_key = st.text_input("Groq API Key (gsk_...):", value=st.session_state.groq_api_key, type="password")
        if st.button("Salva Chiave"):
            st.session_state.groq_api_key = api_key
            st.success("API Key salvata! Chatbot potenziato.")

# ---------------------------------------------------------
# CHATBOT WIDGET CON POPUP E FORM DI CONFERMA
# ---------------------------------------------------------
if (st.session_state.pm_logged_in or st.session_state.hr_logged_in):
    st.sidebar.markdown("---")
    with st.sidebar.popover("💬 Assistente AI (Copilot)", use_container_width=True):
        st.markdown("**Copilot Aziendale**")
        if st.session_state.groq_api_key and st.session_state.groq_api_key.startswith("gsk_"):
            st.caption("🟢 *Motore: Llama-3 (Groq LLM)*")
        else:
            st.caption("🟠 *Motore: Rules Engine (Simulatore)*")
        
        for msg in st.session_state.chat_msgs:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        if st.session_state.bot_action:
            act = st.session_state.bot_action
            st.info(act['desc'])
            
            if act['type'] == 'alloca':
                with st.form("form_bot_conferma"):
                    c1, c2 = st.columns(2)
                    nuovo_cliente = c1.text_input("Cliente/Progetto", value=act['cliente'])
                    nuova_perc = c2.number_input("Occupazione %", min_value=0, max_value=100, value=act['perc'])
                    date_range = st.date_input("Periodo", value=(datetime.today(), datetime.today() + timedelta(days=30)))
                    
                    c_btn1, c_btn2 = st.columns(2)
                    submit_bot = c_btn1.form_submit_button("✅ Conferma ed Esegui")
                    cancel_bot = c_btn2.form_submit_button("❌ Annulla")
                    
                    if submit_bot:
                        if len(date_range) == 2:
                            act['cliente'] = nuovo_cliente
                            act['perc'] = nuova_perc
                            act['end_date'] = date_range[1]
                            esegui_azione_chatbot(act)
                            st.rerun()
                        else:
                            st.error("Seleziona una data di fine.")
                    if cancel_bot:
                        st.session_state.bot_action = None
                        st.session_state.chat_msgs.append({"role": "assistant", "content": "Operazione annullata."})
                        st.rerun()
            else:
                col_ok, col_ko = st.columns(2)
                if col_ok.button("✅ Esegui"):
                    esegui_azione_chatbot(act)
                    st.rerun()
                if col_ko.button("❌ Annulla"):
                    st.session_state.bot_action = None
                    st.session_state.chat_msgs.append({"role": "assistant", "content": "Operazione annullata."})
                    st.rerun()

        if prompt := st.chat_input("Chiedi all'AI (es. Alloca Luca Neri su TIM al 50%)..."):
            st.session_state.chat_msgs.append({"role": "user", "content": prompt})
            with st.spinner("Elaborazione..."):
                action_dict, error_msg = parse_chatbot_intent_llm(prompt, st.session_state.df_risorse, st.session_state.groq_api_key)
            
            if error_msg:
                st.session_state.chat_msgs.append({"role": "assistant", "content": error_msg})
            else:
                st.session_state.bot_action = action_dict
                st.session_state.chat_msgs.append({"role": "assistant", "content": "Ho preparato la richiesta. Controlla e conferma:"})
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
        prog_att = estrai_progetto_attuale(dati_utente)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Le tue Info")
            st.write(f"**Qualifica:** {dati_utente['Ruolo']}")
            st.write(f"**Skill Validate:** {dati_utente['Skill']}")
            st.write(f"**Stato:** Occupato al {dati_utente['Occupazione_%']}% su **{prog_att}**")
            st.markdown("---")
            st.write("**Richiedi Validazione Skill**")
            nuova_skill = st.text_input("Aggiungi competenza (es. GraphQL):")
            if st.button("Invia Skill al PM"):
                if nuova_skill.strip():
                    st.session_state.pending_approvals.append({"ID": dati_utente['ID'], "Nome": dati_utente['Nome'], "Skill": nuova_skill.strip()})
                    st.success("Richiesta inviata!")
        with c2:
            st.subheader("📅 Richiedi Allocazione / Slot")
            st.info("Invia una richiesta al PM per occupare uno slot in agenda.")
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
        tab_allocazioni = f"📅 Pianificazione ({num_req_alloc})" if num_req_alloc > 0 else "📅 Pianificazione"
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ Navigazione PM")
        pagina_pm = st.sidebar.radio("Vai a:", [
            "🏠 Homepage & Alert", 
            "🚀 Scoping & Staffing AI",
            tab_allocazioni,
            "👥 Pianificazione Team (Scheduling)",
            "👤 Analisi Profili", 
            "🗄️ Master Data (Database)"
        ])
        
        if st.sidebar.button("🚪 Esci (Logout)"):
            st.session_state.pm_logged_in = False
            st.rerun()

        if pagina_pm == "🏠 Homepage & Alert":
            st.title("Centro di Controllo Manageriale")
            if num_req_alloc > 0:
                st.warning(f"🔔 **ATTENZIONE:** Hai **{num_req_alloc}** nuove richieste di allocazione in attesa.")
            
            with st.container(border=True):
                st.markdown("#### 👤 Profilo Manager: Admin")
                st.markdown("**Ruolo:** Senior IT Delivery Manager  \n**Dipartimento:** Digital Transformation")
            
            tot_risorse = len(df)
            occupate = len(df[df['Occupazione_%'] > 0])
            mancati_incassi_gg = df[df['Occupazione_%'] == 0]['Tariffa_Vendita'].sum()
            revenue_attiva_gg = (df['Tariffa_Vendita'] * (df['Occupazione_%']/100)).sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='kpi-card'><h3>Risorse Totali</h3><h2>{tot_risorse}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='kpi-card'><h3>Staffate</h3><h2>{occupate}</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='kpi-card red'><h3>Bench (Perdita GG)</h3><h2>€ {mancati_incassi_gg:,.0f}</h2></div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='kpi-card green'><h3>Revenue GG Attesa</h3><h2>€ {revenue_attiva_gg:,.0f}</h2></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("📊 Bilancio Portafoglio: Ricavi Attivi vs Mancati Ricavi")
            df_fin = pd.DataFrame({
                "Categoria": ["Mancati Ricavi (Bench)", "Ricavi Attivi (Staffati)"],
                "Valore Giornaliero": [mancati_incassi_gg, revenue_attiva_gg]
            })
            fig_fin = px.pie(df_fin, values='Valore Giornaliero', names='Categoria', hole=0.3,
                             color='Categoria', color_discrete_map={"Mancati Ricavi (Bench)": "#FF4B4B", "Ricavi Attivi (Staffati)": "#00CC96"})
            st.plotly_chart(fig_fin, use_container_width=True)

        elif pagina_pm == "🚀 Scoping & Staffing AI":
            st.title("🤖 Scoping Dinamico & Scenario Analysis")
            
            st.info("""
            **AI-enabled Staffing Copilot Roadmap**
            - **Oggi (MVP Operativo):** Motore a Regole Deterministiche (Rules Engine) per Scenario Analysis & Allocation Cockpit.
            - **Domani (In Roadmap):** Integrazione full LLM per scoping semantico profondo, skill extraction automatica e reasoning sui carichi di lavoro.
            - **Futuro:** Guardrail, approval workflow AI, audit log e feedback loop.
            """)
            
            def imposta_brief_demo():
                st.session_state.testo_brief = "Il cliente ha richiesto una nuova piattaforma web. Il frontend sarà in React e TypeScript. Per il backend necessitiamo di Python e database SQL. L'infrastruttura andrà portata su AWS."
            
            st.button("📝 Carica Brief di Esempio (per Demo)", on_click=imposta_brief_demo)
            
            if "testo_brief" not in st.session_state:
                st.session_state.testo_brief = ""
                
            testo_da_analizzare = st.text_area("Requisiti di progetto (Inserisci il brief da valutare col Motore Deterministico):", key="testo_brief", height=100)

            if st.button("Genera WBS e Team", type="primary"):
                fasi, skill_richieste = analizza_testo(testo_da_analizzare)
                
                if not fasi:
                    st.warning("⚠️ Il Motore Deterministico non ha rilevato tecnologie specifiche. Prova a inserire termini tecnici (es. React, Python, AWS, Node, SQL) o usa il 'Brief di Esempio'.")
                    if "wbs_data" in st.session_state: del st.session_state.wbs_data
                    if "team_data" in st.session_state: del st.session_state.team_data
                else:
                    st.session_state.wbs_data = pd.DataFrame(fasi)
                    
                    team_proposto = []
                    for skill in skill_richieste:
                        candidati = df[df['Occupazione_%'] < 100]
                        match_trovato = False
                        for _, risorsa in candidati.iterrows():
                            if skill.lower() in risorsa['Skill'].lower():
                                team_proposto.append({"Skill": skill, "Nome": risorsa['Nome'], "Costo_gg": risorsa['Costo_Giorno'], "Margine_%": 30})
                                match_trovato = True
                                break 
                        if not match_trovato:
                            team_proposto.append({"Skill": skill, "Nome": "DA ASSUMERE", "Costo_gg": 300, "Margine_%": 30})
                    st.session_state.team_data = pd.DataFrame(team_proposto)

            if "wbs_data" in st.session_state and not st.session_state.wbs_data.empty:
                # --- TABS PER LA UI MIGLIORATA ---
                tab_wbs, tab_team = st.tabs(["📋 1. WBS & Stima Tempi", "💰 2. Team Consigliato e Marginalità"])
                
                with tab_wbs:
                    edited_wbs = st.data_editor(st.session_state.wbs_data, num_rows="dynamic", key="wbs_editor", use_container_width=True)
                
                with tab_team:
                    edited_team = st.data_editor(st.session_state.team_data, key="team_editor", use_container_width=True)
                    
                    costo_totale_progetto, proposta_commerciale = 0, 0
                    for idx, row in edited_wbs.iterrows():
                        membro = edited_team[edited_team['Skill'] == row['Skill']]
                        if not membro.empty:
                            costo_fase = row['Giorni'] * membro.iloc[0]['Costo_gg']
                            costo_totale_progetto += costo_fase
                            proposta_commerciale += costo_fase * (1 + (membro.iloc[0]['Margine_%'] / 100))
                    
                    st.markdown("### Breakdown Finanziario (Tempo Reale)")
                    c_fin1, c_fin2, c_fin3 = st.columns(3)
                    c_fin1.markdown(f"<div class='kpi-card orange'><h3>Costo Vivo Progetto</h3><h2>€ {costo_totale_progetto:,.0f}</h2></div>", unsafe_allow_html=True)
                    c_fin2.markdown(f"<div class='kpi-card'><h3>Proposta Commerciale</h3><h2>€ {proposta_commerciale:,.0f}</h2></div>", unsafe_allow_html=True)
                    c_fin3.markdown(f"<div class='kpi-card green'><h3>Margine Netto Finale</h3><h2>€ {proposta_commerciale - costo_totale_progetto:,.0f}</h2></div>", unsafe_allow_html=True)

        elif pagina_pm == tab_allocazioni:
            st.title("Gestione Agende e Allocazioni")
            
            st.subheader("1. Richieste in attesa")
            if len(st.session_state.pending_allocations) > 0:
                for i, req in enumerate(list(st.session_state.pending_allocations)):
                    with st.container(border=True):
                        st.write(f"👤 **{req['Nome']}** richiede il {req['Occupazione']}% per il progetto **{req['Progetto']}** ({req['Dal']} a {req['Al']})")
                        b1, b2 = st.columns(2)
                        if b1.button("✅ Approva", key=f"alloc_ok_{i}"):
                            idx = df.index[df['ID'] == req['ID']].tolist()[0]
                            st.session_state.df_risorse.at[idx, 'Occupazione_%'] = req['Occupazione']
                            st.session_state.df_risorse.at[idx, 'Disponibile_dal'] = req['Al'].strftime("%Y-%m-%d")
                            st.session_state.df_risorse.at[idx, 'Esperienze'].append({"Cliente": "Interno", "Progetto": req['Progetto'], "Tecnologie_Usate": []})
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
                        if b2.button("❌ Rifiuta", key=f"alloc_ko_{i}"):
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
            else: st.success("Nessuna richiesta in sospeso.")
                
            st.divider()
            st.subheader("2. Assegnazione Manuale (Top-Down)")
            with st.form("manual_alloc"):
                r_scelta = st.selectbox("Seleziona Consulente:", df['Nome'].tolist())
                c_form1, c_form2 = st.columns(2)
                cliente_input = c_form1.text_input("Nome Cliente")
                progetto_input = c_form2.text_input("Tipo Progetto / Lavoro")
                
                c_form3, c_form4 = st.columns(2)
                oggi = datetime.today()
                date_range = c_form3.date_input("Periodo di Allocazione", value=(oggi, oggi + timedelta(days=60)))
                perc = c_form4.slider("Percentuale %", 0, 100, 100, step=25)
                
                if st.form_submit_button("Forza Allocazione") and len(date_range) == 2 and cliente_input:
                    idx = df.index[df['Nome'] == r_scelta].tolist()[0]
                    st.session_state.df_risorse.at[idx, 'Occupazione_%'] = perc
                    st.session_state.df_risorse.at[idx, 'Disponibile_dal'] = date_range[1].strftime("%Y-%m-%d")
                    st.session_state.df_risorse.at[idx, 'Esperienze'].append({"Cliente": cliente_input, "Progetto": progetto_input, "Tecnologie_Usate": []})
                    st.success(f"✅ {r_scelta} allocato con successo!")

        elif pagina_pm == "👥 Pianificazione Team (Scheduling)":
            st.title("Scheduling Assistant Team")
            st.write("Componi il tuo team e verifica la disponibilità incrociata attraverso i calendari visivi.")
            
            c_f1, c_f2 = st.columns(2)
            filtro_sen = c_f1.multiselect("Filtra per Seniority:", ["Junior", "Mid", "Senior"], default=["Senior", "Mid", "Junior"])
            df_filtered = df[df['Seniority'].isin(filtro_sen)] if filtro_sen else df
            
            team_selezionato = c_f2.multiselect("Seleziona le risorse per il Team:", df_filtered['Nome'].tolist())
            
            if "team_cal_idx" not in st.session_state: 
                st.session_state.team_cal_idx = 0
                
            oggi = datetime.today()
            orizzonte = st.date_input("Orizzonte temporale di analisi (Inizio - Fine):", value=(oggi, oggi + timedelta(days=180)))
            
            if team_selezionato and len(orizzonte) == 2:
                start_date, end_date = orizzonte
                st.markdown("---")
                
                mesi_presenti = []
                curr = start_date.replace(day=1)
                while curr <= end_date:
                    mesi_presenti.append((curr.year, curr.month))
                    if curr.month == 12: curr = curr.replace(year=curr.year+1, month=1)
                    else: curr = curr.replace(month=curr.month+1)
                
                if st.session_state.team_cal_idx >= len(mesi_presenti): 
                    st.session_state.team_cal_idx = 0
                
                col_p, col_m, col_n = st.columns([1,2,1])
                if col_p.button("◀ Mese Precedente", key="btn_prev_team"):
                    if st.session_state.team_cal_idx > 0:
                        st.session_state.team_cal_idx -= 1
                        st.rerun()
                if col_n.button("Mese Successivo ▶", key="btn_next_team"):
                    if st.session_state.team_cal_idx < len(mesi_presenti) - 1:
                        st.session_state.team_cal_idx += 1
                        st.rerun()
                        
                anno_corr, mese_corr = mesi_presenti[st.session_state.team_cal_idx]
                mesi_ita = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
                nome_mese = mesi_ita[mese_corr]
                
                col_m.markdown(f"<h3 style='text-align:center; margin-top:0;'>{nome_mese} {anno_corr}</h3>", unsafe_allow_html=True)
                
                st.markdown("""
                <div style="display:flex; justify-content:center; gap:20px; font-size:12px; margin-bottom: 30px;">
                    <div style="display:flex; align-items:center;"><div style="width:15px; height:15px; background:#FF4B4B; margin-right:5px; border-radius:3px;"></div> <b>Disponibile (Bench)</b></div>
                    <div style="display:flex; align-items:center;"><div style="width:15px; height:15px; background:#FFD700; margin-right:5px; border-radius:3px;"></div> <b>Parz. Occupato</b></div>
                    <div style="display:flex; align-items:center;"><div style="width:15px; height:15px; background:#00CC96; margin-right:5px; border-radius:3px;"></div> <b>Non Disponibile</b></div>
                    <div style="display:flex; align-items:center;"><div style="width:15px; height:15px; background:#333333; margin-right:5px; border-radius:3px;"></div> Weekend / Fuori Orizz.</div>
                </div>
                """, unsafe_allow_html=True)

                cal = calendar.Calendar(firstweekday=0)
                month_days = cal.monthdatescalendar(anno_corr, mese_corr)
                giorni_sett = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

                cols_per_row = 3
                for i in range(0, len(team_selezionato), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, nome in enumerate(team_selezionato[i:i+cols_per_row]):
                        with cols[j]:
                            r_dati = df[df['Nome'] == nome].iloc[0]
                            prog_att = estrai_progetto_attuale(r_dati)
                            
                            st.markdown(f"<h5 style='text-align:center; color:#1E88E5; margin-bottom:2px;'>{nome}</h5>", unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align:center; font-size:11px; color:#888; margin-top:0px; margin-bottom:10px;'>{prog_att}</p>", unsafe_allow_html=True)
                            
                            data_libero = datetime.strptime(r_dati['Disponibile_dal'], "%Y-%m-%d").date()
                            occ_attuale = r_dati['Occupazione_%']
                            
                            html_cal = "<div style='display:grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 30px;'>"
                            
                            for g in giorni_sett:
                                html_cal += f"<div style='text-align:center; font-size:11px; font-weight:bold; color:#888;'>{g}</div>"
                                
                            for week in month_days:
                                for day in week:
                                    if day.month != mese_corr:
                                        html_cal += "<div style='visibility:hidden;'></div>"
                                    else:
                                        occ = occ_attuale if day < data_libero else 0
                                        if day < start_date or day > end_date: bg_color = "#333333"
                                        elif day.weekday() >= 5: bg_color = "#333333"
                                        elif occ == 0: bg_color = "#FF4B4B"
                                        elif occ < 100: bg_color = "#FFD700"
                                        else: bg_color = "#00CC96"
                                            
                                        html_cal += f"<div style='background-color:{bg_color}; height:35px; border-radius:4px; display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:bold; color:#FFF;'>{day.day}</div>"
                            
                            html_cal += "</div>"
                            st.markdown(html_cal, unsafe_allow_html=True)

        elif pagina_pm == "👤 Analisi Profili":
            st.title("Indagine Singola Risorsa")
            
            nome_ricerca = st.selectbox("Seleziona Consulente:", df['Nome'].tolist())
            if nome_ricerca:
                dati_ricerca = df[df['Nome'] == nome_ricerca].iloc[0]
                prog_att = estrai_progetto_attuale(dati_ricerca)
                
                c1, c2, c3 = st.columns(3)
                c1.info(f"**Qualifica:** {dati_ricerca['Ruolo']}")
                c2.success(f"**Skills:** {dati_ricerca['Skill']}")
                c3.warning(f"**Stato Attuale:** Occupato {dati_ricerca['Occupazione_%']}% | **Progetto:** {prog_att}")
                
                st.markdown("---")
                st.subheader("🗓️ Calendario Visuale (Mensile)")
                
                date_range = st.date_input("Seleziona l'orizzonte totale di analisi:", value=(datetime.today(), datetime.today() + timedelta(days=180)))
                
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    data_libero = datetime.strptime(dati_ricerca['Disponibile_dal'], "%Y-%m-%d").date()
                    
                    mesi_presenti = []
                    curr = start_date.replace(day=1)
                    while curr <= end_date:
                        mesi_presenti.append((curr.year, curr.month))
                        if curr.month == 12: curr = curr.replace(year=curr.year+1, month=1)
                        else: curr = curr.replace(month=curr.month+1)
                    
                    if st.session_state.cal_month_idx >= len(mesi_presenti): st.session_state.cal_month_idx = 0
                    
                    col_p, col_m, col_n = st.columns([1,2,1])
                    if col_p.button("◀ Mese Precedente"):
                        if st.session_state.cal_month_idx > 0:
                            st.session_state.cal_month_idx -= 1
                            st.rerun()
                    if col_n.button("Mese Successivo ▶"):
                        if st.session_state.cal_month_idx < len(mesi_presenti) - 1:
                            st.session_state.cal_month_idx += 1
                            st.rerun()
                            
                    anno_corr, mese_corr = mesi_presenti[st.session_state.cal_month_idx]
                    mesi_ita = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
                    nome_mese = mesi_ita[mese_corr]
                    col_m.markdown(f"<h3 style='text-align:center; margin-top:0;'>{nome_mese} {anno_corr}</h3>", unsafe_allow_html=True)
                    
                    cal = calendar.Calendar(firstweekday=0)
                    month_days = cal.monthdatescalendar(anno_corr, mese_corr)
                    
                    giorni_sett = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
                    html_cal = "<div style='display:grid; grid-template-columns: repeat(7, 1fr); gap: 10px; max-width: 600px; margin: auto;'>"
                    for g in giorni_sett:
                        html_cal += f"<div style='text-align:center; font-weight:bold; color:#888;'>{g}</div>"
                        
                    for week in month_days:
                        for day in week:
                            if day.month != mese_corr:
                                html_cal += "<div style='visibility:hidden;'></div>"
                            else:
                                occ = dati_ricerca['Occupazione_%'] if day < data_libero else 0
                                if day < start_date or day > end_date: bg_color = "#333333"
                                elif day.weekday() >= 5: bg_color = "#333333"
                                elif occ == 0: bg_color = "#FF4B4B"
                                elif occ < 100: bg_color = "#FFD700"
                                else: bg_color = "#00CC96"
                                    
                                html_cal += f"<div style='background-color:{bg_color}; height:60px; border-radius:5px; display:flex; align-items:center; justify-content:center; font-size:16px; font-weight:bold; color:#FFF;'>{day.day}</div>"
                    
                    html_cal += "</div>"
                    st.markdown(html_cal, unsafe_allow_html=True)

        elif pagina_pm == "🗄️ Master Data (Database)":
            st.title("Vista Tabellare Completa")
            df_display = df.copy()
            df_display['Progetto_Attuale'] = df_display.apply(estrai_progetto_attuale, axis=1)
            df_display = df_display.drop(columns=['Esperienze'], errors='ignore')
            
            # --- TABELLA SMART CON CONFIGURAZIONI VISIVE ---
            st.dataframe(
                df_display,
                column_config={
                    "Occupazione_%": st.column_config.ProgressColumn("Impegno (%)", min_value=0, max_value=100, format="%d%%"),
                    "Costo_Giorno": st.column_config.NumberColumn("Costo GG", format="€ %d"),
                    "Tariffa_Vendita": st.column_config.NumberColumn("Tariffa Output", format="€ %d")
                },
                hide_index=True, use_container_width=True
            )

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

        if pagina_hr == "🏠 Dashboard HR":
            st.title("Dashboard Risorse Umane")
            st.info("Panoramica sulla composizione della forza lavoro aziendale.")
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='kpi-card'><h3>Totale Dipendenti</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='kpi-card'><h3>Età Media (Figurativa)</h3><h2>32 Anni</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='kpi-card'><h3>Costo Medio GG</h3><h2>€ {df['Costo_Giorno'].mean():.0f}</h2></div>", unsafe_allow_html=True)
            
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

        elif pagina_hr == "✏️ Gestione e Promozioni":
            st.title("Gestione Dipendente e Promozioni")
            st.write("Aggiorna l'anagrafica, promuovi di livello o modifica il costo di una singola risorsa.")
            
            nome_ricerca = st.selectbox("Seleziona Dipendente da modificare:", df['Nome'].tolist())
            if nome_ricerca:
                idx = df.index[df['Nome'] == nome_ricerca].tolist()[0]
                dati_attuali = df.iloc[idx]
                prog_att = estrai_progetto_attuale(dati_attuali)
                
                st.info(f"💡 Attualmente su: **{prog_att}** (Occupato al {dati_attuali['Occupazione_%']}%)")
                
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

        elif pagina_hr == "🗄️ Master Data Dipendenti":
            st.title("Anagrafica Completa Dipendenti")
            st.write("Vista raw del database aziendale.")
            df_display = df.copy()
            df_display['Progetto_Attuale'] = df_display.apply(estrai_progetto_attuale, axis=1)
            df_display = df_display.drop(columns=['Esperienze', 'Macro_Area'], errors='ignore')
            
            # --- TABELLA SMART CON CONFIGURAZIONI VISIVE ---
            st.dataframe(
                df_display,
                column_config={
                    "Occupazione_%": st.column_config.ProgressColumn("Occupato al (%)", min_value=0, max_value=100, format="%d%%"),
                    "Costo_Giorno": st.column_config.NumberColumn("Costo (€)", format="€ %d")
                },
                hide_index=True, use_container_width=True
            )
