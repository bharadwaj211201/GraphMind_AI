"""
==========================================================
DOMAIN KNOWLEDGE BASE - EXPANDED BIG DATA ONTOLOGY
Knowledge Graph & Data Collection Engine
Targeted for CDAC BDA Project Specifications
==========================================================
"""

# ==========================================================
# MISSIONS (100+ Core Missions & Programs)
# ==========================================================

MISSIONS = [
    # Lunar Exploration
    "Chandrayaan-1", "Chandrayaan-2", "Chandrayaan-3", "Chandrayaan-4", "LUPEX",
    
    # Solar & Space Physics
    "Aditya-L1", "XPoSat", "AstroSat",
    
    # Planetary Exploration
    "Mars Orbiter Mission", "Mangalyaan", "Mangalyaan-2", "Venus Orbiter Mission", "Shukrayaan-1",
    
    # Human Spaceflight & Technology Demonstrators
    "Gaganyaan", "TV-D1", "TV-D2", "TV-D3", "TV-D4", "Gaganyaan-1", "Gaganyaan-2", "Gaganyaan-3",
    "CARE", "SRE-1", "SRE-2", "RLV-TD", "RLV-LEX 01", "RLV-LEX 02", "RLV-LEX 03", "SpaDeX",
    "Bharatiya Antariksh Station",
    
    # Navigation (NavIC / IRNSS)
    "NavIC", "IRNSS", "IRNSS-1A", "IRNSS-1B", "IRNSS-1C", "IRNSS-1D", "IRNSS-1E", "IRNSS-1F", "IRNSS-1G", "IRNSS-1H", "IRNSS-1I", "NVS-01", "NVS-02",
    
    # Earth Observation & Remote Sensing (EOS / Cartosat / RISAT / Oceansat / Resourcesat)
    "EOS-01", "EOS-02", "EOS-03", "EOS-04", "EOS-05", "EOS-06", "EOS-07", "EOS-08",
    "Cartosat-1", "Cartosat-2", "Cartosat-2A", "Cartosat-2B", "Cartosat-2C", "Cartosat-2D", "Cartosat-2E", "Cartosat-2F", "Cartosat-3",
    "RISAT-1", "RISAT-1A", "RISAT-2", "RISAT-2B", "RISAT-2BR1", "RISAT-2BR2",
    "Oceansat-1", "Oceansat-2", "Oceansat-3", "Scatsat-1", "Resourcesat-1", "Resourcesat-2", "Resourcesat-2A", "HySIS", "SARAL",
    
    # Radar & Joint International Missions
    "NISAR", "Axiom-4", "TRISHNA", "Megha-Tropiques",
    
    # Historical Pioneer Missions
    "Aryabhata", "Bhaskara-I", "Bhaskara-II", "Rohini RS-1", "Rohini RS-D1", "APPLE", "Youthsat", "IMS-1", "ANUSAT", "STUDSAT"
]

# ==========================================================
# ORGANIZATIONS & COMPANIES (100+ Space Industry Entities)
# ==========================================================

ORGANIZATIONS = [
    # Indian Government & Space Agencies
    "ISRO", "Indian Space Research Organisation", "Department of Space", "NSIL", "NewSpace India Limited",
    "IN-SPACe", "Antrix Corporation", "DRDO", "Indian Air Force", "IMD", "National Remote Sensing Centre",
    
    # Aerospace & Defense Industry Partners (Indian)
    "Hindustan Aeronautics Limited", "HAL", "Larsen & Toubro", "L&T Aerospace", "Godrej Aerospace",
    "Ananth Technologies", "MTAR Technologies", "Centum Electronics", "Data Patterns", "Walchandnagar Industries",
    "BrahMos Aerospace", "Bharat Electronics Limited", "BEL", "BHEL", "Tata Advanced Systems",
    
    # Space Startups (Indian NewSpace Ecosystem)
    "Skyroot Aerospace", "Agnikul Cosmos", "Pixxel", "Dhruva Space", "Bellatrix Aerospace", "Digantara",
    "GalaxEye Space", "D空间", "SatSure", "Astrogate Labs",
    
    # Global Space Agencies
    "NASA", "ESA", "JAXA", "Roscosmos", "CNES", "DLR", "CSA", "ASI", "UAE Space Agency", "CNSA", "UK Space Agency",
    
    # Global Commercial & NewSpace Companies
    "SpaceX", "Axiom Space", "Blue Origin", "Rocket Lab", "United Launch Alliance", "ULA", "Arianespace",
    "Astrobotic", "Intuitive Machines", "Planet Labs", "Spire Global", "Maxar Technologies"
]

# ==========================================================
# ISRO CENTRES & INSTITUTES
# ==========================================================

CENTRES = [
    "VSSC", "Vikram Sarabhai Space Centre",
    "URSC", "U R Rao Satellite Centre", "ISAC", "ISRO Satellite Centre",
    "SDSC SHAR", "Satish Dhawan Space Centre",
    "ISTRAC", "ISRO Telemetry Tracking and Command Network",
    "LPSC", "Liquid Propulsion Systems Centre",
    "IPRC", "ISRO Propulsion Complex",
    "SAC", "Space Applications Centre",
    "NRSC", "National Remote Sensing Centre",
    "MCF", "Master Control Facility",
    "LEOS", "Laboratory for Electro-Optics Systems",
    "HSFC", "Human Space Flight Centre",
    "IISU", "ISRO Inertial Systems Unit",
    "DECU", "Development and Educational Communication Unit",
    "IDSN", "Indian Deep Space Network",
    "MOX", "Mission Operations Complex",
    "PRL", "Physical Research Laboratory",
    "SPL", "Space Physics Laboratory",
    "NARL", "National Atmospheric Research Laboratory",
    "NESAC", "North Eastern Space Applications Centre",
    "SCL", "Semi-Conductor Laboratory",
    "IIST", "Indian Institute of Space Science and Technology",
    "IIA", "Indian Institute of Astrophysics"
]

# ==========================================================
# LAUNCH VEHICLES
# ==========================================================

LAUNCH_VEHICLES = [
    "SLV-3", "ASLV", "PSLV", "PSLV-G", "PSLV-CA", "PSLV-XL", "PSLV-DL", "PSLV-QL",
    "GSLV", "GSLV Mk I", "GSLV Mk II", "GSLV Mk III", "LVM3", "SSLV", "RLV-TD", "NGLV",
    "Saturn V", "Falcon 9", "Falcon Heavy", "Starship", "Ariane 5", "Ariane 6", "H-IIA", "H3", "Soyuz"
]

# ==========================================================
# ROCKET VARIANTS (PSLV-C1..C65, GSLV-F01..F16, LVM3-M1..M6, SSLV-D1..D3)
# ==========================================================

ROCKET_VARIANTS = [
    # PSLV Missions
    "PSLV-D1", "PSLV-D2", "PSLV-D3",
    "PSLV-C1", "PSLV-C2", "PSLV-C3", "PSLV-C4", "PSLV-C5", "PSLV-C6", "PSLV-C7", "PSLV-C8", "PSLV-C9", "PSLV-C10",
    "PSLV-C11", "PSLV-C12", "PSLV-C13", "PSLV-C14", "PSLV-C15", "PSLV-C16", "PSLV-C17", "PSLV-C18", "PSLV-C19", "PSLV-C20",
    "PSLV-C21", "PSLV-C22", "PSLV-C23", "PSLV-C24", "PSLV-C25", "PSLV-C26", "PSLV-C27", "PSLV-C28", "PSLV-C29", "PSLV-C30",
    "PSLV-C31", "PSLV-C32", "PSLV-C33", "PSLV-C34", "PSLV-C35", "PSLV-C36", "PSLV-C37", "PSLV-C38", "PSLV-C39", "PSLV-C40",
    "PSLV-C41", "PSLV-C42", "PSLV-C43", "PSLV-C44", "PSLV-C45", "PSLV-C46", "PSLV-C47", "PSLV-C48", "PSLV-C49", "PSLV-C50",
    "PSLV-C51", "PSLV-C52", "PSLV-C53", "PSLV-C54", "PSLV-C55", "PSLV-C56", "PSLV-C57", "PSLV-C58", "PSLV-C59", "PSLV-C60",
    "PSLV-C61", "PSLV-C62", "PSLV-C63", "PSLV-C64", "PSLV-C65",

    # GSLV Missions
    "GSLV-D1", "GSLV-D2", "GSLV-D3", "GSLV-D5", "GSLV-D6",
    "GSLV-F01", "GSLV-F02", "GSLV-F03", "GSLV-F04", "GSLV-F05", "GSLV-F06", "GSLV-F07", "GSLV-F08", "GSLV-F09", "GSLV-F10",
    "GSLV-F11", "GSLV-F12", "GSLV-F13", "GSLV-F14", "GSLV-F15", "GSLV-F16",

    # LVM3 Missions
    "LVM3-X", "LVM3-M1", "LVM3-M2", "LVM3-M3", "LVM3-M4", "LVM3-M5", "LVM3-M6",

    # SSLV Missions
    "SSLV-D1", "SSLV-D2", "SSLV-D3"
]

# ==========================================================
# SATELLITES (Communication, EO, Nav, Science)
# ==========================================================

SATELLITES = [
    # Communication (GSAT / INSAT)
    "GSAT-1", "GSAT-2", "GSAT-3", "GSAT-4", "GSAT-5P", "GSAT-6", "GSAT-6A", "GSAT-7", "GSAT-7A", "GSAT-8", "GSAT-9",
    "GSAT-10", "GSAT-11", "GSAT-12", "GSAT-12R", "GSAT-14", "GSAT-15", "GSAT-16", "GSAT-17", "GSAT-18", "GSAT-19",
    "GSAT-20", "GSAT-24", "GSAT-29", "GSAT-30", "GSAT-31", "GSAT-N2",
    "INSAT-1A", "INSAT-1B", "INSAT-1C", "INSAT-1D", "INSAT-2A", "INSAT-2B", "INSAT-2C", "INSAT-2D", "INSAT-2E",
    "INSAT-3A", "INSAT-3B", "INSAT-3C", "INSAT-3D", "INSAT-3DR", "INSAT-3DS", "INSAT-4A", "INSAT-4B", "INSAT-4CR",
    
    # Earth Observation & Sensing
    "EOS-01", "EOS-02", "EOS-03", "EOS-04", "EOS-05", "EOS-06", "EOS-07", "EOS-08",
    "Cartosat-1", "Cartosat-2", "Cartosat-2A", "Cartosat-2B", "Cartosat-2C", "Cartosat-2D", "Cartosat-2E", "Cartosat-3",
    "RISAT-1", "RISAT-2", "RISAT-2B", "RISAT-2BR1", "Oceansat-1", "Oceansat-2", "Oceansat-3", "Scatsat-1", "HySIS",
    
    # Scientific & Navigation
    "AstroSat", "Aditya-L1", "XPoSat", "NISAR", "IRNSS-1A", "IRNSS-1B", "IRNSS-1C", "IRNSS-1D", "IRNSS-1E", "IRNSS-1F", "IRNSS-1G", "NVS-01"
]

# ==========================================================
# SPACECRAFT & MODULES
# ==========================================================

SPACECRAFT = [
    "Orbiter", "Lander", "Rover", "Lander Module", "Propulsion Module", "Vikram", "Pragyan",
    "Crew Module", "Service Module", "Orbital Module", "Crew Escape System", "Crew Escape Tower",
    "Vyommitra", "Target Spacecraft", "Chaser Spacecraft", "Crew Dragon", "Dragon Capsule",
    "Bharatiya Antariksh Station Module"
]

# ==========================================================
# PAYLOADS & INSTRUMENTS
# ==========================================================

PAYLOADS = [
    # Chandrayaan-3
    "ChaSTE", "ILSA", "RAMBHA", "RAMBHA-LP", "Laser Retroreflector Array", "SHAPE", "LIBS", "APXS",
    # Chandrayaan-2
    "DFSAR", "CLASS", "OHRC", "IIRS", "CHACE-2", "TMC-2", "XSM",
    # Aditya-L1
    "VELC", "SUIT", "HEL1OS", "ASPEX", "PAPA", "SoLEXS", "MAG",
    # AstroSat
    "UVIT", "LAXPC", "CZTI", "SXT", "SSM",
    # NISAR & XPoSat
    "L-band SAR", "S-band SAR", "POLIX", "XSPECT",
    # Generic Payloads
    "Synthetic Aperture Radar", "Multispectral Camera", "Hyperspectral Imager", "Optical Camera",
    "Atomic Clock", "Navigation Payload", "Communication Transponder"
]

INSTRUMENTS = [
    "Terrain Mapping Camera", "Terrain Mapping Camera-2", "Imaging Infrared Spectrometer",
    "Orbiter High Resolution Camera", "Dual Frequency Synthetic Aperture Radar",
    "Laser Induced Breakdown Spectroscope", "Alpha Particle X-ray Spectrometer",
    "Visible Emission Line Coronagraph", "Solar Ultraviolet Imaging Telescope",
    "High Energy L1 Orbiting X-ray Spectrometer", "Solar Low Energy X-ray Spectrometer",
    "Plasma Analyser Package for Aditya", "Magnetometer", "Ultraviolet Imaging Telescope",
    "Soft X-ray Telescope", "Cadmium Zinc Telluride Imager", "Large Area X-ray Proportional Counter"
]

# ==========================================================
# ASTRONAUTS & SCIENTISTS
# ==========================================================

ASTRONAUTS = [
    "Rakesh Sharma", "Kalpana Chawla", "Sunita Williams",
    "Shubhanshu Shukla", "Prasanth Balakrishnan Nair", "Ajit Krishnan", "Angad Pratap",
    "Vyommitra", "Peggy Whitson", "Michael Lopez-Alegria", "John Shoffner", "Marcus Wandt"
]

SCIENTISTS = [
    "Vikram Sarabhai", "Satish Dhawan", "U. R. Rao", "A. P. J. Abdul Kalam", "K. Kasturangan",
    "G. Madhavan Nair", "K. Radhakrishnan", "A. S. Kiran Kumar", "K. Sivan", "S. Somanath",
    "V. Narayanan", "Mylswamy Annadurai", "S. Unnikrishnan Nair", "P. Veeramuthuvel",
    "Ritu Karidhal", "Nandini Harinath", "M. Vanitha", "S. Mohana Kumar", "S. Arunan",
    "S. Ramakrishnan", "Anil Bhardwaj", "Tapan Misra", "B. N. Suresh", "V. R. Lalithambika"
]

# ==========================================================
# GEOGRAPHY & FACILITIES
# ==========================================================

COUNTRIES = ["India", "United States", "Japan", "France", "Russia", "Germany", "Canada", "Australia", "United Kingdom", "Italy", "Israel", "Brazil", "South Korea", "UAE", "Singapore"]
STATES = ["Andhra Pradesh", "Karnataka", "Kerala", "Tamil Nadu", "Telangana", "Maharashtra", "Gujarat", "Odisha"]
CITIES = ["Bengaluru", "Hyderabad", "Ahmedabad", "Sriharikota", "Thiruvananthapuram", "Mahendragiri", "Hassan", "Lucknow", "New Delhi", "Mumbai", "Chennai"]
SPACEPORTS = ["Satish Dhawan Space Centre", "SDSC SHAR", "First Launch Pad", "Second Launch Pad", "Third Launch Pad", "Kulasekarapattinam Spaceport"]
FACILITIES = ["Mission Operations Complex", "Indian Deep Space Network", "ISRO Telemetry Tracking and Command Network", "Payload Integration Facility", "Vehicle Assembly Building", "Solid Propellant Space Booster Plant", "ISRO Propulsion Complex"]
LABORATORIES = ["Physical Research Laboratory", "Space Physics Laboratory", "Laboratory for Electro Optics Systems", "Indian Institute of Astrophysics", "Indian Institute of Space Science and Technology"]

# ==========================================================
# CELESTIAL BODIES, TECHNOLOGIES & PROGRAMS
# ==========================================================

CELESTIAL_BODIES = ["Earth", "Moon", "Mars", "Sun", "Venus", "Mercury", "Jupiter", "Saturn", "South Pole", "Lunar South Pole", "Shiv Shakti Point", "Tiranga Point", "Jawahar Point", "Corona", "Photosphere", "Chromosphere", "L1", "L2", "Low Earth Orbit", "Geostationary Orbit", "Polar Orbit", "Sun Synchronous Orbit", "Geosynchronous Transfer Orbit"]

TECHNOLOGIES = ["Cryogenic Engine", "CE-20 Engine", "CE-7.5 Engine", "Vikas Engine", "Semi Cryogenic Engine", "Solid Rocket Motor", "S200 Booster", "PS1 Stage", "PS2 Stage", "PS3 Stage", "PS4 Stage", "Autonomous Navigation", "Soft Landing", "Terrain Relative Navigation", "Hazard Detection", "Reaction Wheel", "Star Sensor", "Synthetic Aperture Radar", "Hyperspectral Imaging", "Telemetry", "Telecommand", "Reusable Launch Vehicle", "Space Docking", "Human Spaceflight"]

PROGRAMS = ["Indian Space Programme", "Chandrayaan Programme", "Gaganyaan Programme", "NavIC Programme", "Earth Observation Programme", "Planetary Exploration Programme", "Human Spaceflight Programme", "Reusable Launch Vehicle Programme"]

DOCUMENT_TYPES = ["Press Release", "Mission Page", "Research Paper", "Technical Report", "Launch Brochure", "Mission Brochure", "Annual Report", "News", "Presentation"]

# Mission Aliases Mapping
MISSION_ALIASES = {
    "mars orbiter mission": "Mangalyaan", "mom": "Mangalyaan",
    "aditya l1": "Aditya-L1", "spadex": "SpaDeX",
    "tvd1": "TV-D1", "tv-d1": "TV-D1", "nisar mission": "NISAR",
    "chandrayaan 3": "Chandrayaan-3", "chandrayaan 2": "Chandrayaan-2", "chandrayaan 1": "Chandrayaan-1"
}

# Organization Aliases Mapping
ORGANIZATION_ALIASES = {
    "isro": "ISRO", "indian space research organisation": "ISRO",
    "nasa": "NASA", "national aeronautics and space administration": "NASA",
    "esa": "ESA", "european space agency": "ESA",
    "jaxa": "JAXA", "japan aerospace exploration agency": "JAXA",
    "roscosmos": "Roscosmos", "cnes": "CNES", "dlr": "DLR",
    "nsil": "NSIL", "newspace india limited": "NSIL",
    "in space": "IN-SPACe", "inspace": "IN-SPACe",
    "antrix": "Antrix Corporation", "hal": "Hindustan Aeronautics Limited"
}

# Centre Aliases Mapping
CENTRE_ALIASES = {
    "vssc": "Vikram Sarabhai Space Centre",
    "ursc": "U R Rao Satellite Centre", "isac": "U R Rao Satellite Centre",
    "sdsc": "Satish Dhawan Space Centre", "shar": "Satish Dhawan Space Centre", "sdsc shar": "Satish Dhawan Space Centre",
    "istrac": "ISRO Telemetry Tracking and Command Network",
    "lpsc": "Liquid Propulsion Systems Centre",
    "iprc": "ISRO Propulsion Complex",
    "sac": "Space Applications Centre",
    "nrsc": "National Remote Sensing Centre",
    "mcf": "Master Control Facility",
    "leos": "Laboratory for Electro-Optics Systems",
    "hsfc": "Human Space Flight Centre",
    "iisu": "ISRO Inertial Systems Unit",
    "idsn": "Indian Deep Space Network",
    "prl": "Physical Research Laboratory",
    "spl": "Space Physics Laboratory",
    "narl": "National Atmospheric Research Laboratory",
    "nesac": "North Eastern Space Applications Centre",
    "scl": "Semi-Conductor Laboratory",
    "iist": "Indian Institute of Space Science and Technology"
}