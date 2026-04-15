import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import requests
import re

# ==========================================
# 1. INIZIALIZZAZIONE DATI E SESSIONI
# ==========================================
st.set_page_config(page_title="AI Resource Manager", layout="wide")

@st.cache_data
def genera_database():
    nomi = ["Marco", "Giulia", "Luca", "Anna", "Matteo", "Sofia", "Andrea", "Martina", "Alessandro", "Chiara",
            "Davide", "Sara", "Lorenzo", "Francesca", "Simone", "Elena", "Gabriele", "Valentina", "Emanuele", "Silvia",
            "Riccardo", "Laura", "Federico", "Alessia", "Stefano", "Giorgia", "Daniele", "Roberta", "Michele", "Ilaria",
            "Tommaso", "Elisa", "Antonio", "Paola", "Giovanni", "Serena", "Roberto", "Caterina", "Francesco", "Marta"]
    
    ruoli_skills = [
        ("Frontend Developer", ["React", "Vue", "TypeScript", "HTML/CSS"]),
        ("Backend Developer", ["Node.js", "Python", "Java", "Go", "C#"]),
        ("Fullstack Developer", ["React", "Node.js", "Python", "TypeScript"]),
        ("DevOps Engineer", ["AWS", "Docker", "Kubernetes", "CI/CD", "Terraform"]),
        ("Data Scientist", ["Python", "Machine Learning", "SQL", "Pandas"])
    ]
    
    db = []
    for i, nome in enumerate(nomi):
        ruolo, skills_possibili = random.choice(ruoli_skills)
        skills = random.sample(skills_possibili, k=random.randint(2, len(skills_possibili)))
        seniority = random.choice(["Junior", "Mid", "Senior"])
        costo_base = {"Junior": 150, "Mid": 250, "Senior": 350}[seniority]
        occupazione = random.choice([0, 0, 50, 100])
        # Simuliamo da quando sarà libero. Se occupato a 0%, è libero oggi.
        giorni_offset = random.randint(5, 30) if occupazione > 0 else 0
        disp_dal = (datetime.now() + timedelta(days=giorni_offset)).strftime("%Y-%m-%d")
        
        db.append({
            "ID": f"RES-{1000+i}",
            "Nome": nome,
            "Ruolo": f"{seniority} {ruolo}",
            "Skill": ", ".join(skills),
            "Costo_Giorno": costo_base,
            "Occupazione_%": occupazione,
            "Disponibile_dal": disp_dal
        })
    return pd.DataFrame(db)

# Inizializziamo il DB e le code in sessione
if "df_risorse" not in st.session_state:
    st.session_state.df_risorse = genera_database()
if "pending_approvals" not in st.session_state:
    st.session_state.pending_approvals = []

if "pm_logged_in" not in st.session_state:
    st.session_state.pm_logged_in = False
if "it_logged_in" not in st.session_state:
    st.session_state.it_logged_in = False
if "current_it_user" not in st.session_state:
    st.session_state.current_it_user = None

df_risorse = st.session_state.df_risorse

# ==========================================
# 2. MOTORE SMART
# ==========================================
def analizza_testo(testo):
    testo_lower = testo.lower()
    competenze_trovate = []
    regole = {
        "react": ("React", 15), "vue": ("Vue", 12), "angular": ("Angular", 15),
        "node": ("Node.js", 20), "python": ("Python", 18), "java ": ("Java", 25),
        "aws": ("AWS", 10), "docker": ("Docker", 5), "kubernetes": ("Kubernetes", 10),
        "machine learning": ("Machine Learning", 20), "sql": ("SQL", 8)
    }
    
    fasi = []
    totale_giorni = 0
    for key, (skill, giorni) in regole.items():
        if key in testo_lower:
            competenze_trovate.append(skill)
            fasi.append({"Fase": f"Sviluppo {skill}", "Skill": skill, "Giorni": giorni})
            totale_giorni += giorni
            
    if not fasi:
        fasi = [{"Fase": "Analisi e Sviluppo Base", "Skill": "Node.js", "Giorni": 10}]
        totale_giorni = 10
        competenze_trovate = ["Node.js"]
        
    return fasi, totale_giorni, competenze_trovate

def leggi_github_readme(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com") + "/main/README.md"
        response = requests.get(raw_url)
        if response.status_code == 200:
            return response.text
        else:
            raw_url_master = url.replace("github.com", "raw.githubusercontent.com") + "/master/README.md"
            resp2 = requests.get(raw_url_master)
            if resp2.status_code == 200: return resp2.text
            return "Errore: README non trovato."
    except Exception as e:
        return str(e)


# ==========================================
# 3. SIDEBAR (NAVIGAZIONE)
# ==========================================
st.sidebar.title("🔐 Accesso Sistema")
ruolo_utente = st.sidebar.radio("Scegli il tuo ruolo:", ["Project Manager", "Consulente"])

st.sidebar.markdown("---")
st.sidebar.write("**Metriche Aziendali**")
st.sidebar.write(f"👥 Totale Risorse: {len(st.session_state.df_risorse)}")
risorse_libere_count = len(st.session_state.df_risorse[st.session_state.df_risorse['Occupazione_%'] == 0])
st.sidebar.write(f"🟢 Risorse Libere: {risorse_libere_count}")

if ruolo_utente == "Consulente" and st.session_state.pm_logged_in:
    st.session_state.pm_logged_in = False
if ruolo_utente == "Project Manager" and st.session_state.it_logged_in:
    st.session_state.it_logged_in = False
    st.session_state.current_it_user = None


# ==========================================
# VISTA 1: PROFILO DEL CONSULENTE
# ==========================================
if ruolo_utente == "Consulente":
    if not st.session_state.it_logged_in:
        st.title("🔒 Accesso Area Personale")
        st.info("Seleziona il tuo nome dal database e inserisci la password aziendale.")
        with st.form("login_it_form"):
            utente_selezionato = st.selectbox("Chi sei?", st.session_state.df_risorse['Nome'].tolist())
            password_it = st.text_input("Password", type="password")
            submitted_it = st.form_submit_button("Accedi")
            
            if submitted_it:
                if password_it == "dev123":
                    st.session_state.it_logged_in = True
                    st.session_state.current_it_user = utente_selezionato
                    st.rerun()
                else:
                    st.error("Password errata. Usa la password condivisa: dev123")
    else:
        utente_loggato = st.session_state.current_it_user
        st.title(f"👤 Area Personale di {utente_loggato}")
        
        if st.button("Esci (Logout)"):
            st.session_state.it_logged_in = False
            st.session_state.current_it_user = None
            st.rerun()
            
        st.markdown("---")
        dati_utente = st.session_state.df_risorse[st.session_state.df_risorse['Nome'] == utente_loggato].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Ruolo Attuale:** {dati_utente['Ruolo']}")
            st.write(f"**Skill Validate:** {dati_utente['Skill']}")
            
            st.markdown("---")
            nuova_skill = st.text_input("Aggiungi competenza (es. GraphQL):")
            if st.button("Invia al PM per validazione"):
                if nuova_skill.strip():
                    st.session_state.pending_approvals.append({
                        "ID": dati_utente['ID'], "Nome": dati_utente['Nome'], "Skill": nuova_skill.strip()
                    })
                    st.success("Richiesta inviata al PM!")
                else:
                    st.warning("Inserisci una competenza.")
                
        with col2:
            st.write(f"**Occupazione Attuale:** {dati_utente['Occupazione_%']}%")
            st.write(f"**Disponibile dal:** {dati_utente['Disponibile_dal']}")
            
            nuova_disp = st.slider("Aggiorna occupazione prossimo mese (%)", 0, 100, int(dati_utente['Occupazione_%']), step=25)
            if st.button("Salva Disponibilità"):
                idx = st.session_state.df_risorse.index[st.session_state.df_risorse['Nome'] == utente_loggato].tolist()[0]
                st.session_state.df_risorse.at[idx, 'Occupazione_%'] = nuova_disp
                # Se si mette a 0%, aggiorniamo la data a oggi
                if nuova_disp == 0:
                    st.session_state.df_risorse.at[idx, 'Disponibile_dal'] = datetime.now().strftime("%Y-%m-%d")
                st.success("Calendario aggiornato.")
                st.rerun()


# ==========================================
# VISTA 2: PANNELLO DEL PROJECT MANAGER
# ==========================================
elif ruolo_utente == "Project Manager":
    if not st.session_state.pm_logged_in:
        st.title("🔒 Accesso Area Riservata PM")
        with st.form("login_pm_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted_pm = st.form_submit_button("Accedi")
            
            if submitted_pm:
                if username == "admin" and password == "admin123":
                    st.session_state.pm_logged_in = True
                    st.rerun()
                else:
                    st.error("Credenziali errate. Usa admin / admin123")
    else:
        st.title("🤖 AI Resource Manager - Dashboard PM")
        
        if st.button("Esci (Logout)"):
            st.session_state.pm_logged_in = False
            st.rerun()

        # ------------------------------------------------
        # ALERT: RISORSE IN BENCH (PANCHINA)
        # ------------------------------------------------
        risorse_libere = st.session_state.df_risorse[st.session_state.df_risorse['Occupazione_%'] == 0]['Nome'].tolist()
        if risorse_libere:
            with st.expander(f"🟢 **Alert:** Hai {len(risorse_libere)} risorse attualmente in Bench (Libere al 100%)", expanded=True):
                st.write(", ".join(risorse_libere))
                st.caption("Queste risorse sono pronte per essere allocate su nuovi progetti oggi stesso.")
        # ------------------------------------------------

        # NOTIFICHE APPROVAZIONE SKILL
        if len(st.session_state.pending_approvals) > 0:
            st.warning(f"🔔 Hai {len(st.session_state.pending_approvals)} competenze in attesa di validazione!")
            with st.expander("Gestisci Approvazioni", expanded=False):
                pending_list = list(st.session_state.pending_approvals)
                for i, req in enumerate(pending_list):
                    col_n, col_action = st.columns([7, 3])
                    col_n.write(f"👤 **{req['Nome']}** vuole aggiungere: **{req['Skill']}**")
                    with col_action:
                        b1, b2 = st.columns(2)
                        if b1.button("✅", key=f"ok_{i}"):
                            idx = st.session_state.df_risorse.index[st.session_state.df_risorse['ID'] == req['ID']].tolist()[0]
                            st.session_state.df_risorse.at[idx, 'Skill'] += f", {req['Skill']}"
                            st.session_state.pending_approvals.pop(i)
                            st.rerun()
                        if b2.button("❌", key=f"ko_{i}"):
                            st.session_state.pending_approvals.pop(i)
                            st.rerun()

        st.markdown("---")

        # ------------------------------------------------
        # MACRO-SCHEDE DELLA DASHBOARD PM
        # ------------------------------------------------
        tab_ai, tab_risorse, tab_db = st.tabs(["🚀 AI Scoping & Staffing", "📊 Analisi Profilo Singolo", "👁️ Esplora Database"])

        # TAB 1: MOTORE AI
        with tab_ai:
            sub_tab1, sub_tab2 = st.tabs(["📝 Testo Manuale", "🔗 GitHub URL"])
            testo_da_analizzare = ""
            
            with sub_tab1:
                req_manuali = st.text_area("Incolla i requisiti del progetto:", height=100)
                if req_manuali: testo_da_analizzare = req_manuali
            with sub_tab2:
                url_github = st.text_input("Inserisci URL GitHub Pubblico:")
                if st.button("Scarica README"):
                    with st.spinner("Download..."):
                        testo_da_analizzare = leggi_github_readme(url_github)
                        st.success("Scaricato! Procedi alla stima.")

            if st.button("🚀 Genera Stima e Cerca Team", type="primary", use_container_width=True):
                if not testo_da_analizzare:
                    st.warning("Fornisci dei requisiti.")
                else:
                    fasi, giorni_tot, skill_richieste = analizza_testo(testo_da_analizzare)
                    
                    st.subheader("📊 Analisi e Stima (Smart Engine)")
                    col_s1, col_s2 = st.columns(2)
                    with col_s1: st.dataframe(pd.DataFrame(fasi))
                    with col_s2: 
                        st.metric("Giorni-Uomo Totali", giorni_tot)
                        st.write(f"**Skill trovate:** {', '.join(skill_richieste)}")
                    
                    st.subheader("👥 Proposta di Allocazione")
                    team_proposto, costo_totale = [], 0
                    for skill in skill_richieste:
                        mask_skill = st.session_state.df_risorse['Skill'].str.contains(skill, flags=re.IGNORECASE, regex=True)
                        mask_liberi = st.session_state.df_risorse['Occupazione_%'] < 100
                        candidati = st.session_state.df_risorse[mask_skill & mask_liberi]
                        if not candidati.empty:
                            scelto = candidati.iloc[0]
                            team_proposto.append({"Nome": scelto['Nome'], "Ruolo": f"Specialista {skill}", "Costo/gg": scelto['Costo_Giorno']})
                            costo_totale += next((item['Giorni'] for item in fasi if item["Skill"] == skill), 0) * scelto['Costo_Giorno']
                        else:
                            team_proposto.append({"Nome": "NON TROVATO", "Ruolo": skill, "Costo/gg": 0})
                            
                    st.table(pd.DataFrame(team_proposto))
                    st.metric("💰 Costo Interno Progetto", f"€ {costo_totale}")

        # TAB 2: ANALISI PROFILO E GRAFICO
        with tab_risorse:
            st.subheader("Dettaglio Risorsa e Grafico di Allocazione")
            
            # Selettore Risorsa
            nome_ricerca = st.selectbox("Cerca un consulente per vederne i dettagli:", st.session_state.df_risorse['Nome'].tolist())
            dati_ricerca = st.session_state.df_risorse[st.session_state.df_risorse['Nome'] == nome_ricerca].iloc[0]
            
            # Riassunto
            c1, c2, c3 = st.columns(3)
            c1.info(f"**Ruolo:** {dati_ricerca['Ruolo']}\n\n**Costo:** {dati_ricerca['Costo_Giorno']} €/gg")
            c2.success(f"**Competenze (Skills):**\n\n{dati_ricerca['Skill']}")
            c3.warning(f"**Situazione Attuale:**\n\nOccupato al {dati_ricerca['Occupazione_%']}%\n\nLibero dal: {dati_ricerca['Disponibile_dal']}")
            
            st.markdown("#### Previsione di Occupazione")
            # Calendarietto a comparsa (Range di date)
            oggi = datetime.today().date()
            default_end = oggi + timedelta(days=60) # Default 2 mesi
            date_range = st.date_input("Seleziona periodo di analisi", value=(oggi, default_end))
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                # Costruiamo i dati finti per il grafico nel periodo selezionato
                # Logica: la risorsa è occupata alla sua % attuale fino a "Disponibile_dal", dopodiché va a 0%
                data_libero = datetime.strptime(dati_ricerca['Disponibile_dal'], "%Y-%m-%d").date()
                
                date_list = pd.date_range(start=start_date, end=end_date)
                occupazioni = []
                for d in date_list:
                    if d.date() < data_libero:
                        occupazioni.append(dati_ricerca['Occupazione_%'])
                    else:
                        occupazioni.append(0) # Dal giorno di disponibilità in poi è libero (0%)
                        
                # Creiamo il dataframe per il grafico
                df_chart = pd.DataFrame({"Data": date_list, "Allocazione %": occupazioni}).set_index("Data")
                
                # Grafico nativo di Streamlit (Area chart è perfetto per far vedere l'ingombro)
                st.area_chart(df_chart, height=200, color="#FF4B4B")
            else:
                st.info("Seleziona una data di inizio e una di fine dal calendario per vedere il grafico.")

        # TAB 3: TUTTO IL DATABASE
        with tab_db:
            st.dataframe(st.session_state.df_risorse, use_container_width=True)
