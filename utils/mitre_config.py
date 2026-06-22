"""
Configuración y mapeo del framework MITRE ATT&CK para la herramienta Warebox.
"""

# Diccionario para traducir los "short codes" de Hayabusa a nombres oficiales MITRE
MITRE_MAPPING = {
    "initaccess": "Initial Access",
    "exec": "Execution",
    "persis": "Persistence",
    "privesc": "Privilege Escalation",
    "evas": "Defense Evasion",
    "credaccess": "Credential Access",
    "disc": "Discovery",
    "latmvmt": "Lateral Movement",
    "collect": "Collection",
    "c2": "Command and Control",
    "exfil": "Exfiltration",
    "impact": "Impact",
    "recon": "Reconnaissance",
    "resdev": "Resource Development"
}

# Orden oficial de la cadena de ataque (Kill Chain) de MITRE ATT&CK
MITRE_ORDER = [
    "Reconnaissance", "Resource Development", "Initial Access", "Execution",
    "Persistence", "Privilege Escalation", "Defense Evasion", "Credential Access",
    "Discovery", "Lateral Movement", "Collection", "Command and Control",
    "Exfiltration", "Impact"
]