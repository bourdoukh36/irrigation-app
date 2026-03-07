import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import geocoder

# 🚨 SUPPRIME TOUTE CONFIG PRÉCÉDENTE
st.markdown("""
<script>
    document.title = "IRRIGATION FERTILISANTE";
    document.querySelector('title').textContent = "IRRIGATION FERTILISANTE";
</script>
""", unsafe_allow_html=True)

# SEULE ET UNIQUE CONFIGURATION
st.set_page_config(
    page_title="IRRIGATION FERTILISANTE",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.image("logo.png", width=150)
# FORCAGE CSS + JS TITRE
st.markdown("""
<style>
/* SUPPRIME TOUS TITRES INDÉSIRABLES */
h1.main-header, h1[class*="header"], title { display: none !important; }
.st-emotion-cache-1r6h4yh h1 { display: none !important; }
/* FORCE TITRE CORRECT */
h1:first-child { color: #1976d2 !important; font-size: 3rem !important; }
</style>
<script>
    // FORCE TITRE NAVIGATEUR
    window.addEventListener('load', function() {
        document.title = "🌱 IRRIGATION FERTILISANTE";
    });
</script>
""", unsafe_allow_html=True)

# TITRE PRINCIPAL PROPRE
st.markdown("# 🌱 **IRRIGATION FERTILISANTE**")
st.markdown("***Agriculture de précision - Souss-Massa 2026***")
st.markdown("─" * 80)


# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1976d2;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .section-header {
        font-size: 1.8rem;
        color: #2e7d32;
        margin-top: 2rem;
        border-bottom: 3px solid #4caf50;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .success-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-left: 5px solid #4caf50;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-left: 5px solid #ff9800;
        border-radius: 5px;
    }
    .stMetric > label {
        color: white !important;
        font-size: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialisation base de données
@st.cache_resource
def init_db():
    conn = sqlite3.connect('agriculture.db', check_same_thread=False)
    cursor = conn.cursor()

    tables = [
        '''CREATE TABLE IF NOT EXISTS Engrais (
            Designation TEXT PRIMARY KEY, N_percent REAL, P_percent REAL, K_percent REAL,
            Ca_percent REAL, Mg_percent REAL)''',
        '''CREATE TABLE IF NOT EXISTS Serres (
            Nom_serre TEXT PRIMARY KEY, Culture TEXT, Variete TEXT, Date_plantation TEXT,
            Superficie REAL, Nb_lignes_irrigation INTEGER, Longueur_ligne REAL, 
            Distance_goutteurs REAL, Debit_goutteur REAL, Quantite_eau_par_heure REAL)''',
        '''CREATE TABLE IF NOT EXISTS Equilibre (
            Age_min INTEGER, Age_max INTEGER, N REAL, P REAL, K REAL, Ca REAL, Mg REAL,
            PRIMARY KEY (Age_min, Age_max))''',
        '''CREATE TABLE IF NOT EXISTS Unites (
            Age_min INTEGER, Age_max INTEGER, N REAL, P REAL, K REAL, Ca REAL, Mg REAL,
            PRIMARY KEY (Age_min, Age_max))'''
    ]

    for table in tables:
        cursor.execute(table)
    conn.commit()
    return conn


conn = init_db()

# Header
st.markdown('<h1 class="main-header">🌱 IRRIGATION FERTILISANTE</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.selectbox("Choisir une section", [
    "🏭 Gestion Engrais", "🏠 Gestion Serres",
    "⚖️ Équilibre", "📏 Unités",
    "💧 Irrigation", "🧮 Calcul Engrais"
])


# Fonctions utilitaires
@st.cache_data(ttl=3600)
def get_location():
    try:
        g = geocoder.ip('me')
        if g.ok:
            return g.latlng
    except:
        return None
    return None


@st.cache_data(ttl=3600)
def get_rayonnement(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=shortwave_radiation_sum&timezone=auto"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        rayonnement = data['daily']['shortwave_radiation_sum'][0]
        return rayonnement * 1_000_000, rayonnement
    except:
        return None, None


def display_metrics_kpi(col1, col2, col3, labels, values):
    with col1: st.metric(labels[0], f"{values[0]:.2f}")
    with col2: st.metric(labels[1], f"{values[1]:.2f}")
    with col3: st.metric(labels[2], f"{values[2]:.2f}")


# Pages
if page == "🏭 Gestion Engrais":
    st.markdown('<h2 class="section-header">🏭 Gestion Engrais</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("➕ Ajouter/Modifier")
        with st.form("form_engrais"):
            designation = st.text_input("Désignation")
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                n = st.number_input("N %", min_value=0.0, format="%.2f")
                p = st.number_input("P %", min_value=0.0, format="%.2f")
            with col_n2:
                k = st.number_input("K %", min_value=0.0, format="%.2f")
                ca = st.number_input("Ca %", min_value=0.0, format="%.2f")
                mg = st.number_input("Mg %", min_value=0.0, format="%.2f")

            if st.form_submit_button("💾 Enregistrer"):
                try:
                    conn.execute('INSERT OR REPLACE INTO Engrais VALUES (?, ?, ?, ?, ?, ?)',
                                 (designation, n, p, k, ca, mg))
                    conn.commit()
                    st.success("✅ Engrais enregistré!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")

    with col2:
        df = pd.read_sql_query("SELECT * FROM Engrais ORDER BY Designation", conn)
        st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "🏠 Gestion Serres":
    st.markdown('<h2 class="section-header">🏠 Gestion Serres</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("➕ Ajouter/Modifier")
        with st.form("form_serres"):
            nom_serre = st.text_input("Nom serre")
            culture = st.text_input("Culture")
            variete = st.text_input("Variété")
            date_plant = st.date_input("Date plantation")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                superficie = st.number_input("Superficie m²", min_value=0.0)
                nb_lignes = st.number_input("Nb lignes irrigation", min_value=0)
            with col_s2:
                longueur = st.number_input("Longueur ligne (m)", min_value=0.0)
                distance = st.number_input("Distance goutteurs (m)", min_value=0.0)
                debit = st.number_input("Débit goutteur L/h", min_value=0.0)

            if st.form_submit_button("💾 Enregistrer"):
                try:
                    conn.execute('INSERT OR REPLACE INTO Serres VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                 (nom_serre, culture, variete, str(date_plant), superficie,
                                  int(nb_lignes), longueur, distance, debit, 0.0))
                    conn.commit()
                    st.success("✅ Serre enregistrée!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")

    with col2:
        df = pd.read_sql_query("SELECT * FROM Serres ORDER BY Nom_serre", conn)
        st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "⚖️ Équilibre":
    st.markdown('<h2 class="section-header">⚖️ Équilibre Nutritionnel</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        with st.form("form_equilibre"):
            col_a1, col_a2 = st.columns(2)
            with col_a1: age_min = st.number_input("Âge min (jours)", min_value=0)
            with col_a2: age_max = st.number_input("Âge max (jours)", min_value=0)

            col_n1, col_n2, col_n3 = st.columns(3)
            with col_n1: n = st.number_input("N", min_value=0.0, format="%.2f")
            with col_n2: p = st.number_input("P", min_value=0.0, format="%.2f")
            with col_n3: k = st.number_input("K", min_value=0.0, format="%.2f")

            col_c1, col_c2 = st.columns(2)
            with col_c1: ca = st.number_input("Ca", min_value=0.0, format="%.2f")
            with col_c2: mg = st.number_input("Mg", min_value=0.0, format="%.2f")

            if st.form_submit_button("💾 Enregistrer"):
                conn.execute('INSERT OR REPLACE INTO Equilibre VALUES (?, ?, ?, ?, ?, ?, ?)',
                             (age_min, age_max, n, p, k, ca, mg))
                conn.commit()
                st.success("✅ Équilibre enregistré!")
                st.rerun()

    with col2:
        df = pd.read_sql_query("SELECT * FROM Equilibre ORDER BY Age_min", conn)
        st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "📏 Unités":
    st.markdown('<h2 class="section-header">📏 Unités Fertilisation</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🧮 Calculateur Auto")
        with st.form("form_unites"):
            col1_u, col2_u = st.columns(2)
            with col1_u:
                age_min = st.number_input("Âge min", min_value=0)
            with col2_u:
                age_max = st.number_input("Âge max", min_value=0)
            n_unite = st.number_input("N unitaire", min_value=0.0, format="%.2f")

            if st.form_submit_button("🧮 Calculer & Sauvegarder"):
                cursor = conn.cursor()
                cursor.execute("SELECT N, P, K, Ca, Mg FROM Equilibre WHERE ? BETWEEN Age_min AND Age_max",
                               (age_min,))
                eq = cursor.fetchone()
                if eq:
                    n_eq, p_eq, k_eq, ca_eq, mg_eq = eq
                    if n_eq > 0:
                        p_u = (p_eq / n_eq) * n_unite
                        k_u = (k_eq / n_eq) * n_unite
                        ca_u = (ca_eq / n_eq) * n_unite
                        mg_u = (mg_eq / n_eq) * n_unite

                        conn.execute('INSERT OR REPLACE INTO Unites VALUES (?, ?, ?, ?, ?, ?, ?)',
                                     (age_min, age_max, n_unite, p_u, k_u, ca_u, mg_u))
                        conn.commit()

                        col1_r, col2_r, col3_r = st.columns(3)
                        display_metrics_kpi(col1_r, col2_r, col3_r,
                                            ["P", "K", "Ca"], [p_u, k_u, ca_u])
                        st.success("✅ Unités calculées et sauvegardées!")
                    else:
                        st.error("❌ N=0 dans équilibre")
                else:
                    st.error("❌ Aucun équilibre trouvé")

    with col2:
        df = pd.read_sql_query("SELECT * FROM Unites ORDER BY Age_min", conn)
        st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "💧 Irrigation":
    st.markdown('<h2 class="section-header">💧 Calcul Irrigation</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌍 ETc (Besoin en eau)")
        localisation = get_location()
        if localisation:
            lat, lon = localisation
            st.info(f"📍 **{lat:.4f}°, {lon:.4f}**")

            rg_j, rg_mj = get_rayonnement(lat, lon)
            if rg_j:
                st.metric("☀️ Rayonnement", f"{rg_mj:.1f} MJ/m²/j")

                kc_dict = {
                    "0️⃣ Initial (0.5)": 0.5,
                    "1️⃣ Végétatif (0.75)": 0.75,
                    "2️⃣ Floraison (1.0)": 1.0,
                    "3️⃣ Fruits (1.1)": 1.1,
                    "4️⃣ Fin cycle (0.9)": 0.9
                }
                kc_key = st.selectbox("🌱 Stade (Kc)", kc_dict.keys())
                kc = kc_dict[kc_key]

                if st.button("💧 Calculer ETc"):
                    lambda_eau = 2450000
                    etc = kc * rg_j * 0.408 / lambda_eau
                    st.metric("💧 **ETc recommandée**", f"{etc:.2f} mm/jour")
                    st.session_state.etc_value = etc
                    st.session_state.kc_value = kc_key
            else:
                st.warning("⚠️ Données météo indisponibles")

    with col2:
        st.subheader("⏱️ Temps irrigation")
        df_serres = pd.read_sql_query("SELECT * FROM Serres", conn)
        if not df_serres.empty:
            serre_nom = st.selectbox("🏠 Serre", df_serres["Nom_serre"].tolist())
            serre_data = df_serres[df_serres["Nom_serre"] == serre_nom].iloc[0]

            if hasattr(st.session_state, 'etc_value'):
                qte_eau = st.number_input("💧 Eau à apporter L/m²",
                                          value=st.session_state.etc_value, step=0.1)

                col1_t, col2_t, col3_t = st.columns(3)
                with col1_t:
                    st.metric("📏 Surface", f"{serre_data['Superficie']:.0f} m²")
                with col2_t:
                    st.metric("🚿 Goutteurs",
                              f"{int(serre_data['Nb_lignes_irrigation'] * serre_data['Longueur_ligne'] / serre_data['Distance_goutteurs']):.0f}")
                with col3_t:
                    st.metric("💧 Débit total",
                              f"{serre_data['Nb_lignes_irrigation'] * serre_data['Longueur_ligne'] / serre_data['Distance_goutteurs'] * serre_data['Debit_goutteur']:.0f} L/h")

                if st.button("⏱️ Calculer temps"):
                    surface = serre_data['Superficie']
                    nb_gout = serre_data['Nb_lignes_irrigation'] * serre_data['Longueur_ligne'] / serre_data[
                        'Distance_goutteurs']
                    debit_g = serre_data['Debit_goutteur']

                    qte_totale = qte_eau * surface
                    temps_h = (qte_totale / nb_gout) / debit_g
                    temps_min = temps_h * 60

                    st.markdown("### 🎯 **Résultat**")
                    st.metric("⏱️ **TEMPS IRRIGATION**", f"{temps_min:.1f} minutes")
                    st.info(f"💧 Eau totale: **{qte_totale:.0f} L**")

elif page == "🧮 Calcul Engrais":
    st.markdown('<h2 class="section-header">🧮 Calcul Quantités Engrais</h2>', unsafe_allow_html=True)

    # Colonnes principales
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader("🏠 **Sélection Serre**")
        df_serres = pd.read_sql_query("SELECT Nom_serre, Culture, Variete, Date_plantation FROM Serres", conn)
        if not df_serres.empty:
            serre_nom = st.selectbox("Sélectionnez la serre :", df_serres["Nom_serre"].tolist())
            serre_data = df_serres[df_serres["Nom_serre"] == serre_nom].iloc[0]

            # Calcul âge
            try:
                date_plant = datetime.strptime(serre_data["Date_plantation"], "%Y-%m-%d")
                age = max(0, (datetime.now() - date_plant).days)
            except:
                age = st.number_input("Âge (jours)", min_value=0, value=30)

            st.info(f"**Culture :** {serre_data['Culture']}")
            st.info(f"**Variété :** {serre_data['Variete']}")
            st.metric("🌱 **Âge**", f"{age} jours")

    with col2:
        st.subheader("⚖️ **Besoins Nutritionnels**")
        cursor = conn.cursor()

        # Équilibre
        cursor.execute("SELECT N, P, K, Ca, Mg FROM Equilibre WHERE ? BETWEEN Age_min AND Age_max", (age,))
        eq = cursor.fetchone()
        if eq:
            col_eq1, col_eq2 = st.columns(2)
            with col_eq1:
                st.metric("🍃 N", f"{eq[0]:.2f}")
                st.metric("🔥 P", f"{eq[1]:.2f}")
            with col_eq2:
                st.metric("⚡ K", f"{eq[2]:.2f}")
                st.metric("🪨 Ca", f"{eq[3]:.2f}")
                st.metric("✨ Mg", f"{eq[4]:.2f}")

        # Unités
        cursor.execute("SELECT N, P, K, Ca, Mg FROM Unites WHERE ? BETWEEN Age_min AND Age_max", (age,))
        un = cursor.fetchone()
        if un:
            col_un1, col_un2 = st.columns(2)
            with col_un1:
                st.metric("📏 N", f"{un[0]:.2f}")
                st.metric("📏 P", f"{un[1]:.2f}")
            with col_un2:
                st.metric("📏 K", f"{un[2]:.2f}")
                st.metric("📏 Ca", f"{un[3]:.2f}")
                st.metric("📏 Mg", f"{un[4]:.2f}")

    with col3:
        st.subheader("🧪 **Acide Nitrique**")
        acide_nitrique_litre = st.number_input("Quantité (L)", min_value=0.0, format="%.2f")

    # Sélection engrais
    st.subheader("🏭 **Sélection Engrais**")
    df_engrais = pd.read_sql_query("SELECT Designation FROM Engrais ORDER BY Designation", conn)
    engrais_list = df_engrais["Designation"].tolist()
    selected_engrais = st.multiselect("Choisissez les engrais :", engrais_list)

    # BOUTON CALCUL
    if st.button("🚀 **CALCULER LES QUANTITÉS**", type="primary") and selected_engrais and 'age' in locals():
        cursor = conn.cursor()
        cursor.execute("SELECT Age_min, Age_max, N, P, K, Ca, Mg FROM Unites WHERE ? BETWEEN Age_min AND Age_max",
                       (age,))
        un = cursor.fetchone()

        if not un:
            st.error("❌ Unités non définies pour cet âge")
            st.stop()

        besoins = list(map(float, un[2:]))  # N, P, K, Ca, Mg CORRIGÉ
        densite_acide_nitrique = 1.4

        # N% acide nitrique
        cursor.execute("SELECT N_percent FROM Engrais WHERE LOWER(Designation)='acide nitrique'")
        res_acide = cursor.fetchone()
        n_percent_acide = res_acide[0] if res_acide else 0

        # CLASSIFICATION ENGRAIS (LOGIQUE IDENTIQUE)
        engrais_compose = {}
        ammonitrate = None
        acide_nitrique_inclu = False

        for eng in selected_engrais:
            cursor.execute("SELECT N_percent FROM Engrais WHERE Designation=?", (eng,))
            res_pct = cursor.fetchone()
            pct_N = res_pct[0] if res_pct else 0

            if pct_N == 0:  # Engrais sans N
                engrais_compose[eng] = None
            else:
                eng_lower = eng.lower()
                if eng_lower == "ammonitrate":
                    ammonitrate = eng
                elif eng_lower == "acide nitrique":
                    acide_nitrique_inclu = True
                else:
                    engrais_compose[eng] = None

        # COMPOSITIONS COMPLÈTES
        for eng in list(engrais_compose.keys()):
            cursor.execute(
                "SELECT N_percent, P_percent, K_percent, Ca_percent, Mg_percent FROM Engrais WHERE Designation=?",
                (eng,))
            compo = cursor.fetchone()
            engrais_compose[eng] = compo

        # CALCUL P,K,Ca,Mg (PARTAGE ÉGAL)
        quantites_par_engrais = {eng: 0 for eng in engrais_compose.keys()}
        elements = ['P', 'K', 'Ca', 'Mg']
        index_elem = {'P': 1, 'K': 2, 'Ca': 3, 'Mg': 4}

        for elem in elements:
            besoin_elem = besoins[index_elem[elem]]
            eng_apporteurs = [eng for eng, compo in engrais_compose.items() if compo[index_elem[elem]] > 0]
            if eng_apporteurs:
                repartition = besoin_elem / len(eng_apporteurs)
                for eng in eng_apporteurs:
                    pct_elem = engrais_compose[eng][index_elem[elem]]
                    qte = repartition / (pct_elem / 100)
                    quantites_par_engrais[eng] = max(quantites_par_engrais[eng], qte)

        # CALCUL N TOTAL DES ENGRAIS COMPOSÉS
        total_N_apporte = 0
        for eng, qte in quantites_par_engrais.items():
            pct_N = engrais_compose[eng][0]
            total_N_apporte += qte * (pct_N / 100)

        # ACIDE NITRIQUE
        if acide_nitrique_inclu and acide_nitrique_litre > 0:
            quantite_acide_kg = acide_nitrique_litre * densite_acide_nitrique
            total_N_apporte += quantite_acide_kg * (n_percent_acide / 100)

        # AMMONITRATE = RESTE N MANQUANT ✅
        besoin_N_restant = max(0, besoins[0] - total_N_apporte)
        quantite_ammonitrate = 0
        compo_ammonitrate = None

        if besoin_N_restant > 0 and ammonitrate:
            cursor.execute(
                "SELECT N_percent, P_percent, K_percent, Ca_percent, Mg_percent FROM Engrais WHERE Designation=?",
                (ammonitrate,))
            compo_ammonitrate = cursor.fetchone()
            if compo_ammonitrate:
                pct_N_ammonitrate = compo_ammonitrate[0]
                quantite_ammonitrate = besoin_N_restant / (pct_N_ammonitrate / 100)

        # AFFICHAGE RÉSULTATS
        st.markdown("## 🎯 **RÉSULTATS**")
        data_results = []
        totaux = [0.0] * 5

        # Engrais composés
        for eng, qte in quantites_par_engrais.items():
            if qte > 0:
                compo = engrais_compose[eng]
                apports = [qte * (p / 100) if p else 0.0 for p in compo]
                data_results.append({
                    'Engrais': eng,
                    'Quantité(g)': round(qte * 1000, 2),
                    'N(g)': round(apports[0] * 1000, 2),
                    'P(g)': round(apports[1] * 1000, 2),
                    'K(g)': round(apports[2] * 1000, 2),
                    'Ca(g)': round(apports[3] * 1000, 2),
                    'Mg(g)': round(apports[4] * 1000, 2)
                })
                totaux = [totaux[i] + apports[i] for i in range(5)]

        # Ammonitrate
        if quantite_ammonitrate > 0 and compo_ammonitrate:
            apports_ammon = [quantite_ammonitrate * (p / 100) if p else 0.0 for p in compo_ammonitrate]
            data_results.append({
                'Engrais': "Ammonitrate",
                'Quantité(g)': round(quantite_ammonitrate * 1000, 2),
                'N(g)': round(apports_ammon[0] * 1000, 2),
                'P(g)': round(apports_ammon[1] * 1000, 2),
                'K(g)': round(apports_ammon[2] * 1000, 2),
                'Ca(g)': round(apports_ammon[3] * 1000, 2),
                'Mg(g)': round(apports_ammon[4] * 1000, 2)
            })
            totaux = [totaux[i] + apports_ammon[i] for i in range(5)]

        # Acide nitrique
        if acide_nitrique_inclu and acide_nitrique_litre > 0:
            quantite_acide_kg = acide_nitrique_litre * densite_acide_nitrique
            apport_N_acide = quantite_acide_kg * (n_percent_acide / 100)
            data_results.append({
                'Engrais': "Acide nitrique",
                'Quantité(g)': round(quantite_acide_kg * 1000, 2),
                'N(g)': round(apport_N_acide * 1000, 2),
                'P(g)': 0, 'K(g)': 0, 'Ca(g)': 0, 'Mg(g)': 0
            })
            totaux[0] += apport_N_acide

        # TOTAUX
        data_results.append({
            'Engrais': "**TOTAUX**",
            'Quantité(g)': "",
            'N(g)': f"{totaux[0] * 1000:.2f}",
            'P(g)': f"{totaux[1] * 1000:.2f}",
            'K(g)': f"{totaux[2] * 1000:.2f}",
            'Ca(g)': f"{totaux[3] * 1000:.2f}",
            'Mg(g)': f"{totaux[4] * 1000:.2f}"
        })

        df_results = pd.DataFrame(data_results)
        st.dataframe(df_results, use_container_width=True)

        st.success("✅ **Calcul terminé ! Ammonitrate complète le N manquant**")

# Footer
st.markdown("---")
with st.container():
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1: st.markdown("*🌱 Agriculture de précision*")
    with col_f2: st.markdown("*📱 Version Streamlit*")
    with col_f3: st.markdown("*Bourdoukh")


