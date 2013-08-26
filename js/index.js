'use strict';

function IndexCtrl($scope, $http, $window) {
    var CONFIRM_URL_IMAGE_FORMAT = 'http://maps.googleapis.com/maps/api/staticmap?size=300x300&visual_refresh=true&sensor=SENSOR&markers=|LATITUDE,LONGITUDE&zoom=14';

    $scope.division = '';
    $scope.address = '';
    $scope.geoConfirmationImage = '';

    function makeGeoConfirmationImage(latitude, longitude, sensor) {
        var image_url = CONFIRM_URL_IMAGE_FORMAT;
        image_url = image_url.replace('SENSOR', sensor);
        image_url = image_url.replace('LATITUDE', latitude);
        image_url = image_url.replace('LONGITUDE', longitude);

        return image_url;
    }

    $scope.geoAvailable = function () {
        return !!navigator.geolocation;
    }

    $scope.geolocate = function () {
        $scope.geoConfirmationImage = '';
        navigator.geolocation.getCurrentPosition(function (position) {
            $scope.geoConfirmationImage =
                makeGeoConfirmationImage(position.coords.latitude,
                                         position.coords.longitude, true)
        }, function (error) {
            console.log(error);
        });
    }

    $scope.addressLookup = function () {
        var geocoder = new google.maps.Geocoder();

        geocoder.geocode({ address: $scope.address, region: 'au'},
            function (results, status) {
                var latlng = results[0].geometry.location;
                $scope.geoConfirmationImage =
                    makeGeoConfirmationImage(latlng.lat(), latlng.lng(), false);
                console.log($scope.geoConfirmationImage);
            });
    }

    $scope.useLocation = function () {
        $http.get(GEO_API_URL + '?latitude=' + latitude + '&longitude=' + longitude).
            success(function (data) {
                $window.location = '/division/' + data.division + '.html';
            }).error(function () {
                console.log("OH NOES");
            });
    }

    $scope.selectDivision = function () {
        $window.location = '/division/' + $scope.division + '.html';
    }
}