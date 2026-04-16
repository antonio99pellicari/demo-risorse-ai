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
    
    clienti_italiani = ["Enel", "TIM", "Poste Italiane", "Intesa Sanpaolo", "Unicredit", "Ferrari", "Eni", "Leonardo", "Ferrovie dello Stato", "Pirelli"]
    tipi_progetto = ["Piattaforma e-commerce", "App Mobile B2C", "Gestionale ERP", "Dashboard IoT", "Sistema Pagamenti", "Migrazione Cloud"]
    
    db = []
    for i, nome in enumerate(nomi):
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
            "Tariffa_Vendita": costo_base * 1.4, # Simuliamo un ricarico del 40% standard
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

if "pm_logged_in" not in st.session_state: st.session_state.pm_logged_in = False
if "it_logged_in" not in st.session_state: st.session_state.it_logged_in = False
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
# 3. SIDEBAR BASE
# ==========================================
st.sidebar.title("🔐 Accesso Sistema")
ruolo_utente = st.sidebar.radio("Scegli il tuo ruolo:", ["Project Manager", "Consulente"])

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
            
        dati_utente = st.session_state.df_risorse[st.session_state.df_risorse['Nome'] == st.session_state.current_it_user].iloc[0]
        
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
            "🗄️ Master Data (Database)",
            "📥 Team HR (Import/Export)"
        ])
        if st.sidebar.button("🚪 Esci (Logout)"):
            st.session_state.pm_logged_in = False
            st.rerun()

        df = st.session_state.df_risorse

        # =====================================
        # 1: HOMEPAGE
        # =====================================
        if pagina_pm == "🏠 Homepage & Alert":
            st.title("Centro di Controllo Manageriale")
            
            # Profilo Manager
            st.markdown("""
            <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <h4>👤 Profilo Manager: Admin</h4>
                <p><b>Ruolo:</b> Senior IT Delivery Manager<br>
                <b>Dipartimento:</b> Digital Transformation</p>
            </div>
            """, unsafe_allow_html=True)
            
            # KPI
            tot_risorse = len(df)
            occupate = len(df[df['Occupazione_%'] > 0])
            ferme = tot_risorse - occupate
            
            # Calcolo Finanziario Giornaliero
            # Costo fermo = somma costo vivo di chi è a 0%
            costo_ferme_gg = df[df['Occupazione_%'] == 0]['Costo_Giorno'].sum()
            # Revenue attiva = tariffa_vendita * (occupazione/100)
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
        # 2: SCOPING & STAFFING AI (SCENARIO ANALYSIS)
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
                        st.subheader("1. WBS & Stima Tempi (Modificabile)")
                        edited_wbs = st.data_editor(st.session_state.wbs_data, num_rows="dynamic", key="wbs_editor")
                    with col2:
                        st.subheader("2. Team Consigliato (Modificabile)")
                        edited_team = st.data_editor(st.session_state.team_data, key="team_editor")
                    
                    # Calcoli Dinamici (Scenario Analysis)
                    costo_totale_progetto = 0
                    proposta_commerciale = 0
                    
                    for idx, row in edited_wbs.iterrows():
                        skill_fase = row['Skill']
                        giorni = row['Giorni']
                        
                        # Cerca il membro del team assegnato a questa skill
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
        # 3: PIANIFICAZIONE & ALLOCAZIONI
        # =====================================
        elif pagina_pm == "📅 Pianificazione & Allocazioni":
            st.title("Gestione Agende e Allocazioni")
            
            if len(st.session_state.pending_allocations) > 0:
                st.error(f"🔔 Hai {len(st.session_state.pending_allocations)} richieste di allocazione dai consulenti.")
                for i, req in enumerate(list(st.session_state.pending_allocations)):
                    with st.container():
                        st.write(f"👤 **{req['Nome']}** richiede il {req['Occupazione']}% per il progetto **{req['Progetto']}** ({req['Dal']} - {req['Al']})")
                        b1, b2 = st.columns(2)
                        if b1.button("✅ Approva Allocazione", key=f"alloc_ok_{i}"):
                            idx = df.index[df['ID'] == req['ID']].tolist()[0]
                            st.session_state.df_risorse.at[idx, 'Occupazione_%'] = req['Occupazione']
                            st.session_state.pending_allocations.pop(i)
                            st.success("Allocazione confermata!")
                            st.rerun()
                        if b2.button("❌ Rifiuta", key=f"alloc_ko_{i}"):
                            st.session_state.pending_allocations.pop(i)
                            st.rerun()
                        st.divider()
            else:
                st.info("Non ci sono richieste di allocazione in sospeso dai consulenti.")
                
            st.subheader("Assegnazione Manuale Diretta")
            with st.form("manual_alloc"):
                r_scelta = st.selectbox("Risorsa", df['Nome'].tolist())
                perc = st.slider("Percentuale %", 0, 100, 100, step=25)
                if st.form_submit_button("Forza Allocazione a Calendario"):
                    idx = df.index[df['Nome'] == r_scelta].tolist()[0]
                    st.session_state.df_risorse.at[idx, 'Occupazione_%'] = perc
                    if perc == 0: st.session_state.df_risorse.at[idx, 'Disponibile_dal'] = datetime.now().strftime("%Y-%m-%d")
                    st.success(f"{r_scelta} allocato al {perc}%!")
                    st.rerun()

        # =====================================
        # 4: ANALISI PROFILI E ASSEGNAZIONI
        # =====================================
        elif pagina_pm == "👤 Analisi Profili & Assegnazioni":
            st.title("Indagine Risorse")
            
            nome_ricerca = st.selectbox("Seleziona Consulente:", df['Nome'].tolist())
            if nome_ricerca:
                dati_ricerca = df[df['Nome'] == nome_ricerca].iloc[0]
                
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
                        
                        df_pie = pd.DataFrame({
                            "Stato": ["Staffato (Ricavo)", "Panchina (Costo)"],
                            "Giorni": [giorni_occupati, giorni_liberi]
                        })
                        
                        # Inversione Colori richiesta: Rosso per Panchina, Verde per Staffato
                        fig = px.pie(df_pie, values='Giorni', names='Stato', hole=0.4, color='Stato', 
                                     color_discrete_map={"Staffato (Ricavo)": "#00CC96", "Panchina (Costo)": "#FF4B4B"})
                        st.plotly_chart(fig, use_container_width=True)

                with col_dettagli:
                    st.subheader("🗓️ Dettaglio Giornaliero")
                    if len(date_range) == 2:
                        # Creiamo una tabellina con i giorni
                        dettaglio = []
                        for d in date_list:
                            stato = f"Occupato al {dati_ricerca['Occupazione_%']}%" if d.date() < data_libero else "Libero 100%"
                            dettaglio.append({"Data": d.strftime("%Y-%m-%d"), "Giorno": d.strftime("%A"), "Stato": stato})
                        st.dataframe(pd.DataFrame(dettaglio), height=350)

        # =====================================
        # 5: MASTER DATA
        # =====================================
        elif pagina_pm == "🗄️ Master Data (Database)":
            st.title("Vista Tabellare Completa")
            df_display = df.drop(columns=['Esperienze'])
            st.dataframe(df_display, use_container_width=True)

        # =====================================
        # 6: COMPATIBILITA' TEAM HR
        # =====================================
        elif pagina_pm == "📥 Team HR (Import/Export)":
            st.title("Interfaccia Zucchetti / HR")
            st.info("Trattandosi di un modulo disaccoppiato, puoi scaricare il template o fare l'upload massivo per aggiornare i dipendenti.")
            
            st.subheader("1. Esporta dati attuali")
            df_export = df.drop(columns=['Esperienze'])
            csv_export = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica Export Zucchetti (CSV)", data=csv_export, file_name='export_hr_zucchetti.csv', mime='text/csv')
            
            st.markdown("---")
            st.subheader("2. Carica anagrafica aggiornata")
            uploaded_file = st.file_uploader("Upload file (.csv o .xlsx)", type=['csv', 'xlsx'])
            
            if uploaded_file is not None:
                with st.spinner("Sincronizzazione DB in corso..."):
                    if uploaded_file.name.endswith('.csv'):
                        new_df = pd.read_csv(uploaded_file)
                    else:
                        new_df = pd.read_excel(uploaded_file)
                    st.success("File letto correttamente! (Simulazione: in produzione aggiornerebbe il DB tramite API)")
                    st.dataframe(new_df.head(5))
