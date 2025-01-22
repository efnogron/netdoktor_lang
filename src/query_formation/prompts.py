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

""")
]) 

QUERY_FORMATION_PROMPT_CONFIG = [{
                "type": "function",
                "function": {
                    "name": "format_analysis",
                    "description": "Format the analysis result as a JSON object",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "needs_verification": {
                                "type": "boolean",
                                "description": "Whether the sentence needs verification"
                            },
                            "query": {
                                "type": "string",
                                "description": "The verification query, starting with 'verify: ' or null if no verification needed"
                            },
                            "reasoning": {
                                "type": "string",
                                "description": "Explanation of what needs to be verified."
                            }
                        },
                        "required": ["needs_verification", "reasoning"]
                    }
                }
            }]