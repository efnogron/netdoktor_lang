VERIFICATION_QUERY_TEMPLATE = """In diesem Absatz:
"{context_paragraph}"

müssen wir folgende Aussage überprüfen:
"{sentence}"

Bitte formuliere eine präzise Verifizierungsanfrage, die wir gegen die medizinischen Leitlinien prüfen können.

Die Anfrage sollte mit "verify:" beginnen und in einem neutralen, sachlichen Ton formuliert sein."""

RESULT_SYNTHESIS_PROMPT = """Basierend auf den medizinischen Leitlinien, analysiere bitte folgende Aussage:

Kontext: {context}
Zu überprüfende Aussage: {query}

Ursprüngliche Begründung für Überprüfung:
{verification_reasoning}

Deine Aufgabe:
1. Vergleiche die Aussage mit den Leitlinien
2. Bewerte die Übereinstimmung oder mögliche Konflikte
3. Berücksichtige dabei die ursprüngliche Begründung für die Überprüfung
4. Gib eine detaillierte Analyse mit Belegen aus den Leitlinien

WICHTIG: 
- Beziehe dich explizit auf die relevanten Stellen in den Leitlinien
- Bewerte die Konfidenz deiner Analyse
- Markiere unklare oder mehrdeutige Fälle als UNCLEAR
- Bei Konflikten oder Aktualisierungsbedarf als FLAGGED markieren
- Bei Übereinstimmung mit Leitlinien als VALID markieren

Formatiere deine Antwort als strukturiertes JSON gemäß der vorgegebenen Funktion."""

RESULT_SYNTHESIS_PROMPT_CONFIG = [{
            "type": "function",
            "function": {
                "name": "format_verification_result",
                "description": "Format the verification result as a JSON object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["FLAGGED", "VALID", "UNCLEAR"],
                            "description": "Status der Überprüfung. Wenn eine Aussage im Konflikt mit den Leitlinien steht, markiere als FLAGGED. Wenn die Aussage korrekt ist, markiere als VALID. Wenn die Aussage unklar ist oder dazu keine relevante Aussage in den Leitlinien gefunden werden kann, markiere als UNCLEAR."
                        },
                        "confidence_score": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Konfidenz der Analyse"
                        },
                        "relevant_guideline_sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "content": {"type": "string"},
                                    "relevance_score": {"type": "number"},
                                    "section_metadata": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"type": "string"},
                                            "page": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "analysis": {
                            "type": "object",
                            "properties": {
                                "potential_conflict": {"type": "string"},
                                "reasoning": {"type": "string"},
                                "suggested_update": {"type": "string"}
                            },
                            "required": ["reasoning"]
                        },
                        "context_assessment": {
                            "type": "object",
                            "properties": {
                                "missing_context": {"type": "boolean"},
                                "ambiguity_issues": {"type": "boolean"},
                                "context_notes": {"type": "string"}
                            }
                        }
                    },
                    "required": ["status", "confidence_score", "relevant_guideline_sections", "analysis"]
                }
            }
        }]