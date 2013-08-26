'use strict';

angular.module('belowtheline', ['ui.sortable']).
    config(['$locationProvider', function ($locationProvider) {
            $locationProvider.html5Mode(true);
    }]);
