import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import requests
import re

# ==========================================
# 1. INIZIALIZZAZIONE DATI E SESSIONI
# ==========================================
st.set_page_config(page_title="AI Resource Manager", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def genera_database():
    nomi = ["Marco", "Giulia", "Luca", "Anna", "Matteo", "Sofia", "Andrea", "Martina", "Alessandro", "Chiara",
            "Davide", "Sara", "Lorenzo", "Francesca", "Simone", "Elena", "Gabriele", "Valentina", "Emanuele", "Silvia",
            "Riccardo", "Laura", "Federico", "Alessia", "Stefano", "Giorgia", "Daniele", "Roberta", "Michele", "Ilaria",
            "Tommaso", "Elisa", "Antonio", "Paola", "Giovanni", "Serena", "Roberto", "Caterina", "Francesco", "Marta"]
    
    ruoli_skills = [
        ("Frontend Developer", ["React", "Vue", "TypeScript", "HTML/CSS"]),
        ("Backend Developer", ["Node.js", "Python", "Java", "Go", "C#"]),
        ("Fullstack Developer", ["React", "Node.js", "Python", "TypeScript", "SQL"]),
        ("DevOps Engineer", ["AWS", "Docker", "Kubernetes", "CI/CD", "Terraform"]),
        ("Data Scientist", ["Python", "Machine Learning", "SQL", "Pandas"])
    ]
    
    clienti_italiani = ["Enel", "TIM", "Poste Italiane", "Intesa Sanpaolo", "Unicredit", "Ferrari", "Eni", "Leonardo", "Ferrovie dello Stato", "Pirelli", "Barilla", "Luxottica", "Generali", "Enav"]
    tipi_progetto = ["Piattaforma e-commerce", "App Mobile B2C", "Gestionale Interno ERP", "Dashboard IoT", "Sistema di Pagamenti", "Migrazione in Cloud", "Motore di Analisi Dati"]
    
    db = []
    for i, nome in enumerate(nomi):
        ruolo, skills_possibili = random.choice(ruoli_skills)
        skills = random.sample(skills_possibili, k=random.randint(2, len(skills_possibili)))
        seniority = random.choice(["Junior", "Mid", "Senior"])
        costo_base = {"Junior": 150, "Mid": 250, "Senior": 350}[seniority]
        occupazione = random.choice([0, 0, 50, 100])
        giorni_offset = random.randint(5, 30) if occupazione > 0 else 0
        disp_dal = (datetime.now() + timedelta(days=giorni_offset)).strftime("%Y-%m-%d")
        
        # Generazione Storico Esperienze (Clienti Reali)
        esperienze = []
        num_progetti = {"Junior": 1, "Mid": 2, "Senior": 3}[seniority]
        for _ in range(num_progetti):
            tech_usate = random.sample(skills, k=random.randint(1, len(skills)))
            esperienze.append({
                "Cliente": random.choice(clienti_italiani),
                "Progetto": random.choice(tipi_progetto),
                "Tecnologie_Usate": tech_usate
            })
        
        db.append({
            "ID": f"RES-{1000+i}",
            "Nome": nome,
            "Ruolo": f"{seniority} {ruolo}",
            "Seniority": seniority,
            "Skill": ", ".join(skills),
            "Esperienze": esperienze, # Lista di dizionari con i progetti passati
            "Costo_Giorno": costo_base,
            "Occupazione_%": occupazione,
            "Disponibile_dal": disp_dal
        })
    return pd.DataFrame(db)

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

# ==========================================
# 2. MOTORE SMART E AI
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
    
    fasi, totale_giorni = [], 0
    for key, (skill, giorni) in regole.items():
        if key in testo_lower:
            competenze_trovate.append(skill)
            fasi.append({"Fase": f"Sviluppo {skill}", "Skill": skill, "Giorni": giorni})
            totale_giorni += giorni
            
    if not fasi:
        fasi = [{"Fase": "Analisi e Setup", "Skill": "Node.js", "Giorni": 10}]
        totale_giorni = 10
        competenze_trovate = ["Node.js"]
        
    return fasi, totale_giorni, competenze_trovate

def leggi_github_readme(url):
    try:
        raw_url = url.replace("github.com", "raw.githubusercontent.com") + "/main/README.md"
        response = requests.get(raw_url)
        if response.status_code == 200: return response.text
        raw_url_master = url.replace("github.com", "raw.githubusercontent.com") + "/master/README.md"
        resp2 = requests.get(raw_url_master)
        if resp2.status_code == 200: return resp2.text
        return "Errore: README non trovato."
    except Exception as e: return str(e)


# ==========================================
# 3. SIDEBAR BASE
# ==========================================
st.sidebar.title("🔐 Accesso Sistema")
ruolo_utente = st.sidebar.radio("Scegli il tuo ruolo:", ["Project Manager", "Consulente"])

# Metriche globali in Sidebar
st.sidebar.markdown("---")
st.sidebar.write("**Metriche Aziendali Globali**")
st.sidebar.write(f"👥 Totale Risorse: {len(st.session_state.df_risorse)}")
risorse_libere_count = len(st.session_state.df_risorse[st.session_state.df_risorse['Occupazione_%'] == 0])
st.sidebar.write(f"🟢 Risorse Libere (Bench): {risorse_libere_count}")

# Logout incrociato
if ruolo_utente == "Consulente" and st.session_state.pm_logged_in: st.session_state.pm_logged_in = False
if ruolo_utente == "Project Manager" and st.session_state.it_logged_in: 
    st.session_state.it_logged_in = False
    st.session_state.current_it_user = None


# ==========================================
# VISTA 1: CONSULENTE
# ==========================================
if ruolo_utente == "Consulente":
    if not st.session_state.it_logged_in:
        st.title("🔒 Accesso Area Personale")
        with st.form("login_it_form"):
            utente_selezionato = st.selectbox("Chi sei?", st.session_state.df_risorse['Nome'].tolist())
            password_it = st.text_input("Password", type="password", help="Password di default: dev123")
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
            
        st.markdown("---")
        dati_utente = st.session_state.df_risorse[st.session_state.df_risorse['Nome'] == st.session_state.current_it_user].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Qualifica:** {dati_utente['Ruolo']}")
            st.write(f"**Skill Validate:** {dati_utente['Skill']}")
            st.markdown("---")
            nuova_skill = st.text_input("Aggiungi competenza da validare:")
            if st.button("Invia al PM"):
                if nuova_skill.strip():
                    st.session_state.pending_approvals.append({"ID": dati_utente['ID'], "Nome": dati_utente['Nome'], "Skill": nuova_skill.strip()})
                    st.success("Richiesta inviata!")
        with c2:
            st.write(f"**Stato:** Occupato al {dati_utente['Occupazione_%']}%")
            st.write(f"**Libero dal:** {dati_utente['Disponibile_dal']}")
            nuova_disp = st.slider("Aggiorna occupazione (%)", 0, 100, int(dati_utente['Occupazione_%']), step=25)
            if st.button("Salva Calendario"):
                idx = st.session_state.df_risorse.index[st.session_state.df_risorse['Nome'] == st.session_state.current_it_user].tolist()[0]
                st.session_state.df_risorse.at[idx, 'Occupazione_%'] = nuova_disp
                if nuova_disp == 0: st.session_state.df_risorse.at[idx, 'Disponibile_dal'] = datetime.now().strftime("%Y-%m-%d")
                st.success("Aggiornato.")
                st.rerun()

# ==========================================
# VISTA 2: PROJECT MANAGER
# ==========================================
elif ruolo_utente == "Project Manager":
    if not st.session_state.pm_logged_in:
        st.title("🔒 Accesso PM")
        with st.form("login_pm_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password", help="Usa admin / admin123")
            if st.form_submit_button("Accedi"):
                if username == "admin" and password == "admin123":
                    st.session_state.pm_logged_in = True
                    st.rerun()
                else: st.error("Credenziali errate.")
    else:
        # MENU LATERALE PM
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ Navigazione PM")
        pagina_pm = st.sidebar.radio("Vai a:", [
            "🏠 Homepage & Alert", 
            "🚀 Scoping & Staffing AI", 
            "👤 Analisi Profili & Assegnazioni", 
            "🗄️ Master Data (Database)"
        ])
        
        if st.sidebar.button("🚪 Esci (Logout)"):
            st.session_state.pm_logged_in = False
            st.rerun()

        # =====================================
        # PAGINA 1: HOMEPAGE
        # =====================================
        if pagina_pm == "🏠 Homepage & Alert":
            st.title("Centro di Controllo Manageriale")
            st.info("Benvenuto. Da qui puoi monitorare lo stato di salute del team, approvare competenze e verificare le risorse in panchina.")
            
            # Alert Bench
            risorse_libere = st.session_state.df_risorse[st.session_state.df_risorse['Occupazione_%'] == 0]
            if not risorse_libere.empty:
                st.error(f"🚨 **ATTENZIONE:** Ci sono {len(risorse_libere)} risorse in Bench (In attesa di allocazione a costo passivo per l'azienda).")
                with st.expander("Vedi lista risorse ferme"):
                    for _, r in risorse_libere.iterrows():
                        st.write(f"- **{r['Nome']}** ({r['Ruolo']}) - Costo: {r['Costo_Giorno']}€/gg")
            
            # Approvals
            if len(st.session_state.pending_approvals) > 0:
                st.warning(f"🔔 Hai {len(st.session_state.pending_approvals)} competenze da validare.")
                with st.expander("Apri Pannello Validazione", expanded=True):
                    for i, req in enumerate(list(st.session_state.pending_approvals)):
                        col_n, col_action = st.columns([7, 3])
                        col_n.write(f"👤 **{req['Nome']}** ha studiato: **{req['Skill']}**")
                        with col_action:
                            b1, b2 = st.columns(2)
                            if b1.button("✅ Approva", key=f"ok_{i}"):
                                idx = st.session_state.df_risorse.index[st.session_state.df_risorse['ID'] == req['ID']].tolist()[0]
                                st.session_state.df_risorse.at[idx, 'Skill'] += f", {req['Skill']}"
                                st.session_state.pending_approvals.pop(i)
                                st.rerun()
                            if b2.button("❌ Rifiuta", key=f"ko_{i}"):
                                st.session_state.pending_approvals.pop(i)
                                st.rerun()

        # =====================================
        # PAGINA 2: SCOPING & STAFFING
        # =====================================
        elif pagina_pm == "🚀 Scoping & Staffing AI":
            st.title("🤖 Motore di Allocazione Intelligente")
            st.write("Incolla le specifiche del cliente o analizza un repository. L'AI cercherà le risorse basandosi sulle loro **Skill** e sulle **Esperienze passate**.")
            
            testo_da_analizzare = st.text_area("Incolla qui i requisiti (oppure l'URL GitHub):", height=150)
            if testo_da_analizzare.startswith("http"):
                if st.button("Scarica da GitHub"): testo_da_analizzare = leggi_github_readme(testo_da_analizzare)

            if st.button("Genera Team Ottimale", type="primary"):
                fasi, giorni_tot, skill_richieste = analizza_testo(testo_da_analizzare)
                st.subheader("WBS e Stima Tempi")
                st.dataframe(pd.DataFrame(fasi), use_container_width=True)
                
                st.subheader("👥 Il Team Consigliato dall'AI")
                team_proposto, costo_totale = [], 0
                
                for skill in skill_richieste:
                    mask_liberi = st.session_state.df_risorse['Occupazione_%'] < 100
                    candidati = st.session_state.df_risorse[mask_liberi]
                    
                    match_trovato = False
                    # Cerchiamo chi ha la skill O l'ha usata in un progetto passato
                    for _, risorsa in candidati.iterrows():
                        ha_skill = skill.lower() in risorsa['Skill'].lower()
                        exp_rilevante = ""
                        for exp in risorsa['Esperienze']:
                            if any(skill.lower() in t.lower() for t in exp['Tecnologie_Usate']):
                                exp_rilevante = f"Ha già usato {skill} nel progetto per {exp['Cliente']}"
                                ha_skill = True
                        
                        if ha_skill:
                            team_proposto.append({
                                "Nome": risorsa['Nome'],
                                "Ruolo Coperto": f"Esperto {skill}",
                                "Motivazione AI": exp_rilevante if exp_rilevante else f"Certificato internamente per {skill}",
                                "Costo Giornaliero": f"€ {risorsa['Costo_Giorno']}"
                            })
                            giorni_skill = next((item['Giorni'] for item in fasi if item["Skill"] == skill), 0)
                            costo_totale += (giorni_skill * risorsa['Costo_Giorno'])
                            match_trovato = True
                            break # Trovata una persona, passiamo alla prossima skill
                            
                    if not match_trovato:
                        team_proposto.append({"Nome": "NESSUNO DISPONIBILE", "Ruolo Coperto": skill, "Motivazione AI": "Nessuna risorsa libera con questa competenza", "Costo Giornaliero": "-"})

                st.table(pd.DataFrame(team_proposto))
                st.metric("💰 Costo Interno Progetto", f"€ {costo_totale}")

        # =====================================
        # PAGINA 3: ANALISI SINGOLO E GRAFICO
        # =====================================
        elif pagina_pm == "👤 Analisi Profili & Assegnazioni":
            st.title("Indagine e Disponibilità Risorse")
            st.write("Filtra per seniority, analizza il curriculum storico dei progetti e verifica l'ingombro a calendario.")
            
            c_filtro1, c_filtro2 = st.columns(2)
            seniority_scelta = c_filtro1.selectbox("1. Filtra per Livello (Seniority):", ["Tutti", "Senior", "Mid", "Junior"])
            
            df_filtrato = st.session_state.df_risorse
            if seniority_scelta != "Tutti": df_filtrato = df_filtrato[df_filtrato['Seniority'] == seniority_scelta]
            
            nome_ricerca = c_filtro2.selectbox("2. Seleziona Consulente:", df_filtrato['Nome'].tolist())
            if nome_ricerca:
                dati_ricerca = df_filtrato[df_filtrato['Nome'] == nome_ricerca].iloc[0]
                
                c1, c2, c3 = st.columns(3)
                c1.info(f"**Qualifica:** {dati_ricerca['Ruolo']}\n\n**Tariffa:** {dati_ricerca['Costo_Giorno']} €/gg")
                c2.success(f"**Hard Skills:**\n\n{dati_ricerca['Skill']}")
                c3.warning(f"**Stato Attuale:**\n\nOccupato {dati_ricerca['Occupazione_%']}%\n\nLibero dal: {dati_ricerca['Disponibile_dal']}")
                
                st.markdown("---")
                col_storico, col_grafico = st.columns([1, 1])
                
                with col_storico:
                    st.subheader("📚 Storico Progetti (Clienti Reali)")
                    for exp in dati_ricerca['Esperienze']:
                        with st.container():
                            st.markdown(f"🏢 **Cliente:** {exp['Cliente']}")
                            st.markdown(f"💻 **Progetto:** {exp['Progetto']}")
                            st.markdown(f"⚙️ **Tech:** {', '.join(exp['Tecnologie_Usate'])}")
                            st.divider()

                with col_grafico:
                    st.subheader("📅 Previsione di Occupazione")
                    oggi = datetime.today().date()
                    date_range = st.date_input("Analizza periodo:", value=(oggi, oggi + timedelta(days=60)))
                    
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        data_libero = datetime.strptime(dati_ricerca['Disponibile_dal'], "%Y-%m-%d").date()
                        date_list = pd.date_range(start=start_date, end=end_date)
                        occupazioni = [dati_ricerca['Occupazione_%'] if d.date() < data_libero else 0 for d in date_list]
                        
                        df_chart = pd.DataFrame({"Data": date_list, "Allocazione %": occupazioni}).set_index("Data")
                        st.area_chart(df_chart, color="#FF4B4B")

        # =====================================
        # PAGINA 4: DATABASE COMPLETO
        # =====================================
        elif pagina_pm == "🗄️ Master Data (Database)":
            st.title("Vista Tabellare Completa")
            st.write("Esportazione e visualizzazione di tutte le anagrafiche aziendali.")
            # Nascondiamo la colonna "Esperienze" dalla vista grezza perché le liste di dizionari si leggono male
            df_display = st.session_state.df_risorse.drop(columns=['Esperienze'])
            st.dataframe(df_display, use_container_width=True)
            
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica Database (CSV)", data=csv, file_name='database_risorse.csv', mime='text/csv')
