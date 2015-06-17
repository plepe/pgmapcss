The "active" language
======================
The default language is assessed at compile time by the compile environment or by the parameter `--lang`. In Mode standalone this will be overridden by the active locale or the parameter `--lang` resp. the CGI parameter 'lang'.

The currently active language is returned by the eval function `lang()`.

Function tr(str: string, arg0..n:value)
=======================================
Translates strings (parameter 'str') to the active language, if a translation is available. When the stylesheet is compiled a file '{style_id}.translation/template.json' (path can be overriden, see config_options.md) is created with a list of strings that are used in the style sheet. You can copy this template to a file with an ISO-639-1 language code as basename (e.g. '{style_id}.translation/en.json' for the English translation). If no translation for a string is available, the input string is used instead.

Common OpenStreetMap tags are already known to the tranlsation system, written as 'tag:key' (for the key) resp. 'tag:key=value' (for key/value combinations). E.g. 'tag:amenity=restaurant'. Additionally, the string 'lang:current' is the name of the active language and 'lang:<language_code>' (e.g. 'lang:en') is the name of the given language in the active language. These translations are collected in a Github repository: https://github.com/plepe/openstreetmap-tag-translations

Example:
* When the active language is 'fr', then 'lang:current' equals 'Français' and 'ang:en' equals 'Anglais'.

Occurences of "{}" in the translated string (or the input string) will be replaced by the arguments. You can also specify the nth argument by using "{n}". Additionally all occurances of {m.key}, {m.value} and {m.tag}, where m is the mth condition of the current selector, will be replaced by the key, the value or the full tag (key=value) in _all_ arguments.

Examples:
```css
node {
  text: tr("Test: {1}{}{0}", "bar", "foo");
}
```
* Output: "Test: foobarbar"

```css
node[power=transformer][!transformer] {
  text: tr("{0} without {1}", "{0.tag}", "{1.key}");
}
```
* Output: "power=cable without voltage"
