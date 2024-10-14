# Getting started with Correct Markdown

Markdown corrector, error explanation and word definition

## Features

Reads a markdown file and rewrites it following the template:

<< Markdown with corrections >>

<< Definitions >>

<< Correction explanations >>

- Every word or expression enclosed by ** generates an entry in
  the Definitions section. The entry gives the meaning of the enclosed
  expression.
- Every correction made in the original text is marked with a number index
  that is linked to an entry in the Correction explanations section. In this
  section is given an explanation of why the correction was made. The original
  text is not deleted, but strike through.


## Example

```
# Input Markdown

Arnaud fait 1m80 et c'est un type en forme pour son âge. Il fait du sport assez
régulierment malgré la petite pochette qui insiste à l'accompagner partout. Il
tiens sur ses épaules non seulement le titre de directeur comptable du celèbre
fabricant de meubles "C'est Dubois", mais aussi une grosse **tronche** carré
étrangement orné d'yeux en amande et des sourcils si **touffus** que parfois on a
l'impression d'entendre les cris des poussins appelant leur mère à rentrer au
nid.

# Corrected Markdown

Arnaud fait 1m80 et c'est un type en forme pour son âge. Il fait du sport assez
~~régulierment~~ régulièrement[^1] malgré la petite ~~pochette~~ bedaine[^2]
qui ~~insiste à l'accompagner~~ l'accompagne[^3] partout. Il ~~tiens~~
porte[^4] sur ses épaules non seulement le titre de directeur comptable du
~~celèbre~~ célèbre[^5] fabricant de meubles "C'est Dubois", mais aussi une
grosse **tronche** ~~carré~~ carrée[^6] étrangement ~~orné~~ ornée[^7] d'yeux
en amande et ~~des~~ de[^8] sourcils si **touffus** que parfois on a
l'impression d'entendre les cris des poussins appelant leur mère à rentrer au
nid.


## Definitions

1. **tronche**: Extrémité supérieure, visage, tête.

2. **touffus**: Qui est fourni et abondant.


## Explanations

[^1]: La modification a été faite pour remplacer "régulierment" par "régulièrement" afin de corriger l'orthographe et d'ajuster l'adverbe pour qu'il corresponde correctement au verbe "fait" dans la phrase.

[^2]: La modification remplace "pochette" par "bedaine" pour utiliser un terme plus familier et approprié pour décrire le ventre qui est mentionné dans le contexte.

[^3]: La modification remplace "insiste à l'accompagner" par "l'accompagne" pour simplifier la phrase et rendre le texte plus fluide en supprimant le verbe "insister" et en rendant le sujet de l'action plus clair.

[^4]: La modification remplace "tiens" par "porte" pour correspondre au sujet pluriel "il" et assurer la concordance des temps et des accords dans la phrase.

[^5]: La modification remplace "celèbre" par "célèbre" pour corriger l'orthographe du mot et ainsi respecter l'accentuation correcte sur la lettre "è".

[^6]: La modification remplace "carré" par "carrée" pour accorder le mot en genre féminin avec le nom féminin "tronche" et assurer la concordance des adjectifs en genre et en nombre.

[^7]: La modification remplace "orné" par "ornée" pour accorder le participe passé avec le nom féminin "tronche".

[^8]: La modification remplace "des" par "de" pour indiquer la possession des sourcils par la grosse tronche carrée et assurer la concordance des adjectifs possessifs en français.
```


## How to use

To correct a markdown file several steps are necessary. These steps are described in a makefile.

```bash
make BUILD_FOLDER=build MARKDOWN_FILE=input-markdown.md LANGUAGE=french TITLE="My title"
```

It is necessary to create a `llm-assistant-config.toml` file before execution. To create this file,
follow the model provided in `llm-assistant-config-model.toml`.


## Contributing

Please reference to our [contribution](http://danoan.github.io/correct-markdown/contributing) and [code-of-conduct]((http://danoan.github.io/correct-markdown/code-of-conduct.md)) guidelines.
