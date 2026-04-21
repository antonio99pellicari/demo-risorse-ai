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
st.set_page_config(page_title="ResourceAI - Manager", layout="wide", initial_sidebar_state="expanded")

# --- INIEZIONE CSS CORPORATE SAAS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
    
    /* Bottoni stile corporate uniformato */
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
    
    /* Titoli a gradiente eleganti */
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
    
    /* KPI Cards Glassmorphism */
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
    
    /* Box Alert Motore Coerenza */
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
    
    clienti_italiani = ["Enel", "TIM", "Poste", "Intesa", "Unicredit", "Ferrari", "Eni", "Leonardo"]
    tipi_progetto = ["Piattaforma e-commerce", "App Mobile", "Gestionale", "Dashboard IoT", "Migrazione Cloud"]
    
    db = []
    for i, nome in enumerate(nomi_completi):
        ruolo, skills_possibili, macro_area = random.choice(ruoli_skills)
        skills = random.sample(skills_possibili, k=random.randint(2, len(skills_possibili)))
        seniority = random.choice(["Junior", "Mid", "Senior"])
        costo_base = {"Junior": 150, "Mid": 250, "Senior": 350}[seniority]
        
        # Generiamo alcune over-allocations volute (150%) per mostrare l'alert
        occupazione = random.choice([0, 0, 50, 100, 150]) 
        
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

@st.cache_data
def genera_commesse():
    """Genera un database mockato per le commesse e i budget"""
    return pd.DataFrame([
        {"ID_Commessa": "PRJ-001", "Cliente": "Enel", "Nome": "Migrazione Cloud", "Budget": 150000, "Costo_Attuale": 165000, "Stato": "Attivo", "Skill_Richieste": "AWS, DevOps"},
        {"ID_Commessa": "PRJ-002", "Cliente": "TIM", "Nome": "App Mobile", "Budget": 80000, "Costo_Attuale": 45000, "Stato": "Attivo", "Skill_Richieste": "React, TypeScript"},
        {"ID_Commessa": "PRJ-003", "Cliente": "Intesa", "Nome": "Dashboard IoT", "Budget": 120000, "Costo_Attuale": 115000, "Stato": "Attivo", "Skill_Richieste": "Python, SQL"},
        {"ID_Commessa": "PRJ-004", "Cliente": "Ferrari", "Nome": "Piattaforma e-commerce", "Budget": 95000, "Costo_Attuale": 20000, "Stato": "In Avvio", "Skill_Richieste": "Node.js, React"}
    ])

def estrai_progetto_attuale(row):
    """Estrae il progetto corrente se la risorsa è occupata"""
    if row.get('Occupazione_%', 0) > 0 and isinstance(row.get('Esperienze', []), list) and len(row['Esperienze']) > 0:
        ult = row['Esperienze'][-1]
        return f"{ult.get('Cliente', 'N/D')} - {ult.get('Progetto', 'N/D')}"
    return "Disponibile (Bench)"

# --- INIZIALIZZAZIONE SESSION STATE ---
if "df_risorse" not in st.session_state: 
    st.session_state.df_risorse = genera_database()
if "df_commesse" not in st.session_state: 
    st.session_state.df_commesse = genera_commesse()
if "pending_approvals" not in st.session_state: 
    st.session_state.pending_approvals = []
if "pending_allocations" not in st.session_state: 
    st.session_state.pending_allocations = []
if "cal_month_idx" not in st.session_state: 
    st.session_state.cal_month_idx = 0
if "team_cal_idx" not in st.session_state: 
    st.session_state.team_cal_idx = 0

# Variabili Chatbot
if "chat_msgs" not in st.session_state:
    st.session_state.chat_msgs = [{"role": "assistant", "content": "Sistema Copilot inizializzato. Inserire query di testo (es. Alloca Marco Rossi su TIM al 50%)."}]
if "bot_action" not in st.session_state: 
    st.session_state.bot_action = None
if "groq_api_key" not in st.session_state: 
    st.session_state.groq_api_key = "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"

if "pm_logged_in" not in st.session_state: 
    st.session_state.pm_logged_in = False
if "it_logged_in" not in st.session_state: 
    st.session_state.it_logged_in = False
if "hr_logged_in" not in st.session_state: 
    st.session_state.hr_logged_in = False
if "current_it_user" not in st.session_state: 
    st.session_state.current_it_user = None

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
    if not nome_trovato: 
        return None, "Identità risorsa non rilevata nel Master Data. Riformulare la query."
    
    if "alloca" in prompt_l or "assegna" in prompt_l:
        perc_match = re.search(r'(\d+)%', prompt_l)
        perc = int(perc_match.group(1)) if perc_match else 100
        cliente = "Nuovo Progetto"
        match_cliente = re.search(r'(?:su|sul|sulla)\s+([a-zA-Z0-9_\-]+)', prompt_l.replace("progetto ", ""))
        if match_cliente: 
            cliente = match_cliente.group(1).capitalize()
        desc = f"Record **{nome_trovato}** bloccato temporaneamente per operazione di allocazione."
        return {"type": "alloca", "nome": nome_trovato, "perc": perc, "cliente": cliente, "desc": desc}, None
    
    if "promuovi" in prompt_l:
        sen = "Senior" if "senior" in prompt_l else "Mid" if "mid" in prompt_l else "Junior"
        return {"type": "promuovi", "nome": nome_trovato, "nuova_sen": sen, "desc": f"Transazione di upgrade a livello **{sen}** predisposta per **{nome_trovato}**."}, None
    
    return None, "Comando di sistema non riconosciuto. Sintassi non valida."

def parse_chatbot_intent_llm(prompt, df, api_key):
    """Vero LLM tramite Groq per il Copilot Chatbot (Versione Antiproiettile)"""
    if not api_key:
        return fallback_simulatore_chatbot(prompt, df)
        
    lista_nomi = ", ".join(df['Nome'].tolist())
    
    system_prompt = f"""
    Sei il modulo Copilot integrato in una piattaforma SaaS HR/Project Management.
    Rispondi SEMPRE E SOLO con un oggetto JSON valido. Non aggiungere discorsi discorsivi.
    Dipendenti presenti a sistema: {lista_nomi}
    
    REGOLE DI RISPOSTA:
    1. Se l'utente chiede di ALLOCARE/ASSEGNARE:
    {{"azione": "alloca", "nome": "Nome e Cognome", "percentuale": 50, "cliente": "Nome cliente", "messaggio_riepilogo": "Processo di allocazione inizializzato..."}}
    
    2. Se l'utente chiede di PROMUOVERE/AVANZARE DI LIVELLO:
    {{"azione": "promuovi", "nome": "Nome e Cognome", "nuova_seniority": "Junior/Mid/Senior", "messaggio_riepilogo": "Iter di promozione preparato..."}}
    
    3. Se l'utente saluta o fa richieste fuori contesto (es. "ciao come stai"):
    {{"azione": "errore", "messaggio_riepilogo": "Copilot di sistema online. Funzionalità attive: Allocazione su commessa, Variazione livelli di seniority."}}
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
            return None, f"Errore Gateway LLM (Codice {response.status_code}): {response.text}"
            
        testo_risposta = response.json()["choices"][0]["message"]["content"]
        
        try:
            match = re.search(r'\{.*\}', testo_risposta, re.DOTALL)
            dati = json.loads(match.group(0)) if match else json.loads(testo_risposta)
        except:
            return None, f"Errore decodifica JSON dal payload AI."
        
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
            
        return None, "Interpretazione logica del payload fallita. Query non compresa."
    except Exception as e:
        return None, f"Errore di connettività Nodo AI: {str(e)}"

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
        msg = f"Task Eseguito: Profilo **{dati_finali['nome']}** integrato su commessa **{dati_finali['cliente']}** (Saturazione: {dati_finali['perc']}%)."
        
    elif dati_finali['type'] == 'promuovi':
        ruolo_puro = df.at[idx, 'Ruolo'].replace('Senior ', '').replace('Mid ', '').replace('Junior ', '')
        df.at[idx, 'Seniority'] = dati_finali['nuova_sen']
        df.at[idx, 'Ruolo'] = f"{dati_finali['nuova_sen']} {ruolo_puro}"
        msg = f"Task Eseguito: Aggiornamento anagrafico completato. **{dati_finali['nome']}** promosso a livello **{dati_finali['nuova_sen']}**."

    st.session_state.bot_action = None
    st.session_state.chat_msgs.append({"role": "assistant", "content": msg})


# ==========================================
# 3. SIDEBAR E NAVIGAZIONE (CORPORATE STYLE)
# ==========================================
# Logo Aziendale
st.sidebar.markdown("<div style='font-size: 26px; font-weight: 800; letter-spacing: -1px; color: #F8F9FA; margin-bottom: 30px; margin-top: -20px;'>Resource<span style='color: #3B82F6;'>AI</span></div>", unsafe_allow_html=True)

ruolo_utente = st.sidebar.selectbox("PROFILO DI ACCESSO", ["Resource Allocation Engine", "Talent Management", "Talent Workspace"])
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Gestione Logout Dinamica
if ruolo_utente != "Resource Allocation Engine": 
    st.session_state.pm_logged_in = False
if ruolo_utente != "Talent Workspace": 
    st.session_state.it_logged_in = False
    st.session_state.current_it_user = None
if ruolo_utente != "Talent Management": 
    st.session_state.hr_logged_in = False

df = st.session_state.df_risorse
df_commesse = st.session_state.df_commesse

# ==========================================
# VISTA 1: RESOURCE ALLOCATION ENGINE (Ex PM)
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

        # ----------------------------------------
        # SOTTO-VISTA: Homepage (Con Consistency Engine)
        # ----------------------------------------
        if pagina_pm == "Homepage":
            st.markdown("<h1 class='gradient-title'>Homepage Manageriale</h1>", unsafe_allow_html=True)
            
            # CONSISTENCY ENGINE (Motore di Coerenza e Alerting)
            st.subheader("⚠️ Motore di Coerenza: Alert e Incoerenze")
            
            overbooked = df[df['Occupazione_%'] > 100]
            commesse_loss = df_commesse[df_commesse['Costo_Attuale'] > df_commesse['Budget']]
            
            has_alerts = False
            
            if not overbooked.empty:
                has_alerts = True
                for _, r in overbooked.iterrows():
                    st.markdown(f"<div class='alert-box alert-red'><b>[Over-Allocation Critica]</b> Il record {r['Nome']} ({r['Ruolo']}) risulta allocato al {r['Occupazione_%']}%. Necessario bilanciamento immediato.</div>", unsafe_allow_html=True)
            
            if not commesse_loss.empty:
                has_alerts = True
                for _, c in commesse_loss.iterrows():
                    st.markdown(f"<div class='alert-box alert-orange'><b>[Erosione Margine]</b> La commessa {c['ID_Commessa']} ({c['Nome']}) ha superato il budget stimato. Costo: €{c['Costo_Attuale']} vs Budget: €{c['Budget']}.</div>", unsafe_allow_html=True)
            
            if not has_alerts:
                st.success("Nessun conflitto logico rilevato nei dati di Master Data. Condizioni ottimali.")
            
            st.markdown("---")
            
            if num_req_alloc > 0:
                st.warning(f"Avviso di Sistema: {num_req_alloc} richieste di allocazione in coda di attesa.")
            
            tot_risorse = len(df)
            occupate = len(df[df['Occupazione_%'] > 0])
            mancati_incassi_gg = df[df['Occupazione_%'] == 0]['Tariffa_Vendita'].sum()
            revenue_attiva_gg = (df['Tariffa_Vendita'] * (df['Occupazione_%']/100)).sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='kpi-card blue'><h3>Database Attivo</h3><h2>{tot_risorse}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='kpi-card'><h3>Risorse in Carico</h3><h2>{occupate}</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='kpi-card red'><h3>Margine Non Realizzato (GG)</h3><h2>€ {mancati_incassi_gg:,.0f}</h2></div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='kpi-card green'><h3>Revenue Attesa (GG)</h3><h2>€ {revenue_attiva_gg:,.0f}</h2></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("Rapporto di Finanza Operativa")
            df_fin = pd.DataFrame({
                "Categoria": ["Bench (Passivo)", "Staffati (Attivo)"],
                "Valore Giornaliero": [mancati_incassi_gg, revenue_attiva_gg]
            })
            fig_fin = px.pie(df_fin, values='Valore Giornaliero', names='Categoria', hole=0.3,
                             color='Categoria', color_discrete_map={"Bench (Passivo)": "#EF4444", "Staffati (Attivo)": "#10B981"})
            st.plotly_chart(applica_tema_plotly(fig_fin), use_container_width=True)

        # ----------------------------------------
        # SOTTO-VISTA: Allocation Advisor
        # ----------------------------------------
        elif pagina_pm == "Allocation Advisor":
            st.markdown("<h1 class='gradient-title'>Allocation Advisor</h1>", unsafe_allow_html=True)
            st.caption("Modulo Analisi: Rules Engine Deterministico (Upgrade LLM Semantico in roadmap)")
            
            # Gestione Persistenza
            if "saved_testo_brief" not in st.session_state:
                st.session_state.saved_testo_brief = ""
            
            def imposta_brief_demo():
                st.session_state.saved_testo_brief = "Il client richiede una nuova architettura web. Stack Frontend in React e TypeScript. Stack Backend in Node.js. Database SQL su Cloud AWS."
            
            st.button("Inizializza Query Demo", on_click=imposta_brief_demo)
            
            testo_da_analizzare = st.text_area("Input Parametri Architetturali (Brief Tecnico):", value=st.session_state.saved_testo_brief, height=100)
            st.session_state.saved_testo_brief = testo_da_analizzare

            if st.button("Elabora WBS e Copertura Target", type="primary"):
                fasi, skill_richieste = analizza_testo(testo_da_analizzare)
                
                if not fasi:
                    st.warning("Errore di Parsing: Nessun framework riconosciuto. Inserire standard di mercato (es. React, Python, AWS).")
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
                            team_proposto.append({"Skill": skill, "Nome": "POSIZIONE APERTA", "Costo_gg": 300, "Margine_%": 30})
                    st.session_state.team_data = pd.DataFrame(team_proposto)

            if "wbs_data" in st.session_state and not st.session_state.wbs_data.empty:
                tab_wbs, tab_team = st.tabs(["Work Breakdown Structure", "Assessment Economico Team"])
                
                with tab_wbs:
                    # Storicizza modifiche editor WBS
                    edited_wbs = st.data_editor(st.session_state.wbs_data, num_rows="dynamic", key="wbs_editor", use_container_width=True)
                    st.session_state.wbs_data = edited_wbs
                
                with tab_team:
                    # Storicizza modifiche editor Team (con step cost=50 e margin=5)
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
                    
                    # Rimosso il "###"
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
            
            st.subheader("Richieste in Sospeso")
            if len(st.session_state.pending_allocations) > 0:
                for i, req in enumerate(list(st.session_state.pending_allocations)):
                    with st.container(border=True):
                        st.write(f"Record **{req['Nome']}** richiede copertura al {req['Occupazione']}% per la commessa **{req['Progetto']}** (Periodo: {req['Dal']} -> {req['Al']})")
                        b1, b2 = st.columns(2)
                        if b1.button("Autorizza Transazione", key=f"alloc_ok_{i}"):
                            idx = df.index[df['ID'] == req['ID']].tolist()[0]
                            st.session_state.df_risorse.at[idx, 'Occupazione_%'] = req['Occupazione']
                            st.session_state.df_risorse.at[idx, 'Disponibile_dal'] = req['Al'].strftime("%Y-%m-%d")
                            st.session_state.df_risorse.at[idx, 'Esperienze'].append({"Cliente": "Gestione Interna", "Progetto": req['Progetto'], "Tecnologie_Usate": []})
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
                        if b2.button("Declina Istanza", key=f"alloc_ko_{i}"):
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
            else: 
                st.caption("Nessun task in coda operativa.")
                
            st.divider()
            st.subheader("Modulo di Override")
            with st.form("manual_alloc"):
                r_scelta = st.selectbox("Identificativo Risorsa:", df['Nome'].tolist())
                c_form1, c_form2 = st.columns(2)
                cliente_input = c_form1.text_input("Ragione Sociale Cliente")
                progetto_input = c_form2.text_input("Codice / Nome Progetto")
                
                c_form3, c_form4 = st.columns(2)
                oggi = datetime.today()
                date_range = c_form3.date_input("Finestra Temporale Copertura", value=(oggi, oggi + timedelta(days=60)))
                perc = c_form4.slider("Indice Saturazione Obiettivo (%)", 0, 100, 100, step=25)
                
                if st.form_submit_button("Esegui Forzatura Allocazione"):
                    if len(date_range) == 2 and cliente_input:
                        idx = df.index[df['Nome'] == r_scelta].tolist()[0]
                        st.session_state.df_risorse.at[idx, 'Occupazione_%'] = perc
                        st.session_state.df_risorse.at[idx, 'Disponibile_dal'] = date_range[1].strftime("%Y-%m-%d")
                        st.session_state.df_risorse.at[idx, 'Esperienze'].append({"Cliente": cliente_input, "Progetto": progetto_input, "Tecnologie_Usate": []})
                        st.success(f"Log: Intervento su {r_scelta} registrato e propagato.")
                    else:
                        st.error("Log: Campi obbligatori mancanti.")

        # ----------------------------------------
        # SOTTO-VISTA: Componi il tuo team
        # ----------------------------------------
        elif pagina_pm == "Componi il tuo team":
            st.markdown("<h1 class='gradient-title'>Analisi Visiva Disponibilità Team</h1>", unsafe_allow_html=True)
            st.write("Verifica degli incroci di agenda su orizzonte esteso.")
            
            c_f1, c_f2 = st.columns(2)
            
            # Memoria filtro Sen
            filtro_sen = c_f1.multiselect("Filtraggio per Livello:", ["Junior", "Mid", "Senior"], default=st.session_state.get('saved_team_filtro', ["Senior", "Mid", "Junior"]))
            st.session_state.saved_team_filtro = filtro_sen
            
            df_filtered = df[df['Seniority'].isin(filtro_sen)] if filtro_sen else df
                
            # Memoria filtro Target e validazione opzioni disponibili
            valid_team = [x for x in st.session_state.get('saved_team_selezionato', []) if x in df_filtered['Nome'].tolist()]
            team_selezionato = c_f2.multiselect("Target Risorse da Valutare:", df_filtered['Nome'].tolist(), default=valid_team)
            st.session_state.saved_team_selezionato = team_selezionato
            
            if "team_cal_idx" not in st.session_state: 
                st.session_state.team_cal_idx = 0
                
            # Memoria Orizzonte
            orizzonte = st.date_input("Configurazione Orizzonte Analitico:", value=st.session_state.get('saved_team_orizzonte', (datetime.today(), datetime.today() + timedelta(days=180))))
            st.session_state.saved_team_orizzonte = orizzonte
            
            if team_selezionato and len(orizzonte) == 2:
                start_date, end_date = orizzonte
                st.markdown("---")
                
                mesi_presenti = []
                curr = start_date.replace(day=1)
                while curr <= end_date:
                    mesi_presenti.append((curr.year, curr.month))
                    if curr.month == 12: 
                        curr = curr.replace(year=curr.year+1, month=1)
                    else: 
                        curr = curr.replace(month=curr.month+1)
                
                if st.session_state.team_cal_idx >= len(mesi_presenti): 
                    st.session_state.team_cal_idx = 0
                
                col_p, col_m, col_n = st.columns([1,2,1])
                if col_p.button("Retrocedi Mese", key="btn_prev_team"):
                    if st.session_state.team_cal_idx > 0:
                        st.session_state.team_cal_idx -= 1
                        st.rerun()
                if col_n.button("Avanza Mese", key="btn_next_team"):
                    if st.session_state.team_cal_idx < len(mesi_presenti) - 1:
                        st.session_state.team_cal_idx += 1
                        st.rerun()
                        
                anno_corr, mese_corr = mesi_presenti[st.session_state.team_cal_idx]
                mesi_ita = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
                nome_mese = mesi_ita[mese_corr]
                
                col_m.markdown(f"<h3 style='text-align:center; color:#3B82F6; margin-top:0;'>{nome_mese} {anno_corr}</h3>", unsafe_allow_html=True)
                
                st.markdown("""
                <div style="display:flex; justify-content:center; gap:20px; font-size:12px; margin-bottom: 30px; color:#8B949E;">
                    <div style="display:flex; align-items:center;"><div style="width:12px; height:12px; background:#EF4444; border-radius:2px; margin-right:5px;"></div> Disponibilità Completa</div>
                    <div style="display:flex; align-items:center;"><div style="width:12px; height:12px; background:#F59E0B; border-radius:2px; margin-right:5px;"></div> Saturazione Parziale</div>
                    <div style="display:flex; align-items:center;"><div style="width:12px; height:12px; background:#10B981; border-radius:2px; margin-right:5px;"></div> Saturazione Totale</div>
                    <div style="display:flex; align-items:center;"><div style="width:12px; height:12px; background:#21262D; border-radius:2px; margin-right:5px;"></div> Fuori Copertura / Festivo</div>
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
                            
                            st.markdown(f"<h5 style='text-align:center; color:#F8F9FA; margin-bottom:2px;'>{nome}</h5>", unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align:center; font-size:11px; color:#8B949E; margin-top:0px; margin-bottom:10px;'>Rif: {prog_att}</p>", unsafe_allow_html=True)
                            
                            data_libero = datetime.strptime(r_dati['Disponibile_dal'], "%Y-%m-%d").date()
                            occ_attuale = r_dati['Occupazione_%']
                            
                            html_cal = "<div style='display:grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 30px;'>"
                            
                            for g in giorni_sett:
                                html_cal += f"<div style='text-align:center; font-size:10px; font-weight:700; color:#8B949E;'>{g}</div>"
                                
                            for week in month_days:
                                for day in week:
                                    if day.month != mese_corr:
                                        html_cal += "<div style='visibility:hidden;'></div>"
                                    else:
                                        occ = occ_attuale if day < data_libero else 0
                                        if day < start_date or day > end_date: 
                                            bg_color = "#21262D"
                                        elif day.weekday() >= 5: 
                                            bg_color = "#21262D"
                                        elif occ == 0: 
                                            bg_color = "#EF4444"
                                        elif occ < 100: 
                                            bg_color = "#F59E0B"
                                        else: 
                                            bg_color = "#10B981"
                                            
                                        html_cal += f"<div style='background-color:{bg_color}; height:32px; border-radius:4px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:600; color:#FFF;'>{day.day}</div>"
                            
                            html_cal += "</div>"
                            st.markdown(html_cal, unsafe_allow_html=True)

        # ----------------------------------------
        # SOTTO-VISTA: Portfolio Commesse
        # ----------------------------------------
        elif pagina_pm == "Portfolio Commesse":
            st.markdown("<h1 class='gradient-title'>Salute Portfolio Commesse</h1>", unsafe_allow_html=True)
            st.info("Incrocio Dati: Il sistema confronta il budget allocato del progetto con il costo reale delle risorse ad esso assegnate per evidenziare delta margin.")
            
            df_view_comm = df_commesse.copy()
            df_view_comm['Delta Margin'] = df_view_comm['Budget'] - df_view_comm['Costo_Attuale']
            
            st.dataframe(
                df_view_comm,
                column_config={
                    "Budget": st.column_config.NumberColumn("Budget Atteso", format="€ %d"),
                    "Costo_Attuale": st.column_config.NumberColumn("Costo Consumato", format="€ %d"),
                    "Delta Margin": st.column_config.NumberColumn("Delta Margin", format="€ %d")
                },
                hide_index=True, use_container_width=True
            )

        # ----------------------------------------
        # SOTTO-VISTA: Indagine Profili
        # ----------------------------------------
        elif pagina_pm == "Indagine Profili":
            st.markdown("<h1 class='gradient-title'>Ispezione Dettaglio Risorsa</h1>", unsafe_allow_html=True)
            
            # Memoria Selettore Anagrafica
            options_nomi = df['Nome'].tolist()
            saved_nome = st.session_state.get('saved_indagine_nome')
            idx_nome = options_nomi.index(saved_nome) if saved_nome in options_nomi else 0
            
            nome_ricerca = st.selectbox("Puntatore Identificativo:", options_nomi, index=idx_nome)
            st.session_state.saved_indagine_nome = nome_ricerca
            
            if nome_ricerca:
                dati_ricerca = df[df['Nome'] == nome_ricerca].iloc[0]
                prog_att = estrai_progetto_attuale(dati_ricerca)
                
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div class='kpi-card blue'><h3>Livello Classificazione</h3><p style='font-size:20px; font-weight:700; color:#FFF; margin:0;'>{dati_ricerca['Ruolo']}</p></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='kpi-card orange'><h3>Matrice Competenze</h3><p style='font-size:20px; font-weight:700; color:#FFF; margin:0;'>{dati_ricerca['Skill']}</p></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='kpi-card green'><h3>Stato Rete Attuale</h3><p style='font-size:16px; font-weight:700; color:#FFF; margin:0;'>Saturazione {dati_ricerca['Occupazione_%']}%<br>Cliente/Progetto: <span style='color:#10B981;'>{prog_att}</span></p></div>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.subheader("Rappresentazione Vettoriale Agenda (Zoom-in)")
                
                # Memoria Range Date
                date_range = st.date_input("Range di Verifica:", value=st.session_state.get('saved_indagine_date', (datetime.today(), datetime.today() + timedelta(days=180))))
                st.session_state.saved_indagine_date = date_range
                
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    data_libero = datetime.strptime(dati_ricerca['Disponibile_dal'], "%Y-%m-%d").date()
                    
                    mesi_presenti = []
                    curr = start_date.replace(day=1)
                    while curr <= end_date:
                        mesi_presenti.append((curr.year, curr.month))
                        if curr.month == 12: 
                            curr = curr.replace(year=curr.year+1, month=1)
                        else: 
                            curr = curr.replace(month=curr.month+1)
                    
                    if st.session_state.cal_month_idx >= len(mesi_presenti): 
                        st.session_state.cal_month_idx = 0
                    
                    col_p, col_m, col_n = st.columns([1,2,1])
                    if col_p.button("Ciclo Precedente"):
                        if st.session_state.cal_month_idx > 0:
                            st.session_state.cal_month_idx -= 1
                            st.rerun()
                    if col_n.button("Ciclo Successivo"):
                        if st.session_state.cal_month_idx < len(mesi_presenti) - 1:
                            st.session_state.cal_month_idx += 1
                            st.rerun()
                            
                    anno_corr, mese_corr = mesi_presenti[st.session_state.cal_month_idx]
                    mesi_ita = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
                    nome_mese = mesi_ita[mese_corr]
                    col_m.markdown(f"<h3 style='text-align:center; color:#3B82F6; margin-top:0;'>{nome_mese} {anno_corr}</h3>", unsafe_allow_html=True)
                    
                    cal = calendar.Calendar(firstweekday=0)
                    month_days = cal.monthdatescalendar(anno_corr, mese_corr)
                    
                    giorni_sett = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
                    html_cal = "<div style='display:grid; grid-template-columns: repeat(7, 1fr); gap: 10px; max-width: 600px; margin: auto;'>"
                    for g in giorni_sett:
                        html_cal += f"<div style='text-align:center; font-weight:700; color:#8B949E;'>{g}</div>"
                        
                    for week in month_days:
                        for day in week:
                            if day.month != mese_corr:
                                html_cal += "<div style='visibility:hidden;'></div>"
                            else:
                                occ = dati_ricerca['Occupazione_%'] if day < data_libero else 0
                                if day < start_date or day > end_date: 
                                    bg_color = "#21262D"
                                elif day.weekday() >= 5: 
                                    bg_color = "#21262D"
                                elif occ == 0: 
                                    bg_color = "#EF4444"
                                elif occ < 100: 
                                    bg_color = "#F59E0B"
                                else: 
                                    bg_color = "#10B981"
                                    
                                html_cal += f"<div style='background-color:{bg_color}; height:60px; border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:16px; font-weight:bold; color:#FFF; box-shadow: 0 2px 5px rgba(0,0,0,0.2);'>{day.day}</div>"
                    
                    html_cal += "</div>"
                    st.markdown(html_cal, unsafe_allow_html=True)

        # ----------------------------------------
        # SOTTO-VISTA: Master Data
        # ----------------------------------------
        elif pagina_pm == "Master Data Risorse":
            st.markdown("<h1 class='gradient-title'>Infrastruttura Dati Principale</h1>", unsafe_allow_html=True)
            df_display = df.copy()
            df_display['Progetto_Corrente'] = df_display.apply(estrai_progetto_attuale, axis=1)
            df_display = df_display.drop(columns=['Esperienze'], errors='ignore')
            
            st.dataframe(
                df_display,
                column_config={
                    "Occupazione_%": st.column_config.ProgressColumn("Saturazione (%)", min_value=0, max_value=100, format="%d%%"),
                    "Costo_Giorno": st.column_config.NumberColumn("OPEX Unitario", format="€ %d"),
                    "Tariffa_Vendita": st.column_config.NumberColumn("Mark-up Target", format="€ %d")
                },
                hide_index=True, use_container_width=True
            )

# ==========================================
# VISTA 2: TALENT WORKSPACE (Ex Consulente IT)
# ==========================================
elif ruolo_utente == "Talent Workspace":
    if not st.session_state.it_logged_in:
        st.markdown("<h1 class='gradient-title'>Gateway di Autenticazione Personale</h1>", unsafe_allow_html=True)
        with st.form("login_it_form"):
            utente_selezionato = st.selectbox("Selettore Identità", df['Nome'].tolist())
            password_it = st.text_input("Codice Sicurezza", type="password", help="Codice Base: dev123")
            if st.form_submit_button("Accesso di Rete"):
                if password_it == "dev123":
                    st.session_state.it_logged_in = True
                    st.session_state.current_it_user = utente_selezionato
                    st.rerun()
                else: 
                    st.error("Handshake fallito. Codice non autorizzato.")
    else:
        st.markdown(f"<h1 class='gradient-title'>Area Operativa: {st.session_state.current_it_user}</h1>", unsafe_allow_html=True)
        if st.button("LOGOUT"):
            st.session_state.it_logged_in = False
            st.rerun()
            
        dati_utente = df[df['Nome'] == st.session_state.current_it_user].iloc[0]
        prog_att = estrai_progetto_attuale(dati_utente)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='kpi-card blue'><h3>Attributi Profilo</h3>", unsafe_allow_html=True)
            st.write(f"**Cluster Tecnico:** {dati_utente['Ruolo']}")
            st.write(f"**Inventario Skill:** {dati_utente['Skill']}")
            st.write(f"**Carico Operativo:** Saturazione {dati_utente['Occupazione_%']}% (Rif: **{prog_att}**)")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.subheader("Processo Espansione Skill")
            nuova_skill = st.text_input("Identificativo Framework (es. GraphQL):")
            if st.button("Sottoponi per Validazione"):
                if nuova_skill.strip():
                    st.session_state.pending_approvals.append({"ID": dati_utente['ID'], "Nome": dati_utente['Nome'], "Skill": nuova_skill.strip()})
                    st.success("Transazione inviata. Attesa validazione PM.")
        with c2:
            st.markdown("<div class='kpi-card orange'><h3>Richiesta Integrazione su Progetto</h3>", unsafe_allow_html=True)
            st.caption("Modulo di notifica disponibilità verso i centri decisionali.")
            with st.form("richiesta_alloc"):
                progetto_req = st.text_input("Codice Cliente / Progetto Target")
                disp_req = st.slider("Fattore di Carico Previsto (%)", 25, 100, 50, step=25)
                date_req = st.date_input("Timeline Stimata", value=(datetime.today(), datetime.today() + timedelta(days=30)))
                if st.form_submit_button("INVIA RICHIESTA"):
                    if len(date_req) == 2:
                        st.session_state.pending_allocations.append({
                            "ID": dati_utente['ID'], "Nome": dati_utente['Nome'], 
                            "Progetto": progetto_req, "Occupazione": disp_req, 
                            "Dal": date_req[0], "Al": date_req[1]
                        })
                        st.success("Payload trasmesso. Inserito in coda PM.")
                    else:
                        st.error("Errore Parsing: Compilare perimetro date completo.")
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# VISTA 3: TALENT MANAGEMENT (Ex Human Resources)
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

        # ----------------------------------------
        # SOTTO-VISTA: Homepage (Ex HR Analytics)
        # ----------------------------------------
        if pagina_hr == "Homepage":
            st.markdown("<h1 class='gradient-title'>Metriche Globali Risorse</h1>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='kpi-card blue'><h3>Headcount Aggregato</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='kpi-card orange'><h3>Indice Anagrafico Teorico</h3><h2>32 Anni</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='kpi-card green'><h3>Costo Base Ponderato</h3><h2>€ {df['Costo_Giorno'].mean():.0f}</h2></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Rapporto Classificazioni")
                df_sen = df['Seniority'].value_counts().reset_index()
                df_sen.columns = ['Seniority', 'Conteggio']
                fig1 = px.pie(df_sen, values='Conteggio', names='Seniority', hole=0.4, color_discrete_sequence=px.colors.sequential.Tealgrn)
                # Rimozione Legenda
                fig1 = applica_tema_plotly(fig1)
                fig1.update_layout(showlegend=False)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_chart2:
                st.subheader("Distribuzione Assorbimento per Ruoli")
                aree_disponibili = ["Cluster Globale"] + sorted(list(df['Macro_Area'].unique()))
                
                # Memoria Filtro Area
                saved_area = st.session_state.get('saved_hr_area', "Cluster Globale")
                idx_area = aree_disponibili.index(saved_area) if saved_area in aree_disponibili else 0
                area_selezionata = st.selectbox("Filtro di Contesto:", aree_disponibili, index=idx_area)
                st.session_state.saved_hr_area = area_selezionata
                
                df_ruoli = df if area_selezionata == "Cluster Globale" else df[df['Macro_Area'] == area_selezionata]
                df_ruoli = df_ruoli['Ruolo'].str.replace('Senior ', '').str.replace('Mid ', '').str.replace('Junior ', '').value_counts().reset_index()
                df_ruoli.columns = ['Ruolo', 'Conteggio']
                fig2 = px.bar(df_ruoli, x='Ruolo', y='Conteggio', color='Ruolo', color_discrete_sequence=px.colors.sequential.Blues_r)
                # Rimozione Legenda
                fig2 = applica_tema_plotly(fig2)
                fig2.update_layout(showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        # ----------------------------------------
        # SOTTO-VISTA: Onboarding Nuovo Assunto
        # ----------------------------------------
        elif pagina_hr == "Processo Onboarding":
            st.markdown("<h1 class='gradient-title'>Creazione Nuova Anagrafica</h1>", unsafe_allow_html=True)
            st.write("La transazione creerà un record istantaneo disponibile ai Project Manager.")
            
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
                        st.success(f"Log Output: Profilo {nuovo_nome} sincronizzato in Master Data.")
                    else:
                        st.error("Log Output: Dati obbligatori carenti. Blocco scrittura.")

        # ----------------------------------------
        # SOTTO-VISTA: Manutenzione e Promozioni
        # ----------------------------------------
        elif pagina_hr == "Manutenzione Inquadramenti":
            st.markdown("<h1 class='gradient-title'>Upgrade Livelli e Manutenzione</h1>", unsafe_allow_html=True)
            
            # Memoria Selettore Anagrafica HR
            options_nomi = df['Nome'].tolist()
            saved_hr_nome = st.session_state.get('saved_hr_manu_nome')
            idx_hr_nome = options_nomi.index(saved_hr_nome) if saved_hr_nome in options_nomi else 0
            
            nome_ricerca = st.selectbox("Record Input (Lookup):", options_nomi, index=idx_hr_nome)
            st.session_state.saved_hr_manu_nome = nome_ricerca
            
            if nome_ricerca:
                idx = df.index[df['Nome'] == nome_ricerca].tolist()[0]
                dati_attuali = df.iloc[idx]
                prog_att = estrai_progetto_attuale(dati_attuali)
                
                st.info(f"Monitor: Record attualmente impiegato su **{prog_att}** (Saturazione al {dati_attuali['Occupazione_%']}%)")
                
                with st.form("form_modifica_dipendente"):
                    st.subheader(f"Buffer Modifiche: {dati_attuali['Nome']}")
                    c1, c2 = st.columns(2)
                    
                    nuovo_nome = c1.text_input("Rettifica Nominativo", value=dati_attuali['Nome'])
                    
                    ruolo_attuale_puro = dati_attuali['Ruolo'].replace('Senior ', '').replace('Mid ', '').replace('Junior ', '')
                    ruoli_disponibili = ["Frontend Developer", "Backend Developer", "Fullstack Developer", "DevOps Engineer", "Data Scientist", "Data Analyst", "Project Manager", "Business Analyst"]
                    if ruolo_attuale_puro not in ruoli_disponibili:
                        ruoli_disponibili.append(ruolo_attuale_puro)
                    
                    index_sen = ["Junior", "Mid", "Senior"].index(dati_attuali['Seniority'])
                    nuova_sen = c1.selectbox("Cambio Gerarchico", ["Junior", "Mid", "Senior"], index=index_sen)
                    
                    index_ruolo = ruoli_disponibili.index(ruolo_attuale_puro)
                    nuovo_ruolo = c2.selectbox("Dominio Professionale", ruoli_disponibili, index=index_ruolo)
                    
                    nuove_skill = st.text_input("Aggiunta Competenze", value=dati_attuali['Skill'])
                    
                    c3, c4 = st.columns(2)
                    costo_gg = c3.number_input("Modifica OPEX Diretto (€)", min_value=50, max_value=2000, value=int(dati_attuali['Costo_Giorno']))
                    tariffa_vendita = c4.number_input("Modifica Mark-up Base (€)", min_value=50, max_value=3000, value=int(dati_attuali['Tariffa_Vendita']))
                    
                    if st.form_submit_button("Esegui Aggiornamento Profilo"):
                        st.session_state.df_risorse.at[idx, 'Nome'] = nuovo_nome
                        st.session_state.df_risorse.at[idx, 'Seniority'] = nuova_sen
                        st.session_state.df_risorse.at[idx, 'Ruolo'] = f"{nuova_sen} {nuovo_ruolo}"
                        st.session_state.df_risorse.at[idx, 'Skill'] = nuove_skill
                        st.session_state.df_risorse.at[idx, 'Costo_Giorno'] = costo_gg
                        st.session_state.df_risorse.at[idx, 'Tariffa_Vendita'] = tariffa_vendita
                        st.success(f"Update Eseguito: I nuovi parametri per {nuovo_nome} sono validi.")
                        st.rerun()

        # ----------------------------------------
        # SOTTO-VISTA: Zucchetti Sync
        # ----------------------------------------
        elif pagina_hr == "Interfaccia ERP (Zucchetti)":
            st.markdown("<h1 class='gradient-title'>Ponte di Trasmissione ERP Software Paghe</h1>", unsafe_allow_html=True)
            st.info("Protocollo di interscambio asincrono per l'allineamento dei Database Centrali.")
            
            st.subheader("Fase 1: Estrazione Dati per Inbound ERP")
            df_export = df.drop(columns=['Esperienze', 'Macro_Area'], errors='ignore')
            csv_export = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("Genera Pacchetto CSV (.csv)", data=csv_export, file_name='export_hr_zucchetti.csv', mime='text/csv')
            
            st.markdown("---")
            st.subheader("Fase 2: Importazione Dati da Outbound ERP")
            uploaded_file = st.file_uploader("Upload Tracciato (.csv o .xlsx)", type=['csv', 'xlsx'])
            
            if uploaded_file is not None:
                with st.spinner("Decodifica buffer in corso..."):
                    if uploaded_file.name.endswith('.csv'):
                        new_df = pd.read_csv(uploaded_file)
                    else:
                        new_df = pd.read_excel(uploaded_file)
                    st.success("Codice di Ritorno 200: Lettura eseguita. Pronti per unificazione tabella.")
                    st.dataframe(new_df.head(5))

        # ----------------------------------------
        # SOTTO-VISTA: Database Dipendenti
        # ----------------------------------------
        elif pagina_hr == "Archivio Generale":
            st.markdown("<h1 class='gradient-title'>Ispezione Diretta Records</h1>", unsafe_allow_html=True)
            df_display = df.copy()
            df_display['Istanza_Corrente'] = df_display.apply(estrai_progetto_attuale, axis=1)
            df_display = df_display.drop(columns=['Esperienze', 'Macro_Area'], errors='ignore')
            
            st.dataframe(
                df_display,
                column_config={
                    "Occupazione_%": st.column_config.ProgressColumn("Indice Occupazione", min_value=0, max_value=100, format="%d%%"),
                    "Costo_Giorno": st.column_config.NumberColumn("Tariffario (€)", format="€ %d")
                },
                hide_index=True, use_container_width=True
            )


# ==========================================
# 4. COMPONENTE COPILOT AI (WIDGET INFERIORE)
# ==========================================
if (st.session_state.pm_logged_in or st.session_state.hr_logged_in):
    # Spaziatura e linea divisoria
    st.sidebar.markdown("<br><br><br><hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
    
    with st.sidebar.popover("Terminale Copilot AI", use_container_width=True):
        if st.session_state.groq_api_key and st.session_state.groq_api_key.startswith("gsk_"):
            st.caption("Stato Nodo: **Llama-3 LLM (Attivo)**")
        else:
            st.caption("Stato Nodo: **Regex Fallback (Attivo)**")
            
        for msg in st.session_state.chat_msgs:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        if st.session_state.bot_action:
            act = st.session_state.bot_action
            st.info(act['desc'])
            
            if act['type'] == 'alloca':
                with st.form("form_bot_conferma"):
                    c1, c2 = st.columns(2)
                    nuovo_cliente = c1.text_input("Tag Commessa", value=act['cliente'])
                    nuova_perc = c2.number_input("Parametro Occupazione %", min_value=0, max_value=100, value=act['perc'])
                    date_range = st.date_input("Restrizione Temporale", value=(datetime.today(), datetime.today() + timedelta(days=30)))
                    
                    c_btn1, c_btn2 = st.columns(2)
                    submit_bot = c_btn1.form_submit_button("Autorizza Transazione")
                    cancel_bot = c_btn2.form_submit_button("Sospendi")
                    
                    if submit_bot:
                        if len(date_range) == 2:
                            act['cliente'] = nuovo_cliente
                            act['perc'] = nuova_perc
                            act['end_date'] = date_range[1]
                            esegui_azione_chatbot(act)
                            st.rerun()
                        else:
                            st.error("Errore Sintassi: Data di termine necessaria.")
                    if cancel_bot:
                        st.session_state.bot_action = None
                        st.session_state.chat_msgs.append({"role": "assistant", "content": "Transazione abortita."})
                        st.rerun()
            else:
                col_ok, col_ko = st.columns(2)
                if col_ok.button("Autorizza Transazione"):
                    esegui_azione_chatbot(act)
                    st.rerun()
                if col_ko.button("Sospendi"):
                    st.session_state.bot_action = None
                    st.session_state.chat_msgs.append({"role": "assistant", "content": "Transazione abortita."})
                    st.rerun()

        if prompt := st.chat_input("Esegui istruzione di sistema..."):
            st.session_state.chat_msgs.append({"role": "user", "content": prompt})
            with st.spinner("Analisi sintattica in corso..."):
                action_dict, error_msg = parse_chatbot_intent_llm(prompt, st.session_state.df_risorse, st.session_state.groq_api_key)
            
            if error_msg:
                st.session_state.chat_msgs.append({"role": "assistant", "content": error_msg})
            else:
                st.session_state.bot_action = action_dict
                st.session_state.chat_msgs.append({"role": "assistant", "content": "Preparazione Payload. Attendere conferma operatore:"})
            st.rerun()

    with st.sidebar.expander("Configurazione Root Backend AI"):
        st.write("Iniezione chiave per motore LLM Llama-3.")
        api_key = st.text_input("Parametro Groq API Key (gsk_...):", value=st.session_state.groq_api_key, type="password")
        if st.button("Forza Aggiornamento"):
            st.session_state.groq_api_key = api_key
            st.success("Parametri salvati sul nodo.")
