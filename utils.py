KEYWORDS = [
    '@sentientAGI', 'sentient', 'ROMA', 'ODS', 'open source ai', 
    'open source AGI', 'AGI', 'Sentient Foundation', 'Open AGI Summit', 
    'Sentient Eco', 'Dobby API', 'GRID'
]




GITHUB_ORGS = ['sentient-agi', 'sentient-engineering']

MONITORED_REPOS = [
    'ROMA', 'Sentient-Enclaves-Framework', 'Sentient-Agent-Client', 'Sentient-Agent-Framework-Examples',
    'Sentient-Agent-Framework', 'OpenDeepSearch', 'Sentient-Social-Agent', 'OML-1.0-Fingerprinting',
    'werewolf-template', 'sentient', 'jobber', 'agent-q', 'multi-agent-fsm'
]


def matches_keywords(text):
    return any(kw.lower() in text.lower() for kw in KEYWORDS)