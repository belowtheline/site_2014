'use strict';

(function () {
    var GEO_API_URL = 'http://api.belowtheline.org.au/division';

    var geocoder = null;

    function divisionByLatLon(latitude, longitude) {
        $.ajax({
            type: "POST",
            url: GEO_API_URL,
            data: JSON.stringify({latitude: latitude, longitude: longitude}),
            processData: false,
            contentType: 'application/json'
        }).done(function (data) {
            window.location = '/division/' + data.division + '.html';
        }).fail(function () {
             console.log("OH NOES");
        });
    }

    $(document).ready(function () {
        if (!!navigator.geolocation) {
            $(".geolocation-only").show();
            $(".geolocation-alt").hide();

            $('#geolocate').click(function (e) {
                e.preventDefault();
                $(this).button('loading');

                navigator.geolocation.getCurrentPosition(function (position) {
                    console.log(position.coords.latitude + ", " + position.coords.longitude);
                    divisionByLatLon(position.coords.latitude,
                                     position.coords.longitude);
                }, function (error) {
                    console.log(error);
                });
            });
        }

        $('#address').submit(function (e) {
            e.preventDefault();
            $('#addressSearch').button('loading');

            var address = $('#addressInput').val();

            if (geocoder == null) {
                geocoder = new google.maps.Geocoder();
            }

            geocoder.geocode({ address: address, region: 'au'},
                function (results, status) {
                    var latlng = results[0].geometry.location;
                    divisionByLatLon(latlng.lat(), latlng.lng());
                });
        });

        $('#division').submit(function (e) {
            e.preventDefault();

            var divisionId = $('#divisionSelector').val();
            window.location = '/division/' + divisionId + '.html';
        })
    });
}());
