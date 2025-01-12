from flask import Flask, request, render_template_string, jsonify
from owlready2 import *
import logging
from rdflib import Graph, Namespace

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def load_ontology():
    # Ontoloji dosyasının bulunduğu klasörü ekliyoruz
    onto_path.append(".")
    # Ontoloji dünyasını (world) oluşturup ontolojiyi yüklüyoruz
    world = World()
    onto = world.get_ontology("crime_ontology.owl").load()
    logging.info(f"Classes: {len(list(onto.classes()))}")
    return world

# Ontolojiyi yüklüyoruz
world = load_ontology()
# Gerekli namespace'i tanımlıyoruz
CRIME = Namespace("http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#")

# Ana template (HTML + CSS + JavaScript)
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Suç Ontolojisi Sorgu Arayüzü</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --dark-bg: #1a1c23;
            --dark-secondary: #242731;
            --dark-hover: #2d303a;
            --accent-color: #6366f1;
            --accent-hover: #4f46e5;
            --text-primary: #e2e8f0;
            --text-secondary: #9ca3af;
            --border-color: rgba(255,255,255,0.1);
        }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--dark-bg);
            color: var(--text-primary);
        }
        .sidebar {
            padding-top: 30px;
            width: 280px;
            position: fixed;
            top: 0;
            bottom: 0;
            left: 0;
            z-index: 100;
            background: var(--dark-secondary);
            border-right: 1px solid var(--border-color);
            overflow-y: auto;
        }
        .main-content {
            margin-left: 280px;
            padding: 2rem;
        }
        .section-header {
            padding: 1rem 1.5rem;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            border-left: 3px solid transparent;
            user-select: none;
        }
        .section-header:hover {
            background: var(--dark-hover);
            border-left-color: var(--accent-color);
        }
        .section-header i {
            transition: transform 0.2s;
        }
        .section-header.collapsed i {
            transform: rotate(-90deg);
        }
        .section-content {
            display: none;
            padding: 0.5rem 1rem;
        }
        .menu-item {
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            color: var(--text-primary);
            text-decoration: none;
            border-radius: 6px;
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .menu-item:hover {
            background: var(--dark-hover);
            color: var(--accent-color);
            transform: translateX(5px);
        }
        .menu-item.active {
            background: var(--dark-hover);
            color: var(--accent-color);
            border: 1px solid var(--accent-color);
        }
        .menu-item i {
            margin-right: 0.75rem;
            width: 20px;
            text-align: center;
        }
        .query-box {
            background: var(--dark-secondary);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
        }
        .query-header {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
            gap: 1rem;
        }
        .query-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            white-space: nowrap;
        }
        .query-description {
            font-size: 0.9rem;
            color: var(--text-secondary);
            border-left: 2px solid var(--accent-color);
            padding-left: 1rem;
            margin: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .query-content {
            width: 100%;
            position: relative;
        }
        .query-textarea {
            font-family: 'Monaco', monospace;
            font-size: 0.9rem;
            resize: vertical;
            min-height: 200px;
            width: 100%;
            background: var(--dark-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            color: var(--text-primary);
            margin-bottom: 1rem;
            box-sizing: border-box;
            line-height: 1.5;
            overflow-y: auto;
        }
        .query-textarea:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25);
            outline: none;
        }
        .btn-run {
            background: var(--accent-color);
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            transition: all 0.2s;
        }
        .btn-run:hover {
            background: var(--accent-hover);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
        }
        .table {
            color: var(--text-primary);
        }
        .table thead th {
            background: var(--dark-hover);
            border-color: var(--border-color);
            position: sticky;
            top: 0;
        }
        .table td {
            border-color: var(--border-color);
        }
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--dark-secondary);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--dark-hover);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent-color);
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <!-- Tek Vaka Sorguları -->
        <div class="section">
            <div class="section-header collapsed" onclick="toggleSection('singleCase')">
                <span>Tek Vaka Sorguları</span>
                <i class="fas fa-chevron-right"></i>
            </div>
            <div class="section-content" id="singleCase">
                <!-- Her bir sorgu menü öğesi -->
                <div class="menu-item" onclick="setQuery('single-killer', 'Bir cinayete ait katilin ad yaş ve cinsiyet bilgileri nelerdir?')">
                    <i class="fas fa-user"></i>
                    Katilin Bilgileri
                </div>
                <div class="menu-item" onclick="setQuery('single-victim', 'Cinayet maktulünün ad yaş ve cinsiyet bilgileri nelerdir?')">
                    <i class="fas fa-user-minus"></i>
                    Maktul Bilgileri
                </div>
                <div class="menu-item" onclick="setQuery('single-suspects', 'Bir cinayete ait şüphelilerin adı, yaşı ve cinsiyetleri nelerdir?')">
                    <i class="fas fa-user-secret"></i>
                    Şüpheli Bilgileri
                </div>
                <div class="menu-item" onclick="setQuery('single-crime-type', 'Cinayet hangi tür cinayet sınıfına girmektedir?')">
                    <i class="fas fa-bookmark"></i>
                    Cinayet Türü
                </div>
                <div class="menu-item" onclick="setQuery('single-location', 'Cinayet nerede gerçekleşmiştir?')">
                    <i class="fas fa-map-marker-alt"></i>
                    Cinayet Konumu
                </div>
                <div class="menu-item" onclick="setQuery('single-time', 'Cinayet ne zaman gerçekleşmiştir?')">
                    <i class="fas fa-clock"></i>
                    Cinayet Zamanı
                </div>
                <div class="menu-item" onclick="setQuery('single-weapon', 'Cinayet hangi cinayet aleti ile işlenmiştir?')">
                    <i class="fas fa-gavel"></i>
                    Cinayet Aleti
                </div>
                <div class="menu-item" onclick="setQuery('single-courtdate', 'Cinayete ait davanın başlangıç tarihi nedir?')">
                    <i class="fas fa-calendar-alt"></i>
                    Dava Başlangıç Tarihi
                </div>
                <div class="menu-item" onclick="setQuery('single-court', 'Davanın gerçekleştiği mahkemenin adı ve konumu nedir?')">
                    <i class="fas fa-university"></i>
                    Mahkeme Bilgileri
                </div>
                <div class="menu-item" onclick="setQuery('single-defendants', 'Davanın sanıkları kimlerdir?')">
                    <i class="fas fa-gavel"></i>
                    Sanıklar
                </div>
                <div class="menu-item" onclick="setQuery('single-killer-sentence', 'Katilin aldığı ceza nedir?')">
                    <i class="fas fa-balance-scale"></i>
                    Katilin Aldığı Ceza
                </div>
                <div class="menu-item" onclick="setQuery('single-suspects-at-scene', 'Söz konusu şüpheliler olay yerinde miydi?')">
                    <i class="fas fa-search-location"></i>
                    Olay Yeri Şüphelileri
                </div>
            </div>
        </div>

        <!-- Tüm Vaka Sorguları -->
        <div class="section">
            <div class="section-header collapsed" onclick="toggleSection('allCase')">
                <span>Tüm Vaka Sorguları</span>
                <i class="fas fa-chevron-right"></i>
            </div>
            <div class="section-content" id="allCase">
                <div class="menu-item" onclick="setQuery('all-killers', 'Tüm cinayetlere ait katillerin ad yaş ve cinsiyet bilgileri nelerdir?')">
                    <i class="fas fa-users-slash"></i>
                    Tüm Katiller
                </div>
                <div class="menu-item" onclick="setQuery('all-victims', 'Tüm cinayet maktullerinin ad yaş ve cinsiyet bilgileri nelerdir?')">
                    <i class="fas fa-users"></i>
                    Tüm Maktuller
                </div>
                <div class="menu-item" onclick="setQuery('all-suspects', 'Tüm cinayetlere ait şüphelilerin adı, yaşı ve cinsiyetleri nedir?')">
                    <i class="fas fa-user-secret"></i>
                    Tüm Şüpheliler
                </div>
                <div class="menu-item" onclick="setQuery('all-crime-types', 'Tüm cinayetler hangi tür cinayet sınıflarına girmektedirler?')">
                    <i class="fas fa-bookmark"></i>
                    Tüm Cinayet Türleri
                </div>
                <div class="menu-item" onclick="setQuery('all-locations', 'Tüm cinayetler nerelerde gerçekleştiler?')">
                    <i class="fas fa-map-marker-alt"></i>
                    Tüm Cinayet Konumları
                </div>
                <div class="menu-item" onclick="setQuery('all-times', 'Tüm cinayetler ne zaman gerçekleştiler?')">
                    <i class="fas fa-clock"></i>
                    Tüm Cinayet Zamanları
                </div>
                <div class="menu-item" onclick="setQuery('all-weapons', 'Tüm cinayetler hangi cinayet aletleri ile işlenmiştir?')">
                    <i class="fas fa-gavel"></i>
                    Tüm Cinayet Aletleri
                </div>
                <div class="menu-item" onclick="setQuery('all-courtdates', 'Tüm cinayetlere ait davaların başlangıç tarihleri nelerdir?')">
                    <i class="fas fa-calendar-alt"></i>
                    Tüm Dava Başlangıç Tarihleri
                </div>
                <div class="menu-item" onclick="setQuery('all-courts', 'Tüm davaların gerçekleştiği mahkemelerin adları ve konumları nelerdir?')">
                    <i class="fas fa-university"></i>
                    Tüm Mahkeme Bilgileri
                </div>
                <div class="menu-item" onclick="setQuery('all-defendants', 'Tüm davaların sanıkları kimlerdir?')">
                    <i class="fas fa-gavel"></i>
                    Tüm Sanıklar
                </div>
                <div class="menu-item" onclick="setQuery('all-defendants-lawyers', 'Tüm davalarda sanık avukatları kimlerdir?')">
                    <i class="fas fa-user-tie"></i>
                    Sanık Avukatları
                </div>
                <div class="menu-item" onclick="setQuery('all-victim-lawyers', 'Tüm davalarda maktul avukatları kimlerdir?')">
                    <i class="fas fa-user-tie"></i>
                    Maktul Avukatları
                </div>
                <div class="menu-item" onclick="setQuery('all-killer-sentences', 'Tüm davalarda katillerin aldıkları cezalar nelerdir?')">
                    <i class="fas fa-balance-scale"></i>
                    Tüm Katillerin Cezaları
                </div>
            </div>
        </div>

        <!-- Kompleks Sorgular -->
        <div class="section">
            <div class="section-header collapsed" onclick="toggleSection('complex')">
                <span>Kompleks Sorgular</span>
                <i class="fas fa-chevron-right"></i>
            </div>
            <div class="section-content" id="complex">
                <div class="menu-item" onclick="setQuery('age-groups', 'Yaş gruplarına göre katil olma eğilimi nedir?')">
                    <i class="fas fa-chart-pie"></i>
                    Katil Olma Eğilimi (Yaş Grupları)
                </div>
                <div class="menu-item" onclick="setQuery('crime-type-gender', 'Cinayet türlerinin, katillerin cinsiyeti ile bağlantısı?')">
                    <i class="fas fa-percentage"></i>
                    Cinayet Türü & Cinsiyet İlişkisi
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <!-- Query Box -->
        <div class="query-box">
            <div class="query-header">
                <div class="query-title">SPARQL Sorgusu</div>
                <div class="query-description" id="queryDescription">
                    <!-- Sorgu açıklaması buraya gelecek -->
                </div>
            </div>
            <div class="query-content">
                <textarea id="queryInput" class="query-textarea" spellcheck="false"></textarea>
                <button onclick="executeQuery()" class="btn btn-run">
                    <i class="fas fa-play me-2"></i>Sorguyu Çalıştır
                </button>
            </div>
        </div>

        <!-- Results Box -->
        <div class="query-box" id="queryResults">
            <!-- Sorgu sonuçları burada görünecek -->
        </div>
    </div>

    <script>
        // Tüm SPARQL sorguları:
        const queries = {
            /* --- TEK VAKA SORGULARI --- */
            'single-killer': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?katilAdi ?katilYasi ?katilCinsiyet
WHERE {
  crime:vaka_1 crime:isler ?katil .
  ?katil crime:katil_adi ?katilAdi .
  ?katil crime:katil_yasi ?katilYasi .
  ?katil crime:katil_cinsiyet ?katilCinsiyet .
}`,
            'single-victim': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?maktulAdi ?maktulYasi ?maktulCinsiyet
WHERE {
  crime:vaka_1 crime:kurbanidir ?maktul .
  ?maktul crime:maktulun_adi ?maktulAdi .
  ?maktul crime:maktul_yas ?maktulYasi .
  ?maktul crime:maktul_cinsiyet ?maktulCinsiyet .
}`,
            'single-suspects': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?supheliAdi ?supheliYasi ?supheliCinsiyet
WHERE {
  crime:vaka_1 crime:suphelidir ?supheli .
  ?supheli crime:supheli_adi ?supheliAdi .
  ?supheli crime:supheli_yasi ?supheliYasi .
  ?supheli crime:supheli_cinsiyet ?supheliCinsiyet .
}`,
            'single-crime-type': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?cinayetTuruLabel
WHERE {
  crime:vaka_1 crime:cinayet_turudur ?cinayetTuru .
  ?cinayetTuru crime:cinayet_turu ?cinayetTuruLabel.
}`,
            'single-location': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?cinayetKonumu
WHERE {
  crime:vaka_1 crime:konumudur ?konum .
  ?konum crime:cinayet_konumu ?cinayetKonumu .
}`,
            'single-time': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?cinayetTarihi
WHERE {
  crime:vaka_1 crime:zamanidir ?zaman .
  ?zaman crime:cinayet_tarih ?cinayetTarihi .
}`,
            'single-weapon': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?sucAleti
WHERE {
  crime:vaka_1 crime:delilidir ?delil .
  ?delil crime:suc_aleti ?sucAleti .
}`,
            'single-courtdate': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?davaBaslangic
WHERE {
  crime:vaka_1 crime:davasidir ?dava .
  ?dava crime:dava_baslangic ?davaBaslangic .
}`,
            'single-court': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?mahkemeAdi ?mahkemeKonum
WHERE {
  crime:vaka_1 crime:davasidir crime:dava_1 .
  crime:dava_1 crime:mahkeme_adi ?mahkemeAdi .
  crime:dava_1 crime:mahkeme_konum ?mahkemeKonum .
}`,
            'single-defendants': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?sanikAdi ?sanikYasi ?sanikCinsiyet
WHERE {
  crime:vaka_1 crime:davasidir crime:dava_1 .
  crime:dava_1 crime:saniktir ?sanik .
  ?sanik crime:supheli_adi ?sanikAdi .
  ?sanik crime:supheli_yasi ?sanikYasi .
  ?sanik crime:supheli_cinsiyet ?sanikCinsiyet .
}`,
            'single-killer-sentence': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?katil ?katilAdi ?cezaTur
WHERE {
  crime:vaka_1 crime:isler ?katil .
  ?katil crime:katil_adi ?katilAdi .
  ?katil crime:ceza_alir ?ceza .
  ?ceza crime:ceza_tur ?cezaTur .
}`,
            'single-suspects-at-scene': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?supheliAdi ?supheliYasi ?supheliCinsiyet ?olayYerindeMiydi
WHERE {
  crime:vaka_1 crime:suphelidir ?supheli .
  ?supheli crime:supheli_adi ?supheliAdi .
  ?supheli crime:supheli_yasi ?supheliYasi .
  ?supheli crime:supheli_cinsiyet ?supheliCinsiyet .
  ?supheli crime:olay_yerinde_miydi ?olayYerindeMiydi .
}`,

            /* --- TÜM VAKA SORGULARI --- */
            'all-killers': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?katilAdi ?katilYasi ?katilCinsiyet
WHERE {
  ?vaka crime:isler ?katil .
  ?katil crime:katil_adi ?katilAdi .
  ?katil crime:katil_yasi ?katilYasi .
  ?katil crime:katil_cinsiyet ?katilCinsiyet .
}`,
            'all-victims': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?vaka ?maktulAdi ?maktulYasi ?maktulCinsiyet
WHERE {
  ?vaka crime:kurbanidir ?maktul .
  ?maktul crime:maktulun_adi ?maktulAdi .
  ?maktul crime:maktul_yas ?maktulYasi .
  ?maktul crime:maktul_cinsiyet ?maktulCinsiyet .
}`,
            'all-suspects': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

# Not: Burada ontolojinizde "şüpheli" ile ilgili bireyler nasıl tanımlandığına göre değişiklik yapabilirsiniz
SELECT ?vaka ?supheliAdi ?supheliYasi ?supheliCinsiyet
WHERE {
  ?vaka crime:suphelidir ?supheli .
  ?supheli crime:supheli_adi ?supheliAdi .
  ?supheli crime:supheli_yasi ?supheliYasi .
  ?supheli crime:supheli_cinsiyet ?supheliCinsiyet .
}`,
            'all-crime-types': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?vaka ?cinayetTuruLabel
WHERE {
  ?vaka crime:cinayet_turudur ?cinayetTuru .
  ?cinayetTuru crime:cinayet_turu ?cinayetTuruLabel .
}`,
            'all-locations': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?vaka ?cinayetKonumu
WHERE {
  ?vaka crime:konumudur ?konum .
  ?konum crime:cinayet_konumu ?cinayetKonumu .
}`,
            'all-times': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?vaka ?cinayetTarihi
WHERE {
  ?vaka crime:zamanidir ?zaman .
  ?zaman crime:cinayet_tarih ?cinayetTarihi .
}`,
            'all-weapons': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?vaka ?sucAleti
WHERE {
  ?vaka crime:delilidir ?delil .
  ?delil crime:suc_aleti ?sucAleti .
}`,
            'all-courtdates': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

# Not: Ontolojide "davaların başlangıç tarihi" vaka-bazlı mı yoksa dava-bazlı mı tanımlı, kontrol ediniz
SELECT ?vaka ?davaBaslangic
WHERE {
  ?vaka crime:davasidir ?dava .
  ?dava crime:dava_baslangic ?davaBaslangic .
}`,
            'all-courts': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?dava ?mahkemeAdi ?mahkemeKonum
WHERE {
  ?vaka crime:davasidir ?dava .
  ?dava crime:mahkeme_adi ?mahkemeAdi .
  ?dava crime:mahkeme_konum ?mahkemeKonum .
}`,
            'all-defendants': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?vaka ?dava ?sanikAdi ?sanikYasi ?sanikCinsiyet
WHERE {
  ?vaka crime:davasidir ?dava .
  ?dava crime:saniktir ?sanik .
  ?sanik crime:supheli_adi ?sanikAdi .
  ?sanik crime:supheli_yasi ?sanikYasi .
  ?sanik crime:supheli_cinsiyet ?sanikCinsiyet .
}`,
            'all-defendants-lawyers': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?sanik ?avukat_ismi
WHERE {
    ?sanik crime:sanigin_avukatidir ?avukat .
    ?avukat crime:avukat_adi ?avukat_ismi
}`,
            'all-victim-lawyers': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?dava ?avukat_ismi
WHERE {
    ?dava crime:maktulun_avukatidir ?avukat .
    ?avukat crime:avukat_adi ?avukat_ismi
}`,
            'all-killer-sentences': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?vaka ?katil ?katilAdi ?cezaTur
WHERE {
  ?vaka crime:isler ?katil .
  ?katil crime:katil_adi ?katilAdi .
  ?katil crime:ceza_alir ?ceza .
  ?ceza crime:ceza_tur ?cezaTur .
}`,

            /* --- KOMPLEKS SORGULAR --- */
            'age-groups': `PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?yasGrubu (COUNT(?katil) AS ?katilSayisi) 
       ((COUNT(?katil) * 100.0 / ?toplamKatil) AS ?yuzde)
WHERE {
  {
    SELECT (COUNT(?katil) AS ?toplamKatil)
    WHERE {
      ?katil crime:katil_yasi ?katilYasi .
    }
  }
  ?katil crime:katil_yasi ?katilYasi .
  BIND(
    IF(?katilYasi >= 20 && ?katilYasi < 30, "20-30",
    IF(?katilYasi >= 30 && ?katilYasi < 40, "30-40",
    IF(?katilYasi >= 40 && ?katilYasi < 50, "40-50", "Diğer"))) AS ?yasGrubu
  )
}
GROUP BY ?yasGrubu ?toplamKatil
ORDER BY DESC(?katilSayisi)`,
            'crime-type-gender': `# Bu örnekte iki kısım sorgu gösterilmişti. 
# Birincisi detaylı tablo sorgusu, ikincisi yüzdelik toplama dair sorgu.
# İsteğe göre sadece birini ya da ikisini ayrı menü öğesi olarak kullanabilirsiniz.

# Detaylı tablo:
PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?vaka ?cinayetTuruLabel ?maktulAdi ?maktulYasi ?maktulCinsiyet 
       ?katilAdi ?katilYasi ?katilCinsiyet ?kategori
WHERE {
  ?vaka crime:cinayet_turudur ?cinayetTuru .
  ?cinayetTuru crime:cinayet_turu ?cinayetTuruLabel .

  ?vaka crime:kurbanidir ?maktul .
  ?maktul crime:maktulun_adi ?maktulAdi .
  ?maktul crime:maktul_yas ?maktulYasi .
  ?maktul crime:maktul_cinsiyet ?maktulCinsiyet .

  ?vaka crime:isler ?katil .
  ?katil crime:katil_adi ?katilAdi .
  ?katil crime:katil_yasi ?katilYasi .
  ?katil crime:katil_cinsiyet ?katilCinsiyet .

  BIND(
    IF(?cinayetTuruLabel = "kadın cinayeti" && ?maktulCinsiyet = "Kadın" && ?katilCinsiyet = "Erkek", 
       "Kadın cinayeti - Erkek Katil", 
    IF(?cinayetTuruLabel = "seri cinayet" && ?katilCinsiyet = "Erkek" && ?maktulCinsiyet = "Erkek", 
       "Seri cinayet - Erkek Maktul ve Katil", 
    IF(?cinayetTuruLabel = "şiddet içerikli cinayet" && ?katilCinsiyet = "Kadın", 
       "Şiddet içerikli cinayet - Kadın Katil", 
       "Diğer"))) AS ?kategori
  )
}
ORDER BY ?vaka


# Yüzdesel dağılım (ikinci bir sorgu):
#
# PREFIX crime: <http://www.semanticweb.org/hp/ontologies/2024/10/crime_ontology#>
# PREFIX owl: <http://www.w3.org/2002/07/owl#>
# PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#
# SELECT ?kategori (COUNT(?vaka) AS ?toplamVakaSayisi) 
#        ((COUNT(?vaka) * 100.0) / ?genelToplam AS ?yuzdelikOran)
# WHERE {
#   ?vaka crime:cinayet_turudur ?cinayetTuru .
#   ?cinayetTuru crime:cinayet_turu ?cinayetTuruLabel .
#   ?vaka crime:kurbanidir ?maktul .
#   ?maktul crime:maktul_cinsiyet ?maktulCinsiyet .
#   ?vaka crime:isler ?katil .
#   ?katil crime:katil_cinsiyet ?katilCinsiyet .
#   BIND(
#     IF(?cinayetTuruLabel = "kadın cinayeti" && ?maktulCinsiyet = "Kadın" && ?katilCinsiyet = "Erkek", 
#        "Kadın cinayeti - Erkek Katil", 
#     IF(?cinayetTuruLabel = "seri cinayet" && ?katilCinsiyet = "Erkek" && ?maktulCinsiyet = "Erkek", 
#        "Seri cinayet - Erkek Maktul ve Katil", 
#     IF(?cinayetTuruLabel = "şiddet içerikli cinayet" && ?katilCinsiyet = "Kadın", 
#        "Şiddet içerikli cinayet - Kadın Katil", 
#        "Diğer"))) AS ?kategori
#   )
#   {
#     SELECT (COUNT(?vaka) AS ?genelToplam) WHERE {
#       ?vaka crime:cinayet_turudur ?cinayetTuru .
#     }
#   }
# }
# GROUP BY ?kategori ?genelToplam
# ORDER BY DESC(?toplamVakaSayisi)
`
        };

        // Menüde bir başlığa tıklandığında ilgili bölümü açıp kapatan fonksiyon
        function toggleSection(sectionId) {
            const content = document.getElementById(sectionId);
            const header = content.previousElementSibling;
            const isCollapsed = header.classList.contains('collapsed');
            
            // Önce tüm section'ları kapat
            document.querySelectorAll('.section-content').forEach(section => {
                section.style.display = 'none';
                section.previousElementSibling.classList.add('collapsed');
            });

            // Tıklanan section kapalıysa aç
            if (isCollapsed) {
                content.style.display = 'block';
                header.classList.remove('collapsed');
            }
        }

        // Tıklanan menüye göre SPARQL sorgusunu textarea'ya yazdıran fonksiyon
        function setQuery(queryType, description) {
            // Tüm menülerde aktif sınıfını kaldır
            document.querySelectorAll('.menu-item').forEach(item => {
                item.classList.remove('active');
            });
            // Tıklanan menüye aktif sınıfını ekle
            event.target.closest('.menu-item').classList.add('active');

            // Sorgu ve açıklama alanlarını doldur
            document.getElementById('queryInput').value = queries[queryType];
            document.getElementById('queryDescription').textContent = description;
        }

        // "Sorguyu Çalıştır" butonuna basılınca çalışan fonksiyon
        async function executeQuery() {
            const query = document.getElementById('queryInput').value;
            if (!query.trim()) {
                alert('Lütfen bir sorgu girin');
                return;
            }

            // Form verisi oluştur
            const formData = new FormData();
            formData.append('sparql', query);
            
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                document.getElementById('queryResults').innerHTML = result.html;
            } catch (error) {
                console.error('Query error:', error);
                document.getElementById('queryResults').innerHTML = 
                    '<div class="alert alert-danger">Sorgu çalıştırılırken bir hata oluştu.</div>';
            }
        }

        // Sayfa ilk açıldığında bütün section'ları kapalı başlat
        document.querySelectorAll('.section-content').forEach(section => {
            section.style.display = 'none';
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(MAIN_TEMPLATE)

@app.route("/query", methods=["POST"])
def query():
    query_str = request.form.get("sparql", "").strip()
    if not query_str:
        return jsonify({
            "html": '<div class="alert alert-warning">Lütfen bir sorgu girin</div>'
        })
    
    try:
        # rdflib graph nesnesine ontolojiyi yüklüyoruz
        graph = world.as_rdflib_graph()
        graph.bind("crime", CRIME)
        
        # Sorguyu çalıştır
        results = list(graph.query(query_str))
        
        # Sonuç yoksa uyarı dön
        if not results:
            return jsonify({
                "html": '<div class="alert alert-info">Sonuç bulunamadı</div>'
            })

        # Değişken isimlerini alalım
        var_names = getattr(results, 'vars', None) or results[0].labels
        
        # HTML tablo oluşturma
        table = ['<div class="table-responsive">', '<table class="table">', '<thead><tr>']
        for var in var_names:
            table.append(f'<th>{var}</th>')
        table.append('</tr></thead><tbody>')
        
        for row in results:
            table.append('<tr>')
            for cell in row:
                table.append(f'<td>{cell}</td>')
            table.append('</tr>')
        table.append('</tbody></table></div>')
        
        return jsonify({"html": "".join(table)})
            
    except Exception as e:
        logging.error(f"Query error: {e}")
        return jsonify({
            "html": f'<div class="alert alert-danger">Hata: {str(e)}</div>'
        })

if __name__ == "__main__":
    # Flask uygulamasını başlatıyoruz
    app.run(debug=True, port=5000)
