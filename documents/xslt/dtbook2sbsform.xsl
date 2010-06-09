<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet 
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
    xmlns:louis="http://liblouis.org/liblouis"
    xmlns:brl="http://www.daisy.org/z3986/2009/braille/"
    xmlns:str="http://exslt.org/strings"
    xmlns:func="http://exslt.org/functions"
    xmlns:my="http://my-functions"
    xmlns:data="http://sbsform.ch/data"
    exclude-result-prefixes="dtb louis str data"
    extension-element-prefixes="func my">

  <xsl:output method="text" encoding="utf-8" indent="no"/>
  <xsl:strip-space elements="*"/>
  <xsl:preserve-space elements="code samp"/>
	
  <xsl:param name="contraction">0</xsl:param>
  <xsl:param name="version">0</xsl:param>
  <xsl:param name="cells_per_line">40</xsl:param>
  <xsl:param name="lines_per_page">28</xsl:param>
  <xsl:param name="hyphenation" select="false()"/>
  <xsl:param name="toc_level">0</xsl:param>
  <xsl:param name="footer_level">0</xsl:param>
  <xsl:param name="show_original_page_numbers" select="false()"/>
  <xsl:param name="show_v_forms" select="true()"/>
  <xsl:param name="downshift_ordinals" select="true()"/>
  <xsl:param name="enable_capitalization" select="false()"/>
  <xsl:param name="detailed_accented_characters">de-accents</xsl:param>
  <xsl:param name="include_macros" select="true()"/>

  <xsl:variable name="volumes">
    <xsl:value-of select=
		  "count(//brl:volume[@brl:grade=$contraction]) + 1" />
  </xsl:variable>

  <xsl:variable name="lowerCaseLetters">abcdefghijklmnopqrstuvwxyzäöüéè</xsl:variable>
  <xsl:variable name="upperCaseLetters">ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜÉÈ</xsl:variable>

  <func:function name="my:isLower">
    <xsl:param name="char"/>
    <func:result select="contains($lowerCaseLetters,$char)"/>
  </func:function>

  <func:function name="my:isUpper">
    <xsl:param name="char"/>
    <func:result select="contains($upperCaseLetters,$char)"/>
  </func:function>

  <func:function name="my:hasSameCase">
    <xsl:param name="a"/>
    <xsl:param name="b"/>
    <func:result select="(my:isLower($a) and my:isLower($b)) or (my:isUpper($a) and my:isUpper($b))"/>
  </func:function>

  <func:function name="my:tokenizeByCase">
    <xsl:param name="string"/>
    <xsl:variable name="temp">
      <xsl:for-each select="str:tokenize(string(.), '')">
	<xsl:value-of select="."/>
	<xsl:if test="not(my:hasSameCase(.,(following-sibling::*)[1]))">,</xsl:if>
      </xsl:for-each>
    </xsl:variable>
    <func:result select="str:tokenize($temp, ',')"/>
  </func:function>

  <func:function name="my:getTable">
    <xsl:param name="context" select="local-name()"/>
    <func:result>
      <xsl:call-template name="getTable">
  	<xsl:with-param name="context" select="$context"></xsl:with-param>
      </xsl:call-template>
    </func:result>
  </func:function>

  <func:function name="my:containsDot">
    <xsl:param name="string"/>
    <func:result select="contains($string,'.')"/>
  </func:function>

  <xsl:template name="getTable">
    <xsl:param name="context" select="local-name()"/>
    <xsl:choose>
      <xsl:when test="lang('fr')">
	<xsl:choose>
	  <xsl:when test="$contraction = '2'">
	    <xsl:text>Fr-Fr-g2.ctb</xsl:text>
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:text>fr-fr-g1.utb</xsl:text>
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:when>
      <xsl:when test="lang('it')">
	<xsl:text>it-it-g1.utb</xsl:text>
      </xsl:when>
      <xsl:when test="lang('en')">
	<xsl:choose>
	  <xsl:when test="$contraction = '2'">
	    <xsl:text>en-us-g2.ctb</xsl:text>
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:text>en-us-g1.ctb</xsl:text>
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:when>
      <xsl:when test="lang('de')">
	<xsl:text>sbs.dis,</xsl:text>
	<xsl:text>sbs-de-core6.cti,</xsl:text>
	<xsl:if test="$context != 'date_month' and $context != 'date_day'">
	  <xsl:choose>
	    <xsl:when test="$detailed_accented_characters = 'de-ch'">
	      <xsl:text>sbs-de-accents-ch.cti,</xsl:text>
	    </xsl:when>
	    <xsl:when test="$detailed_accented_characters = 'de-reduced'">
	      <xsl:text>sbs-de-accents-reduced.cti,</xsl:text>
	    </xsl:when>
	    <xsl:otherwise>
	      <xsl:text>sbs-de-accents.cti,</xsl:text>
	    </xsl:otherwise>
	  </xsl:choose>
	</xsl:if>
	<xsl:text>sbs-special.cti,</xsl:text>
	<xsl:text>sbs-whitespace.mod,</xsl:text>
	<xsl:if test="$context = 'v-form' or $context = 'name_capitalized' or ($contraction != '2' and $enable_capitalization = '1')">
	  <xsl:text>sbs-de-capsign.mod,</xsl:text>
	</xsl:if>
	<xsl:if test="$contraction = '2' and $context != 'date_month' and $context != 'date_day' and $context !='name_capitalized'">
	  <xsl:text>sbs-de-letsign.mod,</xsl:text>
	</xsl:if>
	<xsl:if test="$context != 'date_month'">
	  <xsl:text>sbs-numsign.mod,</xsl:text>
	</xsl:if>
	<xsl:choose>
	  <xsl:when test="$context = 'num_ordinal' or $context = 'date_day'">
	    <xsl:text>sbs-litdigit-lower.mod,</xsl:text>
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:text>sbs-litdigit-upper.mod,</xsl:text>
	  </xsl:otherwise>
	</xsl:choose>
	<xsl:if test="$context != 'date_month' and $context != 'date_day'">
	  <xsl:text>sbs-de-core.mod,</xsl:text>
	</xsl:if>
	<xsl:if test="$context = 'name_capitalized' or ($context = 'abbr' and not(my:containsDot(.))) or ($contraction = '0' and $context != 'date_day' and $context != 'date_month')">
	  <xsl:text>sbs-de-g0-core.mod,</xsl:text>
	</xsl:if>
	<xsl:if test="$contraction = '1' and ($context != 'name_capitalized' and ($context != 'abbr' or my:containsDot(.)) and $context != 'date_month' and $context != 'date_day')">
	  <xsl:text>sbs-de-g1-core.mod,</xsl:text>
	</xsl:if>
	<xsl:if test="$contraction = '2'">
	  <xsl:if test="$context = 'place'">
	    <xsl:text>sbs-de-g2-place.mod,</xsl:text>
	  </xsl:if>
	  <xsl:if test="$context = 'place' or $context = 'name'">
	    <xsl:text>sbs-de-g2-name.mod,</xsl:text>
	  </xsl:if>
	  <xsl:if test="$context != 'name' and $context != 'name_capitalized' and $context != 'place' and ($context != 'abbr' or  my:containsDot(.)) and $context != 'date_day' and $context != 'date_month'">
	    <xsl:text>sbs-de-g2-core.mod,</xsl:text>
	  </xsl:if>
	</xsl:if>
	<xsl:text>sbs-special.mod</xsl:text>
      </xsl:when>
      <xsl:otherwise>
	<xsl:text>en-us-g2.ctb</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <data:volumeNumberMapping>
    <number value="1">eins</number>
    <number value="2">zwei</number>
    <number value="3">drei</number>
    <number value="4">vier</number>
    <number value="5">fünf</number>
    <number value="6">sechs</number>
    <number value="7">sieben</number>
    <number value="8">acht</number>
    <number value="9">neun</number>
    <number value="10">zehn</number>
    <number value="11">elf</number>
    <number value="12">zwölf</number>
  </data:volumeNumberMapping>

  <xsl:template name="sbsform-macro-definitions">
    <xsl:text>
x ======================= ANFANG SBSFORM.MAK =========================
x Bei Aenderungen den ganzen Block in separate Makrodatei auslagern.
</xsl:text>

    <xsl:text>
xxxxxxxxxxxxxxxxxxxxxxxxxx book, body, rear xxxxxxxxxxxxxxxxxxxxxxxxxx

y b BOOKb ; Anfang des Buches: Globale Einstellungen
z
i b=</xsl:text><xsl:value-of select="$cells_per_line"/>
<xsl:text>
i s=</xsl:text><xsl:value-of select="$lines_per_page"/>
<xsl:if test="$footer_level &gt; 0">
  <xsl:text>
I ~=j
i k=0
</xsl:text>
</xsl:if>
<xsl:text>
y e BOOKb

y b BOOKe ; Ende des Buches, evtl. Inhaltsverzeichnis
y EndBook
</xsl:text>
<xsl:if test="$toc_level &gt; 0">
  <xsl:text>y Inhaltsv
</xsl:text>
</xsl:if>
<xsl:text>
y e BOOKe

y b BODYb ; Bodymatter
R=X
Y
</xsl:text>
<xsl:if test="$show_original_page_numbers = '1'">
  <xsl:text>RX
  </xsl:text>
</xsl:if>
<xsl:text>
y e BODYb
y b BODYe
y e BODYe
</xsl:text>

<xsl:if test="//dtb:rearmatter">
  <xsl:text>y b REARb ; Rearmatter
z
  </xsl:text>
  <xsl:if test="$toc_level &gt; 0">
    <xsl:text>H`lm1
</xsl:text>
  </xsl:if>
  <xsl:text>y e REARb
y b REARe
y e REARe
  </xsl:text>
</xsl:if>

<xsl:text>
xxxxxxxxxxxxxxxxxxxxxxxx Levels und Headings xxxxxxxxxxxxxxxxxxxxxxxxx
y b LEVEL1b
p
Y
y e LEVEL1b
y b LEVEL1e
y e LEVEL1e
y b H1
L
i f=3 l=1
t
Y
u-
</xsl:text>
<xsl:if test="$toc_level &gt; 0">
<xsl:text>H`B+
H`i F=1
Y
H`B-
</xsl:text>
</xsl:if>
<xsl:if test="$footer_level &gt; 0">
  <xsl:text>Y
</xsl:text>
</xsl:if>
<xsl:text>lm1
y e H1
</xsl:text>

<xsl:if test="//dtb:level2">
<xsl:text>
y b LEVEL2b
lm2
n10
Y
y e LEVEL2b
y b LEVEL2e
y e LEVEL2e
y b H2
lm2
i f=3 l=1
w
Y
u
</xsl:text>
  <xsl:if test="$toc_level &gt; 1">
<xsl:text>H`B+
H`i F=3
Y
H`B-
</xsl:text>
  </xsl:if>
<xsl:if test="$footer_level &gt; 1">
  <xsl:text>Y
</xsl:text>
</xsl:if>
<xsl:text>lm1
y e H2
</xsl:text>
</xsl:if>

<xsl:if test="//dtb:level3">
<xsl:text>
y b LEVEL3b
lm1
n6
Y
y e LEVEL3b
y b LEVEL3e
y e LEVEL3e
y b H3
lm1
i f=3 l=1
w
Y
u,
</xsl:text>
  <xsl:if test="$toc_level &gt; 2">
<xsl:text>H`B+
H`i F=5
Y
H`B-
</xsl:text>
  </xsl:if>
  <xsl:if test="$footer_level &gt; 2">
  <xsl:text>Y
</xsl:text>
  </xsl:if>
<xsl:text>y e H3
</xsl:text>
</xsl:if>

<xsl:if test="//dtb:level4">
<xsl:text>
y b LEVEL4b
lm1
Y
y e LEVEL4b
y b LEVEL4e
y e LEVEL4e
y b H4
lm1
Y
</xsl:text>
  <xsl:if test="$toc_level &gt; 3">
<xsl:text>H`B+
H`i F=7
Y
H`B-
</xsl:text>
  </xsl:if>
  <xsl:if test="$footer_level &gt; 3">
  <xsl:text>Y
</xsl:text>
  </xsl:if>
  <xsl:text>y e H4
</xsl:text>
</xsl:if>

<xsl:if test="//dtb:level5">
  <xsl:text>
y b LEVEL5b
lm1
Y
y e LEVEL5b
y b LEVEL5e
y e LEVEL5e
y b H5
lm1
Y
</xsl:text>
  <xsl:if test="$toc_level &gt; 4">
<xsl:text>H`B+
H`i F=9
Y
H`B-
</xsl:text>
  </xsl:if>
  <xsl:if test="$footer_level &gt; 4">
  <xsl:text>Y
</xsl:text>
  </xsl:if>
  <xsl:text>y e H5
</xsl:text>
</xsl:if>

<xsl:if test="//dtb:level6">
  <xsl:text>
y b LEVEL6b
lm1
Y
y e LEVEL6b
y b LEVEL6e
y e LEVEL6e
y b H6
lm1
Y
</xsl:text>
  <xsl:if test="$toc_level &gt; 5">
<xsl:text>H`B+
H`i F=11
Y
H`B-
</xsl:text>
  </xsl:if>
  <xsl:if test="$footer_level &gt; 5">
  <xsl:text>Y
</xsl:text>
  </xsl:if>
  <xsl:text>y e H6
</xsl:text>
</xsl:if>

<xsl:if test="//dtb:p">
  <xsl:text>
xxxxxxxxxxxxxxxxxxxx Absatz, Leerzeile, Separator xxxxxxxxxxxxxxxxxxxx
y b P
i f=3 l=1
y e P
</xsl:text>
</xsl:if>
<xsl:if test="//dtb:p[@class='precedingemptyline']">
<xsl:text>y b BLANK
lm1
n2
y e BLANK
</xsl:text>
</xsl:if>
<xsl:if test="//dtb:p[@class='precedingseparator']">
<xsl:text>y b SEPARATOR
lm1
t::::::
lm1
y e SEPARATOR
</xsl:text>
</xsl:if>

<xsl:if test="//dtb:author">
<xsl:text>y b AUTHOR
r
y e AUTHOR
</xsl:text>
</xsl:if>

<xsl:if test="//dtb:byline">
<xsl:text>y b BYLINE
r
y e BYLINE
</xsl:text>
</xsl:if>

<xsl:if test="//dtb:blockquote">
<xsl:text>
xxxxxxxxxxxxxxxxxxxxxxxxxxxxx Blockquote xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
y b BLQUOb
lm1
n2
i A=3
y e BLQUOb
y b BLQUOe
i A=1
lm1
n2
y e BLQUOe
</xsl:text>
</xsl:if>

<xsl:if test="//dtb:poem">
<xsl:text>
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Poem xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
y b POEMb
lm1
n2
i A=3
y e POEMb
y b POEMe
i A=1
lm1
n2
y e POEMe

y b LINEb
i f=1 l=3
B+
y e LINEb
y b LINEe
B-
y e LINEe
</xsl:text>
</xsl:if>

<xsl:if test="//dtb:linegroup">
<xsl:text>
y b LINEGROUPb
lm1
n2
y e LINEGROUPb
y b LINEGROUPe
y e LINEGROUPe
</xsl:text>
</xsl:if>

<xsl:if test="//dtb:list">
<xsl:text>
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Listen xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

y b PLISTb ; Vorformatierte Liste
lm1
i f=1 l=3
n2
y e PLISTb
y b PLISTe
i f=3 l=1
lm1
n2
y e PLISTe
</xsl:text>
<xsl:text>y b LI
a
y e LI
</xsl:text>
</xsl:if>

<xsl:text>
xxxxxxxxxxxxxxxxxxxxxxxxxxx Bandeinteilung xxxxxxxxxxxxxxxxxxxxxxxxxxx
y b BrlVol
?vol:vol+1
y Titlepage
y e BrlVol
</xsl:text>

<xsl:if test="//brl:volume">
<xsl:text>y b EndVol
B+
L
tCCCCCCCCCCCC
t
</xsl:text>
<xsl:value-of select='louis:translate("Ende des",string(my:getTable()))'/>
<xsl:choose>
  <xsl:when test="$volumes &gt; 12">
<xsl:text>" %B
</xsl:text>
  </xsl:when>
  <xsl:otherwise>
    <xsl:choose>
      <xsl:when test="$contraction='2'">
<xsl:text>" %BC
</xsl:text>
      </xsl:when>
      <xsl:otherwise>
<xsl:text>" %BEN
</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:otherwise>
</xsl:choose>
<xsl:value-of select='louis:translate("Bandes",string(my:getTable()))'/>
<xsl:text>B-
y e EndVol
</xsl:text>
</xsl:if>

<xsl:text>
xxxxxxxxxxxxxxxxxxxxxxxxxxxx Hilfsmakros xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
</xsl:text>
<xsl:if test="$toc_level &gt; 0">
<xsl:text>y b Inhaltsv
E
P1
~~
I ~=j
L
t~
</xsl:text>
<xsl:value-of select='louis:translate("Inhaltsverzeichnis",string(my:getTable()))'/>
<xsl:text>
u-
lm1
y e Inhaltsv
</xsl:text>
</xsl:if>

<xsl:text>y b EndBook
lm1
B+
L
tCCCCCCCCCCCC
t
</xsl:text>
<xsl:value-of select='louis:translate("Ende des Buches",string(my:getTable()))'/>
<xsl:text>
t======
B-
y e EndBook
</xsl:text>

<xsl:if test="$volumes &gt; 1">
  <xsl:text>y b Volumes
lv16
t
  </xsl:text>
  <xsl:value-of select='louis:translate("In",string(my:getTable()))'/>
  <xsl:choose>
    <xsl:when test="$volumes &lt; 13">
      <xsl:variable name="number" select="document('')/*/data:volumeNumberMapping[@value=$volumes]"/>
      <xsl:value-of select='louis:translate($number,string(my:getTable()))'/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select='louis:translate($volumes,string(my:getTable()))'/>
    </xsl:otherwise>
  </xsl:choose>
  <xsl:value-of select='louis:translate("Braille-Bänden",string(my:getTable()))'/>
  <xsl:text>t
</xsl:text>
  <xsl:choose>
    <xsl:when test="$volumes &lt; 13">
      <!-- bis zu zwölf Bänden in Worten -->
      <xsl:text>?vol=1
+R=B</xsl:text>
      <xsl:value-of select='louis:translate("erst",string(my:getTable()))'/>
      <xsl:text>
?vol=2
+R=B</xsl:text>
      <xsl:value-of select='louis:translate("zweit",string(my:getTable()))'/>
      <xsl:if test="$volumes &gt; 2">
	<xsl:text>
?vol=3
+R=B</xsl:text>
	<xsl:value-of select='louis:translate("dritt",string(my:getTable()))'/>
      </xsl:if>
      <xsl:if test="$volumes &gt; 3">
	<xsl:text>
?vol=4
+R=B</xsl:text>
	<xsl:value-of select='louis:translate("viert",string(my:getTable()))'/>
      </xsl:if>
      <xsl:if test="$volumes &gt; 4">
	<xsl:text>
?vol=5
+R=B</xsl:text>
	<xsl:value-of select='louis:translate("fünft",string(my:getTable()))'/>
      </xsl:if>
      <xsl:if test="$volumes &gt; 5">
	<xsl:text>
?vol=6
+R=B</xsl:text>
	<xsl:value-of select='louis:translate("sechst",string(my:getTable()))'/>
      </xsl:if>
      <xsl:if test="$volumes &gt; 6">
	<xsl:text>
?vol=7
+R=B</xsl:text>
	<xsl:value-of select='louis:translate("siebt",string(my:getTable()))'/>
      </xsl:if>
      <xsl:if test="$volumes &gt; 7">
	<xsl:text>
?vol=8
+R=B</xsl:text>
	<xsl:value-of select='louis:translate("acht",string(my:getTable()))'/>
      </xsl:if>
      <xsl:if test="$volumes &gt; 8">
	<xsl:text>
?vol=9
+R=B</xsl:text>
	<xsl:value-of select='louis:translate("neunt",string(my:getTable()))'/>
      </xsl:if>
      <xsl:if test="$volumes &gt; 9">
	<xsl:text>
?vol=10
+R=B</xsl:text>
	<xsl:value-of select='louis:translate("zehnt",string(my:getTable()))'/>
      </xsl:if>
      <xsl:if test="$volumes &gt; 10">
	<xsl:text>
?vol=11
+R=B</xsl:text>
	<xsl:value-of select='louis:translate("elft",string(my:getTable()))'/>
      </xsl:if>
      <xsl:if test="$volumes &gt; 11">
	<xsl:text>
?vol=12
+R=B</xsl:text>
	<xsl:value-of select='louis:translate("zwölft",string(my:getTable()))'/>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="$contraction='2'">
	  <xsl:text>
" %B7
</xsl:text>
        </xsl:when>
        <xsl:otherwise>
	  <xsl:text>
" %BER
</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:otherwise>
      <!-- Vereinfachen mit translate() -->
      <xsl:text>?vol=1
+R=B#,
?vol=2
+R=B#;
</xsl:text>
      <xsl:if test="$volumes &gt; 2">
	<xsl:text>?vol=3
+R=B#:
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 3">
	<xsl:text>?vol=4
+R=B#/
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 4">
	<xsl:text>?vol=5
+R=B#?
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 5">
	<xsl:text>?vol=6
+R=B#+
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 6">
	<xsl:text>?vol=7
+R=B#=
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 7">
	<xsl:text>?vol=8
+R=B#(
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 8">
	<xsl:text>?vol=9
+R=B#*
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 9">
	<xsl:text>?vol=10
+R=B#,)
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 10">
	<xsl:text>?vol=11
+R=B#,,
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 11">
	<xsl:text>?vol=12
+R=B#,;
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 12">
	<xsl:text>?vol=13
+R=B#,:
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 13">
	<xsl:text>?vol=14
+R=B#,/
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 14">
	<xsl:text>?vol=15
+R=B#,?
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 15">
	<xsl:text>?vol=16
+R=B#,+
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 16">
	<xsl:text>?vol=17
+R=B#,=
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 17">
	<xsl:text>?vol=18
+R=B#,(
</xsl:text>
      </xsl:if>
      <xsl:if test="$volumes &gt; 18">
	<xsl:text>?vol=19
+R=B#,*
</xsl:text>
      </xsl:if>
      <xsl:text>" %B
      </xsl:text>
    </xsl:otherwise>
  </xsl:choose>
  <xsl:value-of select='louis:translate("Band",string(my:getTable()))'/>
  <xsl:text>y e Volumes
  </xsl:text>
</xsl:if>
<xsl:text>
xxxxxxxxxxxxxxxxxxxxxxxxxxxx Titelblatt xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
y b Titlepage
O
bb
L5
t
</xsl:text>
<xsl:apply-templates select="//dtb:docauthor/text()"/>
<xsl:text>
l2
t
</xsl:text>
<xsl:apply-templates select="//dtb:doctitle/text()"/>
<xsl:text>
u-
</xsl:text>
<xsl:if test="//brl:volume">
<xsl:text>y Volumes
</xsl:text>
</xsl:if>
<xsl:choose>
  <xsl:when test="$contraction='2'">
<xsl:text>lv23
</xsl:text>
  </xsl:when>
  <xsl:otherwise>
<xsl:text>lv22
</xsl:text>
  </xsl:otherwise>
</xsl:choose>
<xsl:text>t
</xsl:text>
<xsl:value-of select='louis:translate("Schweizerische Bibliothek",string(my:getTable()))'/>
<xsl:text>
t
</xsl:text>
<xsl:value-of select='louis:translate("für Blinde, Seh- und",string(my:getTable()))'/>
<xsl:if test="not($contraction='2')">
<xsl:text>
t
</xsl:text>
</xsl:if>
<xsl:value-of select='louis:translate("Lesebehinderte",string(my:getTable()))'/>
<xsl:text>
l
t
</xsl:text>
<xsl:value-of select='louis:translate("SBS",string(my:getTable("abbr")))'/>
<xsl:value-of select="louis:translate(string(substring-before(//dtb:meta[@name='dc:Date']/@content,'-')),string(my:getTable()))"/>
<xsl:text>
p
L
i f=1 l=1
</xsl:text>
<xsl:value-of select='louis:translate("Dieses Punktschrift-Buch ist die ausschließlich",string(my:getTable()))'/>
<xsl:value-of select='louis:translate("für die Nutzung durch Lesebehinderte Menschen",string(my:getTable()))'/>
<xsl:value-of select='louis:translate("bestimmte zugängliche Version eines urheberrechtlich",string(my:getTable()))'/>
<xsl:value-of select='louis:translate("geschützten Werks. ",string(my:getTable()))'/>
<xsl:value-of select='louis:translate("Sie",string(my:getTable("v-form")))'/>
<xsl:value-of select='louis:translate("können",string(my:getTable()))'/>
<xsl:value-of select='louis:translate("es im Rahmen des Urheberrechts persönlich nutzen",string(my:getTable()))'/>
<xsl:value-of select='louis:translate("dürfen es aber nicht weiter verbreiten oder öffentlich",string(my:getTable()))'/>
<xsl:value-of select='louis:translate("zugänglich machen",string(my:getTable()))'/>
<xsl:choose>
  <xsl:when test="$contraction='2'">
<xsl:text>
lv21
</xsl:text>
  </xsl:when>
  <xsl:otherwise>
<xsl:text>
lv20
</xsl:text>
  </xsl:otherwise>
</xsl:choose>
<xsl:value-of select='louis:translate("Verlag, Satz und Druck",string(my:getTable()))'/>
<xsl:text>
a
</xsl:text>
<xsl:value-of select='louis:translate("Schweizerische Bibliothek",string(my:getTable()))'/>
<xsl:text>
a
</xsl:text>
<xsl:value-of select='louis:translate("für Blinde, Seh- und",string(my:getTable()))'/>
<xsl:if test="not($contraction='2')">
<xsl:text>
a
</xsl:text>
</xsl:if>
<xsl:value-of select='louis:translate("Lesebehinderte",string(my:getTable()))'/>
<xsl:text>
a
</xsl:text>
<xsl:value-of select='louis:translate("SBS",string(my:getTable("abbr")))'/>
<xsl:value-of select="louis:translate(string(substring-before(//dtb:meta[@name='dc:Date']/@content,'-')),string(my:getTable()))"/>
<xsl:text>
l
</xsl:text>
<xsl:value-of select='louis:translate("www.sbs-online.ch",string(my:getTable()))'/>
<xsl:text>
p
L5
</xsl:text>
<xsl:apply-templates select="//dtb:docauthor/text()"/>
<xsl:text>
l2
</xsl:text>
<xsl:apply-templates select="//dtb:doctitle/text()"/>
<xsl:text>
u-
l
</xsl:text>
<xsl:apply-templates select="//dtb:frontmatter/dtb:level1[@class='titlepage']" mode='titlepage'/>
<xsl:text>
b
O
y e Titlepage
</xsl:text>
<xsl:text>
y BrlVol
xxxxxxxxxxxxxxxxxxxxxxxxxx Klappentext etc. xxxxxxxxxxxxxxxxxxxxxxxxxx
O
</xsl:text>
<xsl:apply-templates select="//dtb:frontmatter/dtb:level1[not(@class) or (@class!='titlepage' and @class!='toc')]"/>
<xsl:text>O
xxx ====================== ENDE SBSFORM.MAK ====================== xxx
</xsl:text>
<xsl:text>
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Buchinhalt xxxxxxxxxxxxxxxxxxxxxxxxxxxx
</xsl:text>

</xsl:template>

  <xsl:template match="/">
    <xsl:text>x </xsl:text><xsl:value-of select="//dtb:docauthor"/>
    <xsl:text>: </xsl:text><xsl:value-of select="//dtb:doctitle"/><xsl:text>
</xsl:text>
    <xsl:text>x Daisy Producer Version: </xsl:text>
    <xsl:value-of select="$version"/><xsl:text>
</xsl:text>
    <xsl:text>x contraction:</xsl:text>
    <xsl:value-of select="$contraction"/><xsl:text>
</xsl:text>
    <xsl:text>x cells_per_line:</xsl:text>
    <xsl:value-of select="$cells_per_line"/><xsl:text>
</xsl:text>
    <xsl:text>x lines_per_page:</xsl:text>
    <xsl:value-of select="$lines_per_page"/><xsl:text>
</xsl:text>
    <xsl:text>x hyphenation:</xsl:text>
    <xsl:value-of select="$hyphenation"/><xsl:text>
</xsl:text>
    <xsl:text>x toc_level:</xsl:text>
    <xsl:value-of select="$toc_level"/><xsl:text>
</xsl:text>
    <xsl:text>x show_original_page_numbers:</xsl:text>
    <xsl:value-of select="$show_original_page_numbers"/><xsl:text>
</xsl:text>
    <xsl:text>x show_v_forms:</xsl:text>
    <xsl:value-of select="$show_v_forms"/><xsl:text>
</xsl:text>
    <xsl:text>x downshift_ordinals:</xsl:text>
    <xsl:value-of select="$downshift_ordinals"/><xsl:text>
</xsl:text>
    <xsl:text>x enable_capitalization:</xsl:text>
    <xsl:value-of select="$enable_capitalization"/><xsl:text>
</xsl:text>
    <xsl:text>x detailed_accented_characters:</xsl:text>
    <xsl:value-of select="$detailed_accented_characters"/><xsl:text>
</xsl:text>
    <xsl:text>x include_macros:</xsl:text>
    <xsl:value-of select="$include_macros"/><xsl:text>
</xsl:text>
  <xsl:text>x ---------------------------------------------------------------------------
</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="dtb:dtbook">
    <xsl:choose>
      <xsl:when test="$include_macros = '1'">
	<xsl:call-template name="sbsform-macro-definitions"/>
      </xsl:when>
      <xsl:otherwise>
	<xsl:text>
U dtbook.mak
</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="dtb:head">
    <!-- ignore -->
  </xsl:template>
  
  <xsl:template match="dtb:meta">
    <!-- ignore -->
  </xsl:template>
  
  <xsl:template match="dtb:book">
    <xsl:text>y BOOKb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y BOOKe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:frontmatter">
  </xsl:template>

  <xsl:template match="dtb:bodymatter">
    <xsl:text>y BODYb
i j=</xsl:text>
    <!-- value of first pagenum within body -->
    <xsl:value-of select="descendant::dtb:pagenum[1]/text()"/>
    <xsl:text>
</xsl:text>

    <xsl:apply-templates/>
    <xsl:text>y BODYe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:doctitle">
    <!-- ignore -->
  </xsl:template>

  <xsl:template match="dtb:docauthor">
    <!-- ignore -->
  </xsl:template>

  <xsl:template match="dtb:level1">
    <xsl:text>y LEVEL1b
</xsl:text>
    <!-- add a comment if the first child is not a pagenum -->
      <xsl:if test="not(name(child::*[1])='pagenum')">
	<xsl:text>.xNOPAGENUM
</xsl:text>
      </xsl:if>
    <xsl:apply-templates/>
    <xsl:text>
y LEVEL1e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:level2">
    <xsl:text>y LEVEL2b
</xsl:text>
    <!-- add a comment if the first child is not a pagenum -->
      <xsl:if test="not(name(child::*[1])='pagenum')">
	<xsl:text>.xNOPAGENUM
</xsl:text>
      </xsl:if>
    <xsl:apply-templates/>
    <xsl:text>
y LEVEL2e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:level3">
    <xsl:text>y LEVEL3b
</xsl:text>
    <!-- add a comment if the first child is not a pagenum -->
      <xsl:if test="not(name(child::*[1])='pagenum')">
	<xsl:text>.xNOPAGENUM
</xsl:text>
      </xsl:if>
    <xsl:apply-templates/>
    <xsl:text>
y LEVEL3e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:level4">
    <xsl:text>y LEVEL4b
</xsl:text>
    <!-- add a comment if the first child is not a pagenum -->
      <xsl:if test="not(name(child::*[1])='pagenum')">
	<xsl:text>.xNOPAGENUM
</xsl:text>
      </xsl:if>
    <xsl:apply-templates/>
    <xsl:text>
y LEVEL4e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:level5">
    <xsl:text>y LEVEL5b
</xsl:text>
    <!-- add a comment if the first child is not a pagenum -->
      <xsl:if test="not(name(child::*[1])='pagenum')">
	<xsl:text>.xNOPAGENUM
</xsl:text>
      </xsl:if>
    <xsl:apply-templates/>
    <xsl:text>
y LEVEL5e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:level6">
    <xsl:text>y LEVEL6b
</xsl:text>
    <!-- add a comment if the first child is not a pagenum -->
      <xsl:if test="not(name(child::*[1])='pagenum')">
	<xsl:text>.xNOPAGENUM
</xsl:text>
      </xsl:if>
    <xsl:apply-templates/>
    <xsl:text>
y LEVEL6e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:p[@class='precedingseparator']">   
    <xsl:text>y SEPARATOR
y P
</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="dtb:p[@class='precedingemptyline']">   
    <xsl:text>y BLANK
y P
</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="dtb:p" mode='titlepage'>   
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="dtb:p">   
    <xsl:text>
y P
</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="dtb:list">
    <xsl:text>y PLISTb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
y PLISTe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:li">
    <xsl:text>y LI
</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="dtb:pagenum">
    <!-- add a line feed if we're inside a p -->
    <xsl:if test="name(..) = 'p'">
      <xsl:text>
</xsl:text>
    </xsl:if>
    <xsl:text>j </xsl:text>
    <xsl:value-of select="text()"/>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:h1|dtb:h2|dtb:h3|dtb:h4|dtb:h5|dtb:h6">
    <xsl:variable name="level" select="substring(local-name(), 2)"/>
    <xsl:text>y H</xsl:text><xsl:value-of select="$level"/><xsl:text>
</xsl:text>
    <xsl:apply-templates select="*[local-name() != 'toc-line' and local-name() != 'running-line']"/>
    <xsl:if test="$toc_level &gt;= $level">
      <xsl:text>
H</xsl:text>
      <xsl:choose>
	<xsl:when test="brl:toc-line">
	  <xsl:apply-templates select="brl:toc-line"/>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:apply-templates select="*[local-name() != 'toc-line' and local-name() != 'running-line']"/>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <xsl:if test="$footer_level &gt;= $level">
      <xsl:text>
~</xsl:text>
      <xsl:choose>
	<xsl:when test="brl:running-line[not(@brl:grade) or @brl:grade = $contraction]">
	  <xsl:apply-templates select="brl:running-line[not(@brl:grade)]|brl:running-line[@brl:grade = $contraction]"/>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:apply-templates select="*[local-name() != 'toc-line' and local-name() != 'running-line']"/>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:blockquote">
    <xsl:text>
y BLQUOb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
y BLQUOe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:poem">
    <xsl:text>y POEMb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y POEMe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:author">
    <xsl:text>y AUTHOR
</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="dtb:byline">
    <xsl:text>y BYLINE
</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="dtb:linegroup">
    <xsl:text>y LINEGROUPb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y LINEGROUPe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:line">
    <xsl:text>y LINEb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y LINEe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:br">
    <!-- ignore for now -->
  </xsl:template>
  
  <xsl:template match="dtb:rearmatter">
    <xsl:text>y REARb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y REARe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:strong[lang('de')]|dtb:em[lang('de')]">
    <!-- FIXME: This is a workaround for a liblouis bug that doesn't
         correctly announce multi-word emphasis. We do it manually
         here by counting the words -->
    <xsl:choose>
     <xsl:when test="count(str:tokenize(string(.), ' /-')) > 1">
       <xsl:apply-templates mode="italic"/>
     </xsl:when>
     <xsl:otherwise>
       <xsl:apply-templates mode="bold"/>
     </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="dtb:em">
    <xsl:apply-templates mode="italic"/>
  </xsl:template>

  <xsl:template match="dtb:strong">
    <xsl:apply-templates mode="bold"/>
  </xsl:template>

  <xsl:template match="dtb:abbr[lang('de')]">
    <xsl:choose>
      <xsl:when test="my:containsDot(.)">
	<xsl:variable name="temp">
	  <!-- drop all the spaces -->
	  <xsl:for-each select="str:tokenize(string(.), ' ')">
	    <xsl:value-of select="." />
	  </xsl:for-each>
	</xsl:variable>
	<xsl:value-of select="louis:translate(string($temp),string(my:getTable()))"/>
      </xsl:when>
      <xsl:otherwise>
	<xsl:variable name="temp">
	  <xsl:for-each select="my:tokenizeByCase(.)">
	    <!-- prepend more upper case sequences longer than one char with > -->
	    <xsl:if test="(string-length(.) &gt; 1 or position()=last()) and my:isUpper(substring(.,1,1))"><xsl:text>╦</xsl:text></xsl:if>
	    <!-- prepend single char upper case with $ (unless it is the last char then prepend with >) -->
	    <xsl:if test="string-length(.) = 1 and my:isUpper(substring(.,1,1)) and not(position()=last())"><xsl:text>╤</xsl:text></xsl:if>
	    <!-- prepend the first char with ' if it is lower case -->
	    <xsl:if test="position()=1 and my:isLower(substring(.,1,1))"><xsl:text>╩</xsl:text></xsl:if>
	    <!-- prepend any lower case sequences that follow an upper case sequence with ' -->
	    <xsl:if test="my:isLower(substring(.,1,1)) and string-length((preceding-sibling::*)[1]) &gt; 1 and my:isUpper(substring((preceding-sibling::*)[1],1,1))"><xsl:text>╩</xsl:text></xsl:if>
	    <xsl:value-of select="."/>
	  </xsl:for-each>
	</xsl:variable>
	<xsl:value-of select="louis:translate(string($temp),string(my:getTable()))"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template match="dtb:abbr">
    <xsl:apply-templates />
  </xsl:template>
  
  <xsl:template match="dtb:acronym">
  </xsl:template>

  <!-- Contraction hints -->

  <xsl:template match="brl:num[@role='ordinal' and lang('de')]">
    <xsl:choose>
      <xsl:when test="$downshift_ordinals = '1'">
	<xsl:value-of select="louis:translate(string(translate(.,'.','')),string(my:getTable('num_ordinal')))"/>
      </xsl:when>
      <xsl:otherwise>
	<xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="brl:num[@role='roman' and lang('de')]">
    <xsl:value-of select="louis:translate(string(),string(my:getTable('abbr')))"/>
  </xsl:template>

  <xsl:template match="brl:num[@role='phone' and lang('de')]">
    <!-- Replace ' ' and '/' with '.' -->
    <xsl:for-each select="str:tokenize(string(.), ' /')">
      <xsl:value-of select="louis:translate(string(.),string(my:getTable()))" />
      <xsl:if test="not(position() = last())">.</xsl:if>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="brl:num[@role='measure' and lang('de')]">
    <!-- For all number-unit combinations, e.g. 1 kg, 10 km, etc. drop the space -->
    <xsl:for-each select="str:tokenize(string(.), ' ')">
      <xsl:choose>
	<xsl:when test="not(position() = last())">
	  <!-- FIXME: do not test for position but whether it is a number -->
	  <xsl:value-of select="louis:translate(string(.),string(my:getTable()))"/>
	</xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="louis:translate(string(.),string(my:getTable('abbr')))"/>
      </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="brl:num[@role='isbn' and lang('de')]">
    <xsl:variable name="lastChar" select="substring(.,string-length(.),1)"/>
    <xsl:variable name="secondToLastChar" select="substring(.,string-length(.)-1,1)"/>
    <xsl:choose>
      <!-- If the isbn number ends in a capital letter then keep the
           dash, mark the letter with &#x2566; and translate the
           letter with abbr -->
      <xsl:when test="$secondToLastChar='-' and string(number($lastChar))='NaN' and contains($upperCaseLetters, $lastChar)">
	<xsl:for-each select="str:tokenize(substring(.,1,string-length(.)-2), ' -')">
	  <xsl:value-of select="louis:translate(string(.),string(my:getTable()))" />
	  <xsl:if test="not(position() = last())">.</xsl:if>
	</xsl:for-each>
	<xsl:value-of select="louis:translate($secondToLastChar,string(my:getTable()))"/>
	<xsl:value-of select="louis:translate(concat('&#x2566;',$lastChar),string(my:getTable('abbr')))"/>
      </xsl:when>
      <xsl:otherwise>
	<xsl:for-each select="str:tokenize(string(.), ' -')">
	  <xsl:value-of select="louis:translate(string(.),string(my:getTable()))" />
	  <xsl:if test="not(position() = last())">.</xsl:if>
	</xsl:for-each>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="brl:name[lang('de')]">
    <xsl:value-of select="louis:translate(string(),string(my:getTable()))"/>
  </xsl:template>

  <xsl:template match="brl:place[lang('de')]">
    <xsl:value-of select="louis:translate(string(),string(my:getTable()))"/>
  </xsl:template>

  <xsl:template match="brl:v-form[lang('de')]">
    <xsl:choose>
      <xsl:when test="$show_v_forms = '1'">
  	<xsl:value-of select="louis:translate(string(),string(my:getTable()))"/>
      </xsl:when>
      <xsl:otherwise>
  	<xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="brl:separator">
    <!-- ignore -->
  </xsl:template>

  <xsl:template match="brl:date[lang('de')]">
    <xsl:for-each select="str:tokenize(string(@value), '-')">
      <xsl:choose>
	<xsl:when test="position() = last()-1">
	  <xsl:value-of select="louis:translate(string(),string(my:getTable('date_month')))"/>
	</xsl:when>
	<xsl:when test="position() = last()">
	  <xsl:value-of select="louis:translate(string(),string(my:getTable('date_day')))"/>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:value-of select="louis:translate(string(),string(my:getTable()))"/>
	</xsl:otherwise>	
      </xsl:choose>
      <xsl:if test="not(position() = last())">.</xsl:if>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="brl:time[lang('de')]">
    <xsl:variable name="time">
      <xsl:for-each select="str:tokenize(string(@value), ':')">
	<xsl:value-of select="format-number(.,'#')"/>
	<xsl:if test="not(position() = last())">.</xsl:if>
      </xsl:for-each>
    </xsl:variable>
    <xsl:value-of select="louis:translate(string($time),string(my:getTable()))" />
  </xsl:template>

  <!-- Text nodes are translated with liblouis -->

  <xsl:template match="text()">
    <xsl:value-of select='louis:translate(string(),string(my:getTable()))'/>
  </xsl:template>
  
  <xsl:template match="text()" mode="italic">
    <xsl:value-of select='louis:translate(string(),string(my:getTable()),"italic")'/>
  </xsl:template>
  
  <xsl:template match="text()" mode="bold">
    <xsl:value-of select='louis:translate(string(),string(my:getTable()),"bold")'/>
  </xsl:template>
  
  <xsl:template match="dtb:*">
    <xsl:message>
      *****<xsl:value-of select="name(..)"/>/{<xsl:value-of select="namespace-uri()"/>}<xsl:value-of select="name()"/>******
    </xsl:message>
  </xsl:template>
  
</xsl:stylesheet>
