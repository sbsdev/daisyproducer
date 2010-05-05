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
    exclude-result-prefixes="dtb louis str func my">

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
  <xsl:variable name="options">
    <xsl:if test="$enable_capitalization">
      <xsl:text>capitalization=on</xsl:text>
    </xsl:if>
    <xsl:text>accents=</xsl:text>
    <xsl:value-of select="$detailed_accented_characters"/>
  </xsl:variable>

  <func:function name="my:isGerman">
    <func:result select="ancestor-or-self::*[@xml:lang='de' or @xml:lang='de-CH']]"/>
  </func:function>
  
  <xsl:template match="/">
    <xsl:text>x </xsl:text><xsl:value-of select="//dtb:docauthor"/>
    <xsl:text>: </xsl:text><xsl:value-of select="//dtb:doctitle"/><xsl:text>
</xsl:text>
    <xsl:text>x Daisy Producer Version: </xsl:text>
    <xsl:value-of select="$version"/><xsl:text>
</xsl:text>
    <xsl:text>?grade:</xsl:text>
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
<xsl:value-of select="louis:translate(string(substring-before(//dtb:meta[@name='dc:Date']/@content,'-')),string(ancestor-or-self::*[@xml:lang]),string($contraction),'normal')"/>
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

  <xsl:template match="dtb:em">
    <xsl:apply-templates mode="italic"/>
  </xsl:template>

  <xsl:template match="dtb:strong">
    <xsl:apply-templates mode="bold"/>
  </xsl:template>

  <xsl:template match="dtb:abbr">
  </xsl:template>
  
  <xsl:template match="dtb:acronym">
  </xsl:template>

  <!-- Contraction hints -->

  <xsl:template match="brl:num[@role='ordinal' and my:isGerman()]">
    <xsl:choose>
      <xsl:when test="$downshift_ordinals">
	<xsl:value-of select="louis:translate(string(translate(.,'.','')),'de',string($contraction),'normal',string($options),string('num[ordinal]'))"/>
      </xsl:when>
      <xsl:otherwise>
	<xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="brl:num[@role='roman' and my:isGerman()]">
    <xsl:value-of select="louis:translate(string(),'de',string($contraction),'normal',string($options),string('num[roman]'))"/>
  </xsl:template>

  <xsl:template match="brl:num[@role='phone' and my:isGerman()]">
    <xsl:for-each select="str:tokenize(string(.), ' /')">
      <xsl:value-of select="louis:translate(string(.),'de',string($contraction),'normal')" />
      <xsl:if test="not(position() = last())">.</xsl:if>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="brl:num[@role='measure' and my:isGerman()]">
    <!-- For all number-unit combinations, e.g. 1 kg, 10 km, etc. drop the space -->
    <xsl:for-each select="str:tokenize(string(.), ' ')">
      <xsl:choose>
	<xsl:when test="not(position() = last())">
	  <!-- FIXME: do not test for position but whether it is a number -->
	  <xsl:value-of select="louis:translate(string(.),'de',string($contraction),'normal')"/>
	</xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="louis:translate(string(.),'de',string($contraction),'normal',string($options),string('abbrev'))"/>
      </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="brl:num[@role='isbn' and my:isGerman()]">
    <xsl:variable name="lastChar" select="substring(.,string-length(.),1)"/>
    <xsl:variable name="upperCase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
    <xsl:variable name="secondToLastChar" select="substring(.,string-length(.)-1,1)"/>
    <xsl:choose>
      <!-- If the isbn number ends in a capital letter then keep the
           dash, mark the letter with &#x2566; and translate the
           letter with sbs-de-g0-abbr.ctb -->
      <xsl:when test="$secondToLastChar='-' and string(number($lastChar))='NaN' and contains($upperCase, $lastChar)">
	<xsl:for-each select="str:tokenize(substring(.,1,string-length(.)-2), ' -')">
	  <xsl:value-of select="louis:translate(string(.),'de',string($contraction),'normal')" />
	  <xsl:if test="not(position() = last())">.</xsl:if>
	</xsl:for-each>
	<xsl:value-of select="louis:translate($secondToLastChar,'de',string($contraction),'normal')"/>
	<!-- FIXME: mark the letter with &#x2566; -->
	<!-- concat(&#x2566;,$lastChar)? -->
	<xsl:value-of select="louis:translate($lastChar,'de',string($contraction),'normal',string($options),string('abbrev'))"/>
      </xsl:when>
      <xsl:otherwise>
	<xsl:for-each select="str:tokenize(string(.), ' -')">
	  <xsl:value-of select="louis:translate(string(.),'de',string($contraction),'normal')" />
	  <xsl:if test="not(position() = last())">.</xsl:if>
	</xsl:for-each>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="brl:name[my:isGerman()]">
    <xsl:value-of select="louis:translate(string(),'de',string($contraction),'normal',string($options),string('name'))"/>
  </xsl:template>

  <xsl:template match="brl:place[my:isGerman()]">
    <xsl:value-of select="louis:translate(string(),'de',string($contraction),'normal',string($options),string('place'))"/>
  </xsl:template>

  <xsl:template match="brl:v-form[my:isGerman()]">
    <xsl:choose>
      <xsl:when test="not($show_v_forms)">
	<xsl:apply-templates/>
      </xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="louis:translate(string(),'de',string($contraction),'normal',string($options),string('v-form'))"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="brl:homograph">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="brl:separator">
    <!-- ignore -->
  </xsl:template>

  <xsl:template match="brl:date[my:isGerman()]">
    <xsl:for-each select="str:tokenize(string(@value), '-')">
      <xsl:choose>
	<xsl:when test="position() = last()-1">
	  <xsl:value-of select="louis:translate(string(),'de',string($contraction),'normal',string($options),string('date[month]'))"/>
	</xsl:when>
	<xsl:when test="position() = last()">
	  <xsl:value-of select="louis:translate(string(),'de',string($contraction),'normal',string($options),string('date[day]'))"/>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:value-of select="louis:translate(string(),'de',string($contraction),'normal')"/>
	</xsl:otherwise>	
      </xsl:choose>
      <xsl:if test="not(position() = last())">.</xsl:if>
    </xsl:for-each>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="brl:time[my:isGerman()]">
    <xsl:variable name="time">
      <xsl:for-each select="str:tokenize(string(@value), ':')">
	<xsl:value-of select="format-number(.,'#')"/>
	<xsl:if test="not(position() = last())">.</xsl:if>
      </xsl:for-each>
    </xsl:variable>
    <xsl:value-of select="louis:translate(string($time),'de',string($contraction),'normal')" />
    <xsl:text>
</xsl:text>
  </xsl:template>

  <!-- Text nodes are translated with liblouis -->

  <xsl:template match="text()">
    <xsl:value-of select='louis:translate(string(),string(ancestor-or-self::*[@xml:lang]),string($contraction),"normal",string($options))'/>
  </xsl:template>
  
  <xsl:template match="text()" mode="italic">
    <xsl:value-of select='louis:translate(string(),string(ancestor-or-self::*[@xml:lang]),string($contraction),"italic",string($options))'/>
  </xsl:template>
  
  <xsl:template match="text()" mode="bold">
    <xsl:value-of select='louis:translate(string(),string(ancestor-or-self::*[@xml:lang]),string($contraction),"bold",string($options))'/>
  </xsl:template>
  
  <xsl:template match="dtb:*">
    <xsl:message>
      *****<xsl:value-of select="name(..)"/>/{<xsl:value-of select="namespace-uri()"/>}<xsl:value-of select="name()"/>******
    </xsl:message>
  </xsl:template>
  
</xsl:stylesheet>
