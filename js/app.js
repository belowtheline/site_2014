'use strict';

angular.module('ngGeolocation',[])
  .constant('options',{})
  .factory('geolocation',
        ["$q","$rootScope","options",
function ($q , $rootScope , options){
  return {
    position: function () {
      var deferred = $q.defer()
      navigator.geolocation.getCurrentPosition(function (pos) {
        $rootScope.$apply(function () {
          deferred.resolve(angular.copy(pos))
        })
      }, function (error) {
        $rootScope.$apply(function () {
          deferred.reject(error)
        })
      },options)
      return deferred.promise
    }
  }
}]);

var generateTicketList = function(scopeGroups) {

  var groups = [];
  var tickets = [];

  angular.forEach(scopeGroups, function (group, group_id) {
      groups.push(group_id);
  });

  groups.sort(function (a, b) {
      if (a.length != b.length) {
          return a.length - b.length;
      } else if (a < b) {
          return -1;
      } else if (b > a) {
          return 1;
      } else {
          return 0;
      }
  });

  angular.forEach(groups, function (group_id, idx) {
      var group = scopeGroups[group_id];

      if (group.tickets.length == 1) {
          tickets.push({
              id: group_id + "1",
              name: group.name
          });
      } else {
          angular.forEach(group.tickets, function (ticket, idx) {
              tickets.push({
                  id: group_id + (idx + 1),
                  name: group.name + " (" + (idx + 1) + " of " + group.tickets.length + ")"
              });
          });
      }
  });

  return tickets;
}

angular.module('belowtheline', ['ui.sortable', 'ngGeolocation']).
    config(['$locationProvider', function ($locationProvider) {
            $locationProvider.html5Mode(true);
    }]);
