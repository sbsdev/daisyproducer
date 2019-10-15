<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="2.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
		xmlns:brl="http://www.daisy.org/z3986/2009/braille/"
		exclude-result-prefixes="dtb brl">
  
  <xsl:param name="contraction" select="2"/>
  
  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  
  <xsl:strip-space elements="brl:select"/>
  
  <!-- Drop a, i.e. urls, etc as they will be shown in grade 0 anyway -->
  <xsl:template match="dtb:a|brl:computer">
    <xsl:text> </xsl:text>
  </xsl:template>
  
  <!-- Drop the abbr elements -->
  <xsl:template match="dtb:abbr">
    <xsl:text> </xsl:text>
  </xsl:template>

  <!-- Drop the num elements -->
  <xsl:template match="brl:num">
    <xsl:text> </xsl:text>
  </xsl:template>

  <!-- Drop hyphens immediately before an abbr, a num, a computer  or names with mixed capitalization -->
  <xsl:template match="text()[ends-with(., '-')
		       and following-sibling::*[1][self::dtb:abbr or self::brl:num or self::brl:computer or self::brl:name[matches(string(.), '\p{Ll}\p{Lu}')]]]">
    <xsl:value-of select="substring(., 1, string-length(.)-1)"/>
  </xsl:template>

  <!-- Drop hyphens immediately after an abbr, a num, a computer or names with mixed capitalization -->
  <xsl:template match="text()[starts-with(., '-')
		       and preceding-sibling::*[1][self::dtb:abbr or self::brl:num or self::brl:computer or self::brl:name[matches(string(.), '\p{Ll}\p{Lu}')]]]">
    <xsl:value-of select="substring(., 2)"/>
  </xsl:template>

  <!-- Drop hyphens immediately between an abbr, a num, a computer or names with mixed capitalization -->
  <xsl:template match="text()[starts-with(., '-') and ends-with(., '-')
		       and preceding-sibling::*[1][self::dtb:abbr or self::brl:num or self::brl:computer or self::brl:name[matches(string(.), '\p{Ll}\p{Lu}')]]
		       and following-sibling::*[1][self::dtb:abbr or self::brl:num or self::brl:computer or self::brl:name[matches(string(.), '\p{Ll}\p{Lu}')]]]"
		       priority="10">
    <xsl:value-of select="substring(., 2, string-length(.)-2)"/>
  </xsl:template>

  <!-- Drop brl:literals -->
  <xsl:template match="brl:literal"/>
  
  <!-- Drop text which is not meant for Braille anyway -->
  <xsl:template match="brl:otherwise"/>
  
  <!-- Drop names with mixed capitalization -->
  <xsl:template match="brl:name[matches(string(.), '\p{Ll}\p{Lu}')]">
    <xsl:text> </xsl:text>
  </xsl:template>
  
  <!-- Drop foreign and downgraded words -->
  <xsl:template match="*[not(lang('de'))]"/>
  <xsl:template match="*[@brl:grade and number(@brl:grade) &lt; $contraction]"/>

  <!-- Copy all other nodes and attributes -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
