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
# 1. INIZIALIZZAZIONE E CONFIGURAZIONE
# ==========================================
st.set_page_config(page_title="ResourceAI - Manager", layout="wide", initial_sidebar_state="expanded")

# --- INIEZIONE CSS CORPORATE SAAS (TEMA ADATTIVO LIGHT/DARK) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
    
    .stButton>button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        border: 1px solid rgba(128,128,128,0.2) !important;
        transition: all 0.3s ease !important;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    .stButton>button:hover {
        border-color: #3B82F6 !important;
        color: #3B82F6 !important;
    }
    
    .gradient-title {
        background: linear-gradient(45deg, #3B82F6, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.4rem;
        margin-bottom: 0.5rem;
        margin-top: -1rem;
        letter-spacing: -0.5px;
    }
    
    /* Variabili Adattive per Light e Dark Mode */
    :root {
        --kpi-bg: rgba(0,0,0,0.03);
        --kpi-border: rgba(0,0,0,0.1);
        --kpi-text-main: var(--text-color);
        --kpi-text-sub: #555;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --kpi-bg: linear-gradient(145deg, rgba(30,33,39,0.7) 0%, rgba(20,22,26,0.9) 100%);
            --kpi-border: rgba(255,255,255,0.05);
            --kpi-text-sub: #8B949E;
        }
    }
    
    .kpi-card {
        background: var(--kpi-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--kpi-border);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }
    
    .kpi-card-shadow { box-shadow: 0 8px 30px rgba(0,0,0,0.15) !important; }
    
    .kpi-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; }
    .kpi-card.blue::before { background: #3B82F6; }
    .kpi-card.green::before { background: #10B981; }
    .kpi-card.red::before { background: #EF4444; }
    .kpi-card.orange::before { background: #F59E0B; }
    
    .kpi-card h3 { color: var(--kpi-text-sub); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0; margin-bottom: 8px;}
    .kpi-card h2 { color: var(--kpi-text-main); font-size: 2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px;}
    
    .alert-box {
        padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid; background: rgba(128,128,128,0.1); color: var(--text-color);
    }
    .alert-red { border-color: #EF4444; }
    .alert-orange { border-color: #F59E0B; }
    .alert-blue { border-color: #3B82F6; }
    
    /* CSS Scheduling Assistant Adattivo */
    .scheduling-container { overflow-x: auto; padding-bottom: 15px; margin-top: 20px; }
    .scheduling-row { display: flex; align-items: center; margin-bottom: 4px; flex-wrap: nowrap; }
    .scheduling-header { font-weight: 700; font-size: 11px; color: var(--kpi-text-sub); text-align: center; min-width: 35px; }
    .scheduling-name { min-width: 180px; max-width: 180px; font-weight: 600; font-size: 14px; position: sticky; left: 0; background-color: var(--background-color); z-index: 2; padding-right: 15px; color: var(--text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.3; }
    .scheduling-cell { min-width: 35px; height: 35px; margin-right: 2px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: white; font-weight: 600; }

    /* Stile Neon opzionale per il menu standard */
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: rgba(59, 130, 246, 0.12) !important;
        box-shadow: inset 4px 0 0 #3B82F6 !important;
        border-radius: 4px;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        font-weight: 800 !important;
        color: #3B82F6 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FORMATTAZIONE ---
def formatta_valuta(valore):
    try: return f"€ {float(valore):,.0f}"
    except: return "€ 0"

def formatta_data(data_str):
    if not data_str: return ""
    try:
        if isinstance(data_str, str): return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d-%m-%Y")
        else: return data_str.strftime("%d-%m-%Y")
    except: return data_str

def get_badge(n):
    if n <= 0: return ""
    badges = ["❶","❷","❸","❹","❺","❻","❼","❽","❾","❿"]
    return f" {badges[n-1]}" if n <= 10 else f" ({n})"

def applica_tema_plotly(fig):
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Outfit", color="#8B949E"), margin=dict(l=20, r=20, t=40, b=20))
    return fig

# --- STRUTTURA DATI RELAZIONALE ---
@st.cache_data
def genera_dati_strutturali():
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
    
    db_risorse = []
    for i, nome in enumerate(nomi_completi):
        ruolo, skills_possibili, macro_area = random.choice(ruoli_skills)
        skills = random.sample(skills_possibili, k=random.randint(2, len(skills_possibili)))
        seniority = random.choice(["Junior", "Mid", "Senior"])
        costo_base = {"Junior": 150, "Mid": 250, "Senior": 350}[seniority]
        
        db_risorse.append({
            "ID": f"RES-{1000+i}", "Nome": nome, "Macro_Area": macro_area, "Ruolo": f"{seniority} {ruolo}",
            "Seniority": seniority, "Skill": ", ".join(skills), "Costo_Giorno": costo_base,
            "Tariffa_Vendita": costo_base * 1.4, "Disponibile_dal": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        })
    df_risorse = pd.DataFrame(db_risorse)

    df_commesse = pd.DataFrame([
        {"ID_Commessa": "PRJ-001", "Cliente": "Enel", "Nome": "Migrazione Cloud AWS", "Budget": 45000, "Stato": "Attivo"},
        {"ID_Commessa": "PRJ-002", "Cliente": "TIM", "Nome": "App Mobile React", "Budget": 38000, "Stato": "Attivo"},
        {"ID_Commessa": "PRJ-003", "Cliente": "Intesa", "Nome": "Dashboard IoT", "Budget": 60000, "Stato": "Attivo"},
        {"ID_Commessa": "PRJ-004", "Cliente": "Ferrari", "Nome": "Piattaforma E-commerce", "Budget": 20000, "Stato": "In Avvio"},
        {"ID_Commessa": "PRJ-005", "Cliente": "Poste", "Nome": "Ottimizzazione SQL", "Budget": 15000, "Stato": "Attivo"}
    ])

    allocazioni = []
    timesheet = []
    
    for _, risorsa in df_risorse.iterrows():
        num_commesse = random.choices([0, 1, 2], weights=[0.3, 0.5, 0.2])[0]
        id_risorsa = risorsa['ID']
        if num_commesse > 0:
            commesse_assegnate = random.sample(df_commesse['ID_Commessa'].tolist(), k=num_commesse)
            for c_id in commesse_assegnate:
                perc = random.choice([50, 100, 150])
                allocazioni.append({"ID_Risorsa": id_risorsa, "ID_Commessa": c_id, "Impegno_%": perc})
                giorni_spesi = random.randint(5, 45)
                timesheet.append({
                    "ID_Risorsa": id_risorsa, "ID_Commessa": c_id,
                    "Data_Inizio_Progetto": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                    "Giornate_Spese": giorni_spesi
                })

    df_allocazioni = pd.DataFrame(allocazioni) if allocazioni else pd.DataFrame(columns=["ID_Risorsa", "ID_Commessa", "Impegno_%"])
    df_timesheet = pd.DataFrame(timesheet) if timesheet else pd.DataFrame(columns=["ID_Risorsa", "ID_Commessa", "Data_Inizio_Progetto", "Giornate_Spese"])

    return df_risorse, df_commesse, df_allocazioni, df_timesheet

def get_saturazione(id_risorsa, df_alloc):
    allocs = df_alloc[df_alloc['ID_Risorsa'] == id_risorsa]
    if allocs.empty: return 0
    return allocs['Impegno_%'].sum()

def get_progetti_risorsa(id_risorsa, df_alloc, df_comm):
    allocs = df_alloc[df_alloc['ID_Risorsa'] == id_risorsa]
    if allocs.empty: return "Disponibile (Bench)"
    nodi = []
    for _, a in allocs.iterrows():
        match = df_comm[df_comm['ID_Commessa'] == a['ID_Commessa']]
        nome_c = match['Cliente'].values[0] if not match.empty else "Sconosciuto"
        nodi.append(f"{nome_c} ({a['Impegno_%']}%)")
    return " | ".join(nodi)

# --- INIZIALIZZAZIONE SESSION STATE E FIX CACHE ---
if "df_risorse" not in st.session_state or "df_allocazioni" not in st.session_state:
    res, comm, alloc, ts = genera_dati_strutturali()
    st.session_state.df_risorse = res
    st.session_state.df_commesse = comm
    st.session_state.df_allocazioni = alloc
    st.session_state.df_timesheet = ts

# MIGRATORE DATI IN CACHE (Risolve il KeyError Data_Inizio_Progetto)
if 'Data_Inizio' in st.session_state.df_timesheet.columns:
    st.session_state.df_timesheet.rename(columns={'Data_Inizio': 'Data_Inizio_Progetto'}, inplace=True)

if "pending_approvals" not in st.session_state: st.session_state.pending_approvals = []
if "pending_allocations" not in st.session_state: st.session_state.pending_allocations = []
if "team_cal_idx" not in st.session_state: st.session_state.team_cal_idx = 0
if "chat_msgs" not in st.session_state: st.session_state.chat_msgs = [{"role": "assistant", "content": "Smart Assistant inizializzato. Pronto a processare richieste (Es: 'Alloca Marco Rossi su PRJ-001 al 50%')"}]
if "bot_action" not in st.session_state: st.session_state.bot_action = None
if "groq_api_key" not in st.session_state: st.session_state.groq_api_key = "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"
if "pm_logged_in" not in st.session_state: st.session_state.pm_logged_in = False
if "it_logged_in" not in st.session_state: st.session_state.it_logged_in = False
if "hr_logged_in" not in st.session_state: st.session_state.hr_logged_in = False
if "current_it_user" not in st.session_state: st.session_state.current_it_user = None

# ==========================================
# 2. MOTORI AI E COPILOT
# ==========================================
def analizza_testo_llm(testo, api_key):
    if not api_key:
        testo_lower = testo.lower()
        if any(x in testo_lower for x in ["ciao", "diga", "torta", "mare", "sole"]):
            return [], [], "Input non pertinente. Inserire un brief IT strutturato."
        
        competenze_trovate = []
        regole = {"react": ("React", 15), "node": ("Node.js", 20), "python": ("Python", 18), "java": ("Java", 25), "aws": ("AWS", 10), "sql": ("SQL", 8), "typescript": ("TypeScript", 10), "go": ("Go", 20), "kubernetes": ("Kubernetes", 15)}
        fasi = []
        for key, (skill, giorni) in regole.items():
            if key in testo_lower:
                competenze_trovate.append(skill)
                fasi.append({"Fase": f"Sviluppo {skill}", "Skill": skill, "Giorni": giorni})
        return fasi, competenze_trovate, None
    
    prompt = f"""
    Sei un AI specializzata in IT Project Management.
    ANALIZZA il seguente testo. SE la richiesta NON riguarda lo sviluppo software o l'IT (es. saluti, ricette, dighe, discorsi futili), restituisci QUESTO ESATTO JSON DI ERRORE:
    {{"errore": "Input non pertinente. Inserire un brief di progetto software valido."}}
    
    ALTRIMENTI, estrai le fasi del progetto e restituisci SOLO ED ESCLUSIVAMENTE un JSON valido (senza altre parole o formattazioni Markdown):
    {{
        "fasi": [
            {{"Fase": "Descrizione", "Skill": "Tecnologia", "Giorni": 20}}
        ],
        "competenze": ["Tecnologia1", "Tecnologia2"]
    }}
    
    Testo da analizzare: {testo}
    """
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return [], [], f"Errore API Groq (Codice {response.status_code}): Controllare validità Chiave API o limiti Rate Limit."
            
        txt = response.json()["choices"][0]["message"]["content"]
        txt = txt.replace("```json", "").replace("```", "").strip()
        
        dati = json.loads(txt)
        if "errore" in dati: return [], [], dati["errore"]
        return dati.get("fasi", []), dati.get("competenze", []), None
    except json.JSONDecodeError:
        return [], [], "Il modello AI non ha generato un JSON valido. Riprovare."
    except Exception as e:
        return [], [], f"Errore di sistema AI: {str(e)}"

def parse_chatbot_intent_llm(prompt, df, api_key):
    lista_nomi = ", ".join(df['Nome'].tolist())
    system_prompt = f"""Sei uno Smart Assistant. Rispondi SOLO in formato JSON, senza alcun testo fuori dal JSON. Database Nomi: {lista_nomi}
    1. ALLOCARE: {{"azione": "alloca", "nome": "Nome Cognome", "percentuale": 50, "cliente": "ID_Commessa", "messaggio_riepilogo": "Allocazione..."}}
    2. PROMUOVERE: {{"azione": "promuovi", "nome": "Nome Cognome", "nuova_seniority": "Senior", "messaggio_riepilogo": "Upgrade..."}}
    3. ALTRO (Testo non valido/Saluti): {{"azione": "errore", "messaggio_riepilogo": "Comando non riconosciuto. Specificare se allocare o promuovere una risorsa in anagrafica."}}"""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "temperature": 0.1}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return None, f"Errore API Groq ({response.status_code}). Verifica validità o limiti API Key."

        txt = response.json()["choices"][0]["message"]["content"]
        txt = txt.replace("```json", "").replace("```", "").strip()
        
        dati = json.loads(txt)
        if dati.get("azione") == "errore": return None, dati.get("messaggio_riepilogo")
        if dati.get("azione") == "alloca": return {"type": "alloca", "nome": dati.get("nome"), "perc": dati.get("percentuale", 100), "cliente": dati.get("cliente", "N/D"), "desc": dati.get("messaggio_riepilogo")}, None
        if dati.get("azione") == "promuovi": return {"type": "promuovi", "nome": dati.get("nome"), "nuova_sen": dati.get("nuova_seniority"), "desc": dati.get("messaggio_riepilogo")}, None
        return None, "Errore Parser LLM."
    except Exception as e: return None, f"Errore AI: Inserire chiave API valida o controllare connessione."

def esegui_azione_chatbot(dati_finali):
    df_ris = st.session_state.df_risorse
    idx_ris = df_ris[df_ris['Nome'] == dati_finali['nome']].index
    if len(idx_ris) == 0:
        st.session_state.chat_msgs.append({"role": "assistant", "content": "Risorsa non trovata nell'anagrafica Master."})
        st.session_state.bot_action = None
        return
    id_risorsa = df_ris.iloc[idx_ris[0]]['ID']
    if dati_finali['type'] == 'alloca':
        nuova = pd.DataFrame([{"ID_Risorsa": id_risorsa, "ID_Commessa": dati_finali['cliente'], "Impegno_%": dati_finali['perc']}])
        st.session_state.df_allocazioni = pd.concat([st.session_state.df_allocazioni, nuova], ignore_index=True)
        msg = f"Task Eseguito: **{dati_finali['nome']}** agganciato a **{dati_finali['cliente']}** ({dati_finali['perc']}%)."
    elif dati_finali['type'] == 'promuovi':
        rp = df_ris.at[idx_ris[0], 'Ruolo'].replace('Senior ', '').replace('Mid ', '').replace('Junior ', '')
        st.session_state.df_risorse.at[idx_ris[0], 'Seniority'] = dati_finali['nuova_sen']
        st.session_state.df_risorse.at[idx_ris[0], 'Ruolo'] = f"{dati_finali['nuova_sen']} {rp}"
        msg = f"Task Eseguito: **{dati_finali['nome']}** promosso a **{dati_finali['nuova_sen']}**."
    st.session_state.bot_action = None
    st.session_state.chat_msgs.append({"role": "assistant", "content": msg})


# ==========================================
# 3. SIDEBAR E NAVIGAZIONE
# ==========================================
st.sidebar.markdown("<div style='font-size: 26px; font-weight: 800; letter-spacing: -1px; color: #3B82F6; margin-bottom: 30px; margin-top: -20px;'>ResourceAI</div>", unsafe_allow_html=True)
ruolo_utente = st.sidebar.selectbox("PROFILO DI ACCESSO", ["Resource Allocation Engine", "Talent Management", "Talent Workspace"])
st.sidebar.markdown("<br>", unsafe_allow_html=True)

if ruolo_utente != "Resource Allocation Engine": st.session_state.pm_logged_in = False
if ruolo_utente != "Talent Workspace": st.session_state.it_logged_in, st.session_state.current_it_user = False, None
if ruolo_utente != "Talent Management": st.session_state.hr_logged_in = False

df_risorse = st.session_state.df_risorse
df_commesse = st.session_state.df_commesse
df_allocazioni = st.session_state.df_allocazioni
df_timesheet = st.session_state.df_timesheet

# ==========================================
# VISTA 1: RESOURCE ALLOCATION ENGINE
# ==========================================
if ruolo_utente == "Resource Allocation Engine":
    if not st.session_state.pm_logged_in:
        st.markdown("<h1 class='gradient-title'>Gateway Resource Allocation Engine</h1>", unsafe_allow_html=True)
        with st.form("login_pm_form"):
            username = st.text_input("ID Utente")
            password = st.text_input("Credenziale di Rete", type="password")
            if st.form_submit_button("Esegui Login"):
                if username == "admin" and password == "admin123":
                    st.session_state.pm_logged_in = True; st.rerun()
                else: 
                    st.error("Credenziali non conformi.")
    else:
        # Pre-calcolo Allarmi per Notifiche
        sat_df = df_allocazioni.groupby('ID_Risorsa')['Impegno_%'].sum().reset_index() if not df_allocazioni.empty else pd.DataFrame()
        overbooked = sat_df[sat_df['Impegno_%'] > 100] if not sat_df.empty else pd.DataFrame()
        
        commesse_loss = []
        if not df_timesheet.empty:
            ts_cost = pd.merge(df_timesheet, df_risorse[['ID', 'Costo_Giorno']], left_on='ID_Risorsa', right_on='ID')
            ts_cost['Costo_Tot_Riga'] = ts_cost['Giornate_Spese'] * ts_cost['Costo_Giorno']
            costo_aggregato = ts_cost.groupby('ID_Commessa')['Costo_Tot_Riga'].sum().reset_index()
            analisi_budget = pd.merge(df_commesse, costo_aggregato, on='ID_Commessa', how='left').fillna(0)
            commesse_loss = analisi_budget[analisi_budget['Costo_Tot_Riga'] > analisi_budget['Budget']]

        num_alert = len(overbooked) + len(commesse_loss) + len(st.session_state.pending_allocations)
        
        # --- MENU NATIVO STREAMLIT (STABILE E SENZA DELAY) ---
        st.sidebar.markdown("<p style='font-size:12px; color:var(--kpi-text-sub); margin-bottom:0px; font-weight:600; text-transform:uppercase;'>Sezione Principale</p>", unsafe_allow_html=True)
        main_tab = st.sidebar.radio(
            "Sezione Principale", 
            ["Homepage", f"Project and Resources Management{get_badge(num_alert)}", "Staffing Intelligence", "Data Hub"],
            label_visibility="collapsed"
        )
        
        pagina_pm = "Homepage"
        
        # Gestione Sottomenu Condizionali Robusta
        if "Project and Resources" in main_tab:
            st.sidebar.markdown("<p style='font-size:12px; color:var(--kpi-text-sub); margin-top:15px; margin-bottom:0px; font-weight:600; text-transform:uppercase;'>Moduli Gestionali</p>", unsafe_allow_html=True)
            sub_tab = st.sidebar.radio("Sottomenu", [f"Notification and Alert{get_badge(num_alert)}", "Project Hub", "Resource Allocation"], label_visibility="collapsed")
            pagina_pm = "Notification and Alert" if "Notification" in sub_tab else ("Project Hub" if "Project" in sub_tab else "Resource Allocation")
            
        elif main_tab == "Staffing Intelligence":
            st.sidebar.markdown("<p style='font-size:12px; color:var(--kpi-text-sub); margin-top:15px; margin-bottom:0px; font-weight:600; text-transform:uppercase;'>Moduli Intelligenza</p>", unsafe_allow_html=True)
            sub_tab = st.sidebar.radio("Sottomenu", ["Allocation Advisor", "Build your Team", "Profile Explorer"], label_visibility="collapsed")
            pagina_pm = sub_tab
            
        elif main_tab == "Data Hub":
            st.sidebar.markdown("<p style='font-size:12px; color:var(--kpi-text-sub); margin-top:15px; margin-bottom:0px; font-weight:600; text-transform:uppercase;'>Repository Dati</p>", unsafe_allow_html=True)
            sub_tab = st.sidebar.radio("Sottomenu", ["Project Portfolio", "Resource Master Data"], label_visibility="collapsed")
            pagina_pm = sub_tab

        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        if st.sidebar.button("Termina Sessione Corrente"): st.session_state.pm_logged_in = False; st.rerun()

        # --- CONTENUTI PAGINE ---
        if pagina_pm == "Homepage":
            st.markdown("<h1 class='gradient-title'>Homepage</h1>", unsafe_allow_html=True)
            
            risorse_occupate_ids = df_allocazioni['ID_Risorsa'].unique() if not df_allocazioni.empty else []
            occupate = len(risorse_occupate_ids)
            tot_risorse = len(df_risorse)
            bench = tot_risorse - occupate
            
            mancati_incassi_gg = df_risorse[~df_risorse['ID'].isin(risorse_occupate_ids)]['Tariffa_Vendita'].sum() if not df_allocazioni.empty else df_risorse['Tariffa_Vendita'].sum()
            revenue_attiva_gg = 0
            if not df_allocazioni.empty:
                df_alloc_tariffe = pd.merge(df_allocazioni, df_risorse[['ID', 'Tariffa_Vendita']], left_on='ID_Risorsa', right_on='ID')
                revenue_attiva_gg = (df_alloc_tariffe['Tariffa_Vendita'] * (df_alloc_tariffe['Impegno_%'] / 100)).sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='kpi-card blue'><h3>Database Attivo</h3><h2>{tot_risorse}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='kpi-card'><h3>Risorse Staffate</h3><h2>{occupate}</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='kpi-card red'><h3>Margine Bench (GG)</h3><h2>{formatta_valuta(mancati_incassi_gg)}</h2></div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='kpi-card green'><h3>Revenue Attesa (GG)</h3><h2>{formatta_valuta(revenue_attiva_gg)}</h2></div>", unsafe_allow_html=True)

            st.markdown("---")
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.subheader("Rapporto Lavoratori: Attivi vs Bench")
                fig1 = px.pie(names=["Lavoratori Attivi", "Lavoratori in Bench"], values=[occupate, bench], hole=0.3, color_discrete_sequence=["#10B981", "#EF4444"])
                st.plotly_chart(applica_tema_plotly(fig1), use_container_width=True)
            with c_p2:
                st.subheader("Rapporto Finanziario Giornaliero")
                fig2 = px.pie(names=["Revenue Prodotta", "Perdita (Bench)"], values=[revenue_attiva_gg, mancati_incassi_gg], hole=0.3, color_discrete_sequence=["#3B82F6", "#F59E0B"])
                st.plotly_chart(applica_tema_plotly(fig2), use_container_width=True)

        elif pagina_pm == "Notification and Alert":
            st.markdown("<h1 class='gradient-title'>Notification and Alert</h1>", unsafe_allow_html=True)
            if num_alert == 0:
                st.success("Nessun conflitto logico rilevato. Parametri operativi entro i limiti di sistema.")
            else:
                if not overbooked.empty:
                    st.markdown("<h3 style='color: #EF4444;'>🔴 Allarmi di Overbooking Critico</h3>", unsafe_allow_html=True)
                    for _, r in overbooked.iterrows():
                        match = df_risorse[df_risorse['ID'] == r['ID_Risorsa']]
                        nome_ris = match['Nome'].values[0] if not match.empty else r['ID_Risorsa']
                        st.markdown(f"<div class='alert-box alert-red'>Il record <b>{nome_ris}</b> ({r['ID_Risorsa']}) è allocato oltre il limite ({r['Impegno_%']}%). Richiesto intervento in Resource Allocation.</div>", unsafe_allow_html=True)
                
                if len(commesse_loss) > 0:
                    st.markdown("<h3 style='color: #F59E0B; margin-top:20px;'>🟠 Allarmi Erosione Margine</h3>", unsafe_allow_html=True)
                    for _, c in commesse_loss.iterrows():
                        st.markdown(f"<div class='alert-box alert-orange'>La commessa <b>{c['ID_Commessa']}</b> ha superato il budget stimato.<br>Costo Consuntivato: <b>{formatta_valuta(c['Costo_Tot_Riga'])}</b> | Budget Originale: <b>{formatta_valuta(c['Budget'])}</b>.</div>", unsafe_allow_html=True)
                
                if len(st.session_state.pending_allocations) > 0:
                    st.markdown("<h3 style='color: #3B82F6; margin-top:20px;'>🔵 Richieste in Sospeso (Workspace)</h3>", unsafe_allow_html=True)
                    for req in st.session_state.pending_allocations:
                        st.markdown(f"<div class='alert-box alert-blue'>L'utente <b>{req['Nome']}</b> ha richiesto l'allocazione al {req['Occupazione']}% sul progetto {req['Progetto']}. (Autorizzabile in Resource Allocation).</div>", unsafe_allow_html=True)

        elif pagina_pm == "Project Hub":
            st.markdown("<h1 class='gradient-title'>Project Hub</h1>", unsafe_allow_html=True)
            with st.expander("➕ Genera Nuova Commessa", expanded=False):
                with st.form("form_nuova_commessa"):
                    col1, col2 = st.columns(2)
                    n_id = col1.text_input("Codice Identificativo Progetto")
                    n_cliente = col2.text_input("Ragione Sociale Cliente")
                    n_nome = col1.text_input("Definizione Progetto")
                    n_budget = col2.number_input("Budget Autorizzato (€)", min_value=1000, step=1000, value=50000)
                    n_stato = col1.selectbox("Status Operativo", ["In Avvio", "Attivo", "Sospeso", "Chiuso"])
                    if st.form_submit_button("Inserisci a Sistema"):
                        if n_id and n_cliente:
                            nuova = pd.DataFrame([{"ID_Commessa": n_id, "Cliente": n_cliente, "Nome": n_nome, "Budget": n_budget, "Stato": n_stato}])
                            st.session_state.df_commesse = pd.concat([st.session_state.df_commesse, nuova], ignore_index=True)
                            st.rerun()

            st.markdown("### Database Commesse Attive")
            edited_comm = st.data_editor(st.session_state.df_commesse, use_container_width=True, num_rows="dynamic", column_config={"Budget": st.column_config.NumberColumn(format="€ %d")})
            if st.button("Sincronizza Modifiche Globali"):
                st.session_state.df_commesse = edited_comm
                st.success("Database aggiornato.")

        elif pagina_pm == "Resource Allocation":
            st.markdown("<h1 class='gradient-title'>Allocazione risorse</h1>", unsafe_allow_html=True)
            st.subheader("Richieste in Sospeso")
            if len(st.session_state.pending_allocations) > 0:
                for i, req in enumerate(list(st.session_state.pending_allocations)):
                    with st.container(border=True):
                        st.write(f"Utente **{req['Nome']}** ha richiesto {req['Occupazione']}% su **{req['Progetto']}** (Finestra: {formatta_data(req['Dal'])} -> {formatta_data(req['Al'])})")
                        b1, b2 = st.columns(2)
                        if b1.button("Autorizza Assegnazione", key=f"ok_{i}"):
                            id_ris = df_risorse[df_risorse['Nome'] == req['Nome']]['ID'].values[0]
                            nuova = pd.DataFrame([{"ID_Risorsa": id_ris, "ID_Commessa": req['Progetto'], "Impegno_%": req['Occupazione']}])
                            st.session_state.df_allocazioni = pd.concat([st.session_state.df_allocazioni, nuova], ignore_index=True)
                            st.session_state.pending_allocations.pop(i); st.rerun()
                        if b2.button("Rigetta Richiesta", key=f"ko_{i}"):
                            st.session_state.pending_allocations.pop(i); st.rerun()
            else: st.caption("La coda delle richieste utente è vuota.")
            
            st.divider()
            col_l, col_r = st.columns(2)
            with col_l:
                st.subheader("Modulo di Override")
                with st.form("manual_alloc"):
                    r_scelta = st.selectbox("Seleziona Consulente:", df_risorse['Nome'].tolist())
                    commesse_disp = df_commesse['ID_Commessa'] + " - " + df_commesse['Cliente']
                    c_scelta = st.selectbox("Seleziona Progetto/Commessa:", commesse_disp.tolist())
                    perc = st.slider("Assegnazione Impegno (%)", 0, 100, 100, 25)
                    if st.form_submit_button("Esegui Forzatura / Assegna"):
                        id_risorsa = df_risorse[df_risorse['Nome'] == r_scelta]['ID'].values[0]
                        id_commessa = c_scelta.split(" - ")[0]
                        nuova_alloc = pd.DataFrame([{"ID_Risorsa": id_risorsa, "ID_Commessa": id_commessa, "Impegno_%": perc}])
                        st.session_state.df_allocazioni = pd.concat([st.session_state.df_allocazioni, nuova_alloc], ignore_index=True); st.rerun()

            with col_r:
                st.subheader("Gestione e Revoca Assegnazioni")
                if not df_allocazioni.empty:
                    alloc_view = pd.merge(df_allocazioni, df_risorse[['ID', 'Nome']], left_on='ID_Risorsa', right_on='ID')
                    opz = [f"[{idx}] {r['Nome']} -> Commessa {r['ID_Commessa']} ({r['Impegno_%']}%)" for idx, r in alloc_view.iterrows()]
                    with st.form("remove_alloc"):
                        da_rimuovere = st.selectbox("Punta record da sganciare:", opz)
                        if st.form_submit_button("Revoca Definitiva"):
                            idx_to_drop = int(da_rimuovere.split("]")[0].replace("[", ""))
                            real_idx = alloc_view.loc[idx_to_drop].name
                            st.session_state.df_allocazioni = st.session_state.df_allocazioni.drop(index=real_idx); st.rerun()
                else: st.caption("Il database allocazioni è vuoto.")

        elif pagina_pm == "Allocation Advisor":
            st.markdown("<h1 class='gradient-title'>Allocation Advisor</h1>", unsafe_allow_html=True)
            
            prompt_random = [
                "Sviluppo di un sistema ERP Cloud-native per la logistica aziendale. Il frontend deve essere realizzato interamente in React utilizzando TypeScript. Il backend richiede una solida architettura a microservizi sviluppata in Go e Node.js. È fondamentale l'implementazione di pipeline CI/CD con GitHub Actions, containerizzazione tramite Docker e orchestrazione Kubernetes su AWS. Necessario anche un esperto per l'ottimizzazione del database PostgreSQL e l'analisi predittiva (Python/Pandas).",
                "Rifacimento completo del portale di Home Banking e transazioni sicure. La sicurezza è la priorità: richiesto framework Angular per la web app responsive e Java (Spring Boot) per i processi core di transazione. Il team deve includere DevOps Engineer per la gestione dell'infrastruttura Terraform su cloud AWS, oltre a Data Analyst qualificati per la reportistica direzionale tramite SQL e PowerBI.",
                "Creazione di una piattaforma IoT Edge per il monitoraggio in tempo reale di macchinari industriali. I dati provenienti dai sensori verranno raccolti tramite script Python e processati con algoritmi avanzati di Machine Learning (Scikit-learn). La dashboard di controllo per gli operatori sarà sviluppata in Vue.js. L'infrastruttura backend poggerà completamente su servizi cloud AWS serverless (Lambda e DynamoDB).",
                "Progetto di modernizzazione e migrazione di un CRM Legacy. Migrazione massiva dei dati storici in SQL verso un nuovo database documentale NoSQL. Il frontend applicativo sarà ricostruito da zero sfruttando React. Serve un Business Analyst per la mappatura dei processi BPMN e la gestione dei requisiti tecnici, affiancato da un Project Manager specializzato in Agile/Scrum per coordinare gli sprint di sviluppo.",
                "Sviluppo di una piattaforma e-learning video-based ad alto traffico. Il backend per la gestione dello streaming e degli utenti sarà scritto in Node.js con storage distribuito su AWS S3. Il client web necessita di competenze avanzate in HTML/CSS e TypeScript. È richiesta inoltre la presenza di un Data Scientist che si occuperà di creare il motore di raccomandazione dei corsi basato in Python e logiche SQL complesse.",
                "Sviluppo architettura GenAI Chatbot integrata nel portale HR interno. Richiesta conoscenza approfondita di LangChain e Python per orchestrare le chiamate LLM, oltre alla gestione di un database vettoriale (es. Pinecone). Il layer di interfaccia sarà basato su React e il deployment avverrà tramite Kubernetes su cluster privato."
            ]
            
            if "saved_testo_brief" not in st.session_state: st.session_state.saved_testo_brief = ""
            if st.button("Generazione automatica di prompt per fase Test"):
                st.session_state.saved_testo_brief = random.choice(prompt_random)
                
            testo = st.text_area("Input Requirement (Descrizione del progetto):", value=st.session_state.saved_testo_brief, height=140)
            st.session_state.saved_testo_brief = testo

            if st.button("Simula Scenario e Trova Copertura", type="primary"):
                fasi, skill_richieste, err_msg = analizza_testo_llm(testo, st.session_state.groq_api_key)
                
                if err_msg:
                    st.error(err_msg)
                elif not fasi: 
                    st.warning("Non è stato possibile mappare i requisiti. Inserire tecnologie riconoscibili (es. React, Node, Python, AWS).")
                else:
                    st.session_state.wbs_data = pd.DataFrame(fasi)
                    team = []
                    for skill in skill_richieste:
                        for _, r in df_risorse.iterrows():
                            if get_saturazione(r['ID'], df_allocazioni) < 100 and skill.lower() in r['Skill'].lower():
                                team.append({"Skill": skill, "Nome": r['Nome'], "Costo (€)": r['Costo_Giorno'], "Margine (%)": 30})
                                break
                        else: team.append({"Skill": skill, "Nome": "ASSUNZIONE NECESSARIA", "Costo (€)": 300, "Margine (%)": 30})
                    st.session_state.team_data = pd.DataFrame(team)

            if "wbs_data" in st.session_state and not st.session_state.wbs_data.empty:
                tab_wbs, tab_team = st.tabs(["Work Breakdown Structure (WBS)", "Assessment Economico Team"])
                with tab_wbs: 
                    st.session_state.wbs_data = st.data_editor(st.session_state.wbs_data, num_rows="dynamic", use_container_width=True)
                with tab_team:
                    st.session_state.team_data = st.data_editor(
                        st.session_state.team_data, use_container_width=True,
                        column_config={"Costo (€)": st.column_config.NumberColumn(step=50), "Margine (%)": st.column_config.NumberColumn(step=5)}
                    )
                    costo_tot, prop_comm = 0, 0
                    for _, row in st.session_state.wbs_data.iterrows():
                        m = st.session_state.team_data[st.session_state.team_data['Skill'] == row['Skill']]
                        if not m.empty:
                            c = row['Giorni'] * m.iloc[0]['Costo (€)']
                            costo_tot += c; prop_comm += c * (1 + (m.iloc[0]['Margine (%)'] / 100))
                    
                    st.markdown("<br><div style='font-size: 1.6rem; font-weight: 700; color: var(--text-color); margin-bottom: 15px;'>Previsione Finanziaria di Commessa</div>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"<div class='kpi-card orange'><h3>Spesa Operativa (OPEX)</h3><h2>{formatta_valuta(costo_tot)}</h2></div>", unsafe_allow_html=True)
                    c2.markdown(f"<div class='kpi-card blue'><h3>Valore Offerta (Mercato)</h3><h2>{formatta_valuta(prop_comm)}</h2></div>", unsafe_allow_html=True)
                    c3.markdown(f"<div class='kpi-card green'><h3>Margine Utile Atteso</h3><h2>{formatta_valuta(prop_comm - costo_tot)}</h2></div>", unsafe_allow_html=True)

        elif pagina_pm == "Build your Team":
            st.markdown("<h1 class='gradient-title'>Build your Team</h1>", unsafe_allow_html=True)
            c_f1, c_f2 = st.columns(2)
            f_sen = c_f1.multiselect("Filtro Seniority:", ["Junior", "Mid", "Senior"], default=st.session_state.get('s_t_fil', ["Senior", "Mid", "Junior"]))
            st.session_state.s_t_fil = f_sen
            df_f = df_risorse[df_risorse['Seniority'].isin(f_sen)] if f_sen else df_risorse
            v_t = [x for x in st.session_state.get('s_t_sel', []) if x in df_f['Nome'].tolist()]
            t_sel = c_f2.multiselect("Analizza i seguenti profili:", df_f['Nome'].tolist(), default=v_t)
            st.session_state.s_t_sel = t_sel
            
            vista_tipo = st.radio("Selettore Interfaccia Visiva:", ["Vista Mensile (Calendario a blocchi)", "Vista Giornaliera (Scheduling Assistant)"], horizontal=True)
            
            if t_sel:
                oggi = datetime.today()
                mese_offset = st.session_state.get('team_cal_idx', 0)
                
                # Calcolo mese ciclico
                anno_c = oggi.year
                mese_c = oggi.month + mese_offset
                while mese_c > 12:
                    mese_c -= 12; anno_c += 1
                while mese_c < 1:
                    mese_c += 12; anno_c -= 1

                mesi_ita = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
                
                c_p, c_m, c_n = st.columns([1,2,1])
                if c_p.button("⬅️ Retrocedi Mese"): st.session_state.team_cal_idx -= 1; st.rerun()
                if c_n.button("Avanza Mese ➡️"): st.session_state.team_cal_idx += 1; st.rerun()
                c_m.markdown(f"<h3 style='text-align:center; color:#3B82F6;'>{mesi_ita[mese_c]} {anno_c}</h3>", unsafe_allow_html=True)
                
                cal = calendar.Calendar(firstweekday=0)
                giorni_del_mese = [d for d in cal.itermonthdates(anno_c, mese_c) if d.month == mese_c]

                if vista_tipo == "Vista Giornaliera (Scheduling Assistant)":
                    html_grid = "<div class='scheduling-container'><div>"
                    html_grid += "<div class='scheduling-row'><div class='scheduling-name'>Profili Analizzati</div>"
                    for d in giorni_del_mese:
                        giorno_let = ["L", "M", "M", "G", "V", "S", "D"][d.weekday()]
                        html_grid += f"<div class='scheduling-header'>{giorno_let}<br>{d.day}</div>"
                    html_grid += "</div>"
                    
                    for nome in t_sel:
                        r_id = df_risorse[df_risorse['Nome'] == nome]['ID'].values[0]
                        sat = get_saturazione(r_id, df_allocazioni)
                        prog_att = get_progetti_risorsa(r_id, df_allocazioni, df_commesse)
                        
                        html_grid += f"<div class='scheduling-row'><div class='scheduling-name'>{nome}<br><span style='font-size:11px; color:var(--kpi-text-sub); font-weight:400;'>{prog_att}</span></div>"
                        for d in giorni_del_mese:
                            if d.weekday() >= 5: bg = "#21262D" if st.get_option("theme.base") == "dark" else "#E5E7EB"
                            elif sat == 0: bg = "#EF4444"
                            elif sat < 100: bg = "#F59E0B"
                            else: bg = "#10B981"
                            html_grid += f"<div class='scheduling-cell' style='background:{bg}; color: transparent;'>.</div>"
                        html_grid += "</div>"
                    html_grid += "</div></div>"
                    st.markdown(html_grid, unsafe_allow_html=True)
                
                else:
                    cols_per_row = 3
                    for i in range(0, len(t_sel), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, nome in enumerate(t_sel[i:i+cols_per_row]):
                            with cols[j]:
                                r_id = df_risorse[df_risorse['Nome'] == nome]['ID'].values[0]
                                sat = get_saturazione(r_id, df_allocazioni)
                                prog_att = get_progetti_risorsa(r_id, df_allocazioni, df_commesse)
                                
                                st.markdown(f"<h5 style='text-align:center; color:var(--text-color); margin-bottom:0px;'>{nome}</h5>", unsafe_allow_html=True)
                                st.markdown(f"<p style='text-align:center; font-size:12px; color:var(--kpi-text-sub); margin-top:2px; margin-bottom:10px;'>{prog_att}</p>", unsafe_allow_html=True)
                                
                                html_cal = "<div style='display:grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 30px;'>"
                                for g in ["Lu","Ma","Me","Gi","Ve","Sa","Do"]: html_cal += f"<div style='text-align:center; font-size:10px;'>{g}</div>"
                                for week in cal.monthdatescalendar(anno_c, mese_c):
                                    for day in week:
                                        if day.month != mese_c: html_cal += "<div></div>"
                                        else:
                                            if day.weekday() >= 5: bg = "#21262D" if st.get_option("theme.base") == "dark" else "#E5E7EB"
                                            elif sat == 0: bg = "#EF4444"
                                            elif sat < 100: bg = "#F59E0B"
                                            else: bg = "#10B981"
                                            html_cal += f"<div style='background-color:{bg}; height:32px; border-radius:4px; display:flex; align-items:center; justify-content:center; font-size:12px; color:#FFF;'>{day.day}</div>"
                                html_cal += "</div>"
                                st.markdown(html_cal, unsafe_allow_html=True)

        elif pagina_pm == "Project Portfolio":
            st.markdown("<h1 class='gradient-title'>Project Portfolio</h1>", unsafe_allow_html=True)
            if not df_timesheet.empty:
                ts_merged = pd.merge(df_timesheet, df_risorse[['ID', 'Costo_Giorno']], left_on='ID_Risorsa', right_on='ID')
                ts_merged['Costo_Riga'] = ts_merged['Giornate_Spese'] * ts_merged['Costo_Giorno']
                agg_costi = ts_merged.groupby('ID_Commessa')['Costo_Riga'].sum().reset_index()
                df_view = pd.merge(df_commesse, agg_costi, on='ID_Commessa', how='left').fillna(0)
                df_view.rename(columns={'Costo_Riga': 'Costo_Attuale'}, inplace=True)
            else:
                df_view = df_commesse.copy(); df_view['Costo_Attuale'] = 0

            df_view['Delta Margin'] = df_view['Budget'] - df_view['Costo_Attuale']
            
            df_view_formatted = df_view[['ID_Commessa', 'Cliente', 'Nome', 'Budget', 'Costo_Attuale', 'Delta Margin', 'Stato']].copy()
            df_view_formatted['Budget'] = df_view_formatted['Budget'].apply(formatta_valuta)
            df_view_formatted['Costo_Attuale'] = df_view_formatted['Costo_Attuale'].apply(formatta_valuta)
            df_view_formatted['Delta Margin'] = df_view_formatted['Delta Margin'].apply(formatta_valuta)

            st.dataframe(df_view_formatted, hide_index=True, use_container_width=True)

        elif pagina_pm == "Profile Explorer":
            st.markdown("<h1 class='gradient-title'>Profile Explorer</h1>", unsafe_allow_html=True)
            nomi = df_risorse['Nome'].tolist()
            s_nome = st.session_state.get('s_ind_nome', nomi[0])
            nome_ric = st.selectbox("Ricerca per Anagrafica:", nomi, index=nomi.index(s_nome) if s_nome in nomi else 0)
            st.session_state.s_ind_nome = nome_ric
            
            if nome_ric:
                dati = df_risorse[df_risorse['Nome'] == nome_ric].iloc[0]
                id_ric = dati['ID']
                sat = get_saturazione(id_ric, df_allocazioni)
                
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div class='kpi-card blue'><h3>Livello Inquadramento</h3><h2>{dati['Ruolo']}</h2></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='kpi-card orange'><h3>Competenze Core</h3><p style='font-size:18px; color:var(--text-color); font-weight:700;'>{dati['Skill']}</p></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='kpi-card green'><h3>Saturazione Lavorativa</h3><p style='font-size:22px; font-weight:700; color:var(--text-color);'>{sat}%</p></div>", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("Dettaglio Cliente e Commesse Assegnate")
                allocs_risorsa = df_allocazioni[df_allocazioni['ID_Risorsa'] == id_ric]
                
                if not allocs_risorsa.empty:
                    for i, a in allocs_risorsa.iterrows():
                        match_c = df_commesse[df_commesse['ID_Commessa'] == a['ID_Commessa']]
                        nome_progetto = match_c['Nome'].values[0]
                        cliente_assegnato = match_c['Cliente'].values[0]
                        
                        with st.container(border=True):
                            c_a, c_b, c_c = st.columns([3, 1, 1])
                            c_a.write(f"**Cliente:** {cliente_assegnato} | **Progetto:** {a['ID_Commessa']} - {nome_progetto}")
                            c_b.write(f"**Impegno:** {a['Impegno_%']}%")
                            if c_c.button("Revoca Assegnazione", key=f"rev_{i}"):
                                st.session_state.df_allocazioni = st.session_state.df_allocazioni.drop(i)
                                st.rerun()
                else:
                    st.info("La risorsa non è associata ad alcun cliente (Bench).")

        elif pagina_pm == "Resource Master Data":
            st.markdown("<h1 class='gradient-title'>Resource Master Data</h1>", unsafe_allow_html=True)
            df_v = df_risorse.copy()
            df_v['Sat_%'] = df_v['ID'].apply(lambda x: get_saturazione(x, df_allocazioni))
            df_v['Progetti/Clienti'] = df_v['ID'].apply(lambda x: get_progetti_risorsa(x, df_allocazioni, df_commesse))
            df_v['Costo_Giorno'] = df_v['Costo_Giorno'].apply(formatta_valuta)
            st.dataframe(df_v[['ID', 'Nome', 'Macro_Area', 'Ruolo', 'Sat_%', 'Progetti/Clienti', 'Costo_Giorno']], column_config={"Sat_%": st.column_config.ProgressColumn("Saturazione %", format="%d%%")}, hide_index=True, use_container_width=True)

# ==========================================
# VISTA 2: TALENT WORKSPACE
# ==========================================
elif ruolo_utente == "Talent Workspace":
    if not st.session_state.it_logged_in:
        st.markdown("<h1 class='gradient-title'>Gateway di Autenticazione Personale</h1>", unsafe_allow_html=True)
        with st.form("login_it_form"):
            utente_selezionato = st.selectbox("Selettore Identità", df_risorse['Nome'].tolist())
            password_it = st.text_input("Codice Sicurezza", type="password")
            if st.form_submit_button("Esegui Login"):
                if password_it == "dev123":
                    st.session_state.it_logged_in, st.session_state.current_it_user = True, utente_selezionato
                    st.rerun()
                else: st.error("Accesso Negato.")
    else:
        st.markdown(f"<h1 class='gradient-title'>Dashboard Personale: {st.session_state.current_it_user}</h1>", unsafe_allow_html=True)
        if st.button("Logout"): st.session_state.it_logged_in = False; st.rerun()
            
        dati_utente = df_risorse[df_risorse['Nome'] == st.session_state.current_it_user].iloc[0]
        id_c = dati_utente['ID']
        sat_attuale = get_saturazione(id_c, df_allocazioni)
        prog_attuali = get_progetti_risorsa(id_c, df_allocazioni, df_commesse)
        
        tab_p, tab_ts = st.tabs(["Dashboard Personale", "Consuntivazione (Timesheet)"])
        
        with tab_p:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div class='kpi-card kpi-card-shadow blue'><h3>Attributi Profilo</h3>", unsafe_allow_html=True)
                st.write(f"**Dominio Tecnico:** {dati_utente['Ruolo']}\n\n**Inventario Competenze:** {dati_utente['Skill']}\n\n**Stato Assegnazioni:** {sat_attuale}% Saturazione -> {prog_attuali}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.subheader("Processo Espansione Competenze")
                ns = st.text_input("Segnala Nuova Tecnologia (es. Go, Terraform):")
                if st.button("Sottoponi per Validazione") and ns:
                    st.success("Iter di Validazione Avviato.")
            with c2:
                st.markdown("<div class='kpi-card kpi-card-shadow orange'><h3>Richiesta Cambio Progetto</h3>", unsafe_allow_html=True)
                with st.form("req"):
                    p_req = st.text_input("Inserisci ID o Nome Progetto Target")
                    d_req = st.slider("Disponibilità (FTE %)", 25, 100, 50, 25)
                    dt_req = st.date_input("Restrizione Temporale", value=(datetime.today(), datetime.today()+timedelta(days=30)))
                    if st.form_submit_button("Invia Richiesta") and len(dt_req)==2:
                        st.session_state.pending_allocations.append({"ID": id_c, "Nome": dati_utente['Nome'], "Progetto": p_req, "Occupazione": d_req, "Dal": dt_req[0], "Al": dt_req[1]})
                        st.success("Notifica inserita in coda nel Resource Allocation Engine.")
                st.markdown("</div>", unsafe_allow_html=True)
                
        with tab_ts:
            st.subheader("Registrazione Attività Mensile")
            mie_comm = df_allocazioni[df_allocazioni['ID_Risorsa'] == id_c]
            if mie_comm.empty: st.warning("Il tuo profilo risulta a Bench. Nessuna commessa attiva da consuntivare.")
            else:
                opz = [f"{c['ID_Commessa']} - {df_commesse[df_commesse['ID_Commessa']==c['ID_Commessa']]['Nome'].values[0]}" for _, c in mie_comm.iterrows()]
                with st.form("ts_form"):
                    sel = st.selectbox("Seleziona Progetto Lavorato", opz)
                    gg = st.number_input("Effort in Giornate (FTE)", 0.5, 31.0, 1.0, 0.5)
                    if st.form_submit_button("Registra Consuntivo in Master Data"):
                        id_c_target = sel.split(" - ")[0]
                        nuovo_ts = pd.DataFrame([{"ID_Risorsa": id_c, "ID_Commessa": id_c_target, "Data_Inizio_Progetto": datetime.now().strftime("%Y-%m-%d"), "Giornate_Spese": gg}])
                        st.session_state.df_timesheet = pd.concat([st.session_state.df_timesheet, nuovo_ts], ignore_index=True)
                        st.success("Transazione confermata. Consuntivato inviato per la generazione dei costi di commessa.")
                        
            st.markdown("---")
            st.subheader("Storico Caricamenti Personali")
            mio_ts = df_timesheet[df_timesheet['ID_Risorsa'] == id_c].copy()
            if not mio_ts.empty:
                mio_ts['Data_Inizio_Progetto'] = mio_ts['Data_Inizio_Progetto'].apply(formatta_data)
                st.dataframe(mio_ts[['ID_Commessa', 'Data_Inizio_Progetto', 'Giornate_Spese']], use_container_width=True, hide_index=True)
            else:
                st.caption("Nessun timesheet loggato in precedenza.")

# ==========================================
# VISTA 3: TALENT MANAGEMENT
# ==========================================
elif ruolo_utente == "Talent Management":
    if not st.session_state.hr_logged_in:
        st.markdown("<h1 class='gradient-title'>Gateway Amministrativo HR</h1>", unsafe_allow_html=True)
        with st.form("login_hr"):
            username = st.text_input("Codice Reparto")
            password = st.text_input("Chiave Accesso", type="password")
            if st.form_submit_button("Esegui Login"):
                if username == "hr" and password == "hr123":
                    st.session_state.hr_logged_in = True; st.rerun()
                else: 
                    st.error("Credenziali Errate. Usare hr / hr123")
    else:
        # --- MENU NATIVO STREAMLIT HR ---
        st.sidebar.markdown("<p style='font-size:12px; color:var(--kpi-text-sub); margin-bottom:0px; font-weight:600; text-transform:uppercase;'>Sezione Principale</p>", unsafe_allow_html=True)
        hr_main = st.sidebar.radio("Sezione Principale", ["Homepage", "Talent Lifecycle", "HR Operations", "Data Hub"], label_visibility="collapsed")
        
        pagina_hr = "Homepage"
        if hr_main == "Talent Lifecycle":
            st.sidebar.markdown("<p style='font-size:12px; color:var(--kpi-text-sub); margin-top:15px; margin-bottom:0px; font-weight:600; text-transform:uppercase;'>Ciclo di Vita</p>", unsafe_allow_html=True)
            s_tab = st.sidebar.radio("Sottomenu", ["Talent Onboarding", "Career Development"], label_visibility="collapsed")
            pagina_hr = s_tab
        elif hr_main == "HR Operations":
            st.sidebar.markdown("<p style='font-size:12px; color:var(--kpi-text-sub); margin-top:15px; margin-bottom:0px; font-weight:600; text-transform:uppercase;'>Operatività</p>", unsafe_allow_html=True)
            s_tab = st.sidebar.radio("Sottomenu", ["ERP Integration"], label_visibility="collapsed")
            pagina_hr = s_tab
        elif hr_main == "Data Hub":
            st.sidebar.markdown("<p style='font-size:12px; color:var(--kpi-text-sub); margin-top:15px; margin-bottom:0px; font-weight:600; text-transform:uppercase;'>Repository Dati</p>", unsafe_allow_html=True)
            s_tab = st.sidebar.radio("Sottomenu", ["Data Repository"], label_visibility="collapsed")
            pagina_hr = s_tab
        
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        if st.sidebar.button("Termina Sessione"): st.session_state.hr_logged_in = False; st.rerun()

        if pagina_hr == "Homepage":
            st.markdown("<h1 class='gradient-title'>Talent Management Metrics</h1>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='kpi-card blue'><h3>Headcount Aggregato</h3><h2>{len(df_risorse)}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='kpi-card orange'><h3>Indice Età Teorico</h3><h2>32 Anni</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='kpi-card green'><h3>Costo Base Ponderato</h3><h2>{formatta_valuta(df_risorse['Costo_Giorno'].mean())}</h2></div>", unsafe_allow_html=True)

            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Rapporto Gerarchico")
                df_sen = df_risorse['Seniority'].value_counts().reset_index()
                df_sen.columns = ['Seniority', 'Conteggio']
                fig1 = px.pie(df_sen, values='Conteggio', names='Seniority', hole=0.4, color_discrete_sequence=px.colors.sequential.Tealgrn)
                fig1 = applica_tema_plotly(fig1)
                fig1.update_layout(showlegend=False)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_chart2:
                st.subheader("Assorbimento per Cluster")
                aree_disponibili = ["Tutto il Gruppo"] + sorted(list(df_risorse['Macro_Area'].unique()))
                area_selezionata = st.selectbox("Filtro Divisionale:", aree_disponibili)
                df_ruoli = df_risorse if area_selezionata == "Tutto il Gruppo" else df_risorse[df_risorse['Macro_Area'] == area_selezionata]
                df_ruoli = df_ruoli['Ruolo'].str.replace('Senior ', '').str.replace('Mid ', '').str.replace('Junior ', '').value_counts().reset_index()
                df_ruoli.columns = ['Ruolo', 'Conteggio']
                fig2 = px.bar(df_ruoli, x='Ruolo', y='Conteggio', color='Ruolo', color_discrete_sequence=px.colors.sequential.Blues_r)
                fig2 = applica_tema_plotly(fig2)
                fig2.update_layout(showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        elif pagina_hr == "Talent Onboarding":
            st.markdown("<h1 class='gradient-title'>Talent Onboarding</h1>", unsafe_allow_html=True)
            with st.form("onb"):
                c1, c2 = st.columns(2)
                nome = c1.text_input("Nominativo Legale Assunto")
                sen = c2.selectbox("Collocazione Seniority", ["Junior", "Mid", "Senior"])
                ruolo = c1.selectbox("Dominio d'Inquadramento", ["Frontend Developer", "Backend Developer", "Fullstack Developer", "DevOps Engineer", "Data Scientist", "Data Analyst", "Project Manager", "Business Analyst"])
                skill = c2.text_input("Matrice Competenze (csv format)")
                costo_gg = c1.number_input("Costo Standard Aziendale (OPEX)", min_value=50, max_value=1500, value=200, step=10)
                
                if st.form_submit_button("Sincronizza in Database Master") and nome:
                    macro_area_auto = "IT" if "Developer" in ruolo or "DevOps" in ruolo else "Data Science" if "Data" in ruolo else "Risk/Management"
                    nuovo = pd.DataFrame([{"ID": f"RES-{len(df_risorse)+1000}", "Nome": nome, "Macro_Area": macro_area_auto, "Ruolo": f"{sen} {ruolo}", "Seniority": sen, "Skill": skill, "Costo_Giorno": costo_gg, "Tariffa_Vendita": costo_gg*1.4, "Disponibile_dal": datetime.now().strftime("%Y-%m-%d")}])
                    st.session_state.df_risorse = pd.concat([st.session_state.df_risorse, nuovo], ignore_index=True)
                    st.success(f"L'anagrafica di {nome} è stata resa visibile e utilizzabile da tutti i dipartimenti.")

        elif pagina_hr == "Career Development":
            st.markdown("<h1 class='gradient-title'>Career Development</h1>", unsafe_allow_html=True)
            n_sel = st.selectbox("Seleziona Collaboratore dal Master Data:", df_risorse['Nome'].tolist())
            if n_sel:
                idx = df_risorse.index[df_risorse['Nome']==n_sel].tolist()[0]
                dati = df_risorse.iloc[idx]
                with st.form("mod"):
                    st.write(f"Gestione Upgrade: **{n_sel}**")
                    c1, c2 = st.columns(2)
                    sen = c1.selectbox("Nuovo Livello", ["Junior", "Mid", "Senior"], index=["Junior", "Mid", "Senior"].index(dati['Seniority']))
                    costo_gg = c2.number_input("Nuovo Costo Giornaliero (€)", value=int(dati['Costo_Giorno']), step=10)
                    if st.form_submit_button("Esegui Manutenzione Parametri"):
                        st.session_state.df_risorse.at[idx, 'Seniority'] = sen
                        st.session_state.df_risorse.at[idx, 'Costo_Giorno'] = costo_gg
                        st.success("Dati aggiornati correttamente nell'ERP Centrale."); st.rerun()

        elif pagina_hr == "ERP Integration":
            st.markdown("<h1 class='gradient-title'>ERP Integration (Paghe/Fatturazione)</h1>", unsafe_allow_html=True)
            st.write("Modulo di raccordo per allineare l'infrastruttura Cloud con i sistemi aziendali legacy (Zucchetti, SAP, ecc.).")
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns([1, 1])
            with c1:
                st.download_button("Download", data=df_risorse.to_csv(index=False).encode('utf-8'), file_name='export_hr_erp.csv', use_container_width=True)
            with c2:
                up = st.file_uploader("Upload", type=['csv'], label_visibility="collapsed")
                if up: st.success("Decodifica file avvenuta con successo. Dati pronti al merge.")

        elif pagina_hr == "Data Repository":
            st.markdown("<h1 class='gradient-title'>Data Repository</h1>", unsafe_allow_html=True)
            df_v = df_risorse.copy()
            df_v['Disponibile_dal'] = df_v['Disponibile_dal'].apply(formatta_data)
            st.dataframe(df_v, hide_index=True, use_container_width=True)

# ==========================================
# 4. COMPONENTE COPILOT AI (WIDGET INFERIORE)
# ==========================================
if (st.session_state.pm_logged_in or st.session_state.hr_logged_in):
    st.sidebar.markdown("<br><hr style='border-color: rgba(128,128,128,0.2);'>", unsafe_allow_html=True)
    with st.sidebar.popover("Smart Assistant", use_container_width=True):
        st.caption("Motore LLM LLaMA-3 (Attivo)" if st.session_state.groq_api_key else "Motore Regex (Fallback Attivo)")
        for m in st.session_state.chat_msgs: 
            st.chat_message(m["role"]).write(m["content"])
        
        if st.session_state.bot_action:
            act = st.session_state.bot_action
            if st.button("Autorizza Transazione"): 
                esegui_azione_chatbot(act); st.rerun()
            if st.button("Sospendi"): 
                st.session_state.bot_action = None; st.rerun()
                
        if prompt := st.chat_input("Esegui istruzione..."):
            st.session_state.chat_msgs.append({"role": "user", "content": prompt})
            action, err = parse_chatbot_intent_llm(prompt, df_risorse, st.session_state.groq_api_key)
            if err: 
                st.session_state.chat_msgs.append({"role": "assistant", "content": err})
            else: 
                st.session_state.bot_action = action
            st.rerun()
            
    with st.sidebar.expander("Configurazione Root Backend AI"):
        st.write("*Note: Interfaccia lasciata in evidenza unicamente per agevolare le simulazioni di override del motore LLM (dimostrazione del fallback deterministico).*")
        st.session_state.groq_api_key = st.text_input("Groq API Key (Bearer):", value=st.session_state.groq_api_key, type="password")
