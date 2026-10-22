GeneWeb uses Wikitext, a markup language that offers a simplified alternative to HTML and is used to write pages in wiki websites such as Wikipedia.

A toolbar around text zones allows adding wikitext easily:

Barre wiki.png
Title of the page
Add the “TITLE=” tag before the text.

TITLE=…
Table of contents
The use of heading and subheading format elements, allows for better organization within an article.

= Heading 1 =
== Subheading 2 ==
=== Subheading 3 ===
==== Subheading 4 ====
===== Subheading 5 =====
====== Subheading 6 ======
Once an article has four headings, a table of contents (TOC) will automatically generate. Available options to customize the TOC, include:

To automatically hide the TOC when the article loads, use:
__NOTOC__
To place a table of contents at a specific position, overriding [], use:
__TOC__
To place a shortened TOC, showing only main section headings without subheadings, use:
__SHORT_TOC__
When editing the content of a note is allowed, GeneWeb opens the edit window section—by—section, with three arrows (left, up, right) provided at the top left of the page to allow for easier navigation between sections.

Text formatting
You can format your text using wiki markup. This consists of normal characters such as asterisks, single quotes or equation marks, which have a special function in the wiki that sometimes depends on their position. For example, to format a word in italic, you include it in two single quotes, like this; three single quotes result in bold; five single quotes result in bold and italic:

 ''italic''
 '''bold'''
 '''''bold and italic'''''
For GeneWeb underlining style, green bold by default, use curly brackets: {text}.

To indent text, use a colon at the beginning of the line—as many as needed:

:1st indent
::2nd indent
To add a forced line-break for a new paragraph, leave an empty line or start the line with the HTML tag <br />.

Lines starting with a space are displayed as they are, provided that:

there are at least two such lines
there is an empty line before and after the group of lines.
Bullet List
To create a bullet list simply start each line with an asterisk (*):

* one
* two
* three
** three and one-third
** three and two-thirds
To maintain indentation in a multi-paragraph bullet list, appropriately mix * and : as in:

* one
* two line one

: two line two
:* two one line one
:: two one line two

* three
** three and one-third
** three and two-thirds
:: three and more
resulting in:

one
two line one
two line two
two one line one
two one line two
three
three and one-third
three and two-thirds
three and more
Internal links
You can create links to a page (text+HTML+WikiText) , by putting its name in triple square brackets, like this:

[[[Target_page]]]

If you want to display some other text for the link, you can do so by adding / (forward slash) followed by the alternative name. For example:

[[[Target_page/display text]]]

If a page doesn't exist, the link to it appears in red. Clicking on the link, you'll reach an empty page you can fill.

One can organize linked pages into folders by prefixing the filename with a folder name as in:

[[[Folder:linked_page/text]]]
One may create a link to a wizard's page with the following syntax:

[[w:Wizard]] ou [[w:Wizard/Wizard full name]]
To insert a link to an individual, use the following syntax:

[[first_name/surname/number/display text]]
For example:

[[Maria/Baxter/0/Maria Baxter]]
If the occurence and text part are missing, then "First_name Surname" is displayed.

GeneWeb maintains an index of the notes and pages where a particular individual is mentioned. This information is available on the individual's page under the link linked pages (m=LINKED;p=firstname;n=lastname). The tool update_nldb updates a cross-referenced index.

Note for GeneWeb v7
The wiki syntax for internal links is being updated to use | rather than / as delimiter between the name information and the displayed text, as in:

[[first_name/surname/number|display text]]
With this syntax, the following example

[[John/Smith/1]]
will work as expected.

This applies to the pages and wizards cases.

For backwards compatibility, the use of / is still valid.

Backlink to a page
When a page contain links to individuals, GeneWeb may add a link back to this page at several locations on the individual page:

HEAD= below the name;
OCCU= below the occupation;
DEATH= at the end of the date and place of death, between parenthesis;
BIBLIO= after sources, with a bibliography sub-title;
BNOTE= at the beginning of notes;
NOTE= at the end of notes;
The link to the page appears under the text comprised between ; and ]] in the individual's link, or under the part of the text between curly brackets ({text}), if any. In this text, the character *, if present, is replaced by the content of the tag (Warning, white space before and after the * are taken into account).

If there is no text_for_link (; alone), then the link to the page will not appear for this individual. This may be useful to keep in the page a link back to a wizard.

Page content follows the general wikitext conventions. A TITLE tag must be present, and the other tags must follow immediately.

Here are some typical usage examples of this mechanism.

TITLE=List of MIT alumni
NOTE=<li>MIT

[[John/Doe;]] Managing this page<br>
[[Nicholas/Jhonson/Johnson, Nicholas;* 1942]], engineer, writer, 1942<br>
[[Bernard/Smith/Smith, Bernard;* 1967]] CEO of Ford Motors, 1967<br>
The text "MIT year" will appear at the end of the notes section on the personal page of the persons listed in this page (except for the first one). Note the presence of the <li> tag in the NOTE header which will produce a list bullet.

TITLE=List of Missing in Action
DEATH=MIA

[[Henri/Duchmoll;]] Managing this page<br>
[[Jean/Test/Test, Jean;*]] Argonne campain 1944.<br>
[[Bernard/Dupont;*]], Sargeant, Bois Belleau battle 1917<br>
With this list, the mention (MIA) will appear after the death indications present on the individual page. The text "Argonne campaign 1944" and "Sergeant ..." is displayed when the page itself is requested.

When a person appears in several linked pages, the corresponding information appears in succession, separated by commas (,), but the overall aspect may be changed by the presence of <li> or <br> tags as shown in the MIT alumni example.

Other examples of lists managed with this mechanism can be found on the Roglo site.

 TITLE=Test2
 HEAD=baron d'Empire
 OCCU=maire de Thionville
 DEATH=raison inconnue
 BIBLIO=documentation personnelle
 BNOTE=remarque de début de note
 NOTE=remarque de fin de note

[[Henri/Gouraud;]] Responsable de cette page<br>
[[Bernard/Test/Test, Bernard;* texte_du_lien]] texte 2<br>
[[Charlotte/Test/Test, Charlotte;voir  en complément une {page} d'explications]] texte 3<br>
The example above will produce the following result on the page for Bernard Test (note that in most cases, a single tag will appear in a page):

Error creating thumbnail: File missing
Special caracters
All the characters used for syntax can be written in notes or in the forum preceded by % :

%' gives '.
%} and %{ give } and {.
%] and %[ give ] and [.
%% gives %.