'use strict';

function IndexCtrl($scope, $http, $window, geolocation) {
    var GEO_API_URL = 'http://api.belowtheline.org.au/division';

    $scope.division = '';
    $scope.address = '';
    $scope.position = {
        latitude: 0,
        longitude: 0
    };
    $scope.showMap = false;
    $scope.usingGeolocation = false;

    $scope.geoAvailable = function () {
        return !!navigator.geolocation;
    }

    $scope.geolocate = function () {
        $scope.usingGeolocation = true;
        $scope.showMap = false;
        geolocation.position().
            then(function (position) {
                $scope.position.latitude = position.coords.latitude;
                $scope.position.longitude = position.coords.longitude;
                $scope.position.sensor = true;
                $scope.showMap = true;
            }, function (error) {
                console.log(error);
            });
    }

    $scope.addressLookup = function () {
        $scope.usingGeolocation = false;
        $scope.showMap = false;

        var geocoder = new google.maps.Geocoder();

        geocoder.geocode({ address: $scope.address, region: 'au'},
            function (results, status) {
                $scope.$apply(function () {
                    var latlng = results[0].geometry.location;
                    $scope.position.latitude = latlng.lat();
                    $scope.position.longitude = latlng.lng();
                    $scope.position.sensor = false;
                    $scope.showMap = true;
                })
            });
    }

    $scope.useLocation = function () {
        $http.get(GEO_API_URL + '?latitude=' + $scope.position.latitude + 
                  '&longitude=' + $scope.position.longitude).
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