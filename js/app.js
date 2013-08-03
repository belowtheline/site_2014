'use strict';

angular.module("belowtheline", []).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.
            when('/', {templateUrl: 'main.html', controller: DivisionSelectorCtrl}).
            when('/division/:divisionId', {templateUrl: 'division.html', controller: DivisionDetailCtrl}).
            otherwise({redirectTo: '/'});
    }]);
