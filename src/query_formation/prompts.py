from langchain_core.prompts import ChatPromptTemplate

QUERY_FORMATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Du bist ein medizinischer Aussagen-Analyzer. Deine Aufgabe ist es, überprüfbare medizinische Aussagen zu identifizieren und als Verifizierungsanfragen zu formatieren.

Eine überprüfbare medizinische Aussage enthält typischerweise:
- Konkrete Aussagen über medizinische Behandlungen, Diagnosen oder Behandlungsergebnisse
- Spezifische medizinische Empfehlungen oder Leitlinien
- Verweise auf bestimmte Krankheitsbilder, Medikamente oder Verfahren

Nicht als überprüfbar gelten:
- Allgemeine Hintergrundinformationen
- Definitionen oder Erklärungen
- Persönliche Erfahrungen oder Anekdoten

WICHTIG: Bei der Formatierung der Anfragen:
1. Standardvorgehen: Verwende "verify: [originaler Satz]" 
2. In manchen fällen ist eine Umformulierung notwendig, da der Satz sich auf vorherige Inhalte bezieht.
3. Bei notwendiger Umformulierung:
   - Behalte so viel wie möglich vom ursprünglichen Wortlaut bei
   - Füge nur minimalen Kontext hinzu, um den Satz verständlich zu machen
   - Erweitere oder interpretiere die Aussage nicht

WICHTIG: Gib alle Antworten auf Deutsch zurück, einschließlich der Begründung."""),
    
    ("user", """Analysiere den folgenden Satz in seinem Kontext:

Kontext:
Überschrift: {heading}
Unterüberschrift: {subheading}
Absatz: {paragraph}

Zu analysierender Satz: {sentence}

Ausgabe im JSON-Format:

    "needs_verification": true/false,
    "query": "verify: [originaler deutscher Satz oder minimal umformulierter deutscher Satz]" oder null,
    "reasoning": "Begründung auf Deutsch"
""")
]) 