'use strict';

function TicketViewerCtrl($scope, $http, $location) {
    var state = $location.path();
    var hash = $location.hash();

    $scope.ticket = [null, null];
    if (hash.indexOf('v') != -1) {
        $scope.ticket = hash.split('v', 2);
    } else if (hash) {
        $scope.ticket = [hash, null];
    }

    $scope.candidateOrder = [[], []];

    $scope.ticketList = [];
    $scope.shareURL = '';
    $scope.shareTicketText = 'this ticket';
    $scope.shareWarning = '';

    $scope.changeTicket = function (idx) {
        if (!$scope.ticket[idx]) {
            $scope.candidateOrder[idx] = $scope.ballotOrder;
        } else {
            var group = $scope.ticket[idx].slice(0, -1);
            var ticket = parseInt($scope.ticket[idx].slice(-1)) - 1;

            $scope.candidateOrder[idx] = $scope.groups[group].tickets[ticket];
        }

        if (!$scope.ticket[1]) {
            $location.hash($scope.ticket[0]);
            $scope.shareTicketText = 'this ticket';
            $scope.shareWarning = '';
        } else {
            $location.hash($scope.ticket.join('v'));
            $scope.shareTicketText = 'these tickets';
            $scope.shareWarning = 'Note that only one ticket will be visible on smaller devices such as phones.';
       }
        $scope.shareURL = 'http://btl.tv/t' + state + '/' + $location.hash();
    }

    function generateTicketList() {
        var groups = []
        var tickets = [];

        angular.forEach($scope.groups, function (group, group_id) {
            groups.push(group_id);
        });

        groups.sort(function (a, b) {
            if (a.length != b.length) {
                return a.length - b.length;
            } else if (a < b) {
                return -1
            } else if (b > a) {
                return 1;
            } else {
                return 0;
            }
        })

        angular.forEach(groups, function (group_id, idx) {
            var group = $scope.groups[group_id];

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

        $scope.ticketList = tickets;

        for (var i = 0; i <= 1; i++) {
            console.log(i);
            if (!!$scope.ticket[i]) {
                $scope.changeTicket(i);
            }
        }
    }

    $http.get('/state' + state + '.json').
        success(function (data) {
            $scope.state = data.state;
            $scope.stateOrTerritory = data.state_or_territory;
            $scope.candidates = data.candidates;
            $scope.ballotOrder = data.ballot_order;
            $scope.groups = data.groups;

            $scope.candidateOrder = [$scope.ballotOrder, $scope.ballotOrder];

            generateTicketList();
        }).
        error(function () {
            console.log("I have no idea");
        });
    $http.get('/parties.json').
        success(function (data) {
            $scope.parties = data;
        }).
        error(function () {
            console.log("I have no idea");
        });
}
