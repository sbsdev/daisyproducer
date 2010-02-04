<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
		xmlns:louis="http://liblouis.org/liblouis"
		xmlns:brl="http://www.daisy.org/z3986/2009/braille/"
		exclude-result-prefixes="dtb louis">

  <xsl:output method="text" encoding="utf-8" indent="no"/>
  <xsl:strip-space elements="*"/>
  <xsl:preserve-space elements="code samp"/>
	
  <xsl:param name="translation_table">de-ch-g2.ctb</xsl:param>
  <xsl:param name="contraction">0</xsl:param>
  <xsl:param name="version">0</xsl:param>
  <xsl:param name="cells_per_line">40</xsl:param>
  <xsl:param name="lines_per_page">28</xsl:param>
  <xsl:param name="hyphenation">false</xsl:param>
  <xsl:param name="generate_toc">false</xsl:param>
  <xsl:param name="show_original_page_numbers">false</xsl:param>
  <xsl:param name="enable_capitalization">false</xsl:param>
  <xsl:param name="detailed_accented_characters">false</xsl:param>

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
  <xsl:value-of select="louis:translate(string(substring-before(//dtb:meta[@name='dc:Date']/@content,'-')),string($translation_table))"/>
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

  <xsl:template match="brl:contractionhint[@class='ordinal']">
    <!-- FIXME: insert the proper table here -->
    <xsl:value-of select='louis:translate(string(),string($translation_table))'/>
  </xsl:template>

  <xsl:template match="brl:contractionhint[@class='propername']">
    <!-- FIXME: insert the proper table here -->
    <xsl:value-of select='louis:translate(string(),string($translation_table))'/>
  </xsl:template>

  <xsl:template match="brl:contractionhint[@class='politeform']">
    <!-- FIXME: insert the proper table here -->
    <xsl:value-of select='louis:translate(string(),string($translation_table))'/>
  </xsl:template>

  <xsl:template match="brl:date">
    <!-- FIXME: What do we do with dates that have no year? -->
    <xsl:variable name="year" select="substring-before(@iso, '-')"/>
    <xsl:variable name="month" select="substring-before(substring-after(@iso, '-'),'-')"/>
    <xsl:variable name="day" select="substring-after(substring-after(@iso, '-'), '-')"/>
    <xsl:value-of select="concat($year,',',$month,',',$day)"/>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="brl:time">
    <xsl:variable name="hour" select="substring-before(@iso, ':')"/>
    <xsl:variable name="minute" select="substring-after(@iso, ':')"/>
    <xsl:value-of select="concat($hour,',',$minute)"/>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <!-- Text nodes are translated with liblouis -->

  <xsl:template match="text()">
    <xsl:value-of select='louis:translate(string(),string($translation_table))'/>
  </xsl:template>
  
  <xsl:template match="text()" mode="italic">
    <xsl:value-of select='louis:translate(string(),string($translation_table),"italic")'/>
  </xsl:template>
  
  <xsl:template match="text()" mode="bold">
    <xsl:value-of select='louis:translate(string(),string($translation_table),"bold")'/>
  </xsl:template>
  
  <xsl:template match="dtb:*">
    <xsl:message>
      *****<xsl:value-of select="name(..)"/>/{<xsl:value-of select="namespace-uri()"/>}<xsl:value-of select="name()"/>******
    </xsl:message>
  </xsl:template>
  
</xsl:stylesheet>
