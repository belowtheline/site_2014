'use strict';

var GEO_API_URL = 'http://erstwhile.jeamland.net:5000/division'

function DivisionSelectorCtrl($scope, $http, $location) {
    $scope.states = _btldata.state;
    $scope.divisions = _btldata.division;

    $scope.divisionsArray = [];
    angular.forEach($scope.divisions, function (value, key) {
        var division = angular.copy(value);
        division.id = key;
        this.push(division);
    }, $scope.divisionsArray);

    $scope.division = '';
    $scope.address = null;
    $scope._geolocationFailed = false;

    var geocoder = null;

    function divisionByLatLon(latitude, longitude) {
        console.log("would look up using: " + latitude + ", " + longitude);
        $http.post(GEO_API_URL, { latitude: latitude, longitude: longitude },
                   { headers: {'Content-Type': 'application/json'} }).
            success(function (data, status, headers, config) {
                $location.path('/division/' + data.division);
            }).
            error(function (data, status, headers, config) {
                console.log(status);
            });
    }

    $scope.geolocationAvailable = function () {
        return (!!navigator.geolocation);
    };

    $scope.geolocationFailed = function () {
        return ($scope._geolocationFailed);
    }

    $scope.geolocate = function () {
        console.log("commence the geolocation!");
        console.log($scope);
        navigator.geolocation.getCurrentPosition(function (position) {
            divisionByLatLon(position.coords.latitude,
                             position.coords.longitude);
        }, function (error) {
            console.log(error);
            console.log($scope);
            $scope._geolocationFailed = true;
        });
    };

    $scope.dismissGeolocationError = function () {
        $scope._geolocationFailed = false;
    }

    $scope.searchByAddress = function () {
        console.log("search for: " + $scope.address);

        if (geocoder == null) {
            geocoder = new google.maps.Geocoder();
        }

        geocoder.geocode({ address: $scope.address, region: 'au'},
            function (results, status) {
                var latlng = results[0].geometry.location;
                divisionByLatLon(latlng.lat(), latlng.lng());
            });
    };

    $scope.selectDivision = function () {
        console.log("at this point we'd switch to " + $scope.division.id);
        $location.path('/division/' + $scope.division.id);
    };
}

function DivisionDetailCtrl($scope, $http, $routeParams) {
    $scope.divisionId = $routeParams.divisionId;

    $http.get('/data/division/' + $scope.divisionId + '.json').
        success(function (data, status, headers, config) {
            console.log(data);
        }).
        error(function (data, status, headers, config) {
            console.log(status);
        });

    var state = _btldata.division[$scope.divisionId].state.substr(6);
    $http.get('/data/senators/' + state + '.json').
        success(function (data, status, headers, config) {
            console.log(data);
        }).
        error(function (data, status, headers, config) {
            console.log(status);
        });

}