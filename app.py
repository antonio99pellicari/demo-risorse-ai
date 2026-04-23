import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import re
import plotly.express as px
import calendar
import requests
import json
import io

# ==========================================
# 1. INIZIALIZZAZIONE E CONFIGURAZIONE
# ==========================================
st.set_page_config(page_title="ResourceAI - Manager", layout="wide", initial_sidebar_state="expanded")

# --- INIEZIONE CSS CORPORATE SAAS (TEMA ADATTIVO LIGHT/DARK MIGLIORATO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
    
    /* FIX CONTRASTO: Forza colori chiari e leggibili sui temi scuri */
    p, span, div, label, li { color: #E5E7EB !important; }
    h1, h2, h3, h4, h5, h6 { color: #F9FAFB !important; font-weight: 600 !important; }
    
    .stButton>button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        transition: all 0.3s ease !important;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        color: #F9FAFB !important;
        background-color: rgba(255,255,255,0.05) !important;
    }
    .stButton>button:hover {
        border-color: #3B82F6 !important;
        color: #3B82F6 !important;
        background-color: rgba(59,130,246,0.1) !important;
    }
    
    .gradient-title {
        background: linear-gradient(45deg, #60A5FA, #34D399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        font-size: 2.6rem !important;
        margin-bottom: 0.5rem;
        margin-top: -1rem;
        letter-spacing: -0.5px;
    }
    
    /* Variabili Adattive per Light e Dark Mode */
    :root {
        --kpi-bg: rgba(0,0,0,0.03);
        --kpi-border: rgba(255,255,255,0.1);
        --kpi-text-main: #FFFFFF;
        --kpi-text-sub: #D1D5DB; 
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --kpi-bg: linear-gradient(145deg, rgba(30,40,50,0.8) 0%, rgba(15,20,25,0.9) 100%);
            --kpi-border: rgba(255,255,255,0.15);
            --kpi-text-main: #FFFFFF;
            --kpi-text-sub: #E5E7EB;
        }
        /* Fix per inputs e griglie personalizzate */
        .stTextInput>div>div>input, .stNumberInput>div>div>input {
            color: #FFFFFF !important;
            font-weight: 500 !important;
        }
    }
    
    .kpi-card {
        background: var(--kpi-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--kpi-border);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }
    
    .kpi-card-shadow { box-shadow: 0 8px 30px rgba(0,0,0,0.3) !important; }
    
    .kpi-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; }
    .kpi-card.blue::before { background: #60A5FA; }
    .kpi-card.green::before { background: #34D399; }
    .kpi-card.red::before { background: #F87171; }
    .kpi-card.orange::before { background: #FBBF24; }
    
    .kpi-card h3 { color: var(--kpi-text-sub) !important; font-size: 0.85rem !important; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0; margin-bottom: 8px;}
    .kpi-card h2 { color: var(--kpi-text-main) !important; font-size: 2.2rem !important; font-weight: 700 !important; margin: 0; letter-spacing: -0.5px;}
    
    .alert-box {
        padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid; background: rgba(255,255,255,0.05); color: #FFF; font-weight: 500;
    }
    .alert-red { border-color: #F87171; }
    .alert-orange { border-color: #FBBF24; }
    .alert-blue { border-color: #60A5FA; }
    .alert-green { border-color: #34D399; }

    /* Intestazioni griglia Custom */
    .grid-header { font-size: 13px; font-weight: 600; color: #9CA3AF !important; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
    
    /* CSS Scheduling Assistant Adattivo */
    .scheduling-container { overflow-x: auto; padding-bottom: 15px; margin-top: 20px; }
    .scheduling-row { display: flex; align-items: center; margin-bottom: 4px; flex-wrap: nowrap; gap: 2px; }
    .scheduling-header { font-weight: 700; font-size: 11px; color: var(--kpi-text-sub); text-align: center; min-width: 35px; width: 35px; }
    .scheduling-name { min-width: 180px; max-width: 180px; font-weight: 600; font-size: 14px; position: sticky; left: 0; background-color: var(--background-color); z-index: 2; padding-right: 15px; color: var(--text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.3; }
    .scheduling-cell { min-width: 35px; width: 35px; height: 35px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: white; font-weight: 600; }

    /* CSS Card ERP uniformi */
    .erp-card {
        background: var(--kpi-bg);
        border: 1px solid var(--kpi-border);
        border-radius: 12px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: all 0.3s ease;
    }
    .erp-card:hover { transform: translateY(-5px); box-shadow: 0 12px 40px rgba(0,0,0,0.15); }

    /* Menu Neon */
    [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] label { padding: 10px 14px; margin-bottom: 2px; border-radius: 8px; transition: all 0.3s ease; cursor: pointer; }
    [data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 1.05rem; color: #D1D5DB !important; font-weight: 500; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background: rgba(96, 165, 250, 0.15) !important; box-shadow: inset 4px 0 0 #60A5FA !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { font-weight: 700 !important; color: #60A5FA !important; }
    
    /* Badge Notifiche Neon */
    [data-testid="stSidebar"] div[role="radiogroup"] label em {
        font-style: normal;
        background: rgba(255, 115, 0, 0.15);
        color: #FF7300;
        border-radius: 8px;
        padding: 2px 8px;
        font-size: 0.75rem;
        font-weight: 800;
        margin-left: 8px;
        box-shadow: 0 0 14px rgba(255, 115, 0, 0.6);
        border: 1px solid rgba(255, 115, 0, 0.5);
        display: inline-block;
        transform: translateY(-1px);
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FORMATTAZIONE ---
def formatta_valuta(valore):
    try:
        return f"€ {float(valore):,.0f}"
    except:
        return "€ 0"

def formatta_data(data_str):
    if not data_str:
        return ""
    try:
        if isinstance(data_str, str):
            return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d-%m-%Y")
        else:
            return data_str.strftime("%d-%m-%Y")
    except:
        return data_str

def get_badge(n):
    if n <= 0:
        return ""
    return f" *{n}*"

def applica_tema_plotly(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Outfit", color="#E5E7EB"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig.update_traces(hovertemplate="<b>%{label}</b><br>Valore: %{value}<br>Incidenza: %{percent}<extra></extra>")
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
        "Caterina Conte", "Francesco Ferri", "Marta Bianco",
        "Claudio Ferri", "Simona Riva", "Fabio Conte", "Chiara Rossi", "Massimo Neri", "Federica Galli",
        "Roberto Bruno", "Paolo Marini", "Giada Coppola", "Stefania De Rosa", "Alessio Greco", "Vittoria Giuliani",
        "Edoardo Lombardi", "Valeria Morelli", "Gianluca Ruggiero", "Erica Santoro", "Luigi Palumbo", 
        "Tiziana D'Amico", "Carmine Silvestri", "Ginevra Carbone"
    ]
    
    ruoli_skills = [
        ("Frontend Developer", ["React", "Vue", "TypeScript", "HTML/CSS", "Angular"], "IT"),
        ("Backend Developer", ["Node.js", "Python", "Java", "Go", "C#", "Spring Boot"], "IT"),
        ("Fullstack Developer", ["React", "Node.js", "Python", "TypeScript", "SQL", "Angular"], "IT"),
        ("DevOps Engineer", ["AWS", "Docker", "Kubernetes", "CI/CD", "Terraform"], "IT"),
        ("Data Scientist", ["Python", "Machine Learning", "SQL", "Pandas", "LangChain", "Pinecone"], "Data Science"),
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
            "ID": f"RES-{1000+i}",
            "Nome": nome,
            "Macro_Area": macro_area,
            "Ruolo": f"{seniority} {ruolo}",
            "Seniority": seniority,
            "Skill": ", ".join(skills),
            "Costo_Giorno": costo_base,
            "Tariffa_Vendita": costo_base * 1.4,
            "Disponibile_dal": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        })
    df_risorse = pd.DataFrame(db_risorse)

    df_commesse = pd.DataFrame([
        {"ID_Commessa": "PRJ-001", "Cliente": "Enel", "Nome": "Migrazione Cloud AWS", "Budget": 45000, "Stato": "Attivo"},
        {"ID_Commessa": "PRJ-002", "Cliente": "TIM", "Nome": "App Mobile React", "Budget": 38000, "Stato": "Attivo"},
        {"ID_Commessa": "PRJ-003", "Cliente": "Intesa", "Nome": "Dashboard IoT", "Budget": 60000, "Stato": "Attivo"},
        {"ID_Commessa": "PRJ-004", "Cliente": "Ferrari", "Nome": "Piattaforma E-commerce", "Budget": 20000, "Stato": "In Avvio"},
        {"ID_Commessa": "PRJ-005", "Cliente": "Poste", "Nome": "Ottimizzazione SQL", "Budget": 15000, "Stato": "Attivo"},
        {"ID_Commessa": "PRJ-006", "Cliente": "Bauli", "Nome": "Infrastruttura di Rete", "Budget": 25000, "Stato": "Attivo"}
    ])

    allocazioni = []
    timesheet = []
    
    for _, risorsa in df_risorse.iterrows():
        id_risorsa = risorsa['ID']
        num_commesse = random.choices([0, 1, 2, 3], weights=[0.25, 0.45, 0.20, 0.10])[0]
        
        if num_commesse > 0:
            commesse_assegnate = random.sample(df_commesse['ID_Commessa'].tolist(), k=num_commesse)
            for c_id in commesse_assegnate:
                perc = random.choice([30, 40, 50, 60, 100])
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
    if allocs.empty:
        return 0
    return allocs['Impegno_%'].sum()

def get_progetti_risorsa(id_risorsa, df_alloc, df_comm):
    allocs = df_alloc[df_alloc['ID_Risorsa'] == id_risorsa]
    if allocs.empty:
        return "Disponibile (Bench)"
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

if 'Data_Inizio' in st.session_state.df_timesheet.columns:
    st.session_state.df_timesheet.rename(columns={'Data_Inizio': 'Data_Inizio_Progetto'}, inplace=True)

if "pending_approvals" not in st.session_state:
    st.session_state.pending_approvals = []
if "pending_allocations" not in st.session_state:
    st.session_state.pending_allocations = []
if "pending_skills" not in st.session_state:
    st.session_state.pending_skills = []
if "team_cal_idx" not in st.session_state:
    st.session_state.team_cal_idx = 0
if "chat_msgs" not in st.session_state:
    st.session_state.chat_msgs = [{"role": "assistant", "content": "Smart Assistant inizializzato. Pronto a processare richieste (Es: 'Alloca Marco Rossi e Giulia Bianchi su Enel al 50%')"}]
if "bot_action" not in st.session_state:
    st.session_state.bot_action = None

# GESTIONE SICURA DELLA API KEY
if "groq_api_key" not in st.session_state:
    try:
        st.session_state.groq_api_key = st.secrets["GROQ_API_KEY"]
    except:
        st.session_state.groq_api_key = ""

if "pm_logged_in" not in st.session_state:
    st.session_state.pm_logged_in = False
if "it_logged_in" not in st.session_state:
    st.session_state.it_logged_in = False
if "hr_logged_in" not in st.session_state:
    st.session_state.hr_logged_in = False
if "current_it_user" not in st.session_state:
    st.session_state.current_it_user = None

# ASSEGNAZIONI GLOBALI
df_risorse = st.session_state.df_risorse
df_commesse = st.session_state.df_commesse
df_allocazioni = st.session_state.df_allocazioni
df_timesheet = st.session_state.df_timesheet

# ==========================================
# 2. MOTORI AI E COPILOT
# ==========================================
def analizza_testo_llm(testo, api_key):
    if not api_key:
        return [], [], "🔑 Nessuna API Key trovata nei Secrets."
    
    catalogo_skill = "React, Vue, TypeScript, HTML/CSS, Angular, Node.js, Python, Java, Go, C#, Spring Boot, SQL, AWS, Docker, Kubernetes, CI/CD, Terraform, Machine Learning, Pandas, LangChain, Pinecone, Excel, PowerBI, BPMN, Agile, Scrum, Jira"
    
    prompt = f"""
    Sei un'AI specializzata in IT Project Management.
    ANALIZZA il seguente testo. SE la richiesta NON riguarda lo sviluppo software o l'IT, restituisci:
    {{"errore": "Input non pertinente. Inserire un brief di progetto software valido."}}
    
    ALTRIMENTI, estrai le fasi del progetto e le competenze necessarie.
    REGOLA FONDAMENTALE: Per il campo "Skill", DEVI scegliere ESCLUSIVAMENTE uno dei valori esatti da questo catalogo:
    [{catalogo_skill}]. Non inventare nomi.
    
    Restituisci SOLO ED ESCLUSIVAMENTE un JSON valido:
    {{
        "fasi": [
            {{"Fase": "Descrizione", "Skill": "TecnologiaEsattaDalCatalogo", "Giorni": 20}}
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
            return [], [], f"Errore API Groq ({response.status_code})."
            
        txt = response.json()["choices"][0]["message"]["content"]
        match = re.search(r'\{.*\}', txt, re.DOTALL)
        if match:
            txt = match.group(0)
            
        dati = json.loads(txt)
        if "errore" in dati:
            return [], [], dati["errore"]
            
        return dati.get("fasi", []), dati.get("competenze", []), None
    except Exception as e:
        return [], [], f"Errore di parsing AI: Riprova."

def parse_chatbot_intent_llm(prompt, df, api_key):
    if not api_key:
        return None, "🔑 L'Intelligenza Artificiale è disattivata."
        
    lista_nomi = ", ".join(df['Nome'].tolist())
    system_prompt = f"""Sei uno Smart Assistant. Rispondi SOLO in formato JSON. 
    L'utente potrebbe richiedere azioni su PIÙ RISORSE. Estrai TUTTI i nomi richiesti.
    Database Nomi (Usa solo i nomi che matchano da qui): {lista_nomi}
    
    1. ALLOCARE: {{"azione": "alloca", "nomi": ["Nome Cognome 1", "Nome Cognome 2"], "percentuale": 50, "cliente": "ID_Commessa", "messaggio_riepilogo": "Allocazione..."}}
    2. PROMUOVERE: {{"azione": "promuovi", "nomi": ["Nome Cognome 1"], "nuova_seniority": "Senior", "messaggio_riepilogo": "Upgrade..."}}
    3. ALTRO: {{"azione": "errore", "messaggio_riepilogo": "Comando non riconosciuto."}}"""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "temperature": 0.1}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return None, f"Errore API Groq ({response.status_code}). Verifica validità."

        txt = response.json()["choices"][0]["message"]["content"]
        match = re.search(r'\{.*\}', txt, re.DOTALL)
        if match:
            txt = match.group(0)
            
        dati = json.loads(txt)
        if dati.get("azione") == "errore":
            return None, dati.get("messaggio_riepilogo")
            
        perc_val = 100
        try:
            perc_val = int(dati.get("percentuale", 100))
        except:
            pass

        if dati.get("azione") == "alloca":
            return {"type": "alloca", "nomi": dati.get("nomi", []), "perc": perc_val, "cliente": dati.get("cliente", "N/D"), "desc": dati.get("messaggio_riepilogo")}, None
        if dati.get("azione") == "promuovi":
            return {"type": "promuovi", "nomi": dati.get("nomi", []), "nuova_sen": dati.get("nuova_seniority"), "desc": dati.get("messaggio_riepilogo")}, None
            
        return None, "Errore Parser LLM."
    except Exception as e:
        return None, f"Errore AI interno. Riprova."

def esegui_azione_chatbot(dati_finali):
    nomi = dati_finali.get('nomi', [])
    if not nomi and dati_finali.get('nome'):
        nomi = [dati_finali['nome']]
        
    eseguiti = []
    for nome in nomi:
        df_ris = st.session_state.df_risorse
        idx_ris = df_ris[df_ris['Nome'] == nome.strip()].index
        if len(idx_ris) == 0:
            continue
            
        id_risorsa = df_ris.iloc[idx_ris[0]]['ID']
        if dati_finali['type'] == 'alloca':
            nuova = pd.DataFrame([{"ID_Risorsa": id_risorsa, "ID_Commessa": dati_finali['cliente'], "Impegno_%": dati_finali['perc']}])
            st.session_state.df_allocazioni = pd.concat([st.session_state.df_allocazioni, nuova], ignore_index=True)
            eseguiti.append(nome)
        elif dati_finali['type'] == 'promuovi':
            rp = df_ris.at[idx_ris[0], 'Ruolo'].replace('Senior ', '').replace('Mid ', '').replace('Junior ', '')
            st.session_state.df_risorse.at[idx_ris[0], 'Seniority'] = dati_finali['nuova_sen']
            st.session_state.df_risorse.at[idx_ris[0], 'Ruolo'] = f"{dati_finali['nuova_sen']} {rp}"
            eseguiti.append(nome)
            
    if eseguiti:
        if dati_finali['type'] == 'alloca':
            msg = f"Task Eseguito: **{', '.join(eseguiti)}** agganciati a **{dati_finali['cliente']}** ({dati_finali['perc']}%)."
        else:
            msg = f"Task Eseguito: **{', '.join(eseguiti)}** promossi a **{dati_finali['nuova_sen']}**."
        st.session_state.chat_msgs.append({"role": "assistant", "content": msg})
    else:
        st.session_state.chat_msgs.append({"role": "assistant", "content": "Nessuna risorsa trovata per l'azione richiesta."})
        
    st.session_state.bot_action = None


# ==========================================
# 3. SIDEBAR E NAVIGAZIONE
# ==========================================
st.sidebar.markdown("<div style='font-size: 26px; font-weight: 800; letter-spacing: -1px; color: #3B82F6; margin-bottom: 30px; margin-top: -20px;'>ResourceAI</div>", unsafe_allow_html=True)
ruolo_utente = st.sidebar.selectbox("PROFILO DI ACCESSO", ["Resource Allocation Engine", "Talent Management", "Talent Workspace"])
st.sidebar.markdown("<br>", unsafe_allow_html=True)

if ruolo_utente != "Resource Allocation Engine":
    st.session_state.pm_logged_in = False
if ruolo_utente != "Talent Workspace":
    st.session_state.it_logged_in = False
    st.session_state.current_it_user = None
if ruolo_utente != "Talent Management":
    st.session_state.hr_logged_in = False

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
                    st.session_state.pm_logged_in = True
                    st.rerun()
                else: 
                    st.error("Credenziali non conformi.")
    else:
        # Pre-calcolo Allarmi per Notifiche Globale
        sat_df = df_allocazioni.groupby('ID_Risorsa')['Impegno_%'].sum().reset_index() if not df_allocazioni.empty else pd.DataFrame()
        overbooked = sat_df[sat_df['Impegno_%'] > 100] if not sat_df.empty else pd.DataFrame()
        
        commesse_loss = []
        if not df_timesheet.empty:
            ts_cost = pd.merge(df_timesheet, df_risorse[['ID', 'Costo_Giorno']], left_on='ID_Risorsa', right_on='ID')
            ts_cost['Costo_Tot_Riga'] = ts_cost['Giornate_Spese'] * ts_cost['Costo_Giorno']
            costo_aggregato = ts_cost.groupby('ID_Commessa')['Costo_Tot_Riga'].sum().reset_index()
            analisi_budget = pd.merge(df_commesse, costo_aggregato, on='ID_Commessa', how='left').fillna(0)
            commesse_loss = analisi_budget[analisi_budget['Costo_Tot_Riga'] > analisi_budget['Budget']]

        num_alert = len(overbooked) + len(commesse_loss) + len(st.session_state.pending_allocations) + len(st.session_state.pending_skills)
        
        # Struttura Gerarchica Sidebar
        nav_tree = {
            "Homepage": [],
            "Project and Resources Management": ["Notification and Alert", "Project Hub", "Resource Allocation"],
            "Staffing Intelligence": ["Allocation Advisor", "Build your Team", "Profile Explorer"],
            "Data Hub": ["Project Portfolio", "Resource Master Data"]
        }
        
        if 'active_macro' not in st.session_state:
            st.session_state.active_macro = "Homepage"
        if 'active_sub' not in st.session_state:
            st.session_state.active_sub = None

        mapping = {}
        for macro, subs in nav_tree.items():
            mostra_badge_macro = (macro == "Project and Resources Management" and st.session_state.active_macro != "Project and Resources Management")
            
            d_macro = macro + (get_badge(num_alert) if mostra_badge_macro else "")
            mapping[d_macro] = (macro, None)
            
            if st.session_state.active_macro == macro:
                for sub in subs:
                    d_sub = f"  {sub}" + (get_badge(num_alert) if sub=="Notification and Alert" else "")
                    mapping[d_sub] = (macro, sub)

        def_key = st.session_state.active_macro + (get_badge(num_alert) if st.session_state.active_macro != "Project and Resources Management" and st.session_state.active_macro == "Project and Resources Management" else "")
        if st.session_state.active_sub:
            for k, (mac, sub) in mapping.items():
                if sub == st.session_state.active_sub:
                    def_key = k

        try:
            default_idx = list(mapping.keys()).index(def_key)
        except ValueError:
            default_idx = 0

        selected_display = st.sidebar.radio("Struttura Navigazione", list(mapping.keys()), index=default_idx, label_visibility="collapsed")
        selected_macro, selected_sub = mapping[selected_display]

        if selected_macro != st.session_state.active_macro:
            st.session_state.active_macro = selected_macro
            st.session_state.active_sub = nav_tree[selected_macro][0] if nav_tree[selected_macro] else None
            st.rerun()
        elif selected_sub != st.session_state.active_sub and selected_sub is not None:
            st.session_state.active_sub = selected_sub
            
        pagina_pm = st.session_state.active_sub if st.session_state.active_sub else st.session_state.active_macro
            
        if st.sidebar.button("Logout", key="logout_pm"):
            st.session_state.pm_logged_in = False
            st.rerun()

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
            c1.markdown(f"<div class='kpi-card blue'><h3>Risorse Disponibili</h3><h2>{tot_risorse}</h2></div>", unsafe_allow_html=True)
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
            
            st.markdown("<p style='font-size:13px; color:var(--kpi-text-sub); text-align:center;'>ℹ️ <b>Revenue Prodotta</b>: Valore quotidiano generato dalle risorse allocate al momento. <b>Perdita (Bench)</b>: Costo opportunità / fatturato perso per le risorse a disposizione nel database che non sono staffate.</p>", unsafe_allow_html=True)

        elif pagina_pm == "Notification and Alert":
            st.markdown("<h1 class='gradient-title'>Notification and Alert</h1>", unsafe_allow_html=True)
            
            if num_alert == 0:
                st.success("Nessun conflitto logico rilevato. Parametri operativi entro i limiti di sistema.")
            else:
                if not overbooked.empty:
                    with st.expander(f"🔴 Allarmi di Overbooking Critico ({len(overbooked)})"):
                        for _, r in overbooked.iterrows():
                            match = df_risorse[df_risorse['ID'] == r['ID_Risorsa']]
                            nome_ris = match['Nome'].values[0] if not match.empty else r['ID_Risorsa']
                            st.markdown(f"<div class='alert-box alert-red'>Il record <b>{nome_ris}</b> ({r['ID_Risorsa']}) è allocato oltre il limite ({r['Impegno_%']}%). Richiesto intervento in Resource Allocation.</div>", unsafe_allow_html=True)
                
                if len(commesse_loss) > 0:
                    with st.expander(f"🟠 Allarmi Erosione Margine ({len(commesse_loss)})"):
                        for _, c in commesse_loss.iterrows():
                            st.markdown(f"<div class='alert-box alert-orange'>La commessa <b>{c['ID_Commessa']}</b> ha superato il budget stimato.<br>Costo Consuntivato: <b>{formatta_valuta(c['Costo_Tot_Riga'])}</b> | Budget Originale: <b>{formatta_valuta(c['Budget'])}</b>.</div>", unsafe_allow_html=True)
                
                if len(st.session_state.pending_allocations) > 0:
                    with st.expander(f"🔵 Richieste in Sospeso (Workspace) ({len(st.session_state.pending_allocations)})"):
                        for req in st.session_state.pending_allocations:
                            st.markdown(f"<div class='alert-box alert-blue'>L'utente <b>{req['Nome']}</b> ha richiesto l'allocazione al {req['Occupazione']}% sul progetto {req['Progetto']}. (Autorizzabile in Resource Allocation).</div>", unsafe_allow_html=True)

                if len(st.session_state.pending_skills) > 0:
                    with st.expander(f"🟢 Richieste Integrazione Skill ({len(st.session_state.pending_skills)})"):
                        for i, s in enumerate(list(st.session_state.pending_skills)):
                            st.markdown(f"<div class='alert-box alert-green'>La risorsa <b>{s['Risorsa']}</b> richiede l'aggiunta in anagrafica della competenza tecnica: <b>{s['Skill']}</b>. (Approva/Rifiuta da Resource Allocation).</div>", unsafe_allow_html=True)

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
            edited_comm = st.data_editor(
                st.session_state.df_commesse, 
                use_container_width=True, 
                num_rows="dynamic", 
                column_config={"Budget": st.column_config.NumberColumn("Budget", format="€ %,d")}
            )
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
                        if b1.button("Approva Richiesta", key=f"ok_{i}"):
                            id_ris = df_risorse[df_risorse['Nome'] == req['Nome']]['ID'].values[0]
                            nuova = pd.DataFrame([{"ID_Risorsa": id_ris, "ID_Commessa": req['Progetto'], "Impegno_%": req['Occupazione']}])
                            st.session_state.df_allocazioni = pd.concat([st.session_state.df_allocazioni, nuova], ignore_index=True)
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
                        if b2.button("Rifiuta Richiesta", key=f"ko_{i}"):
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
            else:
                st.caption("Nessuna coda attiva.")
            
            st.subheader("Richieste Integrazione Skill (Da Validare)")
            if len(st.session_state.pending_skills) > 0:
                for i, s in enumerate(list(st.session_state.pending_skills)):
                    with st.container(border=True):
                        st.write(f"**{s['Risorsa']}** richiede l'aggiunta di: **{s['Skill']}**")
                        b1, b2 = st.columns(2)
                        if b1.button("Approva Competenza", key=f"app_skill_{i}"):
                            idx_ris = df_risorse.index[df_risorse['Nome'] == s['Risorsa']].tolist()[0]
                            old_skills = st.session_state.df_risorse.at[idx_ris, 'Skill']
                            st.session_state.df_risorse.at[idx_ris, 'Skill'] = f"{old_skills}, {s['Skill']}"
                            st.session_state.pending_skills.pop(i)
                            st.rerun()
                        if b2.button("Rifiuta Richiesta", key=f"rej_skill_{i}"):
                            st.session_state.pending_skills.pop(i)
                            st.rerun()
            else:
                st.caption("Nessuna skill da approvare.")
            
            st.divider()
            
            col_l, col_r = st.columns(2)
            with col_l:
                st.subheader("Modulo di Override")
                with st.form("manual_alloc"):
                    r_scelta = st.selectbox("Seleziona Consulente:", df_risorse['Nome'].tolist())
                    commesse_disp = df_commesse['ID_Commessa'] + " - " + df_commesse['Cliente']
                    c_scelta = st.selectbox("Seleziona Progetto/Commessa:", commesse_disp.tolist())
                    perc = st.slider("Assegnazione Impegno (%)", 0, 100, 100, 25)
                    dt_req = st.date_input("Durata progetto", value=(datetime.today(), datetime.today()+timedelta(days=30)))
                    
                    if st.form_submit_button("Esegui Forzatura / Assegna") and len(dt_req)==2:
                        id_risorsa = df_risorse[df_risorse['Nome'] == r_scelta]['ID'].values[0]
                        id_commessa = c_scelta.split(" - ")[0]
                        nuova_alloc = pd.DataFrame([{"ID_Risorsa": id_risorsa, "ID_Commessa": id_commessa, "Impegno_%": perc}])
                        st.session_state.df_allocazioni = pd.concat([st.session_state.df_allocazioni, nuova_alloc], ignore_index=True)
                        st.rerun()

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
                            st.session_state.df_allocazioni = st.session_state.df_allocazioni.drop(index=real_idx)
                            st.rerun()
                else:
                    st.caption("Il database allocazioni è vuoto.")

        elif pagina_pm == "Allocation Advisor":
            st.markdown("<h1 class='gradient-title'>Allocation Advisor</h1>", unsafe_allow_html=True)
            
            st.markdown("<p style='font-size:14px; color:var(--kpi-text-sub);'>💡 L'integrazione nativa di formati come PDF o Word è un'estensione banale (richiede l'installazione in ambiente di librerie come PyPDF2). Per comodità ambientale, è abilitato l'upload immediato da file di testo (<b>.txt</b>).</p>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Importa Brief di Progetto (.txt)", type=['txt'])
            
            prompt_random = [
                "Sviluppo di un sistema ERP Cloud-native per la logistica aziendale. Il frontend deve essere realizzato interamente in React utilizzando TypeScript. Il backend richiede una solida architettura a microservizi sviluppata in Go e Node.js. È fondamentale l'implementazione di pipeline CI/CD con GitHub Actions, containerizzazione tramite Docker e orchestrazione Kubernetes su AWS. Necessario anche un esperto per l'ottimizzazione del database PostgreSQL e l'analisi predittiva (Python/Pandas).",
                "Rifacimento completo del portale di Home Banking e transazioni sicure. La sicurezza è la priorità: richiesto framework Angular per la web app responsive e Java (Spring Boot) per i processi core di transazione. Il team deve includere DevOps Engineer per la gestione dell'infrastruttura Terraform su cloud AWS, oltre a Data Analyst qualificati per la reportistica direzionale tramite SQL e PowerBI.",
                "Creazione di una piattaforma IoT Edge per il monitoraggio in tempo reale di macchinari industriali. I dati provenienti dai sensori verranno raccolti tramite script Python e processati con algoritmi avanzati di Machine Learning (Scikit-learn). La dashboard di controllo per gli operatori sarà sviluppata in Vue.js. L'infrastruttura backend poggerà completamente su servizi cloud AWS serverless (Lambda e DynamoDB)."
            ]
            
            if "saved_testo_brief" not in st.session_state:
                st.session_state.saved_testo_brief = ""
            
            if uploaded_file is not None:
                stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
                st.session_state.saved_testo_brief = stringio.read()
            elif st.button("Generazione automatica di prompt per fase Test"):
                st.session_state.saved_testo_brief = random.choice(prompt_random)
                
            testo = st.text_area("Input Requirement (Descrizione del progetto):", value=st.session_state.saved_testo_brief, height=140)
            st.session_state.saved_testo_brief = testo

            if st.button("Simula Scenario e Trova Copertura", type="primary"):
                fasi, skill_richieste, err_msg = analizza_testo_llm(testo, st.session_state.groq_api_key)
                
                if err_msg:
                    st.error(err_msg)
                elif not fasi:
                    st.warning("Non è stato possibile mappare i requisiti. Riprova con descrizioni più chiare.")
                else:
                    # FIX: Assicura che TUTTE le skill trovate abbiano una fase nella WBS, così non ci sono righe non calcolabili
                    fasi_skills = [str(f.get("Skill", "")).strip().lower() for f in fasi]
                    for s in skill_richieste:
                        if str(s).strip().lower() not in fasi_skills:
                            fasi.append({"Fase": f"Task e Supporto {s}", "Skill": s, "Giorni": 10})
                            
                    st.session_state.wbs_data = pd.DataFrame(fasi)
                    
                    team = []
                    for skill in skill_richieste:
                        risorsa_trovata = False
                        clean_skill_req = skill.lower().replace("(", "").replace(")", "")
                        
                        for _, r in df_risorse.iterrows():
                            if get_saturazione(r['ID'], df_allocazioni) < 100:
                                db_skills = r['Skill'].lower()
                                is_match = clean_skill_req in db_skills
                                
                                if not is_match:
                                    for word in clean_skill_req.split():
                                        if len(word) > 2 and word in db_skills:
                                            is_match = True
                                            break
                                            
                                if is_match:
                                    team.append({"Skill": skill, "Nome": r['Nome'], "Costo (€)": r['Costo_Giorno'], "Margine (%)": 30})
                                    risorsa_trovata = True
                                    break
                                    
                        if not risorsa_trovata:
                            team.append({"Skill": skill, "Nome": "ASSUNZIONE NECESSARIA", "Costo (€)": 300, "Margine (%)": 30})
                            
                    st.session_state.team_data = pd.DataFrame(team)

            if "wbs_data" in st.session_state and not st.session_state.wbs_data.empty:
                tab_wbs, tab_team = st.tabs(["Work Breakdown Structure (WBS)", "Assessment Economico Team"])
                
                # ==== FIX ULTIMO: TABELLE CUSTOM CON FRECCETTE (SPINNERS VISIBILI) E LIVE CALC ====
                with tab_wbs:
                    st.markdown("<div class='grid-header' style='display:flex;'><div style='flex:4'>Fase Progettuale</div><div style='flex:4'>Tecnologia</div><div style='flex:2'>Giorni (Effort)</div></div>", unsafe_allow_html=True)
                    new_wbs = []
                    
                    for idx, row in st.session_state.wbs_data.iterrows():
                        c1, c2, c3 = st.columns([4, 4, 2])
                        c1.markdown(f"<div style='padding-top:10px; font-weight:600; color:#E5E7EB;'>{row.get('Fase', '')}</div>", unsafe_allow_html=True)
                        c2.markdown(f"<div style='padding-top:10px; color:#D1D5DB;'>{row.get('Skill', '')}</div>", unsafe_allow_html=True)
                        
                        # QUI SI VEDONO LE FRECCETTE PERCHÉ È UN VERO NUMBER_INPUT
                        giorni = c3.number_input("giorni", min_value=1, step=1, value=int(row.get('Giorni', 10)), key=f"wbs_g_{idx}", label_visibility="collapsed")
                        new_wbs.append({"Fase": row.get('Fase'), "Skill": row.get('Skill'), "Giorni": giorni})
                        
                    st.session_state.wbs_data = pd.DataFrame(new_wbs)

                with tab_team:
                    st.markdown("<div class='grid-header' style='display:flex;'><div style='flex:3'>Skill/Tecnologia</div><div style='flex:3'>Risorsa Assegnata</div><div style='flex:2'>Costo (€)</div><div style='flex:2'>Margine (%)</div></div>", unsafe_allow_html=True)
                    new_team = []
                    
                    for idx, row in st.session_state.team_data.iterrows():
                        c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
                        c1.markdown(f"<div style='padding-top:10px; font-weight:600; color:#E5E7EB;'>{row.get('Skill', '')}</div>", unsafe_allow_html=True)
                        c2.markdown(f"<div style='padding-top:10px; color:#D1D5DB;'>{row.get('Nome', '')}</div>", unsafe_allow_html=True)
                        
                        # QUI SI VEDONO LE FRECCETTE PER I COSTI E MARGINI
                        costo = c3.number_input("costo", min_value=0, step=10, value=int(row.get('Costo (€)', 150)), key=f"team_c_{idx}", label_visibility="collapsed")
                        margine = c4.number_input("margine", min_value=0, max_value=100, step=1, value=int(row.get('Margine (%)', 30)), key=f"team_m_{idx}", label_visibility="collapsed")
                        
                        new_team.append({"Skill": row.get('Skill'), "Nome": row.get('Nome'), "Costo (€)": costo, "Margine (%)": margine})
                        
                    st.session_state.team_data = pd.DataFrame(new_team)
                    
                    # Ricalcolo Totali in tempo reale basato sugli input visibili
                    costo_tot = 0.0
                    prop_comm = 0.0
                    
                    for t_row in new_team:
                        t_skill = str(t_row['Skill']).strip().lower()
                        # Trova i giorni correlati nella WBS per la riga in calcolo
                        giorni_totali = sum(w['Giorni'] for w in new_wbs if str(w['Skill']).strip().lower() == t_skill)
                        
                        c_parz = giorni_totali * t_row['Costo (€)']
                        costo_tot += c_parz
                        prop_comm += c_parz * (1 + (t_row['Margine (%)'] / 100.0))
                    
                    st.markdown("<br><div style='font-size: 1.6rem; font-weight: 700; color: #F9FAFB; margin-bottom: 15px;'>Previsione Finanziaria di Commessa</div>", unsafe_allow_html=True)
                    
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
            
            if t_sel:
                oggi = datetime.today()
                mese_offset = st.session_state.get('team_cal_idx', 0)
                
                anno_c = oggi.year
                mese_c = oggi.month + mese_offset
                
                while mese_c > 12:
                    mese_c -= 12
                    anno_c += 1
                while mese_c < 1:
                    mese_c += 12
                    anno_c -= 1

                mesi_ita = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
                
                c_p, c_m, c_n = st.columns([1,2,1])
                if c_p.button("⬅️ Retrocedi Mese"):
                    st.session_state.team_cal_idx -= 1
                    st.rerun()
                if c_n.button("Avanza Mese ➡️"):
                    st.session_state.team_cal_idx += 1
                    st.rerun()
                    
                c_m.markdown(f"<h3 style='text-align:center; color:#60A5FA;'>{mesi_ita[mese_c]} {anno_c}</h3>", unsafe_allow_html=True)
                
                cal = calendar.Calendar(firstweekday=0)
                giorni_del_mese = [d for d in cal.itermonthdates(anno_c, mese_c) if d.month == mese_c]
                
                tab_mensile, tab_giornaliera = st.tabs(["Vista Mensile", "Vista Giornaliera"])

                with tab_mensile:
                    for i in range(0, len(t_sel), 3):
                        cols = st.columns(3)
                        for j, nome in enumerate(t_sel[i:i+3]):
                            with cols[j]:
                                r_id = df_risorse[df_risorse['Nome'] == nome]['ID'].values[0]
                                sat = get_saturazione(r_id, df_allocazioni)
                                prog_att = get_progetti_risorsa(r_id, df_allocazioni, df_commesse)
                                
                                st.markdown(f"<h5 style='text-align:center; color:#E5E7EB; margin-bottom:0px;'>{nome}</h5>", unsafe_allow_html=True)
                                st.markdown(f"<p style='text-align:center; font-size:12px; color:var(--kpi-text-sub); margin-top:2px; margin-bottom:10px;'>{prog_att}</p>", unsafe_allow_html=True)
                                
                                html_cal = "<div style='display:grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 30px;'>"
                                for g in ["Lu","Ma","Me","Gi","Ve","Sa","Do"]:
                                    html_cal += f"<div style='text-align:center; font-size:10px; color:#E5E7EB;'>{g}</div>"
                                    
                                for week in cal.monthdatescalendar(anno_c, mese_c):
                                    for day in week:
                                        if day.month != mese_c:
                                            html_cal += "<div></div>"
                                        else:
                                            bg = "#374151" if day.weekday() >= 5 else ("#F87171" if sat == 0 else ("#FBBF24" if sat < 100 else "#34D399"))
                                            html_cal += f"<div style='background-color:{bg}; height:32px; border-radius:4px; display:flex; align-items:center; justify-content:center; font-size:12px; color:#FFF; font-weight:bold;'>{day.day}</div>"
                                            
                                html_cal += "</div>"
                                st.markdown(html_cal, unsafe_allow_html=True)

                with tab_giornaliera:
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
                            bg = "#374151" if d.weekday() >= 5 else ("#F87171" if sat == 0 else ("#FBBF24" if sat < 100 else "#34D399"))
                            html_grid += f"<div class='scheduling-cell' style='background:{bg}; color: transparent;'>.</div>"
                            
                        html_grid += "</div>"
                        
                    html_grid += "</div></div>"
                    st.markdown(html_grid, unsafe_allow_html=True)

        elif pagina_pm == "Project Portfolio":
            st.markdown("<h1 class='gradient-title'>Project Portfolio</h1>", unsafe_allow_html=True)
            
            if not df_timesheet.empty:
                ts_merged = pd.merge(df_timesheet, df_risorse[['ID', 'Costo_Giorno']], left_on='ID_Risorsa', right_on='ID')
                ts_merged['Costo_Riga'] = ts_merged['Giornate_Spese'] * ts_merged['Costo_Giorno']
                agg_costi = ts_merged.groupby('ID_Commessa')['Costo_Riga'].sum().reset_index()
                
                df_view = pd.merge(df_commesse, agg_costi, on='ID_Commessa', how='left').fillna(0)
                df_view.rename(columns={'Costo_Riga': 'Costo_Attuale'}, inplace=True)
            else:
                df_view = df_commesse.copy()
                df_view['Costo_Attuale'] = 0

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
                c2.markdown(f"<div class='kpi-card orange'><h3>Competenze Core</h3><p style='font-size:18px; color:#E5E7EB; font-weight:700;'>{dati['Skill']}</p></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='kpi-card green'><h3>Saturazione Lavorativa</h3><p style='font-size:22px; font-weight:700; color:#E5E7EB;'>{sat}%</p></div>", unsafe_allow_html=True)

                st.markdown("---")
                col_left, col_right = st.columns(2)
                
                with col_left:
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
                                if c_c.button("Revoca", key=f"rev_{i}"):
                                    st.session_state.df_allocazioni = st.session_state.df_allocazioni.drop(i)
                                    st.rerun()
                    else:
                        st.info("La risorsa non è associata ad alcun cliente (Bench).")
                
                with col_right:
                    st.subheader("Storico Progetti (Completati)")
                    html_storico = "<div style='padding:15px; border-radius:8px; border:1px solid rgba(255,255,255,0.1); color:#E5E7EB;'>"
                    
                    if dati['Seniority'] == "Junior":
                        html_storico += "🔹 <b>Progetto Formativo Cloud</b> (100%) - <i>Durata: 3 Mesi</i><br>🔹 <b>Assistenza Frontend E-Commerce</b> (50%) - <i>Durata: 2 Mesi</i>"
                    elif dati['Seniority'] == "Mid":
                        html_storico += "🔹 <b>Migrazione CRM Fastweb</b> (100%) - <i>Durata: 8 Mesi</i><br>🔹 <b>Sviluppo Portale API</b> (100%) - <i>Durata: 5 Mesi</i><br>🔹 <b>Bug Fixing App Mobile</b> (30%) - <i>Durata: 6 Mesi</i>"
                    else:
                        html_storico += "🔹 <b>Architettura Cloud BPER</b> (100%) - <i>Durata: 12 Mesi</i><br>🔹 <b>Tech Lead Progetto IoT</b> (50%) - <i>Durata: 9 Mesi</i><br>🔹 <b>Rifacimento Core Banking</b> (80%) - <i>Durata: 18 Mesi</i>"
                        
                    html_storico += "</div>"
                    st.markdown(html_storico, unsafe_allow_html=True)

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
                    st.session_state.it_logged_in = True
                    st.session_state.current_it_user = utente_selezionato
                    st.rerun()
                else:
                    st.error("Accesso Negato.")
    else:
        st.markdown(f"<h1 class='gradient-title'>Dashboard Personale: {st.session_state.current_it_user}</h1>", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.it_logged_in = False
            st.rerun()
            
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
                    st.session_state.pending_skills.append({"Risorsa": st.session_state.current_it_user, "Skill": ns})
                    st.success("Iter di Validazione Avviato e inviato al Management.")
                    
            with c2:
                st.markdown("<div class='kpi-card kpi-card-shadow orange'><h3>Richiesta Cambio Progetto</h3>", unsafe_allow_html=True)
                with st.form("req"):
                    p_req = st.text_input("Inserisci ID o Nome Progetto Target")
                    d_req = st.slider("Disponibilità (FTE %)", 25, 100, 50, 25)
                    dt_req = st.date_input("Durata progetto", value=(datetime.today(), datetime.today()+timedelta(days=30)))
                    
                    if st.form_submit_button("Invia Richiesta") and len(dt_req)==2:
                        st.session_state.pending_allocations.append({"ID": id_c, "Nome": dati_utente['Nome'], "Progetto": p_req, "Occupazione": d_req, "Dal": dt_req[0], "Al": dt_req[1]})
                        st.success("Notifica inserita in coda nel Resource Allocation Engine.")
                st.markdown("</div>", unsafe_allow_html=True)
                
        with tab_ts:
            st.subheader("Registrazione Attività Mensile")
            mie_comm = df_allocazioni[df_allocazioni['ID_Risorsa'] == id_c]
            
            if mie_comm.empty:
                st.warning("Il tuo profilo risulta a Bench. Nessuna commessa attiva da consuntivare.")
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
                col_d = 'Data_Inizio_Progetto' if 'Data_Inizio_Progetto' in mio_ts.columns else 'Data_Inizio'
                mio_ts[col_d] = mio_ts[col_d].apply(formatta_data)
                st.dataframe(mio_ts[['ID_Commessa', col_d, 'Giornate_Spese']], use_container_width=True, hide_index=True)
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
                    st.session_state.hr_logged_in = True
                    st.rerun()
                else: 
                    st.error("Credenziali Errate. Usare hr / hr123")
    else:
        hr_nav_tree = {
            "Homepage": [],
            "Talent Lifecycle": ["Talent Onboarding", "Career Development"],
            "HR Operations": ["ERP Integration"],
            "Data Hub": ["Data Repository"]
        }
        
        if 'hr_active_macro' not in st.session_state:
            st.session_state.hr_active_macro = "Homepage"
        if 'hr_active_sub' not in st.session_state:
            st.session_state.hr_active_sub = None

        hr_mapping = {}
        for macro, subs in hr_nav_tree.items():
            hr_mapping[macro] = (macro, None)
            if st.session_state.hr_active_macro == macro:
                for sub in subs:
                    hr_mapping[f"  {sub}"] = (macro, sub)

        def_key_hr = st.session_state.hr_active_macro
        if st.session_state.hr_active_sub:
            for k, (mac, sub) in hr_mapping.items():
                if sub == st.session_state.hr_active_sub:
                    def_key_hr = k

        try:
            default_idx_hr = list(hr_mapping.keys()).index(def_key_hr)
        except ValueError:
            default_idx_hr = 0

        selected_display = st.sidebar.radio("Struttura Navigazione", list(hr_mapping.keys()), index=default_idx_hr, label_visibility="collapsed")
        selected_macro, selected_sub = hr_mapping[selected_display]

        if selected_macro != st.session_state.hr_active_macro:
            st.session_state.hr_active_macro = selected_macro
            st.session_state.hr_active_sub = hr_nav_tree[selected_macro][0] if hr_nav_tree[selected_macro] else None
            st.rerun()
        elif selected_sub != st.session_state.hr_active_sub and selected_sub is not None:
            st.session_state.hr_active_sub = selected_sub
            
        pagina_hr = st.session_state.hr_active_sub if st.session_state.hr_active_sub else st.session_state.hr_active_macro
        
        if st.sidebar.button("Logout", key="logout_hr"):
            st.session_state.hr_logged_in = False
            st.rerun()

        if pagina_hr == "Homepage":
            st.markdown("<h1 class='gradient-title'>Talent Management Metrics</h1>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='kpi-card blue'><h3>Risorse Disponibili</h3><h2>{len(df_risorse)}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='kpi-card orange'><h3>Indice Età Teorico</h3><h2>32 Anni</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='kpi-card green'><h3>Costo Base Ponderato</h3><h2>{formatta_valuta(df_risorse['Costo_Giorno'].mean())}</h2></div>", unsafe_allow_html=True)

            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Rapporto Gerarchico")
                df_sen = df_risorse['Seniority'].value_counts().reset_index()
                df_sen.columns = ['Seniority', 'Conteggio']
                
                fig1 = px.pie(df_sen, values='Conteggio', names='Seniority', hole=0.4, color_discrete_sequence=["#60A5FA", "#34D399", "#FBBF24"])
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
                
                fig2 = px.bar(df_ruoli, x='Ruolo', y='Conteggio', color='Ruolo', color_discrete_sequence=["#60A5FA", "#34D399", "#FBBF24", "#F87171"])
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
            n_sel_list = st.multiselect("Seleziona Collaboratori dal Master Data (Selezione Multipla):", df_risorse['Nome'].tolist())
            
            if n_sel_list:
                idx_0 = df_risorse.index[df_risorse['Nome']==n_sel_list[0]].tolist()[0]
                dati_0 = df_risorse.iloc[idx_0]
                
                with st.form("mod"):
                    st.write(f"Gestione Upgrade Massivo per: **{', '.join(n_sel_list)}**")
                    c1, c2 = st.columns(2)
                    sen = c1.selectbox("Nuovo Livello per tutti", ["Junior", "Mid", "Senior"], index=["Junior", "Mid", "Senior"].index(dati_0['Seniority']))
                    costo_gg = c2.number_input("Nuovo Costo Giornaliero (€) per tutti", value=int(dati_0['Costo_Giorno']), step=10)
                    
                    if st.form_submit_button("Esegui Manutenzione Parametri"):
                        for n_sel in n_sel_list:
                            idx = df_risorse.index[df_risorse['Nome']==n_sel].tolist()[0]
                            st.session_state.df_risorse.at[idx, 'Seniority'] = sen
                            st.session_state.df_risorse.at[idx, 'Costo_Giorno'] = costo_gg
                        st.success("Dati aggiornati correttamente nell'ERP Centrale.")
                        st.rerun()

        elif pagina_hr == "ERP Integration":
            st.markdown("<h1 class='gradient-title'>ERP Integration (Paghe/Fatturazione)</h1>", unsafe_allow_html=True)
            st.write("Modulo di raccordo per allineare l'infrastruttura Cloud con i sistemi aziendali legacy (Zucchetti, SAP, ecc.).")
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("""
                <div class='erp-card'>
                    <h3 style='color:#60A5FA; margin-bottom:5px;'>Export Flussi Paghe</h3>
                    <p style='color:var(--kpi-text-sub); font-size:14px; margin-bottom:20px;'>Genera tracciato in formato CSV massivo</p>
                """, unsafe_allow_html=True)
                st.download_button("Scarica Export CSV", data=df_risorse.to_csv(index=False).encode('utf-8'), file_name='export_hr_erp.csv', use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            with c2:
                st.markdown("""
                <div class='erp-card'>
                    <h3 style='color:#34D399; margin-bottom:5px;'>Import Massivo Dati</h3>
                    <p style='color:var(--kpi-text-sub); font-size:14px; margin-bottom:20px;'>Sincronizza l'anagrafica da fonti esterne</p>
                """, unsafe_allow_html=True)
                up = st.file_uploader("Upload", type=['csv'], label_visibility="collapsed")
                st.markdown("</div>", unsafe_allow_html=True)
                
                if up: 
                    st.success("Decodifica file avvenuta con successo. Dati pronti al merge.")

        elif pagina_hr == "Data Repository":
            st.markdown("<h1 class='gradient-title'>Data Repository</h1>", unsafe_allow_html=True)
            df_v = df_risorse.copy()
            df_v['Disponibile_dal'] = df_v['Disponibile_dal'].apply(formatta_data)
            st.dataframe(df_v, hide_index=True, use_container_width=True)

# ==========================================
# 4. COMPONENTE COPILOT AI (WIDGET INFERIORE)
# ==========================================
if (st.session_state.pm_logged_in or st.session_state.hr_logged_in):
    st.sidebar.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    with st.sidebar.popover("Smart Assistant", use_container_width=True):
        st.caption("Motore LLM LLaMA-3 (Attivo)" if st.session_state.groq_api_key else "Inserisci Chiave API nei Secrets per abilitare l'AI")
        
        for m in st.session_state.chat_msgs: 
            st.chat_message(m["role"]).write(m["content"])
        
        if st.session_state.bot_action:
            act = st.session_state.bot_action
            st.markdown("### Conferma Dettagli")
            
            with st.form("form_conferma_bot"):
                if act['type'] == 'alloca':
                    val_nomi = ", ".join(act.get('nomi', []))
                    if not val_nomi and 'nome' in act: 
                        val_nomi = act['nome']
                        
                    nuovi_nomi = st.text_input("Risorse Assegnate (separate da virgola):", value=val_nomi)
                    nuovo_cliente = st.text_input("Progetto/Cliente:", value=act.get('cliente', ''))
                    nuova_perc = st.slider("Impegno Richiesto (%)", 0, 100, int(act.get('perc', 100)), 10)
                    
                elif act['type'] == 'promuovi':
                    val_nomi = ", ".join(act.get('nomi', []))
                    if not val_nomi and 'nome' in act: 
                        val_nomi = act['nome']
                        
                    nuovi_nomi = st.text_input("Risorse Selezionate (separate da virgola):", value=val_nomi)
                    livelli = ["Junior", "Mid", "Senior"]
                    curr = act.get('nuova_sen', 'Senior')
                    nuova_sen = st.selectbox("Nuovo Livello Inquadramento:", livelli, index=livelli.index(curr) if curr in livelli else 2)
                
                c1, c2 = st.columns(2)
                if c1.form_submit_button("✅ Conferma", use_container_width=True):
                    if act['type'] == 'alloca':
                        act['nomi'] = [n.strip() for n in nuovi_nomi.split(",") if n.strip()]
                        act['cliente'] = nuovo_cliente
                        act['perc'] = nuova_perc
                    else:
                        act['nomi'] = [n.strip() for n in nuovi_nomi.split(",") if n.strip()]
                        act['nuova_sen'] = nuova_sen
                        
                    esegui_azione_chatbot(act)
                    st.rerun()
                    
                if c2.form_submit_button("❌ Annulla", use_container_width=True):
                    st.session_state.bot_action = None
                    st.rerun()
        else:
            if prompt := st.chat_input("Esegui istruzione..."):
                st.session_state.chat_msgs.append({"role": "user", "content": prompt})
                action, err = parse_chatbot_intent_llm(prompt, df_risorse, st.session_state.groq_api_key)
                
                if err: 
                    st.session_state.chat_msgs.append({"role": "assistant", "content": err})
                else: 
                    st.session_state.bot_action = action
                    
                st.rerun()
