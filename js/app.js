'use strict';

(function () {
    var GEO_API_URL = 'http://api.belowtheline.org.au/division';
    var CONFIRM_URL_IMAGE_FORMAT = 'http://maps.googleapis.com/maps/api/staticmap?size=300x300&visual_refresh=true&sensor=SENSOR&markers=|LATITUDE,LONGITUDE&zoom=14';

    var geocoder = null;

    function confirmLatLon(latitude, longitude, sensor) {
        var image_url = CONFIRM_URL_IMAGE_FORMAT;
        image_url = image_url.replace('SENSOR', sensor);
        image_url = image_url.replace('LATITUDE', latitude);
        image_url = image_url.replace('LONGITUDE', longitude);
        $('#geo-progress').hide();
        $('#geo-progress').after($('<img class="geo-confirm-image" src="' + image_url + '">'));

        $('#use-location').unbind('click');
        $('#use-location').click(function (e) {
            e.preventDefault();
            divisionByLatLon(latitude, longitude);
        });
    }

    function divisionByLatLon(latitude, longitude) {
        $.ajax({
            type: "GET",
            url: GEO_API_URL + '?latitude=' + latitude + '&longitude=' + longitude
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

                $('.geolocation-warning').show();
                $('.address-warning').hide();
                $('.geo-confirm-image').remove();
                $('#geo-progress').show();

                navigator.geolocation.getCurrentPosition(function (position) {
                    confirmLatLon(position.coords.latitude,
                                  position.coords.longitude, true);
                }, function (error) {
                    console.log(error);
                });
            });
        }

        $('#addressInput').keyup(function (e) {
            if (e.keyCode == 13) {
                e.preventDefault();
                $('#addressSearch').click();
            }
        });

        $('#addressSearch').click(function (e) {
            e.preventDefault();

            $('.geolocation-warning').hide();
            $('.address-warning').show();
            $('#geo-confirm-image').remove();
            $('#geo-progress').show();

            var address = $('#addressInput').val();

            if (geocoder == null) {
                geocoder = new google.maps.Geocoder();
            }

            geocoder.geocode({ address: address, region: 'au'},
                function (results, status) {
                    var latlng = results[0].geometry.location;
                    confirmLatLon(latlng.lat(), latlng.lng(), false);
                });
        });

        $('#division').submit(function (e) {
            e.preventDefault();

            var divisionId = $('#divisionSelector').val();
            window.location = '/division/' + divisionId + '.html';
        })
    });
}());


angular.module('belowtheline', ['ui.sortable']).
    config(['$locationProvider', function ($locationProvider) {
            $locationProvider.html5Mode(true);
    }]);
