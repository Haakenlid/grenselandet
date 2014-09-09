// Uses external API to populate dropdown <select> according to visitor's IP address.
jQuery(document).ready(function($) {
    var findLocation = function() {
        var myUrl = "http://ipinfo.io/";
        var thisMenu = this;
        if ($(thisMenu).val() === "") {
            $.get(myUrl, function(response) {
                var myCountryCode = response.country || "";
                $(thisMenu).val(myCountryCode);
            }, "jsonp");
        }
    };
    findLocation.call($("#id_nationality"));
});