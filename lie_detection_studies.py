"""
Módulo con la base científica y utilidades para estudios de detección de engaño.
Incluye función para obtener citas relevantes según el tema.
"""

import unicodedata

studies = [
    {
        "id": 1,
        "title": "Facial Expressions of Emotion",
        "authors": "Paul Ekman & Wallace V. Friesen",
        "institution": "UCSF",
        "year": 1975,
        "summary": "Identificación de microexpresiones faciales involuntarias que delatan emociones ocultas.",
        "impact": "Inspiró la serie Lie to Me y es usado por el FBI, la CIA y policías internacionales.",
        "citation": "Ekman, P., & Friesen, W. V. (1975). Unmasking the face."
    },
    {
        "id": 2,
        "title": "Detecting deception by manipulating cognitive load",
        "authors": "Vrij, A., Fisher, R. P., Mann, S., & Leal, S.",
        "institution": "University of Portsmouth",
        "year": 2006,
        "summary": "Mentir consume más recursos cognitivos que decir la verdad. Aumentar la carga cognitiva mejora la detección.",
        "citation": "Vrij, A., Fisher, R. P., Mann, S., & Leal, S. (2006)."
    },
    {
        "id": 3,
        "title": "Brain activity during simulated deception: an event-related functional magnetic resonance study",
        "authors": "Langleben, D. D. et al.",
        "institution": "University of Pennsylvania",
        "year": 2002,
        "summary": "Diferentes áreas cerebrales (corteza prefrontal) se activan al mentir vs. decir la verdad.",
        "citation": "Langleben, D. D. et al. (2002)."
    },
    {
        "id": 4,
        "title": "Cues to deception",
        "authors": "Bella DePaulo et al.",
        "institution": "University of California, Santa Barbara",
        "year": 2003,
        "summary": "No hay una única señal verbal infalible, pero patrones como menor fluidez, más justificaciones y menos detalles sensoriales son comunes en mentirosos.",
        "citation": "DePaulo, B. M., Lindsay, J. J., Malone, B. E., et al. (2003)."
    },
    {
        "id": 5,
        "title": "Modelo SCAN (Scientific Content Analysis)",
        "authors": "Avinoam Sapir",
        "institution": "SCAN",
        "year": 1996,
        "summary": "Las estructuras lingüísticas y omisiones revelan engaño o manipulación.",
        "citation": "Sapir, A. (1996)."
    },
    {
        "id": 6,
        "title": "AI y Deep Learning en detección de mentiras",
        "authors": "MIT, Carnegie Mellon",
        "institution": "MIT, Carnegie Mellon",
        "year": 2020,
        "summary": "Algoritmos de IA analizan patrones de voz, pausas, expresiones y textos. Algunos modelos superan a humanos en precisión (>75%).",
        "citation": "Estudios recientes (2020)."
    },
    {
        "id": 7,
        "title": "Teoría de la Detección de Engaño Emocional – Emotion Leakage",
        "authors": "Mark Frank & Thomas Feeley",
        "institution": "University at Buffalo",
        "year": 2003,
        "summary": "Los intentos de control emocional ante una mentira suelen fallar levemente en la cara, especialmente en los ojos y boca.",
        "citation": "Frank, M. G., & Feeley, T. H. (2003)."
    }
]

def get_study_citation_by_topic(topic):
    """Devuelve la cita y el resumen de un estudio relevante según el tema o palabra clave normalizada."""
    def normalize(text):
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()
    topic_norm = normalize(topic)
    topic_aliases = {
        "fmri": ["fmri", "resonancia", "f m r i", "magnetic resonance", "resonancia cerebral"],
        "resonancia": ["fmri", "resonancia", "f m r i", "magnetic resonance", "resonancia cerebral"],
        "verbal": ["verbal", "paraverbal", "señal verbal", "señales verbales", "verbales", "verbalidad"],
    }
    for s in studies:
        title_norm = normalize(s["title"])
        summary_norm = normalize(s["summary"])
        # Coincidencia directa o por subcadena
        if topic_norm in title_norm or topic_norm in summary_norm:
            return (s["citation"], s["summary"])
        # Coincidencia por alias: buscar si algún alias está como subcadena en el título o resumen
        for key, aliases in topic_aliases.items():
            alias_norms = [normalize(alias) for alias in aliases]
            if topic_norm == key or topic_norm in alias_norms:
                for alias_norm in alias_norms:
                    if alias_norm in title_norm or alias_norm in summary_norm:
                        return (s["citation"], s["summary"])
        # Coincidencia explícita: si cualquier alias está en el título o resumen (no solo para keys)
        for aliases in topic_aliases.values():
            for alias in aliases:
                alias_norm = normalize(alias)
                if alias_norm in title_norm or alias_norm in summary_norm:
                    return (s["citation"], s["summary"])
    return (None, None)
