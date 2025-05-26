import re
def extraire_medicaments_posologie(nlp,texte):
    doc = nlp(texte)
    resultats = []

    pattern_poso = re.compile(r"(\d+mg|\d+g|\d+mcg|\d+ml)[^\.\,]*")

    for i, token in enumerate(doc):
        # Cherche les médicaments : noms après "de", "du", "l'", etc.
        if token.pos_ == "NOUN" and token.text.lower() in ["amoxicilline", "paracétamol", "ciprofloxacine"]:
            # Cherche à droite la posologie dans le texte brut
            span_text = doc[i:i+6].text  # max 6 tokens à droite
            match = pattern_poso.search(span_text)
            if match:
                resultats.append((token.text, match.group()))

    return resultats

def negation_extraction(nlp,texte):
    negations = []
    doc = nlp(texte)

    for token in doc:
        # Vérifie si c'est un verbe principal
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            # Détection des enfants liés à une négation (ex: 'ne', 'pas')
            negation = any(child.dep_ == "advmod" and child.text.lower() in ["pas", "plus", "jamais"] 
                           or child.dep_ == "neg"
                           for child in token.children)

            negations.append((token.lemma_, negation))

    return negations

def extraire_relations(nlp,texte):
    relations = []
    doc = nlp(texte)

    for token in doc:
        # Relation sujet-verbe-objet
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            sujet = [child for child in token.children if child.dep_ == "nsubj"]
            obj = [child for child in token.children if child.dep_ in ["obj", "obl:arg", "obl"]]

            # Gestion des Négations
            negation = any(s.dep_ =="neg" for s in token.children) 
            
            for s in sujet:
                for o in obj:
                    verb = token.lemma_
                    if negation:
                        verb = "Ne pas"+verb
                    relations.append((s.text.lower(), verb, o.text.lower()))

        # Relation complément circonstanciel (ex: "en raison de saignements")
        if token.text.lower() in ["raison", "cause", "motif"]:  # pivot nominal
            head = token.head
            cc_obj = [child for child in token.children if child.dep_ in ["nmod", "fixed", "det", "amod", "obl"]]
            for child in cc_obj:
                if head.dep_ == "ROOT":
                    relations.append((child.text.lower(), token.text.lower(), head.lemma_))

    return relations