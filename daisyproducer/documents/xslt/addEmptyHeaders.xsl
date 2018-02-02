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

  <!-- Add an empty header to the first level1 w/o h1 in the frontmatter -->
  <xsl:template match="dtb:frontmatter//dtb:level1[@class='titlepage'][1][not(dtb:h1)]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="1"/>
      <xsl:with-param name="blurb" select="'Vorspann'"/>
    </xsl:apply-templates>
  </xsl:template>

  <!-- Insert a h1 if we have a level2 with a heading in the frontmatter -->
  <xsl:template match="dtb:frontmatter//dtb:level1[not(dtb:h1)][dtb:level2/dtb:h2]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="1"/>
      <xsl:with-param name="blurb" select="'Ohne Überschrift'"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <!-- Add an empty header to the first level1 w/o h1 in the rearmatter -->
  <xsl:template match="dtb:rearmatter//dtb:level1[1][not(dtb:h1)]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="1"/>
      <xsl:with-param name="blurb" select="'Nachspann'"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <!-- Add an empty header to the other level1 w/o h1 in the rearmatter -->
  <xsl:template match="dtb:rearmatter//dtb:level1[position()>1][not(dtb:h1)]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="1"/>
      <xsl:with-param name="blurb" select="'Ohne Überschrift'"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <xsl:template match="dtb:bodymatter//dtb:level1[not(dtb:h1)]">
    <xsl:variable name="level" >
      <xsl:choose>
	<xsl:when test="local-name() = 'level1'">1</xsl:when>
	<xsl:otherwise>2</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="1"/>
      <xsl:with-param name="blurb" select="concat(format-number(count(preceding-sibling::dtb:level1) + 1, '0'),
        ' Im Original ohne Nummerierung')"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <xsl:template match="dtb:bodymatter//dtb:level2[not(dtb:h2)]|
                       dtb:bodymatter//dtb:level3[not(dtb:h3)]|
                       dtb:bodymatter//dtb:level4[not(dtb:h4)]|
                       dtb:bodymatter//dtb:level5[not(dtb:h5)]|
                       dtb:bodymatter//dtb:level6[not(dtb:h6)]">
    <xsl:apply-templates select="." mode="addHeading">
      <xsl:with-param name="level" select="substring-after(name(), 'level')"/>
      <xsl:with-param name="blurb" select="'Ohne Überschrift'"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <!-- Add an empty paragraph for class="precedingemptyline" -->
  <xsl:template match="dtb:p[@class='precedingemptyline']">
    <xsl:element name="p" namespace="http://www.daisy.org/z3986/2005/dtbook/">
      <xsl:text> </xsl:text>
    </xsl:element>
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

  <!-- Add a paragraph containing "***" for class="precedingseparator" -->
  <xsl:template match="dtb:p[@class='precedingseparator']">
    <xsl:element name="p" namespace="http://www.daisy.org/z3986/2005/dtbook/">
      <xsl:text>***</xsl:text>
    </xsl:element>
    <xsl:copy>
      <xsl:copy-of select="@*"/>
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
