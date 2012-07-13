<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
		xmlns:brl="http://www.daisy.org/z3986/2009/braille/"
		exclude-result-prefixes="dtb brl">
  
  <xsl:output method="xml" encoding="utf-8" indent="no" 
	      doctype-public="-//NISO//DTD dtbook 2005-3//EN"
              doctype-system="http://www.daisy.org/z3986/2005/dtbook-2005-3.dtd" />

  <xsl:template match="*" mode="copyLeadingPagenums">
    <xsl:apply-templates select="(dtb:pagenum|text()|processing-instruction()|comment())[not(preceding-sibling::dtb:*[not(self::dtb:pagenum)])]" />
  </xsl:template>
  
  <xsl:template match="*" mode="copyAllButLeadingPagenums">
    <xsl:apply-templates select="*[not(self::dtb:pagenum)]|(dtb:pagenum|text()|processing-instruction()|comment())[preceding-sibling::dtb:*[not(self::dtb:pagenum)]]"/>
  </xsl:template>

  <xsl:template match="*" mode="addHeading">
    <xsl:param name="level"/>
    <xsl:param name="blurb"/>
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <!-- <xsl:apply-templates select="." mode="copyLeadingPagenums"/> -->
      <xsl:element name="h{$level}" namespace="http://www.daisy.org/z3986/2005/dtbook/"><xsl:value-of select="$blurb"/></xsl:element>
      <!-- <xsl:apply-templates select="." mode="copyAllButLeadingPagenums"/> -->
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

  <!-- Add empty headers where there are none -->
  <!-- Add an empty header to the first level1 w/o h1 in the frontmatter -->
  <xsl:template match="dtb:frontmatter//dtb:level1[not(dtb:h1)][position()=1]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="1"/>
      <xsl:with-param name="blurb" select="'Vorspann'"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="dtb:bodymatter//dtb:level1[not(dtb:h1)]|dtb:bodymatter//dtb:level2[not(dtb:h2)]">
    <xsl:variable name="level" >
      <xsl:choose>
	<xsl:when test="local-name() = 'level1'">1</xsl:when>
	<xsl:otherwise>2</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="$level"/>
      <xsl:with-param name="blurb" select="'ohne Überschrift'"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <!-- Add an empty header to the first level1 w/o h1 in the rearmatter -->
  <xsl:template match="dtb:rearmatter//dtb:level1[not(dtb:h1)][position()=1]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="1"/>
      <xsl:with-param name="blurb" select="'Nachspann'"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <!-- Add an empty line for class="precedingemptyline" -->
  <xsl:template match="dtb:p[@class='precedingemptyline']">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:element name="br" namespace="http://www.daisy.org/z3986/2005/dtbook/"></xsl:element>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

  <!-- Add an empty line for class="precedingseparator" -->
  <xsl:template match="dtb:p[@class='precedingseparator']">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:text>***</xsl:text>
      <xsl:element name="br" namespace="http://www.daisy.org/z3986/2005/dtbook/"></xsl:element>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

  <!-- Copy all other elements and attributes -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
