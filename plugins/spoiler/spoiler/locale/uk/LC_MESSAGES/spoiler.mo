��          T      �       �      �   �  �      f     o     v  %   �  H  �       A        b
     s
  4   �
  #   �
                                        (:spoiler:) Command Add (:spoiler:) wiki command to parser.

<B>Usage:</B>
<PRE>(:spoiler:)
Text
(:spoilerend:)</PRE>

For nested spoilers use (:spoiler0:), (:spoiler1:)...(:spoiler9:) commands. 

<U>Example:</U>

<PRE>(:spoiler:)
Text
&nbsp;&nbsp;&nbsp;(:spoiler1:)
&nbsp;&nbsp;&nbsp;Nested spoiler
&nbsp;&nbsp;&nbsp;(:spoiler1end:)
(:spoilerend:)</PRE>

<B>Params:</B>
<U>inline</U> - Spoiler will be in inline mode.
<U>expandtext</U> - Link text for the collapsed spoiler. Default: "Expand".
<U>collapsetext</U> - Link text for the expanded spoiler. Default: "Collapse".

<U>Example:</U>

<PRE>(:spoiler expandtext="More..." collapsetext="Less" inline :)
Text
(:spoilerend:)</PRE>
 Collapse Expand Insert (:spoiler:) wiki command https://jenyay.net/Outwiker/SpoilerEn Project-Id-Version: outwiker
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2018-08-23 13:37+0300
Last-Translator: Jenyay <jenyay.ilin@gmail.com>
Language-Team: Ukrainian
Language: uk_UA
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=4; plural=((n%10==1 && n%100!=11) ? 0 : ((n%10 >= 2 && n%10 <=4 && (n%100 < 12 || n%100 > 14)) ? 1 : ((n%10 == 0 || (n%10 >= 5 && n%10 <=9)) || (n%100 >= 11 && n%100 <= 14)) ? 2 : 3));
X-Generator: Poedit 2.0.6
X-Crowdin-Project: outwiker
X-Crowdin-Language: uk
X-Crowdin-File: spoiler.pot
 Команда (:spoiler:) Додає вікі-команду (:spoiler:) до парсеру.

<B>Використання:</B>
<PRE>(:spoiler:)
Текст
(:spoilerend:)</PRE>

Для вкладених спойлерів можна використовувати команди (:spoiler0:), (:spoiler1:)...(:spoiler9:). 

<U>Приклад:</U>

<PRE>(:spoiler:)
Текст
&nbsp;&nbsp;&nbsp;(:spoiler1:)
&nbsp;&nbsp;&nbsp;Вкладений спойлер
&nbsp;&nbsp;&nbsp;(:spoiler1end:)
(:spoilerend:)</PRE>

<B>Параметри:</B>
<U>inline</U> - Спойлер буде розміщений в середині рядка.
<U>expandtext</U> - Текст посилання для згорнутого спойлеру. Значення за замовчуванням: "Розгорнути".
<U>collapsetext</U> - Текст посилання для розгорнутого спойлеру. Значення за замовчуванням: "Згорнути".

<U>Криклад:</U>

<PRE>(:spoiler expandtext="Більше..." collapsetext="Менше" inline :)
Текст
(:spoilerend:)</PRE>
 Згорнути Розгорнути Вставити вікі-команду (:spoiler:) https://jenyay.net/Outwiker/Spoiler 