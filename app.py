import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import requests
import re
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
        ("Frontend Developer", ["React", "Vue", "TypeScript", "HTML/CSS"]),
        ("Backend Developer", ["Node.js", "Python", "Java", "Go", "C#"]),
        ("Fullstack Developer", ["React", "Node.js", "Python", "TypeScript", "SQL"]),
        ("DevOps Engineer", ["AWS", "Docker", "Kubernetes", "CI/CD", "Terraform"]),
        ("Data Scientist", ["Python", "Machine Learning", "SQL", "Pandas"])
    ]
    
    clienti_italiani = ["Enel", "TIM", "Poste Italiane", "Intesa Sanpaolo", "Unicredit", "Ferrari", "Eni", "Leonardo", "Ferrovie dello Stato", "Pirelli"]
    tipi_progetto = ["Piattaforma e-commerce", "App Mobile B2C", "Gestionale ERP", "Dashboard IoT", "Sistema Pagamenti", "Migrazione Cloud"]
    
    db = []
    for i, nome in enumerate(nomi_completi):
        ruolo, skills_possibili = random.choice(ruoli_skills)
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

# Gestione Sessioni per i 3 Ruoli
if "pm_logged_in" not in st.session_state: st.session_state.pm_logged_in = False
if "it_logged_in" not in st.session_state: st.session_state.it_logged_in = False
if "hr_logged_in" not in st.session_state: st.session_state.hr_logged_in = False
if "current_it_user" not in st.session_state: st.session_state.current_it_user = None

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
    
    fasi = []
    for key, (skill, giorni) in regole.items():
        if key in testo_lower:
            competenze_trovate.append(skill)
            fasi.append({"Fase": f"Sviluppo {skill}", "Skill": skill, "Giorni": giorni})
            
    if not fasi:
        fasi = [{"Fase": "Analisi e Setup", "Skill": "Node.js", "Giorni": 10}]
        competenze_trovate = ["Node.js"]
        
    return fasi, competenze_trovate

# ==========================================
# 3. SIDEBAR BASE E LOGOUT INCROCIATI
# ==========================================
st.sidebar.title("🔐 Accesso Sistema")
ruolo_utente = st.sidebar.radio("Scegli il tuo ruolo:", ["Project Manager", "HR (Risorse Umane)", "Consulente"])

# Disconnessione automatica quando si cambia tab
if ruolo_utente != "Project Manager": st.session_state.pm_logged_in = False
if ruolo_utente != "Consulente": 
    st.session_state.it_logged_in = False
    st.session_state.current_it_user = None
if ruolo_utente != "HR (Risorse Umane)": st.session_state.hr_logged_in = False

df = st.session_state.df_risorse

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
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ Navigazione PM")
        pagina_pm = st.sidebar.radio("Vai a:", [
            "🏠 Homepage & Alert", 
            "🚀 Scoping & Staffing AI",
            "📅 Pianificazione & Allocazioni",
            "👤 Analisi Profili & Assegnazioni", 
            "🗄️ Master Data (Database)"
        ]) # Rimosso Team HR
        
        if st.sidebar.button("🚪 Esci (Logout)"):
            st.session_state.pm_logged_in = False
            st.rerun()

        # =====================================
        # PM 1: HOMEPAGE
        # =====================================
        if pagina_pm == "🏠 Homepage & Alert":
            st.title("Centro di Controllo Manageriale")
            st.markdown("""
            <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <h4>👤 Profilo Manager: Admin</h4>
                <p><b>Ruolo:</b> Senior IT Delivery Manager<br><b>Dipartimento:</b> Digital Transformation</p>
            </div>
            """, unsafe_allow_html=True)
            
            tot_risorse = len(df)
            occupate = len(df[df['Occupazione_%'] > 0])
            ferme = tot_risorse - occupate
            
            costo_ferme_gg = df[df['Occupazione_%'] == 0]['Costo_Giorno'].sum()
            revenue_attiva_gg = (df['Tariffa_Vendita'] * (df['Occupazione_%']/100)).sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Risorse Totali", tot_risorse)
            c2.metric("Risorse Staffate", occupate)
            c3.metric("Costo Bench (Giornaliero)", f"€ {costo_ferme_gg:,.2f}")
            c4.metric("Revenue Attesa (Giornaliera)", f"€ {revenue_attiva_gg:,.2f}")
            
            st.markdown("---")
            st.subheader("📊 Bilancio: Costi Bench vs Revenues")
            df_fin = pd.DataFrame({
                "Categoria": ["Costi Risorse Ferme (Perdita)", "Revenues Risorse Staffate (Ricavo)"],
                "Valore Giornaliero": [costo_ferme_gg, revenue_attiva_gg]
            })
            fig_fin = px.pie(df_fin, values='Valore Giornaliero', names='Categoria', hole=0.3,
                             color='Categoria', color_discrete_map={"Costi Risorse Ferme (Perdita)": "#FF4B4B", "Revenues Risorse Staffate (Ricavo)": "#00CC96"})
            st.plotly_chart(fig_fin, use_container_width=True)

        # =====================================
        # PM 2: SCOPING & STAFFING AI
        # =====================================
        elif pagina_pm == "🚀 Scoping & Staffing AI":
            st.title("🤖 Scoping Dinamico & Scenario Analysis")
            st.write("Incolla le specifiche. Modifica le giornate o i margini nelle tabelle sottostanti per ricalcolare i costi in tempo reale.")
            
            testo_da_analizzare = st.text_area("Requisiti di progetto:", height=100)

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
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("1. WBS & Stima Tempi")
                        edited_wbs = st.data_editor(st.session_state.wbs_data, num_rows="dynamic", key="wbs_editor")
                    with col2:
                        st.subheader("2. Team Consigliato")
                        edited_team = st.data_editor(st.session_state.team_data, key="team_editor")
                    
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
                    
                    st.markdown("---")
                    st.subheader("💰 Breakdown Finanziario (Aggiornato in Tempo Reale)")
                    c_fin1, c_fin2, c_fin3 = st.columns(3)
                    c_fin1.metric("Costo Vivo Progetto", f"€ {costo_totale_progetto:,.2f}")
                    c_fin2.metric("Proposta Commerciale", f"€ {proposta_commerciale:,.2f}")
                    margine_assoluto = proposta_commerciale - costo_totale_progetto
                    c_fin3.metric("Margine Netto Finale", f"€ {margine_assoluto:,.2f}")

        # =====================================
        # PM 3: PIANIFICAZIONE & ALLOCAZIONI
        # =====================================
        elif pagina_pm == "📅 Pianificazione & Allocazioni":
            st.title("Gestione Agende e Allocazioni")
            
            if len(st.session_state.pending_allocations) > 0:
                st.error(f"🔔 Hai {len(st.session_state.pending_allocations)} richieste di allocazione.")
                for i, req in enumerate(list(st.session_state.pending_allocations)):
                    with st.container():
                        st.write(f"👤 **{req['Nome']}** richiede il {req['Occupazione']}% per il progetto **{req['Progetto']}** ({req['Dal']} - {req['Al']})")
                        b1, b2 = st.columns(2)
                        if b1.button("✅ Approva", key=f"alloc_ok_{i}"):
                            idx = df.index[df['ID'] == req['ID']].tolist()[0]
                            st.session_state.df_risorse.at[idx, 'Occupazione_%'] = req['Occupazione']
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
                        if b2.button("❌ Rifiuta", key=f"alloc_ko_{i}"):
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
                        st.divider()
            
            st.subheader("Assegnazione Manuale Diretta")
            col_filt1, col_filt2 = st.columns(2)
            seniority_alloc = col_filt1.selectbox("1. Filtra per Livello:", ["Tutti", "Senior", "Mid", "Junior"], key="sen_alloc")
            df_alloc_filt = df if seniority_alloc == "Tutti" else df[df['Seniority'] == seniority_alloc]
            
            with st.form("manual_alloc"):
                r_scelta = st.selectbox("2. Seleziona Consulente:", df_alloc_filt['Nome'].tolist())
                perc = st.slider("Percentuale %", 0, 100, 100, step=25)
                if st.form_submit_button("Forza Allocazione a Calendario"):
                    if r_scelta:
                        idx = df.index[df['Nome'] == r_scelta].tolist()[0]
                        st.session_state.df_risorse.at[idx, 'Occupazione_%'] = perc
                        if perc == 0: st.session_state.df_risorse.at[idx, 'Disponibile_dal'] = datetime.now().strftime("%Y-%m-%d")
                        st.success(f"{r_scelta} allocato al {perc}%!")
                        st.rerun()

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
                        dettaglio = [{"Data": d.strftime("%Y-%m-%d"), "Giorno": d.strftime("%A"), "Stato": f"Occupato al {dati_ricerca['Occupazione_%']}%" if d.date() < data_libero else "Libero 100%"} for d in date_list]
                        st.dataframe(pd.DataFrame(dettaglio), height=350)

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
                # Estrapoliamo il ruolo pulito (togliamo Senior/Mid/Junior dalla stringa)
                df['Ruolo_Puro'] = df['Ruolo'].str.replace('Senior ', '').str.replace('Mid ', '').str.replace('Junior ', '')
                df_ruoli = df['Ruolo_Puro'].value_counts().reset_index()
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
                
                nuovo_ruolo = col1.selectbox("Titolo Professionale", ["Frontend Developer", "Backend Developer", "Fullstack Developer", "DevOps Engineer", "Data Scientist", "Project Manager", "Business Analyst"])
                nuove_skill = col2.text_input("Competenze Iniziali (Separate da virgola, es: React, Node)")
                
                costo_gg = col1.number_input("Costo Giornaliero Base (€)", min_value=50, max_value=1000, value=200)
                
                if st.form_submit_button("✅ Conferma Assunzione e Salva a DB"):
                    if nuovo_nome and nuove_skill:
                        nuovo_dipendente = pd.DataFrame([{
                            "ID": f"RES-{len(df)+1000}",
                            "Nome": nuovo_nome,
                            "Ruolo": f"{nuova_sen} {nuovo_ruolo}",
                            "Seniority": nuova_sen,
                            "Skill": nuove_skill,
                            "Esperienze": [],
                            "Costo_Giorno": costo_gg,
                            "Tariffa_Vendita": costo_gg * 1.4,
                            "Occupazione_%": 0, # Nuova assunzione = disponibile
                            "Disponibile_dal": datetime.now().strftime("%Y-%m-%d")
                        }])
                        st.session_state.df_risorse = pd.concat([st.session_state.df_risorse, nuovo_dipendente], ignore_index=True)
                        st.success(f"Assunzione di {nuovo_nome} completata! Il dipendente è ora a sistema.")
                    else:
                        st.error("Per favore compila Nome e Competenze.")

        # =====================================
        # HR 3: INTEGRAZIONE ZUCCHETTI
        # =====================================
        elif pagina_hr == "📥 Integrazione Zucchetti":
            st.title("Sincronizzazione Software Paghe / Zucchetti")
            st.info("Trattandosi di un modulo disaccoppiato, puoi scaricare il template o fare l'upload massivo per aggiornare le anagrafiche dei dipendenti.")
            
            st.subheader("1. Esporta dati attuali (Per Zucchetti)")
            df_export = df.drop(columns=['Esperienze', 'Ruolo_Puro'], errors='ignore')
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
        # HR 4: MASTER DATA
        # =====================================
        elif pagina_hr == "🗄️ Master Data Dipendenti":
            st.title("Anagrafica Completa Dipendenti")
            st.write("Vista raw del database aziendale.")
            df_display = df.drop(columns=['Esperienze', 'Ruolo_Puro'], errors='ignore')
            st.dataframe(df_display, use_container_width=True)
