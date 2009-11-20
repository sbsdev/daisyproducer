<?xml version='1.0'?>

<xsl:stylesheet 
    xmlns:xsl='http://www.w3.org/1999/XSL/Transform' 
    xmlns:html='http://www.w3.org/1999/xhtml'
    xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
    exclude-result-prefixes="dtb"
    version='1.0'>  

  <xsl:output encoding="UTF-8" method="xml"/>

  <xsl:template match="/">
    <style>
      .level {margin-left: 3em}
    </style>
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="dtb:level">
    <div class="level">
      <xsl:apply-templates />
    </div>
  </xsl:template>

  <xsl:template match="dtb:hd">
    <h2 class="generic-element">
      <xsl:apply-templates />
    </h2>
  </xsl:template>

  <xsl:template match="dtb:pagenum">
    <span class="generic-element" style="position:relative;float:left;left:-3em">
      <xsl:apply-templates />
    </span>
  </xsl:template>

  <xsl:template match="*">
    <div class="generic-element">
      <xsl:apply-templates />
    </div>
  </xsl:template>

</xsl:stylesheet>
