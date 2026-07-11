BEGIN;

-- Running upgrade 093c47d4fb58 -> e75434db887c

CREATE TABLE factsheets (
    course_number VARCHAR(10) NOT NULL, 
    content TEXT NOT NULL, 
    version INTEGER DEFAULT 1 NOT NULL, 
    content_hash VARCHAR(64) NOT NULL, 
    updated_by UUID, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (course_number), 
    FOREIGN KEY(updated_by) REFERENCES users (user_id) ON DELETE SET NULL
);

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('001', '# Medicine (MBBS)
**Course Number:** 001
**Degree:** Bachelor of Medicine, Bachelor of Surgery (MBBS)
**Duration:** 5 years (plus one year compulsory internship)
**Entry Stream:** Biological Science
**Available at:** University of Colombo (001A), University of Peradeniya (001B), University of Sri Jayewardenepura (001C), University of Kelaniya (001D), University of Ruhuna (001E), University of Jaffna (001F), Eastern University (001G), Rajarata University (001H), South Eastern University (001I), Sabaragamuwa University (001J), Wayamba University (001K), Uva Wellassa University (001L)

---

## Overview

Medicine is the most competitive undergraduate degree in Sri Lanka and one of the most respected professional qualifications in the country. The MBBS degree trains students to become medical doctors capable of practising in government hospitals, private hospitals, and community health settings across Sri Lanka and internationally. The programme combines fundamental biomedical sciences with extensive clinical training across all major medical specialties.

Sri Lanka''s state university medical faculties are recognized by the Sri Lanka Medical Council (SLMC), and MBBS graduates must register with the SLMC before practising. The University of Colombo Faculty of Medicine, established in 1870, is the oldest and most prestigious medical school in South Asia.

---

## What You Will Study

The MBBS curriculum is structured across three phases:

**Pre-clinical Phase (Years 1–2):**
Anatomy (gross anatomy, histology, embryology), Physiology, Biochemistry, and introductory Pharmacology. Students spend extensive time in the dissection hall and laboratory. Basic science concepts are integrated with early clinical exposure through hospital visits.

**Para-clinical Phase (Year 3):**
Pathology, Microbiology, Pharmacology, Community Medicine, and Forensic Medicine. Students begin understanding disease mechanisms, drug actions, and public health principles. Case-based learning and problem-based learning sessions are introduced.

**Clinical Phase (Years 4–5):**
Rotations through Medicine, Surgery, Paediatrics, Obstetrics & Gynaecology, Psychiatry, Orthopaedics, Ophthalmology, ENT, Dermatology, Anaesthesia, and Emergency Medicine. Students spend most of their time in teaching hospitals attached to the university.

**Compulsory Internship (Year 6):**
One year of supervised practice — six months in Medicine and six months in Surgery — required for full SLMC registration and independent practice.

---

## Career Paths in Sri Lanka

- **Government medical service:** Junior doctors enter the government service as Medical Officers (MOs) in district and provincial hospitals. The Ministry of Health recruits MBBS graduates directly. Government service is compulsory for a set period after graduation.
- **Postgraduate specialization:** After 2–3 years of government service, doctors can sit the MD/MS entrance exam and pursue specialist training in Surgery, Internal Medicine, Paediatrics, Gynaecology, Psychiatry, Radiology, Pathology, Anaesthesia, and other disciplines. Specialist training takes 3–5 additional years.
- **Private practice:** After registration and sufficient experience, doctors may establish private clinics or join private hospitals (Asiri, Lanka Hospitals, Nawaloka, Durdans, etc.).
- **Academic medicine:** University hospitals offer teaching and research positions leading to academic careers.
- **International practice:** MBBS from Sri Lankan state universities is recognized in many countries. Further qualifying exams (PLAB for UK, AMC for Australia, USMLE for USA) open international pathways.
- **Public health and administration:** Senior Medical Officers move into health administration, district health roles, and Ministry positions.

---

## Entry Requirements

**A/L Stream:** Biological Science (mandatory)
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics at A/L
**O/L requirement:** Credit (C) passes in Sinhala/Tamil, English, Mathematics, Science, and typically 6 subjects total

**Z-score context:** Medicine is the most competitive programme in Sri Lanka. Typical qualifying Z-scores range from approximately **1.8 to 2.5+** depending on district and year. Students from educationally disadvantaged districts have access to the district quota (55%) and disadvantaged district quota (5%). The all-island merit pool (40%) is extremely competitive. Students within 0.05 of the cutoff should consider their result carefully — near-cutoff positions may or may not secure a place depending on the year.

---

## Differences Between Universities

- **Colombo (001A):** Oldest faculty, located at the Kynsey Road campus with the National Hospital of Sri Lanka as teaching hospital. Highest demand nationally.
- **Peradeniya (001B):** Strong research culture, Kandy Teaching Hospital as clinical base, pleasant hill country environment.
- **Sri Jayewardenepura (001C):** Relatively newer faculty, Sri Jayewardenepura Teaching Hospital, growing research output.
- **Kelaniya (001D):** North Colombo Teaching Hospital (Ragama) as primary teaching hospital.
- **Ruhuna (001E):** Southern province, Karapitiya Teaching Hospital, slightly lower Z-score cutoff.
- **Jaffna (001F):** Northern province, Teaching Hospital Jaffna, serves the north.
- **Others (EUSL, RUSL, SEUSL, SUSL, WUSL, UWU):** Newer faculties, regional teaching hospitals, somewhat lower cutoffs, excellent for students from provincial backgrounds.

---

## Special Notes

- The MBBS is a professional degree — not a Bachelor''s degree that leads directly to employment without further steps. Registration with the SLMC is required to practise.
- Medical education in Sri Lanka is conducted in English across all universities.
- Students who qualify but do not secure Medicine often pursue Biological Science, Pharmacy, Nursing, or Allied Health Sciences as strong alternative pathways.
- The degree is fully government-funded for state university students — no tuition fees, with a small activity fee only.
', 'f878cc9ec0bbca74209972a512ccc7c95c0eed33c4a2e36fd1419ad2d10b3833');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('002', '# Dental Surgery (BDS)
**Course Number:** 002
**Degree:** Bachelor of Dental Surgery (BDS)
**Duration:** 5 years (plus one year compulsory internship)
**Entry Stream:** Biological Science
**Available at:** University of Peradeniya Faculty of Dental Sciences (002A), University of Sri Jayewardenepura Faculty of Dental Sciences (002B)

---

## Overview

Dental Surgery is one of the most competitive and prestigious health sciences degrees in Sri Lanka, second only to Medicine among biological science students. The BDS degree trains students to become dentists capable of providing comprehensive oral healthcare services including diagnosis, treatment, and prevention of dental and oral diseases.

The Faculty of Dental Sciences at the University of Peradeniya, established in 1943, is the premier dental school in Sri Lanka and one of the oldest in South Asia. USJ introduced its Faculty of Dental Sciences more recently, offering a second state-university pathway.

BDS graduates must register with the Sri Lanka Medical Council (SLMC) to practise. After graduation and internship, dentists can work in government or private settings, or pursue postgraduate specialization.

---

## What You Will Study

The BDS curriculum integrates biomedical sciences with clinical dental training:

**Year 1 — Basic Sciences:**
Anatomy (head, neck, and general), Physiology, Biochemistry, Dental Materials Science, Introduction to Oral Biology, Community Dentistry fundamentals.

**Year 2 — Pre-clinical:**
Oral Anatomy, Oral Histology, Dental Pathology, Pharmacology, Microbiology, Pre-clinical Dental Skills (using dental simulators and phantom heads). Students practice tooth preparations, crown fabrication, and basic procedures on models before treating patients.

**Year 3 — Para-clinical:**
Oral Medicine, Oral Pathology, Radiology, Periodontology (gum disease), Basic Restorative Dentistry (fillings), Introduction to Prosthodontics (dentures).

**Years 4–5 — Clinical:**
Full clinical training across all departments: Conservative Dentistry and Endodontics (root canal treatment), Prosthodontics (dentures, crowns, bridges), Periodontology, Oral Surgery, Paediatric Dentistry, Orthodontics (braces), Oral Medicine, Community Dentistry clinics. Students treat real patients under supervision.

**Departments at Peradeniya:**
Basic Sciences, Community Dental Health, Comprehensive Oral Health Care, Oral Medicine and Periodontology, Oral Surgery, Oral Pathology, Prosthetic Dentistry, Restorative Dentistry.

**Compulsory Internship (Year 6):**
One year of supervised dental practice in government dental clinics or hospital settings.

---

## Career Paths in Sri Lanka

- **Government dental service:** Government dentists (Medical Officers — Dental) work in district hospitals, base hospitals, community dental clinics, and school dental services across Sri Lanka. The Ministry of Health maintains a national dental service.
- **Private practice:** After sufficient experience, dentists establish private clinics or join dental group practices. Private dentistry is a highly profitable career in urban and suburban Sri Lanka.
- **Postgraduate specialization:** Specialist training leads to qualifications in Orthodontics, Oral Surgery, Periodontology, Prosthodontics, Paediatric Dentistry, Oral Medicine, Oral Pathology, Community Dentistry. Training can be done locally or abroad (UK, Australia, India).
- **Academic dentistry:** Dental school lecturers and researchers.
- **Hospital dentistry:** Specialist consultants in teaching hospitals.
- **International practice:** BDS from Sri Lankan state universities is recognized in several countries. MFDS/MJDF examinations (UK) or ADC (Australia) examinations allow overseas practice.
- **Military dental corps:** Sri Lanka Army, Navy, and Air Force maintain dental services.

---

## Entry Requirements

**A/L Stream:** Biological Science (mandatory)
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics
**O/L requirements:** Credit passes in Sinhala/Tamil, English, Mathematics, and Science

**Z-score context:** Dental Surgery is the second most competitive Biological Science programme after Medicine. Typical qualifying Z-scores are in the **1.5 to 2.2** range depending on district and year. Peradeniya (002A) is more competitive than USJ (002B). Only around 100–120 students are selected nationally each year, making this a narrow intake.

---

## Differences Between Universities

- **Peradeniya (002A):** Oldest and most established dental school, 8 clinical departments, Peradeniya Teaching Hospital as the clinical base, strong postgraduate programme, highest reputation.
- **USJ (002B):** Newer faculty, Sri Jayewardenepura Teaching Hospital as clinical base, growing reputation, slightly lower cutoffs than Peradeniya.

---

## Special Notes

- Dental education is conducted in English at both universities.
- Students who qualify for Medicine but prefer a practice-based profession often choose Dental Surgery as their first preference.
- The dental equipment and materials required during training can involve personal costs — students should be prepared for some expenditure on instruments.
- Private dentistry in Sri Lanka is one of the highest-income professions, with experienced private practitioners earning significantly more than government salary scales.
', '2a57221635815d530442e40669a90b837f76ffbefa2125bef4cbc8fbd0d3fd41');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('003', '# Veterinary Science (B.V.Sc.)
**Course Number:** 003
**Degree:** Bachelor of Veterinary Science (B.V.Sc.)
**Duration:** 5 years
**Entry Stream:** Biological Science
**Available at:** University of Peradeniya Faculty of Veterinary Medicine and Animal Science (003A)

---

## Overview

Veterinary Science is offered exclusively at the University of Peradeniya and is among the most competitive Biological Science programmes in Sri Lanka. The Faculty of Veterinary Medicine and Animal Science, established in 1962, is the only state-university veterinary institution in the country.

Veterinarians diagnose and treat diseases in animals — livestock, pets, wildlife, and aquatic animals. In Sri Lanka, veterinary graduates play a critical role in food security (maintaining healthy livestock for meat, milk, and eggs), public health (zoonotic disease control — diseases that spread from animals to humans), wildlife conservation, and the growing companion animal sector.

---

## What You Will Study

The B.V.Sc. curriculum is intensive and covers all major animal species:

**Year 1 — Basic Sciences:**
Veterinary Anatomy, Physiology, Biochemistry, Histology, Embryology. Heavy emphasis on comparative anatomy of cattle, buffalo, horses, small ruminants (sheep, goats), pigs, poultry, dogs, and cats.

**Year 2 — Pre-clinical:**
Veterinary Microbiology, Pathology, Pharmacology, Parasitology. Understanding how diseases develop, the agents that cause them, and how drugs work in different species.

**Year 3 — Clinical Foundation:**
Clinical Examination Techniques, Diagnostic Methods, Radiology, Anaesthesia, Surgical Principles. Students begin supervised clinical rotations in the teaching veterinary hospital.

**Year 4–5 — Clinical Rotations:**
Large Animal Medicine and Surgery (cattle, buffalo), Small Animal Medicine and Surgery (dogs, cats), Poultry Medicine, Wildlife Medicine, Reproductive Technology and Theriogenology (reproductive medicine), Aquatic Animal Health, Veterinary Public Health, Meat Inspection, Farm Management.

**Five Academic Departments:**
- Basic Veterinary Sciences
- Veterinary Pathobiology
- Veterinary Public Health and Pharmacology
- Veterinary Clinical Sciences
- Farm Animal Production and Health

---

## Career Paths in Sri Lanka

- **Government veterinary service:** The Department of Animal Production and Health (DAPH) employs Veterinary Surgeons at divisional, district, and provincial levels for livestock disease control, vaccination programmes, and advisory services. This is the largest employer of veterinarians in Sri Lanka.
- **Private veterinary practice:** Companion animal (small animal) clinics for dogs and cats in urban areas. Also large animal practice serving dairy farms, poultry farms, and livestock operations.
- **Livestock and poultry industry:** Technical managers and veterinary officers at commercial poultry farms (Cargills, Prima, local producers), dairy farms, pig farms, and cattle operations.
- **Meat inspection:** Government and private slaughterhouses require licensed veterinary inspectors to certify meat for human consumption (a public health role).
- **Food safety and public health:** DAPH, Ministry of Health, and food regulatory agencies (Food Control Unit) employ veterinarians in zoonotic disease control and food safety.
- **Wildlife conservation:** Department of Wildlife Conservation, elephant transit homes, national zoo (Dehiwala Zoo), and international conservation organizations (Dilmah Conservation, WWF Sri Lanka).
- **Military veterinary corps:** Sri Lanka Army has a veterinary corps for working animals.
- **Aquatic animal health:** NARA and fisheries sector for disease management in fish farms and sea-cage aquaculture.
- **Academic veterinary medicine:** Lecturers and researchers at the Faculty of Veterinary Medicine, Peradeniya.
- **Postgraduate and international practice:** M.Sc. or PhD in Veterinary Science, and overseas practice (UK RCVS examinations, Australian registration).

---

## Entry Requirements

**A/L Stream:** Biological Science (mandatory)
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Veterinary Science is highly competitive — typically **1.3 to 1.9** range. Only around 60–80 students are selected nationally per year, making the intake among the smallest of all degree programmes. Students from educationally disadvantaged districts have the benefit of district and disadvantaged-district quotas.

---

## Special Notes

- Veterinary education is conducted in English.
- Only one state university (Peradeniya) offers this degree — there is no alternative within the state university system.
- The growing companion animal sector in Sri Lanka (increasing pet ownership in urban areas) has significantly expanded the market for private small-animal veterinary practice.
- International animal welfare organizations and conservation bodies frequently partner with the Faculty of Veterinary Medicine for research and placement opportunities.
- Students considering Veterinary Science should genuinely enjoy working with animals — the clinical years involve direct and sometimes demanding animal handling.
', '2303de32b47b423c00a598f6a1cfd35a0437b70922faffd1fc15d7aa45750a31');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('004', '# Agriculture (B.Sc.)
**Course Number:** 004
**Degree:** Bachelor of Science in Agriculture (Honours) / Bachelor of Agricultural Technology and Management
**Duration:** 4 years
**Entry Stream:** Biological Science, Biosystems Technology
**Available at:** University of Jaffna Faculty of Agriculture (004A), Eastern University Faculty of Agriculture (004B), Rajarata University Faculty of Agriculture (004C)

---

## Overview

Agriculture degrees prepare graduates to modernize and manage Sri Lanka''s agricultural sector — one of the most important contributors to the national economy. Approximately 25% of Sri Lanka''s workforce is employed in agriculture, making this a profession with deep social significance. Course 004 specifically refers to Agriculture programmes at regional universities (Jaffna, Eastern, Rajarata), while the main Agriculture programmes at Peradeniya are listed under different course numbers (Agricultural Technology and Management — 039, Animal Science and Fisheries — 086, Food Science and Technology — 035).

Sri Lanka''s agriculture covers rice (paddy), vegetables, fruits, tea, rubber, coconuts, spices, and fisheries. Modern agriculture requires professionals trained in crop science, soil management, irrigation, pest management, post-harvest technology, and agribusiness.

---

## What You Will Study

**Year 1 — Agricultural Foundations:**
Crop Science (major crops of Sri Lanka), Soil Science, Agricultural Botany, Agricultural Chemistry, Animal Husbandry Basics, Agricultural Economics, Computing for Agriculture, Statistics.

**Year 2 — Applied Agriculture:**
Agronomy (crop management — rice, vegetables, field crops), Horticulture (fruits, ornamentals, vegetables), Plant Pathology (crop diseases), Agricultural Entomology (pest management, integrated pest management), Soil Fertility and Fertilizer Management, Farm Machinery and Power, Irrigation Principles.

**Year 3 — Specialization and Management:**
Plant Biotechnology and Tissue Culture, Post-Harvest Technology, Agribusiness and Farm Management, Extension Agriculture (teaching farmers modern methods), Agricultural Meteorology, Integrated Crop Management, Research Methods. Field research projects in local farming communities.

**Year 4 — Research and Professional:**
Dissertation on agricultural research question, Agricultural Policy and Development, Export Agriculture and Supply Chain, Rural Development, Professional Agriculture Practice.

---

## Career Paths in Sri Lanka

- **Department of Agriculture:** The largest employer. Agricultural Instructors (AI) and Agricultural Research Officers work with farmers in every district, introducing new varieties, pest control methods, and modern farming practices.
- **Mahaweli Development Authority:** Managing Sri Lanka''s largest irrigation and agricultural settlement project, which covers large areas of the North Central, Eastern, and Uva provinces.
- **Provincial agricultural departments:** Each province maintains an agricultural department employing graduates as extension officers.
- **Tea, rubber, and coconut industries:** Plantations companies (Malwatte Valley, Kelani Valley, Elpitiya Plantations) employ agricultural officers for estate management.
- **Seed certification and quality control:** Seed Certification Service, Department of Agriculture seed farms.
- **Agri-business:** Fertilizer companies, agrochemical companies (Hayleys Agro, CIC Agri Businesses, Prima Agro), seed companies.
- **NGOs and international development:** UNDP, FAO, World Food Programme, and international NGOs working on food security and rural development in Sri Lanka.
- **Research institutions:** Central Agricultural Research Institute, Horticultural Crops Research Development Institute, Field Crops Research Development Institute, and regional research stations.
- **Entrepreneurship:** Commercial farming, organic farming, greenhouse operations, and agri-tech ventures.
- **Postgraduate:** M.Sc. in Agriculture, Biotechnology, or Agricultural Economics, leading to research and academic careers.

---

## Entry Requirements

**A/L Stream:** Biological Science (primary); Biosystems Technology stream students may also be eligible
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Agriculture at regional universities (Jaffna 004A, Eastern 004B, Rajarata 004C) has relatively lower cutoffs — typically **0.4 to 0.9** range. These programmes serve the provincial agricultural communities and have smaller intakes than the main Peradeniya Agriculture programmes.

---

## Special Notes

- Agriculture graduates from Sri Lankan state universities are eligible for government service in the Department of Agriculture immediately after graduation.
- The growing global interest in sustainable agriculture, organic farming, and food security has increased the international career prospects for agriculture graduates.
- Students from farming families often return to transform their family farms using modern techniques — a valuable entrepreneurship path.
- Field visits, farm placements, and research at agricultural research stations are integral to the programme from early years.
', 'c65beb86bcadb573157350952a22346508cf88f5f47356947f3468212c96ad09');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('005', '# Food Science and Nutrition (B.Sc.)
**Course Number:** 005
**Degree:** Bachelor of Science (Honours) in Food Science and Nutrition
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** Wayamba University of Sri Lanka Faculty of Livestock, Fisheries and Nutrition, Department of Food Science and Nutrition (005A)

---

## Overview

Food Science and Nutrition at Wayamba University (WUSL) combines food technology with nutritional science and dietetics — preparing graduates for careers in clinical nutrition, community nutrition, food manufacturing, and public health. Wayamba University''s campus in Makandura, Gonawila (North Western Province) serves students from the Northwest and surrounding areas.

With Sri Lanka''s growing burden of diet-related non-communicable diseases (diabetes, obesity, cardiovascular disease) and ongoing challenges with child malnutrition and micronutrient deficiencies, nutrition professionals are increasingly critical to public health.

---

## What You Will Study

**Year 1 — Sciences Foundation:**
Biochemistry, Physiology, Organic Chemistry, Food Science Basics, Statistics.

**Year 2 — Core Nutrition and Food Science:**
Human Nutrition (macronutrients, micronutrients, energy balance), Food Microbiology, Food Chemistry, Maternal and Infant Nutrition, Nutritional Epidemiology (how diet affects disease rates in populations), Food Analysis Methods.

**Year 3 — Applied Nutrition and Technology:**
Clinical Nutrition (dietary management of diabetes, kidney disease, heart disease, cancer), Community Nutrition (programmes for school children, pregnant women, elderly), Food Product Development, Food Safety and HACCP, Nutritional Assessment methods (anthropometry, dietary surveys), Field placement in hospitals or community health settings.

**Year 4 — Research:**
Research Dissertation, Public Health Nutrition, Advanced Clinical Dietetics, Food Policy and Nutrition Policy.

---

## Career Paths in Sri Lanka

- **Clinical dietitian:** Hospitals (government and private) employ dietitians to manage clinical nutrition for in-patients with diabetes, kidney disease, surgical recovery, and other conditions.
- **Community nutrition officer:** Ministry of Health Nutrition Division, Food and Nutrition Policy Division — designing and implementing national nutrition programmes.
- **School nutrition:** Ministry of Education school meal programmes and nutrition education.
- **Food industry:** Product development, quality assurance, and food labelling in food manufacturing companies.
- **Research:** Medical Research Institute, Nutrition Coordination Division (Ministry of Health), UNICEF and WHO nutrition research.
- **International:** WHO, FAO, UNICEF, World Food Programme — all have nutrition technical officers working in developing countries.
- **Private practice:** Registered Dietitians providing consultation to individuals for weight management, sports nutrition, disease management.

---

## Entry Requirements

**A/L Stream:** Biological Science (mandatory)
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Food Science and Nutrition at WUSL (005A) has cutoffs typically in the **0.5 to 0.9** range — accessible to most Biological Science students.

---

## Special Notes

- Sri Lanka''s Ministry of Health employs Nutrition Officers as a formal cadre — a direct government career pathway.
- The combination of food technology and clinical nutrition skills makes graduates employable across both public health and food industry sectors — an unusually broad employment range.
- Sri Lanka''s child wasting and stunting rates (particularly in tea estate communities) mean that community nutrition remains a high-priority public health area with sustained government investment.
', '36180a9128ae682709a4ec5038efe6eae93b8f69f455cd0e703747b639623db6');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('006', '# Biological Science (B.Sc.)
**Course Number:** 006
**Degree:** Bachelor of Science (Honours) in Biological Science / B.Sc. (Honours) in Science
**Duration:** 4 years (Honours) or 3 years (General)
**Entry Stream:** Biological Science
**Available at:** University of Colombo Faculty of Science (006A), University of Peradeniya Faculty of Science (006B), University of Sri Jayewardenepura Faculty of Applied Sciences (006C), University of Kelaniya Faculty of Science (006D), University of Ruhuna Faculty of Science (006E), University of Jaffna Faculty of Science (006F)

---

## Overview

Biological Science is the foundation degree for students from the Biological Science A/L stream who do not enter Medicine, Dental Surgery, or Veterinary Science. It provides rigorous training in the life sciences — including Botany, Zoology, Microbiology, Biochemistry, Molecular Biology, and Biotechnology — and produces graduates for research, teaching, healthcare support, agriculture, and environmental management.

A B.Sc. (Honours) in Biological Science from a top university (Colombo, Peradeniya) is a highly respected research qualification. Many graduates go on to postgraduate study (M.Sc., M.Phil., PhD) in Sri Lanka or abroad, entering careers in research, academia, or specialized science industries.

---

## What You Will Study

Most universities offer a flexible degree where students take a broad base of biology subjects and then specialize through elective streams. The structure varies by university.

**Year 1 — Core Sciences:**
Cell Biology, Genetics, Molecular Biology, General Zoology, Plant Biology (Botany), General Chemistry, Biochemistry, Statistics, Scientific Communication.

**Year 2 — Breadth:**
Microbiology, Physiology (animal and plant), Ecology and Environmental Biology, Developmental Biology, Biostatistics and Bioinformatics, Laboratory techniques (PCR, electrophoresis, microscopy, cell culture).

**Year 3 — Specialization:**
Students choose a major: Zoology, Botany/Plant Sciences, Microbiology, Biochemistry, Molecular Biology and Biotechnology, Environmental Sciences, or Ecology. Core research skills are developed.

**Year 4 (Honours) — Research:**
Full research project / dissertation under a supervisor, advanced electives in chosen field, seminars, professional skills. Honours year is what distinguishes a 4-year degree from the 3-year general degree.

**Specific focus areas at different universities:**
- Colombo: Strong in Zoology, Botany, and Environmental Sciences
- Peradeniya: Strong in Molecular Biology, Biotechnology, and Ecology — with access to Peradeniya Botanical Gardens and diverse ecosystems
- SJP: Applied Sciences focus — Aquatic Bioresources, Urban Bioresources, Food Science links
- Kelaniya: Zoology, Plant Biology, Environmental Management
- Ruhuna: Coastal ecology, marine and fisheries sciences proximity

---

## Career Paths in Sri Lanka

- **Postgraduate research:** Many Biology graduates pursue M.Sc. or M.Phil. degrees at local universities or overseas, entering research careers in molecular biology, biotechnology, ecology, or environmental science.
- **Academic teaching:** After postgraduate qualifications, graduates teach at state universities, national schools, international schools, or vocational training institutions.
- **Healthcare and laboratory science:** Biology graduates work as laboratory technologists in hospitals, diagnostic laboratories (channelling labs), blood banks, and quality control labs.
- **Government research institutions:** Industrial Technology Institute (ITI), National Aquatic Resources Research & Development Agency (NARA), Coconut Research Institute, Tea Research Institute, Rubber Research Institute, and similar institutions recruit biology graduates as research officers.
- **Pharmaceuticals and biotech industry:** Pharmaceutical companies, medical device companies, and biotech startups in Sri Lanka.
- **Environmental consulting:** Environmental Impact Assessment (EIA) is legally required for many development projects in Sri Lanka. Environmental Science graduates work as consultants.
- **Conservation and wildlife:** Department of Wildlife Conservation, Forest Department, and international conservation NGOs (WWF, IUCN Sri Lanka Chapter).
- **Food and agriculture sector:** Quality assurance, food safety testing, and technical roles in food manufacturing.
- **Teaching in schools:** Biology teachers are in demand at A/L level across national schools.

---

## Entry Requirements

**A/L Stream:** Biological Science
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Biological Science at top universities (Colombo, Peradeniya) has cutoffs typically in the **0.9 to 1.4** range. Ruhuna and Jaffna have lower cutoffs, making this degree accessible to most Biology stream students. Students who narrowly miss Medicine typically have Z-scores well above the Biological Science cutoff at any university, so this is a reliable next-choice programme.

---

## Differences Between Universities

- **Colombo (006A):** Located in Colombo, 7 departments, strong research output, proximity to national institutions and hospitals for collaboration.
- **Peradeniya (006B):** Located in Kandy, access to Royal Botanical Gardens, diverse ecosystems, strong in plant and environmental sciences. One of the best science campuses in Sri Lanka.
- **SJP (006C):** Applied Sciences focus, newer programmes in Aquatic and Urban Bioresources, strong links with industry.
- **Kelaniya (006D):** Strong in Microbiology and Environmental Management, near Colombo.
- **Ruhuna (006E):** Southern Sri Lanka, proximity to southern coast and national parks for fieldwork.
- **Jaffna (006F):** Northern Sri Lanka, lower cutoffs, serves Northern Province students.

---

## Special Notes

- The Honours degree (4 years) is strongly recommended over the General degree (3 years) for students who may pursue postgraduate study, as most M.Sc./PhD programmes require an Honours qualification.
- Biology graduates with strong postgraduate qualifications (PhD) from reputable overseas universities are actively recruited as university lecturers in Sri Lanka, which is a shortage area.
- Sri Lanka''s rich biodiversity (endemic species, rainforests, marine zones) provides exceptional research opportunities for ecologists and conservationists trained here.
', '9784697b91489efdd32d62a8c14f7879e246105f746750ac081b77e2f8711afd');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('007', '# Applied Sciences
**Course Number:** 007
**Degree:** Bachelor of Science (Honours) in Applied Sciences
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** Rajarata University of Sri Lanka (007K), Sabaragamuwa University of Sri Lanka (007L), University of Vavuniya, Sri Lanka (007R)

---

## Overview

The Bachelor of Science in Applied Sciences is a multidisciplinary degree designed to bridge the gap between theoretical scientific knowledge and practical industrial application. In the Sri Lankan context, this degree is vital for producing graduates who can contribute to the nation’s agro-based industries, food technology sectors, environmental management, and emerging biotechnology fields. By focusing on the "applied" aspect, the curriculum ensures that students are not merely researchers, but problem-solvers capable of addressing real-world challenges in the local economy.

The programme is notable for its emphasis on laboratory-based learning and field exposure, which are critical for the Sri Lankan job market. Universities like Rajarata, Sabaragamuwa, and Vavuniya leverage their unique geographical locations to provide students with hands-on experience in regional industries, such as large-scale agriculture, water resource management, and rural development projects. This degree prepares students to transition seamlessly into roles that require both scientific literacy and operational management skills.

---

## What You Will Study

**Year 1: Foundation in Basic Sciences**
Focuses on core modules in Biology, Chemistry, Physics, and Mathematics. Students also undertake introductory courses in Computer Literacy and English for Academic Purposes to build a strong academic base.

**Year 2: Core Applied Modules**
Introduction to specialized applied fields such as Microbiology, Biochemistry, Applied Statistics, and Environmental Science. Students begin to explore the intersection of these subjects with industrial processes and laboratory safety protocols.

**Year 3: Specialization and Industrial Exposure**
Students choose a specialization track (e.g., Food Science, Biotechnology, or Environmental Management). This year includes advanced laboratory techniques, industrial field visits, and a mandatory industrial training component where students work within local firms or research institutes.

**Year 4: Advanced Research and Professional Development**
The final year is dedicated to a comprehensive individual research project (dissertation) that addresses a specific industrial or environmental problem in Sri Lanka. Students also study Management, Entrepreneurship, and Quality Assurance to prepare for leadership roles in the workforce.

---

## Career Paths in Sri Lanka

- **Quality Assurance Officer:** Working in food and beverage manufacturing companies like Ceylon Biscuits Limited (CBL) or Nestlé Lanka to ensure product safety and regulatory compliance.
- **Environmental Consultant:** Assessing environmental impacts for infrastructure projects with organizations like the Central Environmental Authority (CEA) or private consultancy firms.
- **Research Scientist:** Conducting R&D in agricultural biotechnology or crop improvement at the Industrial Technology Institute (ITI) or the Tea Research Institute (TRI).
- **Laboratory Manager:** Overseeing diagnostic or industrial testing labs in private hospitals or chemical manufacturing plants.
- **Production Supervisor:** Managing manufacturing lines in the pharmaceutical or agro-chemical sectors, ensuring efficiency and safety standards.
- **Postgraduate Study:** Pursuing M.Sc. or Ph.D. programmes in specialized fields like Molecular Biology, Environmental Science, or Industrial Management at universities like the University of Peradeniya or the University of Colombo.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Biological Science stream. Candidates must have obtained passes in Biology, Chemistry, and Physics/Mathematics. The Z-score requirement is highly competitive and varies annually based on the applicant pool and university-specific intake capacities. Some universities, such as the University of Vavuniya, may require candidates to pass an additional aptitude test. The medium of instruction is English; therefore, proficiency in technical English is essential for success.

---

## Differences Between Universities

- **Rajarata University (007K):** Offers a strong focus on agro-based applications and rural development, benefiting from its location in the North Central Province. It has deep ties with regional agricultural research stations.
- **Sabaragamuwa University (007L):** Known for a diverse range of applied specializations and a strong emphasis on industrial training, often collaborating with the plantation and processing sectors in the Sabaragamuwa region.
- **University of Vavuniya (007R):** Provides a unique perspective on applied sciences in the Northern Province, with a focus on post-war development, water resource management, and regional industrial revitalization. It is distinct in its requirement for an aptitude test for entry.

---

## Special Notes

Graduates of this programme are eligible for membership in various professional bodies depending on their specialization, such as the Institute of Biology, Sri Lanka (IOBSL) or the Institute of Chemistry, Ceylon (IChemC). While there is no mandatory licensing for general applied scientists, those entering the food or pharmaceutical sectors must adhere to the standards set by the Food and Drugs Authority. The degree is highly valued for overseas employment, particularly in technical and laboratory-based roles in the Middle East, Australia, and Europe, provided the graduate obtains the necessary professional certifications. Students are encouraged to pursue professional qualifications in Quality Management (e.g., ISO standards) alongside their degree to increase employability.', 'deed96bcf3c07fbfcf7cb11b7858e6197061eb1fea4f38553a579b5270d11c33');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('008', '# Engineering (B.Sc.Eng.)
**Course Number:** 008
**Degree:** Bachelor of Science in Engineering (B.Sc.Eng. Honours)
**Duration:** 4 years
**Entry Stream:** Physical Science (primarily), Engineering Technology
**Available at:** University of Peradeniya (008A), University of Moratuwa (008B), University of Ruhuna (008C), University of Sri Jayewardenepura (008D), University of Jaffna (008E), Eastern University (008F)

---

## Overview

Engineering is the second most competitive undergraduate degree in Sri Lanka. A B.Sc.Eng. degree from a Sri Lankan state university qualifies graduates for professional engineering practice and is recognized by the Institution of Engineers Sri Lanka (IESL). The University of Moratuwa is widely regarded as the premier engineering university in Sri Lanka, with the highest Z-score cutoffs in the country. The University of Peradeniya''s Faculty of Engineering has been training engineers since 1950 and is the oldest engineering faculty.

Sri Lankan engineering graduates are highly sought after both locally and internationally, with strong employment pathways in the construction sector, ICT industry, manufacturing, utilities, and consulting.

---

## What You Will Study

Engineering programmes share a common foundation in the first year and then branch into specializations. The core and specialization areas are:

**Common First Year (all universities):**
Engineering Mathematics, Engineering Physics, Engineering Drawing and Design, Workshop Technology, Fundamentals of Programming, Circuit Theory, and Engineering Chemistry.

**Specializations Available:**

**Civil Engineering:** Structural engineering, geotechnical engineering, hydraulics and water resources, transportation engineering, environmental engineering, construction management. Available at Peradeniya, Moratuwa, Ruhuna.

**Electrical and Electronic Engineering / Electrical Engineering:** Power systems, control systems, electronics, telecommunications, signal processing, microprocessors. Available at Peradeniya, Moratuwa, Ruhuna, SJP.

**Mechanical Engineering / Mechanical and Manufacturing Engineering:** Thermodynamics, fluid mechanics, manufacturing processes, machine design, robotics, mechatronics, CAD/CAM. Available at Peradeniya, Moratuwa, Ruhuna.

**Computer Engineering / Computer Science and Engineering:** Algorithms, software engineering, computer architecture, AI, machine learning, networks, cybersecurity. One of the fastest-growing specializations. Available at Moratuwa, Ruhuna (introduced 2020 with 200-student intake).

**Chemical and Process Engineering:** Chemical reaction engineering, process design, separation processes, polymer technology. Available at Moratuwa.

**Materials Science and Engineering:** Metallic, ceramic, polymer, and composite materials. Available at Moratuwa.

**Electronics and Telecommunication Engineering:** Wireless systems, networking, signal processing, embedded systems. Available at Moratuwa.

**Earth Resources Engineering:** Mineral exploration, mining engineering, geological engineering. Available at Moratuwa.

**Textile and Apparel Engineering:** Textile processes, apparel manufacturing technology. Available at Moratuwa.

**Marine Engineering and Naval Architecture:** Ship design, marine propulsion, marine structures, STCW maritime training. Available at Ruhuna (from 2022).

**Transport and Logistics Engineering:** Road and rail infrastructure, logistics systems, transport planning. Available at Moratuwa.

---

## Career Paths in Sri Lanka

- **Construction and infrastructure:** Civil engineers work with government agencies (Road Development Authority, National Water Supply & Drainage Board, Central Engineering Consultancy Bureau) and private contractors on roads, bridges, buildings, irrigation, and water projects.
- **ICT and software:** Computer and electronics engineers are heavily recruited by Sri Lanka''s booming IT/BPO sector. Companies like WSO2, IFS, Virtusa, hSenid, and hundreds of software firms hire engineering graduates.
- **Power and utilities:** Electrical engineers work with Ceylon Electricity Board (CEB), Lanka Electricity Company (LECO), and renewable energy companies in solar, wind, and hydro projects.
- **Manufacturing:** Mechanical and industrial engineers work in apparel, rubber, pharmaceutical, ceramic, and food manufacturing industries.
- **Consultancy:** Senior engineers establish or join engineering consultancy firms.
- **Postgraduate and academia:** Many graduates pursue MSc or PhD locally (Moratuwa, Peradeniya) or abroad (Australia, UK, USA, Germany) and return to teaching or research.
- **Overseas employment:** Sri Lankan engineers are in high demand in Australia, UK, Middle East, Canada, and Singapore. Washington Accord accreditation (held by Peradeniya, Moratuwa, Ruhuna faculties) enables direct recognition in member countries.
- **Chartered Engineer status:** After experience and assessment, graduates can become Chartered Engineers through IESL.

---

## Entry Requirements

**A/L Stream:** Physical Science (Combined Mathematics required), Engineering Technology
**Required subjects for Physical Science:** Combined Mathematics, Physics, and Chemistry
**Required subjects for Engineering Technology:** Engineering Technology stream subjects

**O/L requirements:** Minimum credit passes in Mathematics, Science, and English, plus other subjects per university requirements.

**Z-score context:** Engineering is the second most competitive programme nationally. Moratuwa (008B) carries the highest cutoffs — typically **1.8 to 2.3+** for popular specializations. Peradeniya (008A) is similarly competitive. Ruhuna (008C) and SJP (008D) have somewhat lower cutoffs, providing access for students in the 1.3–1.8 range in many years. Students below 1.3 should explore Engineering Technology (Course 102) as an alternative pathway.

---

## Differences Between Universities

- **Moratuwa (008B):** National leader, most diverse specializations (12+ departments), strongest industry links, located in Katubedda near Colombo.
- **Peradeniya (008A):** Pioneer faculty, strong in Civil and Electrical, Washington Accord accredited, pleasant hill country campus.
- **Ruhuna (008C):** Washington Accord accredited across four specializations (Civil, Electrical & Information, Mechanical, and the new Marine Engineering), growing Computer Engineering programme.
- **SJP (008D):** Newer faculty, Nugegoda campus, growing industry connections.
- **Jaffna (008E) / Eastern (008F):** Regional campuses serving Northern and Eastern provinces.

---

## Special Notes

- All engineering programmes at state universities are conducted in English.
- A one-year industrial training placement is compulsory in most programmes (typically in Year 3 or 4), providing real industry experience.
- Engineering graduates frequently rank among the highest-earning professionals in Sri Lanka immediately after graduation.
- Students who narrowly miss Engineering often pursue Physical Science (Course 013) or Engineering Technology (Course 102) as alternatives.
', '242d5c59afdb5f1c636637f5e3fc1b3106fff2d752962cff350117f7a4d4e81d');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('009', '# Engineering — Electronic and Mechatronics (EM)
**Course Number:** 009
**Degree:** Bachelor of Science (Honours) in Engineering — Electronic and Mechatronics
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** University of Moratuwa (009G)

---

## Overview

Engineering (EM) is the Electronic and Mechatronics Engineering specialization track at the University of Moratuwa''s Faculty of Engineering — one of the most prestigious and competitive engineering programmes in Sri Lanka. Students admitted under code 009G are directly placed into the Electronic and Mechatronics Engineering stream rather than competing for specialization allocation after the common first year.

Mechatronics is the integration of mechanical engineering, electronics, and computer control systems — the discipline behind robots, automated manufacturing lines, CNC machines, autonomous vehicles, and smart industrial systems. The University of Moratuwa is Sri Lanka''s premier engineering institution, consistently ranked among the top engineering schools in South Asia, with strong industry linkages and a highly employable graduate pool.

Sri Lanka''s manufacturing sector, export processing zones, and emerging technology industry increasingly demand mechatronics-trained engineers for automation, product development, and precision manufacturing. International demand (especially in Singapore, Germany, Japan, and the UAE) for mechatronics graduates is consistently strong.

---

## What You Will Study

**Year 1 — Engineering Foundations (Common with all Engineering disciplines):**
Engineering Mathematics, Mechanics, Electrical Technology, Engineering Drawing and Design, Thermodynamics, Computer Programming, Physics of Materials, Communication Skills.

**Year 2 — Core Engineering:**
Electronics Fundamentals, Mechanics of Materials, Fluid Mechanics, Theory of Machines, Electrical Machines, Analog and Digital Electronics, Control Systems, Manufacturing Processes, Instrumentation and Measurement.

**Year 3 — Mechatronics Core:**
Robotics and Automation, Advanced Control Systems, Embedded Systems and Microcontrollers, Electromechanical Systems, Power Electronics, Industrial Electronics, Actuators and Sensors, PLC Programming, Computer-Aided Engineering (CAE), Industrial Training (6–12 weeks in a manufacturing or automation company).

**Year 4 — Specialization and Research:**
Individual or group research project in robotics, automation, mechatronics product design, or advanced control. Electives from: Autonomous Systems, MEMS (Micro-Electro-Mechanical Systems), Advanced Robotics, Smart Manufacturing, Machine Vision, Renewable Energy Systems, AI in Industrial Applications.

---

## Career Paths in Sri Lanka

- **Automation and robotics engineering:** Design and deployment of industrial robots and automation systems. Key Sri Lankan employers: MAS Holdings (factory automation), Brandix, garment and apparel sector, export processing zone manufacturers.
- **Manufacturing and process engineering:** CNC machining, precision manufacturing, production systems optimization. Rubber, ceramics, apparel, and electronics manufacturing sectors.
- **R&D and product development:** Sri Lanka''s emerging tech startups (drones, smart devices, prototype manufacturing) increasingly hire mechatronics graduates.
- **Control systems engineering:** Power plant automation, building management systems, utility infrastructure. Ceylon Electricity Board, Lanka Coal, and large industrial complexes.
- **Overseas employment:** Singapore, South Korea, Japan, Germany, UAE, and Australia have consistent demand for mechatronics engineers — among the best internationally mobile Sri Lankan engineering graduates.
- **Automotive and aerospace supply chain:** Sri Lanka has growing aerospace MRO (maintenance, repair, overhaul) activity; mechatronics engineers serve this sector.
- **Postgraduate study:** MSc in Mechatronics, Robotics, Autonomous Systems, or Control Engineering at UoM, or abroad (University of Melbourne, Sheffield, NTU Singapore, TU Munich).

---

## Entry Requirements

**A/L Stream:** Physical Science
**Typical subjects:** Combined Mathematics + Physics + Chemistry
**Z-score context:** Engineering (EM) at Moratuwa has a **separate and typically higher cutoff** than the general Engineering (008G) pool because Electronic and Mechatronics is among the most sought-after specializations at UoM. Students who narrowly miss 009G may enter through the general 008G code and still have a chance of selecting Mechatronics during the specialization allocation, subject to performance. District quota applies.

---

## Special Notes

- The University of Moratuwa is accredited by the Institution of Engineers Sri Lanka (IESL). Graduates can apply for Graduate Member (GMIESL) status and work towards Chartered Engineer (CEng) recognition.
- The Faculty of Engineering at Moratuwa is consistently ranked the **#1 engineering faculty in Sri Lanka** and among the top in South Asia.
- Industrial training (typically 6–12 weeks) is mandatory and provides practical exposure in automation, manufacturing, or electronics firms.
- English is the medium of instruction.
- Graduates are among the highest-earning engineering professionals in Sri Lanka, particularly those who enter automation, robotics, or overseas employment.
- Course 010G at UoM (Transport Management and Logistics Engineering) is the other separately admitted engineering specialization track; both 009G and 010G require separate Z-score cutoffs.
', '24e7fc0e6b6ae1afee2815e09ea21198938d1523b9b15a598c24eadb642753ad');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('010', '# Engineering
**Course Number:** 010
**Degree:** Bachelor of the Science of Engineering (Honours)
**Duration:** 4 years
**Entry Stream:** Physical Science (A/L Mathematics stream)
**Available at:** University of Moratuwa (010G)

---

## Overview

The Bachelor of the Science of Engineering at the University of Moratuwa is the premier engineering qualification in Sri Lanka. As the nation’s leading technological university, the Faculty of Engineering provides a rigorous academic environment that combines theoretical excellence with practical application. This degree is the primary gateway for students aiming to become Chartered Engineers and leaders in the nation’s industrial and infrastructure sectors.

Engineering in Sri Lanka is a cornerstone of national development, spanning sectors from large-scale infrastructure projects like the Port City and expressway networks to the rapidly growing software and manufacturing industries. The University of Moratuwa is notable for its strong industry links, state-of-the-art research laboratories, and the Engineering Research Unit (ERU), which fosters innovation. Graduates are highly sought after by both local conglomerates and multinational corporations for their technical proficiency and problem-solving capabilities.

---

## What You Will Study

**Year 1: Foundation in Engineering**
Focuses on core mathematics, physics, and programming. Students are introduced to the fundamentals of engineering mechanics, thermodynamics, and electrical circuits, alongside English for technical communication.

**Year 2: Core Engineering Disciplines**
Students delve into discipline-specific modules based on their chosen field (e.g., Civil, Mechanical, Electrical, Chemical, Computer Science, Materials, or Textile). This year emphasizes advanced mathematics, engineering design, and laboratory-based experimentation.

**Year 3: Specialization and Industrial Training**
Students undertake advanced modules in their chosen specialization. A mandatory 6-month industrial training component is integrated, allowing students to apply classroom knowledge in real-world engineering firms or manufacturing plants across Sri Lanka.

**Year 4: Advanced Research and Design**
The final year is dedicated to a comprehensive individual research project (Final Year Project) that addresses a specific engineering challenge. Students also take elective modules in management, ethics, and specialized technical areas, preparing them for professional practice.

---

## Career Paths in Sri Lanka

*   **Civil Engineer:** Working with firms like Access Engineering or Maga Engineering on large-scale infrastructure, bridge construction, and water management.
*   **Software Engineer:** Developing systems for global tech companies or local firms like WSO2 and 99x, focusing on software architecture and AI.
*   **Electrical/Power Engineer:** Managing grid stability and renewable energy projects with the Ceylon Electricity Board (CEB) or private power sector companies.
*   **Manufacturing/Process Engineer:** Optimizing production lines in the apparel or FMCG sectors, working with companies like MAS Holdings or Brandix.
*   **Consultant/Project Manager:** Overseeing complex engineering projects, managing budgets, and ensuring regulatory compliance for private consultancy firms.
*   **Postgraduate Study:** Pursuing M.Sc. or Ph.D. degrees at the University of Moratuwa or abroad to specialize in fields like Robotics, Sustainable Energy, or Structural Engineering.

---

## Entry Requirements

Admission is strictly based on the G.C.E. Advanced Level examination results in the Physical Science stream. Candidates must have high grades in Combined Mathematics, Physics, and Chemistry. Admission is highly competitive and determined by the Z-score system, which ranks students based on their district and national performance. An aptitude test or specific selection criteria may be enforced by the University Grants Commission (UGC) for certain engineering specializations. The medium of instruction is English.

---

## Differences Between Universities

While the University of Moratuwa (010G) is the primary state institution for this degree, other universities (such as Peradeniya, Ruhuna, and Jaffna) also offer Engineering degrees. Moratuwa is distinguished by its high concentration of specialized departments, extensive industry-sponsored research laboratories, and a long-standing reputation for producing the highest number of engineers who go on to obtain Chartered status. Its location in the Greater Colombo area provides students with unparalleled access to internships and networking opportunities with the country''s largest engineering firms.

---

## Special Notes

The degree is fully accredited by the Institution of Engineers, Sri Lanka (IESL), which is the mandatory body for obtaining Chartered Engineer status. Graduates are eligible to apply for IESL membership, which is recognized internationally under the Washington Accord. Students should be aware that the workload is intensive and requires a high level of commitment to both academic study and industrial training. Proficiency in English is essential, as all technical documentation and professional communication in the Sri Lankan engineering sector are conducted in English.', '99480dfa22747e6565b76e58017610749e39001f76fac87db9f3565beb8d0d5a');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('011', '# Quantity Surveying (B.Sc.)
**Course Number:** 011
**Degree:** Bachelor of Science (Honours) in Quantity Surveying
**Duration:** 4 years
**Entry Stream:** Physical Science, Engineering Technology
**Available at:** University of Moratuwa Department of Building Economics (011A)

---

## Overview

Quantity Surveying (QS) is a construction industry profession focused on the financial and contractual management of building and infrastructure projects. A Quantity Surveyor manages costs, contracts, procurement, and financial risk from the design stage through to project completion.

The Department of Building Economics at the University of Moratuwa is the only state-university provider of this degree in Sri Lanka, and produces graduates who are internationally recognized and in high demand. The Chartered Institute of Building (CIOB) and the Australian Institute of Quantity Surveyors (AIQS) both recognize Sri Lankan QS qualifications.

---

## What You Will Study

**Year 1 — Construction Fundamentals:**
Building Technology and Materials, Engineering Drawing, Construction Methods, Mathematics, Computing for Construction, Economics, Professional Communication.

**Year 2 — Measurement and Cost:**
Bill of Quantities (BOQ) Preparation, Construction Economics, Contract Law, Measurement of Building Works (SMM), Structural and Civil Engineering Basics, Procurement Systems.

**Year 3 — Contract Management:**
Construction Contract Administration, Project Cost Management, Value Engineering, Risk Management in Construction, Property Valuation, Facilities Management, Research Methods. Industrial training placement.

**Year 4 — Advanced Practice:**
Construction Project Management, Dispute Resolution (arbitration, claims, adjudication), International Construction, Real Estate Economics, Research Project / Dissertation.

---

## Career Paths in Sri Lanka

- **Government contracts:** Building projects for the Government Engineer''s Department, Urban Development Authority, Road Development Authority, and all public infrastructure contracts require QS services.
- **Private construction:** QS firms and construction companies managing cost and contracts for commercial buildings, apartments, hotels, hospitals, and factories.
- **Consultancy:** Independent QS consultancy firms (Rider Levett Bucknall, Davis Langdon, and local firms) providing cost consultancy to clients.
- **Project management:** Senior QS professionals move into overall project management roles.
- **Property development:** Cost planning and feasibility studies for real estate development projects.
- **International markets:** Sri Lankan QS graduates are highly sought in the Middle East (UAE, Qatar, Saudi, Oman), Singapore, and Australia — where construction booms create sustained demand.
- **Port City Colombo:** The large-scale Port City development provides years of QS employment in Sri Lanka itself.
- **Government valuation:** Government Valuation Department employs QS graduates for property valuation.

---

## Entry Requirements

**A/L Stream:** Physical Science (primary), Engineering Technology
**Required subjects:** Combined Mathematics + Physics + Chemistry (Physical Science)

**Z-score context:** Quantity Surveying at Moratuwa has cutoffs typically in the **1.0 to 1.5** range — competitive but noticeably lower than Engineering at Moratuwa. A strong choice for Physical Science students who want a practical construction profession.

---

## Special Notes

- QS is the only undergraduate programme at Moratuwa that does not require the aptitude test — unlike Architecture.
- Medium of instruction is English.
- Sri Lankan QS graduates working in the Middle East often earn USD 3,000–8,000+ per month — among the highest overseas earnings of any Sri Lankan professional category.
- The degree also provides pathways into the related Facilities Management programme (Course 056) offered by the same department.
', 'b5a7a5e95685fb53cb908cfd363219250196e7dd0d6c588bd1bfcec8ecc75cf3');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('012', '# Computer Science
**Course Number:** 012
**Degree:** Bachelor of Science (Honours) in Computer Science
**Duration:** 4 years
**Entry Stream:** Physical Science, Biological Science (some intakes), Mathematics
**Available at:** University of Colombo School of Computing — UCSC (012A), University of Sri Jayewardenepura Faculty of Computing (012B)

---

## Overview

Computer Science at UCSC is one of the most sought-after degrees in Sri Lanka''s growing IT industry. The University of Colombo School of Computing (UCSC) is a dedicated computing institution — the first of its kind in Sri Lanka — producing 250+ graduates annually with a documented 90% employability rate. The Faculty of Computing at USJ (formerly known as FCC) is a newer but rapidly growing computing faculty.

Sri Lanka''s IT and BPO industry contributes over USD 1 billion annually to exports and employs over 100,000 people, making Computer Science graduates among the most employed and highest-paid of all university graduates.

---

## What You Will Study

The Computer Science curriculum is rigorous and covers both theoretical foundations and practical software development skills.

**Year 1 — Foundations:**
Programming Fundamentals (Python, Java), Discrete Mathematics, Data Structures and Algorithms, Digital Logic and Computer Organization, Communication Skills for Computing, Introduction to Databases.

**Year 2 — Core Computing:**
Object-Oriented Programming, Operating Systems, Computer Networks, Database Management Systems, Software Engineering, Statistical Methods for Computing, Web Application Development, Human-Computer Interaction.

**Year 3 — Advanced Topics:**
Algorithms and Complexity, Artificial Intelligence, Machine Learning, Computer Graphics, Distributed Systems, Information Security, Mobile Application Development, Research Methods. Optional industrial training placement.

**Year 4 — Specialization and Research:**
Individual or group research project, optional electives in Data Science, Cloud Computing, Cybersecurity, Computer Vision, Natural Language Processing, Enterprise Systems. At UCSC, students also have access to the External BIT programme and postgraduate conversion pathways.

**UCSC''s Three Departments:**
- Department of Computation and Intelligent Systems (AI, ML, algorithms)
- Department of Information Systems Engineering (databases, enterprise systems)
- Department of Communication and Media Technologies (networks, multimedia)

---

## Career Paths in Sri Lanka

- **Software development:** The largest employer of CS graduates. Roles include Frontend Developer, Backend Developer, Full-Stack Developer, Mobile Developer. Companies range from global tech firms (Calcey, IFS, Virtusa, WSO2, 99X) to startups.
- **Data science and AI:** Growing rapidly in Sri Lanka. Roles in data analytics, machine learning engineering, business intelligence, data engineering.
- **Cybersecurity:** Increasingly in demand. Roles in security operations, penetration testing, security architecture.
- **Cloud and DevOps:** Cloud architects and DevOps engineers are among the highest-paid roles in the Sri Lankan tech sector.
- **IT consultancy:** Senior professionals in ERP implementation, systems integration, digital transformation.
- **Product management:** CS graduates with business aptitude move into product ownership and technical project management.
- **Postgraduate study:** MSc programmes in UCSC, Moratuwa, or abroad (Australia, UK, USA, Singapore) for research or advanced specialization.
- **Freelancing and entrepreneurship:** Sri Lanka has a growing freelancing community; many CS graduates build global client bases independently.
- **Academia:** Lecturers and researchers at state and private universities.

---

## Entry Requirements

**A/L Stream:** Physical Science (primary pathway) or Biological Science for some intakes
**Typical subjects:** Combined Mathematics + Physics + Chemistry (Physical Science), or Biology + Chemistry + Physics

**Z-score context:** UCSC (012A) is highly competitive — typically **1.3 to 1.8** in recent years. USJ Computing (012B) has moderately lower cutoffs. The district quota applies, giving students from educationally disadvantaged districts better chances. Students who just miss CS often pursue Information Systems (096), Software Engineering (099), or Information Technology (026) as closely related alternatives.

---

## Differences Between Universities

- **UCSC (012A):** Standalone computing school, longest history, largest output (250+ graduates/year), dedicated industry partnerships, central Colombo location. Both Computer Science and Information Systems (096) programmes offered.
- **USJ FCC (012B):** Newer faculty but growing quickly. Also offers Software Engineering (099). Located in Nugegoda, close to Sri Lanka''s main IT corridor.

---

## Special Notes

- English is the medium of instruction at both institutions.
- UCSC also operates the largest external degree programme in IT in Sri Lanka (Bachelor of IT — BIT), which is separate from the internal Computer Science degree.
- Graduates from UCSC are in demand internationally, particularly in Australia, UK, UAE, and Singapore.
- Students interested in Computer Science but who take Arts or Commerce A/Ls should look at the external BIT degree or private institution pathways, as internal CS requires a Science A/L background.
', '6b5a8187e098ef601e69546595e889b9b515003f4802147dfdda2da0039fc0b5');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('013', '# Physical Science (B.Sc.)
**Course Number:** 013
**Degree:** Bachelor of Science (Honours) in Physical Science / B.Sc. (Honours) in Science
**Duration:** 4 years (Honours) or 3 years (General)
**Entry Stream:** Physical Science
**Available at:** University of Colombo Faculty of Science (013A), University of Peradeniya Faculty of Science (013B), University of Kelaniya Faculty of Science (013C), University of Sri Jayewardenepura Faculty of Applied Sciences (013D), University of Ruhuna Faculty of Science (013E), University of Jaffna Faculty of Science (013F)

---

## Overview

Physical Science is the foundation degree for Physical Science A/L students who do not enter Engineering. It provides deep training in Mathematics, Physics, Chemistry, and Statistics — the core quantitative disciplines that underpin engineering, finance, data science, research, and academia. A B.Sc. (Honours) in Physical Science is a stepping stone to many of Sri Lanka''s most intellectually demanding postgraduate programmes and careers.

This degree is ideal for students who love mathematics and physics, enjoy research and problem-solving, and want to keep multiple career doors open — including postgraduate specialization in Engineering, IT, Finance, or Fundamental Sciences.

---

## What You Will Study

Physical Science degrees offer flexibility. Students can major in Physics, Chemistry, Mathematics, Statistics, or combinations, depending on the university.

**Year 1 — Foundations:**
Calculus and Analysis, Linear Algebra, Classical Mechanics, Electromagnetism, Thermodynamics, Analytical Chemistry, Inorganic Chemistry, Organic Chemistry, Introduction to Programming (Python/Matlab), Laboratory work.

**Year 2 — Core Sciences:**
Quantum Mechanics, Mathematical Methods for Physics, Statistical Thermodynamics, Physical Chemistry, Organic Synthesis, Differential Equations, Numerical Methods, Data Analysis, Computer Simulation.

**Year 3 — Specialization:**
Students typically select a major (Physics, Chemistry, Mathematics, or Statistics) and take advanced courses. Examples:
- **Physics track:** Solid State Physics, Optics, Nuclear Physics, Electronics, Computational Physics
- **Chemistry track:** Spectroscopy, Environmental Chemistry, Polymer Chemistry, Biochemistry
- **Mathematics track:** Real Analysis, Complex Analysis, Abstract Algebra, Topology, Mathematical Modelling
- **Statistics track:** Probability Theory, Regression, Time Series, Stochastic Processes, Biostatistics

**Year 4 (Honours) — Research:**
Research project or dissertation in chosen specialization. Advanced seminars and professional development.

---

## Career Paths in Sri Lanka

- **Postgraduate in Engineering:** Many Physical Science graduates with strong Mathematics and Physics results pursue M.Sc. in Civil, Electrical, or Computer Engineering through universities like Moratuwa or overseas institutions, converting to engineering careers without having done an Engineering undergraduate degree.
- **Data science and analytics:** The quantitative strength of Physical Science (especially Mathematics and Statistics) maps directly onto data science roles. Graduates are highly sought by banks, telecoms, insurance companies, and tech firms.
- **Finance and actuarial science:** Mathematics and Statistics graduates enter banking, investment analysis, and actuarial roles (with additional actuarial exams — CT/CM series).
- **Teaching:** Physics, Chemistry, and Mathematics teachers at A/L level are in chronic shortage in Sri Lankan national schools. Physical Science graduates are among the best-qualified to fill these roles.
- **Research institutions:** ITI, Arthur C. Clarke Institute, SLINTEC, and various government scientific research bodies.
- **Pharmaceutical and chemical industry:** Chemistry graduates work in quality control, R&D, and regulatory roles in pharmaceutical companies.
- **Environmental science:** Environmental chemistry and physics applications in sustainability, pollution management.
- **Academia:** Lecturers in university science departments after postgraduate study.
- **ICT industry:** Physical Science graduates with programming skills enter software development, especially in embedded systems, scientific computing, and fintech.

---

## Entry Requirements

**A/L Stream:** Physical Science (mandatory)
**Required subjects:** Combined Mathematics, Physics, and Chemistry

**Z-score context:** Physical Science at Colombo and Peradeniya has cutoffs typically in the **0.8 to 1.3** range. Other universities are lower, making this degree accessible to most Physical Science students. Students who score in the 0.5–0.9 range can comfortably enter at Ruhuna, Jaffna, Eastern, or Rajarata.

---

## Differences Between Universities

- **Colombo (013A):** Strong in Chemistry and Environmental Sciences, 7 departments, good research infrastructure.
- **Peradeniya (013B):** Strongest Physics department in Sri Lanka, excellent Mathematics, beautiful campus environment, 9 departments.
- **Kelaniya (013C):** Growing Faculty of Science, Industrial Management department linking science to business.
- **SJP (013D):** Applied Sciences orientation, ICT-Physical Science combined tracks available.
- **Ruhuna (013E):** Southern province, accessible to Matara and Galle students.
- **Jaffna (013F):** Northern province, lower cutoff.

---

## Special Notes

- Physical Science graduates with Honours degrees and strong academic records are eligible to apply directly to engineering firms and IT companies without needing an engineering degree, particularly for software and data roles.
- The degree is highly valued in Singapore and Australia, where skilled Physical Scientists are recruited for research, finance, and technology roles.
- Students who love Mathematics should consider whether the related Statistics and Operations Research programme (Course 060) or Industrial Statistics and Mathematical Finance (Course 059) might offer a more focused career path.
', '52437f61a1ef8b8a748b82c9e612362778381f7229c5decd6c098ddf0d704c80');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('014', '# Surveying Science (B.Sc.)
**Course Number:** 014
**Degree:** Bachelor of Science (Honours) in Surveying Science / Geomatics
**Duration:** 4 years
**Entry Stream:** Physical Science, Engineering Technology
**Available at:** Sabaragamuwa University Faculty of Geomatics (014A)

---

## Overview

Surveying Science (also called Geomatics or Geospatial Science) is the discipline of measuring, mapping, and representing the Earth''s surface. Surveyors collect, process, and analyse spatial data for land management, infrastructure development, environmental monitoring, and disaster management. The Faculty of Geomatics at Sabaragamuwa University (Belihuloya campus) is the primary state-university centre for surveying education in Sri Lanka.

Sri Lanka''s rapid infrastructure development — roads, railways, real estate, irrigation, and the Colombo Port City — generates sustained demand for qualified surveyors.

---

## What You Will Study

**Year 1 — Geospatial Foundations:**
Fundamentals of Surveying, Mathematics (Calculus, Linear Algebra), Physics, Computing for Geomatics, Technical Drawing, Introduction to Remote Sensing.

**Year 2 — Core Surveying Sciences:**
Land Surveying Techniques (Total Station, GPS, GNSS), Geographic Information Systems (GIS — QGIS, ArcGIS), Photogrammetry (extracting measurements from aerial photographs and drone imagery), Geodesy (the shape and size of the Earth), Cartography (map making), Hydrographic Surveying (underwater mapping).

**Year 3 — Advanced and Applied:**
Remote Sensing and Satellite Imagery Analysis, Cadastral Surveying (land ownership boundaries), Land Law and Land Registry (Sri Lanka''s land registration system), Engineering Surveying (setting out roads, buildings, tunnels), Valuation basics, Research Methods. Field practical camps are a major component.

**Year 4 — Research:**
Research Dissertation, Urban Remote Sensing, Disaster Management GIS (mapping flood zones, landslide risk), Spatial Data Infrastructure, GIS Application Development.

---

## Career Paths in Sri Lanka

- **Survey Department (government):** Sri Lanka''s Survey Department is the primary mapping authority — maintaining the national topographic map series, cadastral records (land boundaries), and geodetic network. Surveyors are recruited as technical officers.
- **Land Registry and Land Commissioner''s Department:** Managing land ownership records and resolving boundary disputes.
- **Road Development Authority (RDA):** Engineering surveyors for road design and construction.
- **National Physical Planning Department:** Spatial planning and land use mapping.
- **Construction and real estate:** Licensed Surveyors are required for all land subdivisions and building permit applications in Sri Lanka. Private surveying firms service the construction industry.
- **GIS and spatial technology:** Government agencies, telecoms, utilities, and private companies are building GIS capabilities — spatial analysts and GIS developers are in growing demand.
- **Disaster risk management:** National Disaster Relief Services Centre and provincial disaster management units use GIS for flood and landslide mapping.
- **International:** Middle East construction projects, Australia, and Singapore employ surveyors.

---

## Entry Requirements

**A/L Stream:** Physical Science (primary), Engineering Technology
**Required subjects:** Combined Mathematics + Physics + Chemistry

**Z-score context:** Surveying Science cutoffs are typically in the **0.6 to 1.1** range — accessible to Physical Science students across a wide range.

---

## Special Notes

- Licensed Surveying is a regulated profession in Sri Lanka. After graduation and experience, graduates can sit the Sri Lanka Surveyors Institute (SLSI) examination to become Licensed Surveyors.
- Drone (UAV) surveying and LiDAR scanning are transforming the profession — graduates with drone surveying skills are increasingly valued.
- GIS software skills (QGIS, ArcGIS, ERDAS) developed during the degree are immediately commercially applicable.
- Belihuloya campus (Sabaragamuwa University) is in the hill country — fieldwork in diverse terrain (mountains, plains, coasts) provides excellent practical experience.
', '11a59ce5afbbe7a407c0af06e48f616fbdaaf85376b69557d4874d4406f2bc98');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('015', '# Applied Sciences
**Course Number:** 015
**Degree:** Bachelor of Science (Honours) in Applied Sciences
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** 
- Rajarata University of Sri Lanka (015K)
- Sabaragamuwa University of Sri Lanka (015L)
- Wayamba University of Sri Lanka (015M)
- University of Vavuniya, Sri Lanka (015R)
- Trincomalee Campus, Eastern University, Sri Lanka (015W)

---

## Overview

The Bachelor of Science in Applied Sciences is a multidisciplinary degree designed to bridge the gap between pure scientific theory and industrial application. Unlike traditional B.Sc. degrees that focus primarily on academic research, this programme emphasizes the practical utility of science in sectors such as manufacturing, food technology, information technology, and environmental management. In the Sri Lankan context, this degree is vital for producing graduates who can contribute to the country’s industrial growth and sustainable development goals.

The programme is highly valued by local industries because it integrates core scientific principles with management and technical skills. Graduates are equipped to solve real-world problems, making them highly employable in both the public and private sectors. Each university offering this degree leverages its unique regional context—such as the agricultural focus of the Rajarata and Wayamba regions or the industrial and maritime focus of the Trincomalee and Sabaragamuwa regions—to provide students with specialized field experience and industry exposure.

---

## What You Will Study

**Year 1: Foundation in Basic Sciences**
Focuses on core modules in Mathematics, Physics, Chemistry, and Computer Science. Students build a strong theoretical foundation while being introduced to the philosophy of applied sciences and laboratory safety protocols.

**Year 2: Core Applied Modules**
Introduction to specialized areas such as Applied Statistics, Electronics, Industrial Chemistry, and Environmental Science. Students begin to bridge the gap between theory and practice through intensive laboratory work and field visits to local manufacturing plants.

**Year 3: Specialization and Technical Skills**
Students select a specialization track (e.g., Industrial Physics, Applied Mathematics, or Computing). Coursework includes advanced modules in Quality Control, Project Management, and specialized software applications relevant to the chosen industry.

**Year 4: Research and Industrial Training**
The final year is dedicated to a mandatory Industrial Training placement (usually 6 months) and a comprehensive Final Year Research Project. Students must apply their knowledge to solve a specific industrial problem, culminating in a thesis and a professional presentation.

---

## Career Paths in Sri Lanka

- **Quality Assurance (QA) Executive:** Working in food and beverage companies like Ceylon Biscuits Limited (CBL) or Nestlé Lanka to ensure products meet safety and quality standards.
- **Production/Process Engineer:** Managing production lines in manufacturing sectors, including apparel or chemical processing plants, ensuring efficiency and technical compliance.
- **Data Analyst/Statistician:** Providing data-driven insights for financial institutions, telecommunications providers like Dialog or SLT-Mobitel, and market research firms.
- **Environmental Consultant:** Working with organizations like the Central Environmental Authority (CEA) or private consultancy firms to manage waste, water quality, and environmental impact assessments.
- **IT/Software Developer:** Utilizing computational skills in the booming Sri Lankan software industry, working with firms like Virtusa or WSO2.
- **Postgraduate Research:** Pursuing M.Sc. or Ph.D. programmes in specialized fields like Renewable Energy, Applied Statistics, or Biotechnology at local universities or via international scholarships.

---

## Entry Requirements

Admission is strictly based on the G.C.E. Advanced Level examination results under the Physical Science stream. Candidates must have passed Physics, Chemistry, and Mathematics. The Z-score requirement is highly competitive and varies annually based on the applicant pool and the specific university''s intake capacity. The medium of instruction is English, and students are expected to have a strong command of the language for technical writing and presentations. No specific aptitude tests are required beyond the standard UGC selection process.

---

## Differences Between Universities

- **Rajarata University:** Strong focus on agricultural and food-based applied sciences, leveraging its location in the North Central Province.
- **Sabaragamuwa University:** Known for a diverse range of applied subjects and strong links to the plantation and processing industries in the Sabaragamuwa region.
- **Wayamba University:** Highly regarded for its focus on food technology and industrial management, with strong ties to the agro-industrial sector.
- **University of Vavuniya & Trincomalee Campus (EUSL):** These institutions offer unique regional perspectives, often focusing on community-based development, coastal resource management, and regional industrial growth, providing students with a distinct advantage in local development projects.

---

## Special Notes

Graduates of this programme are eligible for membership in various professional bodies depending on their specialization (e.g., the Institute of Chemistry Ceylon or the Computer Society of Sri Lanka). While this is not a professional engineering degree (like those accredited by IESL), it is highly recognized for technical and managerial roles in the industry. There is significant demand for these graduates in overseas markets, particularly in the Middle East and Australia, for roles in laboratory management and technical operations. Students are encouraged to seek internships early in their degree to maximize their employability upon graduation.', '47b18d4b4d8aae5f6b520eb260f92291a20bde0481b676ff788085efccc95301');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('016', '# Management
**Course Number:** 016
**Degree:** Bachelor of Business Administration (BBA) / Bachelor of Commerce (B.Com.) / Bachelor of Science in Management (Honours)
**Duration:** 4 years
**Entry Stream:** Commerce (primary), Arts, Physical Science (some universities)
**Available at:** University of Colombo Faculty of Management & Finance (016A), University of Sri Jayewardenepura Faculty of Management Studies and Commerce (016B), University of Kelaniya Faculty of Commerce and Management Studies (016C), University of Peradeniya Faculty of Management (016D), University of Ruhuna Faculty of Management and Finance (016E), University of Jaffna Faculty of Management Studies (016F)

---

## Overview

Management is one of the most popular undergraduate programmes in Sri Lanka, offering a broad business education that prepares graduates for careers in corporate management, banking, finance, marketing, and entrepreneurship. Nearly every major Sri Lankan state university offers a Management or Commerce degree, and collectively these faculties produce thousands of business graduates annually.

The University of Colombo Faculty of Management and Finance (FMF) has the highest reputation nationally, reporting a 94% employability rate among graduates. USJ''s Faculty of Management Studies and Commerce is the second most sought-after, followed by Kelaniya and Peradeniya.

---

## What You Will Study

Management programmes follow a broad business curriculum in early years before allowing specialization:

**Year 1 — Business Foundations:**
Principles of Management, Financial Accounting, Microeconomics, Macroeconomics, Business Mathematics and Statistics, Business Communication, Introduction to Marketing, Organizational Behaviour.

**Year 2 — Core Business:**
Financial Management, Cost and Management Accounting, Marketing Management, Human Resource Management, Operations Management, Business Law, Research Methods for Business, Management Information Systems.

**Year 3 — Specialization Electives:**
Students select a major area from options including: Accounting and Finance, Marketing Management, Human Resource Management, International Business, Operations Management, Entrepreneurship, Banking and Financial Services, Hospitality Management (some universities). Industry-sponsored projects are common in Year 3.

**Year 4 — Capstone:**
Strategic Management, Business Policy, Dissertation or Research Project, Advanced electives in chosen specialization, Leadership and Professional Development.

**Colombo (FMF) — 8 Departments:**
Accounting, Business Economics, Finance, Human Resources Management, International Business, Management Studies, Marketing Management, Tourism and Hospitality Management.

---

## Career Paths in Sri Lanka

- **Banking and financial services:** Largest employer of Management graduates. Commercial Bank, Bank of Ceylon, People''s Bank, HNB, NDB, Sampath Bank, NSB and dozens of licensed finance companies recruit every year for trainee management, credit, and operations roles.
- **Corporate management:** Trainees in large conglomerates (John Keells Holdings, Aitken Spence, Hemas Holdings, Singer, Cargills, Nestlé Lanka, Unilever) across functions: finance, HR, supply chain, marketing.
- **Marketing and brand management:** FMCG companies, advertising agencies, and digital marketing firms.
- **Accounting and audit:** With additional professional qualifications (CA Sri Lanka, ACCA, CIMA, CMA), Management graduates enter audit firms (KPMG, PwC, EY, Deloitte) and corporate finance roles.
- **Insurance:** National Insurance Trust Fund, Ceylinco Insurance, AIA, Allianz, and others recruit for underwriting, claims, and management roles.
- **Entrepreneurship:** Management education provides the business fundamentals for starting ventures. Government incubators (SLASSCOM, BOI) support graduate entrepreneurs.
- **Public sector management:** Government corporations, statutory boards, and ministries recruit management graduates for administration and financial roles.
- **Postgraduate study:** MBA programmes at University of Colombo, USJ, Kelaniya, Moratuwa, and internationally for career advancement.

---

## Entry Requirements

**A/L Stream:** Commerce (primary path); some universities accept Arts or Physical Science students into Management
**Typical Commerce A/L subjects:** Accounting, Business Studies/Economics, and one other (Logic, Geography, etc.)

**Z-score context:** Management at top universities (Colombo 016A, USJ 016B) is moderately competitive — typical cutoffs in the **0.8 to 1.4** range for Commerce stream. Kelaniya, Peradeniya, and Ruhuna faculties have lower cutoffs, making Management accessible to a wide range of Commerce students. Arts stream students who apply to Management programmes at universities that accept them typically face different (often higher) Z-score thresholds because they are competing with fewer seats from the Arts quota.

---

## Differences Between Universities

- **Colombo FMF (016A):** Highest reputation, 8 departments, located in central Colombo, strong industry placement network, 94% employability claimed. Offers BBA, MBA, DBA.
- **USJ (016B):** Second most prestigious, Nugegoda campus, strong commerce and management output, Faculty of Management Studies and Commerce.
- **Kelaniya (016C):** Faculty of Commerce and Management Studies, strong Northern-Western province links, Commerce and Financial Management departments.
- **Peradeniya (016D):** Newer management faculty, Kandy campus, serves Central and Uva provinces.
- **Ruhuna (016E):** Southern province focus, Matara campus, serves Southern Province students.
- **Jaffna (016F):** Serves Northern Province, Faculty of Management Studies.

---

## Special Notes

- Professional accounting qualifications (CA Sri Lanka, ACCA, CIMA) are highly complementary to a Management degree and significantly boost employability and salary. Many Management graduates pursue these while studying or immediately after graduation.
- Management degrees in Sri Lanka are typically offered in English, though some universities may have Sinhala or Tamil medium options.
- MBA programmes are widely available in Sri Lanka through both state universities and private institutions for career advancement after gaining work experience.
', 'b3d84fb9a26d382f09f6f8787f271af7cb8d46b49a403d0d22c4260636cb8662');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('017', '# Real Estate Management and Valuation (B.Sc.)
**Course Number:** 017
**Degree:** Bachelor of Science (Honours) in Real Estate Management and Valuation
**Duration:** 4 years
**Entry Stream:** Commerce, Physical Science
**Available at:** University of Sri Jayewardenepura Faculty of Management Studies and Commerce, Department of Estate Management and Valuation (017A)

---

## Overview

Real Estate Management and Valuation is a professional degree combining property economics, valuation methodology, real estate investment, property development management, and land law. It trains graduates for careers in the rapidly growing Sri Lankan property market — one of the most dynamic sectors of the economy, driven by the Colombo Port City development, luxury apartment construction, commercial real estate expansion, and government infrastructure projects.

Qualified real estate professionals are needed for property valuation (for loans, tax, legal purposes), investment analysis, property development management, and government land administration.

---

## What You Will Study

**Year 1 — Property and Business Foundations:**
Economics for Real Estate, Financial Accounting, Introduction to Property Law and Land Law in Sri Lanka, Built Environment Studies, Mathematics and Statistics for Property, Communication.

**Year 2 — Core Valuation:**
Principles of Valuation (methods: comparison, income, cost, investment, residual approaches), Urban Economics, Property Markets and Investment, Construction Technology for Valuers (understanding building quality), Real Estate Finance (mortgage lending, property investment financing), GIS and Mapping for Property.

**Year 3 — Advanced Practice:**
Property Development Process (feasibility, design management, construction, marketing, disposal), Commercial Property Valuation, Plant and Machinery Valuation, Real Estate Portfolio Management, Property Management (leases, maintenance, tenant relationships), Research Methods. Industrial training with a government valuation office or private firm.

**Year 4 — Research:**
Research Dissertation, Real Estate Investment Analysis (discounted cash flow, IRR), International Real Estate Markets, Compulsory Acquisition and Compensation, Property Taxation in Sri Lanka.

---

## Career Paths in Sri Lanka

- **Government Valuation Department:** The official government agency for property valuation — producing valuations for government land acquisitions, inheritance tax, stamp duty, and public sector property. A well-respected government service career.
- **Banks and finance:** Every bank providing mortgages requires independent property valuations from Incorporated Valuers. Private valuation firms contract to banks (Commercial Bank, Bank of Ceylon, HNB, Sampath) for panel valuation work.
- **Real estate development:** Property developers (Access Engineering, John Keells Holdings, Waterfront Properties, Softlogic, and many others) employ Real Estate Managers for project management and marketing.
- **Property management:** Managing commercial buildings, apartments, shopping complexes (One Galle Face, Colombo City Centre, Crescat).
- **Investment advisory:** Real estate investment advisors and fund managers.
- **Port City Colombo:** The massive Port City project is generating decades of property valuation and development work.
- **International:** Middle East (Dubai, Riyadh, Abu Dhabi), Singapore, Australia — all have active real estate industries recruiting Sri Lankan valuers.
- **Postgraduate:** MSc in Real Estate from local (USJ) or international universities.

---

## Entry Requirements

**A/L Stream:** Commerce (primary), Physical Science (also accepted)
**Typical Commerce subjects:** Accounting, Business Studies, Economics

**Z-score context:** Real Estate Management cutoffs are typically in the **0.7 to 1.2** range for Commerce stream — accessible to a wide range of Commerce students.

---

## Special Notes

- USJ''s Faculty of Management also offers an MSc in Real Estate Management and Valuation for postgraduate study.
- The Incorporated Valuer designation (obtained through the Institute of Valuers, Sri Lanka and after passing the professional exam) is the gold standard for private practice.
- Port City Colombo — a 269-hectare reclaimed land development with international financial city, residential, and entertainment zones — is the largest single real estate development in Sri Lanka''s history, generating enormous demand for real estate professionals over the coming decades.
- Sri Lanka''s stamp duty and land registration systems make real estate law knowledge an important part of every valuer''s professional toolkit.
', 'da21605e9dde805f6dc5865951bd30319a9e88129576d9da9bcf2526d34f259d');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('018', '# Commerce (B.Com.)
**Course Number:** 018
**Degree:** Bachelor of Commerce (B.Com. Honours)
**Duration:** 4 years
**Entry Stream:** Commerce (primary), Arts
**Available at:** University of Kelaniya Faculty of Commerce and Management Studies (018A), Eastern University Faculty of Commerce and Management (018B)

---

## Overview

Commerce is the classic business degree in Sri Lanka, focusing on accounting, business economics, and financial management. A B.Com. provides a broad commercial education combining theory and professional practice, with strong pathways into accounting, banking, auditing, and corporate finance.

The Faculty of Commerce and Management Studies at Kelaniya is one of the most established commerce faculties in Sri Lanka, producing thousands of graduates annually. Eastern University''s commerce programme serves the Eastern Province.

---

## What You Will Study

**Year 1 — Business and Accounting Foundations:**
Financial Accounting I, Business Mathematics, Microeconomics, Macroeconomics, Business Law, Business Communication, Introduction to Management.

**Year 2 — Core Commerce:**
Financial Accounting II, Cost and Management Accounting, Financial Management, Taxation, Auditing Principles, Business Statistics, Commercial Law (Companies Act, Sale of Goods).

**Year 3 — Advanced Commerce:**
Advanced Financial Accounting (Sri Lanka Accounting Standards — SLFRS/LKAS), Advanced Management Accounting, Corporate Finance, Banking and Financial Services, Investment Analysis, Income Tax Law, Research Methods.

**Year 4 — Specialization:**
Dissertation or Research Project, Strategic Management, International Business, Forensic Accounting, Advanced Auditing and Assurance, Contemporary Issues in Accounting and Finance.

---

## Career Paths in Sri Lanka

- **Professional accountancy:** B.Com. is the foundation for pursuing CA Sri Lanka (Chartered Accountancy), ACCA, CIMA, or CMA qualifications. Many Commerce graduates work at audit firms (KPMG, PwC, EY, Deloitte, SJMS Associates, Grant Thornton) while completing professional exams.
- **Banking:** Commercial Bank, Bank of Ceylon, People''s Bank, HNB, Sampath, NSB — all recruit B.Com. graduates as Management Trainees and Credit Officers.
- **Insurance and finance:** National Insurance Trust Fund, insurance companies, licensed finance companies, and leasing companies.
- **Taxation and audit:** Inland Revenue Department, Customs, and private tax consultancy firms.
- **Corporate finance:** Finance officers, accountants, and financial controllers at manufacturing and service companies.
- **Government finance:** Treasury, Auditor General''s Department, and government corporation finance departments.

---

## Entry Requirements

**A/L Stream:** Commerce (primary), Arts
**Typical Commerce subjects:** Accounting, Business Studies, Economics

**Z-score context:** Commerce at Kelaniya (018A) has cutoffs typically in the **0.7 to 1.2** range for Commerce stream students. Eastern University (018B) is lower. The degree is accessible to the majority of Commerce stream students.

---

## Special Notes

- Professional accountancy qualifications (CA Sri Lanka, ACCA, CIMA) greatly enhance B.Com. graduate employability and salaries.
- Sri Lanka''s adoption of Sri Lanka Financial Reporting Standards (SLFRS, aligned with IFRS) means B.Com. graduates are trained in internationally recognized accounting standards.
- Kelaniya''s Faculty of Commerce also offers Financial Economics (131), Accounting Information Systems (127), and Financial Engineering (110) as related programmes.
', '53d8a25e88185b25bf288ae8c72e76c2db35a602070257562a38f4cb8ac9d1e0');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('019', '# Arts (B.A.)
**Course Number:** 019
**Degree:** Bachelor of Arts (B.A. Honours) / Bachelor of Arts (General)
**Duration:** 4 years (Honours) or 3 years (General)
**Entry Stream:** Arts (all-island merit — no district quota)
**Available at:** University of Colombo Faculty of Arts (019A), University of Peradeniya Faculty of Arts (019B), University of Sri Jayewardenepura Faculty of Humanities and Social Sciences (019C), University of Kelaniya Faculty of Humanities (019D), University of Jaffna Faculty of Arts (019E), University of Ruhuna Faculty of Humanities and Social Sciences (019F), South Eastern University Faculty of Arts and Culture (019G), Sabaragamuwa University Faculty of Social Sciences and Languages (019H)

---

## Overview

The Bachelor of Arts is one of the most versatile degrees in Sri Lanka, encompassing the humanities and social sciences — history, economics, political science, sociology, geography, languages, psychology, philosophy, and more. Arts faculties are among the largest in Sri Lankan universities, with thousands of students enrolled across many disciplines.

Arts graduates develop critical thinking, communication, research, and analytical skills that are transferable across many career sectors. The perception that Arts degrees have limited career paths is outdated — Arts graduates work in government service, banking, NGOs, media, teaching, law, international organizations, and the private sector.

**Selection is on all-island merit** — no district quota applies to Arts programmes at the main universities listed under Course 019.

---

## What You Will Study

Arts degrees are highly flexible. Students choose a major (or double major) from their university''s offerings. The range of available subjects varies by university.

**Available subjects at major Arts faculties:**

**Languages and Linguistics:**
Sinhala, Tamil, English, Pali and Buddhist Studies, Arabic and Islamic Civilization, Classical Languages (Sanskrit, Greek, Latin)

**Social Sciences:**
Sociology, Psychology, Political Science, International Relations, Economics and Statistics, Geography, Demography, Anthropology

**History and Culture:**
History, Archaeology, Fine Arts, Philosophy

**Applied Social Sciences:**
Social Work, Criminology and Criminal Justice, Women''s Studies, Peace and Conflict Resolution, Information Technology (within Arts faculty)

**Year 1:** Broad exposure to two or three disciplines. Core academic skills — essay writing, research methods, critical reading.
**Year 2:** Narrowing focus. Major and subsidiary subjects.
**Year 3:** Advanced topics in chosen major. Research methodology.
**Year 4 (Honours):** Dissertation on chosen research topic. Advanced seminars.

---

## Career Paths in Sri Lanka

- **Sri Lanka Administrative Service (SLAS):** The most prestigious government career pathway for Arts graduates. The competitive SLAS examination recruits graduates from all disciplines, but Arts and Economics graduates are historically well-represented.
- **Civil service:** All government ministries, departments, and statutory boards employ Arts graduates in administrative and programme officer roles.
- **Education:** Arts graduates become teachers — History, Sinhala, English, Geography, and other A/L and O/L subjects. Teaching is one of the largest graduate employment sectors.
- **Media and journalism:** Print, broadcast, and digital media. Sinhala, English, and Tamil language graduates are sought by newspapers, TV channels, and online media.
- **Banking and finance:** Many banks recruit graduates from any discipline as management trainees. Communication and analytical skills from Arts degrees are valued.
- **NGOs and international development:** UNICEF, WHO, UNDP, World Bank, and hundreds of local NGOs recruit Arts graduates for programme, research, and communications roles.
- **Law:** Arts graduates who pursue Law (attending Sri Lanka Law College after graduation) become Attorneys-at-Law.
- **Diplomacy and foreign service:** Ministry of Foreign Affairs recruits through competitive examination. Arts graduates — particularly those with international relations, history, or languages — are strong candidates.
- **Research:** Social science research organizations, think tanks, university research departments.
- **Private sector:** Marketing, human resources, corporate communications, customer service management.

---

## Entry Requirements

**A/L Stream:** Arts (selection on all-island merit — no district quota)
**Subjects:** Any three Arts subjects. No specific subject requirements — the student selects a major at university based on available combinations.

**Z-score context:** Arts at top universities (Colombo, Peradeniya) has cutoffs in the **0.5 to 1.2** range. Because selection is all-island merit, the competition is national — students from all 25 districts compete in the same pool. Universities in Ruhuna, Sabaragamuwa, and South Eastern have lower cutoffs.

---

## Special Notes

- The B.A. (General) is a 3-year degree; the B.A. (Honours) is 4 years with a research dissertation. Honours is strongly recommended for students who may pursue postgraduate study.
- English is a key advantage: Arts graduates with strong English communication skills are significantly more employable across all sectors.
- Economics within Arts faculties is one of the most employment-friendly Arts subjects — Economics graduates have strong pathways into banking, government, consulting, and research.
- Colombo Faculty of Arts also offers Education (B.Ed.) for students who want to enter teaching directly.
', '87e41198f3d612e245d8d8d9925ed7711bf34fd84ebd9c3a5b9902046b4e5a3c');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('020', '# Arts
**Course Number:** 020
**Degree:** Bachelor of Arts (Special) in Mass Media
**Duration:** 4 years
**Entry Stream:** Arts Stream
**Available at:** Sripalee Campus, University of Colombo (020S)

---

## Overview

The Bachelor of Arts in Mass Media offered at the Sripalee Campus of the University of Colombo is a specialized degree designed to bridge the gap between theoretical communication studies and the practical demands of the modern media industry. In the Sri Lankan context, where the media landscape is rapidly evolving through digital transformation and social media, this degree provides students with the critical thinking skills and technical proficiency required to navigate complex information environments.

The Sripalee Campus is uniquely positioned to offer this programme, focusing on the intersection of creative arts and professional communication. Unlike traditional general Arts degrees, this programme is highly industry-oriented, preparing graduates for roles in journalism, broadcasting, public relations, and digital content creation. Students benefit from the campus’s specialized environment, which emphasizes hands-on training in media production, fostering a culture of creativity and professional excellence within the Sri Lankan media sector.

---

## What You Will Study

**Year 1: Foundations of Communication**
Introduction to mass communication theories, history of media in Sri Lanka, basic sociology, political science, and language proficiency (Sinhala/English/Tamil). Students are introduced to the fundamental principles of journalism and visual communication.

**Year 2: Media Production and Technology**
Focus shifts to technical skills. Subjects include photography, videography, audio production, and digital media tools. Students begin exploring media law, ethics, and the socio-political impact of media in Sri Lanka.

**Year 3: Specialization and Advanced Theory**
Students choose between tracks such as Print Media, Electronic Media (Radio/TV), or Digital/New Media. Advanced modules cover advertising, public relations, scriptwriting, and media management. Research methodology is introduced to prepare for the final year.

**Year 4: Professional Application and Research**
The final year is dedicated to a mandatory internship in a recognized media organization and the completion of a dissertation or a major creative project. Students refine their portfolios and engage in advanced seminars on contemporary media issues and global communication trends.

---

## Career Paths in Sri Lanka

*   **Journalism and News Reporting:** Working for major Sri Lankan media houses like Lake House, Wijeya Newspapers, or TV channels like Sirasa/Derana. Involves field reporting, investigative writing, and editorial work.
*   **Public Relations and Corporate Communications:** Managing brand reputation and internal communications for corporate entities, NGOs, or government ministries.
*   **Digital Content Strategy:** Creating and managing content for digital platforms, social media marketing, and SEO for advertising agencies or private digital firms.
*   **Broadcasting and Production:** Roles in radio and television production, including directing, editing, and scriptwriting at national or private broadcasting stations.
*   **Media Research and Consultancy:** Working with think tanks or research institutes to analyze media trends, public opinion, and the impact of communication policies.
*   **Postgraduate Study:** Graduates can pursue a Master’s in Mass Media or related fields at the University of Colombo or other UGC-recognized universities to specialize in media policy or communication management.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results in the Arts stream. Candidates must have obtained three passes in one sitting. Selection is highly competitive and is determined by the Z-score system managed by the University Grants Commission (UGC). Proficiency in English is highly recommended as it is a key medium for modern media research and global industry standards. An aptitude test or interview may be required by the Sripalee Campus to assess creative potential and communication skills.

---

## Differences Between Universities

The Mass Media programme at Sripalee Campus is distinct due to its specialized focus on the creative arts and media production. Unlike general Arts degrees offered at other national universities, which often focus on traditional humanities (History, Geography, Sociology), the Sripalee programme is a dedicated professional degree. Its location in the Western Province provides students with proximity to the headquarters of major national media organizations, offering superior networking and internship opportunities compared to more remote regional universities.

---

## Special Notes

The degree is conducted primarily in the Sinhala medium, with significant components of the curriculum requiring English language proficiency for technical software and research. Graduates are well-positioned for both local employment and overseas opportunities in the creative industries. While there is no formal "licensing" body like the IESL for media, a degree from the University of Colombo is highly regarded by employers across the private and public sectors. Students are encouraged to build a strong professional portfolio throughout their four years, as this is often more critical than academic grades when applying for media roles.', '35656ab86b395ae0dc7d243e3c6675a71c704dc157db3ab80bdbfd221c1f4968');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('021', '# Arts (SAB) — Sabaragamuwa University
**Course Number:** 021
**Degree:** Bachelor of Arts (Honours) — Sabaragamuwa University of Sri Lanka
**Duration:** 4 years (Special/Honours) or 3 years (General)
**Entry Stream:** Arts (Humanities), Commerce, and some science streams depending on subject choice
**Available at:** Sabaragamuwa University of Sri Lanka (021L)

---

## Overview

The Bachelor of Arts degree at Sabaragamuwa University of Sri Lanka (SUSL), located in Belihuloya, Ratnapura District, is offered through the Faculty of Social Sciences and Languages. This degree allows students to select from a broad range of humanities and social science disciplines including Sinhala, English, Economics, Geography, History, Political Science, Sociology, and Mass Communication, depending on the subjects a student offers at A/L and their preferences.

SUSL is a relatively young national university established in 1995, situated in the scenic Sabaragamuwa province — a predominantly agricultural region with growing tourism potential. The Arts degree here serves a significant regional population and provides graduates with foundational knowledge for careers in public administration, education, journalism, and community development.

The university has a smaller student body than major universities like Colombo or Peradeniya, which means smaller class sizes and relatively closer faculty-student interaction. The campus is residential for most students, which builds a strong student community.

---

## What You Will Study

Students select a major subject (Special degree) or two subjects (General degree) from the Faculty of Social Sciences and Languages. Common subject areas include:

**Sinhala Language and Literature:**
Classical and modern Sinhala literature, linguistic theory, translation studies, Sinhala journalism.

**English Language and Literature:**
Academic writing, British and world literature, applied linguistics, communication skills, TESOL fundamentals.

**Economics:**
Microeconomics, macroeconomics, development economics, Sri Lankan economic history, statistics for economics, econometrics.

**Geography:**
Physical geography, human geography, GIS and cartography, environmental studies, regional development.

**Political Science:**
Sri Lankan constitutional law, comparative politics, international relations, governance and public policy.

**Sociology:**
Social theory, community development, research methods, gender studies, rural sociology.

**Mass Communication:**
Print and broadcast journalism, media theory, public relations, digital media, media ethics.

All pathways include a **research component and dissertation** in the Honours year (Year 4).

---

## Career Paths in Sri Lanka

- **Public administration:** Ceylon Administrative Service (CAS) and other public sector examinations (Local Government, Cooperative Service, Education Service) are the most common employment pathway for Arts graduates.
- **Education:** Teaching at government schools in the relevant subject areas (Sinhala, English, Economics, Geography, etc.) after obtaining a Postgraduate Diploma in Education (PGDE).
- **Journalism and media:** Print, TV, and online media organizations — Colombo''s major media houses recruit Arts graduates with Communication and Language backgrounds.
- **NGO and development sector:** Community development officers, field researchers, advocacy officers at local and international development NGOs working in health, agriculture, women''s rights, and rural development.
- **Translation and interpretation:** Government departments, courts, and UN agencies require Sinhala-English translators.
- **Postgraduate study:** MA, MPhil, or MSc programmes in relevant disciplines at Kelaniya, Colombo, Peradeniya, or overseas institutions.
- **Entrepreneurship:** Graduates in the Sabaragamuwa region often engage in tourism, handicrafts, or local service businesses leveraging their educational background.

---

## Entry Requirements

**A/L Stream:** Arts/Humanities (primary), Commerce (for Economics, some social sciences)
**Typical subjects:** Varies by specialization. Most humanities subjects require A/L Arts stream (Languages, History, Political Science, Geography, Logic).
**Z-score context:** The BA at SUSL (021L) is generally not among the highest-cutoff programmes — it is accessible to students who performed well in the Arts stream across all districts. Students from the Sabaragamuwa province receive additional advantage from the district quota system.

---

## Special Notes

- SUSL is a **residential university** — most students live on campus in Belihuloya, which creates a close-knit campus community but requires students and families to be prepared for the residential setting away from major cities.
- The **Sabaragamuwa location** (in a rural/forest zone near Balangoda) is a distinctive feature — it attracts students who appreciate the natural environment but may require adjustment for those accustomed to urban life.
- The programme competes with Arts degrees at more established universities (Colombo, Kelaniya, Peradeniya, Ruhuna). Z-score rankings for Arts often reflect students'' preferences for location and university reputation rather than programme quality differences.
- Graduates from the Economics specialization are often competitive in banking sector recruitment examinations (BOC, People''s Bank, HNB).
- English Language graduates have strong prospects in the private sector, ESL teaching, and overseas employment.
', 'd184efd35b6a058b5d2f4909b86290ce659b9f7d56badd6743d117b4f8f9ebae');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('022', '# Management Studies
**Course Number:** 022
**Degree:** Bachelor of Management Studies (Honours)
**Duration:** 4 years
**Entry Stream:** Commerce, Arts, or Physical/Biological Science (subject to UGC criteria)
**Available at:** University of Vavuniya, Sri Lanka (022R), Trincomalee Campus, Eastern University, Sri Lanka (022W)

---

## Overview

The Bachelor of Management Studies (BMS) is a comprehensive undergraduate programme designed to cultivate versatile management professionals capable of navigating the complexities of the modern Sri Lankan business landscape. In an era where the national economy is transitioning toward digital transformation and export-oriented growth, this degree provides the foundational knowledge in organizational behavior, strategic planning, and financial management required to lead both public and private sector enterprises.

The programme is particularly notable for its focus on regional economic development. By being hosted at the University of Vavuniya and the Trincomalee Campus of Eastern University, these faculties play a critical role in bridging the gap between academic theory and the unique industrial challenges of the Northern and Eastern provinces. Students are equipped to address local economic needs while maintaining a global perspective, ensuring they are prepared for the competitive corporate environments of Colombo as well as emerging regional markets.

---

## What You Will Study

**Year 1: Foundation of Business**
Focuses on core principles including Principles of Management, Business Mathematics, Micro and Macro Economics, Business Communication, and Information Technology for Business.

**Year 2: Functional Areas of Management**
Deep dives into specialized business functions: Financial Accounting, Marketing Management, Human Resource Management, Business Law, and Organizational Behavior.

**Year 3: Advanced Management & Specialization**
Students begin to focus on specific tracks such as Financial Management, Supply Chain Management, or Entrepreneurship. Modules include Strategic Management, Research Methodology, and Management Information Systems.

**Year 4: Professional Integration & Research**
The final year emphasizes practical application. Students undertake a mandatory industrial training/internship programme and complete a comprehensive Independent Research Project (Dissertation) that addresses a real-world business problem in the Sri Lankan context.

---

## Career Paths in Sri Lanka

*   **Banking and Finance:** Roles in credit analysis or retail banking at institutions like Bank of Ceylon (BOC), People’s Bank, or Sampath Bank. Involves managing customer portfolios and financial risk assessment.
*   **Human Resource Management:** Positions in HR departments of large conglomerates like John Keells Holdings or MAS Holdings, focusing on recruitment, payroll, and employee relations.
*   **Marketing and Brand Management:** Working with agencies or corporate marketing teams to develop campaigns for local brands; involves market research and consumer behavior analysis.
*   **Public Sector Management:** Administrative roles within government ministries or provincial councils, focusing on policy implementation and public service efficiency.
*   **Entrepreneurship/Small Business Management:** Starting or managing local enterprises, utilizing skills in business planning, taxation, and operational scaling.
*   **Logistics and Supply Chain:** Coordinating distribution networks, particularly relevant for the growing port and industrial zones in Trincomalee and the Northern region.

*Postgraduate options include the MBA (Master of Business Administration) or MSc in Management offered by the University of Colombo, University of Sri Jayewardenepura, or the Postgraduate Institute of Management (PIM).*

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results. Students must satisfy the minimum requirements set by the University Grants Commission (UGC) for the Commerce stream, though students from the Arts and Science streams are often eligible if they meet specific subject combinations. The Z-score requirement is highly competitive and varies annually based on the applicant pool. The medium of instruction is English, and proficiency in the language is essential for academic success.

---

## Differences Between Universities

*   **University of Vavuniya (022R):** Offers a strong focus on regional economic development and entrepreneurship, leveraging its position in the Northern Province to foster links with local SMEs and agricultural business sectors.
*   **Trincomalee Campus, Eastern University (022W):** Benefits from its proximity to the Trincomalee Port and industrial zones. The faculty has a unique focus on logistics, maritime management, and tourism-related business studies, providing students with specific exposure to the blue economy.

---

## Special Notes

Graduates are eligible for exemptions from various professional accounting and management bodies, such as CA Sri Lanka, CIMA, or ACCA, depending on the specific modules completed. While the degree is primarily academic, the mandatory industrial training component is a vital bridge to employment. Students are encouraged to pursue professional certifications alongside their degree to enhance employability in the private sector. The programme is fully recognized by the UGC, ensuring eligibility for all government and private sector employment opportunities within Sri Lanka.', '8d0cd4f041730a2c8968702342b63b350b58941d5f4f93ca7d8683e315fef0a8');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('023', '# Architecture (B.Arch.)
**Course Number:** 023
**Degree:** Bachelor of Architecture (B.Arch. Honours)
**Duration:** 5 years
**Entry Stream:** Physical Science (primarily), Engineering Technology
**Available at:** University of Moratuwa Department of Architecture (023A)

---

## Overview

Architecture at the University of Moratuwa is the only state-university architecture degree in Sri Lanka and one of the most competitive undergraduate programmes in the country. The Department of Architecture, established in 1972, is the flagship built-environment education centre in Sri Lanka, also offering Landscape Architecture, Quantity Surveying, Urban Planning, Design, and Facilities Management.

Architecture combines art, design, engineering, and environmental thinking. Sri Lankan architects design buildings, urban spaces, and environments — from private residences to major infrastructure projects. The profession is regulated by the Sri Lanka Institute of Architects (SLIA), and B.Arch. graduates must complete the professional practice examination to become Chartered Architects.

**Important:** Architecture at Moratuwa requires passing an aptitude test (design and spatial reasoning assessment) in addition to meeting the Z-score threshold. A qualifying Z-score is necessary but not sufficient.

---

## What You Will Study

The B.Arch. is a five-year programme combining design studio work with technical and theoretical studies:

**Year 1 — Foundation:**
Architectural Design Studio (the centrepiece of all years), History of Architecture, Building Technology, Environmental Studies, Drawing and Visual Communication, Mathematics for Architects, Model Making, Introduction to Urban Design.

**Year 2 — Developing Design:**
Advanced Architectural Design Studio, Structural Systems, Building Services (HVAC, plumbing, electrical), Architectural Theory, Sri Lankan Architecture, Landscape Studies, Site Planning.

**Year 3 — Complexity:**
Complex design projects (public buildings, multi-residential), Advanced Structural Design, Professional Practice, Building Economics, Acoustics, Conservation of Heritage Buildings.

**Year 4 — Advanced Studio:**
Urban-scale design projects, Sustainable Architecture and Green Building Design, Research Methods, Dissertation proposal, Technology Integration.

**Year 5 — Thesis and Professional:**
Individual Architectural Thesis — a major independent design project on a self-chosen topic. Professional Practice and office simulation. Preparation for SLIA Professional Practice examination.

---

## Career Paths in Sri Lanka

- **Private practice:** Most architects in Sri Lanka eventually establish their own firms or join established architecture and engineering consultancies. Private practice involves designing homes, commercial buildings, apartments, factories, hospitals, and schools.
- **Government service:** The Government Architect''s Department, Urban Development Authority (UDA), National Building Research Organisation (NBRO), and Ceylon Tourism Development Authority employ architects.
- **Construction industry:** Project architects, site architects, and design managers within construction companies.
- **Real estate development:** Property developers (Softlogic, Access Engineering, Watawala Plantations, major hotel groups) employ architects for project development and design management.
- **Interior design:** Many architects specialize in or transition to interior design for hospitality, retail, and residential sectors.
- **Heritage conservation:** UNESCO-linked projects, Colombo Port City development, and ancient monument conservation (Sigiriya, Polonnaruwa, Anuradhapura) offer heritage architecture roles.
- **Urban planning:** With additional study or specialization, architects enter urban planning and environmental planning roles.
- **Academic architecture:** Lecturers and design critics at Moratuwa and private architecture schools.
- **International practice:** Sri Lankan architects with SLIA membership and overseas experience work in the Middle East (UAE, Qatar, Saudi Arabia), Singapore, and Australia.
- **Sustainable design:** Green building certification (LEED, EDGE) specialists are in growing demand across the region.

---

## Entry Requirements

**A/L Stream:** Physical Science (primary stream), Engineering Technology
**Required A/L subjects:** Combined Mathematics, Physics, and Chemistry (for Physical Science stream)

**Aptitude Test:** Architecture at Moratuwa requires a mandatory aptitude test assessing spatial awareness, design thinking, and creative visualization. A qualifying Z-score at the cutoff only makes you eligible to sit the aptitude test — you must pass both. Students should prepare for this test separately.

**Z-score context:** Architecture (023A) has cutoffs typically in the **1.4 to 1.9** range for Physical Science applicants in competitive years. The limited intake (around 40–60 students per year) and the aptitude test requirement make this among the most selective programmes at Moratuwa.

---

## Special Notes

- Architecture is offered **only at the University of Moratuwa** within the state university system.
- The 5-year duration (compared to 4 years for most degrees) reflects the depth and breadth of training required.
- Moratuwa''s Department of Architecture also offers Landscape Architecture (097), Quantity Surveying (011), Design (024), and Town and Country Planning (030) — related programmes for students with similar interests but who may not qualify for Architecture itself.
- The design studio is the heart of architectural education — students spend many hours per week creating design proposals, which are then presented and critiqued by lecturers and invited practitioners.
- Strong drawing and spatial reasoning skills are essential. Students who do not enjoy design, visual arts, or creative problem-solving may find this programme challenging.
- The SLIA membership process requires professional practice experience after graduation before full chartered status is granted.
', '16dcc2bf08970909a229ba8aaf8a91354e65ae2454b8e10dab4709a442edc210');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('024', '# Design (B.Des.)
**Course Number:** 024
**Degree:** Bachelor of Design (Honours) / Bachelor of Integrated Design
**Duration:** 4 years
**Entry Stream:** Physical Science, Engineering Technology
**Available at:** University of Moratuwa Department of Integrated Design (024A)

---

## Overview

Design at the University of Moratuwa is one of Sri Lanka''s most creative and multidisciplinary undergraduate degrees. The Department of Integrated Design approaches design as a problem-solving discipline at the intersection of aesthetics, engineering, and human behaviour — covering industrial design, product design, communication design (graphic design), interior design, and interaction design.

**Important:** Design at Moratuwa requires an aptitude test assessing visual creativity, spatial reasoning, and design thinking — in addition to meeting the Z-score threshold.

---

## What You Will Study

**Year 1 — Design Foundations:**
Design Drawing and Sketching, Colour Theory, Design Thinking, Fundamentals of Communication Design, Introduction to 3D Form and Space, Digital Design Tools (Adobe Creative Suite, CAD), Materials and Manufacturing.

**Year 2 — Core Design Practice:**
Product Design Studio, Communication Design (typography, graphic design, branding), Interior Space Design, Design Research Methods, Ergonomics and Human Factors, Digital Fabrication (3D printing, laser cutting, CNC).

**Year 3 — Specialization:**
Students develop a design specialization through studio projects in their chosen area (Product/Industrial Design, Communication/Graphic Design, Interior/Environmental Design, Interaction/UX Design). Industry-linked projects, client briefs.

**Year 4 — Thesis Design Project:**
Major individual design thesis — a complex design challenge from research through to a final prototype or system. Professional portfolio development. Industry exhibition (often held at Design Faculty open days).

---

## Career Paths in Sri Lanka

- **Product/industrial design:** Designing manufactured products for local and export industries. Sri Lanka''s apparel, rubber, gem, ceramic, and furniture industries all require design input.
- **Graphic design and branding:** Creative agencies, advertising companies, marketing departments. Growing demand for digital design skills.
- **Interior design:** Commercial (offices, hotels, retail), residential, and hospitality interior design — a booming sector with Port City Colombo and hotel construction activity.
- **UX/UI design:** User experience and interface design for mobile apps, websites, and software products — one of the most in-demand digital creative roles.
- **Apparel and fashion design:** Sri Lanka''s dominant export industry (USD 5 billion annually) requires design talent at all levels.
- **Design consultancy:** Running an independent design studio or joining a consultancy.
- **Brand management:** Senior designers move into brand strategy and management roles at corporates.
- **International design:** Singapore, Australia, UK, and UAE have active design industries recruiting Sri Lankan graduates.
- **Academia:** Design lecturers at Moratuwa and private design schools.

---

## Entry Requirements

**A/L Stream:** Physical Science (primary), Engineering Technology
**Required subjects:** Combined Mathematics + Physics + Chemistry

**Aptitude Test:** Compulsory — assesses drawing ability, spatial reasoning, colour sense, and creative problem-solving. Prepare by drawing regularly, studying design basics, and practising freehand sketching.

**Z-score context:** Design cutoffs are typically in the **1.2 to 1.7** range — competitive but somewhat lower than Architecture. The aptitude test creates an additional filter.

---

## Special Notes

- Students should build a portfolio of creative work before applying — sketches, drawings, photographs, any design projects.
- Design is taught in English at Moratuwa.
- The growing digital economy has dramatically increased demand for UX/UI designers — a career path that Design graduates are well-positioned for.
', '8e822ef47a3e350bdd0dde72dfaf4d7dd0beaee870d64e1c2731775ba64473c8');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('025', '# Law (LL.B.)
**Course Number:** 025
**Degree:** Bachelor of Laws (LL.B.)
**Duration:** 4 years
**Entry Stream:** Arts (all-island merit basis — no district quota)
**Available at:** University of Colombo Faculty of Law (025A), University of Peradeniya Department of Law (025B)

---

## Overview

The LL.B. degree from the University of Colombo Faculty of Law is the most prestigious law qualification in Sri Lanka. The Faculty of Law at Colombo is the only standalone Faculty of Law in the traditional Sri Lankan university system, making it unique among Sri Lankan law institutions. Established in 1942, it has produced the majority of Sri Lanka''s senior judges, attorneys-general, senior counsel, and leading legal academics.

Law at Peradeniya is offered through the Faculty of Arts and provides a second state-university pathway for aspiring lawyers.

Sri Lankan Law graduates must subsequently complete the Attorney-at-Law examination through the Sri Lanka Law College to be admitted to the bar. The LL.B. degree is not itself a licence to practise — it is an academic qualification that provides the foundation for law college exams and legal careers.

---

## What You Will Study

The LL.B. curriculum at Colombo is structured around three departments covering the major branches of law:

**Year 1 — Foundations:**
Introduction to Law and the Legal System, Constitutional Law and Fundamental Rights, Law of Contract I, Legal Research and Writing, Criminal Law, History of Roman-Dutch and English Law (the two pillars of Sri Lanka''s mixed legal system).

**Year 2 — Core Law:**
Law of Contract II, Law of Torts, Property Law, Administrative Law, Evidence, Jurisprudence and Legal Theory, Land Law.

**Year 3 — Specialization:**
Commercial Law (Companies, Securities, Banking), International Law (Public International Law, International Trade Law), Family Law, Labour Law, Environmental Law, Intellectual Property Law.

**Year 4 — Advanced and Applied:**
Research project / dissertation, International Economic and Commercial Law, Arbitration and Alternative Dispute Resolution, Human Rights Law, Comparative Constitutional Law, Clinical Legal Education (moot courts, client counselling, legal aid).

**Three Academic Departments at Colombo:**
- Commercial Law (contracts, companies, banking, trade)
- Private and Comparative Law (torts, family, property)
- Public and International Law (constitutional, administrative, international)

---

## Career Paths in Sri Lanka

- **Attorney-at-Law (court practice):** After completing the LL.B. and passing the Sri Lanka Law College examination, graduates are enrolled as Attorneys-at-Law. They can practise in all courts of Sri Lanka including the Supreme Court, Court of Appeal, High Courts, and Magistrates'' Courts.
- **Corporate legal practice:** Large law firms (Julius & Creasy, F.J. & G. de Saram, Nithyanandam & Sivagnanasundaram, D.L. & F. de Saram) recruit LL.B. graduates for commercial, corporate, and international law practice.
- **In-house counsel:** Banks, insurance companies, listed companies, and multinationals maintain legal departments recruiting LL.B. graduates.
- **Government legal service:** The Attorney General''s Department, State Counsel positions, Solicitor General''s office, and legal officer roles in government ministries and state corporations.
- **Judiciary:** After gaining experience as an Attorney, lawyers can apply for Judicial Service Commission appointments as Magistrates and District Judges, with pathways to the High Court and Supreme Court.
- **International law and diplomacy:** International organizations (UN agencies, WTO, ICRC), foreign missions, and the Ministry of Foreign Affairs recruit legally trained graduates.
- **Academia:** Law lecturers and researchers at state and private universities.
- **Postgraduate study:** LL.M. programmes at Colombo, and internationally at universities in the UK, USA, Australia, the Netherlands. Colombo offers an LL.M. in International Economic and Commercial Law (IECCL) by coursework.

---

## Entry Requirements

**A/L Stream:** Arts (selection is on all-island merit basis — no district quota applies)
**Subjects:** Any three Arts subjects at A/L. There are no specific subject requirements. Students with Economics, History, Political Science, Languages, Logic, or any combination are eligible.
**O/L requirement:** Credit passes in at least 6 subjects including Sinhala/Tamil, English, and Mathematics.

**Z-score context:** Law is among the most competitive Arts programmes in Sri Lanka. Because selection is all-island merit (no district quota), the competition is national. Typical cutoff Z-scores are in the range of **1.5 to 2.0+** in recent years, making it harder to enter than many Physical Science programmes. The limited intake (around 100–150 students per year at Colombo) makes this a narrow gate.

---

## Differences Between Universities

- **Colombo (025A):** The only standalone Faculty of Law, 4-year LL.B., dedicated law library and moot court facilities, strongest reputation and alumni network in Sri Lanka''s legal profession.
- **Peradeniya (025B):** Offered through the Faculty of Arts, Arts-integrated legal education, Kandy-based, slightly lower Z-score cutoff but still highly competitive.

---

## Special Notes

- Sri Lanka follows a mixed legal system based on Roman-Dutch law and English common law, with customary laws (Tesawalamai, Kandyan Law, Muslim Personal Law) applying to specific communities. This unique legal heritage is a central part of the curriculum.
- The LL.B. alone does not permit legal practice — graduates must additionally pass the Attorney-at-Law exam at the Sri Lanka Law College (typically 2 years of further study and examinations).
- Some graduates choose to pursue practice in the UK (GDL conversion) or Australia (postgraduate LL.M. and bar admission) without sitting the Sri Lanka Law College exam.
- The Faculty of Law at Colombo publishes the Colombo Law Review and the Sri Lanka Journal of International Law — both peer-reviewed academic publications.
', 'a4ad4d5f0d8618695359d90e9083f1d272bec143e255c054b2ce0b294c5ec112');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('026', '# Information Technology (IT)
**Course Number:** 026
**Degree:** Bachelor of Information Technology (B.IT. Honours) / Bachelor of Science in Information Technology
**Duration:** 4 years
**Entry Stream:** Physical Science, Engineering Technology, Biological Science (some intakes)
**Available at:** University of Moratuwa Faculty of Information Technology (026A)

---

## Overview

The Faculty of Information Technology at the University of Moratuwa offers one of the most highly regarded IT degrees in Sri Lanka. Established as a standalone faculty dedicated to IT, it benefits from Moratuwa''s strong industry reputation and proximity to Sri Lanka''s major IT corridor. Graduates are in high demand in Sri Lanka''s booming IT and BPO industry, which contributes over USD 1 billion annually to exports.

Information Technology differs from Computer Science in that it places greater emphasis on practical systems, business applications, IT management, and technology deployment alongside the core computing fundamentals. It is designed to produce graduates who bridge the gap between technology and business.

---

## What You Will Study

**Year 1 — Computing and IT Foundations:**
Programming Fundamentals (Python, Java), Web Technologies, Digital Logic and Computer Architecture, Mathematics for IT, Database Fundamentals, Networking Basics, Professional Communication.

**Year 2 — Core IT:**
Object-Oriented Programming, Data Structures and Algorithms, Operating Systems, Database Management Systems, Computer Networks and Security, Systems Analysis and Design, Human-Computer Interaction, IT Project Management.

**Year 3 — Advanced Applications:**
Software Engineering, Information Security, Cloud Computing, Mobile Application Development, Enterprise Systems (ERP), Data Analytics and Visualization, Business Intelligence, Industrial Training placement (compulsory).

**Year 4 — Specialization and Capstone:**
Research Project, Electives in chosen specialization (Data Science, Cybersecurity, IoT, AI applications, IT Governance), Advanced Networking, IT Entrepreneurship.

**Also offered by this Faculty:**
- Information Technology and Management (Course 091) — combines IT with management principles

---

## Career Paths in Sri Lanka

- **Software development:** Web developers, mobile app developers, backend engineers at Sri Lankan software companies and global tech firms with Sri Lanka offices.
- **IT infrastructure and networks:** Systems administrators, network engineers, cloud architects managing enterprise IT environments for banks, telecoms, and corporations.
- **Cybersecurity:** Security analysts, penetration testers, security architects — a fast-growing field as Sri Lankan organizations increase digital investment.
- **Business intelligence and data analytics:** Data analysts and BI developers using Power BI, Tableau, SQL analytics at banks, insurance companies, and corporates.
- **Enterprise systems:** ERP consultants and system administrators for SAP, Oracle, Microsoft Dynamics deployments.
- **IT project management:** Project Managers and Scrum Masters in software development companies.
- **IT consultancy:** Technology advisory roles in consulting firms.
- **Government IT:** Sri Lanka Government Information Centre, ICTA (ICT Agency of Sri Lanka), and all major government ministries managing digital transformation projects.
- **Freelancing:** A significant number of IT graduates freelance on international platforms (Upwork, Fiverr) in web development, digital marketing, and software development.
- **Startups:** Sri Lanka''s growing startup ecosystem (PickMe, Lanka QR, Dialog Axiata ventures) recruits IT graduates for product and technology roles.

---

## Entry Requirements

**A/L Stream:** Physical Science (primary), Engineering Technology
**Typical subjects:** Combined Mathematics + Physics + Chemistry (Physical Science), or Engineering Technology stream subjects

**Z-score context:** IT at Moratuwa (026A) is competitive — cutoffs typically in the **1.1 to 1.6** range. Slightly lower than Engineering at Moratuwa but higher than many other universities. Students who just miss Engineering but have strong Z-scores find IT at Moratuwa an excellent alternative.

---

## Special Notes

- Medium of instruction is English.
- Industrial training is compulsory — students gain 6 months to 1 year of real industry experience during their degree, which significantly improves employability.
- Moratuwa IT graduates command among the highest starting salaries of any state university degree, reflecting industry demand.
- The Faculty of IT at Moratuwa also offers Management and Information Technology (Course 091), which combines IT with business management for students who want a hybrid qualification.
- The ICTA (ICT Agency of Sri Lanka) and government digital transformation initiatives create significant public-sector IT employment opportunities for graduates.
', '7302644e93eb7c2403d1cd008b0cb00f93b559f06430aa5347ee13c927915d17');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('027', '# Management and Information Technology
**Course Number:** 027
**Degree:** Bachelor of Science (Honours) in Management and Information Technology
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** University of Kelaniya (027D)

---

## Overview

The Bachelor of Science (Honours) in Management and Information Technology (MIT) is a multidisciplinary degree designed to bridge the gap between technical IT expertise and strategic business management. In the context of Sri Lanka’s rapidly digitizing economy, there is a high demand for professionals who can not only develop software solutions but also understand the business processes, organizational behavior, and financial implications of technological implementations.

The programme is particularly notable for its unique positioning within the Faculty of Science at the University of Kelaniya. By combining core management principles with advanced computing, the degree prepares graduates to act as "translators" between technical teams and corporate leadership. This skill set is highly valued in Sri Lanka’s thriving ICT sector, banking, and logistics industries, where digital transformation is a top priority for local and multinational corporations.

---

## What You Will Study

**Year 1: Foundations**
Focuses on the fundamentals of computing, mathematics for management, and introductory business studies. Subjects include Programming, Database Management Systems, Principles of Management, Financial Accounting, and Mathematics for Management.

**Year 2: Core Integration**
Deepens the technical and managerial knowledge base. Subjects include Data Structures and Algorithms, Object-Oriented Programming, Marketing Management, Human Resource Management, and Business Statistics. Students begin to apply IT tools to solve management problems.

**Year 3: Advanced Application**
Focuses on specialized areas and professional development. Subjects include Software Engineering, Enterprise Resource Planning (ERP), Operations Research, Management Information Systems, and Business Law. Students often engage in industrial training or internships during this period.

**Year 4: Specialization and Research**
The final year emphasizes strategic application and independent research. Students undertake a comprehensive Research Project or Dissertation. Elective modules may include E-Commerce, Strategic Management, Project Management, and Advanced Data Analytics.

---

## Career Paths in Sri Lanka

- **Business Analyst:** Working with firms like WSO2 or Virtusa to bridge the gap between client business requirements and technical development teams.
- **Systems Analyst:** Analyzing and improving organizational IT infrastructure within large local conglomerates like John Keells Holdings or Hayleys.
- **Project Manager (IT):** Overseeing software development lifecycles and managing resources in Sri Lankan software houses and multinational IT firms.
- **ERP Consultant:** Implementing and managing enterprise software (e.g., SAP, Oracle) for manufacturing or retail sectors in Sri Lanka.
- **Data Analyst:** Interpreting complex business data to drive decision-making in the banking and finance sector (e.g., Commercial Bank, Sampath Bank).
- **Postgraduate Study:** Graduates are well-positioned for an MBA in IT, MSc in Industrial Management, or specialized Master’s degrees in Data Science or Business Analytics at institutions like the University of Moratuwa or the University of Kelaniya.

---

## Entry Requirements

Admission is strictly based on the G.C.E. Advanced Level examination in the Physical Science stream. Candidates must have passed all three subjects in one sitting. Due to the interdisciplinary nature of the course, an aptitude test is typically conducted by the University of Kelaniya to assess logical reasoning and analytical skills. The Z-score requirement is highly competitive, reflecting the high demand for this unique blend of management and technology. The medium of instruction is English.

---

## Differences Between Universities

While the University of Kelaniya is the primary provider of the "Management and Information Technology" (MIT) degree under the 027 course code, other universities offer similar interdisciplinary programmes under different titles. The Kelaniya MIT programme is distinct because it is housed within the Faculty of Science, ensuring a rigorous technical foundation, while maintaining strong links to the Department of Industrial Management. This provides students with a more scientific approach to management compared to degrees offered solely within Management faculties, which may focus more on the social science aspects of business.

---

## Special Notes

- **Professional Recognition:** Graduates are often eligible for exemptions or fast-track pathways toward professional qualifications such as CIMA or CIM, depending on the modules completed.
- **Aptitude Test:** Prospective students must monitor the UGC and University of Kelaniya websites closely, as the aptitude test is a mandatory requirement for selection.
- **Industry Exposure:** The programme heavily emphasizes practical application; students are encouraged to seek internships early to build a portfolio, as the Sri Lankan IT industry places significant weight on practical experience alongside academic credentials.
- **Global Mobility:** The curriculum is aligned with international standards, making graduates competitive for overseas employment in roles such as IT consultancy and business operations management.', '375f4189f0f730b4eab456a9d53ffcebd6bee1d75bd2fb9daacefc7eff6319c3');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('028', '# Management and Public Policy (B.Sc.)
**Course Number:** 028
**Degree:** Bachelor of Science (Honours) in Management (Public Policy)
**Duration:** 4 years
**Entry Stream:** Arts, Commerce
**Available at:** University of Sri Jayewardenepura Faculty of Management Studies and Commerce, Department of Public Administration (028A)

---

## Overview

Management and Public Policy at USJ is a degree focused on the governance, management, and policy dimensions of the public sector — government ministries, statutory boards, public corporations, and policy institutions. It combines public administration theory, policy analysis, economics, and management skills to prepare graduates for government service and public sector leadership.

Sri Lanka''s large public sector — employing hundreds of thousands of people across government ministries, provincial councils, and state-owned enterprises — provides the primary employment market for this degree.

---

## What You Will Study

**Year 1 — Foundations:**
Principles of Public Administration, Political Science and Governance, Economics (Micro and Macro), Business Communication, Organizational Theory, Introduction to Law (administrative law, constitutional law).

**Year 2 — Core Public Management:**
Public Financial Management (government budgeting, treasury operations), Human Resource Management in the Public Sector, Public Policy Process (how policy is made, implemented, and evaluated), Administrative Law, Local Government and Decentralization, Research Methods.

**Year 3 — Policy Analysis:**
Policy Analysis Techniques, Public Sector Performance Management, Development Economics, Government Procurement (public tender procedures, ICTAD regulations), Project Planning and Management (Logframe, PERT/CPM), International Development Administration. Internship with a government ministry or statutory body.

**Year 4 — Specialization:**
Research Dissertation, E-Governance and Digital Government, Comparative Public Administration, Strategic Planning in Government, Public Sector Reform.

---

## Career Paths in Sri Lanka

- **Sri Lanka Administrative Service (SLAS):** The most prestigious government career track. SLAS officers hold senior positions in all government ministries and serve as District Secretaries, Divisional Secretaries, and Ministry Secretary Generals. The competitive SLAS examination is open to all graduates.
- **Government ministry programme officers:** All line ministries (Health, Education, Agriculture, Finance, Foreign Affairs) employ programme officers and administrative officers recruited through public service commission.
- **Provincial councils:** Each of Sri Lanka''s 9 provincial councils operates a provincial public service.
- **Statutory bodies and public corporations:** Sri Lanka Tourism Development Authority, Urban Development Authority, Board of Investment, National Water Supply & Drainage Board, Ceylon Electricity Board — all employ management graduates.
- **Local government:** Municipal councils, urban councils, and Pradeshiya Sabhas employ administrative and management graduates.
- **NGOs and development organizations:** Public policy graduates are valued in NGOs that interface with government programmes.
- **International organizations:** UNDP, World Bank, ADB, and other international development organizations working on governance and public sector reform in Sri Lanka.
- **Postgraduate study:** Master of Public Administration (MPA) or Master of Public Policy (MPP) locally or overseas.

---

## Entry Requirements

**A/L Stream:** Arts (primary), Commerce
**No specific mandatory A/L subjects** — any three subjects from the relevant stream

**Z-score context:** Public Policy cutoffs are typically in the **0.6 to 1.0** range — accessible to Arts and Commerce students, with USJ being more competitive than regional universities.

---

## Special Notes

- The SLAS examination is highly competitive and open to all graduates — a Public Policy degree is the best direct preparation for it.
- Public administration in Sri Lanka has undergone significant reform — knowledge of e-governance, public financial management, and performance accountability is increasingly valued.
- Students who aspire to careers in diplomacy (Ministry of Foreign Affairs) benefit from the international governance component of this degree.
', 'aa18afc3f0090fbe6e510da3d6b20f358c7e1a884f0c3a663fbf091498b75ddc');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('029', '# Communication Studies
**Course Number:** 029
**Degree:** Bachelor of Arts (Honours) in Communication Studies
**Duration:** 4 years
**Entry Stream:** Arts Stream
**Available at:** Trincomalee Campus, Eastern University, Sri Lanka (029W)

---

## Overview

Communication Studies is an interdisciplinary field that examines how human beings exchange information, influence one another, and shape culture through media and interpersonal interaction. In the Sri Lankan context, this degree is vital as the nation navigates a rapidly evolving digital landscape, requiring professionals who can bridge the gap between traditional media, emerging digital technologies, and public discourse.

The programme at the Trincomalee Campus of the Eastern University is designed to provide students with a deep understanding of media theory, communication ethics, and practical production skills. By focusing on the socio-political and cultural nuances of Sri Lanka, the faculty prepares graduates to contribute to the country’s media industry, corporate communications sector, and development communication initiatives, ensuring they are equipped to handle the complexities of a modern, interconnected society.

---

## What You Will Study

**Year 1: Foundations of Communication**
Introduction to Communication Theory, History of Mass Media, Language and Communication, Sociology of Communication, and basic Information Technology skills.

**Year 2: Media and Society**
Print Journalism, Radio and Television Broadcasting, Communication Ethics and Law, Political Communication, and Research Methodology.

**Year 3: Specialization and Application**
Students focus on specific tracks such as Digital Media Production, Public Relations, Advertising, or Development Communication. Core modules include Advanced Media Writing, Multimedia Storytelling, and Organizational Communication.

**Year 4: Advanced Research and Internship**
Final year focuses on the Independent Research Dissertation, a professional Internship programme in a media or corporate organization, and advanced seminars on Global Communication Trends and Crisis Communication.

---

## Career Paths in Sri Lanka

*   **Journalism & Media:** Working with national media houses like Lake House, Wijeya Newspapers, or TV channels (e.g., Sirasa, Derana). Involves reporting, editing, and content creation.
*   **Public Relations (PR) & Corporate Communications:** Managing brand image for companies or government institutions. Involves drafting press releases, managing media relations, and internal communications.
*   **Digital Content Strategy:** Working for digital agencies or marketing firms. Involves social media management, SEO-driven content creation, and digital brand building.
*   **Development Communication:** Working with NGOs (e.g., UNDP Sri Lanka, local NGOs) to design communication campaigns for social change, health awareness, and community development.
*   **Broadcasting & Production:** Roles in radio and television production, including scriptwriting, directing, and technical production.
*   **Postgraduate Study:** Graduates can pursue M.A. or M.Phil. degrees in Mass Communication, International Relations, or Sociology at universities like the University of Kelaniya or the University of Colombo.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results in the Arts stream. Candidates must have obtained passes in three subjects at one sitting. Proficiency in English is highly encouraged as it is a key medium for modern media research. The Z-score requirement is determined annually by the University Grants Commission (UGC) and is generally competitive, reflecting the demand for media-related professional qualifications.

---

## Differences Between Universities

The Bachelor of Arts (Honours) in Communication Studies is exclusively offered at the Trincomalee Campus of the Eastern University. This location offers a unique advantage by providing a regional perspective on communication, allowing students to study the intersection of media and multiculturalism in the Eastern Province. The campus environment encourages a focused, community-oriented approach to learning that differs from the larger, urban-centric media programmes in the Western Province.

---

## Special Notes

The programme is conducted primarily in the medium of English, though some modules may incorporate local language proficiency. Graduates are well-positioned for roles in the growing digital economy. While there is no mandatory professional licensing body like the SLMC for this degree, students are encouraged to seek student memberships in professional bodies such as the Sri Lanka Institute of Marketing (SLIM) or relevant media associations to enhance their networking and employability. Overseas employment demand for communication professionals is high, particularly in roles related to digital marketing and corporate social responsibility (CSR).', 'cbc2a9e92130e25d92500c86f269738360947349f0af48ceae7f4096a78758ff');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('030', '# Urban Informatics and Planning
**Course Number:** 030
**Degree:** Bachelor of Science Honours in Urban Informatics and Planning
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** University of Moratuwa (030G)

---

## Overview

The Bachelor of Science Honours in Urban Informatics and Planning is a specialized, multidisciplinary degree designed to address the complex challenges of rapid urbanization in Sri Lanka. As the country moves toward smarter, more sustainable city development, there is an increasing demand for professionals who can bridge the gap between spatial planning and data-driven technology. This program equips students with the analytical tools to manage urban growth, infrastructure development, and environmental sustainability.

The Department of Town and Country Planning at the University of Moratuwa is the premier institution for this discipline in Sri Lanka. The faculty is notable for its strong industry links with the Urban Development Authority (UDA) and the National Physical Planning Department. By integrating informatics—the science of processing data for storage and retrieval—with traditional urban planning, the program ensures graduates are prepared for the digital transformation of Sri Lankan cities, from Colombo’s Port City project to regional urban renewal initiatives.

---

## What You Will Study

**Year 1: Foundations of Planning and Informatics**
Focuses on the basics of urban systems, introduction to GIS (Geographic Information Systems), spatial data analysis, environmental studies, and the socio-economic context of Sri Lankan settlements.

**Year 2: Spatial Analysis and Planning Techniques**
Students delve into advanced cartography, remote sensing, urban design principles, land-use planning, and quantitative research methods. This year emphasizes the technical skills required for spatial modeling.

**Year 3: Integrated Urban Systems and Infrastructure**
Covers transportation planning, housing policy, disaster risk management, and smart city infrastructure. Students engage in intensive field studies and studio-based projects that simulate real-world planning scenarios.

**Year 4: Advanced Practice and Research**
The final year is dedicated to the Comprehensive Planning Project and an individual research dissertation. Students choose elective modules focusing on specialized areas such as sustainable development, big data analytics in urban environments, or regional policy formulation.

---

## Career Paths in Sri Lanka

*   **Urban Planner:** Working with the Urban Development Authority (UDA) or local municipal councils to design zoning laws and city development master plans.
*   **GIS Specialist:** Employed by private consultancy firms or the Survey Department to map spatial data, analyze land use, and provide visual intelligence for infrastructure projects.
*   **Smart City Consultant:** Working with tech firms or international development agencies (like UN-Habitat) to implement digital solutions for traffic management, waste disposal, and utility optimization.
*   **Environmental Planning Officer:** Collaborating with the Central Environmental Authority (CEA) to conduct Environmental Impact Assessments (EIA) for large-scale construction and development projects.
*   **Real Estate and Development Analyst:** Providing data-driven insights for private sector developers regarding site selection, market feasibility, and urban growth trends.
*   **Postgraduate Study:** Graduates often pursue M.Sc. or Ph.D. programs in Urban Design, Transport Planning, or Data Science at the University of Moratuwa or leading international universities in Australia, the UK, or Singapore.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Physical Science stream. Candidates must have achieved the required Z-score for the academic year, which is highly competitive given the limited intake. Proficiency in English is mandatory as the medium of instruction and assessment is entirely in English. An aptitude test or interview may be conducted by the University of Moratuwa to assess spatial reasoning and analytical capabilities.

---

## Differences Between Universities

This programme is currently offered exclusively at the University of Moratuwa. As the sole provider of this specialized degree in the state university system, the Department of Town and Country Planning maintains a unique position, benefiting from a concentrated pool of expert faculty, specialized planning laboratories, and direct access to national-level policy-making bodies in Colombo.

---

## Special Notes

Graduates of this programme are eligible for professional membership in the Institute of Town Planners, Sri Lanka (ITPSL), which is the primary regulatory body for the profession. The degree is highly regarded internationally, providing a strong foundation for those seeking to migrate or pursue postgraduate studies abroad. Students should be prepared for a rigorous schedule involving significant fieldwork, studio hours, and technical software training. Proficiency in software such as ArcGIS, AutoCAD, and statistical analysis tools is developed throughout the course and is essential for professional success.', '4fa9c0e15a1e9a163ee24e97b5ea176025c42cc99ea9a91239ff867e76224ef0');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('031', '---

# Peace and Conflict Resolution
**Course Number:** 031
**Degree:** Bachelor of Arts (Honours) in Peace and Conflict Resolution
**Duration:** 4 years
**Entry Stream:** Arts Stream
**Available at:** University of Kelaniya (031D)

---

## Overview

The Bachelor of Arts in Peace and Conflict Resolution at the University of Kelaniya is a pioneering interdisciplinary programme, marking the first of its kind in South Asia. It is designed to equip students with the theoretical frameworks and practical skills necessary to understand, analyze, and mitigate conflicts at local, national, and international levels. Given Sri Lanka’s historical context of ethnic, social, and political tensions, this degree is vital for fostering reconciliation, sustainable development, and social cohesion.

The programme is housed within the Faculty of Social Sciences, which provides a rich academic environment drawing on sociology, political science, law, and philosophy. Graduates are prepared for roles in humanitarian agencies, government policy, and civil society, where the ability to navigate complex social dynamics is highly valued. The University of Kelaniya’s long-standing commitment to peace research makes it a premier destination for students aiming to contribute to the nation’s post-conflict development and peacebuilding efforts.

---

## What You Will Study

**Year 1: Foundations of Social Science and Peace**
Introduction to the concepts of peace, violence, and conflict. Core modules include Sociology of Conflict, Political Science fundamentals, Human Rights, and basic research methodology. Students also focus on developing academic writing and critical thinking skills.

**Year 2: Conflict Analysis and Theoretical Frameworks**
Deep dive into the causes of conflict, including ethnic, religious, and resource-based tensions. Subjects include International Relations, Conflict Transformation theories, Psychology of Conflict, and the role of media in peacebuilding.

**Year 3: Applied Peacebuilding and Specialized Tracks**
Students engage with practical applications such as Negotiation and Mediation, Humanitarian Law, Gender and Conflict, and Transitional Justice. This year often involves field visits or workshops related to reconciliation efforts in Sri Lanka.

**Year 4: Advanced Research and Professional Practice**
The final year focuses on a mandatory independent research dissertation. Students also undertake advanced seminars on Peace Policy, Development, and Global Security. The curriculum emphasizes the transition from academic theory to professional practice in the NGO or public sector.

---

## Career Paths in Sri Lanka

*   **Humanitarian Aid Worker:** Working with international and local NGOs (e.g., UNDP, Save the Children, or local community-based organizations) to manage relief efforts and community development in vulnerable regions.
*   **Policy Analyst/Researcher:** Providing research support to government ministries, think tanks (e.g., Centre for Policy Alternatives), or international policy institutes to inform peace-related legislation and social policy.
*   **Conflict Mediator/Negotiator:** Facilitating dialogue between conflicting parties, working within legal aid centers, or as part of community-based dispute resolution mechanisms.
*   **Human Rights Advocate:** Working with organizations like the Human Rights Commission of Sri Lanka to monitor rights violations, conduct advocacy campaigns, and provide legal awareness.
*   **Journalist/Media Specialist:** Specializing in conflict-sensitive reporting and investigative journalism for national media outlets, focusing on social harmony and reconciliation.
*   **Postgraduate Study:** Graduates can pursue M.A. or M.Phil. degrees in International Relations, Human Rights, or Development Studies at universities like the University of Colombo or the University of Peradeniya, or pursue international scholarships for global peace studies.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results in the Arts stream. Candidates must have obtained three passes in one sitting. Proficiency in the English language is essential, as the programme is conducted in English. The Z-score requirement is competitive and varies annually based on the number of applicants and the university’s intake capacity. Students should check the latest UGC handbook for the specific Z-score cut-off for the University of Kelaniya.

---

## Differences Between Universities

This programme is currently offered exclusively at the University of Kelaniya. As the first department to introduce this degree in South Asia, the University of Kelaniya holds a unique position in the academic landscape, offering a specialized curriculum that is deeply integrated with the Faculty of Social Sciences. Its location in the Western Province provides students with proximity to major government institutions, international NGOs, and diplomatic missions, offering superior networking and internship opportunities compared to regional institutions.

---

## Special Notes

The degree is primarily taught in English, which is a significant advantage for students seeking employment in international organizations or pursuing postgraduate studies abroad. While there is no specific professional licensing body for "Peace Practitioners" in Sri Lanka, the degree is highly regarded by the UN system, international NGOs, and government agencies involved in reconciliation. Students are encouraged to participate in extracurricular activities, such as university debating societies or peace clubs, to build the soft skills required for this field. Graduates are well-positioned for careers in the public sector, the NGO sector, and international development agencies.', 'e4bbf7337a64314121bca384071e0c98d84b36ecfde592e1e867499e77279dbe');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('032', '# Ayurveda Medicine and Surgery (BAMS)
**Course Number:** 032
**Degree:** Bachelor of Ayurveda Medicine and Surgery (BAMS)
**Duration:** 5 years (plus one year internship)
**Entry Stream:** Biological Science
**Available at:** University of Colombo Faculty of Indigenous Medicine (032A), Gampaha Wickramarachchi University of Indigenous Medicine (032B)

---

## Overview

Ayurveda is one of the world''s oldest systems of medicine, originating in ancient India and deeply integrated into Sri Lankan culture and healthcare. The BAMS degree trains practitioners in traditional Ayurvedic medicine alongside modern biomedical sciences, preparing graduates to practise as Ayurvedic physicians (Ayurvedic Medical Officers) in both the government Ayurvedic health service and private practice.

Sri Lanka has a parallel healthcare system — the Department of Ayurveda under the Ministry of Indigenous Medicine — that runs Ayurvedic hospitals, dispensaries, and community health programmes alongside the western medical system. This creates a well-defined government career pathway for BAMS graduates.

The Gampaha Wickramarachchi University of Indigenous Medicine (GWUIM) in Yakkala is the first and only dedicated university for indigenous medicine in Sri Lanka, making it the premier institution for Ayurvedic education nationally.

---

## What You Will Study

The BAMS programme integrates traditional Ayurvedic knowledge with modern medical sciences:

**Year 1 — Sanskrit and Basic Sciences:**
Sanskrit Language (essential for reading classical texts), Basic Principles of Ayurveda (Ashtanga Hridaya, Charaka Samhita), Anatomy and Physiology (both Ayurvedic and modern), Medicinal Plants (Dravyaguna), Introduction to Ayurvedic Pharmacy.

**Year 2 — Traditional Sciences:**
Ayurvedic Pharmacology (Rasa Shastra — herbo-mineral medicines), Classical Ayurvedic texts study, Pathology (Nidana Panchaka), Microbiology, Diagnostics (both pulse diagnosis — Nadi Pariksha — and clinical examination).

**Year 3 — Clinical Foundation:**
Ayurvedic Internal Medicine (Kaya Chikitsa), Panchakarma (the five detoxification and rejuvenation therapies), Surgery and Parasurgical Procedures (Shalya Tantra), Toxicology, Gynaecology and Paediatrics (Striroga and Kaumarabhritya).

**Year 4–5 — Advanced Clinical:**
Advanced Internal Medicine, ENT and Ophthalmology in Ayurveda, Geriatrics and Rejuvenation (Rasayana), Research in Ayurveda, Community Ayurvedic Medicine, Hospital rotations across Ayurvedic teaching hospitals. Forensic Medicine from an Ayurvedic perspective.

**Internship (Year 6):**
One year of supervised clinical practice in Ayurvedic hospitals and dispensaries.

---

## Career Paths in Sri Lanka

- **Government Ayurvedic Medical Officers:** The Department of Ayurveda maintains a network of Ayurvedic hospitals (National Ayurveda Teaching Hospital at Borella, provincial Ayurvedic hospitals) and thousands of Ayurvedic dispensaries across Sri Lanka. BAMS graduates are recruited as Ayurvedic Medical Officers — a permanent government position with salary, pension, and career advancement.
- **Private Ayurvedic practice:** Many Ayurvedic physicians establish private clinics — either standalone or within wellness centres, hotels, and spas.
- **Wellness and spa industry:** Sri Lanka''s booming tourism sector has created strong demand for Ayurvedic treatment centres at five-star hotels and wellness resorts (Amba Estate, Barberyn Beach, Siddhalepa, Jetwing). BAMS graduates manage treatment protocols and supervise therapists.
- **Ayurvedic pharmaceutical industry:** Siddhalepa Ayurvedha Hospital & Herbal Products, Link Natural Products, Samahan, Maharajah, and Ayurvedic manufacturing companies employ BAMS graduates for product development, quality assurance, and regulatory affairs.
- **Research:** Herbal medicine research, clinical trials comparing Ayurvedic and western treatments, ethnopharmacology at government research institutions and universities.
- **International Ayurveda practice:** India (where BAMS is widely recognized), Southeast Asia, UK (complementary medicine practice), Australia, Germany, and Sri Lankan diaspora communities.
- **Export:** Sri Lanka''s herbal medicine products (Siddhalepa, Samahan, Link Natural) are exported globally — BAMS graduates contribute to product formulation and quality.

---

## Entry Requirements

**A/L Stream:** Biological Science
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Ayurveda Medicine has cutoffs typically in the **0.7 to 1.2** range — more accessible than western Medicine but still competitive. GWUIM (032B) is a dedicated Ayurvedic university and often has slightly different cutoffs from Colombo (032A).

---

## Special Notes

- The BAMS is a 5-year professional degree (plus 1-year internship), comparable in duration to MBBS.
- Registration with the Sri Lanka Ayurvedic Medical Council (SLAMC) is required before practice.
- Sanskrit proficiency is an important part of the curriculum — students learn to read classical Ayurvedic texts in the original language.
- Growing global interest in traditional and complementary medicine has significantly expanded the international market for Sri Lankan Ayurvedic practitioners.
- Sri Lanka''s unique position (producing high-quality medicinal herbs like Cinnamon, Cardamom, Pepper, and endemic species) gives Sri Lankan Ayurvedic pharmaceutical research a unique competitive advantage.
', 'c72de01f90ecb6c9504ac5ee08f01e87b87a7b21efb3f66bae52d6469fdaf776');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('033', '# Unani Medicine and Surgery (BUMS)
**Course Number:** 033
**Degree:** Bachelor of Unani Medicine and Surgery (BUMS)
**Duration:** 5 years (plus one year internship)
**Entry Stream:** Biological Science
**Available at:** University of Colombo Faculty of Indigenous Medicine (033A)

---

## Overview

Unani Medicine is a traditional healing system originating in ancient Greece and developed through Islamic scholarship, brought to South Asia via Persia and the Mughal Empire. It is practiced widely in Sri Lanka''s Muslim community and is recognized alongside Ayurveda in Sri Lanka''s parallel indigenous medicine system. The Faculty of Indigenous Medicine at the University of Colombo is the only state-university provider of BUMS in Sri Lanka.

Unani practitioners (Hakims) use herbal, mineral, and animal-origin remedies alongside dietary and lifestyle interventions based on the principles of humoral medicine (mizaj — temperament; and four humours — blood, phlegm, yellow bile, black bile).

---

## What You Will Study

The BUMS curriculum integrates classical Unani sciences with modern medical knowledge:

**Year 1 — Foundations:**
Ilmul Advia (Unani Pharmacology), Kulliyat-e-Tibb (Principles and Philosophy of Unani Medicine), Arabic Language (for reading classical texts), Anatomy and Physiology (modern biomedical), Tasreeh ul Badan (Unani Anatomy).

**Year 2 — Clinical Sciences:**
Mizajiyat (Temperament Theory), Amraz-e-Nizami (Unani Pathology), Ilaj bil Ghiza (Dietotherapy), Urology and Proctology in Unani, Microbiology, Biochemistry.

**Year 3–5 — Applied Unani Medicine:**
Mualejat (Unani Internal Medicine), Ilm ul Jirahaat (Surgery in Unani tradition), Gynaecology and Obstetrics (Amraz-e-Niswan), Paediatrics, Moalejat-e-Nafsiyat (Psychiatry), Ilaj bil Yad (Physiotherapy and Manual Medicine). Clinical placements in Unani hospitals and dispensaries.

**Internship (Year 6):**
One year of supervised clinical practice.

---

## Career Paths in Sri Lanka

- **Government Unani Medical Service:** The Department of Ayurveda manages a Unani section providing government Hakims at Unani hospitals and dispensaries, primarily serving Muslim communities in the Western, Eastern, and Northern provinces.
- **Private Unani practice:** Private Unani clinics serving the Muslim community in Colombo, Kandy, Puttalam, Mannar, Ampara, and Eastern Province.
- **Unani pharmaceutical industry:** Unani herbal product manufacturing companies.
- **Community health:** Working within Muslim community health programmes.
- **Research:** Research on traditional Islamic medicine formulations and their pharmaceutical applications.
- **International:** Unani medicine is practiced in India (where BUMS is widely recognized), Pakistan, Bangladesh, and among diaspora communities.
- **Saudi Arabia and Gulf states:** Islamic medicine practitioners are employed in some Gulf health systems.

---

## Entry Requirements

**A/L Stream:** Biological Science (mandatory)
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Unani Medicine at Colombo (033A) has cutoffs typically in the **0.6 to 1.0** range — more accessible than western Medicine. The intake is small (fewer than 30 students per year), serving a specialized community need.

---

## Special Notes

- Arabic language is a core part of the curriculum — students should have some familiarity with Arabic script.
- The BUMS is particularly pursued by students from Sri Lanka''s Muslim community who wish to combine traditional practice with government service.
- Registration with the Sri Lanka Ayurvedic Medical Council (SLAMC) — which also covers Unani and Siddha medicine — is required before practice.
- The BUMS gives graduates access to the government Unani Medical Service while also allowing private practice.
', '5c8cd8c2f50ae7a045b8cac8efb1a2cc6d8c7bc37314f29688f120a1b4bdd750');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('034', '# Fashion Design & Product Development
**Course Number:** 034
**Degree:** Bachelor of Design (Honours) in Fashion Design and Product Development
**Duration:** 4 years
**Entry Stream:** Any A/L stream (subject to aptitude test)
**Available at:** University of Moratuwa (034G)

---

## Overview

The Bachelor of Design in Fashion Design and Product Development is a premier degree programme designed to bridge the gap between creative design and industrial manufacturing. In the context of Sri Lanka, where the apparel sector is a primary pillar of the national economy, this degree is vital for shifting the industry from a "cut-and-sew" model to a high-value design and innovation hub.

The University of Moratuwa, as the pioneer of this programme in Sri Lanka, maintains strong ties with the Joint Apparel Association Forum (JAAF) and major export manufacturers. The curriculum is uniquely positioned to produce graduates who are not only skilled in aesthetics and trend forecasting but also possess the technical expertise in garment construction, supply chain management, and textile technology required to lead in a competitive global market.

---

## What You Will Study

**Year 1: Foundations of Design**
Focuses on fundamental design principles, fashion illustration, colour theory, and the history of fashion. Students are introduced to basic garment construction, textile science, and the basics of the global apparel industry.

**Year 2: Technical Development**
Deepens the focus on pattern making (2D and 3D CAD), draping, and advanced garment fitting. Students begin exploring fashion marketing, consumer behaviour, and the technical aspects of fabric properties and textile manufacturing.

**Year 3: Industrial Application & Specialization**
Students engage with industrial processes, including mass production techniques, quality assurance, and sustainable design practices. This year often involves industry placements or internships with leading Sri Lankan apparel manufacturers.

**Year 4: Innovation & Final Collection**
The final year is dedicated to the development of a comprehensive final design collection. Students conduct independent research, execute a professional-grade design project, and complete a dissertation focusing on industry-specific challenges such as supply chain optimization or fashion technology.

---

## Career Paths in Sri Lanka

- **Fashion Designer:** Creating original collections for local brands or export-oriented manufacturers like MAS Holdings or Brandix.
- **Product Developer:** Managing the technical lifecycle of a garment from concept to mass production, working with firms like Hirdaramani Group.
- **Fashion Merchandiser:** Analysing market trends and managing inventory for retail giants like ODEL, Cotton Collection, or international buying offices.
- **Textile Technologist:** Working in fabric sourcing and quality control departments to ensure material standards meet international export requirements.
- **Fashion Illustrator/Graphic Designer:** Creating digital prints and technical sketches for apparel brands using industry-standard software.
- **Postgraduate Study:** Graduates can pursue Master’s degrees in Fashion Management, Textile Engineering, or Sustainable Fashion at the University of Moratuwa or through international partnerships in the UK or Australia.

---

## Entry Requirements

Admission is highly competitive and is not based on Z-score alone. Candidates must satisfy the minimum university admission requirements for the GCE Advanced Level (any stream). All applicants must pass a mandatory **Aptitude Test** conducted by the University of Moratuwa, which evaluates creative ability, design thinking, and technical drawing skills. The medium of instruction is English.

---

## Differences Between Universities

While the University of Moratuwa (034G) is the primary provider of the B.Des. Honours degree, other institutions like the Open University of Sri Lanka (OUSL) offer a Bachelor of Industrial Studies (BIS) in the same field. The University of Moratuwa is distinct for its intensive, full-time studio-based environment, direct industry integration with the apparel export sector, and its focus on high-level design innovation. The OUSL programme is often better suited for those seeking a flexible, distance-learning approach combined with industrial studies.

---

## Special Notes

- **Professional Recognition:** Graduates are highly sought after by the Sri Lankan apparel industry and are often recruited directly through campus placement drives.
- **Industry Demand:** There is a significant demand for graduates who can combine creative design with technical production knowledge, particularly in the context of "Made in Sri Lanka" sustainable apparel initiatives.
- **Portfolio:** Prospective students are strongly encouraged to begin building a portfolio of creative work, as this is essential for both the aptitude test and future career placement.
- **Licensing:** No specific professional license is required to practice as a fashion designer in Sri Lanka, but membership in industry-related bodies can enhance professional networking.', '748a3ce7def1a7d130a110b3228f63516d0d15148571c166a7e43606f23c44d9');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('035', '# Food Science and Technology (B.Sc.)
**Course Number:** 035
**Degree:** Bachelor of Science (Honours) in Food Science and Technology
**Duration:** 4 years
**Entry Stream:** Biological Science, Biosystems Technology
**Available at:** University of Sri Jayewardenepura Department of Food Science and Technology (035A), Sabaragamuwa University Faculty of Agricultural Sciences (035B)

---

## Overview

Food Science and Technology applies biological, chemical, and engineering principles to the production, processing, preservation, and quality assurance of food. Sri Lanka has a significant food and beverage manufacturing industry — tea, coconut products, spices, processed foods, confectionery, and seafood — all requiring food science expertise. 

With growing global interest in food safety, functional foods, and sustainable food systems, food science is a future-facing career.

---

## What You Will Study

**Year 1 — Science Foundations:**
General Chemistry and Organic Chemistry, Food Biochemistry, Microbiology, Mathematics and Statistics, Introduction to Food Science.

**Year 2 — Core Food Science:**
Food Chemistry (composition of carbohydrates, proteins, fats, vitamins, minerals in food), Food Microbiology (spoilage organisms, pathogens, preservation), Food Processing Technology (pasteurization, UHT, canning, freezing, drying), Food Engineering (heat transfer, mass transfer, equipment design), Food Analysis (analytical methods for food quality testing).

**Year 3 — Applied Food Technology:**
Quality Assurance and Food Safety Management Systems (HACCP, ISO 22000, GMP), Sensory Evaluation (taste panels, texture analysis), Product Development, Packaging Technology, Food Regulations and Labelling, Fermented Foods (vinegar, yoghurt, traditional Sri Lankan ferments). Factory visits and industrial training.

**Year 4 — Research:**
Research Dissertation (product development or food safety research), Advanced topics, Food Policy, Nutraceuticals and Functional Foods.

---

## Career Paths in Sri Lanka

- **Food manufacturing QC/QA:** Quality Control and Quality Assurance roles at food companies — Nestlé Lanka, CIC Agri, Cargills, Ceylon Biscuits Limited, Prima, Keells Food Products, and hundreds of SME food manufacturers.
- **Tea industry:** Tea Research Institute, regional tea factories, tea exporters — quality testing and processing research.
- **Export food products:** Sri Lanka exports coconut products (desiccated coconut, coconut oil, coconut milk), spices, rubber, and processed foods. Food scientists ensure export quality standards.
- **Government food regulation:** Food Control Unit (Ministry of Health), Sri Lanka Standards Institution (SLSI), National Aquatic Resources Research and Development Agency for seafood.
- **R&D and product development:** Developing new food products for local and export markets.
- **Bakery and confectionery:** Quality and production management in Sri Lanka''s growing bakery sector.
- **Hospitality food safety:** Food safety management in hotels and food service operations.
- **International food industry:** Australia, UK, and Middle East food manufacturing sectors recruit food technologists.

---

## Entry Requirements

**A/L Stream:** Biological Science (primary); Biosystems Technology may also qualify
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Food Science and Technology cutoffs are typically in the **0.6 to 1.1** range — accessible to most Biological Science students, with SJP (035A) slightly more competitive than Sabaragamuwa (035B).

---

## Special Notes

- Sri Lanka''s tea sector (the world''s fourth-largest tea exporter) is a major employer of food scientists.
- Sri Lanka''s rich culinary heritage (spices, tropical fruits, traditional fermented foods) creates unique research opportunities in indigenous food systems and nutraceuticals.
- SLSI (Sri Lanka Standards Institution) certification is increasingly required for food products — creating demand for food scientists who understand standardization.
', 'd6b81f486d1e7ab6d0ebc35c849d1786be0da124bc89a694be0a4bd3a411c450');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('036', '# Siddha Medicine and Surgery
**Course Number:** 036
**Degree:** Bachelor of Siddha Medicine and Surgery (BSMS)
**Duration:** 5 years (plus 1 year of compulsory internship)
**Entry Stream:** Biological Science
**Available at:** University of Jaffna (036E), Trincomalee Campus, Eastern University, Sri Lanka (036W)

---

## Overview

The Bachelor of Siddha Medicine and Surgery (BSMS) is a specialized professional degree programme dedicated to the study of the Siddha system of medicine, one of the oldest traditional medical systems in the world. In the Sri Lankan context, this degree is vital for preserving and advancing indigenous healthcare practices. It integrates ancient traditional wisdom with modern medical sciences, preparing graduates to serve as primary healthcare providers who offer holistic, patient-centered care.

The industry for Siddha medicine in Sri Lanka is supported by the Department of Ayurveda under the Ministry of Health. Graduates play a critical role in the public health sector, particularly in rural and underserved areas where traditional medicine is highly sought after. Both the University of Jaffna and the Trincomalee Campus of Eastern University are notable for their dedicated faculties that provide clinical training, research opportunities, and exposure to the rich heritage of Tamil medical literature and medicinal plant studies.

---

## What You Will Study

**Year 1:** Foundational studies including Basic Principles of Siddha Medicine, History of Siddha Medicine, Anatomy (Siddha and Modern), Physiology, and Biochemistry.

**Year 2:** Advanced study of Siddha Pharmacology (Gunapadam), Toxicology (Visha Vaidyam), Pathology, and Microbiology. Students begin learning the identification and processing of herbal, mineral, and metallic medicines.

**Year 3:** Clinical subjects including General Medicine (Noi Naadal), Pediatrics (Baala Vaidyam), and specialized Siddha diagnostic techniques (Pulse reading/Naadi).

**Year 4:** Advanced clinical practice including Surgery (Siddha Surgery/Sastra), Obstetrics and Gynecology (Magalir Maruthuvam), and Forensic Medicine.

**Year 5:** Final year clinical rotations, research methodology, and the completion of a mandatory research project or dissertation. Students also undergo intensive clinical clerkships in hospital settings.

---

## Career Paths in Sri Lanka

- **Medical Officer (Siddha):** Employed by the Department of Ayurveda, Ministry of Health, to work in government Ayurvedic/Siddha hospitals and rural dispensaries.
- **Private Practitioner:** Establishing private clinics to provide traditional healthcare services to the public.
- **Academic/Researcher:** Working as a lecturer or research assistant at universities or the Bandaranaike Memorial Ayurveda Research Institute (BMARI).
- **Pharmaceutical Industry:** Roles in the manufacturing, quality control, and R&D of Siddha herbal products with companies like Siddhalepa or private indigenous medicine manufacturers.
- **Public Health Consultant:** Working with NGOs or government bodies on community health projects focusing on traditional wellness and preventative care.
- **Postgraduate Study:** Pursuing an MD (Siddha) or M.Phil/PhD in fields like Pharmacology, Clinical Medicine, or Medicinal Botany to specialize further.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Biological Science stream. Candidates must have passed Chemistry, Physics, and Biology. Selection is highly competitive and determined by the Z-score system. The medium of instruction is primarily Tamil, though students must be proficient in English for modern medical literature. No specific physical requirements are mandated, but a high level of dedication to clinical work and patient interaction is expected.

---

## Differences Between Universities

- **University of Jaffna:** Offers a long-standing academic tradition in Siddha medicine with a well-established Faculty of Siddha Medicine. It benefits from deep cultural roots in the region and extensive access to traditional medical literature and experienced practitioners.
- **Trincomalee Campus (Eastern University):** A newer, rapidly developing faculty that focuses on integrating modern clinical infrastructure with traditional practices. It offers a unique geographic advantage for studying coastal and regional medicinal plants and serves a diverse community in the Eastern Province.

---

## Special Notes

Graduates must register with the Sri Lanka Ayurvedic Medical Council (SLAMC) to practice as a registered medical practitioner in Sri Lanka. The degree includes a mandatory one-year internship at a government-approved hospital, which is a prerequisite for full registration. While the degree is highly respected within the South Asian region, those seeking overseas employment should note that recognition varies by country and may require additional licensing examinations. The programme is intensive, combining rigorous academic study with practical clinical training.', '5a481ad8838b36df2d0b91b523768899396d7ad780c9d3a4a7a2e263782f8bd4');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('037', '# Nursing (B.Sc.)
**Course Number:** 037
**Degree:** Bachelor of Science (Honours) in Nursing
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Colombo Faculty of Allied Health Sciences (037A), University of Peradeniya Faculty of Allied Health Sciences (037B)

---

## Overview

Nursing is one of the most essential healthcare professions and a rapidly growing career pathway for Sri Lankan students. A B.Sc. (Honours) in Nursing from a state university is a degree-level qualification that goes beyond the traditional diploma-level nursing training offered by nursing schools — it produces nurses with deeper scientific knowledge, research skills, and leadership capabilities.

Sri Lanka''s state university nursing degree programme is relatively young compared to other allied health degrees, but has grown significantly in national and international recognition. Nursing graduates are in high demand both domestically and internationally, particularly in the UK, Australia, Canada, Middle East, and Maldives.

---

## What You Will Study

**Year 1 — Sciences and Nursing Foundations:**
Human Anatomy and Physiology, Microbiology and Infection Control, Biochemistry, Nutrition, Psychology, Fundamentals of Nursing (basic patient care techniques — bed baths, vital signs, wound care, patient positioning), Introduction to Professional Nursing Ethics.

**Year 2 — Clinical Nursing Specialties:**
Medical-Surgical Nursing (caring for patients with medical and surgical conditions), Pharmacology for Nurses (drug administration, dosage calculations, drug interactions), Maternal and Child Health Nursing (antenatal, postnatal, labour care, neonatal nursing), Psychiatric Nursing (mental health patient care), Community Health Nursing (public health outreach, home nursing). Clinical placements in hospital wards begin.

**Year 3 — Advanced Practice:**
Critical Care Nursing (intensive care units, high dependency units), Paediatric Nursing, Geriatric Nursing, Oncology Nursing, Perioperative Nursing (operating theatre care), Trauma and Emergency Nursing, Nursing Research Methods. Extended ward placements across specialties.

**Year 4 — Leadership and Research:**
Nursing Administration and Management, Healthcare Policy and Nursing Leadership, Community and Public Health Nursing, Research Dissertation, Clinical Leadership project. Students take leadership roles in ward placements.

---

## Career Paths in Sri Lanka

- **Government hospital nursing service:** National hospitals, teaching hospitals, district hospitals, and community health centres employ the largest number of nurses in Sri Lanka. Government nurses are civil servants with job security, pension, and the opportunity to transfer across the country.
- **Private hospital nursing:** Private hospitals (Lanka Hospitals, Asiri, Nawaloka, Durdans, Apollo, and many newer private hospitals) actively recruit B.Sc. nurses for ward, ICU, OT, and specialty roles, often at higher salaries than the government service.
- **ICU and specialist nursing:** Intensive Care Units, Cardiac Care Units, Neonatal Intensive Care Units, and specialty cancer wards require nurses with advanced training. B.Sc. nursing graduates are preferred for these roles.
- **Community and public health nursing:** Ministry of Health public health nursing officers work at the community level, conducting immunization programmes, maternal health clinics (Field Health Centre — FHC), and home visits.
- **International nursing:** The highest-demand career path for many Sri Lankan nursing graduates. UK (NMC registration), Australia (AHPRA), Canada, Maldives, and Middle East (UAE, Qatar, Saudi, Oman, Kuwait) all have ongoing demand for nurses. UK and Australian nursing salaries are significantly higher than Sri Lankan scales.
- **Nurse educator:** Teaching in university nursing departments or government nursing schools.
- **Nursing management:** Senior nursing officers, ward managers, and chief nursing officers in large hospitals.
- **Research:** Nursing research, clinical trials nursing, healthcare quality improvement roles.

---

## Entry Requirements

**A/L Stream:** Biological Science (mandatory)
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Nursing cutoffs are typically in the **0.6 to 1.0** range — one of the more accessible Biological Science programmes, making it achievable for students across a wide range of Z-scores. Colombo (037A) has slightly higher cutoffs than Peradeniya (037B) due to location preference.

---

## Special Notes

- The B.Sc. degree is a separate and higher qualification from the traditional 3-year nursing diploma offered by government nursing schools. Both qualify for nursing practice, but the B.Sc. opens greater career advancement opportunities.
- International nursing is a major career pathway. The investment in a B.Sc. Nursing degree significantly strengthens overseas registration applications.
- Male students are equally eligible for Nursing — male nurses are in demand in ICUs, psychiatric units, and surgical wards.
- Emotional resilience and genuine commitment to patient care are important personal qualities for this profession.
', '996b968ba13f490724eb5770d3839d822bb7687f804f4edc69971bb11a824c7e');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('038', '# Information and Communication Technology
**Course Number:** 038
**Degree:** Bachelor of Information and Communication Technology (Honours)
**Duration:** 4 years
**Entry Stream:** Technology Stream (with ICT as a subject)
**Available at:** Rajarata University of Sri Lanka (038K), University of Vavuniya, Sri Lanka (038R)

---

## Overview

The Bachelor of Information and Communication Technology (BICT) is a specialized degree designed to bridge the gap between theoretical computer science and the practical, hands-on requirements of the modern Sri Lankan technology industry. As the government continues to prioritize the "Technology Stream" in the national education system, this degree serves as a vital pathway for students to gain the technical proficiency required to drive Sri Lanka’s digital economy.

The programme is housed within the Faculties of Technology at the respective universities, focusing on applied computing, software development, and systems management. It is particularly relevant given the rapid growth of the Sri Lankan IT/BPM sector, which is a significant contributor to the country''s export revenue. Students are trained to solve real-world problems, making them highly employable in both the local corporate sector and the global remote-work market.

---

## What You Will Study

**Year 1: Foundation in Technology**
Focuses on core fundamentals including Programming Principles, Mathematics for Technology, Computer Systems, Database Management Systems, and Communication Skills. Students are introduced to the basics of web development and hardware architecture.

**Year 2: Core Technical Competencies**
Advanced programming (Java/Python), Data Structures and Algorithms, Object-Oriented Analysis and Design, Operating Systems, and Networking. Students begin working with enterprise-level databases and software engineering methodologies.

**Year 3: Specialization and Industry Exposure**
Students delve into specialized areas such as Web and Mobile Application Development, Cloud Computing, Information Security, and Human-Computer Interaction. This year includes a mandatory industrial training component where students work in local software houses or IT departments.

**Year 4: Advanced Research and Professional Practice**
Focuses on emerging technologies like Artificial Intelligence, Data Analytics, and Internet of Things (IoT). The final year is dominated by a comprehensive Individual Research Project or a capstone software development project, alongside modules on Entrepreneurship and Professional Ethics.

---

## Career Paths in Sri Lanka

*   **Software Engineer:** Working at major Sri Lankan firms like Virtusa, WSO2, or IFS, developing enterprise-grade software solutions.
*   **Systems Administrator:** Managing IT infrastructure for banks (e.g., BOC, Sampath Bank) or large-scale manufacturing plants.
*   **Network Engineer:** Designing and maintaining connectivity solutions for telecommunication giants like Dialog or SLT-Mobitel.
*   **Database Administrator:** Ensuring data integrity and security for government institutions or large retail chains.
*   **IT Entrepreneur/Freelancer:** Leveraging technical skills to build startups or provide services on global platforms like Upwork or Fiverr.
*   **Postgraduate Study:** Graduates can pursue an M.Sc. or M.Phil. in Computer Science, Data Science, or MBA programmes at institutions like the University of Moratuwa or the University of Colombo.

---

## Entry Requirements

Admission is strictly through the University Grants Commission (UGC) based on the G.C.E. Advanced Level examination. Students must have followed the **Technology Stream** and achieved the required Z-score for the respective university. Proficiency in English is essential as the medium of instruction is English. Candidates must meet the minimum subject requirements as stipulated by the UGC for the Technology stream. The Z-score cutoff is highly competitive, reflecting the high demand for ICT professionals in the current job market.

---

## Differences Between Universities

*   **Rajarata University (038K):** Located in Mihintale, the faculty emphasizes the integration of ICT with agricultural and rural development technologies, offering a unique perspective on how technology can solve regional challenges.
*   **University of Vavuniya (038R):** Situated in the Northern Province, this faculty has a strong focus on fostering an innovative ecosystem. It provides intensive entrepreneurial training and mentorship programmes, often collaborating with regional tech hubs to prepare students for the evolving digital landscape.

---

## Special Notes

The BICT degree is designed to align with industry standards, though students are encouraged to pursue professional certifications (e.g., AWS, Cisco CCNA, Microsoft Certified) alongside their degree to enhance employability. The medium of instruction is English. Graduates are eligible to apply for professional membership in the Computer Society of Sri Lanka (CSSL). There is a high demand for these graduates in overseas markets, particularly in the Middle East, Europe, and Australia, making this a globally recognized qualification.', 'a562083a7180c07710c88c75973df1c9ca410b2c5b64a2f55b40b8eb3af84c0f');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('039', '# Agricultural Technology and Management
**Course Number:** 039
**Degree:** Bachelor of Science (Honours) in Agricultural Technology and Management
**Duration:** 4 years
**Entry Stream:** Biological Science, Physical Science (Biology preferred)
**Available at:** University of Peradeniya (039B)

---

## Overview

Agricultural Technology and Management at the University of Peradeniya is offered through the Faculty of Agriculture — one of the oldest and most prestigious agricultural education institutions in South Asia, established in 1949. Unlike the standard Agriculture degree (004), this programme places greater emphasis on the management, agribusiness, and technology dimensions of agricultural systems — preparing graduates to run farms, agro-enterprises, and agricultural supply chains rather than solely focusing on crop science.

Sri Lanka''s agricultural sector remains the backbone of the rural economy, employing over a third of the workforce and underpinning the livelihoods of millions. However, the sector faces serious challenges: low productivity, aging farmer populations, climate change impacts, post-harvest losses, and poor market integration. Graduates in Agricultural Technology and Management are specifically trained to address these challenges by bringing business acumen and technology application alongside agronomic knowledge.

The University of Peradeniya''s Faculty of Agriculture benefits from the adjacent Peradeniya Royal Botanic Gardens, experimental farms, and close ties with the Department of Agriculture, Tea Research Institute, and Coconut Research Institute — giving students practical field experience in a unique agricultural learning environment.

---

## What You Will Study

**Year 1 — Agricultural Foundations:**
Crop Science (agronomy, horticulture), Soil Science, Plant Biology, Animal Husbandry, Fundamentals of Agricultural Chemistry, Introduction to Agribusiness, Computer Applications, Communication Skills.

**Year 2 — Technology and Production Systems:**
Precision Agriculture and Farm Technology, Irrigation and Water Management, Pest and Disease Management (IPM), Agricultural Mechanization, Post-Harvest Technology, Food Processing Fundamentals, Agricultural Economics, Farm Business Management.

**Year 3 — Management and Value Chain:**
Agribusiness Management, Agricultural Marketing and Supply Chain, Project Planning and Appraisal, Agricultural Extension Methods, Rural Development and Sociology, Agricultural Finance and Credit, GIS Applications in Agriculture, Environmental Impact Assessment, Field Practical Training.

**Year 4 — Research and Enterprise:**
Research project in agricultural technology or management, Technology Transfer and Entrepreneurship, Export Agriculture, Smart Farming and Digital Agriculture, Agricultural Policy Analysis, Sustainable Agriculture Systems.

---

## Career Paths in Sri Lanka

- **Agribusiness management:** Plantation companies (Hayleys Agro, WATAWALA Plantations, Agarapatana Plantations), export crop companies, outgrower scheme management.
- **Agricultural extension:** Government agricultural extension officers (Department of Agriculture, provincial councils) helping farmers adopt improved technologies.
- **Agricultural supply chain:** Cooperative societies, Dedicated Economic Centres (DECs), Ceylon Agri Service — managing logistics from farm to market.
- **Food processing industry:** Production management, quality control, and procurement at food manufacturing companies.
- **Rural banking and microfinance:** Agricultural credit officers at Sanasa Development Bank, Regional Development Bank, and commercial banks with agriculture portfolios.
- **Development sector and NGOs:** Project implementation, monitoring and evaluation for food security and rural livelihoods programmes (UNDP, FAO, Oxfam, World Vision in Sri Lanka).
- **Government sector:** Department of Agriculture, Provincial Agriculture Departments, agricultural statistics divisions.
- **Postgraduate study:** MSc in Agribusiness Management, Agricultural Economics, or Sustainable Agriculture at Peradeniya, or at Asian Institute of Technology (AIT), University of Reading, or Wageningen University.

---

## Entry Requirements

**A/L Stream:** Biological Science (Biology + Chemistry + Agriculture or Physics is the primary pathway)
**Typical subjects:** Biology + Chemistry + Agricultural Science (or Physics/Mathematics as third subject)
**Z-score context:** Agricultural Technology and Management (039B) typically has lower Z-score cutoffs than the main Agriculture degree (004B at Peradeniya) because it is less well known despite offering distinct career advantages in agribusiness. Students interested in agriculture with a business orientation who fall short of Medicine or Engineering cutoffs find this an excellent option.

---

## Special Notes

- The University of Peradeniya''s Faculty of Agriculture is **internationally recognized** and has produced many leaders in Sri Lanka''s agricultural sector, tea industry, and international food organizations.
- Students have access to the faculty''s experimental farms, seed production fields, and the proximity to major research institutions (TRI, CRI, Rubber Research Institute) for research project placement.
- The **agritourism and export horticulture** sectors are growing rapidly in Sri Lanka, creating new roles for graduates with both technical and management training.
- The programme differs from the general Agriculture degree by its emphasis on farm economics, supply chain, and technology management — making it more suitable for students who want business roles in the agricultural sector rather than field-based research.
- Graduates are eligible for roles in the Sri Lanka Administrative Service (through competitive examinations), the Department of Agriculture, and as development bank credit officers.
', '88c6b0c099665338ddeac6bf909381886008901997a0b1671178d20e18793d6d');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('040', '# Management Studies
**Course Number:** 040
**Degree:** Bachelor of Business Management (Honours) in Management Studies
**Duration:** 4 years
**Entry Stream:** Commerce Stream, Arts Stream, Biological Science, Physical Science, and Technology Streams (Any A/L stream)
**Available at:** University of Vavuniya, Sri Lanka (040R), Trincomalee Campus, Eastern University, Sri Lanka (040W)

---

## Overview

Management Studies is a comprehensive undergraduate programme designed to equip students with the essential theoretical knowledge and practical skills required to navigate the complexities of modern business environments. In the Sri Lankan context, this degree is vital for developing the next generation of leaders capable of managing human resources, financial assets, marketing operations, and organizational strategy within both the public and private sectors.

The programme is uniquely positioned to address the needs of regional economic development. By studying at the University of Vavuniya or the Trincomalee Campus of the Eastern University, students gain a localized perspective on entrepreneurship, supply chain management, and organizational behavior. These faculties are notable for their commitment to bridging the gap between academic theory and the practical realities of the Sri Lankan business landscape, preparing graduates to contribute effectively to the nation''s growing service and manufacturing industries.

---

## What You Will Study

**Year 1: Foundations of Business**
Focuses on the core pillars of business, including Principles of Management, Micro and Macroeconomics, Business Mathematics, Financial Accounting, and Business Communication. Students also receive an introduction to Information Technology for business.

**Year 2: Functional Management**
Deepens knowledge in specialized areas such as Human Resource Management, Marketing Management, Cost Accounting, Organizational Behavior, and Business Law. Students begin to analyze the legal and ethical frameworks governing Sri Lankan commerce.

**Year 3: Advanced Business Operations**
Covers strategic subjects including Financial Management, Operations Management, Management Information Systems, and Research Methodology. Students often choose elective modules based on their interest in areas like Entrepreneurship, Banking, or Tourism Management.

**Year 4: Specialization and Research**
The final year focuses on advanced strategic management and leadership. Students are required to conduct an Independent Research Project or Dissertation, applying academic research to solve a real-world business problem. This year also includes professional internships to ensure industry readiness.

---

## Career Paths in Sri Lanka

*   **Human Resource Executive:** Managing recruitment, payroll, and employee relations at firms like MAS Holdings or John Keells Holdings.
*   **Marketing Coordinator:** Developing brand strategies and digital marketing campaigns for local FMCG companies or advertising agencies.
*   **Banking Associate:** Handling credit analysis, customer relations, or operations at institutions like Bank of Ceylon (BOC) or Commercial Bank.
*   **Operations Manager:** Overseeing logistics and supply chain efficiency in the manufacturing or export sectors, common in the Export Processing Zones.
*   **Entrepreneur/Business Consultant:** Starting a small-to-medium enterprise (SME) or providing consultancy services to local businesses, supported by the National Enterprise Development Authority (NEDA).
*   **Postgraduate Study:** Graduates can pursue an MBA or specialized Master’s degrees in Finance or HRM at institutions like the University of Colombo or the Postgraduate Institute of Management (PIM).

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results. The programme is unique in that it accepts students from all A/L streams (Commerce, Arts, Science, and Technology). Candidates must satisfy the minimum university admission requirements set by the University Grants Commission (UGC). The Z-score competitiveness varies annually based on the applicant pool; students are advised to check the latest UGC handbook for cutoff trends. The medium of instruction is English, and proficiency in the language is essential for academic success.

---

## Differences Between Universities

*   **University of Vavuniya:** Offers a strong focus on regional economic development and entrepreneurship, leveraging its location to provide students with insights into the Northern Province''s emerging business sectors.
*   **Trincomalee Campus (Eastern University):** Notable for its Department of Business and Management Studies, which emphasizes the intersection of tourism, logistics, and port-related management due to its proximity to the Trincomalee harbor and coastal economic zones.

---

## Special Notes

This degree provides a solid foundation for professional qualifications. Graduates are often eligible for exemptions from professional bodies such as the Institute of Chartered Accountants of Sri Lanka (CA Sri Lanka), CIMA, or ACCA, depending on the specific modules completed. While the degree is primarily academic, the inclusion of internships is a mandatory component to ensure students gain the practical exposure required by local employers. Graduates are well-positioned for both public sector administrative roles and private sector management positions.', '1906dc1feab933196ac7e73ad215e20c6a642c9a83be52e4eb3573cb0ea83096');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('041', '# Arts
**Course Number:** 041
**Degree:** Bachelor of Arts (Honours) in Performing Arts
**Duration:** 4 years
**Entry Stream:** Arts Stream
**Available at:** Sripalee Campus, University of Colombo (041S)

---

## Overview

The Bachelor of Arts in Performing Arts at the Sripalee Campus, University of Colombo, is a specialized degree designed to bridge the gap between traditional aesthetic practices and modern media industries. Unlike general Arts degrees, this programme focuses on the intersection of creative expression, cultural heritage, and contemporary mass communication, reflecting the evolving needs of Sri Lanka’s creative economy.

The Sripalee Campus is uniquely positioned in Horana, providing a serene environment conducive to artistic exploration while maintaining strong academic ties to the University of Colombo. The faculty emphasizes a blend of theoretical knowledge and practical application, preparing students to navigate the professional landscape of Sri Lankan television, theatre, film, and digital media production.

---

## What You Will Study

**Year 1: Foundations of Aesthetics and Media**
Focuses on the history of performing arts, basic communication theory, introduction to mass media, and foundational training in music, dance, or drama. Students explore the cultural context of Sri Lankan arts.

**Year 2: Technical Skills and Creative Development**
Students delve into specialized modules such as scriptwriting, cinematography, stage management, and digital media production. This year emphasizes the technical aspects of media creation and the evolution of performance styles.

**Year 3: Advanced Specialization and Production**
Students choose a specialization track (e.g., Film Studies, Television Production, or Performing Arts). Coursework includes advanced directing, media ethics, cultural policy in Sri Lanka, and practical workshops in studio production.

**Year 4: Research and Professional Practice**
The final year is dedicated to a comprehensive independent research dissertation and a major creative project (e.g., a short film, a theatrical production, or a media campaign). Students also undergo a professional internship to gain industry experience.

---

## Career Paths in Sri Lanka

*   **Television and Film Production:** Working with major local networks like Sirasa TV, Derana, or ITN as producers, directors, or scriptwriters.
*   **Media and Corporate Communications:** Managing public relations and creative content for corporate firms or advertising agencies like Grant Group or Phoenix Ogilvy.
*   **Arts Administration:** Managing cultural institutions, galleries, or theatre troupes under the Department of Cultural Affairs or private arts organizations.
*   **Digital Content Creation:** Developing multimedia content for digital platforms, focusing on social media strategy and creative storytelling for online audiences.
*   **Education and Academia:** Pursuing teaching roles or lecturing in aesthetic studies at the school or university level after completing postgraduate qualifications.
*   **Postgraduate Study:** Graduates can advance to a Master’s in Mass Media or related fields at the University of Colombo or pursue international scholarships in Creative Industries and Media Studies.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Arts stream. Candidates must satisfy the minimum university entry requirements set by the University Grants Commission (UGC). Proficiency in Sinhala or English is essential, as the medium of instruction involves both. An aptitude test is typically required to assess creative potential and suitability for the performing arts discipline. The Z-score requirement is highly competitive, reflecting the limited intake and the specialized nature of the Sripalee Campus.

---

## Differences Between Universities

The Sripalee Campus (041S) is distinct from general Arts faculties in other state universities because it is specifically dedicated to the study of Performing Arts and Mass Media. While universities like the University of Kelaniya or the University of Sri Jayewardenepura offer broader Arts degrees with optional media modules, Sripalee provides a concentrated, studio-based environment. Its curriculum is more heavily weighted toward practical media production and aesthetic performance than the traditional, theory-heavy Arts degrees found elsewhere.

---

## Special Notes

Graduates of this programme are well-positioned to enter the creative industries, which are currently experiencing a digital transformation in Sri Lanka. While there is no formal "licensing" body for performing arts, the degree is highly regarded by media houses and cultural organizations. Students are encouraged to build a strong portfolio of creative work throughout their four years, as this is often more important than academic grades when applying for roles in the competitive media sector. The degree also serves as a strong foundation for those looking to pursue postgraduate conversion pathways into Law, International Relations, or Business Management.', '71458ff17ca17d2f27f9ef0f32961baaf2c6bbc07c1f2419139ec8e6b8f9136a');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('042', '# Arts
**Course Number:** 042
**Degree:** Bachelor of Arts (General/Special)
**Duration:** 3 years (General) or 4 years (Special)
**Entry Stream:** Arts Stream
**Available at:** Sabaragamuwa University of Sri Lanka (042L)

---

## Overview

The Bachelor of Arts degree at the Sabaragamuwa University of Sri Lanka is designed to provide students with a comprehensive understanding of social sciences, humanities, and languages. In the Sri Lankan context, this degree is vital for developing critical thinkers, policy analysts, and educators who can navigate the country’s complex socio-economic landscape. The curriculum emphasizes the intersection of traditional academic disciplines with contemporary societal needs, preparing graduates to contribute effectively to both the public and private sectors.

The Faculty of Social Sciences and Languages at Sabaragamuwa University is notable for its focus on regional development and interdisciplinary studies. Located in Belihuloya, the university offers a unique environment that encourages students to engage with rural development challenges while maintaining a global perspective. Graduates are equipped with the analytical skills necessary to address issues ranging from cultural preservation to economic policy implementation within the Sri Lankan administrative and corporate frameworks.

---

## What You Will Study

**Year 1: Foundation and Core Competencies**
Students undertake foundational modules in core disciplines such as Economics, Sociology, Political Science, Geography, and Languages (Sinhala, Tamil, or English). The focus is on developing academic writing, critical thinking, and basic research methodology skills.

**Year 2: Disciplinary Depth**
Students begin to specialize in their chosen subjects. The curriculum shifts toward theoretical frameworks and applied social science. Modules cover areas such as Sri Lankan History, International Relations, Public Administration, and advanced linguistic studies.

**Year 3: Applied Knowledge and General Degree Completion**
For General Degree students, this year focuses on the practical application of knowledge through field studies and elective modules. Students engage in project-based learning that addresses local community issues, preparing them for immediate entry into the workforce.

**Year 4: Specialization and Research (Special Degree)**
Students selected for the Special Degree focus exclusively on their major subject. This year is heavily research-oriented, requiring the completion of a dissertation or an independent research project. Advanced seminars on specialized topics such as Development Studies, Human Rights, or Applied Economics are conducted to ensure mastery in the chosen field.

---

## Career Paths in Sri Lanka

- **Public Administration:** Roles as Assistant Divisional Secretaries or administrative officers in government ministries. Employers include the Ministry of Public Administration and the Sri Lanka Administrative Service (SLAS).
- **Education and Academia:** Teaching positions in the national school system or private educational institutions. Requires a Postgraduate Diploma in Education (PGDE) for permanent government teaching roles.
- **Development Sector:** Project officers or research assistants for NGOs and INGOs (e.g., UNDP, Save the Children, or local grassroots organizations) focusing on community development and social welfare.
- **Media and Communications:** Journalists, content creators, or public relations officers. Employers include major media houses like Associated Newspapers of Ceylon (Lake House) or private media networks.
- **Human Resources:** HR executives or administrative support in the corporate sector, utilizing skills in organizational behavior and labor relations.
- **Postgraduate Study:** Graduates can pursue Master’s degrees in International Relations, Development Studies, or Public Policy at institutions like the University of Colombo or the University of Peradeniya to advance into senior policy-making roles.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results. Students must have sat for the A/L examination in the Arts stream and obtained the required Z-score for the academic year. Proficiency in the medium of instruction (Sinhala or Tamil) is essential, and basic English language competency is highly recommended for academic success. Admission is highly competitive, and the Z-score threshold varies annually based on the number of applicants and university capacity.

---

## Differences Between Universities

While the Bachelor of Arts is offered across several national universities, the programme at Sabaragamuwa University is distinct due to its location in the Sabaragamuwa Province. This provides students with unique opportunities for field research in rural and plantation-sector development, which is less accessible in urban-centric universities like the University of Colombo. The faculty maintains strong links with regional government bodies, offering students practical exposure to decentralized administration and local governance that is specific to the university''s geographic advantage.

---

## Special Notes

The Bachelor of Arts degree is primarily conducted in the Sinhala or Tamil medium, depending on the student''s enrollment. Students are encouraged to enhance their English language skills through the university’s English Language Teaching Unit (ELTU), as English proficiency significantly improves employability in the private sector. Graduates often pursue professional qualifications in Human Resource Management (e.g., CIPM) or Law (via the Sri Lanka Law College) as conversion pathways to diversify their career prospects. There is no specific professional licensing body for general Arts graduates, but the degree is the standard academic requirement for entry into the Sri Lanka Administrative Service (SLAS) and the Sri Lanka Foreign Service (SLFS).', 'e68129a3fbcf719b93c834e1a095ebe7ec6ad049cbff7df2cf509790de557836');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('050', '# Health Promotion (B.Sc.)
**Course Number:** 050
**Degree:** Bachelor of Science (Honours) in Health Promotion
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** Rajarata University of Sri Lanka Faculty of Medicine and Allied Sciences (050A)

---

## Overview

Health Promotion is a public health discipline focused on enabling people and communities to improve and control their health — through education, behaviour change, policy, and environmental interventions. Rather than treating illness, Health Promotion professionals prevent it.

In Sri Lanka''s healthcare system, health promotion is a core function of the Ministry of Health, managed by the Health Promotion Bureau (HPB). With Sri Lanka facing a growing burden of non-communicable diseases (NCDs) — diabetes, heart disease, cancer, obesity — health promotion professionals have never been more needed.

Rajarata University''s programme is in the North Central province (Anuradhapura), serving an important regional population.

---

## What You Will Study

**Year 1 — Health Sciences Foundation:**
Human Anatomy and Physiology, Nutrition and Dietetics, Social Sciences for Health (Sociology, Psychology), Epidemiology basics, Biostatistics, Introduction to Public Health.

**Year 2 — Public Health and Promotion:**
Community Health Nursing principles, Health Communication and Education Methods, Behaviour Change Theory, Environmental Health, Health Psychology, Principles of Disease Prevention, Research Methods.

**Year 3 — Applied Health Promotion:**
Programme Planning and Evaluation (designing health promotion programmes), Maternal and Child Health, School Health, Occupational Health, Health Policy and Systems, Non-Communicable Disease Prevention, Field placements in community health settings.

**Year 4 — Research:**
Research Dissertation on a community health topic, Advanced Health Communication, Health Promotion in Sri Lankan Context, Digital Health Promotion (social media, mobile health).

---

## Career Paths in Sri Lanka

- **Health Promotion Bureau (HPB):** The central government agency for health promotion in Sri Lanka. Health Promotion Officers develop national campaigns (anti-tobacco, anti-alcohol, healthy eating, physical activity, mental health, dengue prevention).
- **Ministry of Health — Medical Officer of Health (MOH) offices:** Community-level public health work through the MOH system, supporting community health education and disease prevention programmes.
- **Field Health Centres and district hospitals:** Supporting community-level health education and screening programmes.
- **School health programmes:** Ministry of Education and Ministry of Health joint school health initiatives.
- **NGOs:** Local and international NGOs (Sarvodaya, Cancer Care Alliance, HIV/AIDS prevention organizations) working on public health.
- **Private healthcare:** Patient education roles in corporate hospitals and private health programmes.
- **International health organizations:** WHO Sri Lanka country office, UNICEF, UNFPA working on maternal-child health, nutrition, and NCD prevention.
- **Research:** Academic public health research at universities and research institutions.

---

## Entry Requirements

**A/L Stream:** Biological Science (mandatory)
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Health Promotion cutoffs are typically in the **0.5 to 0.9** range — one of the more accessible Biological Science programmes. Rajarata''s location (Anuradhapura) means students who prefer a quieter campus setting and regional employment will benefit from this programme.

---

## Special Notes

- Registration with the Sri Lanka Medical Council (SLMC) is required for allied health practice.
- The HPB is a well-funded, active government institution — career opportunities are real and meaningful.
- Sri Lanka''s NCD crisis (50%+ of deaths from heart disease, diabetes, cancer) makes Health Promotion a growing priority at the national policy level.
- Students interested in public health, community work, and preventive medicine (as opposed to clinical medicine) will find this degree highly rewarding.
', '168a387e0f1ef8c449d31fd5be49e9ba216ec68ce0ca294dc09be9debe8c1a44');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('051', '# Pharmacy (B.Pharm.)
**Course Number:** 051
**Degree:** Bachelor of Pharmacy (B.Pharm. Honours)
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Peradeniya Faculty of Allied Health Sciences (051A), University of Sri Jayewardenepura Faculty of Allied Health Sciences (051B)

---

## Overview

Pharmacy is one of the most respected healthcare degrees in Sri Lanka. Pharmacists are responsible for the safe and effective use of medicines — dispensing, counselling patients, managing drug information, and ensuring medication quality. The B.Pharm. degree trains students in pharmaceutical sciences, clinical pharmacy, and drug management.

Both Sri Lankan state university pharmacy programmes are accredited by the Sri Lanka Medical Council (SLMC). Pharmacists must register with the SLMC to practise.

Sri Lanka has a rapidly growing pharmaceutical manufacturing industry, a large government pharmacy service, and a busy retail pharmacy sector. All three sectors offer strong employment opportunities for pharmacy graduates.

---

## What You Will Study

The B.Pharm. curriculum integrates pharmaceutical chemistry, biology, and clinical sciences:

**Year 1 — Sciences Foundation:**
General and Organic Chemistry, Biochemistry, Human Anatomy and Physiology, Botany (medicinal plants), Mathematics and Statistics for Pharmacy, Introduction to Pharmacy Practice.

**Year 2 — Pharmaceutical Sciences:**
Pharmaceutical Chemistry (drug synthesis and structure-activity relationships), Pharmacognosy (plant-derived medicines), Pharmaceutics (formulation — tablets, capsules, liquids, injectables, topical preparations), Microbiology and Pharmaceutical Biotechnology, Pharmacology I.

**Year 3 — Applied Pharmacy:**
Pharmacology II and Toxicology, Pharmaceutical Analysis (quality control and testing methods), Pharmacokinetics (how drugs move through the body), Clinical Pharmacy, Drug Regulatory Affairs, Hospital Pharmacy Practice, Community Pharmacy Practice.

**Year 4 — Specialization and Research:**
Industrial Pharmacy, Pharmaceutical Marketing and Management, Dispensing Practice, Pharmacy Law and Ethics, Research Project / Dissertation. Extended practical placements in hospital pharmacies and community pharmacies.

---

## Career Paths in Sri Lanka

- **Government pharmacy service:** Ministry of Health employs pharmacists in government hospitals, teaching hospitals, base hospitals, and district hospitals across the country. The Medical Supplies Division manages procurement and distribution of medicines nationally.
- **Hospital pharmacy:** Consultant Pharmacists and clinical pharmacists in both government and private hospitals (Asiri, Lanka Hospitals, Nawaloka, Durdans, Apollo) — reviewing prescriptions, managing formularies, advising on drug therapy.
- **Community pharmacy (retail):** Pharmacists manage and operate community pharmacies — either government-licensed private pharmacies or chains (Osusala, Lanka Sathosa outlets, private chains). Pharmacists counsel patients and dispense medicines.
- **Pharmaceutical manufacturing industry:** Quality Assurance (QA) and Quality Control (QC) officers, Production Supervisors, Regulatory Affairs Officers at pharmaceutical companies. Sri Lanka has a growing local pharmaceutical manufacturing sector including Astron, CIC Agri Businesses, State Pharmaceuticals Corporation (SPC), and foreign company local offices.
- **Drug regulation:** Sri Lanka Drug Regulatory Authority (previously National Medicines Regulatory Authority — NMRA) and Ministry of Health regulatory divisions employ pharmacists for drug registration and quality monitoring.
- **Pharmaceutical sales and marketing:** Medical Representatives and Product Managers at multinational (GSK, Pfizer, Roche, Novartis) and local pharmaceutical companies.
- **Academic pharmacy:** Pharmacy lecturers at Peradeniya and SJP pharmacy faculties.
- **International practice:** With additional examinations (FPGEE in USA, GPhC registration in UK, KAPS in Australia), Sri Lankan pharmacy graduates can practise internationally.

---

## Entry Requirements

**A/L Stream:** Biological Science (mandatory)
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Pharmacy is competitive — typically **1.0 to 1.6** range for Peradeniya (051A) and somewhat lower for SJP (051B). Students who narrowly miss Medicine or Dental Surgery often find Pharmacy as their next preference. The national intake is around 100–150 students per year across both universities.

---

## Differences Between Universities

- **Peradeniya (051A):** Oldest pharmacy programme, well-established teaching hospital (THTK) for clinical rotations, strong research culture, Kandy campus.
- **SJP (051B):** Newer pharmacy programme, Sri Jayewardenepura General Hospital (Teaching) for clinical exposure, Nugegoda campus near Colombo.

---

## Special Notes

- Pharmacy is conducted in English at both universities.
- Sri Lanka''s pharmaceutical sector is supported by the State Pharmaceuticals Corporation (SPC) and the State Pharmaceuticals Manufacturing Corporation (SPMC) which produce essential medicines domestically — both recruit pharmacy graduates.
- The growing interest in Ayurvedic and traditional medicine in Sri Lanka creates opportunities at the intersection of pharmacy and indigenous medicine.
- Students interested in research should note that pharmaceutical research (drug discovery, formulation research) requires postgraduate study (M.Pharm., M.Sc., or PhD) for meaningful research roles.
', 'b9da5d7d325012233a35fc1d8697745f1cb0eb9e00fb19c1721ceb4c08e4a7ae');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('052', '# Medical Laboratory Sciences (B.Sc.)
**Course Number:** 052
**Degree:** Bachelor of Science (Honours) in Medical Laboratory Sciences
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Peradeniya Faculty of Allied Health Sciences (052A), University of Ruhuna Faculty of Allied Health Sciences (052B)

---

## Overview

Medical Laboratory Sciences (also called Medical Laboratory Technology or Clinical Laboratory Science) trains graduates to operate diagnostic laboratories in hospitals and clinics. Laboratory scientists perform the tests that doctors rely on — blood counts, urine analyses, microbiological cultures, histopathology, blood banking, and hundreds of other diagnostic tests that guide medical decision-making.

Hospitals cannot function without well-trained laboratory personnel. Every blood test, urine culture, cancer biopsy, or blood transfusion requires a Medical Laboratory Scientist. This makes it a profession with guaranteed and growing employment both in Sri Lanka and internationally.

---

## What You Will Study

**Year 1 — Sciences Foundation:**
Human Anatomy and Physiology, Cell Biology and Genetics, General Chemistry and Biochemistry, Microbiology Basics, Introduction to Laboratory Practice, Biostatistics.

**Year 2 — Core Laboratory Sciences:**
Haematology (study of blood and blood disorders), Clinical Biochemistry (chemical analysis of blood and body fluids), Medical Microbiology (bacteria, viruses, fungi causing disease), Histopathology and Cytology (tissue and cell analysis), Immunology and Serology (antibody and immune tests), Phlebotomy (blood collection techniques).

**Year 3 — Advanced and Applied:**
Blood Banking and Transfusion Medicine (blood group typing, cross-matching), Parasitology (malaria, dengue, intestinal parasites), Molecular Diagnostics (PCR, gene sequencing), Clinical Biochemistry Advanced (liver, kidney, cardiac enzyme panels), Point-of-Care Testing, Quality Assurance in Laboratories. Hospital practical placements begin.

**Year 4 — Research and Specialization:**
Research Project or Dissertation, advanced electives, extended hospital placement across departments. Quality Management in laboratories, Laboratory Management and Administration.

---

## Career Paths in Sri Lanka

- **Government hospital laboratories:** Teaching hospitals, district hospitals, and base hospitals maintain clinical laboratories for haematology, biochemistry, microbiology, histopathology, and blood banking. Government Medical Laboratory Technologists are civil servants with job security and pension benefits.
- **Private diagnostic laboratories:** Lanka Hospitals Diagnostics, Asiri Diagnostics, Hemas Diagnostics, Nawaloka Diagnostics, and hundreds of independent channelling labs across Sri Lanka employ laboratory scientists.
- **Blood banks:** National Blood Transfusion Service and hospital blood banks require qualified laboratory personnel for blood grouping, cross-matching, and component preparation.
- **Reference and specialized laboratories:** Colombo Medical Research Institute (MRI), National STD/AIDS Control Programme, Malaria and Dengue reference laboratories, and Sri Lanka Institute of Nanotechnology (SLINTEC) biology labs.
- **Public health laboratories:** Ministry of Health public health laboratories for outbreak investigation and disease surveillance.
- **Pharmaceutical quality control:** QC laboratories in pharmaceutical companies.
- **International opportunities:** UK (IBMS registration), Australia (AIMS), Middle East (Saudi, UAE hospital labs) all recruit Sri Lankan medical laboratory professionals.
- **Academic:** Lecturers at medical faculties and allied health sciences faculties.

---

## Entry Requirements

**A/L Stream:** Biological Science (mandatory)
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Medical Laboratory Sciences has cutoffs typically in the **0.9 to 1.4** range — accessible to most Biology stream students who do not qualify for Medicine or Dental Surgery. Ruhuna (052B) generally has lower cutoffs than Peradeniya (052A).

---

## Special Notes

- The programme is conducted in English.
- After graduation, registration with the Sri Lanka Medical Council (SLMC) is required to practise.
- Sri Lanka has a chronic shortage of qualified medical laboratory scientists, especially in provincial hospitals — employment is virtually guaranteed.
- The COVID-19 pandemic significantly raised the profile of medical laboratory scientists in Sri Lanka and globally, highlighting their critical role in disease diagnosis and public health response.
', '5c01f020baefedb659753bda06b2b210210fb2d1163fd554638f63ad8ae793d8');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('053', '# Radiography (B.Sc.)
**Course Number:** 053
**Degree:** Bachelor of Science (Honours) in Radiography and Radiotherapy
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Peradeniya Faculty of Allied Health Sciences (053A)

---

## Overview

Radiography is a healthcare profession focused on using medical imaging technologies to diagnose and treat diseases. Radiographers operate X-ray machines, CT scanners, MRI machines, ultrasound equipment, and nuclear medicine systems to produce diagnostic images. Radiotherapy Radiographers specifically operate radiation therapy equipment to treat cancer.

As medical imaging technology advances rapidly, and with Sri Lanka''s healthcare sector expanding significantly, Radiography is one of the most employment-secure health sciences careers. University of Peradeniya is the primary provider of the state university Radiography degree in Sri Lanka.

---

## What You Will Study

**Year 1 — Sciences Foundation:**
Human Anatomy and Physiology, Medical Physics (radiation physics, atomic structure, electromagnetic spectrum), Radiobiology (effects of radiation on living tissue), Biochemistry, Introduction to Diagnostic Radiography, Radiation Protection Principles.

**Year 2 — Imaging Sciences:**
Radiographic Technique (conventional X-ray — positioning, projections, exposure factors), Image Quality and Darkroom Technology, Computed Tomography (CT scanning), Fluoroscopy, Basic Ultrasound Imaging, Contrast Media and Procedures (barium studies, IVP).

**Year 3 — Advanced Imaging and Therapy:**
MRI Principles and Practice, Nuclear Medicine (radionuclide imaging, SPECT, PET scanning), Radiotherapy Physics (how radiation kills tumour cells), Radiation Treatment Planning, Mammography, Digital Radiography and PACS (digital image archiving). Clinical placements in all imaging departments of teaching hospitals.

**Year 4 — Specialization and Research:**
Advanced CT and MRI, Radiation Oncology, Interventional Radiology (image-guided procedures), Radiography Management, Research Project / Dissertation, extended hospital placements.

---

## Career Paths in Sri Lanka

- **Government hospital radiology departments:** Teaching hospitals, provincial hospitals, district hospitals — all have radiology departments employing radiographers. Government radiographers are civil servants.
- **Private hospital imaging:** Lanka Hospitals, Asiri, Nawaloka, Durdans, and growing private imaging centres with high-end MRI and CT scanners recruit qualified radiographers.
- **Cancer treatment centres:** The National Cancer Institute Maharagama and private cancer treatment centres employ Radiotherapy Radiographers as part of oncology teams.
- **Diagnostic imaging centres:** Stand-alone imaging centres (MRI, CT, ultrasound, mammography) operating in urban areas.
- **International opportunities:** UK (HCPC registration as Diagnostic Radiographer), Australia (ASMIRT registration), Middle East — all have ongoing demand for radiographers.
- **Medical equipment companies:** Clinical application specialists at companies supplying GE, Siemens, Philips, or Canon medical imaging equipment.
- **Academia:** Lecturers at allied health sciences departments.

---

## Entry Requirements

**A/L Stream:** Biological Science (mandatory)
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics (Physics is particularly relevant for the physics-heavy curriculum)

**Z-score context:** Radiography cutoffs are typically in the **0.8 to 1.3** range. Only Peradeniya offers this degree in the state system, making it a focused intake.

---

## Special Notes

- Radiation protection is a fundamental part of the curriculum — radiographers are trained to minimize radiation exposure to patients and themselves.
- The shift from film-based to digital radiology (PACS and RIS systems) is complete in most Sri Lankan hospitals — graduates are trained in fully digital environments.
- Physics is the most important A/L subject for this programme — students with strong Physics grades find the Medical Physics component more manageable.
', '3e02ab517781661eb252ce4314e2230f6ec8faa9531d93f48c48828b1913eebe');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('054', '# Physiotherapy (B.Sc.)
**Course Number:** 054
**Degree:** Bachelor of Science (Honours) in Physiotherapy
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Colombo Faculty of Allied Health Sciences (054A), University of Peradeniya Faculty of Allied Health Sciences (054B)

---

## Overview

Physiotherapy is a healthcare profession focused on restoring movement and function in people affected by injury, illness, or disability. Physiotherapists assess, diagnose, and treat conditions affecting the musculoskeletal, neurological, respiratory, and cardiovascular systems using physical methods — exercise, manual therapy, electrotherapy, and rehabilitation programmes.

The demand for physiotherapists in Sri Lanka is growing rapidly as the population ages, road traffic accidents increase, and awareness of rehabilitation medicine grows. Both government and private hospitals are expanding their physiotherapy departments. Sri Lankan physiotherapy graduates are also highly sought internationally.

---

## What You Will Study

**Year 1 — Anatomy and Sciences:**
Human Anatomy (musculoskeletal and neurological systems in detail), Physiology, Biochemistry, Kinesiology and Biomechanics (how the body moves), Introduction to Physiotherapy, Basic First Aid.

**Year 2 — Physiotherapy Sciences:**
Electrotherapy (ultrasound, TENS, laser, diathermy), Exercise Physiology, Neuroanatomy, Pathology of Musculoskeletal Conditions, Clinical Assessment and Measurement, Hydrotherapy, Introduction to Cardiorespiratory Physiotherapy.

**Year 3 — Clinical Physiotherapy:**
Musculoskeletal Physiotherapy (sports injuries, back pain, joint conditions), Neurological Physiotherapy (stroke rehabilitation, cerebral palsy, Parkinson''s disease, spinal cord injury), Cardiorespiratory Physiotherapy (post-surgical chest care, COPD management), Paediatric Physiotherapy, Community Physiotherapy. Extended clinical placements in teaching hospitals begin.

**Year 4 — Advanced and Research:**
Geriatric Physiotherapy, Occupational Rehabilitation, Sports Physiotherapy, Women''s Health Physiotherapy, Research Project / Dissertation, extended internship placement in hospital departments.

---

## Career Paths in Sri Lanka

- **Government hospital physiotherapy units:** Teaching hospitals (National Hospital Colombo, Teaching Hospital Kandy, Karapitiya, Jaffna) all have physiotherapy units. Government positions are permanent civil service roles.
- **Private hospital physiotherapy:** Asiri Hospital, Lanka Hospitals, Nawaloka, Durdans, Apollo, and the many private hospitals established across Sri Lanka all require physiotherapy services.
- **Private physiotherapy clinics:** Many physiotherapists establish independent practices, particularly in urban areas. Sports injury clinics, pain management centres, and women''s health clinics are growing markets.
- **Sports sector:** Cricket, football, rugby, athletics, and other sports associations — and professional sports teams — employ physiotherapists for athlete injury management and performance support.
- **Rehabilitation centres:** Dedicated rehabilitation centres for neurological conditions (stroke, traumatic brain injury, spinal injury) and post-surgical rehabilitation.
- **Elderly care:** A growing sector in Sri Lanka as the population ages — nursing homes, elder care facilities, and home-based physiotherapy services.
- **International careers:** UK (HCPC registration), Australia (APC), Middle East (UAE, Qatar, Saudi Arabia, Kuwait) — all with high demand for physiotherapists. Sri Lankan physiotherapists are well-regarded internationally.
- **Academia:** Physiotherapy lecturers at the Colombo and Peradeniya allied health faculties.

---

## Entry Requirements

**A/L Stream:** Biological Science (mandatory)
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Physiotherapy cutoffs are typically in the **0.8 to 1.3** range — accessible to most Biological Science students who do not enter Medicine or Dental Surgery. Colombo (054A) generally has slightly higher cutoffs than Peradeniya (054B).

---

## Special Notes

- The programme is conducted in English.
- After graduation, registration with the Sri Lanka Medical Council (SLMC) is required to practise.
- Clinical placements in teaching hospitals are a major component of the programme — students gain hands-on patient experience from Year 2 onwards.
- The profession offers excellent work-life balance compared to Medicine, while still providing meaningful clinical work and patient impact.
- Growing demand for sports physiotherapy linked to Sri Lanka''s expanding sports culture (cricket, rugby) and the popularity of fitness culture in urban areas.
', 'a24fe2a3fa3ba03f1a65a479f98ad7d3c2af6ce64ec463161405850eba113378');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('055', '# Environmental Conservation & Management
**Course Number:** 055
**Degree:** Bachelor of Science (B.Sc.) / Bachelor of Science (Honours) in Environmental Conservation and Management
**Duration:** 3 years (General) or 4 years (Honours)
**Entry Stream:** Biological Science
**Available at:** University of Kelaniya (055D)

---

## Overview

The Environmental Conservation and Management (ENCM) degree programme at the University of Kelaniya is designed to address the critical intersection of ecological preservation and national development. As Sri Lanka faces increasing challenges related to climate change, biodiversity loss, and sustainable land use, this degree provides the scientific foundation and analytical tools necessary to manage natural resources effectively. The curriculum emphasizes a multidisciplinary approach, blending biological sciences with management principles to solve real-world environmental issues.

The programme is hosted by the Department of Zoology and Environmental Management, a faculty recognized for its high-impact research, including prestigious awards from the National Science Foundation (NSF). Students benefit from the department''s strong focus on practical field applications, such as land suitability analysis and climate-resilient agricultural research, ensuring that graduates are well-prepared for the demands of both the public sector and the growing green economy in Sri Lanka.

---

## What You Will Study

**Year 1: Foundations of Environmental Science**
Focuses on core biological and chemical principles. Subjects include Principles of Ecology, Environmental Chemistry, Biodiversity of Sri Lanka, and Introduction to Environmental Management. Students gain an understanding of the physical and biological processes that govern ecosystems.

**Year 2: Applied Environmental Management**
Students delve into specialized areas such as Environmental Pollution and Control, Geographic Information Systems (GIS) and Remote Sensing, Environmental Microbiology, and Resource Economics. This year emphasizes the technical skills required to monitor and assess environmental quality.

**Year 3: Advanced Conservation Strategies**
Covers Environmental Impact Assessment (EIA), Sustainable Development, Wildlife Management, and Environmental Law and Policy. Students in the 3-year General degree track complete their coursework, while those proceeding to the 4-year Honours track begin preparing for their research specialization.

**Year 4 (Honours Only): Research and Specialization**
Dedicated to advanced research methodology and a mandatory independent research project. Students work under the guidance of senior faculty to conduct original research on topics such as climate-resilient agriculture, ecosystem restoration, or industrial waste management, culminating in a thesis.

---

## Career Paths in Sri Lanka

*   **Environmental Consultant:** Working with private firms or NGOs (e.g., IUCN, WNPS) to conduct Environmental Impact Assessments (EIA) for infrastructure and development projects.
*   **Conservation Officer:** Employed by the Department of Wildlife Conservation (DWC) or the Forest Department to manage protected areas and implement biodiversity conservation plans.
*   **Environmental Management Officer:** Working in the manufacturing or plantation sector (e.g., MAS Holdings, Dilmah Tea) to ensure corporate compliance with environmental regulations and ISO 14001 standards.
*   **Research Scientist:** Conducting field and laboratory research at institutions like the National Aquatic Resources Research and Development Agency (NARA) or the NSF.
*   **GIS/Remote Sensing Specialist:** Using spatial data to map land use changes and natural resource distribution for government planning agencies like the Urban Development Authority (UDA).
*   **Postgraduate Study:** Graduates can pursue M.Sc. or Ph.D. programmes in Environmental Science, Climate Change, or Natural Resource Management at local universities (e.g., University of Peradeniya, University of Colombo) or internationally.

---

## Entry Requirements

Admission is strictly through the Biological Science stream of the G.C.E. Advanced Level examination. Applicants must have obtained a minimum of three passes in the required subjects (Biology, Chemistry, and Physics/Agriculture). The programme is highly competitive, and selection is based on the Z-score determined by the University Grants Commission (UGC). The medium of instruction is English, and candidates are expected to have a strong command of the language for technical writing and research documentation.

---

## Differences Between Universities

This programme is currently offered exclusively at the University of Kelaniya. The department is notable for its specific focus on the integration of Zoology and Environmental Management, providing a unique biological perspective on conservation that is distinct from purely engineering-based environmental degrees. Its location in the Gampaha District allows for easy access to both urban industrial zones and diverse wetland ecosystems, facilitating frequent field-based learning.

---

## Special Notes

Graduates of this programme are well-positioned to work in roles requiring compliance with the Central Environmental Authority (CEA) regulations. While this is a science-based degree, it is highly interdisciplinary; students are encouraged to develop proficiency in data analysis software (such as R or Python) and GIS tools early in their studies to increase employability. The Honours degree is strongly recommended for students intending to pursue academic or high-level research careers, as it provides the necessary training for postgraduate research. There is significant demand for these skills in the international job market, particularly in the fields of sustainability reporting and climate change mitigation.', '333d1231d67ebff0325e90d74857e715ff9c750b82a71bee86741703df9554fa');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('056', '# Facilities Management
**Course Number:** 056
**Degree:** Bachelor of Science Honours in Facilities Management
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** University of Moratuwa (056G)

---

## Overview

Facilities Management (FM) is a multidisciplinary profession that integrates people, place, process, and technology to ensure the functionality, comfort, safety, and efficiency of the built environment. In the Sri Lankan context, as the country undergoes rapid urbanization and the development of high-rise commercial complexes, luxury hotels, and industrial zones, the demand for professionals who can manage these complex assets throughout their lifecycle has surged.

The University of Moratuwa, through its Department of Facilities Management under the Faculty of Architecture, is the pioneer in this field in Sri Lanka. The programme is notable for its unique blend of management, technology, and construction economics. It equips students to bridge the gap between technical building systems and the strategic business objectives of an organization, making graduates essential to the sustainable operation of Sri Lanka’s modern infrastructure.

---

## What You Will Study

**Year 1: Foundations of the Built Environment**
Focuses on the fundamentals of construction technology, building materials, mathematics for management, economics, and communication skills. Students are introduced to the principles of management and the professional role of a facilities manager.

**Year 2: Technical and Managerial Core**
Covers building services (HVAC, electrical, plumbing), structural systems, accounting and finance, law related to construction and property, and organizational behavior. Students begin to understand how building performance impacts business productivity.

**Year 3: Strategic Facilities Management**
Deep dives into operations and maintenance management, energy management, sustainable facilities management, procurement, and real estate management. Students engage in practical case studies and field visits to major commercial and industrial facilities.

**Year 4: Advanced Practice and Research**
Focuses on strategic management, disaster management, and advanced research methodology. The final year culminates in a comprehensive individual research dissertation and a professional practice module that prepares students for the transition into the corporate sector.

---

## Career Paths in Sri Lanka

*   **Corporate Real Estate Manager:** Managing large office portfolios for multinational corporations (e.g., John Keells Holdings, MAS Holdings, or HSBC) to ensure workspace efficiency and cost-effectiveness.
*   **Operations Manager (Hospitality/Healthcare):** Overseeing the complex technical and support services of luxury hotel chains (e.g., Cinnamon Hotels) or private hospitals (e.g., Nawaloka, Lanka Hospitals) to ensure 24/7 operational continuity.
*   **Property/Asset Manager:** Managing high-rise residential or commercial complexes (e.g., Colombo City Centre, One Galle Face) focusing on maintenance, tenant relations, and asset value preservation.
*   **Energy and Sustainability Consultant:** Working with engineering firms or consultancy bodies to audit building energy usage and implement green building practices in line with local environmental regulations.
*   **Project Manager (Fit-out/Refurbishment):** Coordinating the interior fit-out and renovation of commercial spaces, ensuring projects are delivered on time and within budget for corporate clients.
*   **Postgraduate Study:** Graduates often pursue M.Sc. or MBA programmes in Project Management, Sustainable Energy, or Business Administration at the University of Moratuwa or international universities to move into senior executive roles.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Physical Science stream. Candidates must satisfy the minimum requirements for university admission as determined by the University Grants Commission (UGC). The selection is highly competitive, requiring a high Z-score due to the limited intake and the prestige of the University of Moratuwa. The medium of instruction is English, and proficiency in the language is essential for academic success and professional practice.

---

## Differences Between Universities

This programme is exclusively offered by the University of Moratuwa. As the sole provider, the Department of Facilities Management maintains strong, centralized industry links with the International Facility Management Association (IFMA) and local industry leaders, ensuring that the curriculum remains aligned with global standards while addressing specific Sri Lankan infrastructure challenges.

---

## Special Notes

*   **Professional Recognition:** Graduates are eligible for professional membership in relevant local and international bodies, which is a significant advantage for career progression.
*   **Overseas Demand:** There is a high demand for FM professionals in the Middle East and Australia, making this a highly portable degree for those seeking international employment.
*   **Industry Exposure:** The programme includes mandatory industrial training, which is critical for networking and securing employment before graduation.
*   **Multidisciplinary Nature:** Students should be prepared to study a diverse range of subjects, from engineering-based building services to business-based accounting and law.', '8137e425a0ca46ca411ce423f2a2077803f4632bcac6e203cc2e2b65c61d7f19');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('057', '# Transport Management & Logistics Engineering
**Course Number:** 057
**Degree:** Bachelor of Science (Honours) in Transport Management & Logistics Engineering
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** University of Moratuwa (057G)

---

## Overview

The Bachelor of Science in Transport Management & Logistics Engineering (TMLE) is a specialized, multidisciplinary degree offered by the University of Moratuwa, the nation’s premier technological university. This programme sits at the intersection of engineering, management, and economics, designed to address the critical needs of Sri Lanka’s expanding infrastructure and supply chain sectors. With transport and logistics accounting for over 15% of the national GDP and employing over 1 million people, this degree is vital for the country’s economic development.

The curriculum is uniquely positioned to bridge the gap between technical engineering solutions and strategic management. Students gain a deep understanding of how to optimize the movement of goods and people across land, air, and sea. Given Sri Lanka''s strategic location in the Indian Ocean, graduates are prepared to play a pivotal role in transforming the island into a regional logistics hub, working with major local and international stakeholders.

---

## What You Will Study

**Year 1: Foundations**
Focuses on fundamental engineering mathematics, physics, and introductory modules in transport systems, economics, and management principles. Students are introduced to the basics of logistics and the regulatory frameworks governing transport in Sri Lanka.

**Year 2: Core Technical Competencies**
Deepens knowledge in transport planning, traffic engineering, supply chain management, and quantitative techniques. Modules include transport economics, operations research, and information systems for logistics.

**Year 3: Advanced Specialization**
Students engage with complex systems such as maritime logistics, aviation management, public transport planning, and advanced supply chain analytics. This year emphasizes the application of technology in logistics, including warehouse management and freight forwarding.

**Year 4: Research and Professional Practice**
The final year is dedicated to a comprehensive individual research project (dissertation) that addresses real-world industry problems. Students also complete a professional training component, ensuring they are ready to integrate into the workforce immediately upon graduation.

---

## Career Paths in Sri Lanka

*   **Logistics & Supply Chain Manager:** Working for large-scale retailers or manufacturers (e.g., MAS Holdings, Brandix) to optimize inventory and distribution networks.
*   **Port & Maritime Operations Executive:** Managing terminal operations or shipping lines at the Sri Lanka Ports Authority (SLPA) or private terminals like CICT.
*   **Aviation Management Specialist:** Working with Airport and Aviation Services (Sri Lanka) or private airlines to manage ground handling and flight operations.
*   **Transport Planner/Consultant:** Working with the Road Development Authority (RDA) or private urban planning firms to design public transport systems and traffic management solutions.
*   **Freight Forwarding & 3PL Expert:** Managing international trade logistics for global shipping and freight companies operating in the Colombo Port.
*   **Postgraduate Study:** Graduates frequently pursue M.Sc. or Ph.D. programmes in Transport Economics, Supply Chain Management, or Data Science at the University of Moratuwa or leading international universities.

---

## Entry Requirements

Admission is strictly through the University Grants Commission (UGC) based on the G.C.E. Advanced Level examination in the Physical Science stream. Candidates must have achieved the required Z-score for the academic year, which is highly competitive due to the limited intake and the prestige of the University of Moratuwa. The medium of instruction is English; therefore, proficiency in technical English is essential for academic success.

---

## Differences Between Universities

This programme is currently offered exclusively at the University of Moratuwa. As the sole provider of this specialized degree in the state university system, the Department of Transport Management & Logistics Engineering benefits from a highly concentrated pool of industry experts, strong links with the Ministry of Ports and Shipping, and a curriculum that is continuously updated to meet the demands of the global logistics market.

---

## Special Notes

The TMLE degree is a professional-oriented programme. Graduates are highly sought after by both the public and private sectors. While the degree is not a traditional "Engineering" degree in the sense of IESL chartering, it provides a unique blend of management and technical skills that are highly valued in the corporate world. Students are encouraged to seek internships during their academic breaks to build professional networks. The programme is conducted entirely in English, and students are expected to be comfortable with advanced mathematical and analytical concepts.', 'b86eb74046f09da4e5e787593da2ebacd53e6fa68d8df63c7b21057720574d56');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('058', '# Biochemistry and Molecular Biology
**Course Number:** 058
**Degree:** Bachelor of Science (Honours) in Biochemistry and Molecular Biology
**Duration:** 4 years
**Entry Stream:** Biological Science, Physical Science
**Available at:** University of Colombo (058A)

---

## Overview

Biochemistry and Molecular Biology at the University of Colombo is one of the most academically rigorous and research-oriented degrees in the Sri Lankan science stream, offered by the Department of Biochemistry and Molecular Biology within the Faculty of Science. The programme investigates the molecular mechanisms of life — how cells function, how genes are expressed, how proteins fold and interact, and how molecular-level changes lead to diseases like cancer, diabetes, and infectious conditions.

The University of Colombo''s Faculty of Science has a long tradition of producing research scientists, and Biochemistry graduates are among the most internationally mobile science graduates in Sri Lanka — many proceed to PhD programmes at world-leading institutions in the UK, Australia, USA, Japan, and Germany. Within Sri Lanka, biochemists serve in pharmaceutical manufacturing, clinical laboratory science, food technology, and public health research.

The programme benefits from the proximity of the Colombo Medical Faculty, the Medical Research Institute (MRI), and the National Institute of Health Sciences — all of which provide research collaboration and placement opportunities for students.

---

## What You Will Study

**Year 1 — Foundations:**
General Chemistry, Organic Chemistry, Cell Biology, General Physics, Mathematics, Biochemistry Fundamentals, Computer Applications for Sciences, Scientific Communication.

**Year 2 — Core Biochemistry:**
Protein Biochemistry (structure, function, enzymology), Carbohydrate and Lipid Metabolism, Nucleic Acid Biochemistry, Genetics and Gene Expression, Cell Signalling, Immunology, Microbiology for Biochemists, Biophysical Techniques, Analytical Chemistry Methods (HPLC, spectrophotometry, electrophoresis).

**Year 3 — Molecular Biology:**
Molecular Cloning and Recombinant DNA Technology, Genomics and Proteomics, Cancer Biology, Neuroscience Biochemistry, Endocrinology, Clinical Biochemistry, Drug Metabolism and Pharmacology, Molecular Diagnostics, Research Methods and Biostatistics, Industrial Training placement.

**Year 4 — Research:**
Supervised individual research project (thesis) in biochemistry, molecular biology, or a biomedical topic. Students carry out independent wet laboratory research contributing original findings. Seminars, journal clubs, and conference presentations are part of the final year.

---

## Career Paths in Sri Lanka

- **Clinical laboratory science:** Biochemists work in clinical chemistry labs at government hospitals (Colombo National Hospital, Teaching Hospitals), and private diagnostic centres (Durdans, Nawaloka, Lanka Hospitals). Roles include clinical biochemistry technologist, laboratory scientist.
- **Pharmaceutical industry:** Quality control, drug analysis, pharmacokinetics research at companies such as CPC (State Pharmaceuticals Corporation), Hemas Pharmaceuticals, and international pharma companies operating in Sri Lanka.
- **Biomedical research:** Research scientist and research associate roles at the Medical Research Institute (MRI), National Institute of Health Sciences, Faculty of Medicine research labs, and international collaborative research projects in infectious disease, cancer, and metabolic disorders.
- **Food and beverage industry:** Food safety testing, nutritional analysis, quality assurance at Prima Group, Cargills, and export food manufacturers.
- **Cosmetic and personal care industry:** Product development and safety testing at Unilever Lanka, Sunshine Holdings, and local manufacturers.
- **Teaching:** Secondary and tertiary level Biology and Chemistry teaching, after obtaining teaching qualifications.
- **Postgraduate research (primary pathway):** Most Honours graduates with strong GPAs pursue PhD programmes in Biochemistry, Molecular Biology, Genetics, Immunology, or Biomedical Science at UK (Oxford, Cambridge, Imperial, Edinburgh), Australian (Melbourne, ANU, Monash), US, or Japanese universities. Many are fully funded.

---

## Entry Requirements

**A/L Stream:** Biological Science (primary) or Physical Science
**Typical subjects:** Biology + Chemistry + Physics (Biological Science), or Combined Mathematics + Chemistry + Physics (Physical Science)
**Z-score context:** Biochemistry and Molecular Biology (058A) is competitive, attracting students who perform well in Chemistry and Biology. Z-score cutoffs are above the median for Biological Science courses but well below Medicine and Dentistry. Students with strong academic profiles who are interested in research careers (rather than clinical practice) often prefer it over the more crowded healthcare programmes.

---

## Special Notes

- This programme at Colombo is specifically titled "Biochemistry AND Molecular Biology" — it is more research-intensive and molecular-focused than some other university biochemistry programmes.
- English is the medium of instruction.
- The Department of Biochemistry and Molecular Biology has active research groups in cancer biology, tropical infectious diseases, and nutritional biochemistry, giving students early exposure to real research.
- **Students with postgraduate research aspirations** — particularly those aiming for overseas PhD fellowships — should strongly consider this degree. The department has alumni in PhD programmes at Oxford, Imperial, Melbourne, and NUS.
- Students can also access the library and computing facilities of the Colombo Medical Faculty, which is on the same campus.
- The Department also conducts research collaboration with the World Health Organization and the International Atomic Energy Agency through the Faculty of Science.
', '8392750c1e9606ca40b68179f9a5c5d4ec15429a63ff45cfbc5c7e01e905247f');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('059', '# Industrial Statistics & Mathematical Finance
**Course Number:** 059
**Degree:** Bachelor of Science (Special) in Industrial Statistics & Mathematical Finance
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** University of Colombo (059A)

---

## Overview

The Bachelor of Science in Industrial Statistics & Mathematical Finance is a specialized degree programme designed to bridge the gap between pure mathematics and the practical requirements of the modern corporate and industrial sectors. In the context of Sri Lanka’s growing financial hub and the increasing demand for data-driven decision-making in manufacturing and logistics, this degree equips students with the quantitative tools necessary to model complex systems, manage financial risk, and optimize industrial processes.

The University of Colombo, being the premier institution offering this specialized stream, provides a unique environment where students benefit from the synergy between the Department of Statistics and the Department of Mathematics. The programme is highly regarded by the local banking, insurance, and manufacturing sectors, as it produces graduates who are not just theorists, but professionals capable of applying statistical software and mathematical modeling to real-world business challenges.

---

## What You Will Study

**Year 1:** Foundational studies in Pure Mathematics, Applied Mathematics, and introductory Statistics. Students begin their core stream by covering Calculus, Linear Algebra, and the fundamentals of Probability and Statistical Inference.

**Year 2:** Deepening of core subjects. Students focus on Industrial Statistics (Quality Control, Experimental Design), Financial Mathematics (Interest Theory, Financial Markets), and Management Science (Linear Programming, Operations Research). Computer Science is typically offered as an additional fourth subject to enhance programming skills.

**Year 3:** Advanced specialization. The curriculum shifts toward Stochastic Processes, Time Series Analysis, Portfolio Theory, and Advanced Statistical Modeling. Students engage in practical laboratory sessions using industry-standard software such as R, Python, and SAS.

**Year 4:** Focus on research and professional application. Students undertake a compulsory Industrial Training/Internship in a corporate environment and complete a Final Year Research Project. Advanced modules include Financial Derivatives, Risk Management, and Multivariate Data Analysis.

---

## Career Paths in Sri Lanka

*   **Financial Analyst:** Working with institutions like the Central Bank of Sri Lanka, commercial banks (e.g., Sampath Bank, HNB), or investment firms to analyze market trends and manage asset portfolios.
*   **Actuarial Associate:** Employed by insurance giants like AIA, Ceylinco, or Janashakthi to calculate premiums, assess risks, and ensure the financial stability of insurance products.
*   **Data Scientist/Business Analyst:** Working in the tech and retail sectors (e.g., John Keells Holdings, MAS Holdings) to optimize supply chains, predict consumer behavior, and improve operational efficiency.
*   **Quality Assurance Consultant:** Providing statistical process control expertise to manufacturing firms in the BOI zones to ensure product standards and minimize waste.
*   **Risk Manager:** Assessing credit and market risks for financial institutions, ensuring compliance with Basel III and other regulatory frameworks.
*   **Postgraduate Study:** Graduates are well-positioned for M.Sc. or Ph.D. programmes in Financial Engineering, Data Science, or Statistics at local universities or prestigious international institutions abroad.

---

## Entry Requirements

Admission is strictly through the University Grants Commission (UGC) based on the G.C.E. Advanced Level examination. Applicants must be from the Physical Science stream. Required subjects include Combined Mathematics and any two subjects from Physics, Chemistry, or Higher Mathematics. The selection is highly competitive, and students must achieve a high Z-score to qualify for the Physical Science intake at the University of Colombo. The medium of instruction is English.

---

## Differences Between Universities

This programme is uniquely offered as a specialized stream at the University of Colombo. Unlike general B.Sc. degrees, this programme is structured as a dedicated path from the outset of the undergraduate journey, ensuring that students receive focused training in the intersection of finance and statistics. Its location in Colombo provides unmatched proximity to the country''s financial district, facilitating easier access to internships and industry networking events compared to regional universities.

---

## Special Notes

*   **Professional Recognition:** Graduates are often eligible for exemptions in professional examinations such as the Chartered Institute of Management Accountants (CIMA) or the Institute of Chartered Accountants of Sri Lanka (ICASL), depending on the modules completed.
*   **Industry Demand:** There is a significant demand for these graduates in the "FinTech" sector, which is rapidly expanding in Sri Lanka.
*   **Skill Set:** Students are strongly encouraged to develop proficiency in programming languages (R, Python, SQL) early in their degree, as these are essential for the modern job market.
*   **Conversion:** This degree serves as a strong foundation for those wishing to pivot into specialized fields like Econometrics or Quantitative Finance at the postgraduate level.', '21a659ba6aacb7d171d5cb60db99d90779e5f44a133fb13877287b4b3e48713d');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('060', '# Statistics & Operations Research
**Course Number:** 060
**Degree:** Bachelor of Science (Honours) in Statistics & Operations Research
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** University of Peradeniya (060B)

---

## Overview

The Bachelor of Science (Honours) in Statistics & Operations Research is a specialized degree designed to equip students with the mathematical and analytical tools necessary to solve complex decision-making problems. In the context of Sri Lanka’s rapidly digitizing economy, this degree is vital for industries that rely on data-driven strategies, such as logistics, finance, manufacturing, and public policy.

The University of Peradeniya is uniquely positioned to offer this programme, leveraging its strong tradition in mathematical sciences. The curriculum bridges the gap between theoretical statistics and practical optimization, ensuring graduates can address real-world challenges like supply chain efficiency, risk assessment, and resource allocation within the Sri Lankan corporate and government sectors.

---

## What You Will Study

**Year 1: Foundation**
Focuses on core mathematical principles, including Calculus, Linear Algebra, and introductory Probability and Statistics. Students also gain foundational knowledge in Computer Programming (typically Python or R) to support computational work.

**Year 2: Core Theory**
Deepens knowledge in Statistical Inference, Regression Analysis, and Deterministic Operations Research. Students explore Linear Programming, Simplex methods, and the mathematical foundations of optimization.

**Year 3: Advanced Applications**
Covers Stochastic Processes, Time Series Analysis, Multivariate Statistics, and Advanced Operations Research (e.g., Integer Programming, Network Analysis). Students begin applying these tools to business and industrial case studies.

**Year 4: Specialization and Research**
Focuses on elective modules such as Data Mining, Financial Mathematics, or Quality Control. The year culminates in a compulsory Final Year Research Project, where students apply statistical modeling or optimization techniques to a specific industry or academic problem.

---

## Career Paths in Sri Lanka

*   **Data Scientist/Analyst:** Working with firms like Dialog Axiata, MAS Holdings, or John Keells Holdings to interpret large datasets and drive business intelligence.
*   **Operations Research Analyst:** Employed by logistics companies (e.g., Hayleys Advantis) or manufacturing plants to optimize supply chains, inventory management, and production scheduling.
*   **Financial Risk Analyst:** Working in the banking sector (e.g., Commercial Bank, Sampath Bank) to model market risks, credit scoring, and investment portfolios.
*   **Statistical Consultant:** Providing expertise to government departments (e.g., Department of Census and Statistics) or NGOs for survey design, demographic analysis, and policy evaluation.
*   **Quality Assurance Specialist:** Working in the apparel or FMCG sector to implement statistical process control (SPC) to maintain high production standards.
*   **Postgraduate Study:** Graduates are well-prepared for M.Sc. or Ph.D. programmes in Operations Research, Data Science, or Financial Mathematics at institutions like the University of Moratuwa or overseas universities.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Physical Science stream. Candidates must have obtained passes in Combined Mathematics, Physics, and Chemistry. Proficiency in English is essential as the medium of instruction is English. The Z-score requirement is highly competitive, reflecting the rigorous nature of the programme and the limited intake capacity of the Faculty of Science at the University of Peradeniya.

---

## Differences Between Universities

This programme is currently offered exclusively at the University of Peradeniya. Its location in the Kandy district provides a unique academic environment, and the department maintains strong links with the Operations Research Society of Sri Lanka, providing students with networking opportunities and exposure to professional industry standards that are distinct from general science degrees offered elsewhere.

---

## Special Notes

Graduates of this programme are highly sought after for their ability to handle both "big data" and "optimization" problems. While there is no direct professional licensing body like the SLMC for this degree, graduates often pursue professional certifications in Data Science or Business Analytics to enhance their employability. The degree provides a strong foundation for those looking to migrate, as the skills in Statistics and Operations Research are globally standardized and in high demand in international markets. Students are encouraged to participate in internships during their final two years to gain practical exposure to the Sri Lankan industrial landscape.', '08c55982f925f50f12acd6c3c21a7defcd80011c8d93ebfde5c969a5b01fba12');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('062', '# Fisheries and Marine Sciences (B.Sc.)
**Course Number:** 062
**Degree:** Bachelor of Science (Honours) in Fisheries and Marine Sciences
**Duration:** 4 years
**Entry Stream:** Biological Science, Biosystems Technology
**Available at:** University of Ruhuna Faculty of Fisheries and Marine Sciences and Technology (062A)

---

## Overview

Sri Lanka is an island nation with a 1,340 km coastline and rich maritime resources. The fisheries sector contributes approximately 2% of GDP, provides livelihoods to over 500,000 fishers and fishing community members, and is a major source of protein in Sri Lankan diets. The Faculty of Fisheries and Marine Sciences and Technology at the University of Ruhuna — located in Matara in the South — is the dedicated state university centre for fisheries and marine science education.

This degree covers fisheries biology, aquaculture, ocean science, marine ecology, and fish processing technology — preparing graduates for careers in the fisheries industry, government fisheries service, marine research, and environmental conservation.

---

## What You Will Study

**Year 1 — Marine Sciences Foundation:**
Marine Biology, Oceanography, Aquatic Chemistry, Marine Ecology, Fisheries Biology, Statistics, Research Methods, Computing.

**Year 2 — Core Fisheries and Aquaculture:**
Aquaculture Systems (freshwater fish farming — tilapia, catfish, ornamental fish; brackish water farming — shrimp, crab; marine sea-cage aquaculture), Fish Biology and Taxonomy, Limnology (freshwater ecology), Fishing Gear and Technology, Post-Harvest Fish Technology (chilling, freezing, smoking, drying), Fish Inspection and Quality Control.

**Year 3 — Applied Marine Sciences:**
Tropical Fisheries Management (sustainable fishing, stock assessment, quota management), Marine Pollution and Environmental Impact Assessment, Fisheries Economics and Marketing, Marine Biotechnology, Hatchery Management, International Fisheries Law and Policy. Field work at marine research stations and inland reservoirs.

**Year 4 — Research:**
Research Dissertation on marine or fisheries topic, Advanced Marine Biology, Fisheries Governance, Coastal Zone Management, Thesis presentation.

---

## Career Paths in Sri Lanka

- **National Aquatic Resources Research and Development Agency (NARA):** The government''s primary marine research institution. NARA recruits science graduates for fisheries stock assessments, marine pollution monitoring, aquaculture research, and oceanic surveys.
- **Department of Fisheries and Aquatic Resources (DFAR):** District-level Fisheries Officers who provide technical advice to fishing communities, manage inland reservoir fisheries, enforce fishery regulations.
- **Fisheries harbour management:** Fisheries Harbour Corporation manages major fishing harbours (Negombo, Peliyagoda, Beruwala, Mirissa, Tangalle, Trincomalee, Jaffna).
- **Aquaculture sector:** Fish farms, shrimp hatcheries, ornamental fish exporters — a growing private sector.
- **Fish processing and export:** Sri Lanka exports tuna, seer fish, prawns, and other marine products. Quality control officers, plant managers at fish processing plants.
- **Environmental consulting:** Coastal zone environmental impact assessments for development projects.
- **Diving and marine tourism:** Growing marine tourism sector (whale watching, diving, reef conservation).
- **International organizations:** FAO, UNDP marine programme, IUCN, WWF — working on fisheries sustainability and marine conservation.
- **Academic and research:** M.Sc., PhD in Marine Sciences — locally at Ruhuna or overseas (Australia, Japan, UK, Norway — major marine science nations).

---

## Entry Requirements

**A/L Stream:** Biological Science (primary); Biosystems Technology stream students may also be eligible
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Fisheries and Marine Sciences cutoffs are typically in the **0.5 to 1.0** range — accessible to most Biological Science students, with Ruhuna (062A) being the only state university provider.

---

## Special Notes

- Ruhuna''s southern campus location gives students direct access to the Indian Ocean, southern fishing harbours, and marine ecosystems for fieldwork.
- Sri Lanka''s 2004 tsunami significantly damaged the fishing sector — rebuild and resilience programmes have increased government investment in fisheries institutions.
- Freshwater fisheries (reservoirs, rivers) are equally important to coastal fisheries in Sri Lanka''s food security — and are a major focus of the curriculum.
- Students who enjoy outdoor, field-based work and the marine environment will find this degree highly rewarding.
', '8fac59425abb23acb7fd982c27d1284f06ff5f7dfc99fdb2b5fdfb9750a5cb83');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('063', '# Islamic Studies
**Course Number:** 063
**Degree:** Bachelor of Arts (Honours) in Islamic Studies
**Duration:** 4 years
**Entry Stream:** Arts, Biological Science (entry requirements are flexible)
**Available at:** South Eastern University of Sri Lanka (063J)

---

## Overview

Islamic Studies at the South Eastern University of Sri Lanka (SEUSL) is offered through the Faculty of Islamic Studies and Arabic Language at the main campus in Oluvil, Ampara District. SEUSL is a national university established specifically to serve the Eastern Province and Sri Lanka''s Muslim community, and it is the primary institution offering Islamic Studies as a state university degree in Sri Lanka.

The programme provides a rigorous academic study of Islam — encompassing theology (aqeedah), Islamic jurisprudence (fiqh), Quranic sciences, Hadith studies, Islamic history and civilization, comparative religion, and the sociology of Muslim communities. It is designed for students who wish to pursue careers as Islamic scholars, educators, religious counsellors, officials in Muslim affairs, or researchers in Islamic civilization.

SEUSL''s Oluvil campus serves a predominantly Muslim student population and provides a unique academic environment where Islamic scholarship intersects with modern social science and language education. The Faculty of Islamic Studies and Arabic Language also offers Arabic language training, which is highly valued for employment in the Middle East.

---

## What You Will Study

**Year 1 — Islamic Foundations:**
Quran and Tajweed, Fundamentals of Aqeedah (Islamic theology), Fiqh (Islamic jurisprudence) — worship and transactions, Islamic History (Prophet''s era and early caliphate), Arabic Language (elementary), Introduction to Hadith Sciences, Seerah (Biography of the Prophet).

**Year 2 — Jurisprudence and Sciences:**
Advanced Fiqh (family law, inheritance, commercial transactions), Usul al-Fiqh (principles of Islamic law), Tafseer (Quranic exegesis), Hadith criticism and methodology, Islamic civilization and intellectual history, Comparative Religion, Arabic Language (intermediate), Research Methods.

**Year 3 — Specialized Studies:**
Islamic Philosophy and Sufism, Contemporary Issues in Islamic Jurisprudence (bioethics, finance, technology), Muslim Personal Law in Sri Lanka, Islamic Economics and Finance, Muslim Family and Society, Modern Islamic Movements, Arabic Literature, Field Research in Muslim Communities.

**Year 4 — Research:**
Honours dissertation on an Islamic studies topic (jurisprudence, history, sociology of Islam, or contemporary Muslim affairs in Sri Lanka). Seminars and academic presentations. Electives from Islamic finance, Islamic education, or interfaith dialogue.

---

## Career Paths in Sri Lanka

- **Islamic education:** Teaching Islamics and Arabic in government schools (where Islamic Studies is a recognized subject in Muslim schools), and in private Islamic educational institutions (madrasas, Islamic colleges).
- **Religious leadership:** Serving as an Imam or religious counsellor in mosques, Islamic centres, or community organizations — though formal Imam roles also require traditional Islamic education (alim qualifications).
- **Qadi and Muslim Personal Law:** Assisting Quazis (Qadis) and Muslim Personal Law courts — Islamic Studies graduates are eligible to work in the administrative support structure of the Muslim Personal Law system.
- **Waqf Board and Muslim Affairs:** Government Department of Muslim Religious and Cultural Affairs — management of waqf properties, hajj coordination, Islamic fund administration.
- **NGOs and development:** Muslim relief organizations, Islamic charity funds (Zakat funds), and development NGOs working in Muslim communities.
- **Media and journalism:** Islamic broadcasting at Sri Lanka Broadcasting Corporation (SLBC), Muslim-focused publications, online media platforms.
- **Overseas (Middle East):** Arabic language proficiency gained through this degree opens significant employment opportunities in the UAE, Saudi Arabia, Qatar, and Kuwait in Islamic education, translation, and administration.
- **Postgraduate study:** MA or PhD in Islamic Studies, Arabic Language, Muslim Law, or Comparative Religion at Kelaniya, Sri Lanka International Islamic University, or overseas institutions (Egypt''s Al-Azhar, Malaysia, UK).

---

## Entry Requirements

**A/L Stream:** Arts stream (primary). Students who have studied Arabic, Islamic Civilization, or related subjects at A/L have a strong advantage. Some B.Sc. stream students are also considered for management-related specializations.
**Typical subjects:** Varies — Islamic Civilization, Arabic, Sinhala/Tamil, History, Logic are common A/L subjects for this pathway.
**Z-score context:** Islamic Studies (063J) at SEUSL serves a specific regional and community purpose. Z-score cutoffs reflect the intake size and the applicant pool, which is predominantly from the Eastern and Northern provinces'' Muslim community. It is generally accessible to students from the Eastern Province with reasonable A/L results.

---

## Special Notes

- SEUSL is located in **Oluvil, Ampara** — a coastal town in the Eastern Province. The campus is predominantly residential and serves the Muslim communities of the Eastern Province.
- **Muslim Personal Law:** Sri Lanka has its own Muslim Personal Law (Marriage and Divorce Act) system where Islamic jurisprudence intersects with civil law. Islamic Studies graduates are uniquely positioned to work within this system.
- Arabic language proficiency acquired through this programme is a significant asset for Middle East employment, where Sri Lankan Muslims are a well-established migrant worker community.
- The degree is recognized by the Sri Lanka Universities Grants Commission (UGC) as equivalent to other state university BA (Hons) degrees.
- Students interested in Islamic finance (banking without interest) have growing opportunities in Sri Lanka as Amana Bank and other Islamic finance products expand in the country.
- The Faculty also runs Diploma programmes in Arabic Language for part-time students.
', '6f414d0e4a0d17e919330a143569bfd44a6b5668dea2ea55f49d7ee44dc6781f');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('064', '# Science and Technology
**Course Number:** 064
**Degree:** Bachelor of Science (Honours) in Science and Technology
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** Uva Wellassa University of Sri Lanka (064U)

---

## Overview

The Bachelor of Science (Honours) in Science and Technology is a specialized degree programme designed to bridge the gap between fundamental scientific principles and their practical industrial applications. Unlike traditional pure science degrees, this programme focuses on the "value addition" of national resources, equipping students with the technical expertise required to transform raw materials into high-value products. It is uniquely positioned to address the needs of Sri Lanka’s emerging industrial sectors, including food processing, mineral technology, and polymer science.

Uva Wellassa University (UWU) is distinguished by its "Entrepreneurial University" philosophy. The Faculty of Applied Sciences emphasizes hands-on training, industrial exposure, and the development of soft skills, ensuring that graduates are not merely job seekers but potential innovators. The programme is highly relevant to the local context, particularly in the Uva Province and beyond, where there is a growing demand for professionals who can integrate scientific research with sustainable industrial practices.

---

## What You Will Study

**Year 1: Foundation in Basic Sciences**
Focuses on core scientific principles including Mathematics, Physics, Chemistry, and Biology. Students are introduced to the fundamentals of computer literacy, communication skills, and the philosophy of technology.

**Year 2: Core Technological Disciplines**
Introduction to specialized modules such as Material Science, Industrial Chemistry, Thermodynamics, and Instrumentation. Students begin to explore the intersection of science and engineering, focusing on process control and laboratory techniques.

**Year 3: Advanced Specialization and Industrial Application**
Students delve into advanced topics including Polymer Technology, Food Science and Technology, Mineral Processing, and Quality Assurance. This year emphasizes the application of scientific knowledge to industrial problem-solving and sustainable manufacturing.

**Year 4: Research and Professional Development**
The final year is dedicated to a comprehensive Industrial Training programme (internship) and an Independent Research Project. Students conduct original research relevant to national industrial needs, followed by a dissertation and oral defense.

---

## Career Paths in Sri Lanka

*   **Quality Assurance (QA) Executive:** Working in manufacturing firms like Nestlé Lanka or Ceylon Biscuits Limited (CBL) to ensure products meet safety and quality standards.
*   **Production/Process Engineer:** Managing production lines in industries such as rubber, plastics, or mineral processing (e.g., Laugfs Holdings or industrial zones in Biyagama/Katunayake).
*   **Research and Development (R&D) Scientist:** Working with state institutions like the Industrial Technology Institute (ITI) or private sector labs to innovate new product formulations.
*   **Technical Consultant:** Providing expertise to SMEs on resource optimization and value-added manufacturing processes.
*   **Environmental/Sustainability Officer:** Managing waste treatment and sustainable resource usage in large-scale industrial plants.
*   **Postgraduate Study:** Graduates can pursue M.Sc. or Ph.D. programmes in Material Science, Food Science, or Industrial Management at universities like the University of Peradeniya or the University of Moratuwa.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Physical Science stream. Candidates must have obtained passes in Physics, Chemistry, and Combined Mathematics. The programme is highly competitive, and selection is based on the Z-score determined by the University Grants Commission (UGC). The medium of instruction is English; therefore, proficiency in technical English is essential for academic success. No specific physical requirements are mandated, but students should be prepared for laboratory and field-based work.

---

## Differences Between Universities

This programme is exclusively offered by the Uva Wellassa University of Sri Lanka (064U). Its uniqueness lies in its specific focus on "value addition" to national resources, a curriculum that is distinct from the more theoretical BSc degrees offered by traditional universities like the University of Colombo or the University of Peradeniya. The UWU campus environment is specifically designed to foster an entrepreneurial mindset, with strong emphasis on industrial training and mandatory research components that are integrated into the four-year degree structure.

---

## Special Notes

The degree is offered at SLQF Level 6, which is equivalent to a four-year Honours degree. Graduates are eligible to apply for professional memberships in relevant scientific bodies, such as the Institute of Chemistry Ceylon (IChemC) or the Institute of Physics, Sri Lanka (IPSL), depending on the specific modules completed. There is significant demand for these graduates in the export-oriented manufacturing sector in Sri Lanka. Students are encouraged to maintain a high GPA throughout the four years, as this is a primary criterion for securing high-quality industrial training placements in leading multinational corporations.', '113a0a26b35f089d0d513b62368a163bddcc41b9c035797a1d142c01589f5675');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('065', '# Computer Science & Technology
**Course Number:** 065
**Degree:** Bachelor of Science (Honours) in Computer Science and Technology
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** Uva Wellassa University of Sri Lanka (065U)

---

## Overview

The Bachelor of Science (Honours) in Computer Science and Technology is a specialized four-year degree programme designed to bridge the gap between theoretical computer science and practical industrial application. In the context of Sri Lanka’s rapidly expanding ICT sector—which serves as a primary export service—this degree focuses on producing "technopreneurs" and software engineers who are capable of not just maintaining systems, but innovating within them.

Uva Wellassa University (UWU) is notable for its unique "Value Addition" philosophy. Unlike traditional computer science degrees that focus purely on coding, this programme integrates scientific principles with technological management. Located in Badulla, the faculty emphasizes a hands-on approach, ensuring that graduates are well-versed in the latest industry standards, including IEEE and ACME guidelines, making them highly competitive for roles in Colombo-based tech hubs and international remote-work markets.

---

## What You Will Study

**Year 1: Foundations**
Focuses on core mathematical and scientific principles. Subjects include Programming Fundamentals (C/C++), Mathematics for Computing, Computer Systems Architecture, and Introduction to Information Technology.

**Year 2: Core Computing**
Deepens technical proficiency. Subjects include Data Structures and Algorithms, Object-Oriented Programming (Java/Python), Database Management Systems, Operating Systems, and Computer Networks.

**Year 3: Advanced Specialization**
Students engage with complex domains. Subjects include Software Engineering, Web and Mobile Application Development, Artificial Intelligence, and Information Security. Students often begin selecting elective modules based on industry trends.

**Year 4: Research and Professional Practice**
The final year is dedicated to the Industrial Training (internship) programme and the Final Year Research Project. Students apply their knowledge to solve real-world problems, often in collaboration with industry partners, culminating in a thesis or a functional software product.

---

## Career Paths in Sri Lanka

- **Software Engineer:** Working at major Sri Lankan firms like WSO2, 99x, or IFS. Involves designing, coding, and testing software applications.
- **Systems Administrator/Network Engineer:** Managing infrastructure for large organizations like Dialog Axiata or SLT-Mobitel. Involves maintaining server uptime and network security.
- **Data Analyst/Scientist:** Working with financial institutions or retail giants like John Keells Holdings to interpret business data and drive decision-making.
- **IT Consultant/Entrepreneur:** Leveraging the "Value Addition" focus of UWU to start independent tech ventures or provide consultancy for SMEs.
- **Quality Assurance (QA) Engineer:** Ensuring software reliability for global clients in the BPO/KPO sector.
- **Postgraduate Study:** Graduates can pursue M.Sc. or Ph.D. programmes in Computer Science, AI, or Data Science at local universities (UCSC, Moratuwa) or pursue international scholarships in the US, Australia, or Europe.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results under the Physical Science stream. Candidates must have obtained passes in Combined Mathematics, Physics, and Chemistry. Proficiency in English is essential as the medium of instruction is English. The Z-score requirement is highly competitive, reflecting the high demand for IT-related degrees in the national university system. Applicants must also meet the general university admission criteria set by the University Grants Commission (UGC).

---

## Differences Between Universities

The Computer Science and Technology degree at Uva Wellassa University is distinct due to its specific focus on "Value Addition" and the integration of industrial information technology. While other state universities like the University of Colombo (UCSC) or the University of Moratuwa offer more traditional Computer Science or Engineering-based degrees, the UWU programme is specifically structured to produce graduates who understand the business and technological management side of IT, making them particularly effective in project management and industrial application roles.

---

## Special Notes

- **Professional Recognition:** The curriculum is designed to align with IEEE and ACME international standards, facilitating easier recognition for overseas employment and postgraduate admissions.
- **Industrial Training:** The programme includes a mandatory industrial training component, which is critical for securing employment immediately after graduation.
- **Medium of Instruction:** All lectures, laboratory work, and examinations are conducted in English.
- **Career Versatility:** Because of the broad curriculum, graduates are well-positioned for both technical roles (coding) and management roles (IT project coordination).', '8a3cc063f18d43ad93459d58fde98804b7d410b5fbe22acb196ffc7f74f5b2bb');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('066', '# Entrepreneurship and Management
**Course Number:** 066
**Degree:** Bachelor of Business Management (Honours) in Entrepreneurship and Management
**Duration:** 4 years
**Entry Stream:** Commerce Stream
**Available at:** Uva Wellassa University of Sri Lanka (066U)

---

## Overview

The Bachelor of Business Management (Honours) in Entrepreneurship and Management is a specialized degree designed to cultivate a new generation of business leaders capable of navigating the dynamic Sri Lankan economic landscape. Unlike traditional management degrees, this programme focuses on the intersection of innovative venture creation, strategic management, and the application of modern technologies to solve complex business problems. It is uniquely positioned to address the needs of the national economy by fostering an entrepreneurial mindset that is essential for both startups and the transformation of established local enterprises.

Uva Wellassa University (UWU) is notable for its value-addition approach to education, emphasizing practical application over theoretical rote learning. The Faculty of Management maintains strong industry ties, including partnerships with professional bodies like the Sri Lanka Institute of Marketing (SLIM). This ensures that students are not only academically grounded but also exposed to the realities of the Sri Lankan corporate sector, ranging from the plantation and tourism industries in the Uva Province to the broader national financial and service sectors.

---

## What You Will Study

**Year 1: Foundations of Business**
Focuses on core business principles including Principles of Management, Micro and Macro Economics, Business Mathematics, Accounting, and Business Communication. Students are introduced to the fundamental concepts of entrepreneurship and the legal environment of business in Sri Lanka.

**Year 2: Functional Management and Technology**
Students delve into Marketing Management, Financial Management, Human Resource Management, and Business Law. A significant emphasis is placed on Management Technologies, focusing on how digital tools and data analytics drive modern business efficiency.

**Year 3: Specialization Tracks**
Students choose between two specialized streams:
*   **Entrepreneurship and Management Technologies:** Focuses on venture creation, innovation management, business process re-engineering, and the application of technology in scaling small and medium enterprises (SMEs).
*   **Insurance and Actuary:** Focuses on risk management, actuarial science fundamentals, insurance law, and financial modeling, preparing students for the specialized financial services sector.

**Year 4: Advanced Application and Research**
The final year focuses on Strategic Management, Business Ethics, and Entrepreneurial Finance. Students must complete a comprehensive Independent Research Project or a Business Plan development, often involving field research with local industries, to demonstrate their ability to apply academic knowledge to real-world business challenges.

---

## Career Paths in Sri Lanka

*   **Entrepreneur/Founder:** Establishing and scaling new ventures in sectors like agriculture, tourism, or tech. Supported by incubators like the Ceylon Chamber of Commerce or various provincial SME development boards.
*   **Business Development Manager:** Working for established firms (e.g., John Keells Holdings, Hayleys) to identify new market opportunities and drive corporate growth.
*   **Insurance Underwriter/Risk Analyst:** Working with major insurance providers like Ceylinco Insurance or AIA Insurance, assessing risk profiles and managing actuarial data.
*   **Management Consultant:** Providing strategic advice to SMEs and startups on operational efficiency, digital transformation, and market expansion.
*   **Project Manager:** Overseeing business projects within NGOs, government development agencies, or private sector firms, ensuring objectives are met within budget and timelines.
*   **Postgraduate Study:** Graduates can pursue an MBA, M.Sc. in Management, or specialized professional qualifications (e.g., CIMA, CIM, or SLIM) to advance into senior executive roles.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results. Students must have sat for the examination in the **Commerce Stream**. The selection is highly competitive and is based on the Z-score system determined by the University Grants Commission (UGC). Proficiency in English is essential, as the medium of instruction is English, and students are expected to engage with international business literature and case studies.

---

## Differences Between Universities

This programme is exclusively offered at the Uva Wellassa University of Sri Lanka (066U). Its unique advantage lies in its location in Badulla, which provides students with a living laboratory for rural entrepreneurship, agribusiness, and tourism management. The faculty is smaller and more focused than those in larger metropolitan universities, allowing for closer mentorship between academic staff and students. The inclusion of the "Insurance and Actuary" specialization makes this programme distinct from general management degrees offered elsewhere in the country.

---

## Special Notes

The programme is designed to align with the requirements of the Sri Lanka Qualifications Framework (SLQF) at Level 6. Graduates are well-positioned to seek exemptions from various professional accounting and marketing bodies, though students should verify specific module exemptions with institutions like CIMA or SLIM upon enrollment. The degree is highly regarded for those looking to work in the SME sector or the financial services industry. Given the global demand for entrepreneurial skills, graduates are also well-prepared for international postgraduate opportunities or remote work in global business development roles.', '0b8d87f7d4cfc444d5f7dd136ec720b5da8bc5ec83b7a413a355bafdabd13503');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('067', '# Animal Production and Food Technology
**Course Number:** 067
**Degree:** Bachelor of Science (Honours) in Animal Production and Food Technology
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** Uva Wellassa University of Sri Lanka (067U)

---

## Overview

The Bachelor of Science in Animal Production and Food Technology is a specialized degree program designed to bridge the gap between livestock management and the value-added food processing industry. In the Sri Lankan context, where the livestock sector is a vital component of rural livelihoods and national food security, this degree provides the technical expertise required to modernize animal husbandry practices and enhance the quality of animal-based food products.

Uva Wellassa University (UWU) is uniquely positioned to offer this program due to its focus on value addition and entrepreneurship. Located in Badulla, the university leverages its proximity to the Uva Province’s agricultural landscape, allowing students to engage with local dairy, poultry, and meat processing industries. The curriculum is specifically tailored to meet the demands of the Sri Lankan food industry, focusing on sustainable production, hygiene standards, and the technological transformation of raw animal products into marketable goods.

---

## What You Will Study

**Year 1: Foundation in Biological and Basic Sciences**
Focuses on core sciences including Animal Anatomy and Physiology, Biochemistry, Microbiology, and Agricultural Economics. Students are introduced to the basics of livestock production systems and the principles of food chemistry.

**Year 2: Production Systems and Processing Technology**
Covers specialized modules such as Dairy Science, Poultry Production, Meat Science, and Animal Nutrition. Students begin learning the technical aspects of food processing, including food preservation, hygiene, and quality control protocols.

**Year 3: Advanced Technology and Management**
Focuses on Food Engineering, Biotechnology in Animal Production, Farm Management, and Food Safety Management Systems (HACCP/ISO). Students engage in practical laboratory sessions and field visits to commercial farms and processing plants.

**Year 4: Research and Industrial Application**
The final year is dedicated to an Industrial Training program (internship) where students gain hands-on experience in the industry. Students also complete a mandatory Independent Research Project (Dissertation) focusing on current challenges in animal production or food technology, often in collaboration with local industry partners.

---

## Career Paths in Sri Lanka

*   **Livestock Production Manager:** Overseeing large-scale poultry or dairy farms; employers include Cargills Agri Foods, NLDB (National Livestock Development Board), and private commercial farms.
*   **Quality Assurance (QA) Executive:** Ensuring food safety and hygiene standards in processing plants; employers include Ceylon Cold Stores (Elephant House), Fonterra Brands Lanka, and Richlife Dairies.
*   **Food Technologist:** Developing new products and improving processing methods; employers include major FMCG companies and local food manufacturing startups.
*   **Extension Officer/Technical Consultant:** Providing technical guidance to rural farmers; employers include the Department of Animal Production and Health (DAPH) and various NGOs working in rural development.
*   **Entrepreneur:** Establishing independent ventures in value-added meat or dairy processing, leveraging the entrepreneurial training provided by UWU.
*   **Postgraduate Research:** Pursuing M.Sc. or Ph.D. programs in Animal Science, Food Science, or Biotechnology at universities like the University of Peradeniya or overseas institutions.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Biological Science stream. Candidates must have obtained passes in Biology, Chemistry, and Physics (or a third approved science subject). The program is highly competitive, and selection is based on the Z-score determined by the University Grants Commission (UGC). The medium of instruction is English, and students are expected to have a strong command of the language for technical writing and research.

---

## Differences Between Universities

This program is currently offered exclusively at Uva Wellassa University of Sri Lanka. Unlike traditional agriculture faculties, the UWU curriculum is distinctively "value-addition" oriented. The faculty maintains strong industry links within the Uva Province and emphasizes the integration of entrepreneurial skills alongside technical knowledge, preparing graduates to be job creators rather than just job seekers.

---

## Special Notes

Graduates of this program are eligible for professional recognition within the agricultural and food science sectors in Sri Lanka. While there is no mandatory licensing body like the SLMC for doctors, graduates often seek membership in the Sri Lanka Association for the Advancement of Science (SLAAS) or relevant food science professional bodies. The degree is highly valued for overseas employment in the Middle East and Australia, particularly in the food processing and livestock management sectors. Students are encouraged to utilize the university’s career guidance unit to secure high-quality industrial placements during their third or fourth year, as these often lead to direct employment offers.', '187b47b4911539c77da7ba5598d2299908ba4d9ed5206b6e8bffccab76a9512f');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('068', '# Music (B.Mus.)
**Course Number:** 068
**Degree:** Bachelor of Music (B.Mus. Honours)
**Duration:** 4 years
**Entry Stream:** Arts (all-island merit)
**Available at:** University of the Visual and Performing Arts Faculty of Music (068A), University of Sri Jayewardenepura Department of Fine Arts (068B)

---

## Overview

The Bachelor of Music at the University of the Visual and Performing Arts (UVPA) is the premier undergraduate music qualification in Sri Lanka. UVPA — Sri Lanka''s dedicated arts university — has a long tradition of music education rooted in both Western classical and traditional Sri Lankan and South Asian music forms.

**Important:** Music at UVPA requires an aptitude test (practical music audition assessing musical ability, pitch, rhythm, and instrument/voice proficiency). Meeting the Z-score threshold is necessary but not sufficient.

The music industry in Sri Lanka — while not as large as in some countries — encompasses film music, religious music, traditional arts, music education, and the growing entertainment industry.

---

## What You Will Study

**Year 1 — Music Foundations:**
Music Theory (Western — notation, harmony, counterpoint), Traditional Sri Lankan Music (including Sinhala traditional music forms — Udarata, Pahatharata, Sabaragamu), Introduction to Indian Classical Music (Carnatic and Hindustani), Voice Training or Instrumental Studies (primary instrument), Music History.

**Year 2 — Core Music Studies:**
Advanced Music Theory and Analysis, Orchestration and Arrangement, Traditional Percussion (drums — Gatabera, Yak Bera, Udekki), Sri Lankan Folk Music, Music Psychology, Ensemble Performance.

**Year 3 — Specialization:**
Students develop a specialization — Composition, Performance, Ethnomusicology (study of music in cultural context), Music Education, or Film and Media Music. Advanced performance and composition projects.

**Year 4 — Research and Performance:**
Research Dissertation or Major Performance Project, Original Composition, Advanced Seminars, Professional recital preparation.

---

## Career Paths in Sri Lanka

- **Music teaching:** Music teachers at national schools, international schools, and private music academies are in demand throughout Sri Lanka.
- **Film and television music:** Sri Lanka''s film industry, TV dramas, and advertising industry employ music directors, composers, and musicians.
- **Religious music:** Temple, church, mosque, and kovil music — traditional music roles remain integral to Sri Lankan religious and cultural life.
- **Performance and entertainment:** Orchestras, dance drama productions, state cultural departments, and private entertainment.
- **Music therapy:** A growing field — using music for therapeutic purposes with children and adults with disabilities, mental health conditions, and elderly populations.
- **Government arts positions:** Department of Cultural Affairs, National Art Council, provincial cultural offices.
- **Radio and television broadcasting:** SLBC (Sri Lanka Broadcasting Corporation) and Rupavahini employ music professionals.
- **UVPA academia:** Music lecturers and researchers.
- **Digital music production:** Growing online music platforms and content creation opportunities.

---

## Entry Requirements

**A/L Stream:** Arts (all-island merit — no district quota)
**No specific A/L subject requirements** — any three Arts subjects

**Aptitude Test (mandatory):** Practical audition assessing musical knowledge and performance ability. Students should have formal music training (vocal or instrumental) before applying. Proficiency in at least one traditional instrument or demonstrated singing ability is expected.

**Z-score context:** Music Z-score cutoffs are generally in the range of **0.3 to 0.7** for Arts stream — relatively accessible by Z-score, but the aptitude test is the real determining factor.

---

## Special Notes

- The aptitude test is the primary admissions filter — academic Z-score alone will not secure a place.
- Students with lifelong musical training (grade examinations, school music groups, traditional instrument study) have a significant advantage.
- UVPA is the dedicated arts university in Sri Lanka with a campus in Borella, Colombo — a unique environment committed entirely to the arts.
- Creative Music Technology and Production (Course 134) at USJ offers an alternative for students interested in the technical production side of music.
', '23391d4f707a0308445d90ebbd750717c9b007aa467438b85fcb1bf58fc61ef4');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('069', '# Dance (B.Dance)
**Course Number:** 069
**Degree:** Bachelor of Dance (Honours)
**Duration:** 4 years
**Entry Stream:** Arts (all-island merit)
**Available at:** University of the Visual and Performing Arts Faculty of Dance and Drama (069A)

---

## Overview

The Bachelor of Dance at UVPA is Sri Lanka''s premier undergraduate qualification in dance arts, rooted in the rich classical and traditional dance forms of Sri Lanka and South Asia. Sri Lankan classical dance encompasses distinct regional styles — Udarata Nritya (Kandyan Dance), Pahatharata Nritya, Sabaragamu Nritya, and Pahala Nritya — all recognized as important cultural heritage. UVPA has been training professional dancers and dance scholars for decades.

**Important:** Dance at UVPA requires a practical aptitude test assessing dance skill, physical ability, rhythm, and artistic expression. A qualifying Z-score alone is not sufficient for entry.

---

## What You Will Study

**Year 1 — Classical Foundation:**
Sri Lankan Classical Dance Technique (one primary form), History and Theory of Sri Lankan Dance, Music for Dance (drum rhythms — Thovil, Gatabera), Anatomy for Dancers (injury prevention, movement science), Introduction to Indian Classical Dance (Bharatanatyam or Kathak).

**Year 2 — Breadth and Technique:**
Advanced Technique in chosen classical form, Comparative Dance Studies (comparison of regional Sri Lankan traditions), Aesthetic Theory, Dance Choreography Fundamentals, Folk and Ritual Dance Forms (Kohomba Kankariya, Devol Maduwa, Tovil).

**Year 3 — Choreography and Research:**
Original Choreography Project, Teaching Methodology (how to teach dance), Dance and Society (cultural, gender, political dimensions of dance), Research Methods in Dance, Performance.

**Year 4 — Major Work:**
Research Dissertation or Major Choreographic Project, Professional recital/performance, Dance in Contemporary Context (fusion, contemporary dance intersections).

---

## Career Paths in Sri Lanka

- **Dance teaching:** Dance teachers at national schools, private dance academies, and community cultural centres. Highly respected profession within Sri Lankan cultural life.
- **Professional dance performance:** State-sponsored dance troupes, private theatre companies, cultural performance groups, temple and ritual dance.
- **Government cultural positions:** Department of Cultural Affairs, National Arts Council, provincial cultural departments — organizing and preserving classical arts.
- **Dance for film and television:** Choreography and performance for Sri Lankan films, teledrama productions, and music videos.
- **Tourism and cultural shows:** Dance performances for tourist audiences at cultural venues (Kandy Cultural Show, various hotel cultural evenings).
- **UVPA academia:** Dance lecturers and researchers.
- **International Sri Lankan community:** Teaching Sri Lankan classical dance to diaspora communities in Australia, UK, Canada, and Middle East.
- **Dance therapy:** Using movement and dance for wellbeing and therapeutic purposes.

---

## Entry Requirements

**A/L Stream:** Arts (all-island merit — no district quota)
**Aptitude Test (mandatory):** Practical assessment of dance skill. Candidates should have formal training in at least one Sri Lankan classical dance form. Physical fitness, coordination, and artistic expression are assessed.

**Z-score context:** Dance Z-score cutoffs are generally in the **0.2 to 0.6** range — the aptitude test is the decisive factor, not the Z-score alone.

---

## Special Notes

- UVPA is unique in Sri Lanka as a university dedicated entirely to the arts.
- Sri Lankan classical dance has deep spiritual and cultural significance — learning this tradition is both an artistic and cultural responsibility.
- Male dancers are equally important in Sri Lankan classical dance traditions — many costumes and forms specifically require male performers.
- Drama and Dance are offered within the same faculty at UVPA, and collaborative productions between the two departments are common.
', '031bc3eb8f9856eb3e7965869d16e011da3afb0238a06515bf5b0ed521bf55e7');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('070', '# Art & Design
**Course Number:** 070
**Degree:** Bachelor of Fine Arts (Honours) in Art & Design
**Duration:** 4 years
**Entry Stream:** Arts Stream
**Available at:** University of Jaffna (070E)

---

## Overview

The Bachelor of Fine Arts in Art & Design at the University of Jaffna is a comprehensive programme designed to cultivate creative excellence, critical thinking, and technical proficiency in visual arts. In the Sri Lankan context, this degree is vital for preserving cultural heritage while fostering contemporary innovation in the creative economy. The programme bridges the gap between traditional artistic practices and modern design methodologies, preparing students to contribute to the nation’s growing sectors in media, advertising, education, and cultural preservation.

The Faculty of Arts at the University of Jaffna is notable for its deep integration with the rich cultural landscape of the Northern Province. Students benefit from a unique academic environment that encourages the exploration of local aesthetics, history, and social narratives. By combining studio-based practice with theoretical research, the university ensures that graduates are not only skilled practitioners but also informed intellectuals capable of navigating the global art market.

---

## What You Will Study

**Year 1: Foundations of Art and Visual Literacy**
Focuses on fundamental drawing techniques, color theory, art history, and basic design principles. Students are introduced to the history of Sri Lankan art and global art movements to build a strong theoretical base.

**Year 2: Technical Skill Development and Media Exploration**
Students delve into specific mediums such as painting, sculpture, printmaking, and digital design. This year emphasizes the transition from manual techniques to digital software proficiency, including Adobe Creative Suite and basic graphic design tools.

**Year 3: Specialization and Professional Practice**
Students choose a specialization track: Visual Communication, Fine Arts (Painting/Sculpture), or Art Education. The curriculum shifts toward professional application, including branding, exhibition curation, and pedagogical methods for those interested in teaching.

**Year 4: Advanced Research and Final Project**
The final year is dedicated to a major independent research project or a comprehensive studio thesis. Students must produce a body of work that demonstrates their mastery of their chosen specialization, culminating in a public exhibition or portfolio presentation.

---

## Career Paths in Sri Lanka

- **Graphic Designer:** Working with advertising agencies like Phoenix Ogilvy or Grant Group to create visual concepts for marketing campaigns.
- **Art Educator:** Teaching at government schools or private international institutions; requires a passion for pedagogy and curriculum development.
- **Freelance Illustrator/Artist:** Creating content for local publishing houses, digital media platforms, or participating in gallery exhibitions in Colombo and Jaffna.
- **Curator/Gallery Manager:** Managing exhibitions and collections at institutions like the Sapumal Foundation or local cultural centers.
- **UI/UX Designer:** Designing user interfaces for Sri Lankan tech startups and software development firms, focusing on aesthetic and functional user experiences.
- **Postgraduate Study:** Graduates can pursue a Master of Fine Arts (MFA) or a Master of Education (M.Ed.) at local universities like the University of Kelaniya or the University of Visual and Performing Arts to specialize further.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Arts stream. Candidates must have passed three subjects at one sitting. Proficiency in the medium of instruction (Tamil/English) is essential. Applicants are generally required to pass an aptitude test conducted by the University of Jaffna, which assesses creative ability, visual perception, and artistic potential. The Z-score requirement is competitive and varies annually based on the applicant pool and district-based quotas.

---

## Differences Between Universities

The Art & Design programme at the University of Jaffna is unique due to its regional focus and its integration within the Faculty of Arts. Unlike design-focused degrees at the University of Moratuwa, which lean heavily toward industrial and product design, the Jaffna programme maintains a strong emphasis on Fine Arts and cultural expression. Its location provides students with a distinct perspective on post-conflict reconciliation and cultural identity, which is often reflected in the research and creative outputs of the student body.

---

## Special Notes

Graduates of this programme are well-positioned to enter the creative industries, which are increasingly seeking professionals with a blend of traditional artistic skill and digital literacy. While there is no mandatory professional licensing body for artists in Sri Lanka, building a strong professional portfolio is the primary requirement for career advancement. Students are encouraged to engage in internships during their third and fourth years to build industry networks. The medium of instruction is primarily Tamil, with increasing components of English to ensure graduates remain competitive in the globalized digital design market.', '747d608802bd281d035c4258d11bdc76cba1bd298ad269f610d1fd926f4c5c79');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('071', '# Drama and Theatre (B.Drama)
**Course Number:** 071
**Degree:** Bachelor of Drama and Theatre (Honours)
**Duration:** 4 years
**Entry Stream:** Arts (all-island merit)
**Available at:** University of the Visual and Performing Arts Faculty of Dance and Drama (071A), Swamy Vipulananda Institute of Aesthetic Studies — EUSL (071B)

---

## Overview

Drama and Theatre at UVPA provides comprehensive training in the theory and practice of theatre — acting, directing, playwriting, stagecraft, and theatre history. Sri Lanka has a vibrant Sinhala drama tradition (Noortti, Nadagam, Modern Sinhala theatre) alongside Tamil drama traditions and international theatre forms. UVPA''s drama faculty has produced many of Sri Lanka''s leading theatre artists.

Swamy Vipulananda Institute at Eastern University provides Tamil-medium arts education in the Eastern Province.

**Important:** Drama at UVPA typically requires a practical aptitude test assessing dramatic ability and artistic expression.

---

## What You Will Study

**Year 1 — Theatre Foundations:**
Acting Techniques (voice, body, character), History of World Theatre (Greek, Shakespeare, Brecht, Ibsen, Chekhov), History of Sri Lankan Drama (Kolam, Sokari, Nadagam, Noortti), Stagecraft (set design, lighting, costuming basics), Script Reading and Analysis.

**Year 2 — Performance and Production:**
Advanced Acting, Directing Principles, Playwriting and Script Development, Stage Management, Theatre Production (mounting a full production), Movement for Theatre, Voice for Performance.

**Year 3 — Specialization:**
Students develop a focus in Acting, Directing, Playwriting, Theatre Design, or Drama Education. Research Methods, Contemporary Sri Lankan Theatre, Documentary and Political Theatre.

**Year 4 — Major Project and Research:**
Major Drama Production (student directs or performs in a substantial production), Research Dissertation, Professional portfolio.

---

## Career Paths in Sri Lanka

- **Theatre performance:** Acting in Sinhala theatre productions (Lionel Wendt, Nelum Pokuna, touring productions), Tamil theatre, community theatre.
- **Film and television acting:** Sri Lankan film industry and teledrama industry (popular serial dramas on Siyatha, Sirasa, Swarnavahini, Hiru TV).
- **Drama teaching:** Drama teachers are in demand at national schools with performing arts programmes, private drama schools.
- **Theatre directing:** Directing theatrical productions, community theatre, educational theatre.
- **Government cultural sector:** Department of Cultural Affairs, state drama competitions, national drama festivals.
- **Corporate events and entertainment:** Event hosting, corporate theatrical presentations, motivational performances.
- **UVPA academia:** Drama lecturers and researchers.
- **Community theatre and social drama:** Using drama as a tool for social change, health communication, and community development (Applied Theatre).

---

## Entry Requirements

**A/L Stream:** Arts (all-island merit)
**Aptitude Test (mandatory at UVPA):** Practical assessment of dramatic ability, voice, and physical expressiveness.

**Z-score context:** Drama Z-score cutoffs are typically in the **0.2 to 0.6** range — the aptitude test is the deciding factor.

---

## Special Notes

- Sri Lanka''s teledrama (television drama) industry is enormous — producing hundreds of episodes weekly across multiple channels — creating significant employment for trained actors.
- Drama education skills are valuable beyond performance — community development, education, and health communication all use drama techniques.
- EUSL''s SVIAS (071B) serves the Tamil-medium arts community in the Eastern Province.
', 'ecaa87e4663bb7c4772e0829c208cb780bc47bf807be9de8eadf4dc68207c52e');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('072', '# Visual & Technological Arts
**Course Number:** 072
**Degree:** Bachelor of Arts (Special) in Visual and Technological Arts
**Duration:** 4 years
**Entry Stream:** Arts Stream (A/L)
**Available at:** Swamy Vipulananda Institute of Aesthetic Studies, Eastern University, Sri Lanka (072Y)

---

## Overview

The Bachelor of Arts in Visual and Technological Arts is a specialized degree program designed to bridge the gap between traditional aesthetic practices and modern technological applications. Offered by the Swamy Vipulananda Institute of Aesthetic Studies (SVIAS) under the Eastern University, this program focuses on the intersection of creative expression and the socio-economic landscape of Sri Lanka. It aims to produce graduates who are not only skilled in artistic techniques but are also capable of analyzing the role of art in contemporary society.

In the context of Sri Lanka’s growing creative economy, this degree is vital for students looking to professionalize their artistic talents. The curriculum emphasizes the study of line, color, composition, and light, while integrating technological tools that are essential for modern visual communication. By fostering a deep understanding of both heritage and innovation, the program prepares students to contribute to the national cultural sector, the advertising industry, and the digital media landscape.

---

## What You Will Study

**Year 1: Foundations of Visual Arts**
Focuses on the fundamentals of drawing, painting, and design principles. Students are introduced to the history of Sri Lankan art, basic art theory, and the role of technology in visual expression. Core modules include Art History, Drawing Techniques, and Introduction to Digital Media.

**Year 2: Technical Integration and Theory**
Students delve deeper into the relationship between art and social-economic structures. This year covers advanced painting techniques, color theory, and the application of software in visual arts. Subjects include Sociology of Art, Advanced Composition, and Graphic Design Fundamentals.

**Year 3: Specialization and Professional Practice**
Students choose between specializations such as Painting, Graphic Design, or Multimedia Arts. The curriculum shifts toward professional application, including exhibition management, art criticism, and the use of advanced technological tools for creative production.

**Year 4: Research and Final Project**
The final year is dedicated to a comprehensive research dissertation and a final creative project. Students must demonstrate their ability to synthesize theoretical knowledge with practical skills. The year culminates in a public exhibition or a professional portfolio presentation that reflects their mastery of the discipline.

---

## Career Paths in Sri Lanka

*   **Visual Artist/Painter:** Working as independent artists or with galleries like the Barefoot Gallery or Saskia Fernando Gallery, creating original works for exhibitions and private commissions.
*   **Graphic Designer:** Employed by advertising agencies (e.g., Phoenix Ogilvy, Leo Burnett Sri Lanka) to create visual concepts for branding, marketing campaigns, and digital media.
*   **Art Educator:** Teaching at the school level or within private art institutes, contributing to the development of aesthetic education in the Sri Lankan curriculum.
*   **Multimedia Specialist:** Working in digital media houses or production companies to create motion graphics, digital illustrations, and visual content for web and broadcast.
*   **Curator/Gallery Manager:** Managing exhibitions and collections for national museums, cultural centers, or private art foundations, focusing on the preservation and promotion of Sri Lankan art.
*   **Postgraduate Study:** Graduates can pursue a Master of Arts in Fine Arts, Museology, or Cultural Studies at universities like the University of Kelaniya or the University of the Visual and Performing Arts.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Arts stream. Candidates must satisfy the minimum university entry requirements set by the University Grants Commission (UGC). Proficiency in the medium of instruction (Tamil/English) is essential. Applicants are generally required to pass an aptitude test conducted by the SVIAS to assess creative potential and technical interest. The Z-score competitiveness varies annually based on the applicant pool and the specific intake capacity of the Eastern University.

---

## Differences Between Universities

This programme is exclusively offered at the Swamy Vipulananda Institute of Aesthetic Studies (SVIAS), Eastern University. As a specialized institute, it offers a unique environment that combines the traditional aesthetic heritage of the Eastern Province with modern technological training. Unlike general arts faculties, SVIAS provides a dedicated studio-based learning environment, specialized faculty with expertise in both traditional and contemporary arts, and strong regional links to the cultural sector in Batticaloa and beyond.

---

## Special Notes

The degree is fully compliant with the Sri Lanka Qualifications Framework (SLQF). Graduates are eligible to apply for various government and private sector positions that require a degree in the arts or creative industries. Students should be aware that the program involves a significant amount of practical studio work, which may require investment in personal art supplies and digital hardware. The medium of instruction is primarily Tamil, with English components included to ensure students remain competitive in the global creative market. Graduates are encouraged to build a professional portfolio throughout their four years to facilitate easier entry into the workforce.', 'ee2200fe9bbb491a554aee94eecd0a2ba5b17e79f62a439b4c9e10c7ce69fbc9');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('073', '# Export Agriculture
**Course Number:** 073
**Degree:** Bachelor of Science in Export Agriculture
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** Uva Wellassa University of Sri Lanka (073U)

---

## Overview

The Bachelor of Science in Export Agriculture is a specialized degree program designed to bridge the gap between traditional agricultural practices and the modern, value-added export market. In the Sri Lankan context, where the economy relies heavily on the export of tea, rubber, spices, and emerging specialty crops like coffee and mangoes, this degree provides the technical and entrepreneurial skills necessary to enhance the country’s global competitiveness.

Uva Wellassa University (UWU), located in Badulla, is uniquely positioned to offer this program due to its proximity to the heart of Sri Lanka’s plantation and export crop sectors. The faculty emphasizes "Value Addition," ensuring that graduates do not just focus on cultivation, but also on the processing, quality control, and supply chain management required to meet international standards. The program is vital for addressing climate change challenges and modernizing the agri-food sector through precision agriculture and smart irrigation.

---

## What You Will Study

**Year 1: Foundation in Agricultural Sciences**
Focuses on core sciences including Agricultural Botany, Soil Science, Biochemistry, and Principles of Crop Production. Students are introduced to the basics of the Sri Lankan agricultural economy and the unique environmental conditions of the Uva Province.

**Year 2: Crop Management and Technology**
Covers advanced subjects such as Plantation Crop Management (Tea, Rubber, Coconut), Spice and Beverage Crop Production, Plant Physiology, and Agricultural Engineering. Emphasis is placed on the technical aspects of high-value export crops.

**Year 3: Value Addition and Agri-Business**
Students delve into Post-Harvest Technology, Food Quality Assurance, Agricultural Marketing, and Supply Chain Management. This year focuses on how to process raw agricultural products into high-value export commodities.

**Year 4: Research and Industrial Training**
The final year is dedicated to a comprehensive Industrial Training program where students work with major export firms. Students also complete an Independent Research Project (Dissertation) focusing on real-world problems such as climate-resilient farming, organic certification, or precision agriculture technologies.

---

## Career Paths in Sri Lanka

*   **Plantation Management:** Overseeing operations for major regional plantation companies like Kelani Valley Plantations or Bogawantalawa Tea Estates. Involves managing labor, crop yields, and processing facilities.
*   **Quality Assurance & Certification:** Working with organizations like the Sri Lanka Standards Institution (SLSI) or private export firms to ensure products meet international ISO or organic certification standards.
*   **Agri-Business Development:** Roles within the Export Development Board (EDB) or private firms, focusing on market research, export documentation, and expanding the global footprint of Sri Lankan spices and specialty coffee.
*   **Agricultural Extension & Consultancy:** Working with the Department of Export Agriculture (DEA) to provide technical guidance to smallholder farmers on modern cultivation and irrigation techniques.
*   **Supply Chain & Logistics:** Managing the complex logistics of cold-chain transport for perishable agricultural exports, working with freight forwarders and international trade logistics companies.
*   **Postgraduate Research:** Pursuing M.Sc. or Ph.D. programs in Agricultural Economics, Biotechnology, or Sustainable Agriculture at institutions like the Postgraduate Institute of Agriculture (PGIA) in Peradeniya.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Biological Science stream. Candidates must have obtained passes in Biology, Chemistry, and Physics/Agriculture. The program is highly competitive, and selection is based on the Z-score determined by the University Grants Commission (UGC). The medium of instruction is English, and students are expected to have a strong command of the language for technical reporting and research. No specific physical requirements are mandated, but field-based learning requires a high level of physical mobility.

---

## Differences Between Universities

The Export Agriculture degree at Uva Wellassa University is distinct due to its "Entrepreneurial" focus. Unlike traditional agriculture degrees offered at other national universities, the UWU curriculum is specifically tailored to the "Value Addition" model. The university’s location in Badulla provides students with direct access to the Uva tea region, facilitating hands-on field exposure that is difficult to replicate in urban-based faculties. The program is smaller and more specialized than the general agriculture degrees found at the Universities of Peradeniya or Sabaragamuwa, focusing heavily on the export-oriented private sector rather than general food security or subsistence farming.

---

## Special Notes

Graduates of this program are eligible for professional recognition in agricultural sectors. While there is no mandatory licensing body equivalent to the IESL for engineers, graduates often pursue membership in the Sri Lanka Institute of Agricultural Professionals. There is significant demand for these skills in the Middle East and European markets, particularly in roles related to greenhouse management and food safety. Students should be prepared for a curriculum that is heavily weighted toward the private sector, emphasizing business acumen alongside scientific knowledge.', '2fa95dffb41717598b6471292637fecd0a521f857c0626c73d75408f4ae32e83');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('075', '# Industrial Information Technology
**Course Number:** 075
**Degree:** Bachelor of Science (Honours) in Industrial Information Technology
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** Uva Wellassa University of Sri Lanka (075U)

---

## Overview

The Bachelor of Science (Honours) in Industrial Information Technology is a specialized degree programme designed to bridge the gap between traditional computer science and the practical requirements of the industrial sector. In the Sri Lankan context, where the economy is increasingly shifting toward digital transformation in manufacturing, agriculture, and service sectors, this degree provides the technical expertise to optimize industrial processes through advanced IT solutions.

Uva Wellassa University (UWU), located in Badulla, is uniquely positioned to offer this programme. Unlike conventional IT degrees, this course emphasizes the application of technology within business and industrial environments. Students benefit from the university’s focus on "Value Addition," ensuring that graduates are not just software developers, but professionals capable of integrating IT systems into real-world industrial workflows, supply chains, and business management systems.

---

## What You Will Study

**Year 1: Foundations of Computing and Management**
Focuses on core programming (C/C++, Java), mathematics for computing, database management systems, and fundamental management principles. Students are introduced to the industrial context of IT and basic business communication.

**Year 2: Systems Development and Industrial Processes**
Covers advanced software engineering, web development, data structures, and algorithms. Students engage with modules such as Principles of Marketing and Industrial Management to understand how IT supports business growth and operational efficiency.

**Year 3: Specialization and Technical Proficiency**
Students delve into specialized areas such as Enterprise Resource Planning (ERP), Industrial Automation, Network Security, and Business Intelligence. This year focuses on the technical architecture required to run large-scale industrial operations.

**Year 4: Research and Professional Application**
The final year is dedicated to a comprehensive industrial research project. Students apply their knowledge to solve a specific problem within a Sri Lankan industry. This year also includes professional development modules to prepare students for the transition into the corporate workforce.

---

## Career Paths in Sri Lanka

*   **ERP Consultant:** Working with firms like IFS or local implementation partners to integrate software solutions into manufacturing plants and large-scale enterprises.
*   **Industrial Automation Engineer:** Designing and maintaining automated systems for factories and production lines, often employed by manufacturing giants like MAS Holdings or Brandix.
*   **Business Systems Analyst:** Bridging the gap between IT departments and management at companies like John Keells Holdings, focusing on optimizing operational workflows.
*   **Software Engineer (Industrial Focus):** Developing custom software for logistics, supply chain management, and inventory control systems for local software houses and tech startups.
*   **Data Analyst:** Analyzing industrial performance data to drive decision-making in sectors such as agriculture, tea processing, or retail, employed by major conglomerates.
*   **Postgraduate Study:** Graduates are well-prepared for M.Sc. or MBA programmes in IT, Project Management, or Supply Chain Management at institutions like the University of Moratuwa or the University of Colombo.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Physical Science stream. Candidates must have obtained passes in Combined Mathematics, Physics, and Chemistry. Proficiency in English is essential as the medium of instruction is English. The Z-score requirement is highly competitive, as this is a specialized degree programme with limited intake capacity; students should check the current year''s UGC handbook for specific district-based cut-off marks.

---

## Differences Between Universities

This programme is currently offered exclusively at Uva Wellassa University (UWU). The unique advantage of this programme is its location-based industrial focus. While IT degrees in Colombo-based universities often focus on pure software engineering or general computer science, the UWU programme is specifically tailored to the "Industrial" aspect, making it highly relevant for students interested in the intersection of technology and large-scale industrial operations.

---

## Special Notes

The degree is recognized by the University Grants Commission (UGC) of Sri Lanka. Graduates are eligible to apply for professional memberships in bodies such as the Computer Society of Sri Lanka (CSSL). The curriculum is designed to be highly practical, and students are encouraged to seek internships during their academic tenure to gain exposure to the Sri Lankan software and manufacturing industries. The degree provides a strong foundation for both local employment and overseas migration, as the combination of IT and industrial management skills is in high demand globally.', 'a204ae1dd8180e74b7d2f24f2d8220b1e24ccec5ecc2dfa2af5e75ab7c4278a0');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('076', '# Mineral Resources and Technology
**Course Number:** 076
**Degree:** Bachelor of Science Honours in Mineral Resources and Technology
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** Uva Wellassa University of Sri Lanka (076U)

---

## Overview

The Bachelor of Science Honours in Mineral Resources and Technology is a specialized degree programme designed to bridge the gap between traditional geological studies and modern industrial applications. In the Sri Lankan context, this degree is vital for the sustainable management of the country’s natural wealth, including industrial minerals, gemstones, and construction materials. The programme focuses on the scientific exploration, extraction, and value-addition of mineral resources, which are critical drivers for the national economy.

Uva Wellassa University (UWU) is uniquely positioned to offer this programme due to its proximity to the mineral-rich Uva Province and its focus on value-added education. The Faculty of Applied Sciences emphasizes practical, industry-oriented learning, ensuring that graduates are not just geologists, but technologists capable of implementing modern processing methods. The curriculum addresses national priorities such as scientific gem exploration, sustainable mining practices, and environmental remediation, making it a highly relevant qualification for the local industrial sector.

---

## What You Will Study

**Year 1: Foundation in Earth Sciences**
Focuses on core scientific principles including Physics, Chemistry, and Mathematics for Earth Sciences. Students are introduced to Mineralogy, Crystallography, and the fundamentals of Geology, alongside basic computing and communication skills.

**Year 2: Applied Geological Techniques**
Students delve into Petrology, Structural Geology, and Geochemistry. This year introduces Surveying, GIS (Geographic Information Systems), and Remote Sensing, which are essential for mapping and identifying mineral deposits.

**Year 3: Specialization and Processing Technology**
Students choose between specializations such as Mineral Processing Technology or Exploration Geology. Coursework covers Mine Planning, Mineral Economics, Gemmology, and advanced Mineral Processing techniques (e.g., crushing, grinding, and separation methods).

**Year 4: Industrial Application and Research**
The final year is dedicated to an Industrial Training placement (usually 6 months) and a comprehensive Independent Research Project. Students apply their knowledge to real-world problems such as wastewater treatment, environmental impact assessments, or optimizing quartz/gem processing methods.

---

## Career Paths in Sri Lanka

*   **Mineral Processing Engineer:** Working with companies like Lanka Mineral Sands or industrial quartz exporters to design and optimize mineral separation and purification plants.
*   **Exploration Geologist:** Employed by the Geological Survey and Mines Bureau (GSMB) or private mining firms to conduct field surveys and identify new mineral or gem deposits.
*   **Environmental Consultant:** Working with private environmental firms or the Central Environmental Authority (CEA) to manage mine site rehabilitation, water quality monitoring, and pollution control.
*   **Gemmologist/Valuer:** Working with the National Gem and Jewellery Authority (NGJA) or private lapidary and export firms to identify, grade, and value precious stones.
*   **Mine Manager/Safety Officer:** Overseeing daily operations, safety protocols, and regulatory compliance at large-scale quarrying or mining sites across the country.
*   **Postgraduate Research:** Pursuing M.Sc. or Ph.D. degrees in Earth Resources, Environmental Science, or Sustainable Development at institutions like the University of Peradeniya or overseas universities.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Physical Science stream. Candidates must have obtained passes in Combined Mathematics, Physics, and Chemistry. The programme is highly competitive, and selection is based on the Z-score determined by the University Grants Commission (UGC). The medium of instruction is English, and students are expected to have a strong command of the language for technical reporting and research. No specific physical requirements are mandated, but students should be prepared for rigorous field-based practical work.

---

## Differences Between Universities

This programme is exclusively offered at Uva Wellassa University (076U). Unlike traditional geology degrees offered at other state universities, this programme is distinct in its "Technology" focus. It integrates business and management principles with earth science, specifically targeting the value-addition sector of the Sri Lankan mineral industry rather than purely academic or theoretical geology.

---

## Special Notes

Graduates are eligible for membership in professional bodies such as the Geological Society of Sri Lanka (GSSL). While this is a B.Sc. degree, the industrial training component provides a significant advantage for immediate employability. There is a growing demand for these graduates in the private sector for environmental compliance roles, as well as in the export-oriented mineral processing industry. Students should be aware that the curriculum is physically demanding, involving frequent field visits to mines, quarries, and remote geological sites across Sri Lanka.', '040098ebfa4185936cb0d0a93734e70ed33f0e506a93d9ab36a94f9097eab7ee');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('077', '# Business Information Systems (BIS)
**Course Number:** 077
**Degree:** Bachelor of Science (Honours) in Business Information Systems
**Duration:** 4 years
**Entry Stream:** Commerce, Physical Science (some intakes)
**Available at:** University of Sri Jayewardenepura Faculty of Management Studies and Commerce (077A)

---

## Overview

Business Information Systems (BIS) at USJ is a highly regarded hybrid degree combining business management with information technology. It is specifically designed for Commerce-stream students who want technology careers — or for students who want business expertise alongside IT skills. The degree sits at the intersection of management and computing, training graduates who understand both boardroom decisions and technical systems.

USJ''s BIS programme has produced graduates who are competitive in both the tech industry and the management sector, with strong employability in business analysis, IT management, and digital transformation roles.

---

## What You Will Study

**Year 1 — Business and Technology Foundations:**
Programming Fundamentals, Business Accounting, Economics, Database Basics, Mathematics for Business Computing, Business Communication, Introduction to Information Systems.

**Year 2 — Core BIS:**
Object-Oriented Programming, Database Management Systems, Systems Analysis and Design, Business Statistics, Financial Management, E-Business, Business Law, Networking Basics.

**Year 3 — Integration:**
Enterprise Systems (ERP: SAP basics), Business Intelligence and Analytics, IT Project Management (Agile, PRINCE2), Software Engineering for Business Applications, Management Information Systems, Industrial Training.

**Year 4 — Specialization:**
Research Dissertation, Digital Transformation Management, IT Governance and Audit, Business Analytics Advanced, E-Commerce Strategy.

---

## Career Paths in Sri Lanka

- **Business analyst:** The most common role for BIS graduates — bridging the gap between business stakeholders and IT development teams.
- **Systems analyst:** Analysing and designing business-aligned IT solutions.
- **IT manager:** Managing IT departments in banks, finance companies, and corporates.
- **ERP consultant:** Implementing SAP, Oracle, or Microsoft Dynamics systems.
- **Digital transformation officer:** Leading organizational technology change programmes.
- **Data analyst:** Business intelligence and reporting roles.
- **E-commerce management:** Managing online retail platforms and digital channels.
- **IT audit:** Internal audit and compliance reviews of IT systems (often with CISA certification).

---

## Entry Requirements

**A/L Stream:** Commerce (primary); Physical Science applicants may also qualify at some intakes
**Typical Commerce subjects:** Accounting, Business Studies, Economics

**Z-score context:** BIS at USJ (077A) has cutoffs typically in the **0.8 to 1.3** range for Commerce stream — moderately competitive, reflecting the strong demand for this hybrid programme.

---

## Special Notes

- BIS is one of the few programmes accessible to Commerce-stream students that leads directly into technology careers.
- Professional certifications (PMP, ITIL, CISA, Agile/Scrum) complement the BIS degree and are widely pursued by graduates.
- USJ''s BIS students have represented Sri Lanka at international competitions, reflecting the programme''s quality.
', '5570b211180b588f445b517232f235d8311e0a344cfab9af0d01129728e8bef6');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('079', '# Management and Information Technology
**Course Number:** 079
**Degree:** Bachelor of Science (Honours) in Management and Information Technology
**Duration:** 4 years
**Entry Stream:** Physical Science (Combined Mathematics, Physics, Chemistry/ICT)
**Available at:** South Eastern University of Sri Lanka (079J)

---

## Overview

The Bachelor of Science in Management and Information Technology is a multidisciplinary degree designed to bridge the gap between technical computing expertise and organizational management. In the context of Sri Lanka’s rapidly digitizing economy, there is a critical demand for professionals who can not only develop software solutions but also understand the business processes, strategic planning, and operational requirements of local enterprises.

This programme is particularly vital for the Sri Lankan context, where the IT-BPM (Information Technology and Business Process Management) sector is a key export earner. Graduates from this programme are uniquely positioned to act as conduits between technical teams and management, ensuring that technology investments align with corporate goals. The South Eastern University of Sri Lanka (SEUSL) faculty emphasizes a practical approach, integrating regional industrial needs with global standards in systems analysis and business administration.

---

## What You Will Study

**Year 1: Foundations**
Focuses on the fundamentals of computing and management. Subjects include Programming Fundamentals, Mathematics for IT, Principles of Management, Business Communication, and Computer Systems.

**Year 2: Core Integration**
Students delve into intermediate technical and business concepts. Subjects include Data Structures and Algorithms, Database Management Systems, Financial Accounting, Marketing Management, and Object-Oriented Programming.

**Year 3: Advanced Specialization**
Focuses on the intersection of the two fields. Subjects include Systems Analysis and Design, Enterprise Resource Planning (ERP), Human Resource Management, Software Engineering, and Web Technologies. Students often begin exploring elective tracks such as Business Intelligence or E-Commerce.

**Year 4: Professional Application**
The final year focuses on strategic application and research. Students complete a comprehensive Industrial Training (internship) period in a corporate setting, a Final Year Research Project, and advanced modules in Strategic Management, Project Management, and IT Law/Ethics.

---

## Career Paths in Sri Lanka

*   **Business Systems Analyst:** Working with firms like WSO2 or Virtusa to translate business requirements into technical specifications.
*   **IT Project Manager:** Overseeing software development lifecycles at local tech hubs or banks like Commercial Bank or Sampath Bank.
*   **ERP Consultant:** Implementing and maintaining enterprise systems (e.g., SAP or Odoo) for large-scale manufacturing or retail conglomerates like John Keells Holdings.
*   **Database Administrator/Data Analyst:** Managing data infrastructure and deriving business insights for telecommunication giants like Dialog or SLT-Mobitel.
*   **IT Operations Manager:** Ensuring the smooth functioning of IT infrastructure within public sector institutions or private corporate offices.
*   **Postgraduate Study:** Graduates can pursue an MSc in Management and Information Technology (such as the programme offered at the University of Kelaniya) or an MBA to transition into senior executive leadership roles.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results. Students must have completed the Physical Science stream. Required subjects typically include Combined Mathematics, Physics, and Chemistry or ICT. The programme is highly competitive, and entry is determined by the Z-score cutoff for the respective academic year. The medium of instruction is English, and proficiency in the language is essential for success in both coursework and the final year industrial placement.

---

## Differences Between Universities

While the programme is primarily identified with the South Eastern University of Sri Lanka (SEUSL) under the 079 code, it is important to note that similar curricula exist under different faculty structures in other state universities (e.g., the Department of Industrial Management at the University of Kelaniya). SEUSL offers a unique regional perspective, focusing on the application of IT to the specific economic and administrative challenges of the Eastern Province, while providing a curriculum that meets national standards for the Sri Lankan IT industry.

---

## Special Notes

This degree is designed to produce "hybrid" professionals. Students are encouraged to seek student memberships in professional bodies such as the Computer Society of Sri Lanka (CSSL) or the British Computer Society (BCS) Sri Lanka section during their undergraduate years. The mandatory industrial training component is a critical graduation requirement; students should proactively seek placements in reputable software houses or corporate IT departments to ensure high employability upon graduation. The degree is well-recognized for further studies, including conversion pathways into specialized Master’s degrees in Data Science, Cyber Security, or Management.', 'a1c178def0d3176059261c6134eb75127aec117eae8dd49d60ca0282f941a6f9');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('081', '# Physical Education
**Course Number:** 081
**Degree:** Bachelor of Science (Honours) in Physical Education
**Duration:** 4 years
**Entry Stream:** Biological Science, Physical Science, or Arts (with specific subject combinations)
**Available at:** University of Jaffna (081E), Sabaragamuwa University of Sri Lanka (081L)

---

## Overview

The Bachelor of Science (Honours) in Physical Education is a specialized degree designed to produce professionals capable of managing, teaching, and promoting physical health and athletic excellence. In the Sri Lankan context, this degree is vital for addressing the growing need for qualified sports instructors, health educators, and sports administrators within the national school system and the private sports sector. It bridges the gap between theoretical human kinetics and practical field application.

Sabaragamuwa University is particularly notable for its dedicated Department of Sports Sciences and Physical Education, which integrates academic research with field-based training. The University of Jaffna offers a robust programme that emphasizes regional sports development and community health. Both institutions prepare graduates to navigate the evolving landscape of Sri Lankan sports, ranging from grassroots school-level coaching to high-performance national sports management.

---

## What You Will Study

**Year 1: Foundations of Physical Education**
Core modules include Anatomy and Physiology, Foundations of Physical Education, Basic Nutrition, and Introduction to Sports Psychology. Students also begin practical training in fundamental movement patterns and basic coaching principles.

**Year 2: Applied Sciences and Pedagogy**
Focus shifts to Exercise Physiology, Biomechanics, Sports Sociology, and Methods of Teaching Physical Education. Students learn how to design curriculum for school-aged children and understand the physiological responses to exercise.

**Year 3: Specialization and Management**
Students engage with advanced topics such as Sports Management, Adapted Physical Education (for individuals with disabilities), Sports Law, and Advanced Coaching Techniques. This year often includes field placements in schools or sports clubs.

**Year 4: Research and Professional Practice**
The final year is dedicated to a mandatory research dissertation or a comprehensive industry project. Advanced modules include Sports Marketing, High-Performance Training, and Professional Ethics. Students complete an internship to gain real-world experience in their chosen specialization.

---

## Career Paths in Sri Lanka

*   **Physical Education Teacher:** Employed by the Ministry of Education in government schools; involves planning and conducting PE lessons and managing school sports teams.
*   **Sports Development Officer:** Employed by the Ministry of Sports or Provincial Sports Ministries; involves organizing regional sports events and talent identification programmes.
*   **Strength and Conditioning Coach:** Employed by private sports academies or national sports federations (e.g., Sri Lanka Cricket, Sri Lanka Rugby); involves designing training programmes for athletes.
*   **Sports Administrator:** Employed by sports clubs or national governing bodies; involves managing facilities, event logistics, and organizational operations.
*   **Health and Wellness Consultant:** Employed by private fitness centers or corporate wellness programmes; involves providing personalized exercise and lifestyle advice.
*   **Postgraduate Study:** Graduates can pursue M.Sc. or M.Phil. degrees in Sports Science, Exercise Physiology, or Sports Management at local universities or abroad to move into academic or high-level research roles.

---

## Entry Requirements

Admission is based on GCE Advanced Level results. Candidates must have passed three subjects in the Biological, Physical, or Arts streams. Due to the practical nature of the degree, applicants are required to pass a mandatory **Aptitude Test** conducted by the respective universities to assess physical fitness, coordination, and basic sports knowledge. The Z-score requirement is generally competitive, and the medium of instruction is primarily English, though some course materials may be available in local languages.

---

## Differences Between Universities

*   **Sabaragamuwa University (081L):** Offers a highly structured environment within the Faculty of Applied Sciences. It is widely recognized for its strong industry links with national sports bodies and a research-heavy focus on sports management and high-performance training.
*   **University of Jaffna (081E):** Provides a unique perspective on community-based physical education and regional sports development. The faculty emphasizes the role of physical education in social integration and public health within the Northern Province, offering a distinct cultural and practical context for students.

---

## Special Notes

Graduates are eligible to apply for teaching positions within the government sector, subject to the recruitment criteria of the Ministry of Education. While there is no singular "professional body" in the same vein as the IESL for engineers, graduates are encouraged to register with relevant sports associations and the National Institute of Sports Science (NISS) for further professional development. There is a growing demand for these skills in the Middle East and other international markets for fitness coaching and school-level instruction. Students should maintain high physical fitness levels throughout the duration of the course, as practical assessments are a significant component of the grading criteria.', '3be8464545f5240aa261b43b32709395fc389ce2b3ed0a4bb42e97ac03500169');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('082', '# Sports Science and Management (B.Sc.)
**Course Number:** 082
**Degree:** Bachelor of Science (Honours) in Sports Science and Management
**Duration:** 4 years
**Entry Stream:** Physical Science, Biological Science, Arts, Commerce (varies by university)
**Available at:** University of Sri Jayewardenepura (082A), University of Kelaniya Department of Sports Science (082B)

---

## Overview

Sports Science and Management is a multidisciplinary degree combining the science of human performance with the business of sports management. It is ideal for students who are passionate about sport, fitness, health promotion, or sports business, and want to pursue careers as sports scientists, coaches, fitness professionals, sports managers, or physical education teachers.

Sri Lanka''s sports sector is growing — cricket is the national sport, with rugby, football, athletics, swimming, and combat sports also expanding. The government has increased investment in sports facilities, elite athlete development, and school sports programmes.

---

## What You Will Study

**Year 1 — Exercise and Sports Science Foundations:**
Anatomy and Physiology for Sport, Biomechanics (movement analysis), Exercise Physiology (how the body responds to exercise), Psychology of Sport (motivation, mental skills), Introduction to Sports Management, Statistics.

**Year 2 — Applied Sports Science:**
Strength and Conditioning (training programme design), Sports Nutrition, Injury Prevention and Sports Medicine, Motor Learning and Control, Sports Coaching Principles, Sports Marketing and Event Management.

**Year 3 — Advanced and Management:**
Sport Performance Analysis (video analysis, data-driven coaching), Physical Education Pedagogy (teaching methods), Sports Facility Management, Sports Law and Ethics, Research Methods, Industrial placement in sports organization.

**Year 4 — Specialization and Research:**
Research Dissertation, Advanced Coaching or Management electives, Sports Policy and Governance, International Sports Management.

---

## Career Paths in Sri Lanka

- **Sports coaching:** National Sports Council, provincial sports associations, school sports programmes. Sri Lanka Cricket (SLC), Sri Lanka Rugby (SLR), Athletics, Swimming, and other governing bodies.
- **Strength and conditioning:** Fitness trainers, personal trainers, strength and conditioning coaches at gyms, sports academies, and with elite athletes.
- **Sports medicine support:** Exercise rehabilitation, working alongside physiotherapists in sports clinics.
- **Physical education teaching:** P.E. teachers in national schools, international schools, and sports academies.
- **Sports management:** Event management companies (organizing cricket matches, marathons, sports events), sports academies, national associations.
- **Fitness industry:** Sri Lanka''s growing gym and wellness sector — Fitness Life, Body Tech, and many private gyms recruit fitness professionals.
- **Government sports service:** National Youth Services Council (NYSC), Ministry of Sports, Sports Ministry district offices.
- **Sports journalism and broadcasting:** Commentary, sports reporting, sports analysis for TV and digital media.
- **International sports organizations:** IOC, Commonwealth Games Federation, Asian sports governing bodies.

---

## Entry Requirements

**A/L Stream:** Varies by university — Physical Science, Biological Science, Arts, or Commerce streams may qualify; check specific university requirements
**No mandatory aptitude test**, but physical fitness aptitude may be assessed informally.

**Z-score context:** Sports Science cutoffs are generally in the **0.4 to 0.9** range — one of the more accessible degree programmes across multiple streams.

---

## Special Notes

- Students who have represented their school or district in sports will find their practical experience directly relevant to this degree.
- Physical fitness is important but not formally assessed at admission — the degree is primarily academic with applied practical components.
- Sri Lanka Cricket''s enormous popularity creates genuine career opportunities for graduates interested in cricket administration, coaching, and analysis.
- Growing global awareness of physical health, mental wellness, and fitness culture is expanding the private sector opportunities for Sports Science graduates.
', '3c77c78d11c82a263c12e40005c71da6ed688b5b3921af5a0ce4be12d5906211');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('083', '# Speech and Hearing Sciences (B.Sc.)
**Course Number:** 083
**Degree:** Bachelor of Science (Honours) in Speech and Hearing Sciences
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Kelaniya Faculty of Medicine, Department of Disability Studies (083A)

---

## Overview

Speech and Hearing Sciences (also known as Speech-Language Pathology and Audiology) is a healthcare profession focused on diagnosing and treating communication disorders — problems with speech, language, voice, swallowing, and hearing. Speech-Language Pathologists (SLPs) work with children who have delayed speech, stroke patients who have lost the ability to talk, people who stutter, deaf children learning to communicate, and many others.

Sri Lanka has a significant shortage of qualified speech and hearing professionals. The Department of Disability Studies at Kelaniya University is the primary provider of this degree in the state system, and demand for graduates far exceeds supply.

---

## What You Will Study

**Year 1 — Sciences Foundation:**
Anatomy and Physiology of Speech and Hearing Mechanisms, Linguistics and Phonetics (how sounds are produced and perceived), Psychology, Neuroscience basics, Introduction to Communication Disorders.

**Year 2 — Core Sciences:**
Audiology (how hearing works, types of hearing loss, audiometry testing), Speech Science (acoustic analysis of speech), Child Language Development, Neuropathology of Communication (stroke, brain injury), Sign Language basics, Hearing Aid Technology.

**Year 3 — Clinical Practice:**
Assessment and Management of Speech Disorders (articulation, phonological disorders, fluency — stuttering, voice disorders), Language Disorders in Children (developmental language delay, autism spectrum communication), Acquired Language Disorders (aphasia after stroke), Aural Rehabilitation (hearing aid fitting, cochlear implant rehabilitation). Hospital and school placements begin.

**Year 4 — Advanced Clinical and Research:**
Complex Communication Disorders (autism, cerebral palsy, progressive neurological diseases), Swallowing Disorders (dysphagia), Research Dissertation, Extended clinical placements.

---

## Career Paths in Sri Lanka

- **Government hospitals:** Neurology units, ENT departments, rehabilitation centres, child development units — all require speech therapists.
- **Special education:** Schools for deaf and hard-of-hearing students, autism schools, and developmental delay programmes.
- **Paediatric clinics:** Child development assessment centres, early intervention programmes for communication-delayed children.
- **Private practice:** Speech therapy clinics are growing in urban areas as awareness increases.
- **Cochlear implant programmes:** National Hospital Colombo and private hospitals have cochlear implant teams requiring audiologists.
- **NGOs:** Organizations working with disability, rehabilitation, and inclusive education.
- **International opportunities:** UK, Australia, Canada — all have significant shortages of SLPs with strong recruitment of trained professionals.
- **Academia:** Lecturers at Kelaniya and other health sciences faculties.

---

## Entry Requirements

**A/L Stream:** Biological Science
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Speech and Hearing Sciences cutoffs are typically in the **0.6 to 1.0** range — accessible to most Biological Science students. This is one of the most impactful health science careers relative to its Z-score threshold.

---

## Special Notes

- Sri Lanka has a significant unmet need for speech and hearing services — graduates are virtually guaranteed employment.
- International pathways are strong: the profession is in shortage in the UK (RCSLT registration), Australia (SPA registration), and Canada.
- Empathy, patience, and excellent communication skills are essential personal qualities for this profession.
- The field is expanding to include teletherapy — online speech therapy sessions — which has opened new service delivery models.
', '92c80fad47046ba1578cdb02b9c2f1606c0e7fd00d7ac287aef638871a62eeae');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('084', '# Arabic Language
**Course Number:** 084
**Degree:** Bachelor of Arts (Honours) in Arabic Language
**Duration:** 4 years
**Entry Stream:** Arts Stream
**Available at:** South Eastern University of Sri Lanka (084J)

---

## Overview

The Bachelor of Arts (Honours) in Arabic Language, offered by the Faculty of Islamic Studies and Arabic Language at the South Eastern University of Sri Lanka (SEUSL), is a specialized academic programme designed to provide students with comprehensive proficiency in the Arabic language, literature, and linguistics. Given Sri Lanka’s historical and contemporary ties with the Middle East, this degree is vital for fostering cross-cultural communication, religious scholarship, and international diplomacy.

The programme is particularly notable for its focus on the intersection of Arabic studies with the local socio-cultural context. Students engage in rigorous academic study that bridges classical Arabic heritage with modern linguistic applications. Located in Oluvil, the faculty provides a unique environment for students to immerse themselves in a curriculum that addresses the specific needs of the Sri Lankan job market, including translation, education, and international relations.

---

## What You Will Study

**Year 1: Foundations of Arabic Language**
Focuses on basic linguistic skills, including Arabic grammar (Nahw), morphology (Sarf), and introductory reading and writing. Students also study the history of Arabic literature and basic communication skills.

**Year 2: Intermediate Proficiency and Linguistics**
Students advance to complex grammatical structures, advanced composition, and Arabic rhetoric (Balagha). Courses include Arabic prose and poetry, as well as an introduction to the history of Islamic civilization and its linguistic impact.

**Year 3: Advanced Specialization**
Curriculum shifts toward specialized areas such as Arabic-Tamil/English translation techniques, modern Arabic literature, and sociolinguistics. Students begin to analyze the challenges of teaching Arabic as a second language in the Sri Lankan context.

**Year 4: Research and Professional Application**
The final year is dedicated to advanced research, including a compulsory dissertation/research project. Students also undertake professional training in interpretation, advanced translation, and pedagogical methods for teaching Arabic.

---

## Career Paths in Sri Lanka

*   **Education Sector:** Teaching Arabic in government schools or private international schools. Employers include the Ministry of Education and private educational institutions.
*   **Diplomatic and International Relations:** Working as a translator or cultural attaché at embassies (e.g., Embassy of Saudi Arabia, UAE, or Qatar in Colombo).
*   **Translation and Interpretation:** Providing professional translation services for legal, business, or religious documents. Employers include private law firms and translation agencies.
*   **Media and Journalism:** Roles in media houses that focus on international news or religious programming, involving content creation and translation.
*   **Tourism and Hospitality:** Serving as a guide or liaison for Middle Eastern tourists visiting Sri Lanka, facilitating communication and cultural exchange.
*   **Postgraduate Study:** Opportunities to pursue a Master’s or PhD in Arabic Linguistics, Islamic Studies, or Education, either at SEUSL or through international scholarships in the Middle East.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Arts stream. Candidates must have obtained a credit pass (C) or higher in Arabic at the A/L examination. The selection process is highly competitive, and the Z-score required varies annually based on the applicant pool and district-based quotas. Proficiency in English is highly recommended as a secondary language for research and translation purposes.

---

## Differences Between Universities

The Arabic Language programme at the South Eastern University of Sri Lanka (SEUSL) is unique in the state university system for being housed within a dedicated Faculty of Islamic Studies and Arabic Language. Unlike general Arts faculties in other universities where Arabic might be a minor subject, SEUSL offers a specialized, department-led environment. This provides students with access to a concentrated faculty of experts, specialized library resources, and a research culture specifically focused on Arabic-English-Tamil translation and linguistics.

---

## Special Notes

The medium of instruction is primarily Arabic, supplemented by English and Tamil where necessary to facilitate comprehension. Graduates are well-positioned for employment in the Middle East, where there is a constant demand for bilingual professionals. Students should be aware that while this degree provides a strong academic foundation, professional certification for high-level legal translation may require additional government-recognized examinations. The programme is highly research-oriented, and students are encouraged to participate in academic journals and conferences hosted by the faculty during their tenure.', '43650bb3a05eca8ef024f30fbcb3a51033e732e635f8b34e79c37670944d68b9');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('085', '# Visual Arts (B.V.A.)
**Course Number:** 085
**Degree:** Bachelor of Visual Arts (Honours)
**Duration:** 4 years
**Entry Stream:** Arts (all-island merit)
**Available at:** University of the Visual and Performing Arts Faculty of Visual Arts (085A)

---

## Overview

Visual Arts at UVPA covers the full range of visual art disciplines — painting, sculpture, printmaking, ceramics, and new media arts. The Faculty of Visual Arts has a history of over 100 years, rooted in Sri Lanka''s rich tradition of visual arts that connects to ancient cave paintings, temple art, and the modern Sri Lankan art movement.

**Important:** Visual Arts at UVPA requires a practical aptitude test assessing artistic ability, visual creativity, and portfolio of work.

---

## What You Will Study

**Year 1 — Foundations:**
Drawing Fundamentals, Colour Theory and Painting Basics, Two-Dimensional and Three-Dimensional Design, Sri Lankan Art History (ancient to modern), Art Theory, Introduction to Printmaking.

**Year 2 — Media and Technique:**
Advanced Painting (oil, watercolour, acrylic), Sculpture (clay, plaster, mixed media), Printmaking (etching, screen printing, woodblock), Digital Art and New Media, Sri Lankan Traditional Arts (traditional craft and decorative art forms).

**Year 3 — Specialization:**
Students develop a personal artistic direction. Options include Fine Arts Painting, Sculpture, Printmaking, Ceramics, Mixed Media, Digital and New Media Arts. Research in art practice.

**Year 4 — Graduation Exhibition and Research:**
Major independent artwork or exhibition, Research Dissertation, Professional Artist Statement and Portfolio.

---

## Career Paths in Sri Lanka

- **Fine arts practice:** Professional artists who exhibit and sell work — galleries (Lionel Wendt, Harold Pieris Gallery, Saskia Fernando Gallery), art fairs.
- **Art and design teaching:** Art teachers in national schools, private art schools, and higher education.
- **Commercial art:** Graphic design, illustration, and visual design for advertising agencies, publishers, packaging companies.
- **Sri Lankan handicrafts and export:** Traditional arts and crafts sector — designing and producing craft items for tourism and export (batik, lacquerware, brassware, ceramics).
- **Museum and gallery work:** National Museum, Colombo, and private galleries employ visual arts graduates as curators and educators.
- **Digital content creation:** Illustration for social media, animation, digital graphic arts.
- **Film and television:** Set design, costume design, prop creation, visual effects.
- **Government arts:** Department of Cultural Affairs, National Art Council, Arts Council of Sri Lanka.

---

## Entry Requirements

**A/L Stream:** Arts (all-island merit)
**Aptitude Test (mandatory):** Portfolio review and practical assessment of drawing/painting ability. A strong portfolio of original artwork is essential for the aptitude test.

**Z-score context:** Visual Arts Z-score cutoffs are in the **0.2 to 0.5** range — the lowest Z-score thresholds in the state university system. The aptitude test is the decisive factor.

---

## Special Notes

- Students should develop their portfolio systematically from school onwards — a minimum of 10–15 original artworks in various media.
- Sri Lanka''s tourism industry creates commercial demand for visual arts through handicrafts, hotel décor, and cultural displays.
- UVPA''s connections with regional art institutions in India, China, and ASEAN create international exchange and exhibition opportunities.
', '2223366a227c963bab3fa3b81c1198342150f05b3ea5314a8828f906795cd558');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('086', '# Animal Science & Fisheries
**Course Number:** 086
**Degree:** Bachelor of Science in Animal Science and Fisheries (B.Sc. AS&F)
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Peradeniya (086B)

---

## Overview

The Bachelor of Science in Animal Science and Fisheries is a specialized degree program offered by the Faculty of Agriculture at the University of Peradeniya. This program is designed to address the critical needs of Sri Lanka’s livestock and aquatic sectors, focusing on sustainable production, animal health, and the management of marine and inland fisheries resources. Given Sri Lanka’s geographical position as an island nation and the growing demand for high-quality protein, this degree plays a vital role in national food security and economic development.

The University of Peradeniya is uniquely positioned to offer this program due to its extensive research facilities, including experimental farms and proximity to diverse ecological zones. Students benefit from an interdisciplinary approach that combines traditional agricultural practices with modern biotechnology and management techniques. The program is highly regarded for its emphasis on field-based learning, ensuring graduates are prepared to tackle the practical challenges faced by the local farming and aquaculture industries.

---

## What You Will Study

**Year 1: Foundation in Agriculture and Basic Sciences**
Focuses on core biological and agricultural principles, including Agricultural Chemistry, Botany, Zoology, Mathematics, and an Introduction to Animal Science and Fisheries. Students also study basic computer literacy and English for academic purposes.

**Year 2: Core Animal and Aquatic Sciences**
Deepens knowledge in Animal Nutrition, Animal Physiology, Genetics and Breeding, and Principles of Aquaculture. Students begin exploring the biology of farm animals and aquatic organisms, alongside introductory courses in Agricultural Economics and Extension.

**Year 3: Advanced Specialization and Management**
Covers specialized modules such as Ruminant and Non-ruminant Production, Fish Health Management, Aquatic Ecology, Post-harvest Technology, and Animal Biotechnology. Students also engage in farm management practices and field training.

**Year 4: Research and Professional Application**
The final year is dedicated to a mandatory individual research project (dissertation) conducted under the guidance of senior academic staff. Students also undertake industrial training (internships) and study advanced topics like Policy and Legislation in Animal and Fisheries sectors, and Entrepreneurship in Agriculture.

---

## Career Paths in Sri Lanka

*   **Livestock Development Officer:** Working with the Department of Animal Production and Health (DAPH) to provide extension services, disease control, and breeding support to local farmers.
*   **Aquaculture Farm Manager:** Managing commercial shrimp or fish farms in regions like Chilaw or Batticaloa, overseeing production cycles, water quality, and stock health.
*   **Technical Consultant/Sales Representative:** Working for private sector agribusiness firms (e.g., CIC Feeds, Gold Coin, or Prima) providing technical expertise on animal feed, vaccines, and farm equipment.
*   **Research Scientist:** Conducting research at the National Aquatic Resources Research and Development Agency (NARA) or the Veterinary Research Institute (VRI) to improve local breeds and aquatic resource management.
*   **Quality Assurance Officer:** Working in food processing plants (e.g., Cargills, Keells) to ensure that meat, dairy, and fish products meet national and international safety standards.
*   **Postgraduate Academic/Researcher:** Pursuing M.Sc. or Ph.D. programs in specialized fields like Animal Nutrition, Marine Biology, or Biotechnology at local or international universities.

---

## Entry Requirements

Admission is strictly through the University Grants Commission (UGC) based on the G.C.E. Advanced Level examination results. Students must have sat for the A/L examination in the **Biological Science** stream. Required subjects include Biology, Chemistry, and Physics/Agriculture. The Z-score requirement is highly competitive, reflecting the prestige of the Faculty of Agriculture at the University of Peradeniya. The medium of instruction is English, and students are expected to have a strong command of the language for technical writing and research.

---

## Differences Between Universities

This program is currently offered exclusively at the University of Peradeniya under the Faculty of Agriculture. Unlike general science degrees, this program is integrated into an agricultural faculty, providing students with a broader perspective on the entire food value chain—from farm to fork—rather than focusing solely on pure biology.

---

## Special Notes

Graduates of this program are eligible for professional recognition within the agricultural sector. While this degree does not grant a license to practice veterinary medicine (which requires a BVSc degree), it is the primary qualification for technical and managerial roles in the livestock and fisheries industries. There is significant demand for these graduates in the private sector, particularly as Sri Lanka moves toward modernizing its dairy and aquaculture industries. Students are encouraged to participate in student-led agricultural societies to build industry networks early in their academic career.', '31fcca8cf0a1fd9086ebb0db85ce99fb99875a8a630a65586347850265398f28');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('087', '# Food Production & Technology Management
**Course Number:** 087
**Degree:** Bachelor of Science (Honours) in Food Production & Technology Management
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** Wayamba University of Sri Lanka (087M)

---

## Overview

The Bachelor of Science (Honours) in Food Production & Technology Management is a specialized degree program designed to bridge the gap between food science, industrial technology, and business management. In the context of Sri Lanka’s growing food processing and export sectors, this degree is vital for professionals who can ensure food safety, optimize production efficiency, and innovate in product development to meet both local and international market demands.

The program is hosted by the Faculty of Livestock, Fisheries & Nutrition at the Wayamba University of Sri Lanka (Makandura premises). This faculty is uniquely positioned to provide students with a blend of theoretical knowledge and practical exposure to the livestock and food industries. By focusing on the entire value chain—from raw material sourcing to final consumer presentation—graduates are equipped to lead operations in Sri Lanka’s competitive food manufacturing landscape.

---

## What You Will Study

**Year 1: Foundation in Basic Sciences**
Focuses on core scientific principles including Chemistry, Biochemistry, Microbiology, and Mathematics. Students are introduced to the fundamentals of food science and the basics of management and economics.

**Year 2: Food Technology and Processing**
Covers the core technical aspects of food production, including Food Chemistry, Food Microbiology, Principles of Food Processing, and Post-harvest Technology. Students begin to explore the intersection of technology and food safety.

**Year 3: Management and Industrial Application**
Shifts focus toward the "Management" component of the degree. Subjects include Food Quality Management, Industrial Management, Supply Chain Management, and Food Marketing. Students learn about HACCP, ISO standards, and regulatory requirements in the Sri Lankan food industry.

**Year 4: Advanced Specialization and Research**
The final year involves advanced modules such as Food Product Development, Entrepreneurship, and specialized electives. A significant portion of the year is dedicated to an Industrial Training placement and an Independent Research Project, where students apply their knowledge to solve real-world problems in food production facilities.

---

## Career Paths in Sri Lanka

*   **Production Manager:** Overseeing daily operations in large-scale food manufacturing plants (e.g., Ceylon Biscuits Limited, Cargills Quality Foods). Involves managing production lines, staff, and output efficiency.
*   **Quality Assurance (QA) Executive:** Ensuring food products meet safety and quality standards (e.g., Nestlé Lanka, Fonterra). Involves laboratory testing, auditing, and regulatory compliance.
*   **Product Development Specialist:** Working in R&D departments to create new food products or improve existing recipes (e.g., Maliban Biscuit Manufactories, Link Natural).
*   **Supply Chain & Logistics Coordinator:** Managing the procurement of raw materials and the distribution of finished goods (e.g., Keells Food Products).
*   **Food Safety Consultant/Auditor:** Working with regulatory bodies or private firms to ensure food establishments adhere to national health and safety laws.
*   **Postgraduate Study:** Graduates can pursue M.Sc. or Ph.D. programs in Food Science, Food Technology, or Business Administration (MBA) at local universities like the University of Peradeniya or the University of Sri Jayewardenepura, or seek international scholarships.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Biological Science stream. Candidates must satisfy the minimum requirements for university admission as determined by the University Grants Commission (UGC). The selection is highly competitive, and the Z-score required varies annually based on the applicant pool and district-based quotas. The medium of instruction is English.

---

## Differences Between Universities

This programme is exclusively offered by the Wayamba University of Sri Lanka. Its location in the Makandura premises provides a unique advantage, as it is situated in a region with significant agricultural and industrial activity, allowing for strong industry links and practical field exposure that urban-based universities may not offer in the same capacity.

---

## Special Notes

Graduates are eligible to apply for professional membership in relevant scientific bodies, such as the Sri Lanka Association for the Advancement of Science (SLAAS) or the Institute of Food Science and Technology Sri Lanka (IFSTSL). The degree is highly regarded for its practical orientation, making graduates employable in the thriving export-oriented food industry of Sri Lanka, including the tea, spice, and processed food sectors. Students are encouraged to maintain a high GPA during their industrial training, as this often serves as a direct pathway to permanent employment with their host organizations.', 'dac7bf93098d3b7e71dc6836877f4330995c1a9c77268f8f730fd8e4aca89758');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('088', '# Aquatic Resources Technology
**Course Number:** 088
**Degree:** Bachelor of Science (Honours) in Aquatic Resources Technology
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** Uva Wellassa University of Sri Lanka (088U)

---

## Overview

The Bachelor of Science (Honours) in Aquatic Resources Technology is a specialized degree designed to address the growing demand for sustainable management of Sri Lanka’s vast aquatic wealth. As an island nation, Sri Lanka relies heavily on its inland fisheries, coastal aquaculture, and marine resources. This programme bridges the gap between traditional biology and modern industrial technology, focusing on the scientific cultivation of aquatic organisms, the management of water ecosystems, and the processing of aquatic food products.

Uva Wellassa University (UWU) is uniquely positioned to offer this degree through its Faculty of Animal Science and Export Agriculture. The programme is highly practical, emphasizing entrepreneurship and value addition, which aligns with the university''s mission to produce graduates who can contribute directly to the national economy. Students benefit from a curriculum that integrates laboratory research with field-based training, preparing them for both the public sector and the rapidly expanding private aquaculture industry in Sri Lanka.

---

## What You Will Study

**Year 1: Foundation in Basic Sciences**
Focuses on core biological and chemical principles, including Zoology, Botany, Chemistry, and Mathematics. Students are introduced to the fundamentals of aquatic environments, basic ecology, and computer literacy.

**Year 2: Core Aquatic Sciences**
Students delve into Limnology, Oceanography, Aquatic Biology, and Microbiology. Key modules include Fish Physiology, Aquatic Environment Management, and introductory Aquaculture systems.

**Year 3: Applied Technology and Management**
Focuses on specialized technical skills. Subjects include Fish Breeding and Hatchery Management, Aquatic Food Processing Technology, Fish Health Management, and Fisheries Economics. Students begin to explore the intersection of technology and resource conservation.

**Year 4: Specialization and Research**
The final year focuses on advanced topics such as Biotechnology in Aquaculture, Post-harvest Technology, and Environmental Impact Assessment. A significant portion of the year is dedicated to an Independent Research Project (Dissertation) and an Industrial Training placement, where students apply their knowledge in real-world settings like shrimp farms, processing plants, or government research stations.

---

## Career Paths in Sri Lanka

- **Aquaculture Farm Manager:** Overseeing large-scale shrimp or ornamental fish farms. Employers include private sector firms like Ceylon Fresh Seafoods or various export-oriented aquaculture companies. Work involves monitoring water quality, stock health, and production cycles.
- **Fisheries Officer/Researcher:** Working with the National Aquatic Resources Research and Development Agency (NARA) or the Department of Fisheries and Aquatic Resources. Involves field surveys, stock assessment, and policy implementation.
- **Quality Assurance Executive:** Working in seafood processing and export companies (e.g., Tropic Fishery, Global Seafoods). Focuses on food safety standards (HACCP), hygiene, and export quality compliance.
- **Aquatic Environmental Consultant:** Working with environmental NGOs or private consultancies to conduct Environmental Impact Assessments (EIA) for coastal development projects.
- **Academic/Researcher:** Pursuing postgraduate studies (MSc/PhD) at institutions like the University of Peradeniya or the University of Ruhuna to contribute to research in marine biology or biotechnology.
- **Entrepreneur:** Establishing independent ventures in ornamental fish breeding, hydroponics, or value-added aquatic food production for local and international markets.

---

## Entry Requirements

Admission is strictly through the University Grants Commission (UGC) based on the G.C.E. Advanced Level examination in the Biological Science stream. Candidates must have obtained a minimum of three "S" passes in Biology, Chemistry, and Physics/Agriculture. The Z-score requirement is competitive and varies annually based on the applicant pool. The medium of instruction is English, and students are expected to have a strong command of the language for technical writing and research.

---

## Differences Between Universities

This programme is currently offered exclusively at Uva Wellassa University (UWU). Unlike traditional state universities that may focus heavily on pure Marine Biology, the UWU curriculum is distinctively "technology-oriented." It emphasizes the commercial and industrial application of aquatic resources, making it highly relevant for students interested in the business and production side of the industry rather than purely theoretical research.

---

## Special Notes

- **Professional Recognition:** Graduates are eligible for membership in professional bodies related to animal science and aquatic resources.
- **Industrial Training:** The programme includes a mandatory industrial training component, which is a critical bridge to employment. Students are encouraged to build professional networks during this period.
- **Postgraduate Pathways:** Graduates can pursue postgraduate studies in Fisheries Management, Marine Biotechnology, or Environmental Science both locally and internationally.
- **Employment Demand:** There is a steady demand for graduates in the export-oriented seafood sector, which is a significant contributor to Sri Lanka’s foreign exchange earnings.
- **Medium of Instruction:** All lectures, practicals, and examinations are conducted in English.', '7602a2ff6705fe3543a1e7244cfd32eb3a82ac6e3e9257d6d6a52f5c5925fcd9');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('090', '# Hospitality, Tourism and Events Management (B.Sc.)
**Course Number:** 090
**Degree:** Bachelor of Science (Honours) in Hospitality, Tourism and Events Management
**Duration:** 4 years
**Entry Stream:** Commerce, Arts, Physical Science (varies)
**Available at:** Uva Wellassa University Faculty of Management Studies (090A)

---

## Overview

Sri Lanka''s tourism industry is one of the most important sectors of the economy, contributing approximately 5–10% of GDP in pre-COVID years and employing hundreds of thousands of people directly and indirectly. With Sri Lanka receiving over 2 million international tourists annually (pre-COVID), and with ambitious government targets to grow this further, hospitality and tourism graduates are in sustained demand.

This programme at Uva Wellassa University combines hotel management, tourism planning, event management, and the business of hospitality — preparing graduates for the full range of careers in this exciting, people-centred industry.

---

## What You Will Study

**Year 1 — Hospitality Foundations:**
Hotel Operations (Front Office, Housekeeping, Food and Beverage), Food Science and Culinary Arts basics, Tourism Geography (Sri Lanka and the world), Business Communication, Tourism Economics, Introduction to Events Management.

**Year 2 — Tourism and Business:**
Tourism Marketing, Hotel Financial Management (rooms revenue management, F&B costing), Human Resource Management in Hospitality, Tour Operations Management, Cultural Heritage Tourism, Hospitality Law and Regulations, Research Methods.

**Year 3 — Advanced Practice:**
Strategic Hotel Management, MICE (Meetings, Incentives, Conferences, Exhibitions) Management, Sustainable Tourism, Eco-Tourism, Rural Tourism and Community-Based Tourism, Digital Tourism (OTAs, TripAdvisor, Google Hotels), Industrial Training (compulsory — 6 months in a hotel or tourism organization).

**Year 4 — Specialization:**
Research Dissertation, Resort Management, Destination Management, Event Planning and Execution, Sports Tourism, Wellness and Medical Tourism.

---

## Career Paths in Sri Lanka

- **Hotel and resort management:** Front Office Manager, Food and Beverage Manager, Revenue Manager, General Manager pathway in 5-star hotels (Cinnamon, Shangri-La, Marriott, Hilton, Jetwing, Aitken Spence, John Keells Hotels).
- **Tourism management:** Tour operators (Walkers Tours, Malkey Travel, Ceylon Travels), destination management companies, inbound tour operations.
- **Event management:** Corporate events, weddings, sports events, national festivals, MICE events. Event management companies are expanding in Sri Lanka.
- **Government tourism:** Sri Lanka Tourism Development Authority (SLTDA), Sri Lanka Tourism Promotion Bureau (SLTPB) — marketing, planning, and policy roles.
- **Airlines:** SriLankan Airlines cabin crew, ground operations, and marketing roles often recruit hospitality graduates.
- **Travel agencies:** Online and offline travel agencies, OTA (Online Travel Agency) management.
- **Rural and eco-tourism:** Community-based tourism enterprises in Ella, Sigiriya, Knuckles, and Yala areas.
- **Medical tourism:** A growing sector linking Sri Lanka''s healthcare quality with tourism — hospitality management in medical tourism hospitals and wellness centres.
- **Maldives:** The Maldives tourism industry is one of the largest employers of Sri Lankan hospitality professionals.

---

## Entry Requirements

**A/L Stream:** Commerce (primary), Arts, or Physical Science — check Uva Wellassa University''s current requirements
**No specific mandatory subjects** beyond A/L stream requirements.

**Z-score context:** Hospitality, Tourism and Events Management at UWU (090A) has cutoffs typically in the **0.4 to 0.8** range — one of the most accessible degree programmes nationally. Strong practical aptitude and English communication skills matter more than Z-score alone.

---

## Special Notes

- Industrial training (hotel internship) is compulsory and gives students real workplace experience.
- English communication skills are essential in hospitality — students should develop their English proficiency from school onwards.
- Tourism recovered strongly after COVID-19 — with visitor numbers rising rapidly, the industry is actively hiring again.
- Sri Lanka''s unique combination of cultural heritage sites (Sigiriya, Kandy, Anuradhapura, Galle), wildlife (Yala, Udawalawe, Minneriya), beaches, and cuisine creates a distinctive tourism destination profile.
', '6b0f447c2155a5201fbd6c69144e0e715acc88be2cd2f7aec42a329d7594c566');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('091', '# Information Technology & Management
**Course Number:** 091
**Degree:** Bachelor of Science Honours in Information Technology & Management
**Duration:** 4 years
**Entry Stream:** Physical Science (A/L Mathematics stream)
**Available at:** University of Moratuwa (091G)

---

## Overview

The Bachelor of Science Honours in Information Technology & Management is a unique, interdisciplinary degree offered by the Faculty of Information Technology at the University of Moratuwa. It is designed to bridge the gap between technical IT expertise and business management principles. In the context of Sri Lanka’s rapidly expanding IT/BPM sector, this degree produces professionals who can not only build software systems but also manage the strategic, financial, and operational aspects of technology-driven organizations.

The University of Moratuwa is widely recognized as the premier technological university in Sri Lanka. Graduates of this program are highly sought after by both multinational corporations and local tech giants because they possess a dual-competency profile. This degree is particularly relevant for students who wish to move beyond pure coding into leadership roles, project management, and digital transformation consultancy within the Sri Lankan corporate landscape.

---

## What You Will Study

**Year 1: Foundations**
Focuses on core computing and business fundamentals. Subjects include Programming (Java/Python), Mathematics for IT, Database Management Systems, Principles of Management, and Economics. Students also undergo intensive training in communication skills.

**Year 2: Intermediate Technical & Business Skills**
Deepens technical knowledge with Data Structures & Algorithms, Web Technologies, and Software Engineering. Business modules include Financial Accounting, Organizational Behavior, and Marketing Management, providing a solid grounding in how businesses function.

**Year 3: Advanced Integration**
Students explore specialized areas such as Enterprise Resource Planning (ERP), Business Intelligence, Information Systems Security, and Project Management. This year emphasizes the application of IT to solve complex business problems through case studies and lab-based assignments.

**Year 4: Specialization & Research**
The final year focuses on professional practice. Students undertake a comprehensive Industrial Training placement (usually 6 months) in a leading Sri Lankan company. The year culminates in a Final Year Research Project, where students must solve a real-world industry problem, integrating both technical and management solutions.

---

## Career Paths in Sri Lanka

- **Business Analyst:** Working with firms like WSO2 or Virtusa to bridge the gap between client requirements and technical development teams.
- **IT Project Manager:** Overseeing software development lifecycles at companies like IFS or 99x, ensuring projects are delivered on time and within budget.
- **Systems Consultant:** Advising local enterprises on digital transformation and ERP implementation (e.g., SAP/Oracle consultants).
- **Product Manager:** Managing the roadmap and feature sets for software products at local startups or fintech companies like PayHere or PickMe.
- **Data Analyst/Business Intelligence Specialist:** Analyzing organizational data to drive decision-making at large conglomerates like John Keells Holdings or MAS Holdings.
- **Postgraduate Study:** Graduates frequently pursue an MBA or a Master’s in IT Management to accelerate their path into C-suite roles (CIO/CTO) or pursue research-based M.Sc./Ph.D. degrees locally or abroad.

---

## Entry Requirements

Admission is strictly through the University Grants Commission (UGC) based on G.C.E. Advanced Level results in the Physical Science stream. Candidates must have achieved high Z-scores, as this is one of the most competitive programs in the country. In addition to A/L results, applicants must pass a mandatory Aptitude Test conducted by the University of Moratuwa, which evaluates logical reasoning, analytical skills, and basic IT knowledge. The medium of instruction is English.

---

## Differences Between Universities

This programme is currently offered exclusively at the University of Moratuwa. Its uniqueness lies in its location within the Faculty of Information Technology, which provides students with access to state-of-the-art labs, a strong alumni network, and deep-rooted industry links with the nearby Katubedda and Colombo tech hubs.

---

## Special Notes

- **Professional Recognition:** The degree is highly regarded by industry bodies. Graduates are often eligible for exemptions in professional accounting and management certifications.
- **Aptitude Test:** The aptitude test is a critical component of the selection process. Students should monitor the official University of Moratuwa website closely following the release of A/L results for registration deadlines.
- **Industrial Training:** The mandatory industrial training component is a hallmark of the Moratuwa experience, often leading to direct job offers before graduation.
- **Gender Diversity:** The Faculty of Information Technology actively encourages female participation in this degree, noting that the blend of management and IT is an excellent pathway for women to enter leadership roles in the tech industry.', 'c223fbf666d40f9ee52678b950a71cc266ea9e8822b2a097aeb1513fb781d1e9');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('092', '# Tourism and Hospitality Management (B.Sc.)
**Course Number:** 092
**Degree:** Bachelor of Science (Honours) in Tourism and Hospitality Management
**Duration:** 4 years
**Entry Stream:** Commerce, Arts
**Available at:** Sabaragamuwa University Faculty of Management Studies, Department of Tourism Management (092A), Rajarata University Faculty of Management Studies, Department of Tourism Management (092B)

---

## Overview

Tourism and Hospitality Management at Sabaragamuwa and Rajarata universities provides students from the Sabaragamuwa (Belihuloya campus) and North Central (Anuradhapura campus) provinces with access to professional tourism education. Both locations are strategically positioned near Sri Lanka''s most important cultural heritage and nature-based tourism zones — Sabaragamuwa near Adam''s Peak and Ratnapura gem mining; Rajarata near the Cultural Triangle (Anuradhapura, Polonnaruwa, Sigiriya, Dambulla).

The programme trains students for careers in hotel management, tour operations, eco-tourism, heritage tourism management, and government tourism administration.

---

## What You Will Study

**Year 1 — Tourism Fundamentals:**
Introduction to Tourism and Hospitality, Hotel Operations, Tourism Geography of Sri Lanka, Business Communication and English, Economics of Tourism.

**Year 2 — Business and Management:**
Tourism Marketing, Food and Beverage Management, Tour Operations and Travel Agency Management, Sustainable Tourism Principles, Research Methods.

**Year 3 — Applied Tourism:**
Heritage Tourism Management, Community-Based Tourism, Eco-Tourism and Responsible Tourism, Tourism Policy and Planning, Events Management, Industrial Training in a hotel or tourism organization.

**Year 4 — Research:**
Research Dissertation on a tourism topic, Strategic Tourism Management, Digital Tourism and E-Marketing, Tourism Entrepreneurship.

---

## Career Paths in Sri Lanka

- **Heritage site management:** Sites near both campuses — Anuradhapura, Sigiriya, Polonnaruwa, Adam''s Peak, Ratnapura gem tourism — provide direct employment opportunities in tourism management.
- **Hotel and resort management:** Management trainee programmes at hotels near their respective campuses and nationally.
- **Government:** SLTDA, provincial tourism development bodies, municipal tourism offices.
- **Eco-tourism ventures:** Community tourism, national park visitor centres, wildlife safari operations.
- **Tour operations:** Guiding, tour planning, ground operations for inbound tourism.
- **Entrepreneurship:** Running guesthouses, holiday villas, eco-lodges, or tour operations — especially relevant for students from tourism-rich areas.

---

## Entry Requirements

**A/L Stream:** Commerce (primary), Arts
**Z-score context:** Cutoffs typically in the **0.4 to 0.8** range — accessible to most Commerce and Arts students. These programmes specifically serve students from Sabaragamuwa and North Central provinces.

---

## Special Notes

- Location is a distinctive feature — Sabaragamuwa campus is in the tea-country/highland region, Rajarata campus is adjacent to the ancient cultural triangle.
- English communication skills are important — tourism is an international industry.
- Both universities are smaller and offer a more intimate campus experience than the large national universities.
', '6408f8310f4166fc6c1d7c703a9232076ac692a56d69a7a0c27f17b9c16011bc');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('093', '# Agricultural Resource Management and Technology
**Course Number:** 093
**Degree:** Bachelor of Science (Honours) in Agricultural Resource Management and Technology
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Ruhuna (093F)

---

## Overview

The Bachelor of Science (Honours) in Agricultural Resource Management and Technology (ARMT) is a specialized degree program designed to bridge the gap between traditional agricultural practices and modern technological advancements. In the Sri Lankan context, where agriculture remains a cornerstone of the national economy, this degree focuses on the sustainable management of natural resources, precision farming, and the integration of engineering solutions to enhance food security and rural productivity.

The program is hosted by the Faculty of Agriculture at the University of Ruhuna, a premier institution located in Mapalana, Kamburupitiya. The faculty is renowned for its strong emphasis on field-based learning and its deep-rooted connections with the Southern Province’s diverse agricultural landscape, ranging from tea and rubber plantations to paddy cultivation and modern greenhouse operations. Students benefit from the university''s proximity to various agro-ecological zones, providing a unique living laboratory for resource management studies.

---

## What You Will Study

**Year 1: Foundation in Agricultural Sciences**
Focuses on core sciences including Agricultural Biology, Chemistry, Soil Science, and an introduction to Agricultural Engineering. Students also study basic Mathematics, Statistics, and Information Technology to build a quantitative foundation.

**Year 2: Resource Management and Systems**
Deep dives into Soil and Water Resources Management, Farm Power and Machinery, and Agricultural Meteorology. Students begin to understand the physical and chemical properties of land and water and how they interact with modern farming equipment.

**Year 3: Advanced Technology and Applications**
Covers specialized areas such as Precision Agriculture, Protected Agriculture (Greenhouse technology), Irrigation Engineering, and Post-harvest Technology. Students learn to apply GIS (Geographic Information Systems) and Remote Sensing to monitor crop health and land use.

**Year 4: Professional Practice and Research**
The final year is dedicated to the Industrial Training program, where students work in private or public sector organizations to gain hands-on experience. This is complemented by a mandatory Independent Research Project (Dissertation), where students conduct original research on a specific agricultural resource or technological challenge.

---

## Career Paths in Sri Lanka

*   **Agricultural Engineer/Consultant:** Working with firms like Hayleys Agriculture or CIC Agribusiness to design irrigation systems, farm layouts, and mechanized processing units.
*   **Resource Management Specialist:** Employed by the Department of Agriculture or the Mahaweli Authority to manage water distribution, soil conservation projects, and land-use planning.
*   **Precision Farming Manager:** Leading high-tech greenhouse operations or large-scale commercial farms that utilize IoT, drones, and automated climate control systems.
*   **Extension Officer:** Working with the government or NGOs (like CARE or local rural development agencies) to train farmers on sustainable resource utilization and modern technology adoption.
*   **Research Scientist:** Conducting R&D at institutions like the Hector Kobbekaduwa Agrarian Research and Training Institute (HARTI) or the Rubber/Tea Research Institutes.
*   **Postgraduate Study:** Graduates are well-positioned for M.Sc. or Ph.D. programs in Environmental Science, Agricultural Engineering, or Climate Change Adaptation at local universities (e.g., Peradeniya, Ruhuna) or international institutions.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results in the Biological Science stream. Candidates must have passed all three subjects in one sitting. The selection is highly competitive and is based on the Z-score system determined by the University Grants Commission (UGC). The medium of instruction is English, and students are expected to have a strong command of the language to engage with technical literature and research. No specific physical requirements are mandated, but students should be prepared for frequent field visits and outdoor practical work in various climatic conditions.

---

## Differences Between Universities

The BSc (Honours) in Agricultural Resource Management and Technology is currently offered exclusively by the University of Ruhuna. This uniqueness allows the Faculty of Agriculture at Ruhuna to maintain a highly specialized curriculum that is deeply integrated with the specific agricultural challenges of the Southern and Uva provinces. Unlike general agriculture degrees, this program is distinct in its heavy focus on the engineering and technological aspects of resource management, making it a niche and highly sought-after qualification for students interested in the intersection of technology and land-based industries.

---

## Special Notes

Graduates of this program are eligible for professional recognition within the agricultural sector. While this is not an engineering degree in the IESL (Institution of Engineers, Sri Lanka) sense, it is highly respected in the agro-industrial sector. The degree is fully recognized for government sector employment (Sri Lanka Agricultural Service). Students are encouraged to develop proficiency in software tools like AutoCAD, ArcGIS, and statistical packages (e.g., SAS, R) during their undergraduate years, as these are highly valued by employers. Overseas employment demand is growing for graduates with expertise in precision agriculture and sustainable irrigation management, particularly in the Middle East and Australia.', '0c9181d99cb5504df78ab2843a0946158057a2ce9e64dd3d9121599bf9914e62');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('094', '# Agribusiness Management
**Course Number:** 094
**Degree:** Bachelor of Science (Honours) in Agribusiness Management
**Duration:** 4 years
**Entry Stream:** Bio Systems Technology or Biological Science (A/L)
**Available at:** University of Ruhuna (094F)

---

## Overview

Agribusiness Management is a specialized multidisciplinary degree that bridges the gap between agricultural production and the commercial business sector. In the Sri Lankan context, where agriculture remains a cornerstone of the national economy, this degree is vital for transforming traditional farming into a modern, profit-oriented, and sustainable industry. It focuses on the economic principles, supply chain logistics, and management strategies required to navigate the complexities of local and global food markets.

The University of Ruhuna, located in the Southern Province, provides a unique advantage for this programme due to its proximity to major agricultural hubs, export processing zones, and the Hambantota International Port. The curriculum is designed to produce graduates who can lead in corporate agricultural firms, government policy-making bodies, and entrepreneurial ventures, ensuring food security and economic growth in Sri Lanka.

---

## What You Will Study

**Year 1: Foundations of Agriculture and Business**
Focuses on the basics of agricultural sciences, micro and macroeconomics, principles of management, accounting, and business mathematics. Students are introduced to the agricultural environment in Sri Lanka.

**Year 2: Applied Management and Economics**
Covers agricultural marketing, farm management, financial management, business law, and statistics. Students begin to analyze the economic behavior of agricultural producers and consumers.

**Year 3: Advanced Agribusiness Operations**
Explores supply chain management, international trade, human resource management, project appraisal, and agricultural policy. Students engage in field visits to observe real-world agribusiness operations.

**Year 4: Specialization and Research**
The final year focuses on strategic management, entrepreneurship, and specialized electives. Students must complete an independent research project (dissertation) and a professional industrial training placement, applying theoretical knowledge to solve practical problems in the industry.

---

## Career Paths in Sri Lanka

*   **Agribusiness Manager:** Managing large-scale plantations or food processing firms like CIC Agribusinesses or Hayleys Agriculture. Work involves overseeing production cycles, supply chains, and profitability.
*   **Agricultural Policy Analyst:** Working with the Ministry of Agriculture or the Department of National Planning to formulate strategies for food security and rural development.
*   **Supply Chain Coordinator:** Managing logistics for export-oriented companies (e.g., tea, spices, or fruit exporters). Involves coordinating between farmers, warehouses, and shipping ports.
*   **Financial Consultant for Agriculture:** Providing credit analysis and risk assessment for banks like the Bank of Ceylon or People’s Bank, focusing on agricultural loan portfolios.
*   **Entrepreneur/Agri-Tech Founder:** Starting independent ventures in organic farming, value-added food processing, or digital agricultural platforms.
*   **Postgraduate Study:** Graduates can pursue M.Sc. or Ph.D. programmes in Agricultural Economics, Development Studies, or MBA programmes at institutions like the University of Colombo or the Postgraduate Institute of Agriculture (PGIA), Peradeniya.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results. Candidates must have passed the A/L examination in the Bio Systems Technology or Biological Science stream. Selection is highly competitive and is determined by the Z-score system managed by the University Grants Commission (UGC). The medium of instruction is English, and students are expected to have a strong command of the language to engage with technical literature and business reports.

---

## Differences Between Universities

While the University of Ruhuna is the primary provider for this specific degree code, students should note that the Faculty of Agriculture at Ruhuna is distinguished by its strong research focus on tropical agriculture and its strategic location in the Southern Province. The faculty maintains close links with the regional agricultural industry, providing students with unique access to field-based learning and internships that may differ from the more inland-focused agricultural programmes in other parts of the country.

---

## Special Notes

Graduates of this programme are eligible for professional membership in various agricultural and management associations in Sri Lanka. While there is no mandatory licensing required to practice, the degree is highly valued by the private sector for its blend of technical agricultural knowledge and business acumen. There is significant demand for these graduates in the Middle East and developed markets for roles in food safety, quality control, and international trade. Students are encouraged to develop proficiency in data analysis software (such as SPSS or Stata) during their studies, as this is a highly sought-after skill in the modern agribusiness sector.', 'be409d16f92707aadf7700ab9820f591d70674be77c059455f996bbd04a566e7');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('095', '# Green Technology
**Course Number:** 095
**Degree:** Bachelor of Science (Honours) in Green Technology
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Ruhuna (095F)

---

## Overview

The Bachelor of Science in Green Technology is a specialized undergraduate programme designed to address the growing global and local demand for sustainable development and environmental stewardship. In the Sri Lankan context, where the economy is heavily reliant on agriculture and natural resources, this degree provides the technical expertise required to transition toward a circular economy, renewable energy integration, and climate-resilient industrial practices.

The programme is hosted by the Faculty of Agriculture at the University of Ruhuna, a premier institution known for its strong research culture and industry-aligned curriculum. Students benefit from the university’s strategic location in the Southern Province, which serves as a living laboratory for studying coastal ecosystems, sustainable plantation management, and renewable energy pilot projects. This degree is vital for graduates aiming to lead the "Green Revolution" in Sri Lanka, bridging the gap between traditional agricultural practices and modern technological innovation.

---

## What You Will Study

**Year 1: Foundations of Science and Sustainability**
Focuses on core biological and physical sciences, including Principles of Green Technology, Environmental Chemistry, Mathematics for Life Sciences, and Introduction to Sustainable Development.

**Year 2: Core Technical Competencies**
Deepens knowledge in Renewable Energy Systems (Solar, Wind, and Biomass), Soil and Water Conservation, Environmental Microbiology, and Sustainable Agricultural Practices. Students begin learning about resource efficiency and waste management.

**Year 3: Applied Green Technologies**
Advanced modules covering Climate Change Adaptation, Green Engineering, Precision Agriculture, Environmental Impact Assessment (EIA), and Energy Auditing. Students engage in field-based practicals and industrial site visits.

**Year 4: Specialization and Research**
The final year focuses on professional application. Students undertake a mandatory industrial training placement and a comprehensive independent research project (dissertation). Elective modules allow for specialization in areas such as Bio-energy, Sustainable Supply Chain Management, or Environmental Policy.

---

## Career Paths in Sri Lanka

*   **Environmental Consultant:** Working with firms like the Central Environmental Authority (CEA) or private consultancy firms to conduct EIAs and ensure corporate compliance with environmental regulations.
*   **Renewable Energy Project Manager:** Overseeing solar, wind, or biomass energy projects for companies like the Ceylon Electricity Board (CEB) or private sector renewable energy developers.
*   **Sustainable Agriculture Specialist:** Implementing precision farming and resource-efficient techniques for large-scale plantations (e.g., Hayleys Agriculture, Dilmah Tea) to improve yields while reducing environmental footprints.
*   **Waste Management Specialist:** Designing and managing waste-to-energy or recycling systems for municipal councils or private waste management enterprises.
*   **Sustainability Auditor:** Working with manufacturing and export industries to achieve ISO 14001 certification and carbon footprint reduction targets.
*   **Postgraduate Research:** Pursuing M.Sc. or Ph.D. programmes in Environmental Science, Climate Change, or Renewable Energy at institutions like the University of Peradeniya or overseas universities.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level Examination in the Biological Science stream. Candidates must have passed Chemistry, Biology, and Physics (or an approved third subject). The programme is highly competitive, and selection is based on the Z-score determined by the University Grants Commission (UGC). The medium of instruction is English, and students are expected to have a strong command of the language for technical reporting and research.

---

## Differences Between Universities

This programme is currently offered exclusively at the University of Ruhuna. As the sole provider of this specific degree, the Faculty of Agriculture at Ruhuna maintains strong links with the Southern Province’s industrial and agricultural sectors, providing students with unique access to field research sites that are not available in urban-based universities.

---

## Special Notes

Graduates of this programme are well-positioned to contribute to national sustainability goals, such as the transition to 70% renewable energy by 2030. While there is no specific professional licensing body like the IESL for this degree, graduates are eligible for membership in various environmental and agricultural professional associations. The degree provides a strong foundation for international careers in the growing global "Green Economy," particularly in the Middle East and Southeast Asia, where sustainability expertise is in high demand. Students are encouraged to develop proficiency in data analysis software and GIS (Geographic Information Systems) during their studies to enhance their employability.', '553f5a9e8325c6a9a4d4692856ffd900dbf3b0f1331642eba2dffc1eb2a37f6b');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('096', '# Information Systems (B.Sc.)
**Course Number:** 096
**Degree:** Bachelor of Science (Honours) in Information Systems
**Duration:** 4 years
**Entry Stream:** Physical Science, Biological Science (some intakes)
**Available at:** University of Colombo School of Computing — UCSC (096A), University of Sri Jayewardenepura Faculty of Computing (096B)

---

## Overview

Information Systems (IS) bridges computing and business. While Computer Science focuses on algorithms and computation, Information Systems focuses on how technology is used to solve business problems — databases, enterprise systems, business analytics, IT governance, and digital transformation. IS graduates are equally comfortable in a tech team or a management boardroom.

UCSC offers both Computer Science (012A) and Information Systems (096A), making it a dual-programme computing institution — the most prestigious computing school in Sri Lanka.

---

## What You Will Study

**Year 1 — Computing and Business Foundations:**
Programming, Database Fundamentals, Business Information Systems, Systems Thinking, Web Technologies, Business Communication, Quantitative Methods.

**Year 2 — Information Systems Core:**
Database Design and Management, Systems Analysis and Design, Business Process Management, Organizational Behaviour, IT Project Management, Accounting Information Systems, E-Business.

**Year 3 — Applied IS:**
Enterprise Systems (ERP: SAP, Oracle), Data Warehousing and Business Intelligence, Information Security Management, IT Governance (COBIT, ITIL), Digital Marketing, Decision Support Systems, Industrial Training.

**Year 4 — Specialization:**
Research Project, Advanced Analytics, Knowledge Management, IS Strategy and Leadership, Digital Transformation Electives.

---

## Career Paths in Sri Lanka

- **Business analyst:** Bridging technical and business teams in software projects — one of the most in-demand roles in Sri Lanka''s IT and BPO sector.
- **Systems analyst:** Designing IT solutions for organizational needs.
- **Database administrator:** Managing relational databases (Oracle, MS SQL, PostgreSQL) for enterprises.
- **IT manager:** Managing IT departments in banks, insurance, telecoms, and manufacturing.
- **ERP consultant:** SAP and Oracle ERP implementation at consulting firms.
- **Business intelligence:** Data analysis and reporting using Power BI, Tableau, SQL.
- **E-commerce and digital business:** Digital transformation roles at retail, banking, and FMCG companies.
- **IT auditor:** Reviewing IT controls and compliance (a growing area in regulated industries).

---

## Entry Requirements

**A/L Stream:** Physical Science (primary); some intakes accept Biological Science
**Required subjects:** Combined Mathematics + Physics + Chemistry (Physical Science)

**Z-score context:** Information Systems at UCSC (096A) has cutoffs similar to Computer Science at UCSC — typically **1.2 to 1.7**. USJ IS (096B) is somewhat lower. Both are competitive but offer access to UCSC''s strong reputation and industry network.

---

## Special Notes

- The IS degree is ideal for students who enjoy both technology and business, as it opens doors in both sectors.
- UCSC''s IS programme has the same 90% employability rate as its CS programme, reflecting strong industry demand.
- Professional certifications (PMP for project management, CISA for IT audit, ITIL for service management) complement the IS degree and are common among IS graduates.
', '636d5cd83c013a7489ffcb3754a917e3a0236756aeeb4cd80c59db1bad1cf918');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('097', '# Landscape Architecture (B.L.Arch.)
**Course Number:** 097
**Degree:** Bachelor of Landscape Architecture (B.L.Arch. Honours)
**Duration:** 4 years
**Entry Stream:** Physical Science, Engineering Technology
**Available at:** University of Moratuwa Department of Architecture (097A)

---

## Overview

Landscape Architecture is a creative and environmental profession concerned with the design of outdoor spaces — parks, gardens, streetscapes, campuses, resort grounds, ecological corridors, and urban green infrastructure. Landscape Architects work at the intersection of ecology, design, engineering, and social science to create functional and beautiful outdoor environments.

The University of Moratuwa is the sole state-university provider of this degree in Sri Lanka.

**Note:** Landscape Architecture may require an aptitude test similar to Architecture. Students should verify with the faculty before applying.

---

## What You Will Study

**Year 1 — Design and Ecology Foundations:**
Landscape Design Drawing, Ecological Principles, Botany for Landscape Design (plant identification, plant communities), Surveying and Land Measurement, Introduction to Landscape Architecture, History of Gardens and Landscapes.

**Year 2 — Core Landscape Practice:**
Site Analysis and Planning, Planting Design (tree, shrub, groundcover selection and arrangement), Landscape Construction (hard landscape — paving, walls, water features; soft landscape — lawns, planting), Landscape Architecture History, Climate and Microclimate Design, Environmental Impact Assessment.

**Year 3 — Complex Projects:**
Urban Landscape Design (public parks, streetscapes, waterfronts), Site Engineering (grading, drainage, stormwater management), Sustainable Landscape Design (green roofs, rain gardens, ecological landscaping), Research Methods, Professional Practice.

**Year 4 — Thesis:**
Individual Landscape Architecture Thesis — major design project on a chosen site and programme, Portfolio development, Professional registration preparation.

---

## Career Paths in Sri Lanka

- **Government:** Urban Development Authority (UDA), National Physical Planning Department, Central Province Development Authority — landscape planning for urban and regional projects.
- **Parks and recreation:** Municipal councils, national parks, botanical gardens (Peradeniya, Hakgala, Henarathgoda).
- **Resort and hospitality industry:** Hotel groups (Jetwing, Aitken Spence, John Keells Hotels) invest heavily in landscape design for resort grounds.
- **Private landscape design:** Residential garden design, commercial landscape maintenance contracts.
- **Environmental consulting:** Green building certification (LEED), ecological restoration projects.
- **Port City Colombo:** Large-scale urban design and public realm landscape projects.
- **International:** Singapore, Dubai, Australia — all have active landscape architecture professions.
- **Architecture and engineering firms:** Many firms employ Landscape Architects as part of integrated project teams.

---

## Entry Requirements

**A/L Stream:** Physical Science (primary), Engineering Technology
**Required subjects:** Combined Mathematics + Physics + Chemistry

**Z-score context:** Landscape Architecture at Moratuwa has cutoffs typically in the **1.1 to 1.6** range — somewhat more accessible than Architecture (023).

---

## Special Notes

- Interest in plants, outdoor environments, ecology, and design are essential qualities for this profession.
- Sri Lanka''s rapid urbanization creates significant landscape design work — greening of urban spaces, river corridor restoration, and public park development are growing areas.
- The degree is conducted in English.
', '296dbb3e206b26e20cf8859b820fbe3e7e0dde8525f3df1be9f834d49d4a1811');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('098', '# Translation Studies
**Course Number:** 098
**Degree:** Bachelor of Arts (Honours) in Translation Studies
**Duration:** 4 years
**Entry Stream:** Arts Stream (All subjects)
**Available at:** University of Kelaniya (098D), University of Jaffna (098E), Eastern University, Sri Lanka (098H), Sabaragamuwa University of Sri Lanka (098L)

---

## Overview

Translation Studies is a specialized academic discipline that bridges the linguistic and cultural gaps in Sri Lanka’s trilingual society. As the nation moves toward greater integration, the demand for professionals who can accurately translate and interpret between Sinhala, Tamil, and English has become critical for governance, legal proceedings, and international business.

This degree programme is designed to move beyond simple bilingualism; it focuses on the theories of translatology, cross-cultural communication, and the technical nuances of professional translation. By studying at institutions like the University of Kelaniya or the University of Jaffna, students gain exposure to the practical challenges of working in a post-conflict, developing nation, preparing them for roles that require high levels of ethical responsibility and linguistic precision.

---

## What You Will Study

**Year 1: Foundations of Language and Linguistics**
Focuses on core linguistic theory, advanced grammar in two target languages (e.g., Sinhala/English or Tamil/English), introduction to the history of translation, and basic communication skills.

**Year 2: Translation Theory and Methodology**
Explores the theoretical frameworks of translation, comparative linguistics, and the study of sociolinguistics. Students begin practical translation exercises focusing on general texts, media, and basic administrative documents.

**Year 3: Specialized Translation and Technology**
Students delve into technical, legal, and literary translation. This year introduces Computer-Assisted Translation (CAT) tools, terminology management, and interpreting techniques (consecutive and simultaneous).

**Year 4: Professional Practice and Research**
The final year involves an internship programme in a professional setting, a comprehensive research dissertation, and advanced modules in professional ethics, project management for translators, and specialized fields like medical or diplomatic translation.

---

## Career Paths in Sri Lanka

*   **Government Translator/Interpreter:** Working for the Department of Official Languages or various ministries. Involves translating gazettes, legal documents, and providing interpretation for official state functions.
*   **Legal/Court Interpreter:** Employed by the Ministry of Justice. Involves facilitating communication in courtrooms between judges, lawyers, and non-native speakers of the court language.
*   **Corporate Communications Specialist:** Working for multinational corporations (e.g., MAS Holdings, John Keells Group). Involves localizing marketing materials, internal policies, and business correspondence.
*   **Media and Publishing Translator:** Working with local media houses (e.g., Wijeya Newspapers, ITN). Involves translating news reports, subtitles for television, and literary works.
*   **International NGO/Diplomatic Liaison:** Working with organizations like the UN, UNDP, or foreign embassies in Colombo. Involves facilitating communication for development projects and diplomatic missions.
*   **Postgraduate Study:** Graduates can pursue a Master of Arts in Linguistics, International Relations, or specialized Translation and Interpreting studies to move into academic or high-level consultancy roles.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Arts stream. Candidates must demonstrate high proficiency in at least two of the three national languages (Sinhala, Tamil, English). Most universities require candidates to pass an additional Aptitude Test specifically designed to assess linguistic competence and translation potential. The Z-score requirement is generally competitive, reflecting the limited intake capacity of these specialized departments.

---

## Differences Between Universities

*   **University of Kelaniya:** Known for a strong focus on modern linguistic research and a well-established Faculty of Humanities with extensive industry links in the corporate sector.
*   **University of Jaffna:** Offers a unique advantage in Tamil-English-Sinhala trilingual immersion, with a strong focus on the practical needs of the Northern region and legal translation.
*   **Eastern University, Sri Lanka:** Emphasizes community-based translation and the socio-cultural aspects of language in the Eastern province.
*   **Sabaragamuwa University of Sri Lanka:** Features a robust Department of Languages with a curriculum that balances theoretical translatology with field-based practical training in the Sabaragamuwa region.

---

## Special Notes

Graduates are eligible to apply for registration as Sworn Translators through the Ministry of Justice, which is a mandatory requirement for certifying legal documents in Sri Lanka. While there is no singular professional body like the IESL for translators, membership in professional language associations is highly recommended for career advancement. The degree is highly valued for overseas employment, particularly in countries with large Sri Lankan diaspora communities or international organizations requiring multilingual staff. Instruction is primarily in the chosen language pairs, with English often serving as the bridge language for theoretical modules.', '1e40158f2666118589308361c6f1ceac7dcfdec9e341ecab85f1510f448fa01f');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('099', '# Software Engineering (B.Sc.)
**Course Number:** 099
**Degree:** Bachelor of Science (Honours) in Software Engineering
**Duration:** 4 years
**Entry Stream:** Physical Science, Engineering Technology
**Available at:** University of Sri Jayewardenepura Faculty of Computing (099A), University of Kelaniya Faculty of Computing and Technology (099B)

---

## Overview

Software Engineering is one of the fastest-growing degree programmes in Sri Lanka, reflecting the enormous demand for software professionals in Sri Lanka''s IT industry. Unlike Computer Science which emphasizes theoretical computing, Software Engineering focuses on the systematic process of designing, developing, testing, and maintaining large-scale software systems.

Software Engineering graduates are directly aligned with industry demands — many enter employment before graduation through internship placements, and starting salaries are among the highest of all university graduates.

---

## What You Will Study

**Year 1 — Foundations:**
Programming (Python, Java, C++), Discrete Mathematics, Data Structures and Algorithms, Database Systems, Software Engineering Principles, Web Development, Technical Writing.

**Year 2 — Engineering Process:**
Object-Oriented Design and Analysis, Software Architecture, Operating Systems, Computer Networks, Requirements Engineering, Software Testing and Quality Assurance, Agile and Scrum Methodologies.

**Year 3 — Advanced Software Engineering:**
Software Project Management, Distributed Systems, Cloud Application Development, Mobile Software Engineering, DevOps and Continuous Integration, Cybersecurity for Software Engineers, UI/UX Design, Industrial Training.

**Year 4 — Specialization and Capstone:**
Group Capstone Software Project (full software development lifecycle), Research Project, Electives in AI/ML Engineering, Blockchain Development, IoT Software, Enterprise Architecture.

---

## Career Paths in Sri Lanka

- **Software developer / engineer:** The primary role. Frontend, backend, full-stack, mobile — all forms of software development at Sri Lankan and international companies.
- **DevOps engineer:** Automation, CI/CD pipelines, cloud infrastructure management.
- **QA engineer:** Test automation, performance testing, software quality assurance — every major software company needs QA engineers.
- **Software architect:** Senior role designing system architecture for complex software products.
- **Startup founder:** Software Engineering gives the technical skills to build technology products from scratch.
- **International tech companies:** Google, Microsoft, Amazon, Meta, and others recruit Sri Lankan Software Engineers. Many graduates migrate to or work remotely for international tech companies.
- **Fintech:** Growing sector in Sri Lanka — digital payment platforms, mobile banking, insurance tech.

---

## Entry Requirements

**A/L Stream:** Physical Science (primary), Engineering Technology
**Required subjects:** Combined Mathematics + Physics + Chemistry (Physical Science)

**Z-score context:** Software Engineering at SJP and Kelaniya has cutoffs typically **1.0 to 1.5** — competitive but more accessible than Computer Science at UCSC or Engineering at Moratuwa. A strong choice for students who just miss their first-preference computing programmes.

---

## Special Notes

- English is the medium of instruction.
- Industrial training is compulsory, typically in Year 3.
- Software Engineering graduates at Sri Lankan companies earn starting salaries of LKR 60,000–120,000+/month, rising rapidly with experience.
- The degree qualifies for IESL membership (Software Engineering category).
', '56470cd07596c84d639bbbf7ede1f8741f4f20e80d89bd727752d8059a3fabe1');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('100', '# Film & Television Studies
**Course Number:** 100
**Degree:** Bachelor of Arts (Honours) in Film & Television Studies
**Duration:** 4 years
**Entry Stream:** Arts Stream
**Available at:** University of Kelaniya (100D)

---

## Overview

The Bachelor of Arts (Honours) in Film & Television Studies is a specialized degree designed to bridge the gap between theoretical cinematic discourse and practical media production. In the context of Sri Lanka’s burgeoning creative economy, this degree is vital for students aiming to professionalize their craft in an industry that is increasingly shifting toward digital-first storytelling, high-end television production, and global content distribution.

The University of Kelaniya, through its Drama & Theatre and Image Arts Unit, is a pioneer in this field. The programme is notable for its rigorous academic foundation, which encourages students to analyze the socio-political impact of visual media while simultaneously mastering the technical tools required for professional production. Graduates are equipped to navigate the unique landscape of Sri Lankan cinema, television broadcasting, and the digital advertising sector.

---

## What You Will Study

**Year 1: Foundations of Visual Language**
Focuses on the core principles of aesthetics and technical basics. Subjects include Theory and Techniques of Photography, The Language of Film, Computer Technology for Image Arts, Lighting Techniques, and Fundamentals of Aesthetics.

**Year 2: Narrative and Technical Proficiency**
Students delve into the mechanics of storytelling and advanced production. Key areas include Screenwriting, Cinematography, Sound Design for Film, Film History (Global and Sri Lankan), and Digital Editing workflows.

**Year 3: Specialization and Production**
Students choose between tracks such as Documentary Production, Fiction Filmmaking, or Television Studio Production. Coursework includes Directing, Advanced Production Management, Media Law and Ethics, and Visual Effects (VFX) basics.

**Year 4: Professional Application and Research**
The final year is dedicated to the Dissertation and a Final Year Production Project. Students must produce a substantial creative work (short film, documentary, or television pilot) accompanied by a research thesis that contextualizes their work within contemporary media studies.

---

## Career Paths in Sri Lanka

*   **Cinematographer/Director of Photography:** Working with production houses like Dil Films or independent cinema projects; involves planning lighting, camera movement, and visual composition.
*   **Television Producer:** Working for major networks like Sirasa TV, Derana, or Swarnavahini; involves managing production schedules, budgets, and creative content for daily programming.
*   **Film Editor/Post-Production Specialist:** Working in boutique post-production studios in Colombo; involves non-linear editing, color grading, and sound mixing for commercials and feature films.
*   **Screenwriter/Script Consultant:** Freelance or agency-based work; involves drafting scripts for teledramas, web series, and advertising campaigns.
*   **Media Educator/Academic:** Working at vocational training institutes or universities; involves teaching media literacy and technical production skills to the next generation.
*   **Postgraduate Study:** Students may pursue an M.A. or M.Phil. in Mass Communication, Theatre Arts, or International Film Studies at local universities or abroad to transition into research or high-level academic roles.

---

## Entry Requirements

Admission is open to students from the Arts stream. Candidates must have passed the GCE A/L examination with the required subject combinations. Because this is a specialized creative degree, all applicants must pass a mandatory **Aptitude Test** conducted by the University of Kelaniya, which evaluates creative potential, visual literacy, and analytical thinking. The Z-score requirement is generally competitive, reflecting the limited intake and high demand for this specialized programme. The medium of instruction is primarily Sinhala, with academic materials and technical terminology often provided in English.

---

## Differences Between Universities

The Bachelor of Arts (Honours) in Film & Television Studies is currently offered exclusively at the University of Kelaniya (100D). Unlike general Mass Communication degrees offered at other state universities, this programme is uniquely housed within the Drama & Theatre and Image Arts Unit. This provides a distinct advantage: students are immersed in a "studio-culture" environment where the focus is heavily weighted toward artistic expression and practical filmmaking rather than purely theoretical media studies.

---

## Special Notes

*   **Aptitude Test:** The aptitude test is the most critical component of the selection process. Students should prepare by building a portfolio of creative work or demonstrating a deep interest in film history and visual arts.
*   **Professionalism:** While there is no formal "licensing" body like the IESL or SLMC for filmmakers, the industry in Sri Lanka is highly network-driven. Participation in student film festivals and internships during the degree is essential for career placement.
*   **Equipment Access:** Students are expected to engage with the university’s technical facilities, but they are encouraged to invest in personal hardware (laptops capable of video editing) to facilitate their independent projects.
*   **Global Demand:** The skills acquired are highly transferable to the international gig economy, particularly in freelance video editing, motion graphics, and remote production support for global media platforms.', '63b27863a373d1f316870b7b5c8c74aa3ecdf65cede27a4b0b709ae54f811c34');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('101', '# Project Management
**Course Number:** 101
**Degree:** Bachelor of Business Management (Honours) in Project Management
**Duration:** 4 years
**Entry Stream:** Commerce, Arts, or Physical Science streams
**Available at:** University of Vavuniya, Sri Lanka (101R)

---

## Overview

The Bachelor of Business Management in Project Management is a specialized degree designed to equip students with the strategic, operational, and leadership skills required to manage complex projects across diverse sectors. In the Sri Lankan context, where large-scale infrastructure, IT outsourcing, and development projects are central to economic growth, this degree fills a critical gap for professionals who can bridge the divide between high-level planning and on-the-ground execution.

The Faculty of Business Studies at the University of Vavuniya is notable for its proactive engagement with the industry, hosting dedicated project management clusters and field-based learning opportunities. By focusing on the unique challenges of the Sri Lankan market—such as resource constraints, regulatory compliance, and stakeholder management—the programme ensures graduates are ready to contribute immediately to the nation’s development goals.

---

## What You Will Study

**Year 1: Foundations of Management**
Focuses on the core principles of business, including Economics, Accounting, Business Mathematics, Management Theory, and Business Communication. Students gain a baseline understanding of how organizations function.

**Year 2: Project Management Fundamentals**
Introduces the project lifecycle, project planning, scheduling techniques, and cost estimation. Core subjects include Organizational Behavior, Marketing Management, and Introduction to Project Management tools and software.

**Year 3: Advanced Methodologies and Specialization**
Deep dives into specialized areas such as Risk Management, Procurement and Contract Management, Agile Methodologies, and Human Resource Management. Students learn to apply quantitative methods to project decision-making.

**Year 4: Strategic Application and Research**
Focuses on high-level strategy, including Project Portfolio Management, Quality Management, and Corporate Social Responsibility. The year culminates in an Independent Research Project or a comprehensive industry-based internship, allowing students to apply theoretical frameworks to real-world Sri Lankan business problems.

---

## Career Paths in Sri Lanka

*   **Project Coordinator (Construction/Infrastructure):** Working with firms like Maga Engineering or Access Engineering to track daily site progress, manage documentation, and ensure schedule adherence.
*   **IT Project Associate (Software Development):** Supporting software houses in Colombo (e.g., Virtusa, IFS) by managing sprint backlogs, tracking developer output, and facilitating stakeholder communication.
*   **NGO Project Officer:** Managing community development or humanitarian projects for organizations like UNDP Sri Lanka or local NGOs, focusing on budget compliance and impact reporting.
*   **Operations Analyst (Manufacturing/Logistics):** Working in the apparel or logistics sector to optimize supply chain workflows and manage internal process improvement projects.
*   **Public Sector Project Administrator:** Assisting government ministries or provincial councils in implementing state-funded development projects, ensuring adherence to government procurement guidelines.
*   **Postgraduate Study:** Graduates can pursue an MBA, a Master’s in Project Management, or professional certifications such as the PMP (Project Management Professional) or PRINCE2 to advance into senior leadership roles.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results. Students from the Commerce, Arts, or Physical Science streams are eligible to apply. Proficiency in English is essential as the medium of instruction is English. The Z-score requirement is determined annually based on the competitive pool of applicants; candidates should aim for a high Z-score to ensure placement, as this is a specialized and increasingly popular degree programme.

---

## Differences Between Universities

Currently, the Bachelor of Business Management (Honours) in Project Management is uniquely positioned at the University of Vavuniya. Unlike general management degrees offered at other national universities, this programme provides a dedicated focus on project-based learning, supported by the university''s active Project Management Club and its strong emphasis on field-based exposure in the Northern Province.

---

## Special Notes

Graduates are encouraged to seek membership with professional bodies such as the Project Management Institute (PMI) Sri Lanka Chapter to enhance their employability and networking opportunities. While the degree provides a strong academic foundation, students are highly encouraged to pursue industry-recognized certifications (like CAPM or PMP) during their final year to gain a competitive edge in the job market. The degree is fully recognized by the University Grants Commission (UGC) of Sri Lanka, ensuring eligibility for both public and private sector employment, as well as further studies at any recognized international university.', '808185f57cf5970b11ffaa313d2421842e12b47ee91d53e3e5ff648fa348be1a');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('102', '# Engineering Technology (B.ET.)
**Course Number:** 102
**Degree:** Bachelor of Engineering Technology (B.ET. Honours)
**Duration:** 4 years
**Entry Stream:** Engineering Technology (primary), Physical Science (some universities)
**Available at:** University of Colombo Faculty of Technology (102A), University of Sri Jayewardenepura Faculty of Technology (102B), University of Kelaniya Faculty of Computing and Technology (102C), University of Ruhuna Faculty of Technology (102D), University of Jaffna Faculty of Technology (102E), University of Peradeniya (102F)

---

## Overview

Engineering Technology is a practice-oriented engineering programme designed primarily for students who completed the Engineering Technology (ET) A/L stream. It is a full honours degree under SLQF Level 6, aligned with modern industry needs in manufacturing, construction, electronics, automation, and infrastructure.

While the traditional B.Sc.Eng. (Course 008) is science-intensive and research-focused, Engineering Technology emphasizes applied skills, hands-on problem-solving, and direct industry readiness. Graduates are qualified for professional engineering practice and can become chartered Engineering Technologists through IESL (Institution of Engineers Sri Lanka).

---

## What You Will Study

The curriculum varies by university but typically covers these core areas:

**Year 1 — Technology Foundations:**
Engineering Mathematics, Engineering Drawing and CAD, Materials Technology, Electrical and Electronics Technology, Workshop Practice (machining, welding, fabrication), Programming and ICT for Engineers, Technical Communication.

**Year 2 — Core Engineering Technology:**
Mechanical Technology (thermodynamics, fluid mechanics, machine elements), Electrical Systems and Power Electronics, Civil and Structural Technology, Control Systems, Manufacturing Processes, Industrial Automation and PLC Programming.

**Year 3 — Specialization:**
Students choose a specialization track depending on the university. Common tracks include:
- **Mechanical and Manufacturing:** CNC machining, robotics, product design, lean manufacturing
- **Electrical and Electronic:** Power systems, renewable energy, instrumentation, embedded systems
- **Civil and Environmental:** Construction materials, structural systems, surveying, water supply
- **ICT Engineering:** Network engineering, software systems, IoT, industrial IT

**Year 4 — Industrial Project and Advanced:**
Compulsory industrial training placement (typically 6 months), Capstone project (real industry problem solving), Project Management, Entrepreneurship and Technology Business, Professional Engineering Practice.

---

## Career Paths in Sri Lanka

- **Manufacturing industry:** Production engineers, quality engineers, process engineers, and maintenance engineers in garment, rubber, ceramic, pharmaceutical, and food manufacturing companies. This is one of the biggest employers of ET graduates.
- **Construction and building services:** Site engineers, building services engineers in electrical, HVAC, plumbing, and fire protection systems on construction projects.
- **Electrical and power industry:** CEB (Ceylon Electricity Board), LECO, and renewable energy companies for power generation, transmission, and distribution roles.
- **Automation and mechatronics:** Factory automation specialists — PLC programmers, robotics technicians, SCADA system engineers in modern manufacturing facilities.
- **Telecommunications and ICT:** Network support engineers, system engineers at Dialog Axiata, SLT Mobitel, Hutch, and IT companies.
- **Export processing zones:** BOI factories (apparel, electronics, light manufacturing) recruit ET graduates as production supervisors, technical managers, and quality inspectors.
- **Defence and government:** Sri Lanka Army, Navy, Air Force technical corps, and government technical departments (Roads, Irrigation).
- **Entrepreneurship:** Many ET graduates with practical skills establish engineering services businesses (electrical contracting, HVAC installation, construction services).
- **Postgraduate:** Can pursue M.Sc. in relevant engineering fields — either in Sri Lanka or overseas.

---

## Entry Requirements

**A/L Stream:** Engineering Technology (primary pathway); Physical Science students may also be eligible at some universities
**Required A/L subjects for ET stream:** Engineering Technology plus appropriate optional subjects

**Z-score context:** Engineering Technology is significantly less competitive than B.Sc.Eng. (Course 008). Cutoffs typically range from **0.5 to 1.2** depending on university and year, making it accessible to a wide range of ET stream students. Colombo (102A) and SJP (102B) tend to have higher cutoffs within this group.

---

## Differences Between Universities

- **Colombo (102A):** Newest Faculty of Technology, central Colombo campus, strong industry partnerships.
- **SJP (102B):** Faculty of Technology at Nugegoda, near IT and industrial corridor.
- **Kelaniya (102C):** Faculty of Computing and Technology — offers both ET and IT/computing programmes.
- **Ruhuna (102D):** Faculty of Technology, southern province campus.
- **Jaffna (102E) / Peradeniya (102F):** Regional campuses.

---

## Special Notes

- Engineering Technology is a different (and equally valid) degree to B.Sc.Eng. — both are SLQF Level 6 honours degrees and are professionally recognized.
- ET graduates can progress to IESL Engineering Technologist membership and eventually Chartered Engineer status with experience.
- The degree is well-aligned with Sri Lanka''s industrial development priorities — manufacturing, construction, and infrastructure.
- Students who entered the Engineering Technology A/L stream specifically to study engineering will find this degree more directly aligned with their school training than other programmes.
', 'd3be13768516694129b64f54ec6cc1f3e1f752637128722600f6a26ae0351887');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('103', '# Biosystems Technology (B.BST.)
**Course Number:** 103
**Degree:** Bachelor of Biosystems Technology (B.BST. Honours)
**Duration:** 4 years
**Entry Stream:** Biosystems Technology (primary), Biological Science (some universities)
**Available at:** University of Colombo Faculty of Technology (103A), University of Sri Jayewardenepura Faculty of Technology (103B), South Eastern University Faculty of Technology (103C)

---

## Overview

Biosystems Technology is a unique and forward-looking degree that applies engineering and technology principles to biological systems — in agriculture, food production, environmental management, and biotechnology. It was introduced as part of the technology faculties created for A/L students from the Biosystems Technology (BST) stream, bridging biology and applied technology.

The degree trains graduates to design and manage agricultural and biological production systems using modern technology — precision agriculture, bioprocessing, post-harvest technology, aquaculture systems, and environmental biotechnology.

---

## What You Will Study

**Year 1 — Technology and Biological Foundations:**
Engineering Mathematics, Plant and Animal Biology, Chemistry and Biochemistry, Agricultural Systems, Engineering Drawing and CAD, Introduction to Biosystems, Computing Skills.

**Year 2 — Core Biosystems:**
Soil and Water Management, Agricultural Machinery and Power Technology, Food Processing and Post-Harvest Technology, Aquaculture Systems, Controlled Environment Agriculture (greenhouse and hydroponics technology), Bioprocess Engineering (fermentation and biotechnology processes), Irrigation and Drainage Engineering.

**Year 3 — Applied Systems:**
Precision Agriculture (GPS, sensors, drones in farming), Agri-food Quality Assurance, Biorefinery and Biomass Technology, Environmental Technology (waste treatment, biogas, composting), Food Packaging Technology, Renewable Energy in Agricultural Systems. Industrial training placement.

**Year 4 — Research and Project:**
Capstone project on a real biosystems challenge, Research methods, Entrepreneurship in Agri-tech and Food Tech, Technology Business Management, International standards in food and biosystems.

---

## Career Paths in Sri Lanka

- **Agricultural technology industry:** Precision farming companies, agricultural equipment suppliers, greenhouse operators, hydroponic farming ventures.
- **Food processing industry:** Quality assurance and production management in food manufacturing companies (Cargills Food City, Prima, Nestlé Lanka, HNB Biscuits, CIC Agri).
- **Agri-food export sector:** Sri Lanka''s tea, rubber, spice, and coconut export industries all require biosystems technology expertise in processing and quality management.
- **Aquaculture industry:** Freshwater and marine fish farming, prawn farming, ornamental fish production.
- **Environmental technology:** Biogas plants, composting facilities, wastewater treatment systems.
- **Government agriculture services:** Department of Agriculture, Irrigation Department, Mahaweli Development Authority, and National Aquatic Resources Research & Development Agency (NARA).
- **Research institutions:** Tea Research Institute, Rubber Research Institute, Coconut Research Institute, Rice Research Institute.
- **Entrepreneurship:** Many graduates establish agri-tech businesses — micro-irrigation systems, hydroponic farms, post-harvest cold storage, or agricultural drone services.
- **International organizations:** FAO, UNDP, and international development organizations working on food security and sustainable agriculture in South and Southeast Asia.

---

## Entry Requirements

**A/L Stream:** Biosystems Technology (primary pathway); some universities may accept Biological Science applicants
**Required A/L subjects for BST stream:** Biosystems Technology plus appropriate optional subjects

**Z-score context:** Biosystems Technology is accessible — cutoffs typically **0.4 to 0.9** range, making it one of the more attainable Technology faculty programmes. Colombo (103A) and SJP (103B) tend to have the highest cutoffs within this group.

---

## Special Notes

- This degree is specifically designed for Biosystems Technology A/L stream students, making it a tailored pathway rarely offered elsewhere.
- Biosystems Technology graduates are well-positioned for Sri Lanka''s food security and sustainable agriculture goals — an increasingly important national priority.
- The combination of biology knowledge and engineering skills is unique and gives graduates access to job markets that neither pure biologists nor pure engineers can easily enter.
- Growing interest in sustainable food systems, precision agriculture, and organic farming creates new opportunities for BST graduates both locally and internationally.
', '5e66cd1b4ef31ab316d9beee897537dbb33f61b8c80cc01278c6aae3a8a1eae4');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('104', '# Information and Communication Technology (B.ICT.)
**Course Number:** 104
**Degree:** Bachelor of Information and Communication Technology (B.ICT. Honours)
**Duration:** 4 years
**Entry Stream:** Engineering Technology, Physical Science (some universities)
**Available at:** University of Colombo Faculty of Technology (104A), University of Sri Jayewardenepura Faculty of Technology (104B), University of Ruhuna Faculty of Technology (104C)

---

## Overview

The Bachelor of ICT is the technology faculty''s computing degree — designed for Engineering Technology A/L stream students who want to enter the ICT industry. It differs from Computer Science (012) in that it is specifically oriented towards practical ICT skills, telecommunications, networking, and systems — while still covering software development and computing fundamentals.

With Sri Lanka''s ICT industry growing rapidly (contributing USD 1.5+ billion to export earnings and employing 100,000+), ICT Technology graduates are entering one of the most dynamic employment sectors in the country.

---

## What You Will Study

**Year 1 — ICT Foundations:**
Programming (Python, Java), Web Technologies (HTML, CSS, JavaScript), Digital Systems, Database Basics, Networking Fundamentals, Mathematics for ICT, Technical Communication.

**Year 2 — Core ICT:**
Object-Oriented Programming, Data Structures, Operating Systems, Computer Networks and Internet Technology, Database Management Systems, Systems Analysis and Design, Mobile Computing, ICT Project Management.

**Year 3 — Applied ICT:**
Software Engineering, Information Security and Cybersecurity, Cloud Computing and Virtualization, IoT Systems, Mobile App Development (Android/iOS), Business Intelligence, Industrial Training placement.

**Year 4 — Advanced and Capstone:**
Research Project, Electives (AI Applications, Big Data, DevOps, Blockchain), ICT Entrepreneurship, Advanced Networking.

---

## Career Paths in Sri Lanka

- **Software development:** Web, mobile, and enterprise software development at Sri Lanka''s IT companies.
- **Network and infrastructure:** Network engineers and system administrators at telecoms (Dialog, SLT Mobitel, Hutch), banks, and large organizations.
- **Cybersecurity:** Security analysts, security operations centre (SOC) analysts.
- **IoT and embedded systems:** Smart home, smart agriculture, and industrial IoT applications.
- **Government IT:** ICTA digital transformation projects, government ministry IT departments.
- **Freelancing:** Web development, digital services on international freelancing platforms.
- **Startup ecosystem:** Sri Lanka''s growing startup sector in fintech, health tech, and agri-tech.

---

## Entry Requirements

**A/L Stream:** Engineering Technology (primary); Physical Science also accepted at some universities

**Z-score context:** ICT Technology has cutoffs in the **0.5 to 1.1** range — accessible to most ET stream students, with Colombo and SJP being the most competitive within this programme.

---

## Special Notes

- Industrial training is compulsory — students gain direct industry experience before graduation.
- ICT degree holders from Technology Faculties enter the same job market as Computer Science and IT graduates, and are equally competitive for most industry roles.
- The degree is conducted in English at all three universities.
', 'ca6bb71a6f1d01582bd3a06e0de7ecf1f00ec6bbf6ce952169d048ec5647af7f');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('105', '# Teaching English as a Second Language
**Course Number:** 105
**Degree:** Bachelor of Arts (Honours) in Teaching English as a Second Language
**Duration:** 4 years
**Entry Stream:** Arts Stream
**Available at:** University of Sri Jayewardenepura (105C), University of Kelaniya (105D), Sabaragamuwa University of Sri Lanka (105L)

---

## Overview

The Bachelor of Arts in Teaching English as a Second Language (TESL) is a specialized degree designed to produce highly skilled educators capable of addressing the critical need for English proficiency in Sri Lanka. As English remains a vital link language for professional and academic advancement in the country, this degree equips students with the pedagogical theories, linguistic foundations, and practical classroom strategies necessary to teach English effectively in diverse educational settings.

In the Sri Lankan context, this degree is essential for bridging the gap between urban and rural English literacy. Graduates are prepared to navigate the challenges of second-language acquisition, focusing on curriculum development, materials design, and the application of modern educational technology. The programme is highly regarded for its blend of theoretical linguistics and hands-on teaching practice, ensuring that graduates are ready to contribute to the national education system, private sector training, and international language instruction.

---

## What You Will Study

**Year 1: Foundations of Language and Education**
Focuses on the basics of linguistics, English grammar, phonetics, and phonology. Students are introduced to the history of the English language and the fundamental principles of educational psychology and child development.

**Year 2: Pedagogical Theory and Language Acquisition**
Covers Second Language Acquisition (SLA) theories, methods of teaching English, and classroom management. Students begin exploring sociolinguistics and the role of English in the Sri Lankan socio-economic landscape.

**Year 3: Advanced Methodology and Curriculum Design**
Students delve into materials development, testing and evaluation, and the use of ICT in language teaching. This year often includes a compulsory teaching practicum (internship) in a school or educational institute to gain real-world experience.

**Year 4: Research and Professional Specialization**
The final year focuses on advanced research methodology, culminating in a dissertation or a major research project. Students may also choose elective modules such as English for Specific Purposes (ESP), Business English, or Literature in the ESL classroom.

---

## Career Paths in Sri Lanka

*   **Government School Teacher:** Employed by the Ministry of Education; involves teaching English to students from primary to A/L levels in national or provincial schools.
*   **University Lecturer/Instructor:** Working within the English Language Teaching Units (ELTU) of state universities; involves designing and delivering English courses for undergraduates of other faculties.
*   **Corporate Trainer/Business English Instructor:** Employed by private firms or BPO/IT companies; involves training employees in professional communication, email writing, and presentation skills.
*   **Curriculum Developer/Material Designer:** Working with the National Institute of Education (NIE) or private publishing houses; involves creating textbooks, digital learning modules, and assessment tools.
*   **Educational Consultant/NGO Project Officer:** Working with organizations like the British Council or local NGOs; involves managing literacy projects and teacher training workshops.
*   **Postgraduate Study:** Graduates can pursue a Master of Arts in Linguistics, TESL, or Education (M.Ed) at institutions like the University of Colombo or the Open University of Sri Lanka to advance into academic or administrative leadership roles.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Arts stream. Candidates must have obtained a minimum of three "S" passes in one sitting. Proficiency in English is mandatory, and students are often required to pass an additional aptitude test or interview conducted by the respective university to assess their language competency and suitability for the teaching profession. The Z-score requirement is generally competitive, reflecting the high demand for this professional degree.

---

## Differences Between Universities

*   **University of Sri Jayewardenepura:** Known for a strong focus on professional development and links with the corporate sector, often emphasizing Business English and ESP.
*   **University of Kelaniya:** Features a highly established Department of English/TESL with a strong research culture and a long history of producing English language educators for the national system.
*   **Sabaragamuwa University of Sri Lanka:** Offers a unique perspective on the challenges of language acquisition in rural contexts, with a strong emphasis on community-based teaching and practical field experience.

---

## Special Notes

The degree is conducted entirely in the English medium. While this degree is a primary qualification for teaching, those intending to teach in government schools must also comply with the recruitment regulations set by the Ministry of Education and the Teacher Educators'' Service. Graduates are highly sought after for overseas teaching opportunities, particularly in East Asia and the Middle East, due to the global demand for qualified English instructors. Students are encouraged to maintain a high GPA to qualify for postgraduate scholarships.', '30938447c0ba8457ee01445e02467de47f6fe9ea65d055db80c4203bd8e5d114');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('106', '# Marine and Fresh Water Sciences
**Course Number:** 106
**Degree:** Bachelor of Science (Honours) in Marine and Fresh Water Sciences
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Ruhuna (106F)

---

## Overview

The B.Sc. (Honours) in Marine and Fresh Water Sciences is a specialized undergraduate programme designed to address the critical need for scientific management of Sri Lanka’s vast aquatic resources. As an island nation with an Exclusive Economic Zone (EEZ) many times larger than its landmass, Sri Lanka relies heavily on its marine and inland water ecosystems for food security, economic growth, and climate resilience. This degree provides a comprehensive understanding of aquatic environments, ranging from coastal lagoons and deep-sea oceanography to inland reservoirs and riverine systems.

The University of Ruhuna, located in the Southern Province, is uniquely positioned to offer this programme due to its proximity to the Indian Ocean and major inland water bodies. The Faculty of Fisheries and Marine Sciences & Technology is a pioneer in this field, providing students with direct access to coastal research sites, state-of-the-art laboratories, and industry-standard equipment. The curriculum integrates theoretical knowledge with field-based training, ensuring graduates are equipped to tackle challenges such as sustainable fisheries management, water pollution control, and the impacts of climate change on aquatic biodiversity.

---

## What You Will Study

**Year 1: Foundation in Aquatic Sciences**
Focuses on core biological and physical sciences. Subjects include General Biology, Chemistry, Physics for Aquatic Sciences, Mathematics, and an introduction to Marine and Fresh Water environments. Students also begin learning basic laboratory safety and field sampling techniques.

**Year 2: Core Aquatic Disciplines**
Deepens knowledge in specialized areas such as Limnology (study of inland waters), Oceanography, Aquatic Chemistry, Microbiology, and Invertebrate Zoology. Students are introduced to the principles of aquatic ecology and the physical properties of water bodies.

**Year 3: Specialization and Advanced Techniques**
Students choose between two primary tracks: **Oceanography & Marine Geology** (focusing on sea-floor mapping, marine currents, and coastal processes) or **Water Science & Technology** (focusing on water quality analysis, wastewater treatment, and hydrological modeling). Advanced modules include GIS and Remote Sensing for aquatic monitoring.

**Year 4: Research and Professional Application**
The final year is dedicated to a mandatory individual research project (dissertation) conducted under the supervision of senior academics. Students also undertake industrial training or internships, advanced seminars on aquatic resource policy, and specialized elective modules relevant to their chosen track.

---

## Career Paths in Sri Lanka

*   **Aquatic Resource Manager:** Working with the National Aquatic Resources Research and Development Agency (NARA) or the Department of Fisheries and Aquatic Resources to monitor fish stocks and manage sustainable harvesting.
*   **Water Quality Analyst:** Employed by the National Water Supply and Drainage Board (NWSDB) or private environmental consultancy firms to test water safety, monitor pollution, and ensure compliance with environmental standards.
*   **Environmental Consultant:** Working with private firms on Environmental Impact Assessments (EIAs) for coastal development projects, port expansions, or tourism infrastructure.
*   **Aquaculture Specialist:** Managing commercial fish or shrimp farms, focusing on breeding, disease control, and optimizing production efficiency in the private sector.
*   **Marine Researcher/Academic:** Pursuing postgraduate studies (M.Sc./Ph.D.) to conduct research at universities or research institutes, focusing on climate change, marine conservation, or oceanography.
*   **Coastal Conservationist:** Working with international NGOs (e.g., IUCN, UNDP) or local conservation groups on coral reef restoration, mangrove protection, and marine protected area management.

---

## Entry Requirements

Admission is strictly through the University Grants Commission (UGC) based on the G.C.E. Advanced Level examination. Applicants must have sat for the A/L examination in the **Biological Science** stream. Candidates must have obtained a minimum of three ''S'' passes in the required subjects (Biology, Chemistry, and Physics) in a single sitting. The Z-score requirement is highly competitive, reflecting the specialized nature of the programme and the limited intake capacity of the Faculty of Fisheries and Marine Sciences & Technology. The medium of instruction is English.

---

## Differences Between Universities

Currently, this specific degree programme (Marine and Fresh Water Sciences) is offered exclusively at the University of Ruhuna. While other institutions like the Ocean University of Sri Lanka offer degrees in Fisheries and Marine Sciences, the University of Ruhuna programme is distinct for its specific academic focus on the integration of marine and fresh water systems, its strong emphasis on research-led teaching, and its strategic location in the Southern coastal belt, which provides unparalleled access to diverse aquatic ecosystems for field research.

---

## Special Notes

Graduates of this programme are eligible to apply for professional memberships in relevant scientific bodies, such as the Institute of Biology (IOB) Sri Lanka. The degree is highly research-oriented, making it an excellent pathway for students intending to pursue postgraduate studies (M.Sc. or Ph.D.) locally or abroad, particularly in countries with strong maritime research sectors like Australia, Norway, or Japan. Students should be prepared for significant fieldwork, which may involve travel to remote coastal or inland locations and exposure to varying weather conditions. Proficiency in English is essential, as most technical literature and international research journals in this field are published in English.', '6651b7d1f1ce9c25e1f80af688ceb98c12285b92be2b8eb60dd3116464d0e32e');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('107', '# Food Business Management
**Course Number:** 107
**Degree:** Bachelor of Science Honours in Food Business Management
**Duration:** 4 years
**Entry Stream:** Biological Science or Physical Science
**Available at:** Sabaragamuwa University of Sri Lanka (107L)

---

## Overview

The Bachelor of Science Honours in Food Business Management is a specialized degree programme designed to bridge the gap between food science technology and modern business administration. In the Sri Lankan context, where the food and beverage sector is a primary driver of the economy, this degree prepares graduates to navigate the complexities of food supply chains, quality assurance, and market-driven product development.

Sabaragamuwa University of Sri Lanka, located in Belihuloya, is uniquely positioned to offer this programme due to its strong focus on agricultural sciences and rural development. The Faculty of Agricultural Sciences provides students with a holistic view of the food value chain—from farm-gate production to consumer-facing retail. This programme is vital for students aiming to lead in Sri Lanka’s expanding food processing, export, and hospitality industries.

---

## What You Will Study

**Year 1: Foundations of Science and Management**
Focuses on core principles including Food Chemistry, Microbiology, Principles of Management, Economics, and Mathematics for Business. Students gain a baseline understanding of how biological systems interact with economic principles.

**Year 2: Food Technology and Business Operations**
Covers Food Processing Technology, Post-harvest Technology, Accounting, Marketing Management, and Human Resource Management. This year integrates technical food knowledge with the operational side of running a food-based enterprise.

**Year 3: Advanced Management and Supply Chain**
Students delve into Supply Chain Management, Food Quality Assurance and Safety (HACCP/ISO standards), Financial Management, and Entrepreneurship. This year emphasizes the logistics of the food industry and regulatory compliance.

**Year 4: Strategic Management and Research**
The final year focuses on Strategic Management, Food Policy and Law, and International Trade. Students must complete a comprehensive Independent Research Project or a professional internship, allowing them to apply theoretical knowledge to real-world problems in the Sri Lankan food sector.

---

## Career Paths in Sri Lanka

*   **Food Quality Assurance Manager:** Working with major exporters like CBL (Ceylon Biscuits Limited) or Cargills to ensure products meet international safety and quality standards.
*   **Supply Chain Coordinator:** Managing logistics for large-scale retail chains like Keells or Arpico, ensuring the efficient movement of perishable goods from farms to shelves.
*   **Food Entrepreneur:** Starting independent ventures in value-added food processing, leveraging local agricultural produce for domestic or export markets.
*   **Production Supervisor:** Overseeing factory-floor operations in food manufacturing plants, focusing on efficiency, cost-reduction, and staff management.
*   **Market Research Analyst:** Working with food-focused consultancy firms or FMCG companies to analyze consumer trends and develop new product strategies.
*   **Postgraduate Study:** Graduates can pursue an MBA, M.Sc. in Food Science, or specialized postgraduate diplomas in Agribusiness Management at institutions like the University of Peradeniya or the Postgraduate Institute of Management (PIM).

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results. Students must have qualified in either the Biological Science or Physical Science streams. The selection is highly competitive and is determined by the Z-score, which varies annually based on the applicant pool and district-based quotas. The medium of instruction is English, and students are expected to have a strong command of the language for technical reporting and business communication.

---

## Differences Between Universities

This programme is currently offered exclusively at the Sabaragamuwa University of Sri Lanka. Its location in the Sabaragamuwa Province provides students with direct access to diverse agricultural landscapes, making it a premier choice for those interested in the intersection of rural agriculture and corporate food management.

---

## Special Notes

Graduates of this programme are well-positioned to obtain professional certifications in food safety (such as ISO 22000 or HACCP lead auditor training), which are highly valued by the industry. While there is no mandatory licensing body like the SLMC for this degree, the curriculum is aligned with global industry standards, making graduates eligible for employment in multinational food corporations. There is significant demand for these skills in the Middle Eastern and European food export markets, providing strong potential for overseas career opportunities.', '59a945c2f8f00338802faeb96f812ef18d530f2b5cbd129f483eb4232b51476c');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('108', '# Physical Science - ICT
**Course Number:** 108
**Degree:** Bachelor of Science (General) Degree in Physical Science (ICT)
**Duration:** 3 years
**Entry Stream:** Physical Science
**Available at:** University of Sri Jayewardenepura (108C), University of Kelaniya (108D)

---

## Overview

The Physical Science - ICT degree is a specialized undergraduate programme designed to bridge the gap between theoretical physical sciences and the practical application of Information and Communication Technology. In the context of Sri Lanka’s rapidly digitizing economy, this degree equips students with the analytical rigor of physical sciences combined with the technical proficiency required to manage, develop, and implement modern IT solutions.

This programme is highly relevant to the local industry, which is currently experiencing a surge in demand for professionals who can navigate both hardware-level logic and software-level systems. Graduates are well-positioned to contribute to Sri Lanka’s growing software export sector, telecommunications industry, and the digital transformation initiatives currently being undertaken by both government and private sector enterprises.

---

## What You Will Study

**Year 1: Foundation in Science and Computing**
Focuses on core modules in Mathematics, Physics, and introductory Computer Science. Students learn fundamental programming concepts, computer architecture, and the mathematical foundations of data analysis.

**Year 2: Core ICT and Applied Science**
Students delve into data structures, algorithms, database management systems, and operating systems. This year emphasizes the integration of physical science principles with ICT, often including modules on electronics, digital logic, and software engineering methodologies.

**Year 3: Advanced Specialization and Project Work**
The final year focuses on advanced topics such as network security, web development, and cloud computing. Students are required to complete a comprehensive final-year research project or industrial internship, applying their knowledge to solve real-world problems in a professional setting.

---

## Career Paths in Sri Lanka

*   **Software Engineer:** Working with major Sri Lankan tech firms like WSO2, 99x, or IFS to design and maintain software applications.
*   **Systems Administrator:** Managing IT infrastructure for large-scale organizations, including banks like BOC or Sampath Bank, ensuring network stability and security.
*   **Database Administrator:** Overseeing data integrity and storage solutions for telecommunications providers like Dialog Axiata or SLT-Mobitel.
*   **IT Consultant:** Providing technical expertise to SMEs or government departments undergoing digital transformation.
*   **Academic/Researcher:** Pursuing postgraduate studies (MSc/MPhil) at local universities to contribute to research in fields like Data Science or AI.
*   **Technical Support Specialist:** Managing complex hardware and software environments in the BPO and KPO sectors.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level Examination in the Physical Science stream. Candidates must have obtained at least ‘S’ grades in Combined Mathematics, Physics, and Information and Communication Technology. Admission is highly competitive and is determined by the Z-score calculated by the University Grants Commission (UGC). The medium of instruction is English.

---

## Differences Between Universities

*   **University of Sri Jayewardenepura:** Known for its strong industry-integrated curriculum and close ties with the corporate sector in the Colombo metropolitan area. The faculty emphasizes practical application and has a robust alumni network in the software industry.
*   **University of Kelaniya:** Often associated with the "Physics and Electronics" (PHEL) focus within this stream. It offers a strong emphasis on the hardware-software interface, making it ideal for students interested in embedded systems and technical infrastructure, supported by a well-established Faculty of Science.

---

## Special Notes

This degree is a 3-year General Degree. Students aiming for higher academic or research-oriented careers often pursue a postgraduate diploma or a Master’s degree (MSc) after graduation to enhance their specialization. While this is not an engineering degree (and thus not accredited by the IESL), it is highly valued in the IT industry for its strong analytical foundation. Graduates are encouraged to obtain professional certifications (e.g., AWS, Cisco, or Microsoft) alongside their degree to increase employability in the global market.', 'd910121124fc2ae510fe970315862b0d6c3d5dd9db99ad1454e547ed268e96ba');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('109', '# Business Science (B.Sc.)
**Course Number:** 109
**Degree:** Bachelor of Science (Honours) in Business Science
**Duration:** 4 years
**Entry Stream:** Commerce, Physical Science
**Available at:** University of Moratuwa Faculty of Business (109A)

---

## Overview

Business Science at the University of Moratuwa''s Faculty of Business is a unique and prestigious business degree that combines rigorous quantitative methods — data analytics, financial modelling, operations research — with core business management disciplines. It leverages Moratuwa''s engineering and science culture to produce business graduates with stronger analytical and technological capabilities than traditional management degrees.

This degree is ideal for Commerce or Physical Science students who want the prestige and analytical rigour of a Moratuwa degree combined with business and management knowledge.

---

## What You Will Study

**Year 1 — Quantitative and Business Foundations:**
Business Mathematics and Statistics, Financial Accounting, Microeconomics, Business Law, Programming and Business Analytics Tools (Python, Excel Analytics), Management Principles.

**Year 2 — Core Business Science:**
Corporate Finance, Operations Management, Data Analytics for Business, Marketing Management, Supply Chain Management, Human Resource Management, Database Systems for Business.

**Year 3 — Advanced Analytics and Management:**
Business Intelligence (Power BI, Tableau), Machine Learning for Business, Financial Modelling, Strategic Management, Entrepreneurship and Innovation, Advanced Operations Research, Industrial Training.

**Year 4 — Research:**
Research Dissertation, Business Data Science, Digital Business Transformation, Business Strategy and Policy.

---

## Career Paths in Sri Lanka

- **Management consulting:** McKinsey, BCG, Accenture, and local consulting firms value the analytical rigour of Moratuwa Business Science graduates.
- **Financial analysis:** Banks, investment companies, securities firms for quantitative financial analysis.
- **Operations and supply chain:** Manufacturing, FMCG, and logistics companies.
- **Business analytics:** Data-driven business roles across all industries.
- **Digital product management:** Tech companies managing business products.
- **Entrepreneurship:** Business Science provides both analytical and management skills for starting ventures.
- **Postgraduate:** MBA at top local or international universities — Moratuwa''s name opens doors.

---

## Entry Requirements

**A/L Stream:** Commerce (primary), Physical Science (also accepted)
**Typical subjects:** Commerce — Accounting, Business Studies, Economics; Physical Science — Combined Mathematics, Physics, Chemistry

**Z-score context:** Business Science at Moratuwa (109A) benefits from Moratuwa''s brand — cutoffs are typically **0.9 to 1.4** for Commerce stream and somewhat higher for Physical Science stream applicants.

---

## Special Notes

- The quantitative curriculum requires genuine comfort with mathematics — students who found O/L Maths challenging should prepare additional groundwork.
- Being at Moratuwa gives Business Science students access to the same industry networks as Engineering and IT students at the same campus.
- This programme was introduced relatively recently but is rapidly gaining employer recognition due to Moratuwa''s reputation.
', '260fea6ed42d2ceee42a02c5bc848a0bd66003b794e86c75fde82eb849a97ce6');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('110', '# Financial Engineering (B.Sc.)
**Course Number:** 110
**Degree:** Bachelor of Science (Honours) in Financial Engineering
**Duration:** 4 years
**Entry Stream:** Commerce (primary), Physical Science
**Available at:** University of Kelaniya Faculty of Commerce and Management Studies (110A)

---

## Overview

Financial Engineering is a quantitative finance degree that applies mathematical modelling, statistics, programming, and financial theory to solve problems in banking, investment, insurance, and risk management. It is one of the most mathematically demanding business degrees in Sri Lanka, attracting students who excel at both mathematics and finance.

Globally, Financial Engineering and Quantitative Finance are among the highest-paying specializations in the finance industry. Sri Lanka''s growing financial sector — banking, insurance, capital markets, and investment — creates career opportunities for quantitatively skilled graduates.

---

## What You Will Study

**Year 1 — Quantitative Foundations:**
Calculus, Linear Algebra, Probability and Statistics, Financial Accounting, Principles of Economics, Introduction to Finance, Programming (Python/R).

**Year 2 — Core Financial Engineering:**
Financial Mathematics (time value of money, interest rate modelling, bond pricing), Econometrics (statistical modelling of economic data), Financial Derivatives (options, futures, swaps), Corporate Finance, Financial Markets and Institutions, Database for Finance.

**Year 3 — Advanced Modelling:**
Risk Management (market risk, credit risk, operational risk), Portfolio Theory and Investment (Markowitz, CAPM, factor models), Fixed Income Analysis, Stochastic Calculus (mathematical basis of options pricing — Black-Scholes model), Financial Simulation (Monte Carlo methods), Machine Learning for Finance.

**Year 4 — Applied Finance:**
Research Dissertation, Financial Regulation and Compliance, Algorithmic Trading, Actuarial Applications, International Finance, Advanced Derivatives Pricing.

---

## Career Paths in Sri Lanka

- **Commercial banking:** Risk analysts, credit analysts, treasury officers — quantitative skills are valued in banks'' risk and treasury divisions.
- **Investment banking and stockbroking:** Research analysts, equity analysts at stockbrokers and investment banks (NDB Securities, Asia Securities, First Capital, Softlogic Stockbrokers).
- **Insurance:** Actuarial assistant, risk management officer — insurance companies value mathematical finance skills.
- **Colombo Stock Exchange (CSE):** Research and analytics roles.
- **Central Bank of Sri Lanka (CBSL):** Research Department, Financial Intelligence Unit, monetary policy analysis.
- **Fintech:** Financial technology startups in payments, lending, and investment platforms.
- **International finance:** With additional qualifications (CFA — Chartered Financial Analyst, FRM — Financial Risk Manager), international opportunities in Singapore, Dubai, London, and New York are realistic.
- **Actuarial science:** Financial Engineering is excellent preparation for actuarial examinations (CT/CM series from the Institute and Faculty of Actuaries).

---

## Entry Requirements

**A/L Stream:** Commerce (primary, but strong mathematics background needed); Physical Science students may also apply
**Required subjects (Commerce):** Accounting, Business Studies, Economics — but strong mathematics performance at O/L level is important

**Z-score context:** Financial Engineering at Kelaniya (110A) has cutoffs typically in the **0.8 to 1.3** range for Commerce stream. A mathematically focused business programme for students who loved O/L Mathematics.

---

## Special Notes

- This is one of the most quantitatively demanding Commerce-based degrees — students who struggle with mathematics will find Year 2+ challenging.
- The CFA (Chartered Financial Analyst) designation is the gold standard for investment professionals globally. Financial Engineering graduates are well-prepared to begin CFA exams.
- Sri Lanka''s capital markets are underdeveloped compared to regional peers — this is both a challenge and an opportunity for quantitatively skilled graduates who can help develop the market.
', '5f0625e186b2f1c808742acf0fc65ecfbe50a0ab797ee0f67776ea7366b3a359');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('111', '# Geographical Information Science
**Course Number:** 111
**Degree:** Bachelor of Science (Honours) in Geographical Information Science
**Duration:** 4 years
**Entry Stream:** Physical Science (Mathematics/Physics/Statistics) or Arts (with Geography/Economics/Statistics)
**Available at:** University of Peradeniya (111B)

---

## Overview

Geographical Information Science (GISc) is a multidisciplinary field that integrates geography, computer science, and data analytics to capture, store, manipulate, and analyze spatial data. In the Sri Lankan context, this degree is critical for national development, particularly in urban planning, disaster management, and environmental conservation. As the country moves toward digital governance and "Smart City" initiatives, the ability to visualize and interpret spatial patterns is becoming a high-demand skill set.

The University of Peradeniya, through its Department of Geography, offers a unique academic environment that blends traditional geographical knowledge with modern computational tools. Students benefit from the university’s long-standing reputation for research excellence and its strategic location in the central highlands, which serves as a living laboratory for field-based studies in environmental monitoring and land-use planning.

---

## What You Will Study

**Year 1: Foundations**
Introduction to Geography, Fundamentals of GIS, Cartography, Mathematics for Spatial Science, and Introduction to Programming (Python/R).

**Year 2: Data and Technology**
Remote Sensing (RS) techniques, Database Management Systems, Spatial Statistics, Geodesy, and Advanced Cartographic Design.

**Year 3: Applied Specialization**
Environmental Impact Assessment (EIA), Disaster Risk Management, Urban and Regional Planning, Web GIS development, and Global Positioning Systems (GPS) field operations.

**Year 4: Advanced Research and Professional Practice**
Advanced Spatial Modeling, Professional Ethics in Geoinformatics, and a mandatory Final Year Research Project/Dissertation. Students also undertake a professional internship to gain industry-specific experience.

---

## Career Paths in Sri Lanka

*   **GIS Analyst:** Working with the Survey Department of Sri Lanka or the Urban Development Authority (UDA) to manage land-use data and infrastructure mapping.
*   **Remote Sensing Specialist:** Employed by the Department of Meteorology or environmental NGOs to monitor forest cover, climate change impacts, and agricultural health.
*   **Disaster Management Officer:** Working with the Disaster Management Centre (DMC) to create hazard maps and emergency response plans for flood and landslide-prone areas.
*   **Urban Planner:** Assisting local government bodies or private consultancy firms in designing sustainable city layouts and transport networks.
*   **Geospatial Data Scientist:** Working in the private tech sector or logistics companies to optimize delivery routes and location-based services.
*   **Postgraduate Study:** Graduates can pursue an MSc in Geoinformatics at the University of Colombo (IHRA) or the University of Moratuwa to specialize in advanced remote sensing and spatial research.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results. Students are generally expected to have a strong background in Mathematics, Geography, or Statistics. The degree is highly competitive, and the required Z-score varies annually based on the applicant pool and the specific stream (Physical Science or Arts). The medium of instruction is English, and candidates must demonstrate proficiency in academic writing and technical communication.

---

## Differences Between Universities

Currently, the Bachelor of Science (Honours) in Geographical Information Science is primarily offered by the University of Peradeniya. While other universities may offer GIS as a subject module within a BA or BSc Geography degree, the Peradeniya programme is distinct for its dedicated focus on the "Science" aspect of GIS, providing more intensive training in programming, spatial statistics, and technical field instrumentation compared to general geography degrees.

---

## Special Notes

Graduates of this programme are well-positioned for both local and international employment, as GIS skills are globally standardized. While there is no specific professional licensing body comparable to the IESL for engineers, graduates often seek membership in professional geographical or surveying associations. The degree provides a strong foundation for those interested in pursuing further studies in Data Science, Environmental Engineering, or Urban Development. Students are encouraged to maintain a portfolio of their mapping and coding projects throughout their four years to enhance their employability in the private sector.', 'a2faa2c7e0f170f952a3fb882edf0511c52e89637b0a4191ca433a4ecc08a3c0');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('112', '# Social Work
**Course Number:** 112
**Degree:** Bachelor of Social Work (Honours)
**Duration:** 4 years
**Entry Stream:** Arts Stream
**Available at:** University of Peradeniya (112B), University of Sri Jayewardenepura (112C)

---

## Overview

Social Work is a professional discipline dedicated to improving the quality of life and subjective well-being of individuals, families, and communities. In the Sri Lankan context, this degree is vital for addressing complex societal challenges, including poverty alleviation, child protection, elderly care, and post-conflict psychosocial rehabilitation. Graduates are trained to bridge the gap between vulnerable populations and state or non-governmental support systems.

The University of Peradeniya and the University of Sri Jayewardenepura are the primary state institutions offering this specialized training. These faculties are notable for their strong integration of sociological theory with practical field-based interventions. By studying at these institutions, students gain exposure to the diverse socio-economic landscape of Sri Lanka, preparing them to work effectively within the national policy framework and international development sectors.

---

## What You Will Study

**Year 1: Foundations of Social Work**
Introduction to social work values and ethics, sociology for social workers, psychology of human development, and the history of social welfare in Sri Lanka.

**Year 2: Methods and Skills**
Core methods including social casework, group work, and community organization. Students begin learning about social policy, legal frameworks (such as the Children and Young Persons Ordinance), and research methodology.

**Year 3: Specialized Practice**
Advanced modules covering child protection, gender-based violence, mental health, and substance abuse counseling. Students engage in supervised field placements to apply theoretical knowledge in real-world settings.

**Year 4: Professional Integration**
Focus on social administration, project management, and disaster management. The final year requires a comprehensive independent research dissertation and a final intensive internship period to prepare for professional practice.

---

## Career Paths in Sri Lanka

*   **Child Protection Officer:** Working with the National Child Protection Authority (NCPA) or Probation and Child Care Services to safeguard minors from abuse and neglect.
*   **Medical Social Worker:** Employed in government hospitals (e.g., National Hospital of Sri Lanka) to support patients and families dealing with chronic illness, trauma, or terminal conditions.
*   **NGO/INGO Project Coordinator:** Managing community development, livelihood, or psychosocial support projects for organizations like Save the Children, World Vision, or local community-based organizations.
*   **Probation Officer:** Working under the Department of Probation and Child Care to manage rehabilitation programs for juvenile offenders and provide court reports.
*   **Human Resources/CSR Specialist:** Managing corporate social responsibility initiatives or employee welfare programs in large private sector firms.
*   **Postgraduate Study:** Graduates can pursue a Master’s in Social Work (MSW), Sociology, or Development Studies at local universities or abroad to move into policy-making or academic research roles.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination results in the Arts stream. Candidates must have passed three subjects in one sitting. Selection is highly competitive and based on the Z-score system. Proficiency in both Sinhala/Tamil and English is essential, as the curriculum involves both academic reading and field-based communication. No specific aptitude test is required for entry, but a strong commitment to community service is highly valued during the selection process.

---

## Differences Between Universities

*   **University of Peradeniya:** Known for its long-standing tradition in the social sciences and a strong focus on rural development and community-based research in the Central Province. It offers a campus-based experience with extensive access to multidisciplinary library resources.
*   **University of Sri Jayewardenepura:** Offers a more urban-centric approach with strong links to government ministries and NGOs located in the Colombo district. The faculty is highly integrated with modern social policy research and provides excellent networking opportunities for internships in the capital city.

---

## Special Notes

Social Work is a recognized profession in Sri Lanka, though formal licensing requirements are currently evolving. Graduates are encouraged to register with relevant professional bodies if available. The degree is taught primarily in the national languages (Sinhala/Tamil), but English literacy is critical for accessing global research and securing positions in international NGOs. There is a high demand for qualified social workers in the Middle East and Western countries, making this a degree with significant potential for overseas migration, provided that local qualifications are supplemented with relevant international certifications.', '2fdca1488a8ce9e13342e374ded78e55bd6a20d8565ae20dcb0b38f90e46ca07');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('113', '# Financial Mathematics and Industrial Statistics
**Course Number:** 113
**Degree:** Bachelor of Science (Honours) in Financial Mathematics and Industrial Statistics
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** University of Ruhuna (113F)

---

## Overview

The Bachelor of Science (Honours) in Financial Mathematics and Industrial Statistics is a specialized four-year degree programme designed to bridge the gap between advanced mathematical theory and its practical application in the corporate and industrial sectors. In the context of Sri Lanka’s rapidly evolving financial landscape, this degree is highly relevant for students aiming to enter the banking, insurance, and manufacturing sectors, where data-driven decision-making is becoming the primary driver of competitive advantage.

The University of Ruhuna, through its prestigious Department of Mathematics, offers this programme as a response to the growing demand for professionals who can navigate complex financial models and industrial processes. By combining rigorous mathematical training with statistical analysis and computing, the faculty ensures that graduates are equipped to handle the challenges of modern quantitative finance and industrial optimization, making it a unique offering within the Sri Lankan state university system.

---

## What You Will Study

**Year 1:** Foundations in Pure and Applied Mathematics, Calculus, Linear Algebra, Introduction to Programming, and Basic Statistics. Students build the core logical framework required for advanced quantitative analysis.

**Year 2:** Probability Theory, Statistical Inference, Financial Accounting, Data Structures and Algorithms, and Ordinary Differential Equations. This year focuses on the intersection of mathematical theory and basic financial reporting.

**Year 3:** Financial Mathematics (Derivatives, Portfolio Theory), Industrial Statistics (Quality Control, Experimental Design), Stochastic Processes, Time Series Analysis, and Database Management Systems. Students begin to apply models to real-world financial and industrial data.

**Year 4:** Advanced Financial Modelling, Actuarial Science, Operations Research, Multivariate Analysis, and a compulsory Research Project or Industrial Internship. The final year emphasizes independent research, allowing students to solve specific problems faced by Sri Lankan industries or financial institutions.

---

## Career Paths in Sri Lanka

*   **Quantitative Analyst (Quant):** Working with investment banks and private equity firms like Acuity Partners or NDB Capital to develop pricing models for financial derivatives and risk management strategies.
*   **Actuarial Associate:** Employed by insurance giants such as Ceylinco Life or AIA Insurance to calculate premiums, assess risk, and ensure the financial solvency of insurance products.
*   **Data Scientist/Statistician:** Working in the manufacturing or FMCG sector (e.g., MAS Holdings, John Keells Holdings) to optimize supply chains, improve quality control processes, and predict market trends.
*   **Risk Manager:** Roles within the Central Bank of Sri Lanka or commercial banks like Commercial Bank and Sampath Bank, focusing on credit risk, market risk, and regulatory compliance.
*   **Financial Consultant:** Providing analytical support for consultancy firms like KPMG or EY, focusing on corporate finance, valuation, and strategic planning.
*   **Postgraduate Study:** Graduates are well-positioned for M.Sc. or Ph.D. programmes in Financial Engineering, Statistics, or Data Science, both locally at the University of Colombo/Moratuwa or internationally in the UK, Australia, or the USA.

---

## Entry Requirements

Admission is strictly through the Physical Science stream of the G.C.E. Advanced Level examination. Candidates must have obtained a minimum of three ''S'' passes in Combined Mathematics, Physics, and Chemistry (or an approved third subject). Admission is highly competitive and determined by the Z-score, which varies annually based on the performance of the applicant pool. The medium of instruction is English, and students are expected to have a strong command of the language to engage with technical literature and software.

---

## Differences Between Universities

Currently, the University of Ruhuna is the primary state university offering this specific Honours degree title. Unlike general B.Sc. degrees, this programme is highly specialized, focusing specifically on the synergy between finance and industrial statistics. Its location in the Southern Province provides unique industry links to regional industrial zones and the growing financial services sector in the Matara/Hambantota region, while maintaining the high academic standards associated with the University of Ruhuna’s Faculty of Science.

---

## Special Notes

This degree is designed to provide a strong foundation for professional qualifications. Graduates are often eligible for exemptions in professional examinations such as the CIMA (Chartered Institute of Management Accountants) or ACCA, depending on the specific modules completed. While there is no mandatory licensing body for mathematicians in Sri Lanka, the programme is highly regarded by the Institute of Applied Statistics Sri Lanka (IASSL). Students are encouraged to pursue internships during their vacation periods to gain practical exposure, as the industry places a high premium on candidates who can demonstrate the application of mathematical models in real-world business environments.', 'dc6eba7eeaf59522738ec693ab95734f8fe143076424fa082057eb417ba6e870');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('114', '# Human Resource Development
**Course Number:** 114
**Degree:** Bachelor of Business Management Honours in Human Resource Development
**Duration:** 4 years
**Entry Stream:** Commerce Stream
**Available at:** Uva Wellassa University of Sri Lanka (114U)

---

## Overview

The Bachelor of Business Management Honours in Human Resource Development (HRD) at Uva Wellassa University is a specialized degree designed to bridge the gap between traditional human resource management and the strategic development of human capital. In the Sri Lankan context, where the economy is shifting toward value-added services and knowledge-based industries, this degree focuses on training professionals who can design learning interventions, manage organizational change, and foster employee productivity in a competitive global market.

Uva Wellassa University is uniquely positioned to offer this program due to its emphasis on "Entrepreneurial Sri Lanka." Unlike traditional management degrees, this program integrates the socio-economic realities of the Uva Province with national development goals. Students benefit from the university’s strong ties to regional industries and its focus on practical, outcome-based education, ensuring graduates are equipped to handle the complexities of both the public and private sectors in Sri Lanka.

---

## What You Will Study

**Year 1: Foundations of Management**
Focuses on core business principles including Principles of Management, Business Mathematics, Economics, Financial Accounting, and Business Communication. Students are introduced to the organizational environment and the basics of human behavior.

**Year 2: Core HRD Competencies**
Deep dives into Human Resource Management, Organizational Behavior, Training and Development, Labour Law, and Management Information Systems. This year emphasizes the legal framework of Sri Lankan employment and the psychological aspects of workplace motivation.

**Year 3: Strategic Development and Specialization**
Covers advanced topics such as Strategic Human Resource Development, Performance Management, Compensation and Benefits, and Industrial Relations. Students begin to explore specialized tracks including Talent Management, Change Management, and Corporate Social Responsibility (CSR).

**Year 4: Research and Professional Application**
The final year focuses on the application of theory to real-world problems. Students undertake an Independent Research Project (Dissertation) and participate in a mandatory industrial internship. Electives may include Entrepreneurship, Global HR practices, and Advanced Data Analytics for HR.

---

## Career Paths in Sri Lanka

*   **HR Executive/Manager:** Working in large-scale manufacturing firms (e.g., MAS Holdings, Brandix) or service-sector conglomerates (e.g., John Keells Holdings) to oversee recruitment, training, and employee welfare.
*   **Training and Development Specialist:** Designing and implementing capacity-building programs for public sector institutions or private corporations to improve workforce efficiency.
*   **Industrial Relations Officer:** Managing labor disputes and ensuring compliance with the Sri Lankan Shop and Office Employees Act and other labor regulations within the Board of Investment (BOI) zones.
*   **Management Consultant:** Providing advisory services to SMEs on organizational restructuring, performance appraisal systems, and talent retention strategies.
*   **Public Sector Administrator:** Serving in government ministries or provincial councils, focusing on human capital planning and rural development initiatives.
*   **Postgraduate Study:** Graduates are well-prepared for an MBA, MSc in Human Resource Management, or professional qualifications from the Chartered Institute of Personnel Management (CIPM) Sri Lanka.

---

## Entry Requirements

Admission is based on the G.C.E. Advanced Level examination in the Commerce stream. Candidates must satisfy the minimum university entry requirements as determined by the University Grants Commission (UGC). The selection process is highly competitive, and the Z-score requirement varies annually based on the applicant pool. Proficiency in English is essential, as the medium of instruction is English. No specific aptitude test is required beyond the standard university admission criteria.

---

## Differences Between Universities

This programme is currently offered exclusively at Uva Wellassa University (114U). Its unique advantage lies in its location in Badulla, which provides students with a distinct perspective on rural development and regional economic growth. The faculty maintains a strong focus on the "Entrepreneurial" model, which encourages students to view HRD not just as an administrative function, but as a strategic tool for business growth and regional development.

---

## Special Notes

*   **Professional Recognition:** Graduates are encouraged to seek membership with the Chartered Institute of Personnel Management (CIPM) Sri Lanka, which is the leading professional body for HR in the country.
*   **Medium of Instruction:** All lectures, assignments, and examinations are conducted in English.
*   **Industrial Training:** The degree includes a mandatory internship component, which is vital for securing employment in the competitive Colombo-based corporate sector.
*   **Overseas Demand:** The curriculum is aligned with international HR standards, making graduates eligible for HR roles in the Middle East, Singapore, and other global markets where Sri Lankan HR professionals are increasingly sought after.', 'e5ddab9babf567f98b671f7131b90d2c7ac020d41c547c8ebaee69492dc54a25');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('115', '# Occupational Therapy (B.Sc.)
**Course Number:** 115
**Degree:** Bachelor of Science (Honours) in Occupational Therapy
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Kelaniya Faculty of Medicine, Department of Disability Studies (115A)

---

## Overview

Occupational Therapy (OT) is a healthcare profession that helps people of all ages who have physical, mental, or developmental conditions to participate in the activities (occupations) that matter to them — work, self-care, leisure, and daily life. OT practitioners work with stroke patients regaining independence, children with developmental disabilities, people with mental health conditions, and injured workers returning to employment.

Sri Lanka has very few trained Occupational Therapists relative to the population''s needs — making this a profession with virtually guaranteed employment and significant social impact.

---

## What You Will Study

**Year 1 — Sciences and OT Foundations:**
Human Anatomy and Physiology, Kinesiology (movement science), Psychology, Medical Sociology, Introduction to Occupational Therapy, Activity Analysis (understanding how tasks are performed and what skills they require).

**Year 2 — Core OT:**
Physical Disabilities OT (upper limb rehabilitation, splinting, adaptive equipment), Neurological OT (stroke, brain injury, Parkinson''s), Assistive Technology (wheelchairs, communication aids), Mental Health OT (activity-based mental health interventions), Child Development and Paediatric OT.

**Year 3 — Clinical Specializations:**
OT in Community Settings (home visits, community rehabilitation, vocational rehabilitation), Geriatric OT (elderly people), Hand Therapy (a specialized area of OT/physiotherapy), Environmental Modification (home and workplace adaptation), Research Methods. Clinical placements in hospitals, community settings, schools.

**Year 4 — Advanced and Research:**
Research Dissertation, Specialized Populations, OT Management and Leadership, Fieldwork supervision.

---

## Career Paths in Sri Lanka

- **Government hospitals:** National Hospital Colombo, rehabilitation hospitals, district and teaching hospitals all have OT departments (though understaffed).
- **Mental health institutions:** National Institute of Mental Health (NIMH, Angoda), and district mental health units.
- **Schools for children with disabilities:** OT in special education settings for autism, intellectual disability, cerebral palsy.
- **Private rehabilitation centres:** OT in private hospitals and dedicated rehabilitation centres.
- **Community rehabilitation:** Village-based rehabilitation programmes by NGOs and the Ministry of Social Services.
- **Vocational rehabilitation:** Helping people with disabilities return to work — with Industrial Boards and NGOs.
- **International:** Australia (OT Australia registration), UK (HCPC registration), Canada — significant demand for OTs internationally.
- **Academia:** OT lecturers at Kelaniya and other health faculties.

---

## Entry Requirements

**A/L Stream:** Biological Science
**Required subjects:** Chemistry, Biology, and one of Physics or Combined Mathematics

**Z-score context:** Occupational Therapy cutoffs are typically in the **0.6 to 1.0** range — one of the most accessible health science degrees. Graduates have strong career outcomes despite the lower entry threshold.

---

## Special Notes

- Sri Lanka has fewer than 200 qualified OTs for a population of 22 million — the shortage is extreme and employment is near-guaranteed.
- International migration of OTs is common and financially rewarding (UK OT salaries are significantly higher than Sri Lankan scales).
- Empathy, creativity, and problem-solving are the most important personal qualities for OT practitioners.
', '6c9843cd0e36494742964f37532c986f5a9244eb236f451ccb45021fcf17ea40');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('116', '# Optometry
**Course Number:** 116
**Degree:** Bachelor of Science (Honours) in Optometry
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Sri Jayewardenepura (116C)

---

## Overview

Optometry is the science and practice of eye care — examining, diagnosing, and managing visual and ocular disorders without surgical intervention. The BSc (Hons) in Optometry at the University of Sri Jayewardenepura (USJ) is the only state university optometry degree in Sri Lanka, offered through the Faculty of Allied Health Sciences. This makes USJ graduates the most sought-after optometrists in the country''s growing eye care sector.

Sri Lanka faces a significant burden of visual impairment — refractive errors, glaucoma, diabetic retinopathy, and cataract are major public health challenges. As the healthcare system expands to address non-communicable diseases, the demand for qualified optometrists in hospital eye units, optical retail chains, and community eye care programmes is growing rapidly. There are currently far fewer registered optometrists in Sri Lanka than the WHO-recommended ratio per population, creating a structural shortage that benefits new graduates.

USJ''s Faculty of Allied Health Sciences has strong clinical training links with Sri Jayewardenepura General Hospital and national eye hospitals, giving students hands-on patient exposure from the early years of study.

---

## What You Will Study

**Year 1 — Biological and Clinical Foundations:**
Anatomy and Physiology of the Eye, General Human Anatomy and Physiology, Biochemistry, Optics and Photonics, Physics of Light and Vision, Introduction to Clinical Optometry, Communication Skills for Health Professionals, Biostatistics.

**Year 2 — Core Optometry Sciences:**
Visual Optics and Refraction, Binocular Vision and Strabismus, Ocular Pharmacology, Pathology of the Eye, Contact Lens Theory and Practice (Basic), Diagnostic Instrumentation (slit lamp, ophthalmoscope, tonometer), Low Vision Assessment, Clinical Practicum I.

**Year 3 — Advanced Clinical Practice:**
Contact Lens Fitting and Management (Advanced), Paediatric Optometry, Geriatric Vision Care, Neuro-Optometry, Ocular Disease Diagnosis and Management, Dispensing Optics, Community Eye Health, Clinical Practicum II (hospital-based rotations).

**Year 4 — Specialization and Research:**
Individual research project in a clinical or scientific optometry topic. Electives from: Sports Vision, Occupational Optometry, Vision Therapy, Tele-optometry, Forensic Optometry. Extended clinical placement in eye hospitals or optical practice. Final clinical competency assessments.

---

## Career Paths in Sri Lanka

- **Hospital optometry:** Optometrists in government hospitals (National Eye Hospital, Base Hospitals), conducting routine refraction, managing pre- and post-surgical patients (cataract, LASIK), and running glaucoma screening clinics.
- **Optical retail practice:** Optometrist-in-charge at optical chains (Vision Care, Specsavers-affiliated stores, local optical shops) — performing eye examinations, prescribing glasses and contact lenses.
- **Community eye health:** Vision screening programs in schools, estate communities, and rural health campaigns run by NGOs and the Ministry of Health.
- **Contact lens practice:** Specialist contact lens practitioners, particularly for keratoconus, post-surgical fitting, orthokeratology.
- **Low vision rehabilitation:** Supporting patients with untreatable vision loss (macular degeneration, diabetic retinopathy) to maximize remaining vision.
- **Research and public health:** Academic research on Sri Lanka''s visual impairment burden, community-based intervention studies, WHO-affiliated eye health programmes.
- **Overseas practice:** Australia, UK, Canada, UAE, and Singapore recognize BSc Optometry degrees (with additional registration exams). Many Sri Lankan optometrists work abroad.
- **Postgraduate study:** MSc or MPhil in Optometry, Ophthalmology, Public Health at Peradeniya, Kelaniya, or overseas universities.

---

## Entry Requirements

**A/L Stream:** Biological Science
**Typical subjects:** Biology + Chemistry + Physics
**Z-score context:** Optometry (116C) is competitive, sitting below Medicine and Dentistry cutoffs but above many other Biological Science options. It is a popular choice for students who want a health profession career without the 5–6 year duration of Medicine. Nationally only one state university offers this programme, keeping the intake small and cutoffs relatively high.

---

## Special Notes

- **Regulated profession:** Optometrists in Sri Lanka must register with the Sri Lanka Medical Council (SLMC) or the relevant professional body. USJ''s degree is recognized for this registration.
- **USJ is the only state university** offering this degree in Sri Lanka — private optometry programmes exist but are generally not recognized at the same level for government hospital employment.
- The degree is 12 academic terms (3 terms/year × 4 years), each 10 weeks long.
- Eye care is an expanding sector as Sri Lanka''s population ages and diabetes rates rise (diabetic eye disease is now a major clinical challenge).
- Graduates interested in laser refractive surgery and ophthalmology partnerships work closely with consultant ophthalmologists at eye hospitals.
- The programme is conducted primarily in English.
', '56484fc06d0373f4d6aa85e99de50e847ec15b7e7dc7cf2d56f1269a4f92b922');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('117', '# Artificial Intelligence (B.Sc.)
**Course Number:** 117
**Degree:** Bachelor of Science (Honours) in Artificial Intelligence / B.Sc.Eng. in Computer Science and Engineering (AI Specialization)
**Duration:** 4 years
**Entry Stream:** Physical Science, Engineering Technology
**Available at:** University of Moratuwa Faculty of Engineering (117A)

---

## Overview

Artificial Intelligence is one of the newest and most exciting undergraduate programmes in Sri Lanka, introduced at the University of Moratuwa in response to the global AI revolution. As AI transforms industries — from healthcare diagnostics to autonomous vehicles to business process automation — AI engineers are among the most in-demand professionals worldwide.

Moratuwa''s AI programme combines advanced mathematics, computer science, machine learning, and domain applications. Graduates enter careers in AI research, data science, machine learning engineering, and technology product development.

---

## What You Will Study

**Year 1 — Computing and Mathematics Foundations:**
Programming (Python, C++), Calculus, Linear Algebra, Discrete Mathematics, Data Structures and Algorithms, Database Systems, Computer Architecture.

**Year 2 — Core AI and Machine Learning:**
Probability and Statistics for AI, Machine Learning I (supervised and unsupervised learning), Introduction to Neural Networks and Deep Learning, Natural Language Processing I, Computer Vision I, Software Engineering, Algorithms and Complexity.

**Year 3 — Advanced AI:**
Deep Learning (convolutional networks, recurrent networks, transformers), Reinforcement Learning, Advanced NLP (language models, BERT, GPT architectures), Computer Vision II (object detection, image segmentation), AI Ethics and Responsible AI, Robotics and Autonomous Systems, Industrial Training.

**Year 4 — Research and Specialization:**
Research Thesis (original AI research project), Advanced topics (Generative AI, Multimodal AI, AI for Healthcare, AI for Agriculture), AI Systems Engineering, Capstone project.

---

## Career Paths in Sri Lanka and Globally

- **Machine Learning Engineer:** Building and deploying ML models in production systems at tech companies, fintech, and healthcare.
- **Data Scientist:** Analysing large datasets, building predictive models, generating business insights at banks, telecoms, insurance companies.
- **Computer Vision Engineer:** Building image recognition, object detection, and video analysis systems for manufacturing, security, and healthcare.
- **NLP Engineer:** Building chatbots, language understanding systems, text analysis tools.
- **AI Researcher:** Research roles at universities, AI labs (Google DeepMind, OpenAI, Meta AI, IBM Research), and large tech companies.
- **AI Product Manager:** Leading AI product development teams.
- **International tech companies:** Sri Lankan AI graduates are actively recruited by Google, Microsoft, Amazon, Meta, and global AI startups.
- **Freelancing:** AI consulting and machine learning project work for international clients.
- **Startups:** Building AI-powered products in agriculture, healthcare, logistics, and finance.

---

## Entry Requirements

**A/L Stream:** Physical Science (mandatory — strong mathematics is essential)
**Required subjects:** Combined Mathematics, Physics, Chemistry

**Z-score context:** AI at Moratuwa is extremely competitive — cutoffs are similar to or higher than traditional Engineering specializations, typically **1.8 to 2.3+**. This is among the most sought-after programmes in the country given global AI excitement.

---

## Special Notes

- Strong mathematical ability (especially linear algebra, calculus, and probability) is essential for success in this programme — students who found A/L Combined Mathematics challenging may find the programme demanding.
- Python is the dominant AI programming language and is central to the curriculum.
- Moratuwa AI graduates are well-positioned for both local IT industry roles and international tech company positions.
- The global AI job market means that this degree has some of the strongest international career prospects of any Sri Lankan undergraduate programme.
- AI ethics, responsible AI development, and understanding of AI''s societal impacts are increasingly important parts of the curriculum.
', '85ec599295fd29b271a44f0920b7aa04e6859a0cde2ff00620f5eeebddaab21c');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('118', '# Applied Chemistry
**Course Number:** 118
**Degree:** Bachelor of Science (Honours) in Applied Chemistry
**Duration:** 4 years
**Entry Stream:** Physical Science, Biological Science
**Available at:** University of Kelaniya (118D)

---

## Overview

Applied Chemistry at the University of Kelaniya is offered by the Department of Chemistry within the Faculty of Science. Unlike a general Chemistry degree, this programme emphasizes practical industrial applications of chemistry — analytical techniques, industrial process chemistry, environmental chemistry, and research methods — making graduates directly useful in Sri Lanka''s food, pharmaceutical, textile, rubber, and manufacturing industries.

The Department of Chemistry at Kelaniya is one of the most research-active chemistry departments in Sri Lanka, with expertise in natural product chemistry, analytical chemistry, environmental chemistry, and materials science. The programme is notably internationalized — a remarkable proportion of graduates (reportedly over 80%) secure postgraduate placements at overseas universities, particularly in the USA, UK, Australia, and Japan, making it an exceptional launching pad for research careers.

Sri Lanka''s export-oriented industries (apparel, rubber, food, pharmaceuticals, cosmetics) all require chemistry graduates for quality control, R&D, and compliance. Applied Chemistry is specifically designed to produce industry-ready and research-ready graduates.

---

## What You Will Study

**Year 1 — Foundations:**
Physical Chemistry, Organic Chemistry, Inorganic Chemistry, Mathematics for Chemistry, Physics, Computer Applications for Science, Analytical Chemistry Fundamentals, Laboratory Techniques.

**Year 2 — Core Applied Chemistry:**
Spectroscopic Methods of Analysis (UV-Vis, IR, NMR, MS), Chromatography (HPLC, GC, TLC), Electroanalytical Chemistry, Organic Synthesis, Polymer Chemistry, Environmental Chemistry, Industrial Chemistry, Microbiology for Chemists, Statistics for Scientists.

**Year 3 — Specialization:**
Advanced Analytical Techniques, Medicinal Chemistry, Natural Products Chemistry, Food Chemistry and Technology, Pharmaceutical Chemistry, Water Chemistry and Treatment, Catalysis and Green Chemistry, Surface Chemistry and Materials, Industrial Training (NAITA-affiliated placement in a food, pharma, or industrial lab).

**Year 4 — Research:**
Individual research project (thesis) in an area of analytical, organic, or applied chemistry under faculty supervision. Electives from: Forensic Chemistry, Cosmetic Science, Petroleum Chemistry, Nanotechnology and Nanomaterials, Computational Chemistry.

---

## Career Paths in Sri Lanka

- **Quality control and quality assurance:** Laboratory analyst and QC chemist roles in food manufacturing (CIC, Prima, Cargills), pharmaceutical companies (CPC, Hemas, Aspen Lanka), and cosmetics (Unilever, Sunshine Holdings).
- **Food science and technology:** Product development, nutritional testing, food safety compliance for export-oriented food companies.
- **Pharmaceutical industry:** Drug formulation, active ingredient analysis, regulatory compliance — growing sector as Sri Lanka expands generic pharmaceutical production.
- **Environmental chemistry and testing:** Water quality testing, effluent monitoring, environmental consulting. Lanka Laboratories, National Water Supply and Drainage Board, industrial compliance firms.
- **Rubber and polymer industry:** Quality testing, compound development at Hayleys, Richard Pieris, Sri Lanka Rubber Research Institute.
- **Forensic science:** Government analyst''s department, police forensic labs — limited vacancies but specialist career path.
- **Postgraduate research:** This is the standout pathway — over 80% of Applied Chemistry Honours graduates pursue MSc/PhD programmes at international universities (USA, UK, Japan, Australia) in chemistry, chemical engineering, or materials science.
- **Teaching and academia:** Chemistry lecturers at National Colleges of Education, Technical Colleges, and universities.

---

## Entry Requirements

**A/L Stream:** Physical Science (primary) or Biological Science
**Typical subjects:** Physical Science: Combined Mathematics + Physics + Chemistry. Biological Science: Biology + Chemistry + Physics.
**Z-score context:** Applied Chemistry (118D) is moderately competitive within the Physical/Biological Science stream. It attracts students who are strong in Chemistry and interested in industrial or research careers. Z-score cutoffs are typically lower than Medicine or Engineering but competitive among Applied Science programmes.

---

## Special Notes

- English is the medium of instruction.
- Industrial training is arranged through NAITA (National Institute of Technical Assistance) — students complete placements in food processing, pharmaceutical, or industrial chemistry settings.
- The **exceptional postgraduate overseas placement rate** (>80% of Honours graduates) is a unique feature of this programme in Sri Lanka. Students with research ambitions should strongly consider Applied Chemistry.
- Applied Chemistry graduates who do not pursue postgraduate study typically find employment in the quality control, food safety, or environmental testing sectors within 6 months of graduation.
- The department has research collaborations with international institutions and alumni networks in the USA, Japan, and Germany.
- The ACSA (Applied Chemistry Students'' Association) at UoK is an active student body.
', 'bd69888cb947978c464ace4d51246b64e5a7646857c8752a91ddcc1ca2019d5e');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('119', '# Electronics and Computer Science
**Course Number:** 119
**Degree:** Bachelor of Science (Honours) in Electronics and Computer Science
**Duration:** 4 years
**Entry Stream:** Physical Science
**Available at:** University of Kelaniya (119D)

---

## Overview

Electronics and Computer Science (ECS) at the University of Kelaniya is one of the most distinctive degree programmes in Sri Lanka, offered jointly by the Department of Physics and Electronics and the Department of Statistics and Computer Science within the Faculty of Science. Unlike standalone CS or Electronics degrees, ECS graduates are trained to work across both the hardware and software domains — making them versatile engineers capable of bridging embedded systems, telecommunications, and software development.

Sri Lanka''s growing technology sector increasingly demands professionals who understand both hardware and software. Roles in IoT product development, embedded systems for industrial automation, telecommunications infrastructure, and smart device engineering all require exactly the dual competency that ECS develops. The programme is relatively small in intake (typically 30–40 students per year), producing graduates with a rare combination of skills and strong industry demand.

The University of Kelaniya''s Faculty of Science has a long track record in both Physics/Electronics and Computing research, with active laboratories in digital signal processing, embedded systems, and applied computing.

---

## What You Will Study

**Year 1 — Foundations:**
Mathematics for Electronics and Computing, Programming Fundamentals (Python/C), Circuit Theory and Electronics, Digital Logic Design, Discrete Mathematics, Physics of Electronic Devices, Data Structures and Algorithms, Linear Algebra.

**Year 2 — Core Hardware and Software:**
Microprocessors and Microcontrollers, Object-Oriented Programming (Java/C++), Operating Systems, Signals and Systems, Electronic Circuit Design, Database Management Systems, Computer Networks, Analog and Digital Communication Systems, Software Engineering Principles.

**Year 3 — Advanced Systems:**
Embedded Systems Design, Digital Signal Processing (DSP), VLSI Design, Artificial Intelligence and Machine Learning, Computer Architecture, Mobile and Web Application Development, Control Systems, Communication Network Protocols, Research Methods.

**Year 4 — Specialization and Research:**
Individual research project integrating hardware and software. Electives from: Internet of Things (IoT), Wireless Communications, Computer Vision, Robotics, Cybersecurity, Cloud Computing, FPGA Programming, Power Electronics. Industrial training exposure in Year 3 or 4.

---

## Career Paths in Sri Lanka

- **Embedded systems engineering:** Design and programming of microcontroller-based systems in industries like industrial automation, automotive electronics, medical devices. Sri Lankan employers include MAS Active (IoT for factories), Hayleys, Dialog Axiata''s IoT division.
- **Telecommunications and networking:** Network planning, RF engineering, ISP infrastructure management. Key employers: Dialog, Mobitel, Hutch, SLT-Mobitel, telecom equipment suppliers.
- **Software development:** ECS graduates enter software roles at Sri Lanka''s major IT firms — WSO2, IFS, Virtusa, 99X, Calcey, Cambio, and many others. The programming skills from ECS are directly applicable to full-stack, backend, and mobile development.
- **Hardware design and PCB engineering:** Electronic product design at companies involved in manufacturing, defense, and consumer electronics prototyping.
- **IoT and smart systems:** Rapidly growing sector. Sri Lanka has emerging IoT projects in smart agriculture, smart cities (Colombo Port City), and industrial automation.
- **Research and academia:** Postgraduate pathways in signal processing, embedded systems, AI hardware, or computer engineering at University of Kelaniya, University of Moratuwa, UCSC, or abroad (Australia, UK, Japan).
- **Power electronics and energy systems:** Renewable energy system control, solar inverter design, grid automation — a growing sector as Sri Lanka expands renewable energy capacity.

---

## Entry Requirements

**A/L Stream:** Physical Science
**Typical subjects:** Combined Mathematics + Physics + Chemistry (or Physics + Chemistry + another subject)
**Z-score context:** ECS (119D) is moderately competitive — it sits between the most sought-after engineering degrees and the broader science degrees. Students who narrowly miss Engineering (008) at the University of Kelaniya often find ECS as an excellent alternative, offering similarly strong career prospects. District quota applies for educationally disadvantaged districts.

---

## Special Notes

- ECS is offered **only at the University of Kelaniya** — no other state university runs this exact combined programme, making it unique in Sri Lanka.
- The dual hardware-software training is especially valuable for roles in **robotics, IoT, and embedded AI** — fields that cannot be fully served by purely CS or purely Electronics graduates.
- English is the medium of instruction.
- Students who are interested in robotics, drone engineering, or smart devices should strongly consider ECS alongside Engineering (008) programmes.
- Graduates often pursue MSc degrees in Computer Engineering, Communications Engineering, or AI at Moratuwa, UCSC, or overseas institutions.
- The programme coordinator is based in the Department of Physics and Electronics; the Faculty of Science website (science.kln.ac.lk) has the full curriculum.
', '5f8a0feb09069724baf6f8a4d26b8e0e6fa9432151877aafe9da2ff6b731f98e');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('120', '# Indigenous Medicinal Resources
**Course Number:** 120
**Degree:** Bachelor of Science (Honours) in Indigenous Medicinal Resources
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** Gampaha Wickramarachchi University of Indigenous Medicine (120P)

---

## Overview

Indigenous Medicinal Resources at Gampaha Wickramarachchi University of Indigenous Medicine (GWUIM), located in Yakkala, Gampaha District, is a programme dedicated to the scientific study, documentation, conservation, and sustainable use of Sri Lanka''s rich heritage of indigenous medicinal plants and natural health resources. The programme blends ethnobotany, plant taxonomy, phytochemistry, pharmacognosy, and Ayurvedic principles with modern botanical and chemical analysis techniques.

Sri Lanka possesses one of the most biodiverse medicinal plant floras in Asia — Vedda traditional medicine, Sinhala traditional medicine (Deshiya Chikitsa), and Ayurveda each draw from an extensive pharmacopoeia of native plants, minerals, and animal products. GWUIM was established specifically to preserve, study, and develop this indigenous knowledge through modern scientific methods.

GWUIM was elevated from an Ayurveda Institute to full university status in 2021, becoming Sri Lanka''s specialist university for indigenous medicine and health sciences. Its location in Gampaha — one of Sri Lanka''s most densely populated and economically active districts — provides both a research base and a consumer market for graduates working in wellness, herbal products, and traditional medicine services.

---

## What You Will Study

**Year 1 — Scientific and Ayurvedic Foundations:**
Botany and Plant Taxonomy (Sri Lankan medicinal flora), Ayurveda Fundamentals (principles of traditional Indian-Sri Lankan medicine), Ethnobotany and Traditional Knowledge, Organic Chemistry, Biochemistry, Introduction to Pharmacognosy, Research Methods for Indigenous Knowledge.

**Year 2 — Phytochemistry and Pharmacognosy:**
Medicinal Plant Chemistry (secondary metabolites — alkaloids, flavonoids, terpenes, glycosides), Pharmacognosy (standardization, adulteration detection, monograph writing), Ayurvedic Materia Medica (Dravyaguna), Herbal Drug Quality Assurance, Ethnomedicinal Surveys and Documentation, Medicinal Plant Conservation and Cultivation, Laboratory Analysis Techniques.

**Year 3 — Product Development and Conservation:**
Herbal Product Formulation (tablets, capsules, oils, powders, creams — Ayurvedic and modern), Regulatory Framework for Herbal Medicines (National Medicines Regulatory Authority — NMRA, Sri Lanka), Biodiversity Conservation and Protected Area Management, GIS for Medicinal Plant Distribution Mapping, Intellectual Property Rights for Traditional Knowledge, Clinical Evidence for Herbal Medicines.

**Year 4 — Research:**
Individual research project in a medicinal plant, phytochemistry, or ethnobotany topic. Electives: Marine Medicinal Resources, Microorganisms in Indigenous Medicine, Cosmeceuticals from Indigenous Plants, Nutraceuticals, Sustainable Harvesting of Wild Medicinal Plants.

---

## Career Paths in Sri Lanka

- **Herbal pharmaceutical industry:** Product development scientist, quality control analyst at herbal and Ayurvedic pharmaceutical companies (Siddhalepa, Arunalu, Nawaloka Herbal, LRIRH). Sri Lanka''s herbal products export (including Ayurvedic teas, supplements) is a growing sector.
- **Government healthcare (AYUSH):** Research and quality officer at the Department of Ayurveda, Ministry of Indigenous Medicine, Bandaranaike Memorial Ayurvedic Research Institute (BMARI).
- **Medicinal plant cultivation:** Farm manager or consultant for medicinal herb cultivation for supply to herbal manufacturers, organic exports.
- **Wildlife and forest conservation:** Medicinal plant conservation researcher at Department of Wildlife Conservation, National Herbarium (National Museum), and Biodiversity Secretariat.
- **Cosmetics and wellness products:** Natural cosmetic formulation, wellness product development at the growing herbal cosmetics sector.
- **Traditional medicine clinics:** Working alongside Ayurvedic physicians to document treatments and validate traditional practices with modern evidence.
- **Research and academia:** BMARI, Faculty of Ayurveda universities, international collaborations on traditional knowledge documentation.
- **Postgraduate study:** MSc in Pharmacognosy, Phytochemistry, Biodiversity, or Traditional Medicine at Kelaniya, Colombo, or overseas (WHO Collaborating Centres for Traditional Medicine).

---

## Entry Requirements

**A/L Stream:** Biological Science
**Typical subjects:** Biology + Chemistry + Agriculture or Physics
**Z-score context:** Indigenous Medicinal Resources (120P) at GWUIM is accessible to students with Biological Science A/L results who are genuinely interested in traditional medicine, plants, and natural product science. Z-score cutoffs reflect the specialized applicant pool and GWUIM''s newer university status.

---

## Special Notes

- **GWUIM is the only university in Sri Lanka** dedicated to indigenous medicine and health sciences — it holds a unique national mandate and position in Sri Lanka''s healthcare and wellness education landscape.
- Sri Lanka''s **herbal export sector** — including Ayurvedic teas, wellness products, and pharmaceutical-grade plant extracts — is a growth industry with increasing international demand.
- The **NMRA (National Medicines Regulatory Authority)** in Sri Lanka regulates herbal and traditional medicines. Graduates with understanding of both traditional knowledge and modern regulatory frameworks are particularly valued.
- Students interested in the intersection of traditional knowledge and modern pharmaceuticals — **bioprospecting and natural product drug discovery** — will find this degree an excellent research foundation.
- The Gampaha Wickramarachchi University campus in Yakkala has its own medicinal plant gardens and basic phytochemistry laboratories.
', 'd2ebff933e9b21dd13b6464fcec6fbb463be25745b7e5a1f0501b1413176cd29');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('121', '# Health Information and Communication Technology
**Course Number:** 121
**Degree:** Bachelor of Science (Honours) in Health Information and Communication Technology
**Duration:** 4 years
**Entry Stream:** Biological Science, Physical Science
**Available at:** Gampaha Wickramarachchi University of Indigenous Medicine (121P)

---

## Overview

Health Information and Communication Technology (Health ICT) at Gampaha Wickramarachchi University of Indigenous Medicine (GWUIM) is an interdisciplinary programme that trains professionals to manage, design, and operate the information and communication technology systems within the health sector — with a special focus on indigenous medicine, Ayurveda, and wellness information systems, alongside conventional healthcare IT.

Sri Lanka''s health sector is undergoing rapid digital transformation: Hospital Information Systems (HIS), Electronic Medical Records (EMR), telemedicine, health data analytics, and digital public health surveillance are all expanding. At the same time, the indigenous medicine sector — which operates thousands of Ayurveda clinics, dispensaries, and wellness centres across Sri Lanka — increasingly needs IT professionals who understand both healthcare and technology.

GWUIM''s Health ICT programme uniquely combines healthcare informatics skills with a grounding in indigenous medicine context, producing graduates who can serve in both conventional and traditional healthcare IT roles. The programme is offered as part of GWUIM''s expansion beyond its traditional Ayurveda focus into technology and management disciplines.

---

## What You Will Study

**Year 1 — Foundations:**
Computer Fundamentals, Programming Basics (Python), Health Sciences Overview (Ayurveda system, conventional healthcare system in Sri Lanka), Human Anatomy and Physiology for IT Professionals, Database Fundamentals, Mathematics and Statistics for Health Sciences, Medical Terminology.

**Year 2 — Health Informatics Core:**
Health Information Systems (HIS design, EMR systems), Database Design and Management for Healthcare, Web Development for Health Portals, Health Data Privacy and Security, Hospital Management System Operations, Telemedicine Concepts and Technology, Health Statistics and Epidemiology Data Management.

**Year 3 — Advanced Applications:**
Health Data Analytics (analyzing patient data, disease trends, health outcomes), Mobile Health (mHealth) Applications, Electronic Health Records (EHR) Standards (HL7, FHIR), GIS for Public Health, Ayurveda Practice Management Systems (digitizing traditional medicine records), E-health Policy and Regulation, Research Methods in Health Informatics.

**Year 4 — Research and Project:**
Individual project in health ICT (design/implement a health IT system or analyze a health data challenge). Electives: AI in Healthcare, Wearables and IoT in Health Monitoring, Health Cybersecurity, Bioinformatics Basics, Digital Health Entrepreneurship.

---

## Career Paths in Sri Lanka

- **Hospital IT management:** IT officer, health informatics manager at government and private hospitals running electronic health record systems and hospital management software.
- **Ministry of Health IT Division:** Digital health project officers supporting the Health Information System of the Ministry of Health — a rapidly expanding government digital health programme.
- **Telemedicine and mHealth ventures:** Technical support and project management at telemedicine startups and digital health companies emerging in Sri Lanka.
- **Ayurveda and indigenous medicine sector IT:** System administrator and IT support for the Department of Ayurveda''s management information systems, and for private Ayurvedic hospital chains.
- **Health NGOs:** IT officer at UNICEF, WHO, PATH, and other health-focused NGOs managing health data collection (ODK, CommCare) and reporting.
- **Private health IT companies:** Software support, implementation, and helpdesk roles at healthcare IT vendors.
- **Health data analysis:** Junior health analyst at National Institute of Health Sciences, Epidemiology Unit of the Ministry of Health.
- **Postgraduate study:** MSc in Health Informatics, IT Management, or Public Health (with IT specialization) at local or overseas universities.

---

## Entry Requirements

**A/L Stream:** Biological Science (primary), Physical Science
**Typical subjects:** Biology + Chemistry + Physics or Combined Mathematics + Physics + Chemistry
**Z-score context:** Health ICT (121P) at GWUIM serves students interested in the technology side of healthcare. It is accessible to students with moderate A/L results in either science stream who want a career at the health-IT intersection rather than clinical practice.

---

## Special Notes

- This programme is suitable for students who are interested in healthcare but prefer **IT and systems work over direct patient care**.
- **GWUIM''s indigenous medicine context** means graduates gain familiarity with Ayurveda healthcare systems alongside conventional health IT — a rare combination.
- Sri Lanka''s Ministry of Health is actively investing in **digital health infrastructure** through the e-health project — creating sustained government sector demand for health IT professionals.
- Graduates who obtain certifications in health IT (HL7, FHIR, HIMSS CAHIMS) alongside this degree significantly enhance their employability in the growing global health informatics field.
', '89713fcfef58c35b04ff6026111fc1320292e1fe10cb222e4a42724ff3eeea2b');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('122', '# Health Tourism and Hospitality Management
**Course Number:** 122
**Degree:** Bachelor of Science (Honours) in Health Tourism and Hospitality Management
**Duration:** 4 years
**Entry Stream:** Biological Science, Arts, Commerce
**Available at:** Gampaha Wickramarachchi University of Indigenous Medicine (122P)

---

## Overview

Health Tourism and Hospitality Management at Gampaha Wickramarachchi University of Indigenous Medicine (GWUIM) is a pioneering programme in Sri Lanka that addresses the rapidly expanding global market for Ayurvedic wellness tourism, medical tourism, and traditional medicine-based hospitality. Sri Lanka is internationally recognized as a destination for Ayurveda wellness retreats, and this programme trains professionals to manage and promote this unique industry.

Sri Lanka''s health and wellness tourism sector generates significant foreign exchange revenue. Hundreds of Ayurvedic resorts, wellness retreats, spas, and yoga centres — concentrated in Beruwala, Bentota, Negombo, Hikkaduwa, and the hill country — cater to European, Australian, and Asian tourists seeking authentic Ayurvedic treatments and wellness experiences. Managing these establishments requires professionals who understand both hospitality operations AND the health/wellness service delivery.

Sri Lanka Tourism Development Authority (SLTDA) actively promotes Sri Lanka as a wellness tourism destination under the "Wellness Island" branding. GWUIM, as the country''s indigenous medicine university, is uniquely positioned to prepare graduates for this sector.

---

## What You Will Study

**Year 1 — Foundations:**
Introduction to Tourism and Hospitality Management, Ayurveda Wellness Fundamentals (principles of Ayurveda, common treatments, diet and lifestyle), Human Physiology and Wellness, Hotel and Resort Operations, Business Communication, Computer Applications, Sri Lankan Culture and Heritage for Tourism.

**Year 2 — Hospitality Core:**
Food and Beverage Management (Ayurvedic cuisine, therapeutic diets), Accommodation Management, Front Office and Housekeeping Operations, Event and Programme Management, Marketing Principles for Tourism, Customer Relationship Management, Spa and Wellness Centre Operations, Financial Management for Hospitality.

**Year 3 — Health Tourism Specialization:**
Medical Tourism Management (patient coordination, cross-border healthcare facilitation), Wellness Programme Design (Panchakarma packages, yoga retreats, detox programmes), Quality Standards for Health Tourism (NABH, ISO 9001 for wellness facilities), Tourism Law and Regulations, International Health Tourism Markets (European, Middle Eastern, Asian), Digital Marketing and Social Media for Wellness Tourism, Research Methods.

**Year 4 — Research and Industry:**
Industry Placement (extended internship at an Ayurvedic resort or wellness centre). Individual research project in health tourism, wellness management, or hospitality. Electives: Health Tourism Destination Development, Sustainable Tourism, Heritage Tourism, Luxury Hospitality Management.

---

## Career Paths in Sri Lanka

- **Ayurvedic resort management:** Resort manager, wellness programme coordinator, operations manager at Sri Lanka''s Ayurvedic hotel chains (Barberyn Beach Ayurveda Resort, Santani Wellness, Siddhalepa Ayurveda Resorts, Jetwing Ayurveda) — major employers in the Ayurvedic wellness tourism sector.
- **Spa and wellness centre management:** Spa manager, wellness coordinator at hotel spas, standalone wellness centres, and urban Ayurvedic clinics targeting health-conscious city residents.
- **Medical tourism coordination:** Patient coordinator, medical tourism manager at hospitals and clinics attracting international patients (Lanka Hospitals, Apollo Lanka, Asiri Hospitals for cosmetic and elective procedures).
- **Tourism management:** Programme officer at Sri Lanka Tourism Promotion Bureau, SLTDA wellness standards division, and tourism development consultancy.
- **Overseas hospitality:** Wellness tourism is a global industry — graduates can find employment at Ayurvedic resorts and wellness hotels in India (Kerala), Maldives, UAE, UK, Germany, and Australia.
- **Health tourism entrepreneurship:** Starting a small Ayurvedic wellness centre, yoga retreat, or wellness tour operation in Sri Lanka.
- **Destination management companies:** DMCs specializing in wellness tourism itineraries for incoming foreign visitors.

---

## Entry Requirements

**A/L Stream:** Biological Science (primary), Arts, Commerce
**Typical subjects:** Science stream (Biology) or any Arts/Commerce combination. The programme values both science understanding of health and business/hospitality management skills.
**Z-score context:** Health Tourism and Hospitality Management (122P) is accessible to a wider range of A/L students across multiple streams. Cutoffs reflect the specialized applicant pool and GWUIM''s newer university status.

---

## Special Notes

- **Sri Lanka''s Ayurvedic wellness tourism** is internationally recognized and generates significant foreign exchange. This is not a niche hobby sector — it is a mature industry with multi-million dollar resort properties and international clientele.
- Graduates who combine this degree with **SLTDA guide licensing** or hotel management professional qualifications (AHLEI — American Hotel and Lodging Education Institute) significantly enhance employability.
- **Overseas employment opportunity** is genuine — Ayurvedic and wellness resorts across South and Southeast Asia actively recruit Sri Lankan graduates familiar with traditional medicine.
- The programme bridges two sectors that don''t often intersect: healthcare and hospitality. Students who are comfortable in both environments — interacting with patients/guests AND managing hotel-style operations — will thrive.
- The growing interest in **preventive health and wellness among urban Sri Lankans** is also creating demand for wellness centres catering to the domestic market, not just foreign tourists.
', 'ca63d0cf6716a1eda0b3f9a2b16dc4db56817962fd13bbd37057a91388564017');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('123', '# Biomedical Technology
**Course Number:** 123
**Degree:** Bachelor of Science (Honours) in Biomedical Technology
**Duration:** 4 years
**Entry Stream:** Biological Science, Physical Science
**Available at:** Gampaha Wickramarachchi University of Indigenous Medicine (123P)

---

## Overview

Biomedical Technology at Gampaha Wickramarachchi University of Indigenous Medicine (GWUIM) trains graduates to work with the medical equipment, diagnostic devices, and health technology systems used in modern healthcare. Biomedical technologists (also called clinical engineers or biomedical engineers in some contexts) install, calibrate, maintain, and repair the sophisticated equipment found in hospitals — from ventilators and infusion pumps to MRI scanners and laboratory analyzers.

Sri Lanka''s expanding healthcare infrastructure — driven by government hospital upgrades, private hospital growth, and import of advanced medical equipment — creates steady demand for Biomedical Technology graduates. Every new hospital that installs CT scanners, patient monitors, dialysis machines, or operating theatre equipment needs trained professionals to maintain and troubleshoot these systems. Currently, many Sri Lankan hospitals rely on equipment supplier engineers or minimally trained technicians for maintenance — formally qualified biomedical technologists are in short supply.

GWUIM''s programme in Biomedical Technology is part of its expansion into health sciences beyond traditional Ayurveda, positioning the university as a broad health sciences institution in addition to its indigenous medicine specialization.

---

## What You Will Study

**Year 1 — Science and Technology Foundations:**
Human Anatomy and Physiology, Electrical and Electronic Fundamentals, Physics of Measurement and Instrumentation, Medical Terminology, Computer Applications, Mathematics and Statistics for Health Technology, Introduction to Biomedical Equipment.

**Year 2 — Diagnostic Equipment:**
Diagnostic Imaging Equipment (X-ray, ultrasound, CT principles — operation and maintenance), Patient Monitoring Systems (ECG, pulse oximetry, blood pressure monitors, patient monitors), Laboratory Diagnostic Equipment (blood analyzers, centrifuges, spectrophotometers), Electrical Safety in Hospitals, Biomedical Signals Processing, Medical Device Regulations.

**Year 3 — Therapeutic and Advanced Equipment:**
Life Support Equipment (ventilators, defibrillators, infusion pumps, anaesthesia machines), Operating Theatre Technology, Dialysis Machine Operation and Maintenance, Prosthetics and Orthotics Technology Basics, Clinical Laboratory Automation Systems, Hospital Equipment Management and Procurement, Research Methods.

**Year 4 — Research and Practicum:**
Extended clinical placement in a hospital biomedical department. Individual research project in medical equipment assessment, maintenance optimization, or health technology evaluation. Electives: Telemedicine Technology, Rehabilitation Engineering, Biomaterials, Medical Device Innovation.

---

## Career Paths in Sri Lanka

- **Hospital biomedical departments:** The primary employer. Government hospitals (Colombo National, Teaching Hospitals) and private hospitals (Nawaloka, Durdans, Lanka, Asiri, Hemas) maintain biomedical engineering departments responsible for all medical equipment.
- **Ministry of Health Medical Supplies Division:** Medical equipment procurement, acceptance testing, and lifecycle management for government hospital equipment.
- **Medical equipment suppliers and service companies:** Technical representative, field service engineer at companies supplying medical equipment — Siemens Healthineers Lanka, Philips Healthcare Sri Lanka, GE Healthcare distributors, local medical equipment importers.
- **Private diagnostic centres:** Equipment operator and maintenance technician at radiology centres, cardiac labs, and clinical laboratory facilities.
- **Medical device regulation:** NMRA (National Medicines Regulatory Authority) — medical device registration and post-market surveillance (an emerging regulatory area in Sri Lanka).
- **Overseas:** Australia, UK, UAE, and Gulf countries have established career pathways for biomedical technologists — registration requirements vary but Sri Lankan graduates are generally employable.
- **Postgraduate study:** MSc in Biomedical Engineering, Clinical Engineering, or Health Technology Assessment.

---

## Entry Requirements

**A/L Stream:** Biological Science (primary), Physical Science
**Typical subjects:** Biology + Chemistry + Physics or Combined Mathematics + Physics + Chemistry (Physics is essential)
**Z-score context:** Biomedical Technology (123P) at GWUIM is accessible to students with solid science backgrounds in either stream who are interested in the technical aspects of healthcare rather than clinical practice. Z-score cutoffs reflect the programme''s specialization and GWUIM''s newer university status.

---

## Special Notes

- **Biomedical technology is distinct from Biomedical Science** (which focuses on laboratory diagnostics and clinical pathology) and **Medical Physics** (which focuses on radiation in therapy and imaging). Biomedical Technology is specifically about equipment engineering and maintenance.
- Sri Lanka currently has a **shortage of qualified biomedical technologists** — many hospitals rely on equipment supplier engineers for maintenance, which is costly and inefficient. Formally trained graduates fill a genuine gap.
- **Hospital accreditation requirements** (JCI, NABH) increasingly require documented biomedical equipment management programmes — further driving demand for trained professionals.
- Students with a strong interest in electronics, physics, and problem-solving (rather than biology) may find the Physical Science pathway more comfortable for this programme.
- The programme prepares students for the **Biomedical Engineering Society of Sri Lanka (BESSL)** professional community and associated international networking.
', '0c4d4c3a176a5ef9e201b6c2bead183f3da21231e2e11e9c37776130dc3392a3');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('124', '# Indigenous Pharmaceutical Technology
**Course Number:** 124
**Degree:** Bachelor of Science (Honours) in Indigenous Pharmaceutical Technology
**Duration:** 4 years
**Entry Stream:** Biological Science, Physical Science
**Available at:** Gampaha Wickramarachchi University of Indigenous Medicine (124P)

---

## Overview

Indigenous Pharmaceutical Technology at Gampaha Wickramarachchi University of Indigenous Medicine (GWUIM) focuses on the preparation, formulation, standardization, quality control, and manufacturing technology of traditional Ayurvedic and indigenous pharmaceutical products — the medicines used in Sri Lanka''s traditional healthcare system. These include herbal tablets (Kashaya), medicated ghee (Ghruta), medicated oils (Taila), decoctions (Kwatha), powders (Churna), and herbal confections (Lehya).

Sri Lanka has a thriving indigenous pharmaceutical industry — companies like Siddhalepa, Arunalu, Nawaloka Herbal, Link Natural Products, and the Government''s Bandaranaike Memorial Ayurvedic Research Institute (BMARI) manufacture and market Ayurvedic products domestically and for export. The industry is subject to increasing regulatory scrutiny through the National Medicines Regulatory Authority (NMRA), requiring graduates who understand both traditional formulation AND modern pharmaceutical manufacturing and quality standards.

GWUIM is uniquely positioned to offer this programme — as Sri Lanka''s dedicated indigenous medicine university, it has faculty with deep expertise in Ayurvedic pharmacology and formulation science, alongside access to medicinal plant gardens for practical training.

---

## What You Will Study

**Year 1 — Foundational Sciences:**
Pharmacognosy Fundamentals (identification and authentication of medicinal plants), Organic and Inorganic Chemistry, Biochemistry Basics, Ayurveda Basics (core principles, Pancha Bhuta, Tridosha theory), Pharmaceutical Calculations, Laboratory Skills, Anatomy and Physiology.

**Year 2 — Indigenous Pharmaceutical Preparation:**
Ayurvedic Pharmacopoeia (official Ayurvedic monographs — Indian Pharmacopoeia of Ayurveda, Sinhala traditional formulations), Preparation of Classical Ayurvedic Formulations (Asavas, Arishtas, Avalehas, Taila, Ghrita, Bhasmas — metallic preparations), Physical Pharmacy of Herbal Products, Quality Assessment of Traditional Medicines (physical, chemical, biological testing), Modern Analytical Techniques for Herbal Quality Control.

**Year 3 — Pharmaceutical Technology and Quality:**
GMP (Good Manufacturing Practice) for Ayurvedic Pharmaceuticals, Pharmaceutical Equipment and Process Technology (granulation, tablet pressing, capsule filling, oil extraction), Herbal Product Stability Testing, NMRA Regulatory Requirements for Traditional Medicines, Export Market Standards (EU, USA, WHO monographs for herbal medicines), Pilot Plant Operations, Research Methods.

**Year 4 — Research and Industry:**
Factory Attachment at an Ayurvedic pharmaceutical manufacturing facility. Individual research project in indigenous pharmaceutical formulation, quality analysis, or stability. Electives: Nutraceuticals and Functional Foods, Cosmeceuticals from Indigenous Plants, Biopharmaceutics of Herbal Drugs, Herbal Drug Registration.

---

## Career Paths in Sri Lanka

- **Ayurvedic pharmaceutical manufacturing:** Formulation officer, production manager, quality control analyst at indigenous pharmaceutical companies — Siddhalepa, Arunalu, Link Natural Products, Nawaloka Herbal, BMARI, and smaller traditional medicine manufacturers.
- **Quality control and regulatory:** Quality assurance officer responsible for GMP compliance and NMRA registration of Ayurvedic products.
- **Government pharmaceutical sector:** BMARI (Bandaranaike Memorial Ayurvedic Research Institute) — government''s main Ayurvedic medicine manufacturer and research facility. Government Ayurveda Drug Corporation.
- **Herbal export industry:** Quality and regulatory manager for companies exporting Ayurvedic products to EU, USA, and Asian markets (each has different regulatory requirements for herbal medicines).
- **Research:** Product development researcher at GWUIM, BMARI, or private companies developing new traditional formulations or evidence-based improvements of classical medicines.
- **Herbal cosmetics and personal care:** Formulation scientist for cosmeceuticals and herbal personal care products — a rapidly growing consumer market in Sri Lanka and globally.
- **Hospital pharmacy (Ayurveda):** Dispensing and preparing medicines at government Ayurveda hospitals (there are over 4,000 government Ayurveda practitioners in Sri Lanka).
- **Postgraduate study:** MSc in Pharmacognosy, Phytochemistry, Pharmaceutical Sciences, or Traditional Medicine.

---

## Entry Requirements

**A/L Stream:** Biological Science (primary), Physical Science (Chemistry essential in both cases)
**Typical subjects:** Biology + Chemistry + Physics or Combined Mathematics + Chemistry + Physics
**Z-score context:** Indigenous Pharmaceutical Technology (124P) is a specialized programme at GWUIM. It appeals to students interested in both traditional medicine and pharmaceutical science. Z-score cutoffs are moderate, accessible to students with solid science results who may not reach conventional Pharmacy or Medicine cutoffs.

---

## Special Notes

- This programme is **distinct from the mainstream Pharmacy degree** (offered at Peradeniya and USJ faculties of pharmacy) — it focuses specifically on indigenous/Ayurvedic pharmaceutical technology rather than conventional Western pharmaceutical practice.
- The **NMRA regulatory landscape for herbal medicines** in Sri Lanka is tightening, with mandatory registration of all marketed traditional medicines — creating growing career demand for graduates who understand indigenous formulations AND modern regulatory requirements.
- Sri Lanka''s Ayurvedic pharmaceutical industry is increasingly exporting to global wellness markets — graduates who can navigate both traditional formulation knowledge and international herbal medicine regulations are highly sought.
- Students interested in the science of **Bhasma** (metallic preparations used in Ayurveda — a unique and highly specialized area requiring both chemistry and Ayurvedic knowledge) will find this programme one of very few globally that trains in this practice under proper scientific oversight.
', 'bcdf819484e79c70ab555e9e7a98a4486b2c97a2ec568d301e34a7c700f7c340');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('125', '# Yoga and Parapsychology
**Course Number:** 125
**Degree:** Bachelor of Science (Honours) in Yoga and Parapsychology
**Duration:** 4 years
**Entry Stream:** Biological Science, Arts
**Available at:** Gampaha Wickramarachchi University of Indigenous Medicine (125P)

---

## Overview

Yoga and Parapsychology at Gampaha Wickramarachchi University of Indigenous Medicine (GWUIM) is a unique and pioneering degree — the first and only such programme at a state university in Sri Lanka, and one of very few worldwide that formally studies Yoga science alongside Parapsychology within a university academic framework. The programme blends the ancient Indian-Sri Lankan tradition of Yoga as a health and philosophical discipline with the scientific study of consciousness, mind-body interactions, meditation, and parapsychological phenomena.

Yoga is no longer simply a traditional spiritual practice — it is a global wellness industry worth billions of dollars, with certified Yoga instructors, therapeutic yoga practitioners, and yoga therapists in high demand worldwide. At the same time, there is growing scientific and academic interest in the mind-body connection, consciousness studies, meditation science, and traditional psychosomatic healing systems. GWUIM addresses this at the academic level within an indigenous medicine context.

The programme trains students in classical Yoga (Hatha, Pranayama, Meditation, Raja Yoga), physiological and psychological aspects of Yoga practice, Parapsychology research methods, and the therapeutic applications of Yoga for physical and mental health conditions — preparing graduates for careers in wellness, therapeutic yoga, research, and teaching.

---

## What You Will Study

**Year 1 — Yoga Foundations:**
Classical Yoga Philosophy (Patanjali''s Yoga Sutras, Samkhya philosophy), Hatha Yoga Practice (Asana, Pranayama, Bandha, Mudra), Human Anatomy and Physiology (musculoskeletal, respiratory, nervous systems for Yoga), Introduction to Parapsychology (history, scope, key concepts), Psychology Fundamentals, Ayurveda and Yoga Connection, Scientific Research in Yoga.

**Year 2 — Therapeutic Yoga and Consciousness:**
Yoga Therapy for Common Conditions (stress, hypertension, diabetes, back pain, depression — evidence-based applications), Advanced Pranayama Techniques (effects on autonomic nervous system), Meditation Science (neuroscience of meditation, mindfulness, EEG studies), Parapsychology Research Areas (telepathy, psychokinesis, near-death experience — scientific approaches), Psychology of Religion and Spiritual Experience, Sports and Performance Yoga.

**Year 3 — Applied Practice:**
Teaching Methodology for Yoga (curriculum design, sequencing classes, adapting for different populations), Yogic Management of Mental Health Disorders (evidence-based protocols for anxiety, depression, PTSD), Indigenous Healing Practices of Sri Lanka, Research Methods in Yoga and Parapsychology, Yoga and Women''s Health (prenatal, postnatal yoga), Elderly Care Yoga, Yoga for Special Populations (children, athletes, rehabilitation patients).

**Year 4 — Research:**
Supervised research project in yoga science, meditation neuroscience, or parapsychology. Electives: Yoga and Neurophenomenology, Integrative Medicine (combining Yoga with Ayurveda/allopathic approaches), International Yoga Teacher Training standards (Yoga Alliance alignment), Cosmic Healing Practices.

---

## Career Paths in Sri Lanka

- **Yoga instructor and therapist:** Teaching yoga at hotels, wellness centres, yoga studios, gyms, corporate wellness programmes, hospitals (rehabilitation), and schools. Sri Lanka''s tourism sector — particularly Ayurvedic wellness resorts — employs yoga instructors for international guests.
- **Therapeutic yoga practitioner:** Working alongside healthcare providers (physiotherapists, psychiatrists, general practitioners) using Yoga as an evidence-based complementary therapy for specific health conditions.
- **Hospital and clinic wellness programmes:** Running yoga and meditation therapy sessions at hospitals and wellness clinics — a growing practice as Sri Lankan healthcare acknowledges mind-body approaches.
- **Corporate wellness:** Employee wellness programme coordinator running yoga, mindfulness, and stress management workshops for organizations. Growing demand in Colombo''s corporate sector.
- **International yoga teaching:** Sri Lankan yoga teachers work in UAE, UK, Australia, Singapore, and Europe — global demand for yoga instructors is substantial. Yoga Alliance (USA) certification alongside this degree opens international doors.
- **Research and academia:** Research on the physiological effects of yoga (inflammation markers, cortisol, brain imaging), parapsychology, or consciousness at GWUIM and international research partnerships.
- **Yoga centre entrepreneurship:** Founding and managing a yoga studio or wellness centre — a realistic small business model in Sri Lanka''s growing wellness market.
- **School yoga:** Teaching yoga in schools as part of physical education and mindfulness programmes.

---

## Entry Requirements

**A/L Stream:** Biological Science (primary), Arts
**Typical subjects:** Biological Science or any Arts combination. Physical fitness and aptitude for yoga practice are important.
**Z-score context:** Yoga and Parapsychology (125P) is a highly specialized programme with a distinct applicant pool. Z-score cutoffs are accessible to students with reasonable A/L results who have a genuine passion for yoga, wellness, and mind-body science. It is not a programme chosen primarily by score — students must genuinely want to work in the wellness and yoga sector.

---

## Special Notes

- **This is the only BSc in Yoga and Parapsychology in Sri Lanka** — graduates will have a unique qualification in a growing global wellness field.
- **International recognition:** Aligning studies with Yoga Alliance (USA) RYT 200 or RYT 500 standards during the degree significantly enhances international employability. The degree programme''s rigour should help graduates obtain these internationally recognized teaching credentials.
- The **parapsychology component** is studied scientifically — using research methods, controlled experiments, and critical analysis — not as mysticism. It encompasses consciousness studies, extraordinary human experience research, and mind-body phenomena.
- **Sri Lanka''s Ayurvedic tourism sector** employs yoga instructors as integral parts of wellness retreat programmes — this is the most immediate and reliable employment pathway for graduates.
- Students who also have skills in **meditation teaching** (Vipassana, Samatha) can develop a complementary practice combining yoga and Buddhist-derived mindfulness — highly marketable globally.
- Physical health and the ability to practice and demonstrate yoga asanas are important practical requirements for this programme.
', '75b3803f61a43e9a4f881f27116206d12ab897574229c165848c4e2f4754d5d1');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('126', '# Social Studies in Indigenous Knowledge
**Course Number:** 126
**Degree:** Bachelor of Arts (Honours) in Social Studies in Indigenous Knowledge
**Duration:** 4 years
**Entry Stream:** Arts, Biological Science
**Available at:** Gampaha Wickramarachchi University of Indigenous Medicine (126P)

---

## Overview

Social Studies in Indigenous Knowledge at Gampaha Wickramarachchi University of Indigenous Medicine (GWUIM) is a unique interdisciplinary programme that studies the social, cultural, and community dimensions of indigenous knowledge systems — particularly traditional medicine, healing practices, ecological knowledge, and cultural heritage in Sri Lanka. The programme draws on sociology, anthropology, ethnography, oral history, cultural studies, and policy analysis to understand how indigenous knowledge is maintained, transmitted, challenged, and revitalized in modern Sri Lankan society.

Sri Lanka has extraordinarily rich indigenous knowledge traditions: Vedda healing practices, Sinhala traditional medicine, Kandyan ceremonial systems (Kohomba Kankariya, Tovil), traditional ecological knowledge of rural and coastal communities, and Ayurveda as a living intellectual system. All of these face pressures from modernization, urbanization, and the dominance of biomedical healthcare. At the same time, there is growing global recognition of the value of indigenous knowledge — in biodiversity conservation, sustainable agriculture, mental health, and cultural resilience.

GWUIM is uniquely positioned to offer this programme because it is embedded in the indigenous medicine tradition while also being a modern academic institution, creating space for both deep engagement with tradition and critical scholarly analysis.

---

## What You Will Study

**Year 1 — Foundations:**
Introduction to Indigenous Knowledge Systems (Sri Lankan and global perspectives), Social Science Research Methods, Sociology Fundamentals, Anthropology of Health and Healing, Sinhala Culture and Identity, History of Traditional Medicine in Sri Lanka, Introduction to Ethnography, Community Development Principles.

**Year 2 — Core Social Studies:**
Ethnobotanical Knowledge and Its Social Dimensions, Oral Traditions and Knowledge Transmission, Sociology of Traditional Healing Communities, Indigenous Ecological Knowledge and Environmental Management, Cultural Heritage Documentation Methods, Policy and Law for Indigenous Knowledge Protection (TRIPS, CBD — Convention on Biological Diversity), Gender in Traditional Knowledge Systems.

**Year 3 — Applied Studies:**
Intellectual Property Rights for Indigenous Communities (protecting traditional knowledge from biopiracy), Biocultural Diversity (links between linguistic, cultural, and biological diversity), Community-Based Natural Resource Management, Revitalization of Endangered Indigenous Practices, Ethnographic Field Research (community immersion projects), Media and Indigenous Knowledge Communication (documenting and sharing through film, audio, digital archives), Research Methods II.

**Year 4 — Research:**
Extended community-based research project resulting in a thesis. Fieldwork with traditional practitioners, indigenous communities, or cultural institutions. Electives: Digital Heritage and Archiving, Indigenous Knowledge and Climate Change Adaptation, Comparative Indigenous Knowledge (global case studies), Policy Advocacy for Traditional Communities.

---

## Career Paths in Sri Lanka

- **Cultural heritage documentation:** Researcher or documenter at Department of National Museums, Department of Cultural Affairs, Postgraduate Institute of Archaeology, UNESCO culture programmes — recording and preserving intangible cultural heritage.
- **Indigenous knowledge policy:** Policy officer at National Intellectual Property Office (NIPO) — particularly in traditional knowledge protection units; Ministry of Indigenous Medicine.
- **NGO and development sector:** Community development officer, cultural rights advocate, rural livelihoods researcher at NGOs working with indigenous and rural communities (Practical Action, Sevalanka, MONLAR).
- **Community health programmes:** Liaison officer between conventional health systems and traditional healing communities — facilitating integration of traditional and modern healthcare at community level.
- **Academic research:** Research assistant and academic lecturer at GWUIM, social science departments of state universities, and international university collaborations studying indigenous knowledge in South Asia.
- **Media and journalism:** Specialist journalist or documentary filmmaker focused on indigenous culture, traditional medicine, and environmental knowledge — Sri Lanka''s media has growing interest in heritage content.
- **Biodiversity conservation:** Ethnobiologist and community liaison officer at Department of Wildlife Conservation and biodiversity projects — indigenous knowledge informs sustainable use of natural resources.

---

## Entry Requirements

**A/L Stream:** Arts (primary), Biological Science
**Typical subjects:** Arts subjects (Sinhala, History, Political Science, Geography, Sociology, etc.) or Biological Sciences.
**Z-score context:** Social Studies in Indigenous Knowledge (126P) is a highly specialized, relatively niche programme. Z-score cutoffs reflect the unique applicant pool — students who are genuinely interested in traditional culture, social sciences, and indigenous heritage rather than mainstream career tracks.

---

## Special Notes

- This programme is **deeply relevant to Sri Lanka''s cultural policy challenges** — the country is navigating how to preserve traditional knowledge while integrating into the global knowledge economy. Graduates contribute directly to these national conversations.
- The **Convention on Biological Diversity (CBD)** and Nagoya Protocol (which Sri Lanka has ratified) create legal frameworks for protecting traditional knowledge from commercial exploitation without community consent — graduates with expertise in this area serve an important policy function.
- Students who combine this degree with **Sinhala or Tamil language skills, digital archiving proficiency, and ethnographic research skills** will have distinctive capabilities valued by international organizations (UNESCO, WHO Traditional Medicine programmes, WIPO).
- The programme is conducted in a combination of Sinhala and English.
- This is one of the **most academically innovative** programmes in GWUIM''s portfolio, reflecting the university''s mission to bring scholarly rigor to the study of Sri Lanka''s indigenous heritage.
', '438296f51d113b3875404e4542d5e2c7ea6cdcd16977c4cef8ed95a83211336e');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('127', '# Accounting Information Systems
**Course Number:** 127
**Degree:** Bachelor of Science (Honours) in Accounting Information Systems
**Duration:** 4 years
**Entry Stream:** Commerce, Arts (with Mathematics), Physical Science
**Available at:** University of Kelaniya (127D)

---

## Overview

Accounting Information Systems (AIS) at the University of Kelaniya is a distinctive interdisciplinary degree offered by the Faculty of Commerce and Management Studies that sits at the intersection of accounting, information technology, and management. Unlike a traditional Accountancy degree, AIS specifically prepares graduates to design, implement, audit, and manage computerized accounting systems and enterprise software — skills that are increasingly critical as Sri Lankan businesses digitize their finance and ERP functions.

The global shift towards digital finance — ERP systems (SAP, Oracle, Sage), cloud accounting (Xero, QuickBooks), and automated financial reporting — means that professionals who understand both accounting principles AND IT architecture are in extremely high demand. Sri Lanka''s growing IT services and BPO sectors are significant employers of AIS graduates, alongside conventional accounting employers.

The University of Kelaniya''s Faculty of Commerce and Management Studies has produced many of Sri Lanka''s leading accountants and finance professionals, and the AIS programme builds on this reputation with a technology-forward curriculum designed for the modern digital economy.

---

## What You Will Study

**Year 1 — Foundations:**
Financial Accounting, Business Mathematics and Statistics, Principles of Management, Computer Fundamentals and Office Applications, Microeconomics, Business Communication, Programming for Business (Python/Excel VBA basics), Cost and Management Accounting.

**Year 2 — Core AIS:**
Database Design and Management, Accounting Information Systems Design, Enterprise Resource Planning (ERP) — SAP fundamentals, Financial Management, Auditing Principles, Business Analytics, Systems Analysis and Design, Business Taxation, Management Information Systems.

**Year 3 — Advanced IT and Finance:**
IT Audit and Assurance, Cybersecurity for Business, Cloud Accounting Platforms (Xero, QuickBooks), Advanced ERP Configuration, Business Intelligence and Data Warehousing, Forensic Accounting and Fraud Detection, Corporate Governance, Advanced Taxation, Research Methods.

**Year 4 — Research and Specialization:**
Individual research project in an AIS, accounting technology, or digital finance topic. Electives from: Blockchain in Finance, Fintech and Digital Banking, Data Analytics for Accountants, Healthcare Finance Systems, Government Accounting Information Systems.

---

## Career Paths in Sri Lanka

- **ERP implementation and consulting:** SAP, Oracle, and Sage consultants who implement enterprise financial systems at large companies. This is among the highest-paying roles for accounting graduates in Sri Lanka, with major consulting firms (PwC, Deloitte, KPMG, Ernst & Young) actively recruiting AIS graduates.
- **IT audit:** Internal and external IT auditors who review the integrity and security of financial systems. Chartered accountancy firms, internal audit departments of banks and conglomerates.
- **Systems accountant:** Finance departments of large organizations managing their ERP configuration, financial data quality, and reporting automation.
- **Business analytics and BI:** Using Power BI, Tableau, and SQL to analyze financial data — growing role in banks, insurance companies, and retail conglomerates (Hayleys, John Keells).
- **Fintech and digital banking:** Sri Lanka''s Central Bank-licensed fintech companies, digital payment operators, and crypto-adjacent financial services.
- **Professional accountancy:** AIS graduates can proceed to ICASL (CA Sri Lanka), CIMA, ACCA, or CPA Australia alongside employment — AIS provides strong exam exemptions.
- **Government IT audit:** National Audit Office Sri Lanka, Auditor General''s Department — reviewing public sector financial systems.

---

## Entry Requirements

**A/L Stream:** Commerce (primary — Accounting + Business Studies + Economics is most common). Arts with Mathematics. Some Physical Science students are also eligible.
**Typical subjects:** Accounting + Business Studies + Economics (Commerce stream) or Accounting + Economics + Mathematics (some variations)
**Z-score context:** AIS (127D) is a relatively new and growing programme at Kelaniya. Z-score cutoffs reflect a competitive but not ultra-high-demand position — it is accessible to high-performing Commerce A/L students who may not reach the cutoff for the main Accountancy or Management degrees.

---

## Special Notes

- English is the medium of instruction.
- The AIS programme is **recognized by the Institute of Chartered Accountants of Sri Lanka (ICASL)** and provides exemptions in some ICASL exam papers — reducing the time and cost to become a Chartered Accountant.
- Graduates with strong IT skills can pursue **CISA (Certified Information Systems Auditor)** certification, which is highly valued for IT audit and governance roles globally.
- The demand for professionals who can bridge accounting and IT is growing faster than the supply in Sri Lanka — making this a well-positioned degree for the next decade.
- Students interested in **working overseas** (Australia, UK, Middle East) find AIS useful because most countries have a shortage of professionally qualified accountants with strong IT backgrounds.
', 'a41f8cc2c03101b2096c351236cf8f4f34987a4da2e13cda1df75a9d68655728');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('128', '# Arts — Information Technology
**Course Number:** 128
**Degree:** Bachelor of Arts (Honours) in Arts and Information Technology
**Duration:** 4 years
**Entry Stream:** Arts, Commerce (with some IT background or aptitude)
**Available at:** University of Sri Jayewardenepura (128C)

---

## Overview

Arts — Information Technology (Arts IT) at the University of Sri Jayewardenepura is a distinctive interdisciplinary programme offered through the Faculty of Humanities and Social Sciences. It bridges the humanities — language, communication, social studies, cultural studies — with information technology skills, preparing graduates to work in digital media, e-governance, content management, IT-enabled social services, and communication technology fields.

This programme addresses a genuine gap: Sri Lanka has many IT graduates and many Arts graduates, but very few professionals who can navigate both domains fluently. Government agencies, NGOs, and social enterprises increasingly need people who understand both the social and cultural dimensions of technology deployment AND have practical IT skills. Roles in digital content management, e-government project management, community technology education, and digital communications require this hybrid profile.

The University of Sri Jayewardenepura, one of Sri Lanka''s largest national universities with a comprehensive range of faculties including Humanities, Management, Science, Engineering, Medical, and Dental, is well-positioned to offer this interdisciplinary programme.

---

## What You Will Study

**Year 1 — Foundations:**
Computer Fundamentals and Digital Literacy, Sinhala or Tamil Language and Communication, English Language Skills, Introduction to Information Technology, Social Science Research Methods, Principles of Communication, Web Design Fundamentals (HTML/CSS), Cultural Studies.

**Year 2 — Core Programme:**
Database Concepts, Programming Fundamentals (Python or JavaScript), Human-Computer Interaction, Digital Media Production, Sinhala/Tamil Computing and Language Technology, E-governance and Digital Public Services, Content Management Systems (WordPress, Drupal), Social Media Management, Digital Information Management.

**Year 3 — Applied IT for Humanities:**
GIS for Social Sciences, Digital Heritage and Archiving, ICT4D (Information and Communication Technologies for Development), Multimedia and Digital Arts, Community Informatics, Data Analysis for Social Scientists, E-learning Design and Technology, Journalism and Online Media.

**Year 4 — Research and Project:**
Individual research project integrating arts/humanities with IT applications. Electives from: Mobile Application Development for Social Services, Digital Library Management, Language Technology (NLP for Sinhala/Tamil), AI Ethics and Society, Localization and Translation Technology.

---

## Career Paths in Sri Lanka

- **Government digital services:** E-government project officers, digital content managers at ministries and government agencies implementing digital citizen services.
- **Digital media and content creation:** Social media manager, digital content producer, copywriter, and content strategist for media companies, NGOs, and corporate communications departments.
- **Education technology:** e-learning content developer, learning management system (LMS) administrator at universities, schools, and corporate training departments.
- **NGO and development sector:** ICT4D project manager, community technology trainer, digital literacy programme coordinator at development organizations.
- **Library and information science:** Digital archivist, library information system manager at national libraries, university libraries, and cultural institutions (Archaeological Department, National Museum).
- **Corporate communications:** Internal communications manager, digital marketing assistant, corporate social media specialist.
- **Language technology:** Sinhala/Tamil computing, localization (translating software and apps into Sinhala/Tamil), language corpus development for NLP research.
- **Postgraduate study:** MA in Digital Humanities, Information Science, Communication Studies, or Development Studies.

---

## Entry Requirements

**A/L Stream:** Arts (primary), Commerce
**Typical subjects:** Any combination of Arts/Commerce A/L subjects. Applicants do not require prior IT knowledge — the programme teaches IT from the ground up.
**Z-score context:** Arts IT (128C) at USJ is accessible to Arts and Commerce A/L students who performed reasonably well. It is a relatively new programme and the intake is limited. Students from the Colombo and Western Province face higher competition due to district quota.

---

## Special Notes

- This degree is designed for **Arts and Commerce A/L students who want to add IT skills** to their profile — not for Physical Science students seeking a full IT degree (those should consider Computer Science 012 or IT degrees 026).
- The medium of instruction is mixed — some courses in Sinhala and some in English.
- Graduates fill a genuine niche: many public institutions and NGOs struggle to find people who can simultaneously handle social/cultural communication AND manage digital systems.
- **Sinhala and Tamil language computing** is a growing specialization — software localization, Sinhala NLP, and Unicode compliance for government systems are active areas needing qualified professionals.
- The degree is not a traditional engineering IT degree and graduates should not expect to compete for software engineer roles requiring deep technical programming skills — it''s positioned for the intersection of social and technological practice.
', '99a2f627e92d2f1b9147e38fcab49e04ee22ee96f458217f011432c864ef3c33');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('129', '# Aquatic Bioresources
**Course Number:** 129
**Degree:** Bachelor of Science (Honours) in Aquatic Bioresources
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Sri Jayewardenepura (129C)

---

## Overview

Aquatic Bioresources at the University of Sri Jayewardenepura is a specialized degree programme offered through the Faculty of Urban and Aquatic Bioresources (FUAB) — one of USJ''s newest faculties, established to address Sri Lanka''s growing need for experts in sustainable management of biological resources from water environments. The programme covers fisheries science, aquaculture, marine biology, inland water ecology, and the technology needed to sustainably manage Sri Lanka''s extensive marine and freshwater resources.

Sri Lanka is an island nation with a 1,340 km coastline, extensive inland waterways, reservoirs, and rich reef ecosystems. Fisheries contribute significantly to national food security and export revenue (dried fish, ornamental fish). However, Sri Lanka''s fisheries sector faces serious challenges: overfishing, habitat destruction, climate-related changes in fish stocks, and the need to develop sustainable aquaculture to supplement capture fisheries. Graduates in Aquatic Bioresources are trained to research, manage, and innovate in this sector.

USJ''s Faculty of Urban and Aquatic Bioresources is uniquely positioned in Nugegoda (Colombo district), providing access to both urban research infrastructure and field stations on the coast and in major reservoirs.

---

## What You Will Study

**Year 1 — Biological Foundations:**
Marine and Freshwater Biology, General Ecology, Aquatic Chemistry, Cell Biology and Genetics, Mathematics and Statistics for Biologists, Fish Biology and Taxonomy, Introduction to Fisheries Science.

**Year 2 — Fisheries and Aquaculture:**
Fisheries Biology and Stock Assessment, Aquaculture Systems and Technology (pond culture, cage culture, recirculating systems), Fish Nutrition and Feed Formulation, Marine Biotechnology Fundamentals, Coastal Ecology and Mangrove Systems, Oceanography, Environmental Impact Assessment, Post-Harvest Fish Technology.

**Year 3 — Management and Research:**
Fisheries Resource Management, Fisheries Economics and Policy, Marine Protected Area Management, Inland Fisheries and Reservoir Management, Ornamental Fish Production, Aquatic Pollution and Remediation, GIS for Aquatic Resource Mapping, Research Methods and Biostatistics, Field Training at coastal and inland sites.

**Year 4 — Research:**
Individual research project in aquaculture production, fisheries ecology, marine pollution, or aquatic biodiversity. Seminar series and thesis. Electives from: Marine Genomics, Blue Economy and Ocean Governance, Shrimp and Prawn Culture, Coral Reef Management, Food Safety in Fisheries.

---

## Career Paths in Sri Lanka

- **Department of Fisheries and Aquatic Resources:** The primary government employer — fisheries inspectors, aquaculture development officers, research scientists monitoring fish stocks and licensing aquaculture operations.
- **National Aquaculture Development Authority (NAQDA):** Developing and regulating the national aquaculture industry — prawn, fish, seaweed, and ornamental fish sectors.
- **Ornamental fish industry:** Sri Lanka is one of the world''s largest exporters of ornamental (tropical fish), a USD 30+ million export industry. Graduates can work in production, export quality management, and disease management.
- **Deep-sea fishing industry:** Compliance, stock assessment, and sustainable catch certification for Sri Lanka''s fleet operating under IOTC (Indian Ocean Tuna Commission) agreements.
- **Environmental consulting:** Marine environmental impact assessments for coastal construction, port development, and offshore projects.
- **Research institutions:** National Aquatic Resources Research and Development Agency (NARA) — the premier fisheries research institution in Sri Lanka.
- **NGOs and international organizations:** FAO, UNDP, IUCN marine conservation projects in Sri Lanka.
- **Postgraduate study:** MSc in Aquaculture, Marine Biology, Fisheries Science, or Environmental Management at Ruhuna, Peradeniya, or overseas (University of Stirling, UK — a world leader in aquaculture education).

---

## Entry Requirements

**A/L Stream:** Biological Science
**Typical subjects:** Biology + Chemistry + Physics (or Agriculture/Mathematics as third subject)
**Z-score context:** Aquatic Bioresources (129C) is a relatively new and less well-known programme. Z-score cutoffs are typically lower than Medicine, Veterinary Science, or Agriculture, making it accessible to students who perform well in Biological Science but fall short of the top health sciences cutoffs. It is an excellent choice for students genuinely interested in marine and freshwater environments.

---

## Special Notes

- **Only at USJ** — this programme was specifically created for the new Faculty of Urban and Aquatic Bioresources, one of USJ''s newer faculties.
- Sri Lanka''s **Blue Economy** potential — sustainable fisheries, aquaculture, and marine biotechnology — is increasingly recognized by the government and international development organizations. Graduates in this field will be well-positioned for the next decade.
- Sri Lanka''s **ornamental fish export industry** is a unique sector that offers strong employment for aquaculture-trained graduates in fish breeding, disease management, and export logistics.
- The programme offers excellent **fieldwork opportunities** — coastal surveys, reef monitoring, reservoir assessments, and aquaculture farm visits.
- NARA (National Aquatic Resources Research and Development Agency) and NAQDA are the most important government institutions for career entry, and both regularly recruit from Aquatic Bioresources graduates.
', 'bb7d729dc318479ec9e0995f133d478418561213b1b7f4ba2d8f9376c1c1173f');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('130', '# Urban Bio Resources
**Course Number:** 130
**Degree:** Bachelor of Science (Honours) in Urban Bio Resources
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Sri Jayewardenepura (130C)

---

## Overview

Urban Bio Resources is a pioneering and distinctive degree offered through the Faculty of Urban and Aquatic Bioresources (FUAB) at the University of Sri Jayewardenepura — the only programme of its kind in Sri Lanka. It focuses on the biological resources found within and around urban environments: urban forestry, landscape ecology, urban agriculture, green infrastructure, urban biodiversity, and the sustainable management of biological systems in city settings.

As Sri Lanka rapidly urbanizes — particularly in the Colombo Metropolitan Region — there is a critical and growing need for professionals who can plan and manage green spaces, urban forests, rooftop gardens, urban food production systems, biodiversity corridors, and nature-based solutions to urban challenges (flood management, urban heat island mitigation, air quality). Urban Bio Resources graduates are uniquely positioned to serve in city planning authorities, landscaping companies, urban agriculture ventures, and environmental agencies.

USJ''s location in Nugegoda, at the heart of the Colombo metropolitan region, makes it ideal for a programme that studies urban biological systems — students have direct access to Sri Lanka''s most rapidly urbanizing landscape as a living case study.

---

## What You Will Study

**Year 1 — Biological and Environmental Foundations:**
Plant Biology and Taxonomy, Ecology and Environmental Science, Soil Science and Land Resources, Cell Biology and Genetics, Mathematics and Statistics for Biologists, Urban Ecology Introduction, Environmental Policy and Law.

**Year 2 — Urban Systems:**
Landscape Design and Planning, Urban Forestry and Arboriculture, Urban Agriculture Systems (vertical farming, hydroponics, community gardens), GIS and Remote Sensing for Urban Environments, Environmental Impact Assessment, Urban Biodiversity Conservation, Botanic Gardens and Green Space Management, Entomology for Urban Environments.

**Year 3 — Applied Urban Bioresources:**
Urban Food Systems and Security, Nature-Based Solutions for Urban Climate Resilience, Green Infrastructure Design, Ornamental Horticulture and Landscape Management, Urban Wetland and Green Corridor Management, Waste Management and Composting, Community-Based Natural Resource Management, Research Methods and Field Studies.

**Year 4 — Research and Specialization:**
Individual research project in urban ecology, urban agriculture, landscape, or green infrastructure. Electives from: Smart Urban Farming Technology, Phytoremediation, Urban Heat Island Mitigation, Pollinator Conservation in Cities, Biosystems Engineering for Urban Agriculture.

---

## Career Paths in Sri Lanka

- **Urban planning and green space management:** Urban Development Authority (UDA), Colombo Municipal Council Parks Division, National Physical Planning Department — planners and managers of urban parks, trees, and green corridors.
- **Landscape architecture and design:** Landscape firms and consultancies designing gardens, corporate campuses, hotels, and public spaces. Sri Lanka''s luxury tourism sector demands high-quality landscape design.
- **Urban agriculture:** Rooftop farming ventures, urban farm consulting, and food security projects in urban communities. Growing sector as food prices rise and interest in local food production increases.
- **Environmental consulting:** Environmental impact assessment teams for urban construction projects — assessing impacts on urban trees, ecosystems, and biodiversity.
- **Botanical gardens and public institutions:** National Zoological Gardens, Peradeniya Royal Botanical Gardens (Colombo region offices), National Museum.
- **NGO and sustainability sector:** Urban sustainability officers, green city consultants, climate adaptation project officers for Colombo City Project and international development programmes.
- **Hotel and resort industry:** Horticulturists and landscape managers for luxury hotels, Ayurvedic resorts, and eco-lodges — a significant employer in Sri Lanka''s tourism-dependent economy.
- **Postgraduate study:** MSc in Landscape Architecture, Urban Planning, Environmental Management, or Urban Agriculture at Peradeniya, Colombo, or overseas (Wageningen University, University of Melbourne).

---

## Entry Requirements

**A/L Stream:** Biological Science
**Typical subjects:** Biology + Chemistry + Agriculture or Physics
**Z-score context:** Urban Bio Resources (130C) is among the newer and less commonly known programmes. Z-score cutoffs are moderate — accessible to students with solid Biological Science results who are interested in environmental and urban systems but may not reach Medicine, Dentistry, or Veterinary Science cutoffs.

---

## Special Notes

- **Only at USJ** — this is the only Urban Bio Resources degree in Sri Lanka, making the programme unique.
- Sri Lanka''s **Port City Colombo development** and rapid urbanization create immediate demand for professionals who understand urban biological systems, green infrastructure, and nature-based solutions.
- Urban Bio Resources graduates are natural partners for **architects and city planners** — green building certification (LEED, Green Mark) increasingly requires landscape and biodiversity assessments.
- The programme is distinct from traditional Environmental Science (which tends to focus on natural environments). Urban Bio Resources is specifically about the biological dimension of human-made city environments.
- Students interested in **urban farming startups** or agri-tech ventures find this degree excellent preparation — rooftop farms, hydroponic vegetable production, and mushroom cultivation are growing micro-enterprises.
', 'b161392751c5fde4456728f329bd7f44e90e1e7648fdec594dd9bfb3834c89c1');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('131', '# Financial Economics
**Course Number:** 131
**Degree:** Bachelor of Science (Honours) in Financial Economics
**Duration:** 4 years
**Entry Stream:** Commerce, Arts (with Mathematics), Physical Science
**Available at:** University of Sri Jayewardenepura (131C)

---

## Overview

Financial Economics at the University of Sri Jayewardenepura is a rigorous quantitative degree offered by the Faculty of Management Studies and Commerce, combining advanced economic theory with financial mathematics, econometrics, and financial markets analysis. It is positioned at the intersection of economics and finance — more quantitative than a standard Economics degree and more theoretically grounded than a Finance or Commerce degree.

The programme prepares graduates for careers in investment banking, portfolio management, financial analysis, central banking, economic consultancy, and academic research. As Sri Lanka''s capital markets (Colombo Stock Exchange), banking sector, and insurance industry mature, there is growing demand for professionals with strong quantitative and economic analytical skills — exactly the profile Financial Economics produces.

USJ''s Faculty of Management Studies and Commerce is one of the largest and most research-active management faculties in Sri Lanka, with strong alumni networks in Sri Lanka''s banking and finance industry, and the programme benefits from faculty expertise in applied economics and financial modeling.

---

## What You Will Study

**Year 1 — Economic and Mathematical Foundations:**
Microeconomics, Macroeconomics, Mathematics for Economics and Finance (calculus, linear algebra), Statistics for Economists, Principles of Financial Accounting, Business Communication, Computer Applications for Economics.

**Year 2 — Intermediate Theory:**
Intermediate Microeconomics (consumer theory, production theory, market structures), Intermediate Macroeconomics (national income, IS-LM models, aggregate demand), Financial Mathematics (time value, bonds, derivatives pricing basics), Econometrics I (regression, hypothesis testing), Monetary Economics, Public Finance, Financial Markets and Institutions.

**Year 3 — Advanced Finance and Quantitative Methods:**
Financial Econometrics, Time Series Analysis, Investment Theory and Portfolio Management, Derivatives and Risk Management (options, futures, swaps), Corporate Finance, International Economics and Exchange Rates, Financial Risk Management, Development Economics, Research Methods and Dissertation Proposal.

**Year 4 — Research and Specialization:**
Individual research dissertation in financial economics, econometrics, or macroeconomics. Electives from: Behavioral Finance, Islamic Finance, Actuarial Science Fundamentals, Data Analysis for Finance (R, Python), Capital Market Analysis, Labour Economics.

---

## Career Paths in Sri Lanka

- **Commercial banking and treasury:** Treasury analyst, risk analyst, credit analyst roles at major commercial banks (People''s Bank, BOC, HNB, Commercial Bank, Sampath, Nations Trust). The analytical skills from Financial Economics are directly applicable to credit modeling and risk quantification.
- **Capital markets:** Stockbroker analyst, equity researcher, portfolio manager at investment firms listed on the Colombo Stock Exchange — Acuity Partners, CT CLSA, JB Securities.
- **Insurance and actuarial science:** Financial analyst and junior actuarial work at Ceylinco Insurance, Union Assurance, AIA, and Allianz Lanka. Some Financial Economics graduates pursue professional actuarial exams (Institute and Faculty of Actuaries, UK).
- **Central Bank of Sri Lanka:** Economist and analyst roles in monetary policy, financial stability, and research departments — the CBSL recruits quantitatively strong graduates.
- **Economic consultancy:** International consulting firms and think tanks (Institute of Policy Studies, Verité Research, KPMG Advisory) need economists for project-based economic analysis.
- **Development finance:** ADB, World Bank, UNDP — international development organizations with Sri Lanka programmes recruit economics graduates for project economics and monitoring roles.
- **Postgraduate study:** MSc in Financial Economics, Econometrics, or Economics at Colombo, Moratuwa, or overseas (London School of Economics, Warwick, ANU, Melbourne).

---

## Entry Requirements

**A/L Stream:** Commerce (primary — Accounting + Business Studies + Economics), Arts with Mathematics, Physical Science
**Typical subjects:** Economics + Accounting + Business Studies (Commerce), or Mathematics + Economics combinations
**Z-score context:** Financial Economics (131C) at USJ is a competitive programme attracting the stronger Commerce A/L students. Z-score cutoffs are moderate to high within the Commerce stream. Students who find the degree very quantitative (strong maths requirement) self-select — those uncomfortable with calculus and statistics may find the workload challenging.

---

## Special Notes

- Financial Economics is **more quantitative** than standard Economics or Commerce degrees — students must be comfortable with mathematics including calculus, linear algebra, and statistical modeling.
- English is the medium of instruction.
- Students planning to pursue **CFA (Chartered Financial Analyst)** certification will find Financial Economics provides strong theoretical preparation, especially in portfolio management, derivatives, and econometrics.
- The **Colombo Stock Exchange (CSE)** is a unique career training ground for Finance graduates — the CSE runs internship and trainee analyst programmes.
- Students interested in postgraduate studies should note that Financial Economics from USJ is recognized by UK, Australian, and US universities for admission to MSc and PhD programmes in Economics and Finance.
', '2fdb831b028a83ac2be2cc2a7a46edfd25678a8209c3d9d3a7ed63290874ba24');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('132', '# English Language and Applied Linguistics
**Course Number:** 132
**Degree:** Bachelor of Arts (Honours) in English Language and Applied Linguistics
**Duration:** 4 years
**Entry Stream:** Arts
**Available at:** Uva Wellassa University of Sri Lanka (132U)

---

## Overview

English Language and Applied Linguistics at Uva Wellassa University of Sri Lanka is offered through the Faculty of Social Sciences and Languages at the Badulla-based campus. The programme applies the scientific study of language — linguistics, phonetics, discourse analysis, language acquisition — to practical contexts such as English language teaching, translation, communication, and language policy, rather than studying literature in the traditional sense.

English remains the most important career-enabling language in Sri Lanka. Proficiency in English determines access to the best employment, overseas education, and professional advancement across virtually every sector. Applied Linguistics graduates are trained to understand HOW English works, HOW people learn it, and HOW it can be effectively taught — making them highly valuable as English language teachers, ESL trainers, curriculum developers, and communication specialists.

Uva Wellassa University is a relatively young state university (established 2005) located in Badulla, designed specifically to serve the Uva Province and develop its human capital. The Faculty of Social Sciences and Languages provides programmes suited to the region''s development needs, including English language capacity building.

---

## What You Will Study

**Year 1 — Language Foundations:**
Introduction to Linguistics (phonology, morphology, syntax, semantics), Academic Reading and Writing, Language and Society, Grammar and Usage, Phonetics and Pronunciation, Introduction to Communication Studies, Research Skills.

**Year 2 — Core Applied Linguistics:**
Psycholinguistics (how the mind acquires and processes language), Sociolinguistics (language variation, dialects, language and identity), Second Language Acquisition Theory, Discourse Analysis, English for Specific Purposes (ESP), Language Testing and Assessment, Teaching Methodology I (TESOL fundamentals), Curriculum Design.

**Year 3 — Specialization:**
Teaching Methodology II (advanced pedagogical approaches — Communicative Language Teaching, Task-Based Learning, Content and Language Integrated Learning), Translation Theory and Practice, Language Policy and Planning, English in Sri Lankan Context, Digital Tools for Language Teaching, Materials Development for ELT, Corpus Linguistics, Research Methods in Applied Linguistics.

**Year 4 — Research:**
Research dissertation in applied linguistics, TESOL, or a language study topic relevant to the Sri Lankan context. Electives from: Forensic Linguistics, Language and Technology (NLP basics), Business Communication, Intercultural Communication, English for Academic Purposes (EAP).

---

## Career Paths in Sri Lanka

- **English language teaching:** This is the primary career path. Teaching in government and private schools (English as a subject), international schools, private English-medium institutions. PGDE (Postgraduate Diploma in Education) combined with this degree qualifies for government teacher service.
- **ESL and language training institutions:** National languages trainer at SLIM, NIBM, and corporate training companies. English language teacher at British Council, Alliance Française, and private language institutes.
- **Translation and interpretation:** Sinhala-English or Tamil-English translation for government, courts, UN agencies, and media. The Sri Lanka Courts Translation service and the Department of Official Languages recruit translation professionals.
- **Corporate communication and content writing:** Communication officer, technical writer, content writer for corporate communications departments, advertising agencies, and digital media companies.
- **Language curriculum development:** National Institute of Education (NIE) — curriculum designers, materials writers for government school English programmes.
- **Media and journalism:** News copy editing, English-language journalism at Daily Mirror, Daily FT, The Sunday Times — journalism roles where language precision is essential.
- **Postgraduate study:** MA in Applied Linguistics, TESOL, Linguistics, or Language Education at Kelaniya, Peradeniya, Colombo, or overseas (University of Birmingham, Warwick, Leeds — all have excellent Applied Linguistics MA programmes).

---

## Entry Requirements

**A/L Stream:** Arts (primary)
**Typical subjects:** English Literature or any combination of Arts stream subjects. Strong A/L English performance is expected and advantageous.
**Z-score context:** English Language and Applied Linguistics (132U) at Uva Wellassa is generally accessible to Arts students with reasonable A/L results. The UWU location (Badulla) means students from the Uva Province receive quota advantages. Competition may be lower than equivalent programmes at older universities.

---

## Special Notes

- **Medium of instruction is English** — this programme is conducted in English, which both requires and develops strong English proficiency. Students who are not already reasonably proficient in English may struggle.
- This degree is **different from an English Literature degree** — it focuses on linguistic analysis and language use rather than British or world literature. Students who love grammar, language learning theory, and how language works will thrive; those expecting a literary studies experience may find it different from expectations.
- Graduates of this programme are in excellent position to pursue a **CELTA (Certificate in English Language Teaching to Adults)** — an internationally recognized qualification that opens teaching opportunities in 100+ countries.
- The growing demand for **English medium education in Sri Lanka** (international schools, corporate training, online education) creates a steady labour market for English language and applied linguistics graduates.
- Students interested in **natural language processing (NLP)** for Sinhala and Tamil — an active research area in Sri Lanka''s tech sector — will find linguistic training from this programme directly applicable.
', '6755ce9107428eb032a7f807df4deb915d27fe2f366958a08d90039baf25d4d8');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('133', '# Banking and Insurance
**Course Number:** 133
**Degree:** Bachelor of Business Management (Honours) in Banking and Insurance
**Duration:** 4 years
**Entry Stream:** Commerce, Arts (with Economics or Mathematics)
**Available at:** University of Vavuniya, Sri Lanka (133R)

---

## Overview

Banking and Insurance at the University of Vavuniya is a specialized business management degree offered through the Faculty of Business Studies, one of the university''s core faculties. The programme is unique in Sri Lanka''s state university system for its combination of banking operations, financial services, and insurance industry knowledge — a directly vocational degree aimed at producing job-ready graduates for the financial services sector.

Sri Lanka has one of South Asia''s most developed banking systems, with 25+ licensed commercial banks, multiple development finance institutions, a large cooperative banking sector, and a growing insurance industry regulated by the Insurance Regulatory Commission of Sri Lanka (IRCSL). The Northern and Eastern provinces, where the University of Vavuniya serves, are in active post-war economic reconstruction — creating specific demand for banking and financial services professionals who understand the regional economic context.

The University of Vavuniya is a relatively small national university focused on serving the Northern Province. Its Faculty of Business Studies offers focused business management programmes with a pragmatic orientation towards regional and national employment.

---

## What You Will Study

**Year 1 — Business and Finance Foundations:**
Financial Accounting, Principles of Management, Micro and Macroeconomics, Business Mathematics and Statistics, Communication Skills, Computer Applications for Business, Introduction to Banking Operations, Legal Environment of Business.

**Year 2 — Banking Core:**
Banking Law and Practice, Commercial Bank Management, Credit and Loan Administration, Treasury and Foreign Exchange Operations, Central Banking and Monetary Policy, Financial Statement Analysis, Insurance Principles and Practice, Financial Planning, Risk Management Fundamentals.

**Year 3 — Advanced Finance and Insurance:**
Investment Management and Portfolio Theory, Life Insurance Products and Actuarial Basics, General Insurance (property, vehicle, health, marine), Trade Finance and International Payments, Islamic Banking and Finance, Microfinance and Rural Credit, Cooperative Finance, Consumer Banking and Retail Services, Research Methods.

**Year 4 — Research and Industry:**
Individual research project in banking or insurance topics, Fintech and Digital Banking, Regulatory Compliance and Internal Audit, Insurance Claim Management and Fraud Prevention, Bank Management Simulation (case studies), Career Preparation and Professional Practice.

---

## Career Paths in Sri Lanka

- **Commercial banking:** Branch banking, loan officer, credit analyst, teller operations at major banks (People''s Bank, BOC, HNB, NDB, Sampath, Commercial Bank, NSB, Regional Development Bank). The BBM in Banking and Insurance is specifically targeted at banking sector recruitment.
- **Insurance industry:** Sales and marketing of life and general insurance products, claims handling, underwriting, customer service at companies like Ceylinco Insurance, AIA Lanka, Union Assurance, Sri Lanka Insurance (SLIC), National Insurance Trust Fund.
- **Microfinance and rural credit:** Loan officers at Sanasa Development Bank, Women''s Bank, cooperative credit societies — significant employers in the Northern and Eastern provinces.
- **Cooperative and Development Finance:** Cooperative Rural Banks, Regional Development Bank, and Samurdhi Authority credit programmes.
- **Regulatory bodies:** Insurance Regulatory Commission of Sri Lanka (IRCSL), Central Bank of Sri Lanka (CBSL) supervision departments — career entry paths requiring professional examination success.
- **Financial advisory:** Personal financial planning, insurance agency management, investment advisory for individuals and small businesses.
- **Postgraduate study:** MBA, MSc in Finance, or MSc in Banking at Colombo, Kelaniya, or overseas institutions. Also, professional qualifications: IBF (Institute of Bankers of Sri Lanka) examinations, CII (Chartered Insurance Institute, UK) for insurance specialization.

---

## Entry Requirements

**A/L Stream:** Commerce (primary), Arts (with Economics)
**Typical subjects:** Accounting + Business Studies + Economics (Commerce stream)
**Z-score context:** Banking and Insurance (133R) at the University of Vavuniya has moderate Z-score cutoffs, reflecting the programme''s regional catchment area and the smaller applicant pool relative to Colombo-area universities. Students from the Northern Province receive quota advantages. It is accessible to Commerce stream students with good A/L results.

---

## Special Notes

- The **University of Vavuniya** is one of Sri Lanka''s northernmost national universities, located in the Northern Province. Most students are residential. It has a particular mandate to serve the post-conflict reconstruction needs of the Northern Province.
- Students who complete this degree can pursue the **Chartered Institute of Bankers Sri Lanka (IBF)** professional examinations alongside or after the degree to enhance employability.
- Islamic finance (interest-free banking) is a growing sector in Sri Lanka — Amana Bank is the only fully-fledged Islamic bank, but other commercial banks offer Islamic windows. Students with interest in Islamic finance should note the Islamic Banking module.
- The Northern Province has a **significant remittance economy** (money sent by diaspora) — banking professionals in the region often work extensively with foreign remittance services (Western Union, international bank transfers).
- Students can also pursue CIMA, ACCA, or IBF professional qualifications alongside this degree to supplement their credentials.
', '0d00699598b9ad096a5df33b9f8c9864a8cc46eb5405a4d624d1219d702ed18a');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('134', '# Creative Music Technology and Production
**Course Number:** 134
**Degree:** Bachelor of Arts (Honours) in Creative Music Technology and Production
**Duration:** 4 years
**Entry Stream:** Arts (with demonstrated musical ability or aptitude)
**Available at:** University of Sri Jayewardenepura (134C)

---

## Overview

Creative Music Technology and Production at the University of Sri Jayewardenepura is one of Sri Lanka''s most innovative and distinctive degree programmes — the first state university degree in music technology and audio production. Offered through the Faculty of Humanities and Social Sciences, it combines traditional musical knowledge with modern audio technology: digital audio workstations (DAWs), music production, sound design, live sound engineering, film scoring, and the business of the music industry.

Sri Lanka''s music industry — Sinhala pop, electronic music, film music, advertising jingles, game audio — is increasingly professionalized and technology-driven. At the same time, the demand for skilled audio engineers, music producers, and sound designers in media production (films, TV, streaming platforms, corporate events) far exceeds the supply of formally trained professionals. Graduates of this programme are positioned to lead Sri Lanka''s transition from informal, self-taught music production to formally trained, industry-standard professionals.

USJ has a strong tradition in arts and humanities education, and this programme benefits from the university''s creative arts infrastructure and proximity to Colombo''s active music and media industry.

---

## What You Will Study

**Year 1 — Music and Technology Foundations:**
Music Theory and Notation (Western and Sri Lankan), Acoustic Fundamentals, Introduction to Digital Audio Workstations (DAW — Pro Tools, Logic Pro, Ableton Live), Music History and Context, Ear Training and Aural Skills, Introduction to Music Technology, Basic Electronics for Musicians.

**Year 2 — Production Core:**
Music Production Techniques (arrangement, mixing, sound design), Recording Studio Practice (microphone placement, signal chain, multi-track recording), MIDI Production and Electronic Music, Sound Design for Media (film, TV, games, advertising), Synthesis (analog/digital/FM/wavetable), Mastering Fundamentals, Sri Lankan Music Traditions and Fusion.

**Year 3 — Specialization:**
Film Scoring and Post-Production Audio (synchronization, Foley, ADR, dialogue editing), Live Sound Engineering (PA systems, monitor engineering, front-of-house), Music Business (artist management, publishing, licensing, streaming royalties), Advanced Mixing (genres — pop, hip-hop, electronic), Interactive Audio (game audio, UI sound design), Radio and Podcast Production.

**Year 4 — Portfolio and Research:**
Major creative project (a produced album, film score, or sound design portfolio), Research dissertation on music technology or industry topic, Music Entrepreneurship and Career Development, Industry Internship. Final showcase presentation.

---

## Career Paths in Sri Lanka

- **Music production and recording:** Studio producer, recording engineer, mixing engineer for Sinhala pop artists, film music, advertising music. Sri Lanka''s commercial recording industry (including Sinhala film music scene based around Colombo) consistently needs trained audio professionals.
- **Film and TV post-production:** Sound editor, audio post-production engineer at production companies making Sinhala films, TV dramas, documentary films. Sri Lanka''s film and TV production sector is growing with streaming platforms.
- **Live sound engineering:** Front-of-house (FOH) or monitor engineer for concerts, events, corporate events, festivals. Sri Lanka''s live events industry employs sound engineers for hotel shows, corporate conferences, and national events.
- **Advertising and branding:** Jingle producer, sound designer, audio branding specialist at advertising agencies — music for TV/radio commercials.
- **Game audio:** A growing global industry. Sri Lanka has nascent game development companies and outsourcing studios that need game audio designers.
- **Teaching:** Music technology lecturer at private institutes, school music teacher.
- **Music entrepreneurship:** Artist management, music label, online music teaching, YouTube content creation around music and production.
- **Postgraduate study:** MA in Music Production, Music Technology, or Sound Design at UK (Royal College of Music, Leeds Beckett), Australian, or US institutions.

---

## Entry Requirements

**A/L Stream:** Arts (primary). Students with music performance or production backgrounds are at a strong advantage.
**Typical subjects:** Arts stream subjects. A/L Music or Aesthetic Studies is advantageous but may not be strictly required — the university may conduct auditions or aptitude assessments.
**Z-score context:** Creative Music Technology (134C) is a specialized and niche programme. The intake is likely small. Z-score cutoffs reflect the specialized applicant pool — students from Arts backgrounds with musical ability or technology interest.

---

## Special Notes

- This is a **unique programme in Sri Lanka** — no other state university offers a degree specifically in music technology and production.
- The programme is in English medium, which may be a consideration for students whose schooling was in Sinhala or Tamil medium.
- Students should have **genuine passion for music** — either as performers, composers, or technology enthusiasts — to succeed and enjoy this programme.
- The programme may include **DAW software training** that directly translates to industry tools (Pro Tools certification, Ableton certification).
- Sri Lanka''s music industry has historically lacked formal training pathways — graduates of this programme will be pioneers helping professionalize the sector.
- Students interested in **game development** should note that audio is one of the fastest-growing and least-saturated specializations in the global game industry.
', '58417b85c9604dc24c06d8947ab0e203c03609bc8f7022690a73331d4e9ca09d');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('135', '# Plantation Management and Technology
**Course Number:** 135
**Degree:** Bachelor of Science (Honours) in Plantation Management and Technology
**Duration:** 4 years
**Entry Stream:** Biological Science, Physical Science (Biology preferred)
**Available at:** Uva Wellassa University of Sri Lanka (135U)

---

## Overview

Plantation Management and Technology at Uva Wellassa University of Sri Lanka is offered in the heartland of Sri Lanka''s plantation industry — the Badulla-based university is surrounded by tea, rubber, and minor export crop estates, making it uniquely positioned to deliver practically grounded plantation education. The programme covers tea, rubber, and other plantation crop science, plantation management systems, estate operational management, and the technology behind primary processing.

Sri Lanka''s plantation industry — tea, rubber, coconut, and minor export crops — contributes around 7% of export earnings and employs approximately 500,000 workers, including estate plantation workers (mainly Tamil-speaking estate communities), field officers, factory managers, superintendents, and headquarters management. Despite its age, Sri Lanka''s plantation sector is undergoing significant transformation: mechanization of harvesting, precision tea production, specialty and premium teas, Rainforest Alliance and UTZ certification, and organic cultivation.

Uva Wellassa University was established specifically to serve the Uva Province and the plantation economy. Plantation Management and Technology is one of its flagship programmes, with direct connections to the regional tea and rubber estates for field training.

---

## What You Will Study

**Year 1 — Biological and Agricultural Foundations:**
Botany (crop physiology, plant nutrition), Soil Science and Land Management, General Agronomy, Chemistry for Plantation Science, Climate and Meteorology for Plantations, Introduction to Plantation Industry (Sri Lanka''s plantation history, economic significance), Computer Applications.

**Year 2 — Plantation Crop Science:**
Tea Cultivation and Agronomy (cultivar selection, pruning, soil management, fertilization), Rubber Cultivation (tapping systems, clonal selection, latex physiology), Coconut and Minor Export Crops (cocoa, cardamom, pepper, citronella), Pest and Disease Management for Plantation Crops (integrated pest management), Irrigation and Drainage, Plantation Mechanization.

**Year 3 — Processing and Management:**
Tea Manufacture (orthodox, CTC, green and specialty teas — withering, rolling, fermentation, firing, grading), Rubber Processing (RSS, TSR), Quality Assurance and Standards (ISO, GlobalGAP, Rainforest Alliance certification), Plantation Financial Management, Labour Management and Industrial Relations (estate worker welfare, labour law), Environmental Management for Plantations, Export Logistics and Commodity Marketing, Research Methods.

**Year 4 — Research and Specialization:**
Individual research project in plantation science or management. Field research on a working estate. Electives from: Organic Plantation Agriculture, Specialty Tea Development, Precision Agriculture for Plantations, Climate Change Adaptation in Plantation Agriculture, Smart Plantation Technology (IoT sensors, drone monitoring).

---

## Career Paths in Sri Lanka

- **Estate management:** The classical career pathway. Plantation officer, superintendent, and estate manager roles at Regional Plantation Companies (RPCs) — Hayleys Plantations (Kelani Valley, Talawakelle), Aitken Spence Plantations (Kahawatte, Maskeliya), WATAWALA Plantations, Forbes and Walker, Jetwing Tea. Also at smaller private estates and smallholder operations.
- **Tea manufacturing management:** Factory manager (Orthodox or CTC factory), quality control superintendent, tea taster — responsible for the primary processing of green leaf into made tea.
- **Research institutions:** Tea Research Institute (TRI) of Sri Lanka based in Talawakelle, Rubber Research Institute — research officer, field researcher positions requiring plantation science graduates.
- **Commodity marketing and export:** Tea marketing executive, commodity trader at commodity broking houses (Forbes & Walker Tea Brokers, Asia Siyaka Commodities). The Colombo Tea Auction is the primary global benchmark for Ceylon Tea pricing.
- **Regulatory and quality bodies:** Sri Lanka Tea Board, Natural Rubber Secretariat, Export Agriculture Department — certification, promotion, and quality assurance roles.
- **Sustainability and certification:** Rainforest Alliance, UTZ (now merged with Rainforest Alliance), Fairtrade certification auditors and compliance officers — a growing demand as international buyers require certified sustainable tea.
- **Development organizations:** ILO plantation worker welfare programmes, NGOs working in estate communities.
- **Postgraduate study:** MSc in Agronomy, Plantation Crop Management, Tropical Crop Science at Peradeniya or overseas institutions (Wageningen, University of Reading).

---

## Entry Requirements

**A/L Stream:** Biological Science (primary), Physical Science
**Typical subjects:** Biology + Chemistry + Agriculture or Physics
**Z-score context:** Plantation Management and Technology (135U) has moderate Z-score cutoffs, accessible to Biological Science students who may not reach the cutoffs for Medicine, Veterinary Science, or Agriculture at Peradeniya. The Uva Wellassa location draws primarily from the Central, Sabaragamuwa, and Uva provinces. This is a highly specialized degree — students with genuine interest in the plantation sector will be far more satisfied than those who choose it purely based on Z-score.

---

## Special Notes

- **Uva Wellassa University''s location in Badulla** places students in the literal centre of Sri Lanka''s plantation zone — field visits, industrial training, and research projects are conducted on real working estates.
- Sri Lanka''s **premium and specialty tea sector** is growing significantly as demand for single-origin and specialty teas rises globally — creating new market opportunities and more sophisticated management roles.
- **Estate management careers offer residential accommodation**, meals, and other benefits on the estate — a distinctive lifestyle consideration.
- Graduates who obtain estate experience and pursue professional development through the Institute of Human Resource Advancement (IHRA) or Estate Management courses can advance rapidly to superintendent and CEO level in plantation companies.
- The programme is suitable for students from plantation communities who want to return and contribute to the development of their home regions.
', 'f444a115a0d4c8fba0d6a5b070de7d49e102563806d1b2799f25c5d0050674a6');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('136', '# Data Science (B.Sc.)
**Course Number:** 136
**Degree:** Bachelor of Science (Honours) in Data Science
**Duration:** 4 years
**Entry Stream:** Physical Science, Biological Science (some intakes)
**Available at:** Sabaragamuwa University Faculty of Applied Sciences (136A)

---

## Overview

Data Science is one of the most in-demand skills globally and in Sri Lanka. Data Scientists extract meaningful insights from large datasets to drive business decisions, policy choices, and scientific discoveries. The programme combines statistics, mathematics, computer science, and domain knowledge to produce graduates who can collect, process, analyse, and communicate data.

Sabaragamuwa University''s Data Science programme is among the newest undergraduate offerings in Sri Lanka''s state university system, responding directly to industry demand.

---

## What You Will Study

**Year 1 — Quantitative Foundations:**
Mathematics (Calculus, Linear Algebra, Discrete Mathematics), Statistics and Probability, Introduction to Programming (Python, R), Database Fundamentals, Data Literacy and Visualization.

**Year 2 — Core Data Science:**
Statistical Inference and Modelling, Data Structures and Algorithms, Machine Learning I (regression, classification, clustering), Database Systems (SQL and NoSQL), Data Wrangling and Preprocessing, Business Analytics, Research Methods.

**Year 3 — Advanced Analytics:**
Machine Learning II (ensemble methods, deep learning basics), Big Data Technologies (Hadoop, Spark), Data Visualization Tools (Tableau, Power BI), Time Series Analysis, Natural Language Processing basics, Cloud Computing for Data, Industrial Training.

**Year 4 — Specialization:**
Research Dissertation, Advanced Machine Learning, AI Applications, Data Ethics and Privacy, Data Governance, Domain applications (healthcare analytics, agricultural data, financial analytics).

---

## Career Paths in Sri Lanka

- **Data analyst:** Analysing business data to produce reports and insights for banks, insurance, retail, and telecoms. Entry-level role for most graduates.
- **Data scientist:** Building predictive models and machine learning systems — mid-level role after gaining experience.
- **Business intelligence developer:** Power BI, Tableau, SQL analytics dashboards for enterprise reporting.
- **Machine learning engineer:** Deploying ML models to production systems.
- **Financial data analyst:** Banks, stock broking firms, insurance companies — quantitative analysis roles.
- **Healthcare data analyst:** Hospital management, Ministry of Health — epidemiology and health analytics.
- **Agricultural data analyst:** Department of Agriculture, research institutions — crop yield prediction, precision agriculture.
- **Research:** Academic and policy research using quantitative methods.
- **International:** Data Science skills are globally portable — remote work for international companies is common among Sri Lankan data professionals.

---

## Entry Requirements

**A/L Stream:** Physical Science (primary, due to mathematics requirement), some intakes may accept Biological Science
**Required subjects:** Combined Mathematics (essential), Physics, Chemistry

**Z-score context:** Data Science at Sabaragamuwa (136A) has cutoffs typically in the **0.7 to 1.2** range — more accessible than the established Colombo/Peradeniya Science programmes. A very good choice for Physical Science students with mid-range Z-scores who are interested in technology careers.

---

## Special Notes

- Python and R are the two core programming languages — starting to learn Python before university is a significant advantage.
- Data Science graduates who also hold professional certifications (Google Data Analytics, AWS Machine Learning Specialty, Microsoft Azure Data Scientist) are more competitive in the job market.
- The Sri Lankan banking and telecoms sectors are the biggest immediate employers of Data Science graduates for analytics and reporting roles.
- Remote and hybrid work is common in data roles — many Sri Lankan Data Scientists work for international companies without leaving the country.
', '876253683c2157063c01b4ce63078b1ee78e745442c5308b0a8190cc2d075f53');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('137', '# Primary Education
**Course Number:** 137
**Degree:** Bachelor of Education (Honours) in Primary Education
**Duration:** 4 years
**Entry Stream:** Arts, Commerce, or Biological Science (stream requirements may vary)
**Available at:** University of Colombo (137A)

---

## Overview

Primary Education at the University of Colombo is offered through the Faculty of Education — the premier education faculty in Sri Lanka, historically the most research-active and influential in shaping Sri Lanka''s national school education system. This degree specifically prepares professionals to teach children in Grades 1–5 (ages 5–11), covering pedagogy for early childhood and primary education, curriculum design for primary levels, child development, and the practical skills for transforming young learners.

Sri Lanka has a long history of prioritizing primary education — the country achieved near-universal primary school enrolment decades ago and literacy rates are among the highest in South Asia. However, the quality of primary education — particularly in rural and estate schools, schools where English medium is newly introduced, and schools serving disadvantaged communities — continues to need qualified teachers trained specifically for young learners.

The University of Colombo''s Faculty of Education has produced generations of education leaders, curriculum designers at the National Institute of Education (NIE), school principals, education policy researchers, and classroom teachers who have shaped Sri Lanka''s education landscape.

---

## What You Will Study

**Year 1 — Education Foundations:**
Child Development (physical, cognitive, social, emotional development of 5–11 year olds), Principles of Education, Philosophy of Education, Language Development in Young Children, Mathematics for Primary Teachers, Introduction to Curriculum Theory, Sri Lankan Education System and Policy.

**Year 2 — Pedagogy and Curriculum:**
Teaching Reading and Writing (Sinhala, Tamil, and/or English literacy methods), Mathematics Teaching in Primary Schools (activity-based learning, conceptual understanding), Science Education for Primary (hands-on inquiry approaches), Arts and Aesthetics Education, Social Studies Teaching, ICT Integration in Primary Classrooms, Assessment and Evaluation for Young Learners.

**Year 3 — Specialization and School Placement:**
Special Education and Inclusive Schooling (supporting children with learning difficulties and disabilities), Early Childhood Education (pre-primary and transition to Grade 1), English as a Second Language (ESL) in Primary Schools, School Practicum I (supervised teaching practice in primary schools, at least 6 weeks), Educational Psychology, School Counselling Basics, Research Methods in Education.

**Year 4 — Research and Advanced Practice:**
School Practicum II (extended supervised teaching in a primary school), Educational Research Dissertation, School Leadership and Administration, Curriculum Development and Material Design, Early Literacy and Numeracy Intervention, Multicultural Education (managing linguistic and ethnic diversity in Sri Lankan primary classrooms).

---

## Career Paths in Sri Lanka

- **Primary school teacher:** Teaching in government or government-approved private primary schools across Sri Lanka. Graduates are eligible for Grade I Teacher Service positions in government schools — a stable, pensionable career with island-wide placement.
- **Early childhood specialist:** Pre-school and kindergarten teacher, Montessori educator, early childhood programme coordinator at community preschools and child development centres.
- **Special education teacher:** Trained to work with children with learning differences (dyslexia, ADHD, autism spectrum) in inclusive classrooms and special education units.
- **Curriculum development:** National Institute of Education (NIE) — curriculum officer developing textbooks, activity books, and teaching materials for primary level.
- **School administration:** Deputy principal and principal of primary schools — typically after gaining teaching experience and completing management development programmes.
- **Educational NGOs:** Programme officers at educational NGOs (Save the Children, Plan International, UNICEF Sri Lanka) implementing literacy, numeracy, and school quality improvement programmes.
- **Overseas employment:** Qualified primary teachers from Sri Lanka have significant employment demand in the UAE, Saudi Arabia, Qatar, Maldives, and Singapore at international schools serving South Asian communities.
- **Postgraduate study:** MEd, MPhil in Education, or PhD in Primary/Childhood Education at Colombo, Kelaniya, or overseas (Institute of Education London, Melbourne Graduate School of Education).

---

## Entry Requirements

**A/L Stream:** The Faculty of Education at Colombo accepts students from multiple streams, including Arts, Commerce, and Biological Science. The specific stream requirements may vary by year of intake — the UGC handbook should be checked.
**Z-score context:** Primary Education (137A) at Colombo competes within the Faculty of Education applicant pool. Education degrees are popular among students from all streams who aspire to teaching careers. Colombo being in the Western Province means the cutoffs are influenced by the large Colombo district applicant pool.

---

## Special Notes

- **Teaching as a government career:** Government school teachers in Sri Lanka receive competitive salaries by local standards, free accommodation in some postings, annual increments, pension benefits, and defined working hours. This makes teaching a highly regarded career especially outside urban centres.
- **Medium of instruction** at the Faculty of Education can be a mix of Sinhala and English depending on the specialization (Sinhala-medium primary education vs. English-medium primary education tracks).
- Students who specialize in **English medium primary education** are particularly sought-after as government schools expand the English medium stream.
- The **Education sector in Sri Lanka is employer-guaranteed** in the sense that the government has a consistent need for primary teachers across all provinces — graduates face relatively low unemployment risk compared to other degrees.
- Students interested in **early childhood education** (Montessori, play-based learning, pre-school management) will find this degree provides the theoretical grounding for founding and managing pre-schools.
', '4eea9a55ff9824f5b8db9ffe304ff0601e0986a468d0b5f14f08c83d74d71d7a');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('138', '# Medical Imaging Technology
**Course Number:** 138
**Degree:** Bachelor of Science (Honours) in Medical Imaging Technology
**Duration:** 4 years
**Entry Stream:** Biological Science, Physical Science
**Available at:** University of Colombo (138A)

---

## Overview

Medical Imaging Technology at the University of Colombo is offered through the Faculty of Allied Health Sciences — one of Sri Lanka''s premier institutions for health sciences outside of Medicine and Dentistry. The programme trains graduates to operate, maintain, and optimize the complex imaging equipment used in modern medical diagnosis: X-ray systems, CT scanners, MRI scanners, ultrasound machines, nuclear medicine equipment, and fluoroscopy systems.

Medical imaging is the backbone of modern clinical diagnosis. Without skilled radiographers and imaging technologists, hospitals cannot accurately diagnose fractures, tumors, strokes, cardiac conditions, or internal injuries. Sri Lanka''s expanding healthcare system — particularly the growing number of hospitals equipped with advanced CT and MRI scanners — has created consistent and growing demand for qualified Medical Imaging Technologists. Private hospitals (Nawaloka, Durdans, Lanka, Asiri, Hemas) and government hospitals alike actively recruit imaging graduates.

The University of Colombo''s Faculty of Allied Health Sciences benefits from clinical training links with the Colombo National Hospital (one of the largest in South Asia), the Apeksha Cancer Hospital, and multiple Colombo-based teaching hospitals — giving students direct patient-level clinical exposure throughout the programme.

---

## What You Will Study

**Year 1 — Biological and Physical Foundations:**
Human Anatomy and Physiology, Medical Physics (radiation physics, electromagnetic spectrum), Biochemistry, Patient Care and Communication, Radiation Safety and Protection, Introduction to Medical Imaging Modalities, Mathematics and Statistics for Health Sciences.

**Year 2 — Core Imaging Science:**
Diagnostic Radiography (plain X-ray projections — chest, abdomen, musculoskeletal, skull), Radiographic Image Quality, Fluoroscopy and Contrast Studies, Ultrasound Physics and Clinical Applications, Digital Imaging and PACS (Picture Archiving and Communication Systems), Sectional Anatomy (for CT and MRI interpretation), Pathology for Radiographers (recognizing disease on images).

**Year 3 — Advanced Modalities:**
Computed Tomography (CT) — principles, protocols, clinical applications, Magnetic Resonance Imaging (MRI) — physics, safety, sequences, clinical applications, Nuclear Medicine — gamma cameras, PET/CT, radiotracer principles, Interventional Radiology (image-guided procedures), Mammography, Radiation Oncology Support, Clinical Placement I (hospital rotations across all imaging departments).

**Year 4 — Research and Specialization:**
Clinical Placement II (extended hospital training), Individual research project in imaging technology, quality improvement, or radiation protection. Electives from: Advanced MRI Techniques, Cardiac Imaging, Paediatric Imaging, Teleradiology, Artificial Intelligence in Radiology.

---

## Career Paths in Sri Lanka

- **Government hospitals:** Radiographer and Medical Imaging Technologist in the Ministry of Health''s vast network of national, provincial, and base hospitals. The Radiology Department at Colombo National Hospital is the busiest imaging unit in Sri Lanka.
- **Private hospitals:** Senior radiographer, chief radiographer, lead MRI/CT technologist at private hospital chains (Nawaloka, Durdans Hospitals, Lanka Hospitals, Asiri Group, Hemas Hospitals). Private sector salaries are significantly higher than government.
- **Diagnostic imaging centres:** Stand-alone radiology centres and imaging clinics operated by Radiology Lanka, Hemas Diagnostics, and private radiology partnerships.
- **Medical equipment industry:** Applications specialist, clinical educator, and service support roles at companies supplying medical imaging equipment (Siemens Healthineers, Philips, GE Healthcare, Canon Medical — all present in Sri Lanka through agents).
- **Overseas employment:** Medical imaging technologists from Sri Lanka are in high demand in Australia, UK, UAE, Canada, and New Zealand — all of which face shortages of imaging professionals. Registration requirements (AHPRA in Australia, HCPC in UK) require additional assessment but are achievable.
- **Medical education:** Clinical demonstrator and lecturer at medical and allied health sciences faculties.
- **Research:** Imaging research at University of Colombo Faculty of Medicine, MRI protocol development, radiation dose optimization, and AI-assisted diagnosis research.
- **Postgraduate study:** MSc in Medical Imaging, Radiation Sciences, or Healthcare Technology Management at local or overseas universities.

---

## Entry Requirements

**A/L Stream:** Biological Science (primary), Physical Science
**Typical subjects:** Biology + Chemistry + Physics (Biological Science) or Combined Mathematics + Physics + Chemistry (Physical Science)
**Z-score context:** Medical Imaging Technology (138A) is highly competitive within the Allied Health Sciences category — it consistently attracts students with strong Biological Science or Physical Science results. Z-score cutoffs are significantly above the average for the stream, approached by students who narrowly miss Medicine or Dentistry. The programme has a small annual intake at Colombo.

---

## Special Notes

- **Radiation safety** is central to this profession. Students are trained in radiation protection from Year 1, and graduates are responsible for minimizing radiation exposure to patients and themselves.
- **SLMC or Allied Health Sciences Council registration** is required for government hospital employment. The degree from Colombo qualifies graduates for this registration.
- English is the medium of instruction.
- The shift to **digital radiology (PACS, teleradiology)** and **AI-assisted diagnostic imaging** is transforming the profession. Graduates trained in these technologies have significant career advantages.
- **Overseas employment** is a major attraction of this degree. Australia (AHPRA registration), UK (HCPC), UAE, and Canada consistently recruit Sri Lankan imaging technologists — the profession is on skilled migration occupation lists in multiple countries.
- Graduates interested in pursuing a medical career should note that Medical Imaging Technology (unlike Physiotherapy or Pharmacy) does not directly provide a pathway to medical registration — they would need to apply for Medicine through MBBS admission.
', 'd8e22e6892171f329edb686a9b30d31052122c7412f8cf80aaf5e383b133643d');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('139', '# Polymer Science and Industrial Management
**Course Number:** 139
**Degree:** Bachelor of Science (Honours) in Polymer Science and Industrial Management
**Duration:** 4 years
**Entry Stream:** Physical Science, Biological Science
**Available at:** University of Sri Jayewardenepura (139C)

---

## Overview

Polymer Science and Industrial Management at the University of Sri Jayewardenepura is an interdisciplinary degree offered through the Faculty of Applied Sciences, combining the chemistry and physics of polymers (plastics, rubber, fibres, adhesives, coatings, biomaterials) with industrial engineering, quality management, and production management principles. This unique combination produces graduates who understand both the science of materials AND how to manage their production efficiently.

Sri Lanka has significant polymer-related industries: rubber (natural rubber latex products, tyres components), plastics (packaging, consumer goods), synthetic fibres (apparel industry supporting materials), paints and coatings, and adhesives. Natural rubber in particular is a major Sri Lankan export crop and industrial input — and graduates trained in rubber polymer science are sought by rubber manufacturers, research institutions, and the export market.

USJ''s Faculty of Applied Sciences is home to several specialized science programmes, and the Department of Chemistry provides the scientific foundation for this degree, supported by Industrial Management faculty for the production and operations component.

---

## What You Will Study

**Year 1 — Scientific Foundations:**
Polymer Chemistry (monomer chemistry, polymerization reactions, polymer classification), Organic and Physical Chemistry, Mathematics and Statistics, Industrial Management Fundamentals, Computer Applications, Laboratory Techniques, Physics of Materials.

**Year 2 — Polymer Science:**
Polymer Structure and Properties (mechanical, thermal, electrical, optical), Natural Rubber Chemistry and Processing, Synthetic Polymer Manufacturing (polyethylene, polypropylene, PVC, PET), Polymer Characterization Techniques (IR spectroscopy, DSC, GPC, SEM), Plastics Technology, Rubber Compounding and Vulcanization, Textile Polymers and Fibres, Operations Management.

**Year 3 — Industrial Applications:**
Polymer Processing (extrusion, injection moulding, blow moulding, calendering), Quality Control and Quality Assurance in Polymer Industry, ISO Standards and Compliance, Adhesives and Coatings Technology, Recycling and Environmental Management of Polymers, Biopolymers and Sustainable Materials, Industrial Safety and Health, Supply Chain Management, Research Methods.

**Year 4 — Research and Management:**
Individual research project in polymer science or industrial management. Electives from: Biomedical Polymers (implants, drug delivery), Nanocomposites and Advanced Materials, Green Chemistry and Biodegradable Polymers, Polymer Rheology, Production Planning and ERP Systems for Manufacturing.

---

## Career Paths in Sri Lanka

- **Rubber industry:** Research scientist, production technologist, quality control manager at Richard Pieris Rubber (LANXESS Lanka), Kelani Tyres, Loadstar (industrial rubber products), or the Rubber Research Institute of Sri Lanka.
- **Plastics and packaging industry:** Production engineer, QC manager at plastics manufacturing companies — Unichela, Printcare, Lanka Packaging, and multinational FMCG companies'' packaging suppliers.
- **Paint and coatings industry:** Formulation chemist, QA/QC specialist at Dulux (AkzoNobel Lanka), Nippon Paints Lanka, or local paint manufacturers.
- **Synthetic fibre and textile material suppliers:** Material scientist for companies supplying synthetic fibres to Sri Lanka''s garment industry.
- **Adhesives and sealants:** Product development and technical service roles at adhesive companies (Phenix, local hardware chemical manufacturers).
- **Sustainability and recycling:** With global plastic waste management gaining urgency, expertise in polymer science + recycling processes is increasingly valued by government waste agencies and private recyclers.
- **Research institutions:** Rubber Research Institute (RRI), Industrial Technology Institute (ITI) — research officer and materials scientist roles.
- **Overseas:** Polymer scientists and materials engineers are in demand in Malaysia, Singapore, Germany, and the UK — especially for rubber and advanced materials sectors.
- **Postgraduate study:** MSc in Polymer Science, Materials Science, or Chemical Engineering at Peradeniya, Colombo, or overseas (University of Nottingham, Loughborough, Massachusetts Institute of Technology).

---

## Entry Requirements

**A/L Stream:** Physical Science (primary), Biological Science (Chemistry must be a core subject)
**Typical subjects:** Combined Mathematics + Physics + Chemistry (Physical Science) or Biology + Chemistry + Physics (Biological Science)
**Z-score context:** Polymer Science and Industrial Management (139C) is a specialized and relatively niche programme. Z-score cutoffs are moderate — accessible to Physical or Biological Science students who performed well in Chemistry but may not meet cutoffs for the most competitive programmes. The dual science-management curriculum attracts students interested in both technical and management careers.

---

## Special Notes

- Sri Lanka is one of the world''s largest producers of **natural rubber** — there is genuine career demand for polymer scientists who understand natural rubber chemistry, vulcanization, and latex product manufacturing.
- English is the medium of instruction.
- The **green polymer** and **biopolymer** specialization is a growing field globally as the world moves to replace conventional petroleum-based plastics with biodegradable alternatives — graduates with this knowledge will be well-positioned for the next decade.
- This degree is less well-known than mainstream chemistry or materials science degrees, but the **polymer industry in Sri Lanka is substantial** — many companies struggle to find formally trained polymer scientists and often promote chemistry or materials science graduates who learn on the job.
- Students who pursue professional qualifications in industrial management (SLIM, CIMA) alongside this degree strengthen their management career pathway.
', 'f9e6dbd36402ca989a06c352844db2776f154606ae0b336a77d4abc4d26b5934');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('140', '# Service Management
**Course Number:** 140
**Degree:** Bachelor of Science (Honours) in Service Management
**Duration:** 4 years
**Entry Stream:** Arts, Commerce, Biological Science
**Available at:** Gampaha Wickramarachchi University of Indigenous Medicine (140P)

---

## Overview

Service Management at Gampaha Wickramarachchi University of Indigenous Medicine (GWUIM) is a management degree with a healthcare and wellness service industry orientation, offered as part of GWUIM''s expansion into management education alongside its core indigenous medicine programmes. The programme trains graduates to manage service-oriented organizations — particularly in the health, wellness, hospitality, and social service sectors — combining service quality management, human resource management, operations, and marketing in service contexts.

The service sector is the largest and fastest-growing segment of Sri Lanka''s economy, encompassing healthcare, tourism, banking, retail, telecommunications, and social services. Managing service organizations presents different challenges from manufacturing — services are intangible, co-produced with customers, and highly dependent on human interaction. GWUIM''s Service Management programme addresses these challenges with a curriculum designed for the healthcare, wellness, and hospitality industries that the university serves.

As GWUIM grows from an Ayurveda institute into a full university, Service Management supports its goal of producing not just healthcare practitioners but the managers and administrators needed to run healthcare and wellness organizations efficiently.

---

## What You Will Study

**Year 1 — Management Foundations:**
Principles of Management, Microeconomics and Macroeconomics, Financial Accounting, Service Industries Overview (healthcare, tourism, hospitality, retail), Computer Applications for Business, Business Mathematics and Statistics, Business Communication.

**Year 2 — Service Operations:**
Service Operations Management (capacity planning, queuing, scheduling for service delivery), Human Resource Management for Services (recruiting, training, motivating service staff), Service Quality Management (SERVQUAL model, customer satisfaction measurement, complaint management), Healthcare Management Fundamentals, Marketing of Services (service marketing mix, customer experience), Financial Management, Hospital Administration Basics.

**Year 3 — Specialized Service Management:**
Health Service Administration (managing clinics, hospitals, dispensaries), Wellness Centre Management (Ayurvedic resorts, spa operations), Tourism and Hospitality Service Management, Customer Relationship Management (CRM) Technology, Project Management for Service Organizations, Social Service Management (NGO operations, government social services), Research Methods.

**Year 4 — Research and Practice:**
Industry Attachment (internship at a healthcare organization, hotel, or service company). Individual research project in service management, healthcare administration, or service quality. Electives: Digital Service Delivery, Service Design Thinking, Public Health Administration, Elderly Care Service Management, Event Management.

---

## Career Paths in Sri Lanka

- **Healthcare administration:** Hospital administrator, clinic manager, healthcare operations officer at government and private hospitals, Ayurvedic health centres, and community health organizations.
- **Wellness centre management:** Operations manager at Ayurvedic resorts, spas, yoga centres, and wellness retreats — supporting Sri Lanka''s growing health tourism industry.
- **Hospitality and tourism management:** Front office manager, guest relations manager, operations executive at hotels and resort properties.
- **NGO and social services:** Programme coordinator, project manager at development NGOs, social service organizations, and government social welfare departments.
- **Retail and commercial service management:** Operations supervisor, customer service manager, branch manager at retail chains, banks, and service companies.
- **Government service delivery:** Administrative officer in government service departments — health services, social services, district secretariats.
- **Postgraduate study:** MBA, MSc in Healthcare Management, Service Management, or Hospitality Management.

---

## Entry Requirements

**A/L Stream:** Arts (primary), Commerce, Biological Science
**Typical subjects:** Any combination of Arts or Commerce A/L subjects. Biological Science students interested in healthcare management are also eligible.
**Z-score context:** Service Management (140P) is designed to be accessible to a wide range of A/L students across multiple streams. GWUIM''s specialized focus means this degree has a particular healthcare and wellness orientation that distinguishes it from general management degrees at mainstream universities.

---

## Special Notes

- **Healthcare administration** is a growing career field in Sri Lanka as the private healthcare sector expands. Hospitals increasingly need professionally trained administrators rather than medical doctors managing operations.
- Students who combine this degree with **professional qualifications** (SLIM for marketing, CIMA for finance, IHRA for human resources) strengthen their management career profile considerably.
- GWUIM''s unique position as an indigenous medicine university means Service Management graduates have a natural specialization in **Ayurvedic healthcare and wellness service management** — a genuine differentiator in the Sri Lankan job market.
- The programme is conducted in Sinhala and English.
- Students interested in **social entrepreneurship** — founding a wellness centre, a community health service, or a social service organization — will find the management skills from this programme directly applicable.
', '6d303f98bc0e8298037caad05222c92a55e2af5392e0fea674fcdd135025865c');

INSERT INTO factsheets (course_number, content, content_hash) VALUES ('271', '# Management and Information Technology — Biological Science Stream
**Course Number:** 271
**Degree:** Bachelor of Science (Honours) in Management and Information Technology (MIT) — Biological Science Stream
**Duration:** 4 years
**Entry Stream:** Biological Science
**Available at:** University of Kelaniya (271D)

---

## Overview

Management and Information Technology (MIT) — Biological Science Stream at the University of Kelaniya is a specialized variant of the MIT programme (course 026, typically for Physical Science/Commerce) that specifically admits students who have sat A/L Biology examinations under the Biological Science stream. Offered through the Faculty of Commerce and Management Studies, this programme combines IT skills — programming, databases, systems analysis, network management — with business management and operations, creating graduates who can serve as technical managers in the health, pharmaceutical, agriculture, food science, and biotech sectors.

The Biological Science stream admission pathway exists because many career-ready roles at the intersection of IT and life sciences — hospital information systems, laboratory management software, pharmaceutical data management, agricultural IT solutions — require professionals with a background in both biology-related sciences AND information technology. Traditional IT graduates lack the biological sciences context; traditional biology graduates lack IT proficiency. MIT (Bio Science) bridges this gap.

The University of Kelaniya''s Faculty of Commerce and Management Studies is one of Sri Lanka''s largest management faculties, with strong industry connections and a highly employed graduate community across Sri Lanka''s banking, IT, and healthcare sectors.

---

## What You Will Study

The programme covers the same core MIT curriculum as other MIT streams, with biology-science electives that leverage the student''s A/L background:

**Year 1 — Foundations:**
Programming (Python, Java), Database Fundamentals, Business Mathematics and Statistics, Principles of Management, Computer Networks, General Biology Applications in Management, Scientific Communication, Spreadsheet and Office Applications.

**Year 2 — Core MIT:**
Object-Oriented Programming, Database Design (SQL, ERD), Systems Analysis and Design, Operating Systems, Web Application Development, Business Process Management, Financial Accounting for IT Professionals, IT Project Management.

**Year 3 — Management and Specialized IT:**
Enterprise Resource Planning (ERP), Health Informatics and Hospital Information Systems, Laboratory Information Management Systems (LIMS), Bioinformatics Fundamentals, IT in Agriculture and Food Science, E-government and Digital Public Services, Research Methods, Industrial Training (placement in an IT or healthcare IT firm).

**Year 4 — Specialization and Research:**
Individual research project in health IT, agricultural IT, or management information systems. Electives from: Telemedicine and mHealth, Agricultural Data Analytics, Biotech Data Management, Digital Supply Chain for Pharmaceuticals, GIS Applications in Health and Agriculture.

---

## Career Paths in Sri Lanka

- **Hospital information systems:** IT support officer, health informatics manager, systems administrator for hospital management software (HIS/EMR systems) at government and private hospitals. Nawaloka, Durdans, Hemas, and Lanka Hospitals all operate IT-intensive hospital management systems.
- **Pharmaceutical IT:** Data management, clinical trial IT support, regulatory IT compliance at pharmaceutical companies and clinical research organizations operating in Sri Lanka.
- **Agricultural IT:** Software support and systems management for agricultural management systems, irrigation control systems, and plantation management software.
- **Laboratory management:** LIMS (Laboratory Information Management System) implementation and support at clinical labs, food labs, and environmental testing laboratories.
- **Software development in health/bio sectors:** Junior software developer specializing in healthcare or life-sciences applications — growing sector globally as electronic health records expand.
- **Data analytics:** Business intelligence and data analyst roles at healthcare, pharmaceutical, and agricultural companies — using SQL, Python, and Power BI to analyze operational data.
- **General IT roles:** Like all MIT graduates, the biological science stream graduates are fully equipped for mainstream IT roles in software development, database administration, network support, and IT management — the bio-science orientation is an additional specialization, not a limitation.
- **Postgraduate study:** MSc in Health Informatics, IT Management, Bioinformatics, or Computer Science.

---

## Entry Requirements

**A/L Stream:** Biological Science (specifically for this stream — 271D)
**Typical subjects:** Biology + Chemistry + Physics (or other Biological Science combinations)
**Z-score context:** MIT (Bio Science Stream) (271D) at Kelaniya competes within the Biological Science applicant pool. Its Z-score cutoffs are typically lower than Medicine, Pharmacy, or Veterinary Science, making it an attractive option for Biological Science students who are interested in IT and technology careers. Students who didn''t make Medicine but have strong tech interests should strongly consider this pathway.

---

## Special Notes

- **This is the Biological Science entry pathway** for MIT — the standard MIT programme (026D) admits Physical Science and Commerce stream students. Both lead to the same degree title and similar career outcomes.
- The **health informatics specialization** available through this stream is uniquely valuable: Sri Lanka''s National Health Development Plan emphasizes digitization of health records and telemedicine, creating growing demand for health IT professionals.
- English is the medium of instruction.
- Graduates who complete the MIT programme from Kelaniya enter a **strong alumni network** in Sri Lanka''s IT and banking sectors — Kelaniya''s FOM (Faculty of Commerce and Management Studies) has significant industry relationships.
- Students from the Biological Science stream often find the **programming learning curve steeper** than Physical Science students — but MIT''s curriculum is designed to accommodate this, starting from foundations.
- This is one of the **most career-flexible degrees** for Biological Science students — providing pathways into IT, healthcare IT, banking, and general management.
', 'bdf8e4ff283e91ce374ef0cf8f96bb54fb3fa791690090780cd2a0c9a03c46e2');

[migration 41] Seeded 129 factsheets from /home/msi/project/degree-guidance/content/factsheets
UPDATE alembic_version SET version_num='e75434db887c' WHERE alembic_version.version_num = '093c47d4fb58';

COMMIT;

