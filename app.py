import streamlit as st
import pandas as pd
import time

# --- 1. FINTO DATABASE DELLE RISORSE AZIENDALI ---
# In futuro questo sarà il tuo database PostgreSQL
db_risorse = [
    {"Nome": "Marco Rossi", "Ruolo": "Senior Backend", "Skill": ["Node.js", "Python", "AWS"], "Costo_Giorno": 300, "Disponibile_dal": "Immediata", "Occupazione_Attuale": "0%"},
    {"Nome": "Giulia Bianchi", "Ruolo": "Mid Frontend", "Skill": ["React", "TypeScript", "Figma"], "Costo_Giorno": 200, "Disponibile_dal": "Immediata", "Occupazione_Attuale": "0%"},
    {"Nome": "Luca Neri", "Ruolo": "Junior Fullstack", "Skill": ["React", "Node.js"], "Costo_Giorno": 150, "Disponibile_dal": "Tra 2 settimane", "Occupazione_Attuale": "100%"},
    {"Nome": "Anna Verdi", "Ruolo": "Senior DevOps", "Skill": ["AWS", "Docker", "Kubernetes"], "Costo_Giorno": 350, "Disponibile_dal": "Immediata", "Occupazione_Attuale": "50%"}
]

# --- 2. SETUP DELL'INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="AI Resource Manager", layout="wide")

st.title("🤖 AI Resource Manager - PoC")
st.markdown("### Modulo di Scoping & Staffing Intelligente")
st.info("Benvenuto PM. Incolla i requisiti del progetto o il contenuto del README. L'AI stimerà tempi, costi e suggerirà il team ideale pescando dalle risorse aziendali libere.")

# --- 3. INPUT DEL PROJECT MANAGER ---
requisiti = st.text_area(
    "📝 Requisiti del Progetto (Incolla le specifiche qui):", 
    height=150, 
    placeholder="Es: Dobbiamo realizzare una piattaforma e-commerce web. Il frontend sarà in React, mentre il backend deve essere sviluppato in Node.js appoggiandosi ad AWS..."
)

# --- 4. IL MOTORE (Simulazione AI) ---
if st.button("🚀 Genera Stima e Suggerisci Team", type="primary"):
    if not requisiti:
        st.warning("Per favore, inserisci dei requisiti prima di procedere.")
    else:
        with st.spinner("L'AI sta analizzando i requisiti e calcolando la WBS..."):
            time.sleep(2) # Simula il tempo di risposta di GPT-4
            
            st.success("Analisi completata!")
            
            # Layout a due colonne
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Stima Progetto (Output AI)")
                # Simuliamo la risposta strutturata dell'AI
                st.write("**Fasi individuate e giorni stimati:**")
                st.markdown("""
                - **Fase 1: Frontend (React)** ➔ Stimati: 15 giorni
                - **Fase 2: Backend & API (Node.js)** ➔ Stimati: 20 giorni
                - **Fase 3: Cloud Setup (AWS)** ➔ Stimati: 5 giorni
                """)
                st.metric(label="Giorni-Uomo Totali Stimati", value="40 Giorni")
                
            with col2:
                st.subheader("💰 Preventivo Costi Interni")
                st.write("Calcolato automaticamente in base alle tariffe del team suggerito.")
                # Simuliamo il calcolo (15g * 200) + (20g * 300) + (5g * 350)
                st.metric(label="Costo Aziendale Stimato", value="€ 10.750")

            st.divider()

            # --- 5. MATCHING DELLE RISORSE ---
            st.subheader("👥 Team Suggerito (Disponibilità Verificata)")
            st.write("L'AI ha scansionato il database HR e suggerisce queste risorse per coprire le skill richieste (React, Node.js, AWS):")
            
            # Creiamo layout a colonne per le "Card" delle risorse
            card1, card2, card3 = st.columns(3)
            
            with card1:
                st.info("**Frontend Lead**")
                st.write("👤 **Giulia Bianchi**")
                st.write("🛠️ Skill match: React, TypeScript")
                st.write("📅 Disponibilità: Immediata (0% occupata)")
                st.write("💶 Costo: 200€/giorno")
                st.button("✅ Conferma Giulia", key="btn1")
                
            with card2:
                st.success("**Backend Lead**")
                st.write("👤 **Marco Rossi**")
                st.write("🛠️ Skill match: Node.js, Python")
                st.write("📅 Disponibilità: Immediata (0% occupato)")
                st.write("💶 Costo: 300€/giorno")
                st.button("✅ Conferma Marco", key="btn2")
                
            with card3:
                st.warning("**DevOps Engineer**")
                st.write("👤 **Anna Verdi**")
                st.write("🛠️ Skill match: AWS, Docker")
                st.write("📅 Disponibilità: Parziale (50% occupata)")
                st.write("💶 Costo: 350€/giorno")
                st.button("🔄 Cerca Sostituto", key="btn3") # Anna è mezza occupata, il PM potrebbe volerla cambiare

            st.divider()
            
            st.subheader("Dettaglio Database Risorse")
            st.write("Visualizzazione grezza del database per questa demo:")
            st.dataframe(pd.DataFrame(db_risorse))
