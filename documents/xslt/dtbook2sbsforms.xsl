<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
		xmlns:louis="http://liblouis.org/liblouis"
		exclude-result-prefixes="dtb louis">

  <xsl:output method="text" encoding="utf-8" indent="no"/>
  <xsl:strip-space elements="*"/>
  <xsl:preserve-space elements="code samp"/>
	
  <xsl:param name="translation_table">de-ch-g2.ctb</xsl:param>

  <xsl:template match="/">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="dtb:dtbook">
    <xsl:text>y DTBOOKb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y DTBOOKe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:head">
    <xsl:text>y HEADb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y HEADe
</xsl:text>
  </xsl:template>
  
  <xsl:template match="dtb:meta">
    <xsl:apply-templates/>
  </xsl:template>
  
  <xsl:template match="dtb:book">
    <xsl:text>y BOOKb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y BOOKe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:frontmatter">
    <xsl:text>y FRONTb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y FRONTe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:bodymatter">
    <xsl:text>y BODYb
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y BODYe
</xsl:text>
  </xsl:template>

  <xsl:template match="dtb:doctitle">
    <!-- ignore for now -->
  </xsl:template>

  <xsl:template match="dtb:docauthor">
    <!-- ignore for now -->
  </xsl:template>

  <xsl:template match="dtb:level1">
    <xsl:text>y LEVEL1b
</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>y LEVEL1e
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
    <!-- ignore for now -->
  </xsl:template>

  <xsl:template match="dtb:pagenum">
    <xsl:text>
j </xsl:text>
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
  </xsl:template>

  <xsl:template match="dtb:strong">
   </xsl:template>

   <xsl:template match="dtb:abbr">
   </xsl:template>
   
   <xsl:template match="dtb:acronym">
   </xsl:template>
   
   <xsl:template match="text()">
     <xsl:value-of select='louis:translate(string(),string($translation_table))'/>
   </xsl:template>

   <xsl:template match="dtb:*">
     <xsl:message>
       *****<xsl:value-of select="name(..)"/>/{<xsl:value-of select="namespace-uri()"/>}<xsl:value-of select="name()"/>******
     </xsl:message>
   </xsl:template>
   
</xsl:stylesheet>
