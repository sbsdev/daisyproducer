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
  <xsl:template match="dtb:frontmatter//dtb:level1[not(.//dtb:h1)]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="1"/>
      <xsl:with-param name="blurb" select="'Vorspann ohne Überschrift 1'"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="dtb:bodymatter//dtb:level1[not(dtb:h1)]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="1"/>
      <xsl:with-param name="blurb" select="'ohne Überschrift 1'"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <xsl:template match="dtb:rearmatter//dtb:level1[not(dtb:h1)]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="1"/>
      <xsl:with-param name="blurb" select="'Nachspann ohne Überschrift 1'"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <xsl:template match="dtb:frontmatter//dtb:level2[not(.//dtb:h2)]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="2"/>
      <xsl:with-param name="blurb" select="'Vorspann ohne Überschrift 2'"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="dtb:bodymatter//dtb:level2[not(dtb:h2)]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="2"/>
      <xsl:with-param name="blurb" select="'ohne Überschrift 2'"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <xsl:template match="dtb:rearmatter//dtb:level2[not(dtb:h2)]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="1"/>
      <xsl:with-param name="blurb" select="'Nachspann ohne Überschrift 2'"/>
    </xsl:apply-templates>
  </xsl:template>

  <!-- Add an empty line for class="precedingemptyline" -->
  <xsl:template match="dtb:p[@class='precedingemptyline']">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:text>Abschnitt</xsl:text>
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
