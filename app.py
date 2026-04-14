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
        giorni_offset = random.randint(0, 30) if occupazione > 0 else 0
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

# Inizializziamo il DB in sessione
if "df_risorse" not in st.session_state:
    st.session_state.df_risorse = genera_database()

# Inizializziamo la coda delle notifiche (Skill da approvare)
if "pending_approvals" not in st.session_state:
    st.session_state.pending_approvals = []

# Inizializziamo lo stato di Login del PM
if "pm_logged_in" not in st.session_state:
    st.session_state.pm_logged_in = False

df_risorse = st.session_state.df_risorse


# ==========================================
# 2. MOTORE SMART E UTILITIES
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
            return "Errore: README non trovato o repository privato."
    except Exception as e:
        return str(e)


# ==========================================
# 3. SIDEBAR (NAVIGAZIONE)
# ==========================================
st.sidebar.title("🔐 Accesso Sistema")
ruolo_utente = st.sidebar.radio("Scegli il tuo ruolo:", ["Project Manager", "Risorsa IT"])

st.sidebar.markdown("---")
st.sidebar.write("**Metriche Aziendali**")
st.sidebar.write(f"👥 Totale Risorse: {len(df_risorse)}")
st.sidebar.write(f"🟢 Risorse Libere: {len(df_risorse[df_risorse['Occupazione_%'] == 0])}")

# Se il PM fa logout dalla sidebar
if ruolo_utente == "Risorsa IT" and st.session_state.pm_logged_in:
    st.session_state.pm_logged_in = False


# ==========================================
# VISTA 1: PROFILO DELLA RISORSA (DIPENDENTE)
# ==========================================
if ruolo_utente == "Risorsa IT":
    st.title("👤 Area Personale")
    st.info("Qui i dipendenti aggiornano le proprie competenze e disponibilità.")
    
    utente_loggato = st.selectbox("Seleziona il tuo profilo per la demo:", df_risorse['Nome'].tolist())
    dati_utente = df_risorse[df_risorse['Nome'] == utente_loggato].iloc[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Ruolo Attuale:** {dati_utente['Ruolo']}")
        st.write(f"**Skill Validate (Ufficiali):** {dati_utente['Skill']}")
        
        st.markdown("---")
        st.write("**Richiedi Nuova Skill**")
        nuova_skill = st.text_input("Aggiungi competenza (es. GraphQL):", key="input_skill")
        
        if st.button("Invia al PM per validazione"):
            if nuova_skill.strip():
                st.session_state.pending_approvals.append({
                    "ID": dati_utente['ID'],
                    "Nome": dati_utente['Nome'],
                    "Skill": nuova_skill.strip()
                })
                st.success(f"Richiesta inviata! Il PM convaliderà '{nuova_skill}' appena farà l'accesso.")
            else:
                st.warning("Inserisci il nome di una competenza.")
            
    with col2:
        st.write(f"**Occupazione Attuale:** {dati_utente['Occupazione_%']}%")
        st.write(f"**Disponibile dal:** {dati_utente['Disponibile_dal']}")
        
        nuova_disp = st.slider("Aggiorna occupazione prossimo mese (%)", 0, 100, int(dati_utente['Occupazione_%']), step=25)
        if st.button("Salva Disponibilità"):
            # Troviamo l'indice corretto e modifichiamo il DataFrame
            idx = df_risorse.index[df_risorse['Nome'] == utente_loggato].tolist()[0]
            st.session_state.df_risorse.at[idx, 'Occupazione_%'] = nuova_disp
            st.success("Calendario aggiornato.")
            st.rerun()


# ==========================================
# VISTA 2: PANNELLO DEL PROJECT MANAGER
# ==========================================
elif ruolo_utente == "Project Manager":
    
    # --- SISTEMA DI LOGIN PM ---
    if not st.session_state.pm_logged_in:
        st.title("🔒 Accesso Area Riservata PM")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Accedi")
            
            if submitted:
                # Credenziali Harcoded per la demo
                if username == "admin" and password == "admin123":
                    st.session_state.pm_logged_in = True
                    st.rerun()
                else:
                    st.error("Credenziali errate. Usa admin / admin123")
                    
    # --- DASHBOARD PM (Se loggato) ---
    else:
        st.title("🤖 AI Resource Manager - Dashboard PM")
        
        # Bottone Logout
        if st.button("Esci (Logout)", key="logout_btn"):
            st.session_state.pm_logged_in = False
            st.rerun()

        # --- SISTEMA DI NOTIFICHE E APPROVAZIONE ---
        if len(st.session_state.pending_approvals) > 0:
            st.warning(f"🔔 ATTENZIONE: Hai {len(st.session_state.pending_approvals)} nuove competenze in attesa di validazione!")
            
            with st.expander("Gestisci Approvazioni in Sospeso", expanded=True):
                # Usiamo una lista temporanea per iterare, così possiamo rimuovere elementi in modo sicuro
                pending_list = list(st.session_state.pending_approvals)
                
                for i, req in enumerate(pending_list):
                    col_n, col_s, col_action = st.columns([3, 4, 3])
                    col_n.write(f"👤 **{req['Nome']}** ({req['ID']})")
                    col_s.write(f"➕ Vuole aggiungere: **{req['Skill']}**")
                    
                    with col_action:
                        # Bottoni in riga
                        b1, b2 = st.columns(2)
                        
                        if b1.button("✅ Approva", key=f"ok_{i}"):
                            # 1. Trova l'utente nel DB
                            idx = st.session_state.df_risorse.index[st.session_state.df_risorse['ID'] == req['ID']].tolist()[0]
                            # 2. Aggiorna le sue skill
                            skill_attuali = st.session_state.df_risorse.at[idx, 'Skill']
                            st.session_state.df_risorse.at[idx, 'Skill'] = f"{skill_attuali}, {req['Skill']}"
                            # 3. Rimuove dalla coda
                            st.session_state.pending_approvals.pop(i)
                            st.success(f"Approvata: {req['Skill']} per {req['Nome']}")
                            st.rerun()
                            
                        if b2.button("❌ Rifiuta", key=f"ko_{i}"):
                            st.session_state.pending_approvals.pop(i)
                            st.error(f"Rifiutata: {req['Skill']} per {req['Nome']}")
                            st.rerun()
            st.markdown("---")

        st.markdown("### Modulo di Scoping & Staffing")
        
        tab1, tab2 = st.tabs(["📝 Inserimento Manuale", "🔗 Analisi Repository GitHub"])
        testo_da_analizzare = ""
        
        with tab1:
            req_manuali = st.text_area("Incolla i requisiti del progetto:", height=150)
            if req_manuali: testo_da_analizzare = req_manuali
                
        with tab2:
            url_github = st.text_input("Inserisci URL GitHub Pubblico (es. https://github.com/facebook/react):")
            if st.button("Scarica e Leggi README"):
                with st.spinner("Estrazione codice da GitHub in corso..."):
                    readme_content = leggi_github_readme(url_github)
                    if "Errore" in readme_content:
                        st.error(readme_content)
                    else:
                        st.success("README scaricato con successo! Anteprima:")
                        st.code(readme_content[:300] + "...\n[CONTINUA]", language="markdown")
                        testo_da_analizzare = readme_content

        # IL MOTORE DI STIMA E MATCHING
        if st.button("🚀 Genera Stima e Cerca Team", type="primary"):
            if not testo_da_analizzare:
                st.warning("Fornisci dei requisiti o un URL GitHub prima di procedere.")
            else:
                with st.spinner("Il motore Smart sta analizzando le tecnologie richieste..."):
                    fasi, giorni_tot, skill_richieste = analizza_testo(testo_da_analizzare)
                    
                    st.divider()
                    st.subheader("📊 Analisi e Stima (Smart Engine)")
                    
                    col_stima1, col_stima2 = st.columns(2)
                    with col_stima1:
                        st.write("**WBS (Work Breakdown Structure) generata:**")
                        st.dataframe(pd.DataFrame(fasi))
                    with col_stima2:
                        st.metric("Giorni-Uomo Totali", giorni_tot)
                        st.write(f"**Skill identificate:** {', '.join(skill_richieste)}")
                    
                    st.divider()
                    st.subheader("👥 Proposta di Allocazione Team")
                    
                    team_proposto = []
                    costo_totale = 0
                    
                    for skill in skill_richieste:
                        mask_skill = df_risorse['Skill'].str.contains(skill, flags=re.IGNORECASE, regex=True)
                        mask_liberi = df_risorse['Occupazione_%'] < 100
                        candidati = df_risorse[mask_skill & mask_liberi]
                        
                        if not candidati.empty:
                            scelto = candidati.iloc[0]
                            team_proposto.append({
                                "Nome": scelto['Nome'],
                                "Ruolo Coperto": f"Specialista {skill}",
                                "Costo Giornaliero": scelto['Costo_Giorno'],
                                "Disponibilità": "Immediata" if scelto['Occupazione_%']==0 else "Parziale"
                            })
                            giorni_skill = next((item['Giorni'] for item in fasi if item["Skill"] == skill), 0)
                            costo_totale += (giorni_skill * scelto['Costo_Giorno'])
                        else:
                            team_proposto.append({"Nome": "NESSUNO TROVATO", "Ruolo Coperto": f"Manca: {skill}", "Costo Giornaliero": 0, "Disponibilità": "-"})

                    df_team = pd.DataFrame(team_proposto)
                    st.table(df_team)
                    
                    st.metric("💰 Costo Interno Progetto Stimato", f"€ {costo_totale}")
                    
                    csv = df_team.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Scarica Proposta Team (CSV)",
                        data=csv,
                        file_name='proposta_team.csv',
                        mime='text/csv',
                    )

        st.divider()
        with st.expander("👁️ Esplora tutto il Database Aziendale (40 Risorse)"):
            st.dataframe(st.session_state.df_risorse)
