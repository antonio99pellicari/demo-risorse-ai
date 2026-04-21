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

# --- INIEZIONE CSS CORPORATE SAAS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
    
    .stButton>button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
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
    
    .kpi-card {
        background: linear-gradient(145deg, rgba(30,33,39,0.7) 0%, rgba(20,22,26,0.9) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }
    .kpi-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; }
    .kpi-card.blue::before { background: #3B82F6; }
    .kpi-card.green::before { background: #10B981; }
    .kpi-card.red::before { background: #EF4444; }
    .kpi-card.orange::before { background: #F59E0B; }
    
    .kpi-card h3 { color: #8B949E; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0; margin-bottom: 8px;}
    .kpi-card h2 { color: #F8F9FA; font-size: 2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px;}
    
    .alert-box {
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 10px; 
        border-left: 4px solid; 
        background: rgba(30,33,39,0.8);
    }
    .alert-red { border-color: #EF4444; color: #FCA5A5; }
    .alert-orange { border-color: #F59E0B; color: #FCD34D; }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 600;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

def applica_tema_plotly(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Outfit", color="#8B949E"), 
        margin=dict(l=20, r=20, t=40, b=20)
    )
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
    
    # 1. Creazione DB Risorse (Base)
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

    # 2. Creazione DB Commesse
    df_commesse = pd.DataFrame([
        {"ID_Commessa": "PRJ-001", "Cliente": "Enel", "Nome": "Migrazione Cloud AWS", "Budget": 45000, "Stato": "Attivo"},
        {"ID_Commessa": "PRJ-002", "Cliente": "TIM", "Nome": "App Mobile React", "Budget": 38000, "Stato": "Attivo"},
        {"ID_Commessa": "PRJ-003", "Cliente": "Intesa", "Nome": "Dashboard IoT", "Budget": 60000, "Stato": "Attivo"},
        {"ID_Commessa": "PRJ-004", "Cliente": "Ferrari", "Nome": "Piattaforma E-commerce", "Budget": 20000, "Stato": "In Avvio"},
        {"ID_Commessa": "PRJ-005", "Cliente": "Poste", "Nome": "Ottimizzazione SQL", "Budget": 15000, "Stato": "Attivo"}
    ])

    # 3. Creazione DB Allocazioni e Timesheet
    allocazioni = []
    timesheet = []
    
    for _, risorsa in df_risorse.iterrows():
        num_commesse = random.choices([0, 1, 2], weights=[0.3, 0.5, 0.2])[0]
        id_risorsa = risorsa['ID']
        
        if num_commesse > 0:
            commesse_assegnate = random.sample(df_commesse['ID_Commessa'].tolist(), k=num_commesse)
            for c_id in commesse_assegnate:
                perc = random.choice([50, 100, 100])
                allocazioni.append({
                    "ID_Risorsa": id_risorsa,
                    "ID_Commessa": c_id,
                    "Impegno_%": perc
                })
                
                giorni_spesi = random.randint(5, 45)
                timesheet.append({
                    "ID_Risorsa": id_risorsa,
                    "ID_Commessa": c_id,
                    "Data_Log": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                    "Giornate_Spese": giorni_spesi
                })

    df_allocazioni = pd.DataFrame(allocazioni) if allocazioni else pd.DataFrame(columns=["ID_Risorsa", "ID_Commessa", "Impegno_%"])
    df_timesheet = pd.DataFrame(timesheet) if timesheet else pd.DataFrame(columns=["ID_Risorsa", "ID_Commessa", "Data_Log", "Giornate_Spese"])

    return df_risorse, df_commesse, df_allocazioni, df_timesheet

# --- HELPER FUNCTIONS RELAZIONALI ---
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

# --- FIX INIZIALIZZAZIONE ---
if "df_risorse" not in st.session_state or "df_allocazioni" not in st.session_state:
    res, comm, alloc, ts = genera_dati_strutturali()
    st.session_state.df_risorse = res
    st.session_state.df_commesse = comm
    st.session_state.df_allocazioni = alloc
    st.session_state.df_timesheet = ts

if "pending_approvals" not in st.session_state: st.session_state.pending_approvals = []
if "pending_allocations" not in st.session_state: st.session_state.pending_allocations = []
if "cal_month_idx" not in st.session_state: st.session_state.cal_month_idx = 0
if "team_cal_idx" not in st.session_state: st.session_state.team_cal_idx = 0

if "chat_msgs" not in st.session_state:
    st.session_state.chat_msgs = [{"role": "assistant", "content": "Sistema Copilot inizializzato. (Es: 'Alloca Marco Rossi su PRJ-001 al 50%')"}]
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
    prompt_l = prompt.lower()
    nome_trovato = None
    for nome in df['Nome']:
        if nome.lower() in prompt_l:
            nome_trovato = nome
            break
    if not nome_trovato: 
        return None, "Identità risorsa non rilevata nel Master Data. Riformulare la query."
    
    if "alloca" in prompt_l or "assegna" in prompt_l:
        perc_match = re.search(r'(\d+)%', prompt_l)
        perc = int(perc_match.group(1)) if perc_match else 100
        cliente = "PRJ-XXX"
        match_cliente = re.search(r'(?:su|sul|sulla)\s+([a-zA-Z0-9_\-]+)', prompt_l.replace("progetto ", ""))
        if match_cliente: 
            cliente = match_cliente.group(1).upper()
        desc = f"Preparazione allocazione per **{nome_trovato}** su {cliente} al {perc}%."
        return {"type": "alloca", "nome": nome_trovato, "perc": perc, "cliente": cliente, "desc": desc}, None
    
    if "promuovi" in prompt_l:
        sen = "Senior" if "senior" in prompt_l else "Mid" if "mid" in prompt_l else "Junior"
        return {"type": "promuovi", "nome": nome_trovato, "nuova_sen": sen, "desc": f"Transazione di upgrade a livello **{sen}** predisposta per **{nome_trovato}**."}, None
    
    return None, "Comando non riconosciuto."

def parse_chatbot_intent_llm(prompt, df, api_key):
    if not api_key:
        return fallback_simulatore_chatbot(prompt, df)
    lista_nomi = ", ".join(df['Nome'].tolist())
    system_prompt = f"""
    Sei Copilot. Rispondi SEMPRE E SOLO con JSON valido. Nomi a DB: {lista_nomi}
    1. ALLOCARE: {{"azione": "alloca", "nome": "Nome Cognome", "percentuale": 50, "cliente": "ID_Commessa", "messaggio_riepilogo": "Allocazione inizializzata..."}}
    2. PROMUOVERE: {{"azione": "promuovi", "nome": "Nome Cognome", "nuova_seniority": "Senior", "messaggio_riepilogo": "Upgrade preparato..."}}
    3. ALTRO: {{"azione": "errore", "messaggio_riepilogo": "Comandi: alloca risorsa, promuovi risorsa."}}
    """
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "temperature": 0.1}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200: return None, f"Errore LLM: {response.text}"
        
        testo_risposta = response.json()["choices"][0]["message"]["content"]
        match = re.search(r'\{.*\}', testo_risposta, re.DOTALL)
        dati = json.loads(match.group(0)) if match else json.loads(testo_risposta)
        
        if dati.get("azione") == "errore": return None, dati.get("messaggio_riepilogo")
        if dati.get("azione") == "alloca": return {"type": "alloca", "nome": dati.get("nome"), "perc": dati.get("percentuale", 100), "cliente": dati.get("cliente", "N/D"), "desc": dati.get("messaggio_riepilogo")}, None
        if dati.get("azione") == "promuovi": return {"type": "promuovi", "nome": dati.get("nome"), "nuova_sen": dati.get("nuova_seniority"), "desc": dati.get("messaggio_riepilogo")}, None
        return None, "Azione non riconosciuta dal parser LLM."
    except Exception as e:
        return None, f"Errore Network AI: {str(e)}"

def esegui_azione_chatbot(dati_finali):
    df_ris = st.session_state.df_risorse
    idx_ris = df_ris[df_ris['Nome'] == dati_finali['nome']].index
    if len(idx_ris) == 0:
        st.session_state.chat_msgs.append({"role": "assistant", "content": "Errore: Risorsa non trovata a database."})
        st.session_state.bot_action = None
        return
        
    id_risorsa = df_ris.iloc[idx_ris[0]]['ID']
    if dati_finali['type'] == 'alloca':
        nuova_alloc = pd.DataFrame([{"ID_Risorsa": id_risorsa, "ID_Commessa": dati_finali['cliente'], "Impegno_%": dati_finali['perc']}])
        st.session_state.df_allocazioni = pd.concat([st.session_state.df_allocazioni, nuova_alloc], ignore_index=True)
        msg = f"Task Eseguito: Profilo **{dati_finali['nome']}** agganciato a **{dati_finali['cliente']}** ({dati_finali['perc']}%)."
    elif dati_finali['type'] == 'promuovi':
        ruolo_puro = df_ris.at[idx_ris[0], 'Ruolo'].replace('Senior ', '').replace('Mid ', '').replace('Junior ', '')
        st.session_state.df_risorse.at[idx_ris[0], 'Seniority'] = dati_finali['nuova_sen']
        st.session_state.df_risorse.at[idx_ris[0], 'Ruolo'] = f"{dati_finali['nuova_sen']} {ruolo_puro}"
        msg = f"Task Eseguito: **{dati_finali['nome']}** promosso a livello **{dati_finali['nuova_sen']}**."

    st.session_state.bot_action = None
    st.session_state.chat_msgs.append({"role": "assistant", "content": msg})


# ==========================================
# 3. SIDEBAR E NAVIGAZIONE
# ==========================================
st.sidebar.markdown("<div style='font-size: 26px; font-weight: 800; letter-spacing: -1px; color: #F8F9FA; margin-bottom: 30px; margin-top: -20px;'>Resource<span style='color: #3B82F6;'>AI</span></div>", unsafe_allow_html=True)

ruolo_utente = st.sidebar.selectbox("PROFILO DI ACCESSO", ["Resource Allocation Engine", "Talent Management", "Talent Workspace"])
st.sidebar.markdown("<br>", unsafe_allow_html=True)

if ruolo_utente != "Resource Allocation Engine": st.session_state.pm_logged_in = False
if ruolo_utente != "Talent Workspace": 
    st.session_state.it_logged_in = False
    st.session_state.current_it_user = None
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
            password = st.text_input("Credenziale di Rete", type="password", help="admin / admin123")
            if st.form_submit_button("Inizializza Sessione"):
                if username == "admin" and password == "admin123":
                    st.session_state.pm_logged_in = True
                    st.rerun()
                else: 
                    st.error("Rifiutato. Credenziali non conformi.")
    else:
        num_req_alloc = len(st.session_state.pending_allocations)
        tab_allocazioni = f"Allocazione risorse ({num_req_alloc})" if num_req_alloc > 0 else "Allocazione risorse"
        
        pagina_pm = st.sidebar.radio("MODULI OPERATIVI", [
            "Homepage", 
            "Centro Gestione Commesse",  # NUOVO MODULO
            "Allocation Advisor",
            tab_allocazioni,
            "Componi il tuo team",
            "Portfolio Commesse",
            "Indagine Profili", 
            "Master Data Risorse"
        ])
        
        if st.sidebar.button("Termina Sessione Corrente"):
            st.session_state.pm_logged_in = False
            st.rerun()

        if pagina_pm == "Homepage":
            st.markdown("<h1 class='gradient-title'>Homepage Manageriale</h1>", unsafe_allow_html=True)
            
            st.subheader("⚠️ Motore di Coerenza: Alert e Incoerenze")
            
            if not df_allocazioni.empty:
                sat_df = df_allocazioni.groupby('ID_Risorsa')['Impegno_%'].sum().reset_index()
                overbooked = sat_df[sat_df['Impegno_%'] > 100]
            else:
                overbooked = pd.DataFrame()
                
            commesse_loss = []
            if not df_timesheet.empty:
                ts_cost = pd.merge(df_timesheet, df_risorse[['ID', 'Costo_Giorno']], left_on='ID_Risorsa', right_on='ID')
                ts_cost['Costo_Tot_Riga'] = ts_cost['Giornate_Spese'] * ts_cost['Costo_Giorno']
                costo_aggregato = ts_cost.groupby('ID_Commessa')['Costo_Tot_Riga'].sum().reset_index()
                
                analisi_budget = pd.merge(df_commesse, costo_aggregato, on='ID_Commessa', how='left').fillna(0)
                commesse_loss = analisi_budget[analisi_budget['Costo_Tot_Riga'] > analisi_budget['Budget']]

            has_alerts = False
            if not overbooked.empty:
                has_alerts = True
                for _, r in overbooked.iterrows():
                    match_ris = df_risorse[df_risorse['ID'] == r['ID_Risorsa']]
                    nome_ris = match_ris['Nome'].values[0] if not match_ris.empty else "Sconosciuto"
                    st.markdown(f"<div class='alert-box alert-red'><b>[Over-Allocation Critica]</b> Il record {nome_ris} ({r['ID_Risorsa']}) è saturato al {r['Impegno_%']}%. Necessario re-staffing.</div>", unsafe_allow_html=True)
            
            if len(commesse_loss) > 0:
                has_alerts = True
                for _, c in commesse_loss.iterrows():
                    st.markdown(f"<div class='alert-box alert-orange'><b>[Erosione Margine]</b> La commessa {c['ID_Commessa']} ({c['Cliente']}) ha superato il budget. Consuntivato: €{c['Costo_Tot_Riga']:,.0f} vs Budget: €{c['Budget']:,.0f}.</div>", unsafe_allow_html=True)
            
            if not has_alerts:
                st.success("Nessun conflitto logico rilevato nei dati strutturali. Allocazioni e budget nei limiti.")
            
            st.markdown("---")
            
            if not df_allocazioni.empty:
                risorse_occupate_ids = df_allocazioni['ID_Risorsa'].unique()
                occupate = len(risorse_occupate_ids)
                bench_df = df_risorse[~df_risorse['ID'].isin(risorse_occupate_ids)]
                mancati_incassi_gg = bench_df['Tariffa_Vendita'].sum()
                
                df_alloc_tariffe = pd.merge(df_allocazioni, df_risorse[['ID', 'Tariffa_Vendita']], left_on='ID_Risorsa', right_on='ID')
                df_alloc_tariffe['Revenue_ProQuota'] = df_alloc_tariffe['Tariffa_Vendita'] * (df_alloc_tariffe['Impegno_%'] / 100)
                revenue_attiva_gg = df_alloc_tariffe['Revenue_ProQuota'].sum()
            else:
                occupate = 0
                mancati_incassi_gg = df_risorse['Tariffa_Vendita'].sum()
                revenue_attiva_gg = 0

            tot_risorse = len(df_risorse)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='kpi-card blue'><h3>Database Attivo</h3><h2>{tot_risorse}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='kpi-card'><h3>Risorse Staffate</h3><h2>{occupate}</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='kpi-card red'><h3>Margine Bench (GG)</h3><h2>€ {mancati_incassi_gg:,.0f}</h2></div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='kpi-card green'><h3>Revenue Attesa (GG)</h3><h2>€ {revenue_attiva_gg:,.0f}</h2></div>", unsafe_allow_html=True)

        # ----------------------------------------
        # SOTTO-VISTA: Centro Gestione Commesse (NUOVO)
        # ----------------------------------------
        elif pagina_pm == "Centro Gestione Commesse":
            st.markdown("<h1 class='gradient-title'>Centro Gestione Commesse</h1>", unsafe_allow_html=True)
            st.write("Hub centrale per l'apertura e il monitoraggio dei progetti aziendali. Tutte le allocazioni pescano da questo Master Data.")
            
            # Form per Nuova Commessa
            with st.expander("➕ Apri Nuova Commessa", expanded=False):
                with st.form("form_nuova_commessa"):
                    col1, col2 = st.columns(2)
                    n_id = col1.text_input("Codice ID (es. PRJ-006)")
                    n_cliente = col2.text_input("Ragione Sociale Cliente")
                    n_nome = col1.text_input("Nome Progetto")
                    n_budget = col2.number_input("Budget Previsto (€)", min_value=1000, step=1000, value=50000)
                    n_stato = col1.selectbox("Stato", ["In Avvio", "Attivo", "Sospeso", "Chiuso"])
                    
                    if st.form_submit_button("Registra a Sistema"):
                        if n_id and n_cliente and n_nome:
                            nuova = pd.DataFrame([{
                                "ID_Commessa": n_id, "Cliente": n_cliente, 
                                "Nome": n_nome, "Budget": n_budget, "Stato": n_stato
                            }])
                            st.session_state.df_commesse = pd.concat([st.session_state.df_commesse, nuova], ignore_index=True)
                            st.success(f"Commessa {n_id} generata correttamente.")
                            st.rerun()
                        else:
                            st.error("Compila i campi obbligatori (ID, Cliente, Nome).")

            st.markdown("### Elenco Master Data Commesse")
            # Editor interattivo per modifiche rapide (es. Budget o Stato)
            edited_comm = st.data_editor(
                st.session_state.df_commesse,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "Budget": st.column_config.NumberColumn("Budget (€)", format="€ %d"),
                    "Stato": st.column_config.SelectboxColumn("Stato Operativo", options=["In Avvio", "Attivo", "Sospeso", "Chiuso"])
                }
            )
            if st.button("Salva Modifiche Globali"):
                st.session_state.df_commesse = edited_comm
                st.success("Sincronizzazione eseguita con successo.")

        # ----------------------------------------
        # SOTTO-VISTA: Allocation Advisor
        # ----------------------------------------
        elif pagina_pm == "Allocation Advisor":
            st.markdown("<h1 class='gradient-title'>Allocation Advisor</h1>", unsafe_allow_html=True)
            st.caption("Modulo Supporto Decisionale - Scenario Simulator")
            
            if "saved_testo_brief" not in st.session_state: st.session_state.saved_testo_brief = ""
            def imposta_brief_demo(): st.session_state.saved_testo_brief = "Architettura Cloud. Stack Frontend React. Backend Node.js. Database AWS SQL."
            st.button("Inizializza Caso Studio", on_click=imposta_brief_demo)
            
            testo_da_analizzare = st.text_area("Specifiche Architetturali (WBS Source):", value=st.session_state.saved_testo_brief, height=100)
            st.session_state.saved_testo_brief = testo_da_analizzare

            if st.button("Simula Scenario ed Estrai Copertura", type="primary"):
                fasi, skill_richieste = analizza_testo(testo_da_analizzare)
                if not fasi:
                    st.warning("Keyword non individuate nel dizionario AI (React, Python, AWS, Node, ecc.).")
                else:
                    st.session_state.wbs_data = pd.DataFrame(fasi)
                    team_proposto = []
                    for skill in skill_richieste:
                        for _, risorsa in df_risorse.iterrows():
                            sat = get_saturazione(risorsa['ID'], df_allocazioni)
                            if sat < 100 and skill.lower() in risorsa['Skill'].lower():
                                team_proposto.append({"Skill": skill, "Nome": risorsa['Nome'], "Costo_gg": risorsa['Costo_Giorno'], "Margine_%": 30})
                                break
                        else:
                            team_proposto.append({"Skill": skill, "Nome": "POSIZIONE APERTA (Assunzione)", "Costo_gg": 300, "Margine_%": 30})
                    st.session_state.team_data = pd.DataFrame(team_proposto)

            if "wbs_data" in st.session_state and not st.session_state.wbs_data.empty:
                tab_wbs, tab_team = st.tabs(["Work Breakdown Structure", "Assessment Economico Team"])
                with tab_wbs:
                    edited_wbs = st.data_editor(st.session_state.wbs_data, num_rows="dynamic", key="wbs_editor", use_container_width=True)
                    st.session_state.wbs_data = edited_wbs
                
                with tab_team:
                    edited_team = st.data_editor(
                        st.session_state.team_data, 
                        key="team_editor", 
                        use_container_width=True,
                        column_config={
                            "Costo_gg": st.column_config.NumberColumn("Costo_gg", step=50),
                            "Margine_%": st.column_config.NumberColumn("Margine_%", step=5)
                        }
                    )
                    st.session_state.team_data = edited_team
                    
                    costo_totale_progetto = 0
                    proposta_commerciale = 0
                    for idx, row in edited_wbs.iterrows():
                        membro = edited_team[edited_team['Skill'] == row['Skill']]
                        if not membro.empty:
                            costo_fase = row['Giorni'] * membro.iloc[0]['Costo_gg']
                            costo_totale_progetto += costo_fase
                            proposta_commerciale += costo_fase * (1 + (membro.iloc[0]['Margine_%'] / 100))
                    
                    st.markdown("<br><div style='font-size: 1.6rem; font-weight: 700; color: #F8F9FA; margin-bottom: 15px;'>Previsione Finanziaria di Commessa</div>", unsafe_allow_html=True)
                    c_fin1, c_fin2, c_fin3 = st.columns(3)
                    c_fin1.markdown(f"<div class='kpi-card orange'><h3>Spesa Operativa (OPEX)</h3><h2>€ {costo_totale_progetto:,.0f}</h2></div>", unsafe_allow_html=True)
                    c_fin2.markdown(f"<div class='kpi-card blue'><h3>Valore Offerta (Mercato)</h3><h2>€ {proposta_commerciale:,.0f}</h2></div>", unsafe_allow_html=True)
                    c_fin3.markdown(f"<div class='kpi-card green'><h3>Margine Utile Atteso</h3><h2>€ {proposta_commerciale - costo_totale_progetto:,.0f}</h2></div>", unsafe_allow_html=True)

        # ----------------------------------------
        # SOTTO-VISTA: Allocazione risorse
        # ----------------------------------------
        elif pagina_pm == tab_allocazioni:
            st.markdown("<h1 class='gradient-title'>Allocazione risorse</h1>", unsafe_allow_html=True)
            
            st.subheader("Richieste in Sospeso dai Consulenti")
            if len(st.session_state.pending_allocations) > 0:
                for i, req in enumerate(list(st.session_state.pending_allocations)):
                    with st.container(border=True):
                        st.write(f"Record **{req['Nome']}** richiede allocazione al {req['Occupazione']}% su **{req['Progetto']}** ({req['Dal']} -> {req['Al']})")
                        b1, b2 = st.columns(2)
                        if b1.button("Autorizza Registrazione DB", key=f"alloc_ok_{i}"):
                            id_ris = df_risorse[df_risorse['Nome'] == req['Nome']]['ID'].values[0]
                            nuova = pd.DataFrame([{"ID_Risorsa": id_ris, "ID_Commessa": req['Progetto'], "Impegno_%": req['Occupazione']}])
                            st.session_state.df_allocazioni = pd.concat([st.session_state.df_allocazioni, nuova], ignore_index=True)
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
                        if b2.button("Declina", key=f"alloc_ko_{i}"):
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
            else: 
                st.caption("Nessuna richiesta in coda.")
                
            st.divider()
            
            # --- OVERRIDE ALLOCAZIONI MIGLIORATO ---
            col_l, col_r = st.columns(2)
            
            with col_l:
                st.subheader("Associa Nuova Commessa")
                with st.form("manual_alloc"):
                    r_scelta = st.selectbox("Seleziona Consulente:", df_risorse['Nome'].tolist())
                    commesse_disp = df_commesse['ID_Commessa'] + " - " + df_commesse['Cliente']
                    c_scelta = st.selectbox("Mappa su Commessa Master Data:", commesse_disp.tolist())
                    
                    perc = st.slider("Fattore di Impegno (FTE %)", 0, 100, 100, step=25)
                    
                    if st.form_submit_button("Assegna Risorsa"):
                        id_risorsa = df_risorse[df_risorse['Nome'] == r_scelta]['ID'].values[0]
                        id_commessa = c_scelta.split(" - ")[0]
                        nuova_alloc = pd.DataFrame([{"ID_Risorsa": id_risorsa, "ID_Commessa": id_commessa, "Impegno_%": perc}])
                        st.session_state.df_allocazioni = pd.concat([st.session_state.df_allocazioni, nuova_alloc], ignore_index=True)
                        st.success(f"Log: {r_scelta} agganciato a {id_commessa}.")
                        st.rerun()

            with col_r:
                st.subheader("Revoca Assegnazioni Esistenti")
                if not df_allocazioni.empty:
                    # Facciamo un merge per vedere i nomi e facilitare la rimozione
                    alloc_view = pd.merge(df_allocazioni, df_risorse[['ID', 'Nome']], left_on='ID_Risorsa', right_on='ID')
                    alloc_view = pd.merge(alloc_view, df_commesse[['ID_Commessa', 'Nome']], left_on='ID_Commessa', right_on='ID_Commessa', suffixes=('_Ris', '_Comm'))
                    
                    opzioni_rimozione = []
                    for idx, row in alloc_view.iterrows():
                        opzioni_rimozione.append(f"[{idx}] {row['Nome_Ris']} -> {row['ID_Commessa']} ({row['Impegno_%']}%)")
                        
                    with st.form("remove_alloc"):
                        da_rimuovere = st.selectbox("Seleziona allocazione da interrompere:", opzioni_rimozione)
                        if st.form_submit_button("Revoca Assegnazione"):
                            idx_to_drop = int(da_rimuovere.split("]")[0].replace("[", ""))
                            # idx_to_drop nel df_alloc_view corrisponde all'index originario perché abbiamo fatto un merge... 
                            # Meglio farlo per indice esatto del df_allocazioni
                            # Per sicurezza:
                            real_idx = alloc_view.loc[idx_to_drop].name
                            st.session_state.df_allocazioni = st.session_state.df_allocazioni.drop(index=real_idx)
                            st.success("Allocazione revocata con successo.")
                            st.rerun()
                else:
                    st.caption("Nessuna allocazione attiva a sistema.")

        # ----------------------------------------
        # SOTTO-VISTA: Componi il tuo team
        # ----------------------------------------
        elif pagina_pm == "Componi il tuo team":
            st.markdown("<h1 class='gradient-title'>Analisi Visiva Disponibilità Team</h1>", unsafe_allow_html=True)
            c_f1, c_f2 = st.columns(2)
            
            filtro_sen = c_f1.multiselect("Filtraggio per Livello:", ["Junior", "Mid", "Senior"], default=st.session_state.get('saved_team_filtro', ["Senior", "Mid", "Junior"]))
            st.session_state.saved_team_filtro = filtro_sen
            
            df_filtered = df_risorse[df_risorse['Seniority'].isin(filtro_sen)] if filtro_sen else df_risorse
                
            valid_team = [x for x in st.session_state.get('saved_team_selezionato', []) if x in df_filtered['Nome'].tolist()]
            team_selezionato = c_f2.multiselect("Target Risorse da Valutare:", df_filtered['Nome'].tolist(), default=valid_team)
            st.session_state.saved_team_selezionato = team_selezionato
            
            orizzonte = st.date_input("Orizzonte Analitico:", value=st.session_state.get('saved_team_orizzonte', (datetime.today(), datetime.today() + timedelta(days=180))))
            st.session_state.saved_team_orizzonte = orizzonte
            
            if team_selezionato and len(orizzonte) == 2:
                start_date, end_date = orizzonte
                st.markdown("---")
                
                mesi_presenti = []
                curr = start_date.replace(day=1)
                while curr <= end_date:
                    mesi_presenti.append((curr.year, curr.month))
                    curr = curr.replace(year=curr.year+1, month=1) if curr.month == 12 else curr.replace(month=curr.month+1)
                
                if st.session_state.team_cal_idx >= len(mesi_presenti): st.session_state.team_cal_idx = 0
                
                col_p, col_m, col_n = st.columns([1,2,1])
                if col_p.button("Retrocedi Mese", key="btn_prev_team") and st.session_state.team_cal_idx > 0: 
                    st.session_state.team_cal_idx -= 1; st.rerun()
                if col_n.button("Avanza Mese", key="btn_next_team") and st.session_state.team_cal_idx < len(mesi_presenti) - 1: 
                    st.session_state.team_cal_idx += 1; st.rerun()
                        
                anno_corr, mese_corr = mesi_presenti[st.session_state.team_cal_idx]
                mesi_ita = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
                col_m.markdown(f"<h3 style='text-align:center; color:#3B82F6; margin-top:0;'>{mesi_ita[mese_corr]} {anno_corr}</h3>", unsafe_allow_html=True)
                
                cal = calendar.Calendar(firstweekday=0)
                month_days = cal.monthdatescalendar(anno_corr, mese_corr)
                
                cols_per_row = 3
                for i in range(0, len(team_selezionato), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, nome in enumerate(team_selezionato[i:i+cols_per_row]):
                        with cols[j]:
                            r_dati = df_risorse[df_risorse['Nome'] == nome].iloc[0]
                            sat = get_saturazione(r_dati['ID'], df_allocazioni)
                            prog_att = get_progetti_risorsa(r_dati['ID'], df_allocazioni, df_commesse)
                            
                            st.markdown(f"<h5 style='text-align:center; color:#F8F9FA; margin-bottom:2px;'>{nome}</h5>", unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align:center; font-size:11px; color:#8B949E; margin-top:0px; margin-bottom:10px;'>Rif: {prog_att}</p>", unsafe_allow_html=True)
                            
                            html_cal = "<div style='display:grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 30px;'>"
                            for g in ["Lu", "Ma", "Me", "Gi", "Ve", "Sa", "Do"]: html_cal += f"<div style='text-align:center; font-size:10px;'>{g}</div>"
                                
                            for week in month_days:
                                for day in week:
                                    if day.month != mese_corr:
                                        html_cal += "<div></div>"
                                    else:
                                        if day < start_date or day > end_date or day.weekday() >= 5: bg_color = "#21262D"
                                        elif sat == 0: bg_color = "#EF4444"
                                        elif sat < 100: bg_color = "#F59E0B"
                                        else: bg_color = "#10B981"
                                            
                                        html_cal += f"<div style='background-color:{bg_color}; height:32px; border-radius:4px; display:flex; align-items:center; justify-content:center; font-size:12px; color:#FFF;'>{day.day}</div>"
                            html_cal += "</div>"
                            st.markdown(html_cal, unsafe_allow_html=True)

        # ----------------------------------------
        # SOTTO-VISTA: Portfolio Commesse
        # ----------------------------------------
        elif pagina_pm == "Portfolio Commesse":
            st.markdown("<h1 class='gradient-title'>Salute Portfolio Commesse</h1>", unsafe_allow_html=True)
            st.info("Logica Sistema: Il costo consumato è calcolato moltiplicando le giornate caricate dai consulenti nei Timesheet per il loro costo giornaliero (OPEX) a sistema.")
            
            if not df_timesheet.empty:
                ts_merged = pd.merge(df_timesheet, df_risorse[['ID', 'Costo_Giorno']], left_on='ID_Risorsa', right_on='ID')
                ts_merged['Costo_Consumato_Riga'] = ts_merged['Giornate_Spese'] * ts_merged['Costo_Giorno']
                agg_costi = ts_merged.groupby('ID_Commessa')['Costo_Consumato_Riga'].sum().reset_index()
                df_view = pd.merge(df_commesse, agg_costi, on='ID_Commessa', how='left').fillna(0)
                df_view.rename(columns={'Costo_Consumato_Riga': 'Costo_Attuale_Real_Time'}, inplace=True)
            else:
                df_view = df_commesse.copy()
                df_view['Costo_Attuale_Real_Time'] = 0

            df_view['Delta Margin (Profit/Loss)'] = df_view['Budget'] - df_view['Costo_Attuale_Real_Time']
            
            st.dataframe(
                df_view[['ID_Commessa', 'Cliente', 'Nome', 'Budget', 'Costo_Attuale_Real_Time', 'Delta Margin (Profit/Loss)', 'Stato']],
                column_config={
                    "Budget": st.column_config.NumberColumn("Budget Approvato", format="€ %d"),
                    "Costo_Attuale_Real_Time": st.column_config.NumberColumn("Costo Consuntivato (TS)", format="€ %d"),
                    "Delta Margin (Profit/Loss)": st.column_config.NumberColumn("Margine a Finire", format="€ %d")
                },
                hide_index=True, use_container_width=True
            )

        # ----------------------------------------
        # SOTTO-VISTA: Indagine Profili (Con Edit Assegnazioni)
        # ----------------------------------------
        elif pagina_pm == "Indagine Profili":
            st.markdown("<h1 class='gradient-title'>Ispezione Dettaglio Risorsa</h1>", unsafe_allow_html=True)
            
            options_nomi = df_risorse['Nome'].tolist()
            saved_nome = st.session_state.get('saved_indagine_nome', options_nomi[0])
            nome_ricerca = st.selectbox("Puntatore Identificativo:", options_nomi, index=options_nomi.index(saved_nome) if saved_nome in options_nomi else 0)
            st.session_state.saved_indagine_nome = nome_ricerca
            
            if nome_ricerca:
                dati_ricerca = df_risorse[df_risorse['Nome'] == nome_ricerca].iloc[0]
                id_ricerca = dati_ricerca['ID']
                sat_reale = get_saturazione(id_ricerca, df_allocazioni)
                
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div class='kpi-card blue'><h3>Livello Classificazione</h3><p style='font-size:20px; font-weight:700; color:#FFF; margin:0;'>{dati_ricerca['Ruolo']}</p></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='kpi-card orange'><h3>Matrice Competenze</h3><p style='font-size:20px; font-weight:700; color:#FFF; margin:0;'>{dati_ricerca['Skill']}</p></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='kpi-card green'><h3>Stato Saturazione</h3><p style='font-size:22px; font-weight:700; color:#FFF; margin:0;'>{sat_reale}%</p></div>", unsafe_allow_html=True)

                st.markdown("---")
                # Gestione Commesse Integrate
                st.subheader(f"Commesse Assegnate: {nome_ricerca}")
                allocs_risorsa = df_allocazioni[df_allocazioni['ID_Risorsa'] == id_ricerca]
                
                if not allocs_risorsa.empty:
                    for i, a in allocs_risorsa.iterrows():
                        nome_c = df_commesse[df_commesse['ID_Commessa'] == a['ID_Commessa']]['Nome'].values[0]
                        with st.container(border=True):
                            c_a, c_b, c_c = st.columns([3, 1, 1])
                            c_a.write(f"**{a['ID_Commessa']}** - {nome_c}")
                            c_b.write(f"**Impegno:** {a['Impegno_%']}%")
                            if c_c.button("❌ Revoca", key=f"revoca_{i}"):
                                st.session_state.df_allocazioni = st.session_state.df_allocazioni.drop(i)
                                st.rerun()
                else:
                    st.info("La risorsa è attualmente a Bench (nessuna commessa assegnata).")

        # ----------------------------------------
        # SOTTO-VISTA: Master Data
        # ----------------------------------------
        elif pagina_pm == "Master Data Risorse":
            st.markdown("<h1 class='gradient-title'>Infrastruttura Dati Principale</h1>", unsafe_allow_html=True)
            
            df_view = df_risorse.copy()
            df_view['Saturazione_%'] = df_view['ID'].apply(lambda x: get_saturazione(x, df_allocazioni))
            df_view['Assegnazioni'] = df_view['ID'].apply(lambda x: get_progetti_risorsa(x, df_allocazioni, df_commesse))
            
            st.dataframe(
                df_view[['ID', 'Nome', 'Macro_Area', 'Ruolo', 'Saturazione_%', 'Assegnazioni', 'Costo_Giorno']],
                column_config={
                    "Saturazione_%": st.column_config.ProgressColumn("Saturazione", min_value=0, max_value=100, format="%d%%"),
                    "Costo_Giorno": st.column_config.NumberColumn("OPEX", format="€ %d")
                },
                hide_index=True, use_container_width=True
            )

# ==========================================
# VISTA 2: TALENT WORKSPACE (Consulente IT)
# ==========================================
elif ruolo_utente == "Talent Workspace":
    if not st.session_state.it_logged_in:
        st.markdown("<h1 class='gradient-title'>Gateway di Autenticazione Personale</h1>", unsafe_allow_html=True)
        with st.form("login_it_form"):
            utente_selezionato = st.selectbox("Selettore Identità", df_risorse['Nome'].tolist())
            password_it = st.text_input("Codice Sicurezza", type="password", help="Codice Base: dev123")
            if st.form_submit_button("Accesso di Rete"):
                if password_it == "dev123":
                    st.session_state.it_logged_in = True
                    st.session_state.current_it_user = utente_selezionato
                    st.rerun()
                else: 
                    st.error("Handshake fallito.")
    else:
        st.markdown(f"<h1 class='gradient-title'>Area Operativa: {st.session_state.current_it_user}</h1>", unsafe_allow_html=True)
        if st.button("LOGOUT"):
            st.session_state.it_logged_in = False
            st.rerun()
            
        dati_utente = df_risorse[df_risorse['Nome'] == st.session_state.current_it_user].iloc[0]
        id_consulente = dati_utente['ID']
        sat_attuale = get_saturazione(id_consulente, df_allocazioni)
        prog_attuali = get_progetti_risorsa(id_consulente, df_allocazioni, df_commesse)
        
        tab_profilo, tab_timesheet = st.tabs(["Dashboard Personale", "Consuntivazione (Timesheet)"])
        
        with tab_profilo:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div class='kpi-card blue'><h3>Attributi Profilo</h3>", unsafe_allow_html=True)
                st.write(f"**Cluster Tecnico:** {dati_utente['Ruolo']}")
                st.write(f"**Inventario Skill:** {dati_utente['Skill']}")
                st.write(f"**Carico Operativo:** {sat_attuale}% su {prog_attuali}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.subheader("Processo Espansione Skill")
                nuova_skill = st.text_input("Identificativo Framework (es. GraphQL):")
                if st.button("Sottoponi per Validazione") and nuova_skill.strip():
                    st.session_state.pending_approvals.append({"ID": id_consulente, "Nome": dati_utente['Nome'], "Skill": nuova_skill.strip()})
                    st.success("Transazione inviata in approvazione.")
                    
            with c2:
                st.markdown("<div class='kpi-card orange'><h3>Richiesta Cambio Progetto</h3>", unsafe_allow_html=True)
                with st.form("richiesta_alloc"):
                    progetto_req = st.text_input("Codice Cliente Desiderato")
                    disp_req = st.slider("Fattore di Carico Previsto (%)", 25, 100, 50, step=25)
                    date_req = st.date_input("Timeline", value=(datetime.today(), datetime.today() + timedelta(days=30)))
                    if st.form_submit_button("INVIA RICHIESTA") and len(date_req) == 2:
                        st.session_state.pending_allocations.append({
                            "ID": id_consulente, "Nome": dati_utente['Nome'], 
                            "Progetto": progetto_req, "Occupazione": disp_req, 
                            "Dal": date_req[0], "Al": date_req[1]
                        })
                        st.success("Payload trasmesso in coda manageriale.")
                st.markdown("</div>", unsafe_allow_html=True)
                
        with tab_timesheet:
            st.subheader("Registrazione Attività Mensile")
            st.write("Seleziona la commessa su cui caricare le giornate (FTE) effettivamente spese.")
            
            le_mie_commesse = df_allocazioni[df_allocazioni['ID_Risorsa'] == id_consulente]
            if le_mie_commesse.empty:
                st.warning("Nessuna commessa attiva assegnata sul tuo record. Contattare il Project Manager.")
            else:
                opzioni_commesse = []
                for _, c in le_mie_commesse.iterrows():
                    nome_c = df_commesse[df_commesse['ID_Commessa'] == c['ID_Commessa']]['Nome'].values[0]
                    opzioni_commesse.append(f"{c['ID_Commessa']} - {nome_c}")
                    
                with st.form("timesheet_form"):
                    selezionata = st.selectbox("Puntatore Commessa Target", opzioni_commesse)
                    giornate_spese = st.number_input("Giornate Consuntivate (FTE)", min_value=0.5, max_value=31.0, value=1.0, step=0.5)
                    
                    if st.form_submit_button("Registra Consuntivo in Master Data"):
                        id_c_target = selezionata.split(" - ")[0]
                        nuovo_ts = pd.DataFrame([{
                            "ID_Risorsa": id_consulente,
                            "ID_Commessa": id_c_target,
                            "Data_Log": datetime.now().strftime("%Y-%m-%d"),
                            "Giornate_Spese": giornate_spese
                        }])
                        st.session_state.df_timesheet = pd.concat([st.session_state.df_timesheet, nuovo_ts], ignore_index=True)
                        st.success("Log: Giornate registrate. Il costo impatterà sul budget della commessa in tempo reale.")
                        
            st.markdown("---")
            st.subheader("Storico Caricamenti Personali")
            mio_ts = df_timesheet[df_timesheet['ID_Risorsa'] == id_consulente]
            if not mio_ts.empty:
                st.dataframe(mio_ts[['ID_Commessa', 'Data_Log', 'Giornate_Spese']], use_container_width=True, hide_index=True)
            else:
                st.caption("Nessun dato storico.")

# ==========================================
# VISTA 3: TALENT MANAGEMENT (Ex HR)
# ==========================================
elif ruolo_utente == "Talent Management":
    if not st.session_state.hr_logged_in:
        st.markdown("<h1 class='gradient-title'>Gateway Amministrativo HR</h1>", unsafe_allow_html=True)
        with st.form("login_hr_form"):
            username = st.text_input("Identificativo Reparto")
            password = st.text_input("Chiave Accesso Struttura", type="password", help="hr / hr123")
            if st.form_submit_button("Esegui Login HR"):
                if username == "hr" and password == "hr123":
                    st.session_state.hr_logged_in = True
                    st.rerun()
                else: 
                    st.error("Accesso Denegato. Credenziali incorrette.")
    else:
        pagina_hr = st.sidebar.radio("MODULI HR ATTIVI", [
            "Homepage", 
            "Processo Onboarding",
            "Manutenzione Inquadramenti",
            "Interfaccia ERP (Zucchetti)", 
            "Archivio Generale"
        ])
        
        if st.sidebar.button("Uscita di Sicurezza"):
            st.session_state.hr_logged_in = False
            st.rerun()

        if pagina_hr == "Homepage":
            st.markdown("<h1 class='gradient-title'>Metriche Globali Risorse</h1>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='kpi-card blue'><h3>Headcount Aggregato</h3><h2>{len(df_risorse)}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='kpi-card orange'><h3>Indice Anagrafico Teorico</h3><h2>32 Anni</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='kpi-card green'><h3>Costo Base Ponderato</h3><h2>€ {df_risorse['Costo_Giorno'].mean():.0f}</h2></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Rapporto Classificazioni")
                df_sen = df_risorse['Seniority'].value_counts().reset_index()
                df_sen.columns = ['Seniority', 'Conteggio']
                fig1 = px.pie(df_sen, values='Conteggio', names='Seniority', hole=0.4, color_discrete_sequence=px.colors.sequential.Tealgrn)
                fig1 = applica_tema_plotly(fig1)
                fig1.update_layout(showlegend=False)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_chart2:
                st.subheader("Distribuzione Assorbimento per Ruoli")
                aree_disponibili = ["Cluster Globale"] + sorted(list(df_risorse['Macro_Area'].unique()))
                saved_area = st.session_state.get('saved_hr_area', "Cluster Globale")
                idx_area = aree_disponibili.index(saved_area) if saved_area in aree_disponibili else 0
                area_selezionata = st.selectbox("Filtro di Contesto:", aree_disponibili, index=idx_area)
                st.session_state.saved_hr_area = area_selezionata
                
                df_ruoli = df_risorse if area_selezionata == "Cluster Globale" else df_risorse[df_risorse['Macro_Area'] == area_selezionata]
                df_ruoli = df_ruoli['Ruolo'].str.replace('Senior ', '').str.replace('Mid ', '').str.replace('Junior ', '').value_counts().reset_index()
                df_ruoli.columns = ['Ruolo', 'Conteggio']
                fig2 = px.bar(df_ruoli, x='Ruolo', y='Conteggio', color='Ruolo', color_discrete_sequence=px.colors.sequential.Blues_r)
                fig2 = applica_tema_plotly(fig2)
                fig2.update_layout(showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        elif pagina_hr == "Processo Onboarding":
            st.markdown("<h1 class='gradient-title'>Creazione Nuova Anagrafica</h1>", unsafe_allow_html=True)
            
            with st.form("form_onboarding"):
                col1, col2 = st.columns(2)
                nuovo_nome = col1.text_input("Nominativo Legale")
                nuova_sen = col2.selectbox("Scala Gerarchica", ["Junior", "Mid", "Senior"])
                
                nuovo_ruolo = col1.selectbox("Dominio d'Inquadramento", ["Frontend Developer", "Backend Developer", "Fullstack Developer", "DevOps Engineer", "Data Scientist", "Data Analyst", "Project Manager", "Business Analyst"])
                nuove_skill = col2.text_input("Definizione Competenze (csv format)")
                
                costo_gg = col1.number_input("Opex Standardizzato (€/GG)", min_value=50, max_value=1000, value=200)
                
                if st.form_submit_button("Esegui Scrittura su Database"):
                    if nuovo_nome and nuove_skill:
                        macro_area_auto = "IT" if "Developer" in nuovo_ruolo or "DevOps" in nuovo_ruolo else "Data Science" if "Data" in nuovo_ruolo else "Risk/Management"
                        nuovo_dipendente = pd.DataFrame([{
                            "ID": f"RES-{len(df_risorse)+1000}",
                            "Nome": nuovo_nome,
                            "Macro_Area": macro_area_auto,
                            "Ruolo": f"{nuova_sen} {nuovo_ruolo}",
                            "Seniority": nuova_sen,
                            "Skill": nuove_skill,
                            "Costo_Giorno": costo_gg,
                            "Tariffa_Vendita": costo_gg * 1.4,
                            "Disponibile_dal": datetime.now().strftime("%Y-%m-%d")
                        }])
                        st.session_state.df_risorse = pd.concat([st.session_state.df_risorse, nuovo_dipendente], ignore_index=True)
                        st.success(f"Log Output: Profilo {nuovo_nome} sincronizzato in Master Data.")

        elif pagina_hr == "Manutenzione Inquadramenti":
            st.markdown("<h1 class='gradient-title'>Upgrade Livelli e Manutenzione</h1>", unsafe_allow_html=True)
            
            options_nomi = df_risorse['Nome'].tolist()
            saved_hr_nome = st.session_state.get('saved_hr_manu_nome', options_nomi[0])
            idx_hr_nome = options_nomi.index(saved_hr_nome) if saved_hr_nome in options_nomi else 0
            
            nome_ricerca = st.selectbox("Record Input (Lookup):", options_nomi, index=idx_hr_nome)
            st.session_state.saved_hr_manu_nome = nome_ricerca
            
            if nome_ricerca:
                idx = df_risorse.index[df_risorse['Nome'] == nome_ricerca].tolist()[0]
                dati_attuali = df_risorse.iloc[idx]
                
                sat = get_saturazione(dati_attuali['ID'], df_allocazioni)
                st.info(f"Monitor di Rete: Saturazione a DB = {sat}%")
                
                with st.form("form_modifica_dipendente"):
                    c1, c2 = st.columns(2)
                    nuovo_nome = c1.text_input("Rettifica Nominativo", value=dati_attuali['Nome'])
                    
                    ruolo_attuale_puro = dati_attuali['Ruolo'].replace('Senior ', '').replace('Mid ', '').replace('Junior ', '')
                    ruoli_disponibili = ["Frontend Developer", "Backend Developer", "Fullstack Developer", "DevOps Engineer", "Data Scientist", "Data Analyst", "Project Manager", "Business Analyst"]
                    if ruolo_attuale_puro not in ruoli_disponibili: ruoli_disponibili.append(ruolo_attuale_puro)
                    
                    nuova_sen = c1.selectbox("Cambio Gerarchico", ["Junior", "Mid", "Senior"], index=["Junior", "Mid", "Senior"].index(dati_attuali['Seniority']))
                    nuovo_ruolo = c2.selectbox("Dominio Professionale", ruoli_disponibili, index=ruoli_disponibili.index(ruolo_attuale_puro))
                    
                    nuove_skill = st.text_input("Aggiunta Competenze", value=dati_attuali['Skill'])
                    
                    c3, c4 = st.columns(2)
                    costo_gg = c3.number_input("Modifica OPEX Diretto (€)", value=int(dati_attuali['Costo_Giorno']))
                    tariffa_vendita = c4.number_input("Modifica Mark-up Base (€)", value=int(dati_attuali['Tariffa_Vendita']))
                    
                    if st.form_submit_button("Esegui Aggiornamento Profilo"):
                        st.session_state.df_risorse.at[idx, 'Nome'] = nuovo_nome
                        st.session_state.df_risorse.at[idx, 'Seniority'] = nuova_sen
                        st.session_state.df_risorse.at[idx, 'Ruolo'] = f"{nuova_sen} {nuovo_ruolo}"
                        st.session_state.df_risorse.at[idx, 'Skill'] = nuove_skill
                        st.session_state.df_risorse.at[idx, 'Costo_Giorno'] = costo_gg
                        st.session_state.df_risorse.at[idx, 'Tariffa_Vendita'] = tariffa_vendita
                        st.success("Update Eseguito: I nuovi parametri sono validi.")
                        st.rerun()

        elif pagina_hr == "Interfaccia ERP (Zucchetti)":
            st.markdown("<h1 class='gradient-title'>Ponte ERP Software Paghe</h1>", unsafe_allow_html=True)
            st.download_button("Genera Pacchetto CSV (.csv)", data=df_risorse.to_csv(index=False).encode('utf-8'), file_name='export_hr_zucchetti.csv', mime='text/csv')
            
            uploaded_file = st.file_uploader("Upload Tracciato (.csv o .xlsx)", type=['csv', 'xlsx'])
            if uploaded_file is not None:
                new_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                st.success("Lettura eseguita."); st.dataframe(new_df.head())

        elif pagina_hr == "Archivio Generale":
            st.markdown("<h1 class='gradient-title'>Ispezione Diretta Records</h1>", unsafe_allow_html=True)
            
            df_view = df_risorse.copy()
            df_view['Saturazione_%'] = df_view['ID'].apply(lambda x: get_saturazione(x, df_allocazioni))
            df_view['Assegnazioni'] = df_view['ID'].apply(lambda x: get_progetti_risorsa(x, df_allocazioni, df_commesse))
            
            st.dataframe(df_view, hide_index=True, use_container_width=True)

# ==========================================
# 4. COMPONENTE COPILOT AI (WIDGET INFERIORE)
# ==========================================
if (st.session_state.pm_logged_in or st.session_state.hr_logged_in):
    st.sidebar.markdown("<br><br><br><hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
    
    with st.sidebar.popover("Terminale Copilot AI", use_container_width=True):
        st.caption("Stato Nodo: **Llama-3 LLM (Attivo)**" if st.session_state.groq_api_key else "Stato Nodo: **Regex Fallback (Attivo)**")
            
        for msg in st.session_state.chat_msgs:
            with st.chat_message(msg["role"]): st.write(msg["content"])
        
        if st.session_state.bot_action:
            act = st.session_state.bot_action
            st.info(act['desc'])
            
            if act['type'] == 'alloca':
                with st.form("form_bot_conferma"):
                    c1, c2 = st.columns(2)
                    nuovo_cliente = c1.text_input("Tag Commessa", value=act['cliente'])
                    nuova_perc = c2.number_input("Impegno %", min_value=0, max_value=100, value=act['perc'])
                    c_btn1, c_btn2 = st.columns(2)
                    if c_btn1.form_submit_button("Autorizza Registrazione"):
                        act['cliente'], act['perc'] = nuovo_cliente, nuova_perc
                        esegui_azione_chatbot(act); st.rerun()
                    if c_btn2.form_submit_button("Sospendi"):
                        st.session_state.bot_action = None; st.rerun()
            else:
                col_ok, col_ko = st.columns(2)
                if col_ok.button("Autorizza Transazione"): esegui_azione_chatbot(act); st.rerun()
                if col_ko.button("Sospendi"): st.session_state.bot_action = None; st.rerun()

        if prompt := st.chat_input("Esegui istruzione di sistema..."):
            st.session_state.chat_msgs.append({"role": "user", "content": prompt})
            with st.spinner("Analisi sintattica in corso..."):
                action_dict, error_msg = parse_chatbot_intent_llm(prompt, df_risorse, st.session_state.groq_api_key)
            if error_msg: st.session_state.chat_msgs.append({"role": "assistant", "content": error_msg})
            else: st.session_state.bot_action = action_dict
            st.rerun()

    with st.sidebar.expander("Configurazione Root Backend AI"):
        st.write("Iniezione chiave per motore LLM Llama-3.")
        api_key = st.text_input("Parametro Groq API Key:", value=st.session_state.groq_api_key, type="password")
        if st.button("Forza Aggiornamento"):
            st.session_state.groq_api_key = api_key
            st.success("Parametri salvati sul nodo.")
