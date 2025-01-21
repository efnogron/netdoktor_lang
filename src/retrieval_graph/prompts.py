VERIFICATION_QUERY_TEMPLATE = """In diesem Absatz:
"{context_paragraph}"

müssen wir folgende Aussage überprüfen:
"{sentence}"

Bitte formuliere eine präzise Verifizierungsanfrage, die wir gegen die medizinischen Leitlinien prüfen können.

Die Anfrage sollte mit "verify:" beginnen und in einem neutralen, sachlichen Ton formuliert sein."""

RESULT_SYNTHESIS_PROMPT = """Basierend auf den medizinischen Leitlinien, überprüfe bitte folgende Aussage:

Kontext: {context}
Zu überprüfende Aussage: {query}

Antworte mit "True", "False" oder "Unclear" und erkläre dann deine Bewertung basierend auf den verfügbaren Leitlinien.
Beziehe dich dabei explizit auf die relevanten Stellen in den Leitlinien."""