import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import re
import plotly.express as px
import calendar

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

if "df_risorse" not in st.session_state: st.session_state.df_risorse = genera_database()
if "pending_approvals" not in st.session_state: st.session_state.pending_approvals = []
if "pending_allocations" not in st.session_state: st.session_state.pending_allocations = []
if "cal_month_idx" not in st.session_state: st.session_state.cal_month_idx = 0

# Variabili Chatbot
if "chat_msgs" not in st.session_state:
    st.session_state.chat_msgs = [{"role": "assistant", "content": "Ciao! Sono il tuo Copilot AI. Scrivimi un comando, ad esempio:\n- *Alloca Marco Rossi su TIM al 50%*\n- *Promuovi Giulia Bianchi a Senior*"}]
if "bot_action" not in st.session_state: st.session_state.bot_action = None

if "pm_logged_in" not in st.session_state: st.session_state.pm_logged_in = False
if "it_logged_in" not in st.session_state: st.session_state.it_logged_in = False
if "hr_logged_in" not in st.session_state: st.session_state.hr_logged_in = False
if "current_it_user" not in st.session_state: st.session_state.current_it_user = None

# ==========================================
# 2. MOTORE SMART E COPILOT DEMO
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

def parse_chatbot_intent(prompt, df):
    """Il Copilot AI ottimizzato per estrarre correttamente i clienti e gestire i dati"""
    prompt_l = prompt.lower()
    nome_trovato = None
    
    for nome in df['Nome']:
        if nome.lower() in prompt_l:
            nome_trovato = nome
            break
            
    if not nome_trovato:
        return None, "Non ho trovato il nome del dipendente. Assicurati di scriverlo correttamente (es. Marco Rossi)."
        
    if "alloca" in prompt_l or "assegna" in prompt_l:
        perc_match = re.search(r'(\d+)%', prompt_l)
        perc = int(perc_match.group(1)) if perc_match else 100
        
        cliente = "Nuovo Progetto"
        # Regex migliorata: prende la parola che viene dopo "su " o "sul " ignorando "progetto"
        prompt_pulito = prompt_l.replace("progetto ", "").replace("cliente ", "")
        match_cliente = re.search(r'(?:su|sul|sulla)\s+([a-zA-Z0-9_\-]+)', prompt_pulito)
        if match_cliente: 
            cliente = match_cliente.group(1).capitalize()
            
        desc = f"**{nome_trovato}** pronto per l'allocazione. Controlla e scegli il periodo:"
        return {"type": "alloca", "nome": nome_trovato, "perc": perc, "cliente": cliente, "desc": desc}, None

    if "promuovi" in prompt_l or "livello" in prompt_l:
        nuova_sen = "Senior" if "senior" in prompt_l else "Mid" if "mid" in prompt_l else "Junior"
        desc = f"Sto per promuovere **{nome_trovato}** a **{nuova_sen}**."
        return {"type": "promuovi", "nome": nome_trovato, "nuova_sen": nuova_sen, "desc": desc}, None
        
    return None, "Non ho capito l'operazione. Usa: 'Alloca [Nome] su [Cliente] al [X]%' oppure 'Promuovi [Nome] a [Livello]'."

def esegui_azione_chatbot(dati_finali):
    df = st.session_state.df_risorse
    idx = df.index[df['Nome'] == dati_finali['nome']].tolist()[0]
    
    if dati_finali['type'] == 'alloca':
        df.at[idx, 'Occupazione_%'] = dati_finali['perc']
        
        # Se è stata passata una data dal widget, usala, altrimenti usa default 30 gg
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
        msg = f"✅ Successo: **{dati_finali['nome']}** è stato promosso a **{dati_finali['nuova_sen']}**."

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
# CHATBOT WIDGET CON POPUP E FORM DI CONFERMA
# ---------------------------------------------------------
if (st.session_state.pm_logged_in or st.session_state.hr_logged_in):
    st.sidebar.markdown("---")
    with st.sidebar.popover("💬 Assistente AI (Copilot)", use_container_width=True):
        st.markdown("**Copilot Aziendale**")
        st.caption("🟢 *Modello: AI Resource Engine (Attivo)*")
        
        for msg in st.session_state.chat_msgs:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # Se c'è un'azione pendente, mostra i dettagli modificabili
        if st.session_state.bot_action:
            act = st.session_state.bot_action
            st.info(act['desc'])
            
            # Form interattivo dentro il bot per validare i dati prima dell'esecuzione
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

        # Input testuale della chat
        if prompt := st.chat_input("Chiedi all'AI (es. Alloca Luca Neri su TIM al 50%)..."):
            st.session_state.chat_msgs.append({"role": "user", "content": prompt})
            with st.spinner("Elaborazione..."):
                action_dict, error_msg = parse_chatbot_intent(prompt, st.session_state.df_risorse)
            
            if error_msg:
                st.session_state.chat_msgs.append({"role": "assistant", "content": error_msg})
            else:
                st.session_state.bot_action = action_dict
                st.session_state.chat_msgs.append({"role": "assistant", "content": "Ho preparato la richiesta. Controlla e conferma i dettagli:"})
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
            "👥 Pianificazione Team (Scheduling)",  # <--- NUOVA TAB TEAM
            "👤 Analisi Profili", 
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
                st.warning(f"🔔 **ATTENZIONE:** Hai **{num_req_alloc}** nuove richieste di allocazione in attesa.")
            
            with st.container(border=True):
                st.markdown("#### 👤 Profilo Manager: Admin")
                st.markdown("**Ruolo:** Senior IT Delivery Manager  \n**Dipartimento:** Digital Transformation")
            
            tot_risorse = len(df)
            occupate = len(df[df['Occupazione_%'] > 0])
            mancati_incassi_gg = df[df['Occupazione_%'] == 0]['Tariffa_Vendita'].sum()
            revenue_attiva_gg = (df['Tariffa_Vendita'] * (df['Occupazione_%']/100)).sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Risorse Totali", tot_risorse)
            c2.metric("Risorse Staffate", occupate)
            c3.metric("Mancati Incassi Bench", f"€ {mancati_incassi_gg:,.2f}")
            c4.metric("Revenue Attesa", f"€ {revenue_attiva_gg:,.2f}")

        # =====================================
        # PM 2: SCOPING & STAFFING AI
        # =====================================
        elif pagina_pm == "🚀 Scoping & Staffing AI":
            st.title("🤖 Scoping Dinamico & Scenario Analysis")
            st.info("💡 Incolla il testo del progetto. Puoi modificare giorni o margine in percentuale direttamente nella griglia.")
            
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
                                team_proposto.append({"Skill": skill, "Nome": risorsa['Nome'], "Costo_gg": risorsa['Costo_Giorno'], "Margine_%": 30})
                                match_trovato = True
                                break 
                        if not match_trovato:
                            team_proposto.append({"Skill": skill, "Nome": "DA ASSUMERE", "Costo_gg": 300, "Margine_%": 30})
                    st.session_state.team_data = pd.DataFrame(team_proposto)

                if "wbs_data" in st.session_state:
                    st.markdown("### 1. WBS & Stima Tempi")
                    edited_wbs = st.data_editor(st.session_state.wbs_data, num_rows="dynamic", key="wbs_editor", use_container_width=True)
                    st.markdown("### 2. Team Consigliato e Marginalità")
                    edited_team = st.data_editor(st.session_state.team_data, key="team_editor", use_container_width=True)
                    
                    costo_totale_progetto, proposta_commerciale = 0, 0
                    for idx, row in edited_wbs.iterrows():
                        membro = edited_team[edited_team['Skill'] == row['Skill']]
                        if not membro.empty:
                            costo_fase = row['Giorni'] * membro.iloc[0]['Costo_gg']
                            costo_totale_progetto += costo_fase
                            proposta_commerciale += costo_fase * (1 + (membro.iloc[0]['Margine_%'] / 100))
                    
                    st.info("### 💰 Breakdown Finanziario (Tempo Reale)")
                    c_fin1, c_fin2, c_fin3 = st.columns(3)
                    c_fin1.metric("Costo Vivo Progetto", f"€ {costo_totale_progetto:,.2f}")
                    c_fin2.metric("Proposta Commerciale", f"€ {proposta_commerciale:,.2f}")
                    c_fin3.metric("Margine Netto Finale", f"€ {proposta_commerciale - costo_totale_progetto:,.2f}")

        # =====================================
        # PM 3: PIANIFICAZIONE & ALLOCAZIONI
        # =====================================
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

        # =====================================
        # PM 4: NUOVA TAB - SCHEDULING TEAM (STILE TEAMS)
        # =====================================
        elif pagina_pm == "👥 Pianificazione Team (Scheduling)":
            st.title("Scheduling Assistant Team")
            st.write("Componi il tuo team e verifica la disponibilità incrociata.")
            
            c_f1, c_f2 = st.columns(2)
            filtro_sen = c_f1.multiselect("Filtra per Seniority:", ["Junior", "Mid", "Senior"], default=["Senior", "Mid", "Junior"])
            df_filtered = df[df['Seniority'].isin(filtro_sen)] if filtro_sen else df
            
            team_selezionato = c_f2.multiselect("Seleziona le risorse per il Team:", df_filtered['Nome'].tolist())
            
            oggi = datetime.today()
            orizzonte = st.date_input("Orizzonte temporale di analisi (Inizio - Fine):", value=(oggi, oggi + timedelta(days=30)))
            
            if team_selezionato and len(orizzonte) == 2:
                start_date, end_date = orizzonte
                st.markdown("---")
                
                # Genera la lista esatta dei giorni tra start_date ed end_date
                date_list = pd.date_range(start=start_date, end=end_date)
                
                # Costruzione della Matrice (Heatmap HTML)
                html_matrix = """
                <div style='overflow-x: auto;'>
                <table style='width: 100%; border-collapse: collapse; text-align: center; font-size: 12px;'>
                    <thead>
                        <tr style='background-color: #2E3338; color: white;'>
                            <th style='padding: 10px; text-align: left; min-width: 150px; border: 1px solid #444;'>Membro Team</th>
                """
                # Intestazioni delle colonne con "GG/MM" reale
                for d in date_list:
                    html_matrix += f"<th style='padding: 5px; width: 35px; border: 1px solid #444; font-size: 11px;'>{d.strftime('%d/%m')}</th>"
                html_matrix += "</tr></thead><tbody>"
                
                # Righe per ogni membro
                for nome in team_selezionato:
                    r_dati = df[df['Nome'] == nome].iloc[0]
                    data_libero = datetime.strptime(r_dati['Disponibile_dal'], "%Y-%m-%d").date()
                    occ_attuale = r_dati['Occupazione_%']
                    
                    html_matrix += f"<tr><td style='padding: 10px; text-align: left; border: 1px solid #444;'><b>{nome}</b><br><span style='font-size:10px; color:#888;'>{r_dati['Ruolo']}</span></td>"
                    
                    for d in date_list:
                        current_day = d.date()
                        
                        # Salta i weekend (visivamente grigi scuro)
                        if current_day.weekday() >= 5:
                            bg_color = "#333333" 
                        else:
                            # Logica colori Teams
                            if current_day < data_libero:
                                if occ_attuale == 100: bg_color = "#00CC96" # Verde (Staffato al 100%, non disponibile)
                                elif occ_attuale > 0: bg_color = "#FFD700" # Giallo (Parzialmente disponibile)
                                else: bg_color = "#FF4B4B" # Rosso (Bench, Totalmente disponibile)
                            else:
                                bg_color = "#FF4B4B" # Dopo la data di fine progetto è Bench (Rosso)

                        # Mostra il giorno del mese dentro la cella in piccolino per maggior chiarezza visiva
                        html_matrix += f"<td style='background-color: {bg_color}; border: 1px solid #444; color: rgba(255,255,255,0.3); font-size: 9px;'>{current_day.day}</td>"
                    html_matrix += "</tr>"
                    
                html_matrix += "</tbody></table></div>"
                
                st.markdown(html_matrix, unsafe_allow_html=True)
                
                # Legenda stile Teams
                st.markdown("""
                <br>
                <div style="display:flex; gap:20px; font-size:12px;">
                    <div style="display:flex; align-items:center;"><div style="width:15px; height:15px; background:#FF4B4B; margin-right:5px; border-radius:3px;"></div> <b>Disponibile (Bench)</b></div>
                    <div style="display:flex; align-items:center;"><div style="width:15px; height:15px; background:#FFD700; margin-right:5px; border-radius:3px;"></div> <b>Parzialmente Occupato</b></div>
                    <div style="display:flex; align-items:center;"><div style="width:15px; height:15px; background:#00CC96; margin-right:5px; border-radius:3px;"></div> <b>Non Disponibile (100%)</b></div>
                    <div style="display:flex; align-items:center;"><div style="width:15px; height:15px; background:#333333; margin-right:5px; border-radius:3px;"></div> Weekend</div>
                </div>
                """, unsafe_allow_html=True)

        # =====================================
        # PM 5: ANALISI SINGOLI PROFILI (CALENDARIO MESE)
        # =====================================
        elif pagina_pm == "👤 Analisi Profili":
            st.title("Indagine Singola Risorsa")
            
            nome_ricerca = st.selectbox("Seleziona Consulente:", df['Nome'].tolist())
            if nome_ricerca:
                dati_ricerca = df[df['Nome'] == nome_ricerca].iloc[0]
                c1, c2, c3 = st.columns(3)
                c1.info(f"**Qualifica:** {dati_ricerca['Ruolo']}")
                c2.success(f"**Skills:** {dati_ricerca['Skill']}")
                c3.warning(f"**Stato Attuale:** Occupato {dati_ricerca['Occupazione_%']}%")
                
                st.markdown("---")
                st.subheader("🗓️ Calendario Visuale (Mensile)")
                
                # Input per l'orizzonte temporale totale (es. 6 mesi)
                date_range = st.date_input("Seleziona l'orizzonte totale di analisi:", value=(datetime.today(), datetime.today() + timedelta(days=180)))
                
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    data_libero = datetime.strptime(dati_ricerca['Disponibile_dal'], "%Y-%m-%d").date()
                    
                    # Calcola tutti i mesi all'interno dell'orizzonte selezionato
                    mesi_presenti = []
                    curr = start_date.replace(day=1)
                    while curr <= end_date:
                        mesi_presenti.append((curr.year, curr.month))
                        # Aggiungi un mese
                        if curr.month == 12: curr = curr.replace(year=curr.year+1, month=1)
                        else: curr = curr.replace(month=curr.month+1)
                    
                    # Controllo indici per la navigazione
                    if st.session_state.cal_month_idx >= len(mesi_presenti): st.session_state.cal_month_idx = 0
                    
                    # UI Navigazione Mese
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
                    nome_mese = calendar.month_name[mese_corr].capitalize()
                    col_m.markdown(f"<h3 style='text-align:center; margin-top:0;'>{nome_mese} {anno_corr}</h3>", unsafe_allow_html=True)
                    
                    # Generazione del calendario per IL MESE selezionato
                    cal = calendar.Calendar(firstweekday=0) # Lunedi=0
                    month_days = cal.monthdatescalendar(anno_corr, mese_corr)
                    
                    # Header giorni settimana
                    giorni_sett = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
                    html_cal = "<div style='display:grid; grid-template-columns: repeat(7, 1fr); gap: 10px; max-width: 600px; margin: auto;'>"
                    for g in giorni_sett:
                        html_cal += f"<div style='text-align:center; font-weight:bold; color:#888;'>{g}</div>"
                        
                    # Caselle dei giorni
                    for week in month_days:
                        for day in week:
                            if day.month != mese_corr:
                                # Giorno del mese precedente/successivo (vuoto)
                                html_cal += "<div style='visibility:hidden;'></div>"
                            else:
                                # Logica del colore per il singolo giorno
                                occ = dati_ricerca['Occupazione_%'] if day < data_libero else 0
                                if day < start_date or day > end_date:
                                    bg_color = "#333333" # Fuori dall'orizzonte (grigio)
                                elif day.weekday() >= 5:
                                    bg_color = "#333333" # Weekend
                                elif occ == 0:
                                    bg_color = "#FF4B4B" # Libero / Bench
                                elif occ < 100:
                                    bg_color = "#FFD700" # Parziale
                                else:
                                    bg_color = "#00CC96" # Staffato 100%
                                    
                                html_cal += f"<div style='background-color:{bg_color}; height:60px; border-radius:5px; display:flex; align-items:center; justify-content:center; font-size:16px; font-weight:bold; color:#FFF;'>{day.day}</div>"
                    
                    html_cal += "</div>"
                    st.markdown(html_cal, unsafe_allow_html=True)

        # =====================================
        # PM 6: MASTER DATA
        # =====================================
        elif pagina_pm == "🗄️ Master Data (Database)":
            st.title("Vista Tabellare Completa")
            st.dataframe(df.drop(columns=['Esperienze']), use_container_width=True)

# ==========================================
# VISTA 3: HR (RISORSE UMANE) - (Intatta per brevità, ometti modifiche logiche qui se non chieste)
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
    else:
        st.sidebar.markdown("---")
        pagina_hr = st.sidebar.radio("Vai a:", ["🏠 Dashboard HR", "➕ Onboarding", "🗄️ Master Data"])
        if st.sidebar.button("🚪 Esci"):
            st.session_state.hr_logged_in = False
            st.rerun()

        if pagina_hr == "🏠 Dashboard HR":
            st.title("Dashboard Risorse Umane")
            st.metric("Totale Dipendenti", len(df))
        elif pagina_hr == "➕ Onboarding":
            st.title("Assunzione Nuovo Dipendente")
            with st.form("form_onboarding"):
                n_nome = st.text_input("Nome e Cognome")
                if st.form_submit_button("Salva"):
                    st.success(f"{n_nome} aggiunto!")
        elif pagina_hr == "🗄️ Master Data":
            st.dataframe(df.drop(columns=['Esperienze']))
