<?xml version="1.0" encoding="utf-8"?>

<!-- This stylesheet modifies the input dtbook xml so that liblouisxml
  can properly handle it trough its dtbook.sem semantic action file.
  -->

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
		exclude-result-prefixes="dtb">
  
  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- Drop the class attribute of pagenum -->
  <xsl:template match="dtb:pagenum[@class]">
  </xsl:template>
  
  <!-- Change level into levelX (where X = [1..6]) -->
  <!-- FIXME: is this really needed? can't we just ignore them? -->
  <xsl:template match="dtb:level">
    <xsl:variable name="level">
      <xsl:value-of select="count(ancestor::dtb:level)+1"/>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$level=1"><dtb:level1><xsl:apply-templates select="@*|node()"/></dtb:level1></xsl:when>
      <xsl:when test="$level=2"><dtb:level2><xsl:apply-templates select="@*|node()"/></dtb:level2></xsl:when>
      <xsl:when test="$level=3"><dtb:level3><xsl:apply-templates select="@*|node()"/></dtb:level3></xsl:when>
      <xsl:when test="$level=4"><dtb:level4><xsl:apply-templates select="@*|node()"/></dtb:level4></xsl:when>
      <xsl:when test="$level=5"><dtb:level5><xsl:apply-templates select="@*|node()"/></dtb:level5></xsl:when>
      <xsl:when test="$level>5"><dtb:level6><xsl:apply-templates select="@*|node()"/></dtb:level6></xsl:when>
    </xsl:choose>
  </xsl:template>
  
  <!-- Change hd into hdX (where X = [1..6]) -->
  <xsl:template match="dtb:hd">
    <xsl:variable name="level">
      <xsl:value-of select="count(ancestor::dtb:level)"/>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$level=1"><dtb:h1><xsl:apply-templates select="@*|node()"/></dtb:h1></xsl:when>
      <xsl:when test="$level=2"><dtb:h2><xsl:apply-templates select="@*|node()"/></dtb:h2></xsl:when>
      <xsl:when test="$level=3"><dtb:h3><xsl:apply-templates select="@*|node()"/></dtb:h3></xsl:when>
      <xsl:when test="$level=4"><dtb:h4><xsl:apply-templates select="@*|node()"/></dtb:h4></xsl:when>
      <xsl:when test="$level=5"><dtb:h5><xsl:apply-templates select="@*|node()"/></dtb:h5></xsl:when>
      <xsl:when test="$level>5"><dtb:h6><xsl:apply-templates select="@*|node()"/></dtb:h6></xsl:when>
    </xsl:choose>
  </xsl:template>

  <!-- Copy all other elements and attributes -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
