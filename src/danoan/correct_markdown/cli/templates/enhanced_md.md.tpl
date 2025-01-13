{{text}}

## Summary

{{summary}}

## Definitions

{% for entry in words_definitions -%}

{{loop.index}}. **{{entry.Word}}**: {{entry.Definition}}

{% endfor %}

## Corrections

{% for entry in corrections_explanations -%}

[^{{loop.index}}]: {{entry}}

{% endfor %}
