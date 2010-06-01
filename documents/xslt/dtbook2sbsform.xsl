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
    exclude-result-prefixes="dtb louis str"
    extension-element-prefixes=" func my">

  <xsl:output method="text" encoding="utf-8" indent="no"/>
  <xsl:strip-space elements="*"/>
  <xsl:preserve-space elements="code samp"/>
	
  <xsl:param name="contraction">0</xsl:param>
  <xsl:param name="version">0</xsl:param>
  <xsl:param name="cells_per_line">40</xsl:param>
  <xsl:param name="lines_per_page">28</xsl:param>
  <xsl:param name="hyphenation" select="false()"/>
  <xsl:param name="generate_toc" select="false()"/>
  <xsl:param name="show_original_page_numbers" select="false()"/>
  <xsl:param name="show_v_forms" select="true()"/>
  <xsl:param name="downshift_ordinals" select="true()"/>
  <xsl:param name="enable_capitalization" select="false()"/>
  <xsl:param name="detailed_accented_characters">de-accents</xsl:param>

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
	<xsl:if test="$context = 'v-form' or $context = 'name_capitalized' or ($contraction != '2' and $enable_capitalization and ($context = 'name' or $context = 'place' or $context = 'num_ordinal'))">
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

  <xsl:template match="/">
    <xsl:text>x </xsl:text><xsl:value-of select="//dtb:docauthor"/>
    <xsl:text>: </xsl:text><xsl:value-of select="//dtb:doctitle"/><xsl:text>
</xsl:text>
    <xsl:text>x Daisy Producer Version: </xsl:text>
    <xsl:value-of select="$version"/><xsl:text>
</xsl:text>
    <xsl:text>?contraction:</xsl:text>
    <xsl:value-of select="$contraction"/><xsl:text>
</xsl:text>
    <xsl:text>?cells_per_line:</xsl:text>
    <xsl:value-of select="$cells_per_line"/><xsl:text>
</xsl:text>
    <xsl:text>?lines_per_page:</xsl:text>
    <xsl:value-of select="$lines_per_page"/><xsl:text>
</xsl:text>
    <xsl:text>?hyphenation:</xsl:text>
    <xsl:value-of select="$hyphenation"/><xsl:text>
</xsl:text>
    <xsl:text>?generate_toc:</xsl:text>
    <xsl:value-of select="$generate_toc"/><xsl:text>
</xsl:text>
    <xsl:text>?show_original_page_numbers:</xsl:text>
    <xsl:value-of select="$show_original_page_numbers"/><xsl:text>
</xsl:text>
    <xsl:text>?show_v_forms:</xsl:text>
    <xsl:value-of select="$show_v_forms"/><xsl:text>
</xsl:text>
    <xsl:text>?downshift_ordinals:</xsl:text>
    <xsl:value-of select="$downshift_ordinals"/><xsl:text>
</xsl:text>
    <xsl:text>?enable_capitalization:</xsl:text>
    <xsl:value-of select="$enable_capitalization"/><xsl:text>
</xsl:text>
    <xsl:text>?detailed_accented_characters:</xsl:text>
    <xsl:value-of select="$detailed_accented_characters"/><xsl:text>
</xsl:text>
    <xsl:text>U dtbook.sbf
</xsl:text>
    <xsl:text>x ---------------------------------------------------------------------------
</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="dtb:dtbook">
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
y b Titlepage
y TPb
</xsl:text><xsl:apply-templates select="//dtb:docauthor/text()"/><xsl:text>
</xsl:text><xsl:apply-templates select="//dtb:doctitle/text()"/><xsl:text>
</xsl:text>
<xsl:value-of select="louis:translate(string(substring-before(//dtb:meta[@name='dc:Date']/@content,'-')),string(my:getTable()))"/>
  <xsl:text>
    
y TPink
</xsl:text>
    <xsl:apply-templates select="//dtb:frontmatter/dtb:level1[1]"/>
<xsl:text>y Tpe
y e Titlepage
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y BOOKe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:frontmatter">
    <xsl:text>y BrlVol
y FRONTb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y FRONTe
</xsl:text>
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
    <xsl:text>y LEVEL1b</xsl:text>
    <!-- invoke a different macro if the first child is a pagenum -->
    <xsl:if test="name(child::*[1])='pagenum'">
    <xsl:text>_j</xsl:text>
    </xsl:if>
    <xsl:text>
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y LEVEL1e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:level2">
    <xsl:text>y LEVEL2b</xsl:text>
    <!-- invoke a different macro if the first child is a pagenum -->
    <xsl:if test="name(child::*[1])='pagenum'">
    <xsl:text>_j</xsl:text>
    </xsl:if>
    <xsl:text>
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y LEVEL2e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:level3">
    <xsl:text>y LEVEL3b</xsl:text>
    <!-- invoke a different macro if the first child is a pagenum -->
    <xsl:if test="name(child::*[1])='pagenum'">
    <xsl:text>_j</xsl:text>
    </xsl:if>
    <xsl:text>
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y LEVEL3e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:level4">
    <xsl:text>y LEVEL4b</xsl:text>
    <!-- invoke a different macro if the first child is a pagenum -->
    <xsl:if test="name(child::*[1])='pagenum'">
    <xsl:text>_j</xsl:text>
    </xsl:if>
    <xsl:text>
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y LEVEL4e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:level5">
    <xsl:text>y LEVEL5b</xsl:text>
    <!-- invoke a different macro if the first child is a pagenum -->
    <xsl:if test="name(child::*[1])='pagenum'">
    <xsl:text>_j</xsl:text>
    </xsl:if>
    <xsl:text>
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y LEVEL5e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:level6">
    <xsl:text>y LEVEL6b</xsl:text>
    <!-- invoke a different macro if the first child is a pagenum -->
    <xsl:if test="name(child::*[1])='pagenum'">
    <xsl:text>_j</xsl:text>
    </xsl:if>
    <xsl:text>
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y LEVEL6e
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:p[@class='precedingseparator']">   
    <xsl:text>y SEPARATOR
y Pb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
y Pe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:p[@class='precedingemptyline']">   
    <xsl:text>y BLANK
y Pb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
y Pe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:p">   
    <xsl:text>y Pb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
y Pe
</xsl:text>
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
    <xsl:text>y LIb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
y LIe
</xsl:text>
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

  <xsl:template match="dtb:h1">
    <xsl:text>y H1
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:h2">
    <xsl:text>y H2
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:h3">
    <xsl:text>y H3
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:h4">
    <xsl:text>y H4
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:h5">
    <xsl:text>y H5
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:h6">
    <xsl:text>y H6
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:blockquote">
    <xsl:text>y BLQUOb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y BLQUOe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:poem">
    <xsl:text>y POEMb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y POEMe
</xsl:text>
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
      <xsl:when test="$downshift_ordinals">
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
      <xsl:when test="$show_v_forms">
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
