<StyledLayerDescriptor version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd">
<NamedLayer>
<Name>Brightness and contrast</Name>
<UserStyle>
<Title>SLD Cook Book: Brightness and contrast</Title>
<FeatureTypeStyle>
<Rule>
<RasterSymbolizer>
<ContrastEnhancement>
<Normalize/>
<GammaValue>0.5</GammaValue>
</ContrastEnhancement>
<ColorMap>
<ColorMapEntry color="#008000" quantity="70"/>
<ColorMapEntry color="#663333" quantity="256"/>
</ColorMap>
</RasterSymbolizer>
</Rule>
</FeatureTypeStyle>
</UserStyle>
</NamedLayer>
</StyledLayerDescriptor>