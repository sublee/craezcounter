(function( key, width ) {
    var iframe = "<iframe src='http://{{ request.host }}/";
    iframe += key + "/embed' style='width:" + width + ";height:20px;";
    iframe += "border:none'></iframe>";
    document.write( iframe );
})( "{{ key }}", "{{ width }}".replace( /(\d)$/, "$1px" ) );
