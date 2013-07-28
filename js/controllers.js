'use strict';

function DivisionSelectorCtrl($scope) {
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

    $scope.geolocationAvailable = function () {
        return (!!navigator.geolocation);
    };

    $scope.geolocate = function () {
        console.log("commence the geolocation!");
    };

    $scope.searchByAddress = function () {
        console.log("search for: " + $scope.address);
    };

    $scope.selectDivision = function () {
        console.log("at this point we'd switch to " + $scope.division.id);
    };
}